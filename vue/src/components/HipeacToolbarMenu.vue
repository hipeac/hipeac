<template>
  <q-page-sticky expand position="top" class="hipeac__submenu" :class="{ 'bg-dark': dark }">
    <q-toolbar class="container" :class="{ 'bg-dark': dark }">
      <q-toolbar-title :class="{ 'q-pl-none': $q.screen.gt.sm }">{{ title }}</q-toolbar-title>
      <q-tabs v-if="$q.screen.gt.sm && menu.length" stretch inline-label no-caps>
        <q-route-tab
          v-for="(item, i) in menu"
          :key="i"
          :exact="item.exact"
          :href="item.href"
          :to="item.to"
          :class="{ 'q-px-xs': !item.label }"
        >
          <q-icon v-if="item.icon" :name="item.icon" size="20px" :class="{ 'q-mr-sm': item.label }" />
          <div v-if="item.label" class="q-tab__label">{{ item.label }}</div>
          <q-icon
            v-if="!item.icon && item.href"
            name="arrow_forward_ios"
            size="13px"
            :class="{ 'q-ml-sm': item.label }"
          />
        </q-route-tab>
      </q-tabs>
      <!--<hipeac-submenu-tabs v-if="event" :menu="menu" :checks="{'not_ready': !event.is_ready, 'ready': event.is_ready, 'registration': !!registration, 'not_active': !event.is_active, }" :hashtag="event.hashtag"></hipeac-submenu-tabs>-->
    </q-toolbar>
  </q-page-sticky>
</template>

<script setup lang="ts">
import { PropType } from 'vue';

interface MenuItem {
  readonly label: string;
  readonly href?: string;
  readonly to?: object;
  readonly icon?: string;
  readonly exact?: boolean;
}

defineProps({
  title: {
    type: String,
    required: true,
  },
  menu: {
    type: Array as PropType<MenuItem[]>,
    required: true,
  },
  dark: {
    type: Boolean,
    default: false,
  },
});
</script>
