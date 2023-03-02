import { computed, ref } from 'vue';
import { defineStore, storeToRefs } from 'pinia';
import { Loading } from 'quasar';

import { api } from '@/axios.ts';
import { useCommonStore } from '@/stores/common';

function mapJob(job: HipeacJob): HipeacJob {
  const tags = [
    ...job.application_areas.map((area) => area.value),
    ...job.topics.map((topic) => topic.value),
    ...job.keywords,
  ];

  return {
    ...job,
    q: [job.title, job.institution.name, job.location, job.country.name, ...tags].join(' ').toLowerCase(),
    applicationAreaIds: new Set(job.application_areas.map((area) => area.id)),
    topicIds: new Set(job.topics.map((topic) => topic.id)),
    careerLevelIds: new Set(job.career_levels),
    tags: tags,
  };
}

export const useStore = defineStore('jobs', () => {
  const { metadataByType } = storeToRefs(useCommonStore());

  const allJobs = ref<HipeacJob[] | undefined>(undefined);

  async function init() {
    await fetchJobs();
  }

  async function fetchJobs() {
    await api.get('/jobs/').then((res) => {
      allJobs.value = res.data as HipeacJob[];
      Loading.hide();
    });
  }

  const jobs = computed<HipeacJob[] | undefined>(() => {
    return allJobs.value?.map((job) => mapJob(job)) || undefined;
  });

  const employers = computed<Institution[]>(() => {
    const employerIds = new Set<number>();
    const uniqueEmployers: Institution[] = [];

    allJobs.value?.forEach((job) => {
      if (!employerIds.has(job.institution.id)) {
        uniqueEmployers.push(job.institution);
        employerIds.add(job.institution.id);
      }
    });

    return uniqueEmployers.sort((a, b) => a.name.localeCompare(b.name));
  });

  const countries = computed<Country[]>(() => {
    const countryCodes = new Set<string>();
    const uniqueCountries: Country[] = [];

    allJobs.value?.forEach((job) => {
      if (!countryCodes.has(job.country.code)) {
        uniqueCountries.push(job.country);
        countryCodes.add(job.country.code);
      }
    });

    return uniqueCountries.sort((a, b) => a.name.localeCompare(b.name));
  });

  const applicationAreas = computed<ApplicationArea[]>(() => {
    const applicationAreaIds = new Set<number>();
    const uniqueApplicationAreas: ApplicationArea[] = [];

    allJobs.value?.forEach((job) => {
      job.application_areas.forEach((area) => {
        if (!applicationAreaIds.has(area.id)) {
          uniqueApplicationAreas.push(area);
          applicationAreaIds.add(area.id);
        }
      });
    });

    return uniqueApplicationAreas.sort((a, b) => a.value.localeCompare(b.value));
  });

  const topics = computed<Topic[]>(() => {
    const topicIds = new Set<number>();
    const uniqueTopics: Topic[] = [];

    allJobs.value?.forEach((job) => {
      job.topics.forEach((topic) => {
        if (!topicIds.has(topic.id)) {
          uniqueTopics.push(topic);
          topicIds.add(topic.id);
        }
      });
    });

    return uniqueTopics.sort((a, b) => a.value.localeCompare(b.value));
  });

  const careerLevels = computed<CareerLevel[]>(() => {
    const all = (metadataByType.value.job_position.sort((a, b) => a.value.localeCompare(b.value)) ||
      []) as CareerLevel[];

    const careerLevelIds = new Set<number>();
    allJobs.value?.forEach((job) => {
      job.career_levels.forEach((id) => careerLevelIds.add(id));
    });

    return all.filter((level) => careerLevelIds.has(level.id));
  });

  return {
    init,
    jobs,
    countries,
    employers,
    applicationAreas,
    topics,
    careerLevels,
  };
});
