<template>
  <session-dialog :obj="(obj as HipeacSession)">
    <template #side-col>
      <div class="col-12 col-md-4">
        <div v-if="!obj.has_ended" class="q-gutter-sm">
          <q-btn v-if="!registration" @click="register" unelevated no-caps color="primary" class="full-width"
            >Register</q-btn
          >
          <q-btn v-else @click="unregister" outline no-caps color="negative" class="full-width">Unregister</q-btn>
          <q-btn
            v-if="registration"
            type="a"
            :href="registration.zoom_access_link"
            target="_black"
            rel="noopener"
            unelevated
            no-caps
            color="primary"
            class="full-width"
            >Join Zoom webinar</q-btn
          >
        </div>
      </div>
    </template>
  </session-dialog>
</template>

<script setup lang="ts">
import { computed } from 'vue';
import { storeToRefs } from 'pinia';

import { api } from '@/axios';
import { notify } from '@/utils/notify';
import { useStore } from '../store';

import SessionDialog from '@/components/events/SessionDialog.vue';

const store = useStore();

const props = defineProps<{
  obj: HipeacWebinar;
}>();

const { registrations } = storeToRefs(store);

const registration = computed<HipeacWebinarRegistration | null>(() => {
  return registrations.value.find((reg) => reg.webinar == props.obj.id) || null;
});

function register() {
  api.post(props.obj.rel_register).then((res) => {
    store.addRegistration(res.data[0]); // TODO: check why API is returning a list here
    notify.success('You have been registered to the webinar.');
  });
}

function unregister() {
  api.post(props.obj.rel_unregister).then(() => {
    if (registration.value) store.removeRegistration(registration.value);
    notify.info('You have been unregistered from the webinar.');
  });
}
</script>
