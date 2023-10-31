import { computed, onMounted, onUnmounted, ref } from 'vue';
import { defineStore } from 'pinia';

import { api } from '@/axios.ts';
import { storage } from '@/utils/storage';

export const useCommonStore = defineStore('common', () => {
  const metadata = ref<Metadata[]>([]);
  const now = ref<Date>(new Date());
  const user = ref<DjangoAuthenticatedUser | null>(null);

  async function init(djangoUser: DjangoAuthenticatedUser | null) {
    user.value = djangoUser;
    await fetchMetadata();
  }

  async function fetchMetadata() {
    const existingMetadata = storage.get('metadata');

    if (existingMetadata) {
      metadata.value = existingMetadata;
    } else {
      await api.get('/metadata/').then((res) => {
        metadata.value = res.data;
        storage.set('metadata', res.data, storage.ONE_HOUR);
      });
    }
  }

  const metadataByType = computed<Record<string, Metadata[]>>(() =>
    metadata.value.reduce((acc, meta) => ({ ...acc, [meta.type]: [...(acc[meta.type] || []), meta] }), {})
  );

  onMounted(() => {
    const interval = setInterval(() => {
      now.value = new Date();
    }, 1000);
    onUnmounted(() => clearInterval(interval));
  });

  return {
    init,
    metadataByType,
    now,
    user,
  };
});
