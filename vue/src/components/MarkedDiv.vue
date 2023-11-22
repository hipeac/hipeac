<template>
  <div v-html="html" />
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { render } from '@/utils/markdown';

const props = defineProps<{
  text: string;
}>();

const html = computed<string>(() => render(props.text));
</script>
