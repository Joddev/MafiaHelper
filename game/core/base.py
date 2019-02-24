import logging
from collections import Counter
from random import shuffle
from game.core.job import *

logger = logging.getLogger('mafia')


class RoomStatus:

    @classmethod
    def job_default(cls):
        return {
            'instance': None,
            'count': 1,
        }

    def __init__(self, room_name, users=None, jobs=None):
        self.room_name = room_name
        if users is not None:
            self.users = [User(user.key, user.name) for user in users]
        else:
            self.users = []
        self.choices = [Choice(user) for user in self.users]
        if jobs is not None:
            from_jobs = {}
            for job in jobs:
                from_jobs[job] = {
                    'instance': None,
                    'count': jobs[job]['count']
                }
            self.jobs = from_jobs
        else:
            self.jobs = {
                JobEnum.citizen.name: RoomStatus.job_default(),
                JobEnum.police.name: RoomStatus.job_default(),
                JobEnum.doctor.name: RoomStatus.job_default(),
                JobEnum.mafia.name: RoomStatus.job_default(),
            }
        self.order = 0
        self.type = None

    def add_user(self, user):
        self.users.append(user)
        self.choices.append(Choice(user))

    def remove_user(self, user):
        self.users.remove(user)
        self.choices = [choice for choice in self.choices if choice.user != user]

    def add_job(self, job):
        if job.name in self.jobs:
            self.jobs[job.name]['count'] += 1
        else:
            self.jobs[job.name] = RoomStatus.job_default()

    def remove_job(self, job):
        if job.name in self.jobs:
            self.jobs[job.name]['count'] -= 1
            if self.jobs[job.name]['count'] < 1:
                self.jobs.pop(job.name, None)

    def job_count_list(self):
        return [{'job': job, 'count': self.jobs[job]['count']} for job in self.jobs]

    def choose(self, user, target, status):
        choice = next(choice for choice in self.choices if choice.user == user)
        choice.choose(target, status)

    def choose_done(self):
        return all(not choice.user.can_act() or choice.status == Choice.Status.FIXED for choice in self.choices)

    def clear_choices(self):
        for choice in self.choices:
            choice.target = None
            choice.status = Choice.Status.YET

    def increase_order(self):
        self.order += 1

    def can_start(self):
        return len(self.users) == sum(self.jobs[job]['count'] for job in self.jobs)

    def shuffle_jobs(self):
        if self.can_start():
            job_list = []
            for job in self.jobs:
                self.jobs[job]['instance'] = JobEnum.get_by_name(job).value()
                for i in range(self.jobs[job]['count']):
                    job_list.append(job)
            shuffle(job_list)
            for user, job_name in zip(self.users, job_list):
                user.job = self.jobs[job_name]['instance']

    def clear_temporary_status(self):
        for user in self.users:
            user.clear_temporary_status()

    def game_done(self):
        try:
            groups = set(user.job.group for user in self.users)
            for group in groups:
                if group.do_win(self):
                    return group
        except AttributeError:
            return None
        return None


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


class RoomProcessor:

    def __init__(self, room_status):
        self.room_status = room_status
        room_status.clear_choices()

    def get_user(self, user_key):
        try:
            return next(user for user in self.room_status.users if user.key == user_key)
        except StopIteration:
            return None

    def add_user(self, user_key, user_name):
        raise NotImplementedError

    def remove_user(self, user_key):
        raise NotImplementedError

    def get_user_list(self):
        return self.room_status.users

    def get_choice_list(self):
        return self.room_status.choices

    def reconnect_user(self, user_key):
        user = self.get_user(user_key)
        if user:
            user.connected = True
            return True
        else:
            return False

    def disconnect_user(self, user_key):
        user = self.get_user(user_key)
        if user:
            user.connected = False
            return True
        else:
            return False

    def choose_limit(self, user, target, status):
        return user.can_act()

    def choose(self, user_key, target, status):
        user = self.get_user(user_key)
        if user and self.choose_limit(user, target, status):
            self.room_status.choose(user, target, status)
            return True
        else:
            return False

    def add_job(self, job_name):
        raise NotImplementedError

    def remove_job(self, job_name):
        raise NotImplementedError

    def get_job_list(self):
        return self.room_status.job_count_list()

    def result(self):
        raise NotImplementedError

    def done(self):
        return self.room_status.choose_done()

    def get_type(self):
        raise NotImplementedError

    def game_done(self):
        return self.room_status.game_done()


class WaitingRoom(RoomProcessor):

    def __init__(self, room_status):
        super().__init__(room_status)
        self.room_status.type = WaitingRoom

    def add_user(self, user_key, user_name):
        user = self.get_user(user_key)
        if not user:
            user = User(user_key, user_name)
            self.room_status.add_user(user)
            return True
        else:
            logger.error("try to add user duplicated")
            return False

    def remove_user(self, user_key):
        user = self.get_user(user_key)
        if user:
            self.room_status.remove_user(user)
            return True
        else:
            return False

    def disconnect_user(self, user_key):
        self.remove_user(user_key)

    def add_job(self, job_name):
        job = JobEnum.get_by_name(job_name)
        if job:
            self.room_status.add_job(job)
            return True
        else:
            return False

    def remove_job(self, job_name):
        job = JobEnum.get_by_name(job_name)
        if job:
            self.room_status.remove_job(job)
            return True
        else:
            return False

    def choose_limit(self, user, target, status):
        if super().choose_limit(user, target, status):
            if target == 'ready' and status == Choice.Status.FIXED:
                return True
            elif status == Choice.Status.YET:
                return True
        return False

    def done(self):
        return super().done() and self.room_status.can_start()

    def result(self):
        if self.done():
            self.room_status.shuffle_jobs()
            return self.room_status.users
        return False

    def next_phase(self):
        self.room_status.increase_order()
        self.room_status.clear_temporary_status()
        return DayRoom(self.room_status)

    def get_type(self):
        return 0


class DayRoom(RoomProcessor):

    def __init__(self, room_status):
        super().__init__(room_status)
        self.room_status.type = DayRoom

    def add_user(self, user_key, user_name):
        self.get_user(user_key).connected = True

    def remove_user(self, user_key):
        self.get_user(user_key).connected = False

    def choose_limit(self, user, target, status):
        if super().choose_limit(user, target, status):
            if target in ['election', 'night'] and status == Choice.Status.FIXED:
                return True
            elif status == Choice.Status.YET:
                return True
        return False

    def next_phase(self):
        if not self.done():
            return False
        self.room_status.clear_temporary_status()
        target = Counter(choice.target for choice in self.room_status.choices).most_common(1)[0][0]
        if target == 'election':
            return ElectionRoom(self.room_status)
        else:
            return NightRoom(self.room_status)

    def result(self):
        return None

    def get_type(self):
        return 1


class ElectionRoom(RoomProcessor):

    def __init__(self, room_status):
        super().__init__(room_status)
        self.room_status.type = ElectionRoom

    def add_user(self, user_key, user_name):
        self.get_user(user_key).connected = True

    def remove_user(self, user_key):
        self.get_user(user_key).connected = False

    def choose_limit(self, user, target, status):
        if super().choose_limit(user, target, status):
            if any(target == user.key and user.can_act() for user in self.room_status.users) and \
                    status in [Choice.Status.FIXED, Choice.Status.TMP]:
                return True
            elif status == Choice.Status.YET:
                return True
            elif target is None:
                return True
        return False

    def result(self):
        if not self.done():
            return False
        target_key, times = Counter(choice.target for choice in self.room_status.choices).most_common(1)[0]
        target_user = self.get_user(target_key)
        if target_user and times > sum(1 for choice in self.room_status.choices if choice.user.can_act())/2:
            target_user.executed()
            return target_user
        else:
            return False

    def next_phase(self):
        self.room_status.clear_temporary_status()
        return NightRoom(self.room_status)

    def get_type(self):
        return 2


class ActionProcessor:

    def __init__(self, act_list):
        self.act_list = act_list
        self.act_list.sort(key=lambda act: act[0].order)

    def process(self):
        result_list = []
        for job, target in self.act_list:
            result = job.act(target)
            if result is not None:
                result_list.append(result)
        return result_list


class NightRoom(RoomProcessor):

    def __init__(self, room_status):
        super().__init__(room_status)
        self.room_status.type = NightRoom

    def add_user(self, user_key, user_name):
        self.get_user(user_key).connected = True

    def remove_user(self, user_key):
        self.get_user(user_key).connected = False

    def choose_limit(self, user, target, status):
        if super().choose_limit(user, target, status):
            if target is None or status == Choice.Status.YET:
                return True
            target_user = self.get_user(target)
            if target_user and user.job.can_target(target_user, self.room_status):
                return True
        return False

    def result(self):
        if not self.done():
            return False
        action_list = []
        for job_name in self.room_status.jobs:
            job = self.room_status.jobs[job_name]['instance']
            if not job.can_act(self.room_status):
                continue
            try:
                target_key = Counter(choice.target for choice in self.room_status.choices
                                     if choice.user.job == job and choice.target is not None).most_common(1)[0][0]
                if target_key is not None:
                    action_list.append((job, self.get_user(target_key)))
            except IndexError:
                pass
        processor = ActionProcessor(action_list)
        return processor.process()

    def next_phase(self):
        self.room_status.clear_temporary_status()
        for user in self.room_status.users:
            user.clear_temporary_status()
        self.room_status.increase_order()
        return DayRoom(self.room_status)

    def done(self):
        return all(choice.status == Choice.Status.FIXED for choice in self.room_status.choices
                   if choice.user.can_act() and choice.user.job.can_act(self.room_status))

    def get_type(self):
        return 3
