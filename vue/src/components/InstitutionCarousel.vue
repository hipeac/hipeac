<style type="scss">
.hipeac__carousel-logo {
  max-width: 100%;
  height: 9ch;
}
</style>

<template>
  <q-carousel
    v-model="slide"
    transition-prev="slide-right"
    transition-next="slide-left"
    swipeable
    animated
    infinite
    autoplay
    height="90px"
    class="bg-transparent q-ma-none q-pa-none"
  >
    <q-carousel-slide
      v-for="(group, idx) in groups"
      :key="idx"
      :name="idx"
      class="column items-center q-ma-none q-pa-none"
    >
      <div class="row fit items-center justify-center q-col-gutter-lg">
        <div
          v-for="institution in group"
          :key="institution.id"
          class="col column full-height justify-center text-center"
        >
          <q-img
            @click="callback(institution)"
            :src="institution.images?.lg"
            fit="contain"
            class="hipeac__carousel-logo cursor-pointer"
          />
        </div>
      </div>
    </q-carousel-slide>
  </q-carousel>
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';

const props = defineProps<{
  institutions: Institution[];
  callback: (institution: Institution) => void;
  random?: boolean;
}>();

const slide = ref<number>(0);

const groups = computed<Institution[][]>(() => {
  const groupSize = 5;
  const groups: Institution[][] = [];
  const institutions: Institution[] = [...props.institutions];

  if (props.random) {
    institutions.sort(() => Math.random() - 0.5);
  }

  for (let i = 0; i < institutions.length; i += groupSize) {
    groups.push(institutions.slice(i, i + groupSize));
  }

  return groups;
});
</script>
