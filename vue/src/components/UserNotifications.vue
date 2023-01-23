<template>
  <q-btn round flat :icon="icon" :disable="counter == 0" size="md">
    <q-badge v-if="counter" rounded color="red-7" floating>{{ counter }}</q-badge>
    <q-menu anchor="bottom right" self="top right" max-width="300px">
      <q-list separator padding class="text-body2" style="min-width: 140px">
        <q-item-label header>Notifications</q-item-label>
        <q-item v-for="n in notifications" clickable tag="a" :href="n.message.path">
          <q-item-section side><q-icon :name="n.icon" size="xs" /></q-item-section>
          <q-item-section>{{ n.message.text }}</q-item-section>
        </q-item>
      </q-list>
    </q-menu>
  </q-btn>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const notifications = [];
const icon = computed(() => (notifications.length > 0 ? 'notifications_active' : 'notifications_none'));
const counter = computed(() => (notifications ? notifications.length : 0));

/*
'hipeac-notifications-btn': {
  setup: function () {
    Vuex.useStore();
  },
  computed: _.extend(
    Vuex.mapState('common', ['notifications']), {
  }),
  created: function () {
    this.$store.commit('common/getNotifications');
  }
},
*/
</script>
