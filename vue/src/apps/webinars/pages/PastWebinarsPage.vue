<template>
  <webinar-list :webinars="pastWebinars" title="Previous webinars" />
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';

import { useStore } from '../store';

import WebinarList from '../components/WebinarList.vue';

const store = useStore();

const { pastWebinars } = storeToRefs(store);
</script>
