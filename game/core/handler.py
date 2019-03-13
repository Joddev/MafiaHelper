from game.core.base import *
from game.core.room_status import RoomStatus
from game.core.room_processor import *
from channels.layers import get_channel_layer
from game.socket import HandlerType


class Room:

    DELEGATION_METHOD = [
        'get_user',
        'add_user',
        'remove_user',
        'get_user_list',
        'get_choice_list',
        'reconnect_user',
        'disconnect_user',
        'choose',
        'add_job',
        'remove_job',
        'get_job_list',
        'result',
        'done',
        'get_type',
    ]

    def __init__(self, room_key, users=None):
        self.status = RoomStatus(room_key, users)
        self.phases = [WaitingRoom(self.status)]
        self.cur_phase = self.phases[0]

    def __getattr__(self, method):
        if method in Room.DELEGATION_METHOD:
            return getattr(self.cur_phase, method)
        raise AttributeError("'%s' object has no attribute '%s'" % (self.__class__.__name__, method))

    def can_target(self, user, target):
        return self.cur_phase.choose_limit(user, target.key, Choice.Status.FIXED)

    def next_phase(self):
        self.cur_phase = self.cur_phase.next_phase()
        self.phases.append(self.cur_phase)

    def game_done(self):
        result = self.cur_phase.game_done()
        if result is not None:
            self.status = RoomStatus(self.status.room_key, [user for user in self.status.users if user.connected]
                                     , self.status.jobs)
            for user in self.status.users:
                user.init_status()
            self.cur_phase = WaitingRoom(self.status)
            self.phases.append(self.cur_phase)
        return result

    def type(self):
        return type(self.cur_phase)


class RoomHandler:

    def __init__(self):
        logger.debug('RoomContainer initiated.')
        self.room_map = {}

    def room_exists(self, room_key):
        return room_key in self.room_map

    def get_user(self, room_key, user_key):
        try:
            return self.room_map[room_key].get_user(user_key)
        except KeyError:
            return None

    def get_type(self, room_key):
        try:
            return self.room_map[room_key].get_type()
        except KeyError:
            return None

    async def add_user(self, room_key, channel):
        try:
            # room exists
            logger.debug('user {} is added to room {}'.format(channel.username, room_key))
            self.room_map[room_key].add_user(channel.user_key, channel.username, channel.channel_name)
            await self.alert_member_changed(room_key, channel.user_key, channel.username)
        except KeyError:
            # create new room
            logger.debug('new room {} is created'.format(room_key))
            new_room = Room(room_key)
            new_room.add_user(channel.user_key, channel.username, channel.channel_name)
            self.room_map[room_key] = new_room

    async def remove_user(self, room_key, channel):
        try:
            self.room_map[room_key].cur_phase.remove_user(channel.user_key)
            if len([user for user in self.room_map[room_key].get_user_list() if user.connected]) < 1:
                # remove empty room
                del self.room_map[room_key]
            else:
                await self.alert_member_changed(room_key, channel.user_key, channel.username)
        except KeyError:
            logger.error('Attempt to remove user from unregistered room!')

    async def reconnect_user(self, room_key, channel):
        try:
            # room exists
            logger.debug('user {} is reconnected to room {}'.format(channel.user_key, room_key))
            self.room_map[room_key].reconnect_user(channel.user_key, channel.channel_name)
            await self.alert_member_changed(room_key, channel.user_key, channel.username)
        except KeyError:
            logger.error('Attempt to reconnected user from unregistered room!')

    def disconnect_user(self, room_key, user_key):
        try:
            # room exists
            self.room_map[room_key].disconnect_user(user_key)
            if len(self.room_map[room_key].users) < 1:
                del self.room_map[room_key]
        except KeyError:
            logger.error('Attempt to disconnect user from unregistered room!')

    async def choose(self, room_key, user_key, target_key, status):
        try:
            # room exsits
            cur_room = self.room_map[room_key]
            if cur_room.choose(user_key, target_key, Choice.Status(status)):
                event = {
                    'type': HandlerType.CHOOSE_CHANGED,
                    'user': user_key,
                    'choice': {
                        'target': target_key,
                        'status': status
                    }
                }
                if cur_room.get_type() == 3:
                    # when night
                    await self.alert_on_jobs(room_key, user_key, event)
                else:
                    await get_channel_layer().group_send(room_key, event)
            else:
                # can not choose
                user = self.get_user(room_key, user_key)
                await get_channel_layer().send(
                    user.channel_name,
                    {
                        'type': HandlerType.COMMON_SEND,
                        'ret_type': HandlerType.CANNOT_CHOOSE,
                        'user': user_key,
                        'target': target_key,
                    }
                )
        except KeyError:
            logger.error('Attempt to toggle ready from unregistered room!')
            return None
        except ValueError:
            logger.error('Choice with invalid status')
            return None

    async def check_done(self, room_key):
        logger.debug('check_done')
        try:
            # room exists
            cur_room = self.room_map[room_key]
            if cur_room.done():
                prev_status = cur_room.get_type()
                result = cur_room.result()
                cur_room.next_phase()
                for user in self.room_user_list(room_key):
                    if user.connected:
                        processed = self.process_result(room_key, user, prev_status, result)
                        await get_channel_layer().send(
                            user.channel_name,
                            {
                                'type': HandlerType.COMMON_SEND,
                                'ret_type': HandlerType.ROOM_STATUS_CHANGED,
                                'prev_status': prev_status,
                                'result': processed,
                                'status': cur_room.get_type(),
                            }
                        )
                await self.alert_member_changed(room_key, user.key, user.name)
                done = cur_room.game_done()
                if done is not None:
                    await get_channel_layer().group_send(
                        room_key,
                        {
                            'type': HandlerType.COMMON_SEND,
                            'ret_type': HandlerType.GAME_DONE,
                            'result': done.dict()
                        }
                    )
        except KeyError:
            logger.error('Attempt to toggle ready from unregistered room!')
            return None

    def get_team_mates(self, room_key, user_key):
        user = self.get_user(room_key, user_key)
        if user.job.visible_team():
            return [row.dict() for row in self.room_user_list(room_key) if type(row.job) == type(user.job)]
        else:
            return [user.dict()]

    def get_targets(self, room_key, user_key):
        cur_room = self.room_map[room_key]
        return [target_user.dict() for target_user in self.room_user_list(room_key) 
                    if cur_room.can_target(self.get_user(room_key, user_key), target_user)]

    def process_result(self, room, user, status, result):
        cur_room = self.room_map[room]
        processed = {}
        if status == 0:
            # after job initiated
            if user.job.visible_team():
                team_mates = [row.dict() for row in result if type(row.job) == type(user.job)]
            else:
                team_mates = [user.dict()]
            processed['team_mates'] = team_mates
            processed['job'] = user.job.name()
        if status == 2:
            # after day vote result
            if result:
                processed['victim'] = result.dict()
        if status == 3:
            # after night action result
            act_list = []
            for row in result:
                if row.scope == 'all' or row.scope == user.job.name():
                    act_list.append(row.dict())
            processed['act_list'] = act_list
        if cur_room.get_type() == 3:
            # before night
            processed['targets'] = [target_user.dict() for target_user in self.room_user_list(room)
                                    if cur_room.can_target(user, target_user)]
        return processed

    def add_job(self, room, job):
        try:
            self.room_map[room].add_job(job)
        except KeyError:
            logger.error('Attempt to add job to unregistered room!')

    def remove_job(self, room, job):
        try:
            self.room_map[room].remove_job(job)
        except KeyError:
            logger.error('Attempt to remove job to unregistered room!')

    def room_list(self):
        rooms = []
        for room_key in self.room_map:
            room = self.room_map[room_key]
            if room.type() == WaitingRoom:
                rooms.append({
                    'name': room_key,
                    'num': len(room.get_user_list())
                })
        return rooms

    def room_user_list(self, room):
        try:
            return self.room_map[room].get_user_list()
        except KeyError:
            logger.error('Attempt to access unregistered room!')

    def room_job_list(self, room):
        try:
            return self.room_map[room].get_job_list()
        except KeyError:
            logger.error('Attempt to access unregistered room!')

    def room_choice_list(self, room):
        try:
            return [choice.user_dict() for choice in self.room_map[room].get_choice_list()]
        except KeyError:
            logger.error('Attempt to access unregistered room!')

    def game_done(self, room):
        try:
            return self.room_map[room].game_done()
        except KeyError:
            logger.error('Attempt to access unregistered room!')

    ######################
    ### Sender Methods ###
    ######################

    async def alert_member_changed(self, room_key, user_key, username):
        await get_channel_layer().group_send(
            room_key,
            {
                'type': HandlerType.COMMON_SEND,
                'ret_type': HandlerType.ROOM_MEMBER_CHANGED,
                'id': user_key,
                'name': username,
                'users': [choice for choice in self.room_choice_list(room_key)]
            }
        )

    async def alert_on_jobs(self, room_key, user_key, message):
        user_list = self.room_user_list(room_key)
        chooser = self.get_user(room_key, user_key)
        if chooser.job.visible_team():
            team_mates = [user for user in user_list if type(user.job) == type(chooser.job)]
        else:
            team_mates = [chooser]
        for mate in team_mates:
            await get_channel_layer().send(mate.channel_name, message)
