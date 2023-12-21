<template>
  <hipeac-toolbar-menu :title="title" :menu="menu" :dark="$page.props.vue_template == 'dark'" />
</template>

<script setup lang="ts">
import HipeacToolbarMenu from '@/components/HipeacToolbarMenu.vue';

const title = 'Steering Committee';
const menu = [
  {
    label: null,
    to: { name: 'dashboard' },
    icon: 'query_stats',
  },
  {
    label: 'Meetings',
    to: { name: 'meetings' },
  },
  {
    label: 'Action points',
    to: { name: 'actionPoints' },
  },
  {
    label: 'Membership requests',
    to: { name: 'membershipRequests' },
  },
];
</script>
