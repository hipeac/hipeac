<style lang="scss">
.q-dialog__inner--minimized {
  padding: 0;
}

.hipeac__session-dialog-layout {
  height: 800px;

  .q-dialog__inner--minimized > & {
    width: 1100px !important;
    max-width: 100vw;
  }

  .q-stepper--vertical .q-stepper__tab {
    padding: 12px 24px 12px 20px;
  }
}
</style>

<template>
  <q-layout view="hHh lpR fFf" container class="bg-white hipeac__session-dialog-layout">
    <q-header class="bg-white">
      <q-toolbar class="text-dark bg-grey-2">
        <q-tabs v-model="tab" no-caps inline-label shrink class="q-mr-md">
          <q-tab name="main">
            <q-icon size="xs" name="lens" :color="obj.color" class="q-mr-sm" />
            <div class="q-tab__label">{{ obj.type.value }}</div>
          </q-tab>
          <q-tab v-if="obj.main_speaker" name="speaker" label="Main speaker" />
          <q-tab v-if="obj.program" name="program" label="Program" />
          <q-tab v-if="obj._registered" name="attendees" label="Attendees" />
        </q-tabs>
        <q-space />
        <!--<editor-link v-if="session.editor_href" type="btn" :url="session.editor_href" target="_blank" />-->
        <q-btn flat round v-close-popup icon="close" />
      </q-toolbar>
      <div class="q-pa-md text-center text-caption text-grey-8">
        <ul class="row inline q-col-gutter-y-sm q-col-gutter-x-md q-mb-none">
          <li>
            <q-icon size="xs" name="today" class="q-mr-xs" />
            <span>{{ obj.start_day }}</span>
          </li>
          <li>
            <q-icon size="xs" name="schedule" class="q-mr-xs" />
            <span>{{ obj.start_time }} - {{ obj.end_time }}</span>
          </li>
          <li v-if="$q.screen.gt.sm && obj._registered" class="text-bold text-green">
            <q-icon size="xs" name="fact_check" color="green-7" class="q-mr-xs" />
            <span>Registered</span>
          </li>
        </ul>
      </div>
      <q-separator class="q-mb-none" />
    </q-header>
    <q-page-container>
      <q-page>
        <q-tab-panels v-model="tab" :swipeable="$q.screen.lt.md" horizontal class="q-pa-sm">
          <q-tab-panel name="main">
            <div class="row q-col-gutter-x-xl q-col-gutter-y-lg">
              <div class="col-12 col-md">
                <h3 class="q-mb-md">{{ obj.title }}</h3>
                {{ obj.summary }}
              </div>
              <slot name="side-col">
                <div class="col-12 col-md-4"></div>
              </slot>
            </div>
          </q-tab-panel>
          <q-tab-panel name="program">
            {{ obj.program }}
          </q-tab-panel>
          <q-tab-panel name="attendees">
            <attendees-list :session="obj" />
          </q-tab-panel>
        </q-tab-panels>
      </q-page>
    </q-page-container>
    <q-footer class="bg-white">
      <slot name="footer"></slot>
    </q-footer>
  </q-layout>
</template>

<script setup lang="ts">
import { ref } from 'vue';

import AttendeesList from './AttendeesList.vue';

defineProps<{
  obj: HipeacSession;
}>();

const tab = ref<string>('main');
</script>
