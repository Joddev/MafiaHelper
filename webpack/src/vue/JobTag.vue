<template>
	<span class="tag job" @click="handler(job)">
		<template v-if="count">
			{{ job }}: {{ count }}
			<i @click="add_job(job)" class="fas fa-caret-up"></i>
			<i @click="remove_job(job)" class="fas fa-caret-down"></i>
		</template>
		<template v-else>
			{{ job }}
			<template v-if="detail">
				<div class="job-tooltip">
					<i class="fas fa-moon"></i>
					<div class="job-tooltip-holder"><span class="job-tooltiptext">{{ action(job) }}</span></div>
				</div>
				<div class="job-tooltip">
					<i class="fas fa-crosshairs"></i>
					<div class="job-tooltip-holder"><span class="job-tooltiptext">{{ mission(job) }}</span></div>
				</div>
			</template>
		</template>
	</span>
</template>

<script>
	import sender from '../sender'

	export default {
		props: {
			job: {
				type: String,
				required: true
			},
			count: {
				type: Number,
				required: false
			},
			detail: {
				type: Boolean,
				default: false
			},
			handler: {
				type: Function,
				required: false,
				default: (job) => {					
				}
			}
		},		
		methods: {
			add_job: sender.add_job,
			remove_job: sender.remove_job,
			action: function (job) {
				switch (job) {
					case 'citizen':
						return 'no action'
					case 'police':
						return 'ascertain that someone is mafia every night'
					case 'doctor':
						return 'protect someone from death every night'
					case 'mafia':
						return 'kill someone every night'
					default:
						return 'unknown'
				}
			},
			mission: function (job) {
				switch (job) {
					case 'citizen':
					case 'police':
					case 'doctor':
						return 'get rid of all except citizen group'
					case 'mafia':
						return 'hold a majority'
					default:
						return 'unknown'
				}
			}
		}
	}
</script>

<style scoped>
	.job-tooltip {		
    display: inline-block;
		cursor: 'default';
	}
	.job-tooltip .job-tooltiptext {
		visibility: hidden;
		background-color: #000;
		color: #fff;
		text-align: center;
		padding: 3px 6px;
		border-radius: 6px;
    white-space: nowrap;
		position: absolute;
		z-index: 1;
    top: -60px;
    left: -20px;
	}
	.job-tooltip:hover .job-tooltiptext {
		visibility: visible;
	}
	.job-tooltip-holder {
		position: relative;
	}
	.tag.job {
		background-color: #2f5773;
	}
	.fas:hover {
		color: #d82e2e
	}
	.fas.fa-moon:hover {
		color: #e4e028;
	}
	.fas.fa-crosshairs:hover {
		color: #f53ecc;
	}
</style>