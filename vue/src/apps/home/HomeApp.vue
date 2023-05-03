<style lang="scss">
.hipeac__home_app {
  h1 {
    text-align: center;
    font-family: 'Roboto Slab', Georgia, 'Times New Roman', Times, serif;
    font-size: 1.75rem;
    font-weight: 600;
    color: #222;

    @media (min-width: 768px) {
      width: 90%;
      text-align: left;
      font-size: 2.5rem;
      line-height: 1.1;
    }
  }

  h2 {
    text-align: center;
    font-size: 1.25rem;
    font-weight: 300;
    line-height: 1.4;

    @media (min-width: 768px) {
      width: 90%;
      text-align: left;
      font-size: 1.35rem;
      padding-left: 24px;
    }

    span {
      background: linear-gradient(to bottom, transparent 80%, #ffe800 1%, #ffe800);
    }
  }

  .q-focus-helper {
    display: none;
  }
}
</style>

<template>
  <div class="hipeac__home_app">
    <div class="row q-col-gutter-lg items-center">
      <div class="col-12 col-md-7">
        <h1 class="q-mb-lg">Bridging industry and academia in computing systems since 2004</h1>
        <h2>
          <span
            >Spanning the compute continuum from edge to cloud, HiPEAC is a network of around 2,000 world-class
            computing systems researchers, industry representatives and students.</span
          >
        </h2>
      </div>
      <div class="col-12 col-md q-pt-xl q-pb-lg">
        <q-card flat bordered class="full-height">
          <q-tabs v-model="tab" no-caps switch-indicator indicator-color="primary">
            <q-tab name="industry"><h5>For industry</h5></q-tab>
            <q-tab name="academia"><h5>For academia</h5></q-tab>
          </q-tabs>
          <q-tab-panels v-model="tab" class="q-px-sm">
            <q-tab-panel v-for="(text, type) in texts" :key="type" :name="type">
              <q-list>
                <q-item v-for="(item, index) in text.items" :key="index" :href="item[2]" class="q-px-none q-py-md">
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
                <h6 class="q-mb-md">Latest from H<span class="text-lowercase">i</span>PEAC TV</h6>
                <q-video
                  :ratio="16 / 9"
                  :src="`https://www.youtube.com/embed/${$page.props.video.youtube_id}?rel=0`"
                  class="rounded-borders"
                />
              </div>
              <article-list :items="$page.props.articles" :max="10" />
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
  return events.find((event) => new Date(event.start_date) > now);
});

onMounted(() => {
  let twitterScript = document.createElement('script');
  twitterScript.setAttribute('src', 'https://platform.twitter.com/widgets.js');
  document.head.appendChild(twitterScript);
});
</script>