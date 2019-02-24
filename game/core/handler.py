from game.core.base import *
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

    def __init__(self, room_name, users=None):
        self.status = RoomStatus(room_name, users)
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
            self.status = RoomStatus(self.status.room_name, [user for user in self.status.users if user.can_act()]
                                     , self.status.jobs)
            self.cur_phase = WaitingRoom(self.status)
            self.phases.append(self.cur_phase)
        return result

    def type(self):
        return type(self.cur_phase)


class RoomHandler:

    def __init__(self):
        logger.info('RoomContainer initiated.')
        self.__rooms = {}

    def room_exists(self, room):
        return room in self.__rooms

    def get_user(self, room, key):
        try:
            return self.__rooms[room].get_user(key)
        except KeyError:
            return None

    async def add_user(self, room, channel):
        # room already exists
        try:
            logger.info('user {} is added to room {}'.format(channel.name, room))
            self.__rooms[room].add_user(channel.channel_name, channel.name)
            await self.alert_member_changed(room, channel.channel_name, channel.name)
        except KeyError:
            logger.info('new room {} is created'.format(room))
            new_room = Room(room)
            new_room.add_user(channel.channel_name, channel.name)
            self.__rooms[room] = new_room

    async def remove_user(self, room, channel):
        try:
            self.__rooms[room].cur_phase.remove_user(channel.channel_name)
            if len([user for user in self.__rooms[room].get_user_list() if user.connected]) < 1:
                del self.__rooms[room]
            else:
                await self.alert_member_changed(room, channel.channel_name, channel.name)
        except KeyError:
            logger.error('Attempt to remove user from unregistered room!')

    async def alert_member_changed(self, room, key, name):
        await get_channel_layer().group_send(
            room,
            {
                'type': HandlerType.COMMON_SEND,
                'ret_type': HandlerType.ROOM_MEMBER_CHANGED,
                'id': key,
                'name': name,
                'users': [choice for choice in self.room_choice_list(room)]
            }
        )

    def reconnect_user(self, room, user):
        # room already exists
        try:
            logger.info('user {} is reconnected to room {}'.format(user.name, room))
            self.__rooms[room].reconnect_user(user)
        except KeyError:
            logger.error('Attempt to reconnected user from unregistered room!')

    def disconnect_user(self, room, user):
        try:
            self.__rooms[room].disconnect_user(user)
            if len(self.__rooms[room].users) < 1:

                del self.__rooms[room]
        except KeyError:
            logger.error('Attempt to disconnect user from unregistered room!')

    async def job_send(self, room, user_key, message):
        user_list = self.room_user_list(room)
        chooser = self.get_user(room, user_key)
        if chooser.job.visible_team():
            team_mates = [user for user in user_list if type(user.job) == type(chooser.job)]
        else:
            team_mates = [chooser]
        for mate in team_mates:
            await get_channel_layer().send(mate.key, message)

    async def choose(self, room, key, target, status):
        try:
            cur_room = self.__rooms[room]
            if cur_room.choose(key, target, Choice.Status(status)):
                event = {
                    'type': HandlerType.CHOOSE_CHANGED,
                    'user': key,
                    'choice': {
                        'target': target,
                        'status': status
                    }
                }
                # when night
                if cur_room.get_type() == 3:
                    await self.job_send(room, key, event)
                else:
                    await get_channel_layer().group_send(room, event)
            else:
                await get_channel_layer().send(
                    key,
                    {
                        'type': HandlerType.COMMON_SEND,
                        'ret_type': HandlerType.CANNOT_CHOOSE,
                        'user': key,
                        'target': target,
                    }
                )
        except KeyError:
            logger.error('Attempt to toggle ready from unregistered room!')
            return None
        except ValueError:
            logger.error('Choice with invalid status')
            return None

    async def check_done(self, room):
        try:
            cur_room = self.__rooms[room]
            if cur_room.done():
                prev_status = cur_room.get_type()
                result = cur_room.result()
                cur_room.next_phase()
                for user in self.room_user_list(room):
                    if user.connected:
                        processed = self.process_result(room, user, prev_status, result)
                        await get_channel_layer().send(
                            user.key,
                            {
                                'type': HandlerType.COMMON_SEND,
                                'ret_type': HandlerType.ROOM_STATUS_CHANGED,
                                'prev_status': prev_status,
                                'result': processed,
                                'status': cur_room.get_type(),
                            }
                        )
                await self.alert_member_changed(room, user.key, user.name)
                done = cur_room.game_done()
                if done is not None:
                    await get_channel_layer().group_send(
                        room,
                        {
                            'type': HandlerType.COMMON_SEND,
                            'ret_type': HandlerType.GAME_DONE,
                            'result': done.dict()
                        }
                    )
        except KeyError:
            logger.error('Attempt to toggle ready from unregistered room!')
            return None

    def process_result(self, room, user, status, result):
        cur_room = self.__rooms[room]
        processed = {}
        # job initiated
        if status == 0:
            if user.job.visible_team():
                team_mates = [row.dict() for row in result if type(row.job) == type(user.job)]
            else:
                team_mates = [user.dict()]
            processed['team_mates'] = team_mates
            processed['job'] = user.job.name()
        if status == 2:
            if result:
                processed['victim'] = result.dict()
        if status == 3:
            act_list = []
            logger.info(user.dict())
            for row in result:
                if row.scope == 'all' or row.scope == user.job.name():
                    act_list.append(row.dict())
            processed['act_list'] = act_list
        if cur_room.get_type() == 3:
            processed['targets'] = [target_user.dict() for target_user in self.room_user_list(room)
                                    if cur_room.can_target(user, target_user)]
        return processed

    def add_job(self, room, job):
        try:
            self.__rooms[room].add_job(job)
        except KeyError:
            logger.error('Attempt to add job to unregistered room!')

    def remove_job(self, room, job):
        try:
            self.__rooms[room].remove_job(job)
        except KeyError:
            logger.error('Attempt to remove job to unregistered room!')

    def room_list(self):
        rooms = []
        for room_name in self.__rooms:
            room = self.__rooms[room_name]
            if room.type() == WaitingRoom:
                rooms.append({
                    'name': room_name,
                    'num': len(room.get_user_list())
                })
        return rooms

    def room_user_list(self, room):
        try:
            return self.__rooms[room].get_user_list()
        except KeyError:
            logger.error('Attempt to access unregistered room!')

    def room_job_list(self, room):
        try:
            return self.__rooms[room].get_job_list()
        except KeyError:
            logger.error('Attempt to access unregistered room!')

    def room_choice_list(self, room):
        try:
            return [choice.user_dict() for choice in self.__rooms[room].get_choice_list()]
        except KeyError:
            logger.error('Attempt to access unregistered room!')

    def game_done(self, room):
        try:
            return self.__rooms[room].game_done()
        except KeyError:
            logger.error('Attempt to access unregistered room!')
