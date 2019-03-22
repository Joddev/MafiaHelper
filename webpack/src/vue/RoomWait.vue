<template>
	<div>
			<div class="tag-container m-t-30">
					<span class="tag-label">jobs</span>
					<job-tag v-for="elem in jobs" :key=elem.job v-bind=elem></job-tag>
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
    import JobTag from './JobTag'

    export default {
				props: ['me', 'jobs'],
				data: function() {
					return {
					}
				},
        components: {
            'job-tag': JobTag
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