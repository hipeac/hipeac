<template>
  <q-layout view="hHh LpR lff" class="hipeac__layout">
    <q-header bordered class="bg-white text-dark hipeac__header">
      <q-toolbar class="hipeac__toolbar container">
        <q-btn flat round v-show="$q.screen.lt.md" @click="visibleDialogMenu = !visibleDialogMenu" icon="menu" class="q-mr-sm text-hipeac" style="margin-left: -12px"></q-btn>
        <a href="/" class="q-mr-lg">
          <img src="../assets/hipeac.svg" class="logo q-mt-xs">
        </a>
        <q-btn-group stretch flat v-show="$q.screen.gt.sm">
          <q-btn no-caps v-for="item in hipeac_menu" type="a" :href="item[1]" :label="item[0]" :class="item[2]"></q-btn>
        </q-btn-group>
        <q-space></q-space>
        <user-menu v-if="django_user" :user="django_user" />
        <div v-else>
          <q-btn outline no-caps type="a" href="/accounts/signup/" color="green" class="q-mr-sm">Join</q-btn>
          <q-btn outline no-caps type="a" href="/accounts/login/?next={{ request.path }}" color="primary">Log in</q-btn>
        </div>
      </q-toolbar>
    </q-header>

    <router-view name="drawer" />

    <q-page-container>
      <router-view class="q-pa-md q-pb-xl" />
    </q-page-container>

    <q-footer
      class="ugent__footer bg-ugent text-white q-py-lg q-mt-xl full-width q-px-md"
      :class="{ 'q-px-lg': $q.screen.gt.sm }"
    >
      <div class="row justify-between text-body2">
        <div class="col-12 col-md">
          <p>version {{ version }}</p>
        </div>
        <div class="col-12 col-md-9">
          <ul :class="{ 'text-right q-gutter-x-md': $q.screen.gt.sm }">
            <li :class="{ inline: $q.screen.gt.sm }">
              <a :href="`mailto:${helpdeskEmail}`">Feedback</a>
            </li>
            <li :class="{ inline: $q.screen.gt.sm }">
              <span>&copy; {{ year }}</span>
            </li>
          </ul>
        </div>
      </div>
    </q-footer>
  </q-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue';

import UserMenu from '@/components/UserMenu.vue';

// get basic info from Django
defineProps({
  django_csrf_token: String,
  django_debug: Boolean,
  django_user: [Object, null],
  git_commit_hash: String,
  hipeac_menu: Array,
});

const helpdeskEmail = 'helpdesk.ariadne@ugent.be';
const leftDrawer = ref(false);
const year = new Date().getFullYear();
</script>
