from enum import Enum
from game.core.base import User

###################
### Game Groups ###
###################


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

#################
### Game Jobs ###
#################


class Job:
    """Base abstract class for all jobs
    
    Attributes:
        order {int} -- order of job execution (job action with less order will be excuted early)
    """

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
        """Can this job members recongnize each other
        """
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
        # it must be ahead of killers
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

        Arguemtns:
            result_type {str}
                'user' -- return result type User
                'bool' -- return target with boolean result
            scope {str}
                'all' -- notify result to all users
                'job' -- notify result to users with specific job
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
