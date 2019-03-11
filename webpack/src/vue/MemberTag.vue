<template>
    <div :style="{display: target ? '' : 'inline-block'}">
        <span class="tag name" v-bind:class="[ tag_color ]">
            {{ member.name }}
        </span>
        <template v-if="target">
            <i class="fas fa-long-arrow-alt-right" style="vertical-align: text-top" v-bind:style="{ color: member.choice.status === 'fixed' ? '' : '#aeaeae' }"></i>
            <span class="tag name">
                {{ target_user }}
            </span>
        </template>
    </div>
</template>
<script>
    export default {
        props: ['member', 'self', 'target', 'member_list'],
        name: "MemberTag",
        computed: {
            target_user : function() {
                if(this.member.choice.target)
                    return this.member_list.find(member => member.id === this.member.choice.target).name;
                else
                    return 'NONE';
            },
            tag_color: function() {
                if(this.member.status === 'dead')
                    return 'dead';
                if(!this.member.connected)
                    return 'disconnected';
                if(this.member.choice) {
                    if (this.member.choice.status === 'fixed')
                        if (this.member.choice.target == null || this.member.choice.target.startsWith('specific'))
                            return 'ready';
                    return this.member.choice.target;
                }
                return null;
            }
        }
    }
</script>