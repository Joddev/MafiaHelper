import logging
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
