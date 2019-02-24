from enum import Enum


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


class Group:
    pass


class CitizenGroup(Group):
    @classmethod
    def do_win(cls, status):
        return all(user.job.group == cls for user in status.users if user.can_act())

    @classmethod
    def dict(cls):
        return 'citizen_group'


class MafiaGroup(Group):
    @classmethod
    def do_win(cls, status):
        return len([user for user in status.users if user.can_act() and user.job.group == cls]) \
               >= len([user for user in status.users if user.can_act()]) / 2

    @classmethod
    def dict(cls):
        return 'mafia_group'


citizen_group = CitizenGroup()
mafia_group = MafiaGroup()


class Job:
    def __init__(self):
        self.order = 100

    def can_act(self, room_status):
        return False

    def can_target(self, user, room_status):
        return False

    def act(self, target):
        return None

    def name(self):
        return self.__class__.__name__.lower()

    def visible_team(self):
        return True


class Citizen(Job):

    def __init__(self):
        super().__init__()
        self.group = CitizenGroup

    def visible_team(self):
        return False


class Police(Citizen):

    def __init__(self):
        super().__init__()
        self.order = 50

    def can_act(self, room_status):
        return True

    def can_target(self, user, room_status):
        return user.can_act()

    def act(self, target):
        result = {
            'target': target,
            'confirmation': type(target.job) == Mafia
        }
        return ActResult('bool', 'police', result)

    def visible_team(self):
        return True


class Doctor(Citizen):

    def __init__(self):
        super().__init__()
        self.order = 30

    def can_act(self, room_status):
        return True

    def can_target(self, user, room_status):
        return user.can_act()

    def act(self, target):
        target.status = User.Status.SAVED
        return None

    def visible_team(self):
        return True


class Mafia(Job):

    def __init__(self):
        super().__init__()
        self.group = MafiaGroup
        self.order = 70

    def can_act(self, room_status):
        return True

    def can_target(self, user, room_status):
        return user.can_act()

    def act(self, target):
        if target.status == User.Status.SAVED:
            target.status = User.Status.ALIVE
            return None
        else:
            target.status = User.Status.DEAD
            return ActResult('user', 'all', target)


class ActResult:
    def __init__(self, result_type, scope, result):
        """
        :param str result_type:
            user - return result type User
            bool - return target with boolean result
        :param str scope:
            all - notify result to all users
            job - notify result to users with specific job
        """
        self.result_type = result_type
        self.scope = scope
        self.result = result

    def dict(self):
        if self.result_type == 'user':
            return {
                'result_type': self.result_type,
                'result': self.result.dict()
            }
        elif self.result_type == 'bool':
            return {
                'result_type': self.result_type,
                'result': {
                    'target': self.result['target'].key,
                    'confirmation': self.result['confirmation']
                }
            }
        return self.__dict__


class JobEnum(Enum):
    citizen = Citizen
    doctor = Doctor
    police = Police
    mafia = Mafia

    @classmethod
    def get_by_name(cls, name):
        try:
            return cls[name.lower()]
        except KeyError:
            return None
