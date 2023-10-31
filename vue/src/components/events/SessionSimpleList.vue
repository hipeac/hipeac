<template>
  <div v-for="session in sessions" :key="session.id" class="row">
    <div class="col-12 border-top"></div>
    <div class="col-3 col-sm-2 q-py-md q-px-sm text-center">
      <h4 class="text-h6 text-weight-light">{{ session.start_day }}</h4>
    </div>
    <div
      class="col border-left q-py-md q-pl-lg col-pointer"
      @click="router.push({ params: { sessionId: session.id } })"
    >
      <!--<hipeac-profile-item v-if="keynotesDict[session.id] && keynotesDict[session.id].main_speaker" :profile="keynotesDict[session.id].main_speaker.profile" class="q-px-none q-pt-none q-mb-sm"></hipeac-profile-item>-->
      <h3 class="q-mb-xs text-h6">{{ session.title }}</h3>
      <ul class="row inline q-col-gutter-y-sm q-col-gutter-x-md q-mb-none text-caption text-grey-9">
        <li>
          <q-icon size="xs" name="lens" :color="session.color" class="q-mr-xs"></q-icon>
          <span>{{ session.type.value }}</span>
        </li>
        <li>
          <q-icon size="xs" name="schedule" color="grey-7" class="q-mr-xs"></q-icon>
          <span>{{ session.start_time }} - {{ session.end_time }}</span>
        </li>
      </ul>
    </div>
  </div>
</template>

<script setup lang="ts">
import { useRouter } from 'vue-router';

const router = useRouter();

defineProps<{
  sessions: HipeacSession[];
}>();
</script>
