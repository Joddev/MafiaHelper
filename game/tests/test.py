from game.core.base import *
from django.test import TestCase


class MyTest(TestCase):

    def setUp(self):
        self.room_name = 'room_name'
        self.room_status = RoomStatus('room_name')
        self.user1 = User('key1', 'name1')
        self.user2 = User('key2', 'name2')
        self.user3 = User('key3', 'name3')
        self.user4 = User('key4', 'name4')
        self.user5 = User('key5', 'name5')

    def test_init_default_room_status(self):
        room_status = RoomStatus(self.room_name)
        self.assertEqual(room_status.room_name, self.room_name)
        self.assertEqual(len(room_status.users), 0)
        self.assertEqual(len(room_status.choices), 0)
        self.assertDictEqual(room_status.jobs, {
            JobEnum.citizen.name: 1,
            JobEnum.police.name: 1,
            JobEnum.doctor.name: 1,
            JobEnum.mafia.name: 1,
        })
        self.assertEqual(room_status.order, 0)
        self.assertIsNone(room_status.type)

    def test_init_users_room_status(self):
        room_status = RoomStatus(self.room_name, [self.user1, self.user2])
        self.assertEqual(room_status.room_name, self.room_name)
        self.assertEqual(len(room_status.users), 2)
        self.assertEqual(len(room_status.choices), 2)
        self.assertDictEqual(room_status.jobs, {
            JobEnum.citizen.name: 1,
            JobEnum.police.name: 1,
            JobEnum.doctor.name: 1,
            JobEnum.mafia.name: 1,
        })
        self.assertEqual(room_status.order, 0)
        self.assertIsNone(room_status.type)

    def test_job_related_room_status(self):
        self.room_status.add_job(JobEnum.citizen)
        self.assertDictEqual(self.room_status.jobs, {
            JobEnum.citizen.name: 2,
            JobEnum.police.name: 1,
            JobEnum.doctor.name: 1,
            JobEnum.mafia.name: 1,
        })
        self.room_status.remove_job(JobEnum.police)
        self.assertDictEqual(self.room_status.jobs, {
            JobEnum.citizen.name: 2,
            JobEnum.doctor.name: 1,
            JobEnum.mafia.name: 1,
        })
        self.room_status.add_job(JobEnum.police)
        self.assertDictEqual(self.room_status.jobs, {
            JobEnum.citizen.name: 2,
            JobEnum.police.name: 1,
            JobEnum.doctor.name: 1,
            JobEnum.mafia.name: 1,
        })

    def test_user_related_room_status(self):
        self.room_status.add_user(self.user1)
        self.assertListEqual(self.room_status.users, [self.user1])
        self.assertTrue(len(self.room_status.choices) == 1)
        self.assertTrue(any(choice.user == self.user1 for choice in self.room_status.choices))
        self.room_status.add_user(self.user2)
        self.assertListEqual(self.room_status.users, [self.user1, self.user2])
        self.assertTrue(len(self.room_status.choices) == 2)
        self.assertTrue(any(choice.user == self.user1 for choice in self.room_status.choices))
        self.assertTrue(any(choice.user == self.user2 for choice in self.room_status.choices))
        self.room_status.remove_user(self.user1)
        self.assertListEqual(self.room_status.users, [self.user2])
        self.assertTrue(len(self.room_status.choices) == 1)
        self.assertFalse(any(choice.user == self.user1 for choice in self.room_status.choices))
        self.assertTrue(any(choice.user == self.user2 for choice in self.room_status.choices))

    def test_choice_related_room_status(self):
        self.room_status.add_user(self.user1)
        self.room_status.add_user(self.user2)
        self.assertFalse(self.room_status.choose_done())
        self.room_status.choose(self.user1, 'target', Choice.Status.FIXED)
        self.room_status.choose(self.user2, 'target', Choice.Status.FIXED)
        self.assertTrue(self.room_status.choose_done())

    def test_waiting_room(self):
        waiting_room = WaitingRoom(self.room_status)

        # simple addition
        self.assertTrue(waiting_room.add_user('key1', 'name1'))
        self.assertTrue(any(user.key == 'key1' for user in self.room_status.users) and len(self.room_status.users) == 1)
        self.assertTrue(waiting_room.add_user('key2', 'name2'))
        self.assertTrue(any(user.key == 'key2' for user in self.room_status.users) and len(self.room_status.users) == 2)
        # simple removal
        self.assertTrue(waiting_room.remove_user('key1'))
        self.assertTrue(not any(user.key == 'key1' for user in self.room_status.users) and len(self.room_status.users) == 1)
        # removal fail
        self.assertFalse(waiting_room.remove_user('key1'))
        # duplicated addition
        self.assertTrue(waiting_room.add_user('key1', 'name1'))
        self.assertFalse(waiting_room.add_user('key1', 'name1'))
        # simple job removal
        self.assertTrue(waiting_room.remove_job('Doctor'))
        self.assertTrue(waiting_room.remove_job('citizen'))
        # choose test
        self.assertTrue(waiting_room.choose('key1', 'ready', Choice.Status.FIXED))
        self.assertTrue(waiting_room.choose('key1', None, Choice.Status.YET))
        self.assertFalse(waiting_room.done())
        # choose fail
        self.assertFalse(waiting_room.choose('key3', 'ready', Choice.Status.FIXED))
        self.assertFalse(waiting_room.choose('key2', 'ready2', Choice.Status.FIXED))
        # done
        self.assertTrue(waiting_room.choose('key1', 'ready', Choice.Status.FIXED))
        self.assertTrue(waiting_room.choose('key2', 'ready', Choice.Status.FIXED))
        self.assertTrue(waiting_room.result())
        self.assertTrue(all(user.job for user in self.room_status.users))
        self.assertEqual(DayRoom, type(waiting_room.next_phase()))
        self.assertEqual(self.room_status.order, 1)

    def test_day_room(self):
        self.room_status.add_user(User('key1', 'name1'))
        self.room_status.add_user(User('key2', 'name2'))
        self.room_status.add_user(User('key3', 'name3'))
        day_room = DayRoom(self.room_status)

        # choose test
        self.assertTrue(day_room.choose('key1', None, Choice.Status.YET))
        self.assertTrue(day_room.choose('key1', 'election', Choice.Status.FIXED))
        self.assertFalse(day_room.done())
        # choose fail
        self.assertFalse(day_room.choose('key1', 'election', Choice.Status.TMP))
        self.assertFalse(day_room.choose('key4', 'election', Choice.Status.FIXED))
        # done
        self.assertFalse(day_room.done())
        self.assertTrue(day_room.choose('key2', 'election', Choice.Status.FIXED))
        self.assertTrue(day_room.choose('key3', 'night', Choice.Status.FIXED))
        self.assertTrue(day_room.done())
        # next
        self.assertEqual(ElectionRoom, type(day_room.next_phase()))
        self.assertTrue(day_room.choose('key2', 'night', Choice.Status.FIXED))
        self.assertEqual(NightRoom, type(day_room.next_phase()))

    def test_election_room(self):
        self.room_status.add_user(self.user1)
        self.room_status.add_user(self.user2)
        self.room_status.add_user(self.user3)
        election_room = ElectionRoom(self.room_status)

        # choose test
        self.assertTrue(election_room.choose(self.user1.key, None, Choice.Status.YET))
        self.assertTrue(election_room.choose(self.user1.key, None, Choice.Status.TMP))
        self.assertTrue(election_room.choose(self.user1.key, self.user2.key, Choice.Status.FIXED))
        self.assertFalse(election_room.done())
        # choose fail
        self.assertFalse(election_room.choose(self.user1.key, 'election', Choice.Status.TMP))
        self.assertFalse(election_room.choose('key4', self.user1.key, Choice.Status.FIXED))
        # election result target
        self.assertFalse(election_room.done())
        self.assertTrue(election_room.choose(self.user2.key, self.user1.key, Choice.Status.FIXED))
        self.assertTrue(election_room.choose(self.user3.key, self.user2.key, Choice.Status.FIXED))
        self.assertEqual(election_room.result(), self.user2)
        self.assertEqual(self.user2.status, User.Status.DEAD)
        # election with two result None
        self.room_status.clear_choices()
        self.assertFalse(election_room.choose(self.user2.key, self.user1.key, Choice.Status.FIXED))
        self.assertFalse(election_room.choose(self.user1.key, self.user2.key, Choice.Status.FIXED))
        self.assertTrue(election_room.choose(self.user1.key, self.user3.key, Choice.Status.FIXED))
        self.assertTrue(election_room.choose(self.user3.key, None, Choice.Status.FIXED))
        self.assertFalse(election_room.result())
        self.assertEqual(NightRoom, type(election_room.next_phase()))

    def test_night_room(self):
        self.room_status.add_user(self.user1)
        self.room_status.add_user(self.user2)
        self.room_status.add_user(self.user3)
        self.room_status.add_user(self.user4)
        self.room_status.add_user(self.user5)
        night_room = NightRoom(self.room_status)
        # set job
        self.user1.job = JobEnum.citizen.value
        self.user2.job = JobEnum.police.value
        self.user3.job = JobEnum.doctor.value
        self.user4.job = JobEnum.mafia.value
        self.user5.job = JobEnum.mafia.value
        self.room_status.jobs = {
            JobEnum.citizen.name: 1,
            JobEnum.police.name: 1,
            JobEnum.doctor.name: 1,
            JobEnum.mafia.name: 2,
        }

        # choose test
        self.assertFalse(night_room.choose(self.user1.key, 'Fail', Choice.Status.TMP))
        self.assertFalse(night_room.choose(self.user1.key, self.user2.key, Choice.Status.TMP))
        self.assertTrue(night_room.choose(self.user2.key, self.user4.key, Choice.Status.TMP))
        self.assertTrue(night_room.choose(self.user2.key, self.user1.key, Choice.Status.FIXED))
        self.assertTrue(night_room.choose(self.user3.key, self.user3.key, Choice.Status.FIXED))
        self.assertTrue(night_room.choose(self.user4.key, self.user1.key, Choice.Status.FIXED))
        self.assertTrue(night_room.choose(self.user5.key, self.user3.key, Choice.Status.FIXED))
        self.assertTrue(night_room.done())
        print('done')
        print(night_room.result())
