import Vue from 'vue';
import _ from 'lodash';
import VueJsModal from 'vue-js-modal';
import JobModal from './vue/JobModal.vue'
import MemberTag from './vue/MemberTag.vue'

Vue.use(VueJsModal, {
  dialog: true,
  dynamic: true,
});

Vue.component('mafia-room', {
    props: ['room'],
    template:`
        <div class="container-login100-form-btn m-t-30">
            <div class="login100-form-btn">
                {{ room.name }}<span class="cnt">{{ room.num }}</span>
            </div>
        </div>
    `
});

Vue.component('mafia-user-tag', MemberTag);

Vue.component('mafia-self-tag', {
    props: ['member'],
    template: '<span class="tag name">{{ member.name }} <i v-bind:class="fas fa-pencil-alt"></i></span>'
});

Vue.component('job-tag', {
    props: ['job'],
    template: '<span class="tag job">{{ job }}</span>'
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
    methods: {
        toggle_name_input: () => {
            app.edit_name = !app.edit_name;
            app.$nextTick(() => {
                if(app.edit_name) app.$refs.editor.focus();
            });
        },
        change_name: () => {
            change_name_debounce();
        },
        create_room: () => {
            app.socket.send_json({
                type: TYPE.CREATE_ROOM
            })
        },
        join_room: (room) => {
            app.socket.send_json({
                type: TYPE.JOIN_ROOM,
                room: room.name,
            })
        },
        leave_room: () => {
            app.socket.send_json({
                type: TYPE.LEAVE_ROOM,
                room: app.room,
            })
        },
        ready: function() {
            if(this.me.choice.status === 'yet')
                this.choose('ready', 'fixed');
            else
                this.choose(null, 'yet');
        },
        day_choose: function(target) {
            if(this.me.choice.status === 'yet')
                this.choose(target, 'fixed');
            else
                this.choose(null, 'yet');
        },
        elect: function(target) {
            if(target === 'fix')
                if (this.me.choice.target === null) alert('choose target user first');
                else if(this.me.choice.status === 'fixed') this.choose(null, 'yet');
                else this.choose(this.me.choice.target, 'fixed');
            else if(target === 'abstain')
                if(this.me.choice.status === 'fixed' && this.me.choice.target === null) this.choose(null, 'yet');
                else this.choose(null, 'fixed');
            else if(target === app.me.id || target === app.me.choice.target)
                this.choose(null, 'yet');
            else
                this.choose(target, 'tmp');
        },
        choose_target: function(target) {
            if(target === 'fix')
                if (this.me.choice.target === null) alert('choose target user first');
                else if(this.me.choice.status === 'fixed') this.choose(null, 'yet');
                else this.choose(this.me.choice.target, 'fixed');
            else if(target === 'abstain')
                if(this.me.choice.status === 'fixed' && this.me.choice.target === null) this.choose(null, 'yet');
                else this.choose(null, 'fixed');
            else if(target === app.me.choice.target)
                this.choose(null, 'yet');
            else
                this.choose(target, 'tmp');
        },
        choose: function(target, status) {
            this.socket.send_json({
                type: TYPE.CHOOSE,
                target: target,
                status: status,
            });
        },
        toggle_status: function(status) {
            if(this.status === 'dead')
                return;
            if(status === this.status)
                this.status = '';
            else
                this.status = status;
            this.socket.send_json({
                type: TYPE.TOGGLE_STATUS,
                status: status,
            })
        },
        add_job: function(job) {
            console.log(job);
            this.socket.send_json({
                type: TYPE.ADD_JOB,
                job: job,
            })
        },
        remove_job: function(job) {
            this.socket.send_json({
                type: TYPE.REMOVE_JOB,
                job: job,
            })
        },
        get_jobs: function() {
            this.socket.send_json({
                type: TYPE.GET_JOBS
            });
        },
        modal: function(jobs) {
            this.$modal.show(JobModal,{
                jobs: jobs,
                handler: (job) => {
                    this.add_job(job);
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
                app.member_list = Object.values(app.member_set);
            }
            this.room_status = 0;
            this.targets = [];
            this.clear_block();
        },
        clear_room_status: function() {
            this.clear_status();
            this.job = null;
            this.jobs = [];
            this.member_list = [];
            this.member_set = {};
            this.room = 'main'
        }
    }
});

export default app;