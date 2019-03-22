import Vue from 'vue';
import _ from 'lodash';
import VueJsModal from 'vue-js-modal';
import JobModal from './vue/JobModal.vue'
import MemberTag from './vue/MemberTag.vue'
import MainVue from './vue/Main.vue'
import RoomVue from './vue/Room.vue'
import sender from './sender'

Vue.use(VueJsModal, {
  dialog: true,
  dynamic: true,
});

const status = {
    room_list: [],
    room_status: 0,
    room: 'main',
    status: '',
    socket: null,
    me: {
        name:'NAME',
    },
    job: 'JOB',
    member_list: [],
    member_set: {},
    team_mates: {},
    edit_name: false,
    jobs: {},
    block: {
        activated: false,
        msg: null,
    },
    targets: []
};

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

const change_name_debounce = _.debounce(
    () => {
        app.socket.send_json({
            type: TYPE.CHANGE_NAME,
            name: app.me.name,
        });
    }
    , 500
);

const app = new Vue({
    el: '#mafia-vue',
    data: status,
    components: {
        'main-view': MainVue,
        'room-view': RoomVue,
        'mafia-user-tag': MemberTag
    },
    methods: {
        change_name: () => {
            change_name_debounce();
        },
        create_room: () => {
            app.socket.send_json({
                type: TYPE.CREATE_ROOM
            })
        },
        join_room: (room) => {
            sender.join_room(room)
        },
        modal: function(jobs) {
            this.$modal.show(JobModal,{
                jobs: jobs,
                handler: (job) => {
                    sender.add_job(job);
                    this.$modal.hide('job-vue');
                },
                read_only: this.room_status !== 0,
            }, {
                name: 'job-vue',
                adaptive: true,
                width: '480px',
            });
        },
        block_screen: function(msg) {
            this.block.activated = true;
            this.block.msg = msg;
        },
        clear_block: function() {
            this.block.activated = false;
            this.block.msg = null;
        },
        clear_status: function() {
            for (const id in this.member_set) {
                const member = this.member_set[id];
                if (member.status !== 'dead')
                    member.status = '';
                member.choice = {
                    target: null,
                    status: 'yet'
                };
            }
            this.room_status = 0;
            this.targets = [];
            this.clear_block();
        },
        clear_game: function() {
            for (const id in this.member_set) {
                const member = this.member_set[id];
                member.status = '';
                member.choice = {
                    target: null,
                    status: 'yet'
                };
                if(!member.connected)
                    delete this.member_set[id];
            }
            app.member_list = Object.values(app.member_set);
            this.room_status = 0;
            this.targets = [];
            this.clear_block();
        },
        clear_room_status: function() {
            this.clear_status();
            this.me.job = null;
            this.jobs = [];
            this.member_list = [];
            this.member_set = {};
            this.room = 'main'
        }
    }
});

export default app;