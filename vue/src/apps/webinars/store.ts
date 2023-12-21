import { computed, ref } from 'vue';
import { defineStore, storeToRefs } from 'pinia';
import { cloneDeep } from 'lodash-es';

import { api } from '@/axios.ts';
import { useCommonStore } from '@/stores/common';
import { useUserStore } from '@/stores/user';
import { mapSession } from '@/utils/mapper';

export const useStore = defineStore('webinars', () => {
  const { now } = storeToRefs(useCommonStore());
  const { user } = storeToRefs(useUserStore());

  const allWebinars = ref<HipeacWebinar[]>([]);
  const allRegistrations = ref<HipeacWebinarRegistration[]>([]);

  async function init() {
    await fetchWebinars();

    if (user.value) {
      await fetchRegistrations();
    }
  }

  async function fetchRegistrations() {
    await api.get('/user/webinars/').then((res) => {
      allRegistrations.value = res.data;
    });
  }

  async function fetchWebinars() {
    await api.get('/webinars/').then((res) => {
      allWebinars.value = res.data.map((webinar: HipeacWebinar) => mapSession(webinar) as HipeacWebinar);
    });
  }

  function addRegistration(registration: HipeacWebinarRegistration) {
    allRegistrations.value.push(cloneDeep(registration));
  }

  function removeRegistration(registration: HipeacWebinarRegistration) {
    const index = allRegistrations.value.findIndex((r) => r.id === registration.id);
    if (index !== -1) {
      allRegistrations.value.splice(index, 1);
    }
  }

  const registrations = computed<HipeacWebinarRegistration[]>(() => {
    return allRegistrations.value.map((registration) => ({
      ...registration,
      Webinar: allWebinars.value.find((webinar) => webinar.id === registration.webinar),
    }));
  });

  const pastWebinars = computed<HipeacWebinar[]>(() => {
    return webinars.value.filter((webinar) => webinar.end && webinar.end < now.value).reverse();
  });

  const upcomingWebinars = computed<HipeacWebinar[]>(() => {
    return webinars.value.filter((webinar) => webinar.end && webinar.end > now.value);
  });

  const webinars = computed<HipeacWebinar[]>(() => {
    return allWebinars.value.map((webinar) => ({
      ...webinar,
      _registered: registrations.value.some((reg) => reg.webinar === webinar.id),
    }));
  });

  return {
    init,
    addRegistration,
    removeRegistration,
    registrations,
    webinars,
    pastWebinars,
    upcomingWebinars,
  };
});
