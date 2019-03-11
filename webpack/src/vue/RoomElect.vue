<template>
	<div>
			<div style="width:100%; padding-top:100%; position:relative">
					<div id="canvas-container" style="position:absolute; top:0; left:0; width:100%; height:100%;">
							<!--<canvas id="my-canvas" width="500" height="500" style="width:100%; height:100%;">Your browser does not support the HTML5 canvas tag.</canvas>-->
					</div>
			</div>
			<div class="container-login100-form-btn m-t-30">
					<div @click="elect('fix')" class="login100-form-btn double-btn vote">
							{{ me.choice.status == 'fixed' && me.choice.target != null ? 'cancel':'fix' }}
					</div>
					<div @click="elect('abstain')" class="login100-form-btn double-btn night">
							{{ me.choice.status == 'fixed' && me.choice.target == null ? 'cancel':'abstain' }}
					</div>
			</div>
	</div>
</template>

<script>
import sender from '../sender'

    export default {
				props: ["me"],
				data: function() {
					return {
					}
				},
				methods: {
					elect: function(target) {
							if(target === 'fix')
									if (this.me.choice.target === null) alert('choose target user first');
									else if(this.me.choice.status === 'fixed') sender.choose(null, 'yet');
									else sender.choose(this.me.choice.target, 'fixed');
							else if(target === 'abstain')
									if(this.me.choice.status === 'fixed' && this.me.choice.target === null) sender.choose(null, 'yet');
									else sender.choose(null, 'fixed');
					}
				},
				mounted: function() {
					console.log(this.me);
				}
    }
</script>