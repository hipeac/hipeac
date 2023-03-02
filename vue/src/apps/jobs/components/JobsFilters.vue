<style lang="scss">
.filter-dense {
  padding: 0 !important;
  min-height: auto !important;

  .q-item__section--side {
    padding-right: 4px !important;
  }

  .q-item__section--avatar {
    height: 20px;
    min-width: 20px !important;
  }
}
</style>

<template>
  <q-list separator class="hipeac__custom-list text-caption">
    <q-expansion-item dense label="Type" default-opened header-class="q-px-none q-py-sm">
      <q-list dense class="q-pb-lg">
        <q-item v-for="type in typeOptions" :key="type.label" tag="label" class="filter-dense">
          <q-item-section avatar>
            <q-radio v-model="filter.typeId" :val="type.value" size="xs" />
          </q-item-section>
          <q-item-section>
            <q-item-label class="ellipsis">{{ type.label }}</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-expansion-item>
    <q-expansion-item dense group="hipeac__jobs-filter" label="Topics" header-class="q-px-none q-py-sm">
      <q-list dense class="q-pb-lg">
        <q-item v-for="topic in topics" :key="topic.id" tag="label" class="filter-dense">
          <q-item-section avatar>
            <q-checkbox v-model="filter.topicIds" :val="topic.id" size="xs" />
          </q-item-section>
          <q-item-section>
            <q-item-label class="ellipsis">{{ topic.value }}</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-expansion-item>
    <q-expansion-item dense group="hipeac__jobs-filter" label="Career levels" header-class="q-px-none q-py-sm">
      <q-list dense class="q-pb-lg">
        <q-item v-for="level in careerLevels" :key="level.id" tag="label" class="filter-dense">
          <q-item-section avatar>
            <q-checkbox v-model="filter.careerLevelIds" :val="level.id" size="xs" />
          </q-item-section>
          <q-item-section>
            <q-item-label class="ellipsis">{{ level.value }}</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-expansion-item>
    <q-expansion-item dense group="hipeac__jobs-filter" label="Countries" header-class="q-px-none q-py-sm">
      <q-list dense class="q-pb-lg">
        <q-item v-for="country in countries" :key="country.code" tag="label" class="filter-dense">
          <q-item-section avatar>
            <q-checkbox v-model="filter.countryCodes" :val="country.code" size="xs" />
          </q-item-section>
          <q-item-section>
            <q-item-label class="ellipsis">{{ country.name }}</q-item-label>
          </q-item-section>
        </q-item>
      </q-list>
    </q-expansion-item>
  </q-list>
</template>

<script setup lang="ts">
import { ref } from 'vue';

const props = defineProps<{
  filter: JobsFilter;
  topics: Topic[];
  careerLevels: CareerLevel[];
  countries: Country[];
}>();

const filter = ref(props.filter);

const typeOptions: QuasarOption[] = [
  { value: null, label: 'All' },
  { value: 16, label: 'Full-time' },
  { value: 17, label: 'Internship' },
];
</script>
