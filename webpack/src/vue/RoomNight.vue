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
					<mafia-user-tag class="team" v-for="mate in team_mates" :member="mate" :target="true" :member_list="member_list" :key="mate.id"></mafia-user-tag>
			</div>
			<div class="tag-container m-t-30">
					<span class="tag-label">targets</span>
					<mafia-user-tag v-for="member in targets" @click.native="choose_target(member.id)" :member="member" :key="member.id"></mafia-user-tag>
					<span v-show="targets.length == 0">You can not choose target users.</span>
			</div>
			<div class="container-login100-form-btn m-t-30">
					<div @click="choose_target('fix', 'fixed')" class="login100-form-btn double-btn vote">
							{{ me.choice.status == 'fixed' && me.choice.target != null ? 'cancel':'fix' }}
					</div>
					<div @click="choose_target('abstain', 'fixed')" class="login100-form-btn double-btn night">
							{{ me.choice.status == 'fixed' && me.choice.target == null ? 'cancel':'abstain' }}
					</div>
			</div>
	</div>
</template>

<script>
import sender from '../sender'

    export default {
				props: ['me', 'team_mates', 'targets', 'member_list'],
				data: function() {
					return {
					}
				},
				methods: {
					choose_target: function(target) {
							if(target === 'fix')
									if (this.me.choice.target === null) alert('choose target user first');
									else if(this.me.choice.status === 'fixed') sender.choose(null, 'yet');
									else sender.choose(this.me.choice.target, 'fixed');
							else if(target === 'abstain')
									if(this.me.choice.status === 'fixed' && this.me.choice.target === null) sender.choose(null, 'yet');
									else sender.choose(null, 'fixed');
							else if(target === this.me.choice.target)
									sender.choose(null, 'yet');
							else
									sender.choose(target, 'tmp');
					},
					get_jobs: sender.get_jobs,
				},
    }
</script>