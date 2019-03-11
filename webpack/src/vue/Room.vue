<template>
	<div>
		<div class="leave-icon">
				<i @click="leave_room" class="far fa-times-circle"></i>
		</div>
		<div class="tag-container">
				<span class="tag-label">members</span>
				<mafia-user-tag v-for="member in member_list" v-bind:member="member" :key="member.id"></mafia-user-tag>
		</div>
		<room-wait v-if="room_status === 0" :me="me" :jobs="jobs"></room-wait>
		<room-day v-else-if="room_status === 1" :me="me" :team_mates="team_mates"></room-day>
		<room-elect v-else-if="room_status === 2" :me="me"></room-elect>
		<room-night v-else-if="room_status === 3" :me="me" :team_mates="team_mates" :targets="targets" :member_list="member_list"></room-night>
	</div>
</template>

<script>
import MemberTag from './MemberTag.vue'
import RoomWait from './RoomWait.vue'
import RoomDay from './RoomDay.vue'
import RoomElect from './RoomElect.vue'
import RoomNight from './RoomNight.vue'
import sender from '../sender'

    export default {
				props: ['me', 'member_list', 'jobs', 'room_status', 'team_mates', 'room', 'targets'],
				data: function() {
					return {
					}
				},
				methods: {
					ready: function() {
							if(this.me.choice.status === 'yet')
									sender.choose('ready', 'fixed');
							else
									sender.choose(null, 'yet');
					},
					day_choose: function(target) {
							if(this.me.choice.status === 'yet')
									sender.choose(target, 'fixed');
							else
									sender.choose(null, 'yet');
					},
					elect: function(target) {
							if(target === 'fix')
									if (this.me.choice.target === null) alert('choose target user first');
									else if(this.me.choice.status === 'fixed') sender.choose(null, 'yet');
									else sender.choose(this.me.choice.target, 'fixed');
							else if(target === 'abstain')
									if(this.me.choice.status === 'fixed' && this.me.choice.target === null) sender.choose(null, 'yet');
									else sender.choose(null, 'fixed');
							else if(target === app.me.id || target === app.me.choice.target)
									sender.choose(null, 'yet');
							else
									sender.choose(target, 'tmp');
					},
					choose_target: function(target) {
							if(target === 'fix')
									if (this.me.choice.target === null) alert('choose target user first');
									else if(this.me.choice.status === 'fixed') sender.choose(null, 'yet');
									else sender.choose(this.me.choice.target, 'fixed');
							else if(target === 'abstain')
									if(this.me.choice.status === 'fixed' && this.me.choice.target === null) sender.choose(null, 'yet');
									else sender.choose(null, 'fixed');
							else if(target === app.me.choice.target)
									sender.choose(null, 'yet');
							else
									sender.choose(target, 'tmp');
					},
					add_job: sender.add_job,
					remove_job: sender.remove_job,
					get_jobs: sender.get_jobs,
					leave_room: function() {
							sender.leave_room(this.room)
					},
				},
				components: {
					'mafia-user-tag': MemberTag,
					'room-wait': RoomWait,
					'room-day': RoomDay,
					'room-elect': RoomElect,
					'room-night': RoomNight,
				}
    }
</script>