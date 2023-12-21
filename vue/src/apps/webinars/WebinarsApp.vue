<template>
  <div>
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { useStore } from './store';

const store = useStore();

store.init();
</script>
