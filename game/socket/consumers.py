import logging
import names
import uuid
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from game.core import room_container, job_list
from game.socket import HandlerType
import time

logger = logging.getLogger('mafia')
MAIN_GROUP = 'main'


class GameConsumer(AsyncJsonWebsocketConsumer):

    room_key = None
    user_key = None
    username = None

    #####################
    ### Basic methods ###
    #####################

    async def connect(self):
        """Connect client

        Give random name and accept client. Join to main group
        """
        logger.debug('connect')
        self.username = self.scope["session"].get("username", names.get_first_name())
        self.user_key = self.scope["session"].get("user_key", 'user_{}'.format(uuid.uuid4()))
        await self.accept()
        # Enter main        
        await self.main_joined()
        # Check rejoin
        room_key = self.scope["session"].get("room_key", None)
        if room_key is not None and room_container.room_exists(room_key):
            await self.confirm_rejoin(room_key)

    async def disconnect(self, close_code):
        """Disconnect
        
        Disconnect client and leave group
        """
        logger.debug('disconnect')
        # Leave room
        if self.room_key != MAIN_GROUP:
            logger.debug('leave room {}'.format(self.room_key))
            self.scope["session"]["room_key"] = self.room_key
            await self.room_left(self.room_key)
        else:
            self.scope["session"]["room_key"] = None
        # Leave main also
        await self.main_left()
        self.scope["session"]["username"] = self.username
        self.scope["session"]["user_key"] = self.user_key
        self.scope["session"].save()

    async def receive_json(self, content, **kwargs):
        logger.debug('receive_json')
        logger.debug(content)
        method = content['type']
        try:
            func = getattr(self, method)
            await func(content)
        except Exception:
            logger.exception("Error")

    #######################
    ### Public Handlers ###
    #######################

    async def create_room(self, _):
        """Create room and enter it
        """
        logger.debug('create_room')
        room = 'game_{}'.format(uuid.uuid4())
        await self.room_joined(room)

    async def join_room(self, event):
        """Join room
        
        Arguments:
            event {dict} -- socket event
        """
        logger.debug('join_room')
        logger.debug(event)
        room = event['room']
        await self.room_joined(room)

    async def leave_room(self, event):
        """Leave room
        
        Arguments:
            event {dict} -- socket event
        """
        logger.debug('leave_room')
        room = event['room']
        await self.room_left(room)
        await room_container.check_done(room)
        await self.main_changed()

    async def change_name(self, event):
        """Change user name
        It does not need to change name in room, allowed only in main groups
        
        Arguments:
            event {dict} -- socket event
        """
        logger.debug('change_name')
        if self.room_key == MAIN_GROUP:
            self.username = event['name']
        else:
            #TODO does not allowed
            pass

    async def choose(self, event):
        """Choose actions
        
        Arguments:
            event {dict} -- socket event
        """
        logger.debug('choose')
        await room_container.choose(self.room_key, self.user_key, event['target'], event['status'])

    async def add_job(self, event):
        """Add job
        
        Arguments:
            event {dict} -- socket event
        """
        logger.debug('add_job')
        room_container.add_job(self.room_key, event['job'])
        await self.job_changed(self.room_key)

    async def remove_job(self, event):
        """Remove job
        
        Arguments:
            event {dict} -- socket event
        """
        logger.debug('remove_job')
        room_container.remove_job(self.room_key, event['job'])
        await self.job_changed(self.room_key)

    async def get_jobs(self, _):
        """Get job list
        
        Arguments:
            event {dict} -- socket event
        """
        logger.debug('get_jobs')
        await self.send_json({
            'type': HandlerType.JOB_LIST,
            'data': job_list,
        })

    async def common_send(self, event):
        """Send messages to client
        
        Arguments:
            event {dict} -- socket event
        """
        logger.debug('common_send')
        msg = event.copy()
        msg['type'] = event['ret_type']
        msg.pop('ret_type', None)
        await self.send_json(msg)

    ########################
    ### Private Handlers ###
    ########################

    async def choose_changed(self, event):
        """Alert choose result
        
        Arguments:
            event {dict} -- socket event
        """
        logger.debug('choose_changed')
        await self.send_json(event)
        await room_container.check_done(self.room_key)

    async def main_initiated(self):
        """Send main groups information to client
        """
        logger.debug('main_intiated')        
        await self.send_json({
            'type': HandlerType.MAIN_INITIATED,
            'me': {
                'id': self.user_key,
                'name': self.username,
            },
            'room': self.room_key,
        })

    async def main_joined(self):
        """Join main group and alert
        """
        self.room_key = MAIN_GROUP
        await self.channel_layer.group_add(
            self.room_key,
            self.channel_name
        )
        await self.main_initiated()
        await self.main_changed()

    async def main_left(self):
        """Leave main group and alert
        """
        await self.channel_layer.group_discard(
            self.room_key,
            self.channel_name
        )
        await self.main_changed()

    async def main_changed(self):
        """Send changed main group information to client
        """
        logger.debug('main_changed')
        logger.debug(self.room_key)
        logger.debug(MAIN_GROUP)
        await self.channel_layer.group_send(
            MAIN_GROUP,
            {
                'type': HandlerType.COMMON_SEND,
                'ret_type': HandlerType.MAIN_CHANGED,
                'room_list': room_container.room_list(),
            }
        )

    async def room_initiated(self, room):
        """Send room information to client
        
        Arguments:
            room {str} -- group name
        """
        logger.debug('room_initiated')
        room_status = room_container.get_type(room)
        await self.send_json({
            'type': HandlerType.ROOM_INITIATED,
            'users': room_container.room_choice_list(room),
            'jobs': room_container.room_job_list(room),
            'room': room,
            'room_status': room_status,
            'team_mates': room_container.get_team_mates(room, self.user_key)
                if room_status != 0 else [],
            'job': room_container.get_user(room, self.user_key).job.name()
                if room_status != 0 else None,
            'targets': room_container.get_targets(room, self.user_key)
                if room_status == 3 else []
        })

    async def room_joined(self, group):
        """Join new group and alert
        
        Arguments:
            group {str} -- group key
        """
        logger.debug('room_joined {}'.format(group))
        await self.main_left()
        self.room_key = group
        # Join new group
        await self.channel_layer.group_add(
            self.room_key,
            self.channel_name
        )
        if room_container.get_user(self.room_key, self.user_key):
            await room_container.reconnect_user(self.room_key, self)
        else:
            await room_container.add_user(self.room_key, self)
        await self.main_changed()
        await self.room_initiated(group)

    async def room_left(self, group):
        """Leave prev group, join main group and alert
        
        Arguments:
            group {str} -- group key
        """
        await self.channel_layer.group_discard(
            group,
            self.channel_name
        )
        # Alert leave state
        await room_container.remove_user(group, self)
        # Join main group
        await self.main_joined()
        logger.debug('leave room {}'.format(group))

    async def job_changed(self, group):
        """Alert job changed result
        
        Arguments:
            event {dict} -- socket event
        """
        await self.channel_layer.group_send(
            group,
            {
                'type': HandlerType.COMMON_SEND,
                'ret_type': HandlerType.JOB_CHANGED,
                'jobs': room_container.room_job_list(group),
            }
        )
        await room_container.check_done(self.room_key)

    async def confirm_rejoin(self, room_key):
        """Confirm rejoin
        
        Arguments:
            room_key {str} -- group key
        """
        logger.debug("confirm_rejoin")
        await self.send_json({
            'type': HandlerType.CONFIRM_REJOIN,
            'room': room_key
        })

