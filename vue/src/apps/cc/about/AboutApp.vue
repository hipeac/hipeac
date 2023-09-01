<template>
  <div>
    <div class="row justify-center q-mb-xl">
      <div class="col-12 col-md-11 text-center q-pb-xl">
        <h3 class="text-display">
          Explore the core projects driving Computing Continuum, each pivotal to advancing Europe's computing ecosystem.
        </h3>
      </div>
    </div>
    <q-list separator>
      <q-item v-for="p in $page.props.projects" :key="p.id" class="q-pt-md">
        <div class="row items-center q-col-gutter-lg rounded-borders q-py-md">
          <div class="col-2 col-sm-1 col-md">
            <img :src="p.project.images.lg" class="full-width" />
          </div>
          <div class="col-12 col-md-11" :class="{'q-pl-xl': $q.screen.gt.sm}">
            <h5 class="q-mb-md">{{ p.project.name }}</h5>
            <marked-div :text="p.description" />
          </div>
        </div>
      </q-item>
    </q-list>
  </div>
</template>

<script setup lang="ts">
import MarkedDiv from '@/components/MarkedDiv.vue';
</script>
