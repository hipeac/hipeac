<style lang="scss">
.hipeac__article_list {
  .q-focus-helper {
    display: none;
  }
}
</style>

<template>
  <div>
    <h6 class="q-mb-md">Latest news</h6>
    <q-separator />
    <q-list separator class="hipeac__article_list">
      <q-item v-for="item in visibleItems" :key="item.id" :href="item.url" class="q-px-none q-py-md">
        <q-item-section>
          <small class="q-mb-xs"
            ><strong>{{ item.type_display }}</strong
            >, {{ item.date }}</small
          >
          <span>{{ item.title }}</span>
        </q-item-section>
        <q-item-section side>
          <q-icon name="arrow_forward_ios" size="xs" />
        </q-item-section>
      </q-item>
    </q-list>
    <div class="text-center q-gutter-x-sm">
      <q-btn unelevated no-caps color="grey-3" text-color="dark" href="/news/" class="q-mt-md">
        All news <q-icon name="arrow_forward_ios" size="13px" class="q-ml-sm" />
      </q-btn>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, PropType } from 'vue';

import { format } from '@/utils/date';

const props = defineProps({
  items: Array as PropType<HipeacArticle[]>,
});

const visibleItems = computed(() => {
  return props.items?.map((item) => ({
    ...item,
    date: format(item.publication_date, 'MMM d, yyyy'),
  }));
});
</script>
