<template>
  <hipeac-toolbar-menu :title="title" :menu="menu" />
</template>

<script setup lang="ts">
import HipeacToolbarMenu from '@/components/HipeacToolbarMenu.vue';

import { iconAdd, iconRssFeed, iconLinkedIn, iconX } from '@/icons/index.ts';

const title = 'HiPEAC Jobs';
const menu = [
  {
    label: 'Open positions',
    to: { name: 'openPositions' },
  },
  {
    label: 'About',
    to: { name: 'about' },
  },
  {
    label: 'Add new',
    href: '/editor/new/job/',
    btnColor: 'green',
    icon: iconAdd,
  },
  {
    label: null,
    href: 'https://twitter.com/hipeacjobs',
    icon: iconX,
  },
  {
    label: null,
    href: '/linkedin/',
    icon: iconLinkedIn,
  },
  {
    label: null,
    href: '/jobs/feed/',
    icon: iconRssFeed,
  },
];
</script>
