import { ref } from 'vue';
import { defineStore } from 'pinia';
import { pick } from 'lodash-es';

import { api } from '@/axios.ts';

function mapNotification(obj: UserNotification) {
  return {
    ...obj,
    icon: 'star',
    color: 'grey',
  };
}

export const useUserStore = defineStore('user', () => {
  const user = ref<DjangoAuthenticatedUser | null>(null);
  const notifications = ref<UserNotification[]>([]);

  async function init(djangoUser: DjangoAuthenticatedUser) {
    user.value = djangoUser;
    fetchNotifications();
  }

  async function fetchNotifications() {
    // setTimeout(fetchNotifications, 60 * 1000);

    await api.get('/user/notifications/').then((res) => {
      notifications.value = res.data.map(mapNotification);
    });
  }

  async function updateUser(fields: string[]) {
    await api.patch('/user/account/', pick(user.value, fields)).then((res) => {
      user.value = res.data;
      // notify.success('updated');
    });
  }

  return {
    init,
    updateUser,
    user,
  };
});
