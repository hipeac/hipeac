<style lang="scss">
.hipeac__layout {
  h6 {
    font-family: inherit !important;
    text-transform: none;
    font-size: 20px;
    padding-top: 12px;
  }
}
</style>

<template>
  <q-layout view="hHh LpR lff" class="hipeac__layout">
    <q-dialog v-model="visibleDialogMenu" position="top" full-width full-height>
      <q-card class="bg-particles">
        <q-card-section>
          <q-btn unelevated round icon="close" color="white" text-color="dark" v-close-popup />
          <div class="q-gutter-y-md text-center q-pb-xl">
            <img src="@/assets/hipeac.svg" class="logo q-mt-xs" />
            <p v-for="item in hipeac_menu" :key="item[1]" class="text-h4 text-grey-8 text-weight-light">
              <a :href="item[1]" :class="item[2]" class="flat">{{ item[0] }}</a>
            </p>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
    <q-header bordered class="bg-white text-dark hipeac__header">
      <q-toolbar class="hipeac__toolbar container">
        <q-btn
          flat
          round
          v-show="$q.screen.lt.md"
          @click="visibleDialogMenu = !visibleDialogMenu"
          icon="menu"
          class="q-mr-sm text-hipeac"
          style="margin-left: -12px"
        ></q-btn>
        <a href="/" class="q-mr-lg">
          <img src="@/assets/hipeac.svg" class="logo q-mt-xs" />
        </a>
        <q-btn-group stretch flat v-show="$q.screen.gt.sm">
          <q-btn
            no-caps
            v-for="item in hipeac_menu"
            :key="item[1]"
            :href="item[1]"
            :label="item[0]"
            :class="item[2]"
          ></q-btn>
        </q-btn-group>
        <q-space></q-space>
        <user-menu v-if="django_user" :user="django_user" />
        <div v-else>
          <q-btn outline no-caps href="/accounts/signup/" color="green" class="q-mr-sm">Join</q-btn>
          <q-btn outline no-caps :href="`/accounts/login/?next=${$page.url}`" color="primary">Log in</q-btn>
        </div>
      </q-toolbar>
    </q-header>

    <q-page-container>
      <q-page
        :class="{ 'q-py-xs q-px-lg': $q.screen.gt.sm, 'q-py-none bg-white': $q.screen.lt.md }"
        style="margin-top: 56px"
      >
        <router-view name="menu" />
        <div class="container">
          <router-view class="q-py-lg q-pb-xl" />
          <div class="q-mt-xl text-transparent">.</div>
        </div>
      </q-page>
    </q-page-container>

    <q-footer class="bg-transparent text-grey-8 q-py-xl" :class="{ 'q-px-xl': $q.screen.gt.sm }">
      <div class="container">
        <div class="row q-col-gutter-lg justify-between text-caption" :class="{ reverse: $q.screen.gt.sm }">
          <div class="col-12 col-md-3" :class="{ 'text-right': $q.screen.gt.sm }">
            <img src="@/assets/eu-horizon.svg" style="height: 40px" />
          </div>
          <div class="col-12 col-md-9">
            <p class="text-caption q-mb-sm">
              <strong>&copy; 2004-{{ year }} High Performance, Edge And Cloud computing</strong>
            </p>
            <p class="text-caption">
              The HiPEAC project has received funding from the European Union's Horizon Europe research and innovation
              funding programme under grant agreement number 101069836. Views and opinions expressed are however those
              of the author(s) only and do not necessarily reflect those of the European Union. Neither the European
              Union nor the granting authority can be held responsible for them.
            </p>
            <div class="q-gutter-x-md">
              <a href="/privacy-policy/" class="inherit">Privacy policy</a>
              <a href="/disclaimer/" class="inherit">Disclaimer</a>
              <a :href="`mailto:${contactEmail}`" class="inherit">
                <q-icon name="alternate_email" class="q-mr-xs"></q-icon>Contact</a
              >
            </div>
          </div>
        </div>
      </div>
    </q-footer>
  </q-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue';

import UserMenu from '@/components/UserMenu.vue';

// get basic info from Django
defineProps<{
  django_csrf_token: string;
  django_debug: boolean;
  django_user: DjangoAuthenticatedUser | null;
  git_commit_hash: string;
  hipeac_menu: Array<[string, string, string]>;
}>();

const contactEmail = 'info@hipeac.net';
const visibleDialogMenu = ref(false);
const year = new Date().getFullYear();
</script>