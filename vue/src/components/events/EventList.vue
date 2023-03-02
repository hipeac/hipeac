<template>
  <div>
    <div v-for="(data, is_finished) in visibleItems" :key="is_finished">
      <h6 v-if="is_finished === 'false'">Upcoming events</h6>
      <h6 v-else>Past events</h6>
      <q-separator />
      <q-list separator class="hipeac__custom-list q-mb-lg">
        <q-item v-for="item in data" :key="item.id" :href="item.url" class="q-px-none q-py-md">
          <q-item-section avatar>
            <q-avatar rounded class="bg-grey-4">
              <img v-if="item.images" :src="item.images.th" />
            </q-avatar>
          </q-item-section>
          <q-item-section>
            <h6 class="item-title q-mb-xs">{{ item.name }}</h6>
            <small>
              <q-icon v-if="item.is_virtual" name="monitor" size="13px" class="q-mb-xs q-mr-xs" />
              <span v-else
                ><strong>{{ item.country.name }}</strong
                >,
              </span>
              {{ item.dates }}
            </small>
          </q-item-section>
          <q-item-section side>
            <q-icon name="arrow_forward_ios" size="xs" />
          </q-item-section>
        </q-item>
      </q-list>
    </div>
    <div class="text-center q-gutter-x-sm">
      <q-btn @click="showMore = !showMore" unelevated no-caps color="grey-3" text-color="dark">
        <q-icon :name="showMore ? 'remove' : 'add'" size="13px" class="q-mr-sm" />
        <span v-if="showMore">Show less</span>
        <span v-else>Show more</span>
      </q-btn>
      <q-btn unelevated no-caps color="grey-3" text-color="dark" href="/events/">
        All events <q-icon name="arrow_forward_ios" size="13px" class="q-ml-sm" />
      </q-btn>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, PropType } from 'vue';
import { groupBy } from 'lodash-es';

import { format } from '@/utils/date';

const props = defineProps({
  items: Array as PropType<HipeacEvent[]>,
  min: {
    type: Number,
    default: 8,
  },
  max: {
    type: Number,
    default: 1000,
  },
});

const showMore = ref(false);

const visibleItems = computed(() => {
  const items = props.items;
  if (!items) return null;

  const size = showMore.value ? props.max : props.min;
  const subset = items.slice(0, size).map((item) => ({
    ...item,
    dates: [format(item.start_date, 'MMM d'), format(item.end_date, 'd, yyyy')].join('-'),
  }));
  const groupedItems = groupBy(subset, 'is_finished');
  if (groupedItems.false) groupedItems.false.reverse();

  return groupedItems;
});
</script>
