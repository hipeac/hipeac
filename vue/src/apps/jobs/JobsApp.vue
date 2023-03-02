<template>
  <div>
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { Loading, useMeta } from 'quasar';

import { useStore } from './store';

const store = useStore();

store.init();

Loading.show({
  delay: 250,
});

useMeta({
  title: 'Jobs',
  titleTemplate: (title) => (title == 'HiPEAC' ? title : `${title} - HiPEAC`),
});
</script>
