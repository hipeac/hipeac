import { onMounted, onUnmounted, ref } from 'vue';
import { defineStore } from 'pinia';

export const useCommonStore = defineStore('common', () => {
  const now = ref<Date>(new Date());

  onMounted(() => {
    const interval = setInterval(() => {
      now.value = new Date();
    }, 1000);
    onUnmounted(() => clearInterval(interval));
  });

  return {
    now,
  };
});
