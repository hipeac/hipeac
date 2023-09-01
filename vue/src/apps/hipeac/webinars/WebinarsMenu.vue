<template>
  <hipeac-toolbar-menu :title="title" :menu="menu" />
</template>

<script setup lang="ts">
import HipeacToolbarMenu from '@/components/HipeacToolbarMenu.vue';

const title = 'HiPEAC Webinars';
const menu = [
  {
    label: 'Upcoming',
    to: { name: 'upcomingWebinars' },
  },
  {
    label: 'Previous',
    to: { name: 'pastWebinars' },
  },
  {
    label: 'Logistics',
    to: { name: 'logistics' },
  },
];
</script>
