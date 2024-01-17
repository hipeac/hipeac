<template>
  <div>
    <div class="row q-col-gutter-y-xl">
      <div class="col-12 col-md-7" :class="{ 'q-py-lg': $q.screen.gt.sm }">
        <big-display
          title="Bridging industry and academia in computing systems since 2004"
          subtitle="Spanning the compute continuum from edge to cloud, HiPEAC is a network of around 2,000 world-class
            computing systems researchers, industry representatives and students."
          class="q-mt-md"
          :class="{ 'q-mt-xl': $q.screen.gt.sm }"
        />
      </div>
      <div class="col-12 col-md" :class="{ 'q-pt-xl q-pb-lg': $q.screen.gt.sm }">
        <q-card flat bordered class="full-height">
          <q-tabs v-model="tab" no-caps switch-indicator indicator-color="primary">
            <q-tab name="industry"><h5>For industry</h5></q-tab>
            <q-tab name="academia"><h5>For academia</h5></q-tab>
          </q-tabs>
          <q-tab-panels v-model="tab">
            <q-tab-panel v-for="(text, type) in texts" :key="type" :name="type">
              <q-list>
                <q-item
                  v-for="(item, index) in text.items"
                  :key="index"
                  :href="item[2]"
                  class="q-pa-md rounded-borders"
                >
                  <q-item-section avatar>
                    <q-avatar color="grey-3" text-color="dark" :icon="item[0]" />
                  </q-item-section>
                  <q-item-section>{{ item[1] }}</q-item-section>
                  <q-item-section side>
                    <q-icon name="arrow_forward_ios" size="xs" />
                  </q-item-section>
                </q-item>
              </q-list>
            </q-tab-panel>
          </q-tab-panels>
        </q-card>
      </div>
    </div>
    <event-banner :event="nextEvent" with-join-btn class="q-mt-lg" />
    <div class="row q-col-gutter-lg q-mt-none">
      <div class="col-12 col-md-4 d-flex align-items-stretch">
        <q-card flat bordered class="q-px-lg q-pt-sm q-pb-lg full-height">
          <event-list :items="$page.props.events" :min="8" :max="14" />
        </q-card>
      </div>
      <div class="col-12 col-md d-flex align-items-stretch">
        <q-card flat bordered class="q-px-lg q-pt-sm q-pb-lg full-height">
          <div class="row q-col-gutter-xl">
            <div class="col-12 col-md-7">
              <div v-if="$page.props.video" class="q-mb-lg">
                <h6 class="q-mb-md">Latest from HiPEAC TV</h6>
                <q-video
                  :ratio="16 / 9"
                  :src="`https://www.youtube.com/embed/${$page.props.video.youtube_id}?rel=0`"
                  class="rounded-borders"
                />
              </div>
              <article-list :items="($page.props.articles as HipeacArticle[])" :max="10" show-more />
            </div>
            <div class="col-12 col-md">
              <a
                class="twitter-timeline"
                href="https://twitter.com/hipeac"
                data-height="1200"
                data-dnt="true"
                data-chrome="nofooter noborders"
              ></a>
            </div>
          </div>
        </q-card>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, onMounted, ref } from 'vue';
import { usePage } from '@inertiajs/vue3';

import BigDisplay from '@/components/BigDisplay.vue';
import ArticleList from '@/components/communication/ArticleList.vue';
import EventBanner from '@/components/events/EventBanner.vue';
import EventList from '@/components/events/EventList.vue';

const page = usePage();
const tab = ref('industry');

const texts = {
  industry: {
    title: 'For industry',
    items: [
      ['swap_horizontal_circle', 'Grow your technology user base or ecosystem at HiPEAC events', '/events/'],
      ['assistant', 'Find highly qualified, specialist staff and interns with HiPEAC Jobs', '/jobs/'],
      ['star', 'Stay ahead of the competition and influence policy with the HiPEAC Vision', '/vision/'],
    ],
  },
  academia: {
    title: 'For academia',
    items: [
      ['question_answer', 'Disseminate your research and build project consortia at HiPEAC events', '/events/'],
      ['school', 'Recruit PhD students and post-docs with HiPEAC Jobs', '/jobs/'],
      ['directions', 'Shape the direction of EU-funded research with the HiPEAC Vision', '/vision/'],
    ],
  },
};

const nextEvent = computed(() => {
  const events = page.props.events.slice().reverse();
  const now = new Date();
  return events.find((event) => new Date(event.end_date) > now);
});

onMounted(() => {
  let twitterScript = document.createElement('script');
  twitterScript.setAttribute('src', 'https://platform.twitter.com/widgets.js');
  document.head.appendChild(twitterScript);
});
</script>
