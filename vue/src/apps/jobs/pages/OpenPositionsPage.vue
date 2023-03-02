<template>
  <div v-if="jobs">
    <div class="row q-col-x-gutter-lg">
      <div class="col-12 col-md-6" :class="{ 'q-py-lg': $q.screen.gt.sm }">
        <big-display v-if="jobs.length" title="Find your ideal computing job in Europe" :subtitle="subtitle" />
      </div>
      <div class="col-12 col-md">
        <institution-carousel :institutions="employers" :callback="searchEmployer" random />
        <q-input
          v-model="filter.query"
          filled
          clearable
          label="Search"
          hint="Search open positions by title, company, country, topic or keywords."
        >
          <template v-slot:prepend>
            <q-icon name="search" />
          </template>
        </q-input>
      </div>
    </div>
    <div class="row q-col-gutter-lg q-mt-none">
      <div class="col-12 d-flex align-items-stretch">
        <q-card flat bordered class="q-px-lg q-pb-lg full-height">
          <q-tabs
            v-model="tab"
            no-caps
            align="justify"
            switch-indicator
            indicator-color="primary"
            class="square q-mb-sm"
          >
            <q-tab name="jobs"
              ><h5>Positions ({{ filteredJobs.length }})</h5></q-tab
            >
            <q-tab name="employers"
              ><h5>Employers ({{ filteredEmployers.length }})</h5></q-tab
            >
          </q-tabs>
          <div class="row q-col-gutter-x-xl">
            <div v-if="$q.screen.gt.sm" class="col-12 col-md-3">
              <jobs-filters :filter="filter" :topics="topics" :career-levels="careerLevels" :countries="countries" />
            </div>
            <div class="col-12 col-md">
              <q-tab-panels v-model="tab">
                <q-tab-panel name="jobs" class="q-pa-none">
                  <q-list separator class="hipeac__custom-list">
                    <q-item v-for="job in filteredJobs" :key="job.id" class="q-px-none q-py-md" :href="job.url">
                      <q-item-section v-if="$q.screen.gt.sm" avatar>
                        <q-avatar rounded class="bg-grey-4">
                          <img :src="job.institution.images?.th" />
                        </q-avatar>
                      </q-item-section>
                      <q-item-section>
                        <span class="text-caption text-weight-bold">{{ job.institution.name }}</span>
                        <h6 class="item-title q-my-sm">{{ job.title }}</h6>
                        <div class="text-caption text-grey-8">
                          <q-icon name="place" /> {{ job.location }}, {{ job.country.name }}
                        </div>
                        <div v-if="job.tags && job.tags.length" class="text-caption text-grey-8">
                          <div class=""><q-icon name="label" /> {{ job.tags.join(', ') }}</div>
                        </div>
                      </q-item-section>
                      <q-item-section side class="text-caption">
                        <q-icon name="arrow_forward_ios" size="xs" />
                      </q-item-section>
                    </q-item>
                  </q-list>
                </q-tab-panel>
                <q-tab-panel name="employers" class="q-pa-none">
                  <q-list separator class="hipeac__custom-list">
                    <q-item
                      v-for="employer in filteredEmployers"
                      :key="employer.id"
                      class="q-px-none q-py-md"
                      :href="employer.url"
                    >
                      <q-item-section avatar>
                        <q-avatar rounded class="bg-grey-4">
                          <img :src="employer.images?.th" />
                        </q-avatar>
                      </q-item-section>
                      <q-item-section>
                        <h6 class="item-title q-mt-none q-mb-xs">{{ employer.name }}</h6>
                        <div class="text-caption text-grey-8">
                          <span v-if="employer.jobs.length == 1">One position</span>
                          <span v-else>{{ employer.jobs.length }} positions</span>
                        </div>
                      </q-item-section>
                      <q-item-section side class="text-caption">
                        <q-icon name="arrow_forward_ios" size="xs" />
                      </q-item-section>
                    </q-item>
                  </q-list>
                </q-tab-panel>
              </q-tab-panels>
            </div>
          </div>
        </q-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { storeToRefs } from 'pinia';

import BigDisplay from '@/components/BigDisplay.vue';
import InstitutionCarousel from '@/components/InstitutionCarousel.vue';
import JobsFilters from '../components/JobsFilters.vue';

import { useStore } from '../store';

const route = useRoute();
const router = useRouter();
const store = useStore();

const { jobs, employers, countries, topics, careerLevels } = storeToRefs(store);

const tab = ref<string>('jobs');
const subtitle = computed<string>(() => `There are currently ${jobs.value?.length} open positions!`);

const filter = ref<JobsFilter>({
  query: '',
  typeId: null,
  topicIds: [],
  careerLevelIds: [],
  countryCodes: [],
  sort: 'newest',
});

const filteredJobs = computed<HipeacJob[]>(() => {
  return (jobs.value || [])
    .filter((job) => {
      return !filter.value.query || job.q?.toLowerCase().includes(filter.value.query.toLowerCase());
    })
    .filter((job) => {
      return filter.value.typeId === null || job.employment_type === filter.value.typeId;
    })
    .filter((job) => {
      return filter.value.topicIds.length === 0 || filter.value.topicIds.some((id: number) => job.topicIds?.has(id));
    })
    .filter((job) => {
      return (
        filter.value.careerLevelIds.length === 0 ||
        filter.value.careerLevelIds.some((id: number) => job.careerLevelIds?.has(id))
      );
    })
    .filter((job) => {
      return filter.value.countryCodes.length === 0 || filter.value.countryCodes.includes(job.country.code);
    });
});

const filteredEmployers = computed<InstitutionWithJobs[]>(() => {
  const employerIds = new Set<number>();
  const uniqueEmployers: InstitutionWithJobs[] = [];

  filteredJobs.value.forEach((job) => {
    if (!employerIds.has(job.institution.id)) {
      uniqueEmployers.push({
        ...job.institution,
        jobs: [job],
      });
      employerIds.add(job.institution.id);
    } else {
      const employer = uniqueEmployers.find((employer) => employer.id === job.institution.id);
      employer?.jobs.push(job);
    }
  });

  return uniqueEmployers.sort((a, b) => a.name.localeCompare(b.name));
});

function searchEmployer(institution: Institution) {
  return (filter.value.query = institution.name);
}

interface InstitutionWithJobs extends Institution {
  jobs: HipeacJob[];
}

// track query changes

watch(
  () => filter.value.query,
  (newVal) => {
    if (newVal) {
      router.push({ query: {
        ...route.query,
        q: newVal,
      } });
    } else {
      router.push({ query: {} });
    }
  }
);

onMounted(() => {
  if (route.query.q) {
    filter.value.query = route.query.q as string;
  }
});
</script>
