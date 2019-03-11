<template>
	<div>
			<div class="tag-container m-t-30">
					<span class="tag-label">jobs</span>
					<span v-for="elem in jobs" class="tag job" :key=elem.job>
							{{ elem.job }}: {{ elem.count }}
							<i @click="add_job(elem.job)" class="fas fa-caret-up"></i>
							<i @click="remove_job(elem.job)" class="fas fa-caret-down"></i>
					</span>
					<i @click="get_jobs" class="fas fa-plus-circle" style="color:#2f5773"></i>
			</div>
			<div @click="ready()" class="container-login100-form-btn m-t-30">
					<div class="login100-form-btn">
							{{ me.choice.status == 'yet'? 'ready':'cancel' }}
					</div>
					<!--<span style="position:absolute; bottom:-22px; color:#ff6868;">{{ ready_msg }}</span>-->
			</div>
	</div>
</template>

<script>
import sender from '../sender'

    export default {
				props: ['me', 'jobs'],
				data: function() {
					return {
					}
				},
				methods: {
					get_jobs: sender.get_jobs,
					ready: function() {
							if(this.me.choice.status === 'yet')
									sender.choose('ready', 'fixed');
							else
									sender.choose(null, 'yet');
					},
					add_job: sender.add_job,
					remove_job: sender.remove_job,
				}
    }
</script>