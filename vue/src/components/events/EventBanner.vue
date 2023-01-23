<style lang="scss">
.hipeac__banner-btn {
  position: absolute;
  top: 24px;
  left: -16px;
}
</style>

<template>
  <div v-if="event && !event.is_finished" class="relative-position">
    <a :href="event.url">
      <q-responsive :ratio="$q.screen.gt.sm ? 5 / 1 : 2 / 1">
        <q-img :src="event.images.lg" class="rounded-borders full-width" />
      </q-responsive>
    </a>
    <q-btn
      v-if="withJoinBtn"
      no-caps
      color="yellow"
      text-color="dark"
      :href="event.url"
      size="lg"
      class="hipeac__banner-btn"
    >
      <span>
        Join us in {{ event.city }} for <strong>#{{ event.hashtag }}</strong>
        <q-icon name="arrow_forward_ios" size="xs" class="q-mb-xs q-ml-sm" />
      </span>
    </q-btn>
  </div>
</template>

<script setup lang="ts">
import { PropType } from 'vue';

defineProps({
  event: Object as PropType<HipeacEvent>,
  withJoinBtn: {
    type: Boolean,
    default: false,
  },
});
</script>
