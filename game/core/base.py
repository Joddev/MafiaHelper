import logging
from enum import Enum

logger = logging.getLogger('mafia')


class User:
    class Status(str, Enum):
        DEAD = 'dead'
        ALIVE = 'alive'
        SAVED = 'saved'

    def __init__(self, user_key, user_name):
        self.key = user_key
        self.name = user_name
        self.status = User.Status.ALIVE
        self.connected = True
        self.job = None

    def can_act(self):
        return self.status != User.Status.DEAD and self.connected

    def executed(self):
        self.status = User.Status.DEAD

    def clear_temporary_status(self):
        if self.status == User.Status.SAVED:
            self.status = User.Status.ALIVE
        if self.Status != User.Status.DEAD and not self.connected:
            self.status = User.Status.DEAD

    def dict(self):
        return {
            'id': self.key,
            'name': self.name,
            'status': self.status.value,
            'connected': self.connected,
            # 'job': self.job.name() if self.job else None
        }


class Choice:
    class Status(str, Enum):
        YET = 'yet'
        TMP = 'tmp'
        FIXED = 'fixed'

    def __init__(self, user):
        self.user = user
        self.status = Choice.Status.YET
        self.target = None

    def choose(self, target, status):
        self.target = target
        self.status = status

    def dict(self):
        return {
            'target': self.target,
            'status': self.status.value
        }

    def user_dict(self):
        result = self.user.dict()
        result['choice'] = self.dict()
        return result
