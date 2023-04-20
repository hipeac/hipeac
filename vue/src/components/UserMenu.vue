<template>
  <a class="cursor-pointer">
    <span v-show="$q.screen.gt.xs">{{ displayName }} &nbsp;</span><q-icon name="account_circle" size="xxs" />
    <q-menu anchor="top end" self="bottom right" :offset="[0, 8]">
      <q-list dense style="min-width: 140px" class="text-body2 q-py-sm">
        <q-item clickable tag="a" href="/">
          <q-item-section>Homepage</q-item-section>
        </q-item>
        <q-item clickable tag="a" href="/u/logout/">
          <q-item-section>{{ $t('menu.logout') }}</q-item-section>
          <q-item-section side><q-icon name="logout" size="xs" /></q-item-section>
        </q-item>
      </q-list>
    </q-menu>
  </a>
</template>

<script setup lang="ts">
import { computed } from 'vue';

const props = defineProps({
  user: Object,
});

const displayName = computed(() => {
  if (props.user) {
    return `${props.user.first_name} ${props.user.last_name}` || props.user.username;
  }
  return '';
});
</script>
