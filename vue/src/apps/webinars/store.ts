import { computed, ref } from 'vue';
import { defineStore, storeToRefs } from 'pinia';
import { cloneDeep } from 'lodash-es';

import { api } from '@/axios.ts';
import { useCommonStore } from '@/stores/common';
import { mapSession } from '@/utils/mapper';

export const useStore = defineStore('webinars', () => {
  const commonStore = useCommonStore();
  const { now } = storeToRefs(commonStore);

  const allWebinars = ref<HipeacWebinar[]>([]);
  const allRegistrations = ref<HipeacWebinarRegistration[]>([]);

  async function init(djangoUser: DjangoAuthenticatedUser | null) {
    await fetchWebinars();

    if (djangoUser) {
      await fetchRegistrations();
    }
  }

  async function fetchRegistrations() {
    await api.get('/user/webinars/').then((response) => {
      allRegistrations.value = response.data;
    });
  }

  async function fetchWebinars() {
    await api.get('/webinars').then((response) => {
      allWebinars.value = response.data.map((webinar: HipeacWebinar) => mapSession(webinar) as HipeacWebinar);
    });
  }

  function addRegistration(reg: HipeacWebinarRegistration) {
    allRegistrations.value.push(cloneDeep(reg));
  }

  function removeRegistration(reg: HipeacWebinarRegistration) {
    const index = allRegistrations.value.findIndex((r) => r.id === reg.id);
    if (index !== -1) {
      allRegistrations.value.splice(index, 1);
    }
  }

  const registrations = computed<HipeacWebinarRegistration[]>(() => {
    return allRegistrations.value.map((reg) => ({
      ...reg,
      Webinar: allWebinars.value.find((webinar) => webinar.id === reg.webinar),
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
