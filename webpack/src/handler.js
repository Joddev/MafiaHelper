import app from './view'
import VisGraph from './graph'
import _ from 'lodash'

const handler = {};

export const TYPE = {
    MAIN_INITIATED: 'main_initiated',
    MAIN_JOINED: 'main_joined',
    MAIN_LEFT: 'main_left',
    ROOM_JOINED: 'room_joined',
    ROOM_LEFT: 'room_left',
    MEMBER_STATUS_CHANGED: 'member_status_changed',
    ROOM_STARTED: 'room_started',
    ROOM_NOT_STARTED: 'room_not_started',
    ROOM_JOB_INITIATED: 'room_job_initiated',
    ROOM_STATUS_CHANGED: 'room_status_changed',
    JOB_CHANGED: 'job_changed',
    JOB_LIST: 'job_list',
    VOTE_CHANGED: 'vote_changed',
    TARGET_CHANGED: 'target_changed',
    JOB_TARGET_DONE: 'job_target_done',
    CHOOSE_CHANGED: 'choose_changed',
    CANNOT_CHOOSE: 'cannot_choose',
    MAIN_CHANGED: 'main_changed',
    ROOM_INITIATED: 'room_initiated',
    ROOM_MEMBER_CHANGED: 'room_member_changed',
    GAME_DONE: 'game_done',
    CONFIRM_REJOIN: 'confirm_rejoin'
};

handler.accept = (json) => {
    console.log(json);
    const type = json['type'];
    switch(type) {
        case TYPE.MAIN_INITIATED:
            main_initiated(json);
            return;
        case TYPE.MAIN_CHANGED:
            main_changed(json);
            return;
        case TYPE.MAIN_JOINED:
            main_joined(json);
            return;
        case TYPE.ROOM_INITIATED:
            room_initiated(json);
            return;
        case TYPE.ROOM_JOINED:
            room_joined(json);
            return;
        case TYPE.MAIN_LEFT:
            main_left(json);
            return;
        case TYPE.ROOM_LEFT:
            room_left(json);
            return;
        case TYPE.ROOM_MEMBER_CHANGED:
            room_member_changed(json);
            return;
        case TYPE.MEMBER_STATUS_CHANGED:
            member_status_changed(json);
            return;
        case TYPE.JOB_CHANGED:
            job_changed(json);
            return;
        case TYPE.JOB_LIST:
            job_list(json);
            return;
        case TYPE.ROOM_NOT_STARTED:
            room_not_started(json);
            return;
        case TYPE.ROOM_STARTED:
            room_started(json);
            return;
        case TYPE.ROOM_JOB_INITIATED:
            room_job_initiated(json);
            return;
        case TYPE.ROOM_STATUS_CHANGED:
            room_status_changed(json);
            return;
        case TYPE.VOTE_CHANGED:
            vote_changed(json);
            return;
        case TYPE.TARGET_CHANGED:
            target_changed(json);
            return;
        case TYPE.JOB_TARGET_DONE:
            job_target_done(json);
            return;
        case TYPE.CHOOSE_CHANGED:
            choose_changed(json);
            return;
        case TYPE.CANNOT_CHOOSE:
            cannot_choose(json);
            return;
        case TYPE.GAME_DONE:
            game_done(json);
            return;
        case TYPE.CONFIRM_REJOIN:
            confirm_rejoin(json);
            return;
        default:
            console.log(json);
            return;
    }
};

const main_initiated = (json) => {
    app.clear_room_status();
    app.me = json.me;
    app.room = json.room;
};

const main_changed = (json) => {
    app.room_list = json.room_list;
};

const main_joined = (json) => {
    const room = json['room'];
    let found = false;
    // when exists
    app.room_list.forEach((it) => {
        if(it.name === room) {
            it.num++;
            found = true;
        }
    });
    // when does not exists
    if(!found) {
        app.room_list.push({
            name: room,
            num: 1,
        });
    }
};

const set_user = (user, refresh) => {
    if(typeof(app.member_set[user.id]) === 'undefined')
        app.member_set[user.id] = user;
    else
        Object.assign(app.member_set[user.id], user);

    if(refresh)
        app.member_list = Object.values(app.member_set);
};

const set_users = (user_list) => {
    const remains = [];
    for (let i = 0; i < user_list.length; i++) {
        const cur = user_list[i];
        remains.push(cur.id);
        set_user(cur);
    }
    for (const id in app.member_set)
        if(!remains.includes(id))
            delete app.member_set[id];
    app.member_list = Object.values(app.member_set);
};

const room_initiated = (json) => {
    app.room = json.room;
    app.jobs = json['jobs'];
    set_users(json.users);
    app.me = app.member_set[app.me.id];
    app.me.job = json.job;
    app.room_status = json.room_status
    // set team_mates
    const team_mates = [];
    json.team_mates.forEach(function(row) {
        team_mates.push(app.member_set[row.id]);
    });
    app.team_mates = team_mates;
    // set targets
    app.targets = json.targets
    // draw vote map
    if (app.room_status === 2) {
        app.$nextTick(function () {
            const voters = app.member_list.filter(member => member.status !== 'dead');
            app.voteMap = VisGraph.makeGraph(document.getElementById('canvas-container'), app.me, voters);            
        });
    }
};

const room_member_changed = (json) => {
    set_users(json.users);
};

const room_joined = (json) => {
    app.room = json.room;
    app.jobs = json['jobs'];
    set_users(json.users);
    app.me = app.member_set[app.me.id];
};

const main_left = (json) => {
    const room = json.room;
    for (let i = 0; i < app.room_list.length; i++) {
        if(app.room_list[i].name === room)
            if(--app.room_list[i].num <= 0)
                app.room_list.splice(i,1);
    }
};

const room_left = (json) => {
    set_users(json.users);
};

const choose_changed = (json) => {
    app.member_set[json.user].choice = json.choice;
    if(app.room_status === 2) {
        app.voteMap.vote(json.user, json.choice.target, json.choice.status)
    }
};

const cannot_choose = (json) => {
    if(json.target in app.member_set)
        alert(`Cannot choose ${app.member_set[json.target].name}`);
    else
        alert('Cannot choose');
};

const job_changed = (json) => {
    app.jobs = json['jobs'];
    app.ready_msg = '';
};

const job_list = (json) => {
    app.modal(json['data'])
};

let clearReadyMsg =  _.debounce(() => {
    app.ready_msg = '';
}, 2000);

const room_not_started = (json) => {
    app.ready_msg = 'the number of jobs and members does not matched';
    clearReadyMsg();
};

const room_started = (json) => {
    app.room_status = 1;
    app.clear_status();
};

const room_status_changed = (json) => {
    const prev_status = app.room_status;
    app.clear_status();
    app.room_status = json.status;
    switch (prev_status) {
        case 0:
            app.me.job = json.result.job;
            const team_mates = [];
            json.result.team_mates.forEach(function(row) {
                team_mates.push(app.member_set[row.id]);
            });
            app.team_mates = team_mates;
            break;
        case 1:
            if (app.room_status === 2)
                app.$nextTick(function () {
                    const voters = app.member_list.filter(member => member.status !== 'dead');
                    app.voteMap = VisGraph.makeGraph(document.getElementById('canvas-container'), app.me, voters);
                });
            break;
        case 2:
            if (json.result && json.result.victim) {
                set_user(json.result.victim, true);
                if (json.result.victim.status === 'dead')
                    alert(`${json.result.victim.name} was executed.`);
                else
                    alert(`${json.result.victim.name} was not executed.`);
            }
            break;
        case 3:
            for (let i = 0; i < json.result.act_list.length; i++) {
                const row = json.result.act_list[i];
                switch (row.result_type) {
                    case 'user':
                        set_user(row.result, true);
                        break;
                    case 'bool':
                        if (app.me.job === 'police') {
                            const suspect = app.member_set[row.result.target];
                            if(row.result.confirmation) alert(`${suspect.name} belongs to mafia`);
                            else alert(`${suspect.name} does not belong to mafia`);
                        }
                }
            }
    }
    if(json.status === 3) {
        app.targets = json.result.targets;
    }
};

const game_done = (json) => {
    app.clear_game();
    switch(json.result) {
        case 'citizen_group':
            alert('Citizen wins');
            break;
        case 'mafia_group':
            alert('Mafia wins');
            break;
        default:
            alert(`${json.result} wins`);
            break;
    }
};

const job_target_done = (json) => {
    const target = json['target'] ? app.members.find(function (member) {
        return member.id === json['target'];
    }).name : null;
    app.block_screen(`Waiting for others (target: ${target})`);
};

const confirm_rejoin = (json) => {
    if(confirm('Progressing room exists. Do you want join again?')) {
        console.log(json)
        app.join_room(json.room)        
    }
}

export { app };
export default handler;