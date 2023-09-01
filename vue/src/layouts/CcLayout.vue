<template>
  <q-layout view="hHh LpR lff" class="cc__layout">
    <q-dialog v-model="visibleDialogMenu" position="top" full-width full-height>
      <q-card class="bg-particles">
        <q-card-section>
          <q-btn unelevated round icon="close" color="white" text-color="dark" v-close-popup />
          <div class="q-gutter-y-md text-center q-pb-xl">
            <a href="/">
              <img src="@/assets/cc.svg" class="logo q-mt-xs" />
            </a>
            <p v-for="item in site_menu" :key="item[1]" class="text-h4 text-grey-8 text-weight-light">
              <a :href="item[1]" :class="item[2]" class="flat">{{ item[0] }}</a>
            </p>
          </div>
        </q-card-section>
      </q-card>
    </q-dialog>
    <q-header bordered class="bg-white text-dark cc__header">
      <q-toolbar class="cc__toolbar container">
        <q-btn
          flat
          round
          v-show="$q.screen.lt.md"
          @click="visibleDialogMenu = !visibleDialogMenu"
          icon="menu"
          class="q-mr-sm"
          style="margin-left: -12px"
        ></q-btn>
        <a href="/" class="q-mr-xl">
          <img src="@/assets/cc.svg" class="logo q-mt-xs" />
        </a>
        <q-btn-group stretch flat v-show="$q.screen.gt.sm">
          <q-btn
            no-caps
            v-for="item in site_menu"
            :key="item[1]"
            :href="item[1]"
            :label="item[0]"
            :class="item[2]"
          ></q-btn>
        </q-btn-group>
        <q-space />
        <user-menu v-if="django_user" :user="django_user" />
      </q-toolbar>
    </q-header>

    <q-page-container>
      <q-page
        :class="{ 'q-py-xs q-px-lg': $q.screen.gt.sm, 'q-py-none bg-white': $q.screen.lt.md }"
        style="margin-top: 56px"
      >
        <div class="container">
          <router-view class="q-py-lg q-pb-xl" :class="{ 'q-py-xl': $q.screen.gt.sm }" />
        </div>
      </q-page>
    </q-page-container>

    <q-footer class="bg-transparent text-grey-8 q-py-xl" :class="{ 'q-px-xl': $q.screen.gt.sm }">
      <div class="container">
        <div class="row q-col-gutter-lg justify-between text-caption" :class="{ reverse: $q.screen.gt.sm }">
          <div class="col-12 col-md-3 q-pt-xl" :class="{ 'text-right': $q.screen.gt.sm }">
            <img src="@/assets/eu-horizon.svg" style="height: 40px" />
          </div>
          <div class="col-12 col-md-9">
            <p class="text-caption q-mb-sm">
              <strong>&copy; 2023 Computing Continuum</strong>
            </p>
            <p class="text-caption">
              <!--Computing Continuum is .-->
            </p>
            <div class="q-gutter-x-lg q-my-md text-grey">
              <a
                href="https://github.com/computing-continuum"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="GitHub"
                class="inherit"
              >
                <q-icon :name="iconGitHub" size="sm" />
              </a>
              <a
                href="https://mastodon.social/@computing_continuum"
                target="_blank"
                rel="noopener noreferrer"
                aria-label="Mastodon"
                class="inherit"
              >
                <q-icon :name="iconMastodon" size="sm" />
              </a>
            </div>
            <!--<div class="q-gutter-x-md">
              <a href="/privacy-policy/" class="inherit">Privacy policy</a>
              <a href="/disclaimer/" class="inherit">Disclaimer</a>
              <a :href="`mailto:${contactEmail}`" class="inherit">
                <q-icon name="alternate_email" class="q-mr-xs"></q-icon>Contact</a
              >
            </div>-->
          </div>
        </div>
      </div>
    </q-footer>
  </q-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue';

import { useCommonStore } from '@/stores/common';
import { useUserStore } from '@/stores/user';

import UserMenu from '@/components/UserMenu.vue';

import { iconGitHub, iconMastodon } from '@/icons';

const commonStore = useCommonStore();
const userStore = useUserStore();

// get basic info from Django
const props = defineProps<{
  django_csrf_token: string;
  django_debug: boolean;
  django_user: DjangoAuthenticatedUser | null;
  git_commit_hash: string;
  site_menu: Array<[string, string, string]>;
}>();

const visibleDialogMenu = ref(false);

// init
commonStore.init();
if (props.django_user) userStore.init(props.django_user);
</script>
