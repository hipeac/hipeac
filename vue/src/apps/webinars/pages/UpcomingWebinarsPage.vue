<template>
  <div class="row q-col-gutter-lg">
    <div class="col-12 col-md-6" :class="{ 'q-py-lg': $q.screen.gt.sm }">
      <big-display
        title="Directly to your desk"
        subtitle="The HiPEAC webinar series allows you to keep up to date on the latest advances in computer architecture and compilation research via online sessions which can be accessed from any location."
        class="q-mt-xl"
      />
    </div>
    <div class="col-12 col-md" :class="{ 'q-py-xl': $q.screen.gt.sm }">
      <webinar-list :webinars="upcomingWebinars" title="Upcoming webinars" class="q-mb-lg" />
    </div>
  </div>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';

import { useStore } from '../store';

import BigDisplay from '@/components/BigDisplay.vue';
import WebinarList from '../components/WebinarList.vue';

const store = useStore();

const { upcomingWebinars } = storeToRefs(store);
</script>
