<template>
<div>
		<span class="tag name" @click="change_name">
				{{ me.name }} <i class="fas" v-bind:class="{ 'fa-check': edit_name, 'fa-pencil-alt': !edit_name }"></i>
		</span>
		<input ref="editor" v-model="me.name" class="input-tag" v-show="edit_name" @keyup.enter="change_name">
		<mafia-room v-for="room in room_list" v-bind:room="room" @click.native="join_room(room)" :key="room.name"></mafia-room>
		<div @click="create_room" class="container-login100-form-btn m-t-30">
				<div class="login100-form-btn">
						+ create room
				</div>
		</div>
	</div>
</template>

<script>
		import sender from '../sender'

    export default {
				props: ['me', 'room_list'],
				data: function() {
					return {
						edit_name: false
					}
				},
				methods: {
					change_name: function () {
							this.edit_name = !this.edit_name;
							this.$nextTick(() => {
									if(this.edit_name) this.$refs.editor.focus();
							});
							if(!this.edit_name) sender.change_name(this.me.name)
					},
					join_room: sender.join_room,
					create_room: sender.create_room
				},
				components: {
					'mafia-room': {
							props: ['room'],
							template:`
									<div class="container-login100-form-btn m-t-30">
											<div class="login100-form-btn">
													{{ room.name }}<span class="cnt">{{ room.num }}</span>
											</div>
									</div>
							`
					}					
				}
    }
</script>