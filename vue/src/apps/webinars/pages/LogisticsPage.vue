<template>
  <q-card flat bordered class="q-px-lg q-pt-sm q-pb-lg full-height">
    <img src="@/assets/zoom.svg" class="q-my-xl q-ml-xl float-right" style="width: 150px" />
    <h6 class="q-mb-md">Logistics</h6>
    <p>
      All webinars will be delivered using Zoom. Once you register on our website, you will receive an email from Zoom
      with a unique link to join the webinar. A reminder will be sent 24 hours before the webinar starts.
    </p>
    <div v-if="registrations.length">
      <p>You can also access your upcoming webinars directly using the following links:</p>
      <q-list>
        <q-item
          v-for="reg in registrations"
          :key="reg.id"
          clickable
          tag="a"
          :href="reg.zoom_access_link"
          target="_blank"
          class="q-pa-md rounded-borders"
        >
          <q-item-section avatar>
            <q-avatar color="grey-3" text-color="dark" icon="present_to_all" />
          </q-item-section>
          <q-item-section>
            <q-item-label>{{ reg.Webinar?.title }}</q-item-label>
            <q-item-label caption
              >{{ reg.Webinar?.start_day }}, {{ reg.Webinar?.start_time }} - {{ reg.Webinar?.end_time }}</q-item-label
            >
          </q-item-section>
        </q-item>
      </q-list>
    </div>
  </q-card>
</template>

<script setup lang="ts">
import { storeToRefs } from 'pinia';

import { useStore } from '../store';

const store = useStore();

const { registrations } = storeToRefs(store);
</script>
