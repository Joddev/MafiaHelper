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

    user = None
    group = None
    name = None

    async def connect(self):
        self.name = names.get_first_name()
        await self.accept()
        await self.join_main()
        # Join main group
        # self.group = MAIN_GROUP
        # await self.channel_layer.group_add(
        #     self.group,
        #     self.channel_name
        # )
        # # Accept
        # # Initiate
        # await self.main_changed()

    async def disconnect(self, close_code):
        logger.info('disconnect')
        # Leave room
        if self.group != MAIN_GROUP:
            logger.info('leave room {}'.format(self.group))
            await self._leave_room(self.group)
        # Leave main also
        await self.leave_main()

    async def receive_json(self, content, **kwargs):
        print('receive_json')
        print(content)

        method = content['type']
        try:
            func = getattr(self, method)
            await func(content)
        except Exception:
            logger.exception("Error")

        # if content['type'] == HandlerType.CREATE_ROOM:
        #     await self.create_room(content)
        # elif content['type'] == HandlerType.JOIN_ROOM:
        #     await self.join_room(content)
        # else:
        #     await self.channel_layer.group_send(
        #         self.group,
        #         content
        #     )

    async def room_initiated(self, room):
        await self.send_json({
            'type': HandlerType.ROOM_INITIATED,
            'users': room_container.room_choice_list(room),
            'jobs': room_container.room_job_list(room),
            'room': room,
        })

    async def main_initiated(self):
        await self.send_json({
            'type': HandlerType.MAIN_INITIATED,
            'me': {
                'id': self.channel_name,
                'name': self.name,
            },
            'room': self.group,
        })

    async def main_changed(self):
        logger.info('main_changed')
        await self.channel_layer.group_send(
            MAIN_GROUP,
            {
                'type': HandlerType.COMMON_SEND,
                'ret_type': HandlerType.MAIN_CHANGED,
                'room_list': room_container.room_list(),
            }
        )

    async def create_room(self, _):
        logger.info('create_room')
        room = 'game_{}'.format(uuid.uuid4())
        await self._enter_room(room)

    async def join_room(self, event):
        logger.info('join_room')
        room = event['room']
        await self._enter_room(room)

    async def leave_room(self, event):
        logger.info('leave_room')
        room = event['room']
        await self._leave_room(room)
        await room_container.check_done(room)
        await self.main_changed()

    async def change_name(self, event):
        self.name = event['name']

    async def choose(self, event):
        await room_container.choose(self.group, self.channel_name, event['target'], event['status'])

    async def choose_changed(self, event):
        await self.send_json(event)
        await room_container.check_done(self.group)

    async def job_changed(self, group):
        await self.channel_layer.group_send(
            group,
            {
                'type': HandlerType.COMMON_SEND,
                'ret_type': HandlerType.JOB_CHANGED,
                'jobs': room_container.room_job_list(group),
            }
        )
        await room_container.check_done(self.group)

    async def add_job(self, event):
        room_container.add_job(self.group, event['job'])
        await self.job_changed(self.group)

    async def remove_job(self, event):
        room_container.remove_job(self.group, event['job'])
        await self.job_changed(self.group)

    async def get_jobs(self, _):
        await self.send_json({
            'type': HandlerType.JOB_LIST,
            'data': job_list,
        })

    async def common_send(self, event):
        # event 변경 하지 말것
        logger.info('common_send')
        msg = event.copy()
        msg['type'] = event['ret_type']
        msg.pop('ret_type', None)
        await self.send_json(msg)

    async def leave_main(self):
        await self.channel_layer.group_discard(
            self.group,
            self.channel_name
        )
        await self.main_changed()

    async def join_main(self):
        self.group = MAIN_GROUP
        await self.channel_layer.group_add(
            self.group,
            self.channel_name
        )
        await self.main_initiated()
        await self.main_changed()

    async def _enter_room(self, group):
        logger.info('_enter_room {}'.format(group))
        await self.leave_main()
        self.group = group
        # Join new group
        await self.channel_layer.group_add(
            self.group,
            self.channel_name
        )
        await room_container.add_user(self.group, self)
        await self.main_changed()
        await self.room_initiated(group)

    # Leave room group
    async def _leave_room(self, group):
        await self.channel_layer.group_discard(
            group,
            self.channel_name
        )
        # Alert leave state
        await room_container.remove_user(group, self)
        # Join main group
        await self.join_main()
        logger.info('leave room {}'.format(group))
