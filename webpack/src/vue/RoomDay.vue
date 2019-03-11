<template>
	<div>
			<div class="tag-container m-t-30">
					<span class="tag-label">job</span>
					<span class="tag job">
							{{ me.job }}
					</span>
					<i @click="get_jobs" class="far fa-question-circle" style="color:#2f5773"></i>
			</div>
			<div class="tag-container m-t-30">
					<span class="tag-label">teammates</span>
					<mafia-user-tag class="team" v-for="mate in team_mates" v-bind:member="mate" :key="mate.id"></mafia-user-tag>
			</div>
			<div class="container-login100-form-btn m-t-30">
					<div @click="day_choose('election')" class="login100-form-btn double-btn vote">
							{{ me.choice.target == 'election'? 'cancel':'election' }}
					</div>
					<div @click="day_choose('night')" class="login100-form-btn double-btn night">
							{{ me.choice.target == 'night'? 'cancel':'night' }}
					</div>
			</div>
	</div>
</template>

<script>
import sender from '../sender'

    export default {
				props: ['me', 'team_mates'],
				data: function() {
					return {
					}
				},
				methods: {
					day_choose: function(target) {
							if(this.me.choice.status === 'yet')
									sender.choose(target, 'fixed');
							else
									sender.choose(null, 'yet');
					},
					get_jobs: sender.get_jobs,
				}
    }
</script>