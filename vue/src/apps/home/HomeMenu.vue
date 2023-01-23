<template>
  <hipeac-toolbar-menu :title="title" :menu="menu" />
</template>

<script setup lang="ts">
import HipeacToolbarMenu from '@/components/HipeacToolbarMenu.vue';

import { iconLinkedIn, iconTwitter, iconYouTube } from '@/icons/index.ts';

const title = 'Welcome to HiPEAC';
const menu = [
  {
    label: 'Join an event',
    href: '/events/',
  },
  {
    label: 'Become a member',
    href: '/membership/',
  },
  {
    label: 'Find your next job',
    href: '/jobs/',
  },
  {
    label: null,
    href: '/twitter/',
    icon: iconTwitter,
  },
  {
    label: null,
    href: '/linkedin/',
    icon: iconLinkedIn,
  },
  {
    label: null,
    href: '/youtube/',
    icon: iconYouTube,
  },
];
</script>
