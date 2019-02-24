<template>
    <div class="modal-job">
        <table style="width:100%; text-align:center;" cellspacing="0">
            <tr v-for="job in jobs">
                <td>{{ job }}</td>
                <td style="text-align: left;">
                    mission: {{ job.mission }} <p/>
                    action: {{ job.action }}
                </td>
                <td v-if="!read_only"><i @click="handler(job)" class="fas fa-plus-circle" style="color:#2f5773"></i></td>
            </tr>
        </table>
    </div>
</template>

<script>
    export default {
        props: ['jobs', 'handler', 'read_only'],
    }
</script>