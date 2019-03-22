<template>
    <div class="modal-job">
        <div class="job-area">
            <job-tag v-for="job in jobs" :key=job :job=job :handler="handler" :detail="true"></job-tag>
        </div>
    </div>
</template>

<script>
    import JobTag from './JobTag'
    export default {
        props: ['jobs', 'handler', 'read_only'],
        components: {
            'job-tag': JobTag
        },
        mounted: function() {
            this.$el.parentElement.style.overflow = 'unset';
        }
    }
</script>

<style scoped>
    .job-area {
        padding: 20px 15px;        
    }
</style>