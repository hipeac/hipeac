<template>
  <q-input
    v-if="sessions.length > 10"
    v-model="query"
    clearable
    dense
    square
    filled
    type="text"
    class="col-12 col-md q-mb-md"
  >
    <template #prepend>
      <q-icon name="search" />
    </template>
  </q-input>
  <div class="text-caption q-pb-md text-primary" v-if="showLocalTimes">
    All times are displayed in your local time zone: <strong>{{ tz }}</strong>
  </div>
  <session-simple-list :sessions="(queriedRows as HipeacSession[])" />
  <q-dialog v-if="dialogComponent" v-model="dialogVisible">
    <component :is="dialogComponent" :obj="selectedObj" />
  </q-dialog>
</template>

<script setup lang="ts">
import { computed, ref, ComponentOptions } from 'vue';
import { useRouter } from 'vue-router';

import SessionDialog from './SessionDialog.vue';
import SessionSimpleList from './SessionSimpleList.vue';

const router = useRouter();

const props = defineProps<{
  sessions: HipeacSession[];
  dialogComponent?: ComponentOptions;
  groupByDate?: boolean;
  showLocalTimes?: boolean;
}>();

const tz = computed(() => Intl.DateTimeFormat().resolvedOptions().timeZone);
const dialogComponent = computed(() => props.dialogComponent || SessionDialog);
const selectedObj = computed<HipeacSession | null>(() => {
  return props.sessions.find((s) => s.id == router.currentRoute.value.params.sessionId) || null;
});
const dialogVisible = computed<boolean>({
  get() {
    return !!selectedObj.value;
  },
  set(value) {
    if (value === false && selectedObj.value) {
      const route = router.currentRoute.value;
      router.push({ name: route.name, params: { ...route.params, sessionId: null } });
    }
  },
});

const rows = computed<HipeacSession[]>(() => {
  return props.sessions;
});

const query = ref<string>('');
const queriedRows = computed<HipeacSession[]>(() => {
  if (!query.value) {
    return rows.value;
  }

  // we split the query search and count the matches
  // if the number of matches is equal to the number of query terms, we have a match

  const queryTerms = query.value.toLowerCase().split(' ');

  return rows.value.filter((row) => {
    let matches = 0;

    for (const queryTerm of queryTerms) {
      if (row._q?.includes(queryTerm)) {
        matches++;
        break;
      }
    }
    return matches === queryTerms.length;
  });
});
</script>
