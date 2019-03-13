import ws from './socket'

const TYPE = {
	CREATE_ROOM: 'create_room',
	JOIN_ROOM: 'join_room',
	LEAVE_ROOM: 'leave_room',
	CHANGE_NAME: 'change_name',
	TOGGLE_STATUS: 'toggle_status',
	ADD_JOB: 'add_job',
	REMOVE_JOB: 'remove_job',
	GET_JOBS: 'get_jobs',
	VOTE: 'vote',
	TARGET: 'target',
	CHOOSE: 'choose'
};

const sender = {
	create_room: () => {
			ws.current.send_json({
					type: TYPE.CREATE_ROOM
			})
	},
	change_name: (name) => {
			ws.current.send_json({
					type: TYPE.CHANGE_NAME,
					name: name,
			});
	},
	join_room: (room) => {
			ws.current.send_json({
					type: TYPE.JOIN_ROOM,
					room: room,
			})
	},
	choose: function(target, status) {
			ws.current.send_json({
					type: TYPE.CHOOSE,
					target: target,
					status: status,
			});
	},
	add_job: function(job) {
			ws.current.send_json({
					type: TYPE.ADD_JOB,
					job: job,
			})
	},
	remove_job: function(job) {
			ws.current.send_json({
					type: TYPE.REMOVE_JOB,
					job: job,
			})
	},
	get_jobs: function() {
			ws.current.send_json({
					type: TYPE.GET_JOBS
			});
	},
	leave_room: function(room) {
			ws.current.send_json({
					type: TYPE.LEAVE_ROOM,
					room: room,
			})
	}
}

export default sender;