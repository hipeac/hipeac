<template>
  <q-card flat bordered class="q-px-lg q-pt-sm q-pb-lg full-height">
    <h6 class="q-mb-md">{{ title }}</h6>
    <session-list :sessions="(webinars as HipeacSession[])" :dialog-component="WebinarDialog" show-local-times />
  </q-card>
</template>

<script setup lang="ts">
import SessionList from '@/components/events/SessionList.vue';
import WebinarDialog from './WebinarDialog.vue';

defineProps<{
  webinars: HipeacWebinar[];
  title?: string;
}>();
</script>
