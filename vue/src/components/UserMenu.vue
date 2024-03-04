<template>
  <div v-if="user" class="row reverse q-gutter-md">
    <q-btn no-caps outline color="primary" class="q-pr-sm">
      {{ user.username }} <q-icon name="arrow_drop_down" size="xs" />
      <q-menu anchor="top end" self="bottom right" :offset="[0, 0]" class="text-body2 q-py-sm" style="min-width: 140px">
        <q-list dense>
          <q-item clickable tag="a" :href="`/~${user.username}/`">
            <q-item-section>Public profile</q-item-section>
          </q-item>
          <q-separator class="q-my-xs" />
          <q-item clickable tag="a" href="/accounts/profile/">
            <q-item-section>Settings</q-item-section>
            <q-item-section side><q-icon name="settings" size="xs" /></q-item-section>
          </q-item>
        </q-list>
        <q-list v-if="is_steering" dense>
          <q-separator class="q-my-xs" />
          <q-item-label header class="text-caption text-uppercase q-py-sm">Steering Committe</q-item-label>
          <q-item clickable tag="a" href="/sc/#/">
            <q-item-section>Dashboard</q-item-section>
            <q-item-section side><q-icon name="query_stats" size="xs" /></q-item-section>
          </q-item>
          <q-item clickable tag="a" href="/sc/#/meetings/">
            <q-item-section>Meetings</q-item-section>
          </q-item>
          <q-item clickable tag="a" href="/sc/#/action-points/">
            <q-item-section>Action points</q-item-section>
          </q-item>
          <q-item clickable tag="a" href="/sc/#/membership-requests/">
            <q-item-section>Membership requests</q-item-section>
          </q-item>
          <q-item clickable tag="a" href="https://cloud.hipeac.net/index.php/apps/files/files/57011?dir=/HiPEAC7" target="_blank">
            <q-item-section>File repository</q-item-section>
            <q-item-section side><q-icon name="cloud_queue" size="xs" /></q-item-section>
          </q-item>
        </q-list>
        <q-list dense>
          <q-separator class="q-my-xs" />
          <q-item-label header class="text-caption text-uppercase q-py-sm">Management</q-item-label>
          <q-item clickable tag="a" href="/jobs/management/">
            <q-item-section>My job posts</q-item-section>
          </q-item>
          <q-item v-if="user.is_staff" clickable tag="a" href="/admin/">
            <q-item-section>Admin area</q-item-section>
            <q-item-section side><q-icon name="lock" size="xs" color="primary" /></q-item-section>
          </q-item>
        </q-list>
        <q-list dense>
          <q-separator class="q-my-xs" />
          <q-item clickable tag="a" href="/accounts/logout/">
            <q-item-section>Sign out</q-item-section>
            <q-item-section side><q-icon name="logout" size="xs" /></q-item-section>
          </q-item>
        </q-list>
      </q-menu>
    </q-btn>
    <user-notifications />
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue';

import UserNotifications from '@/components/UserNotifications.vue';

const props = defineProps<{
  user: DjangoAuthenticatedUser;
}>();

const is_steering = computed(() =>
  props.user?.groups.some((group: DjangoGroup) => group.name === 'Steering Committee')
);
</script>
