<template>
  <plotly-graph :data="data" :show-legend="props.showLegend" />
  <q-select v-model="year" :options="years" label="Year" filled dense color="primary" style="width: 100px" />
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import PlotlyGraph from './PlotlyGraph.vue';

import { PRIMARY_COLOR } from '@/colors.ts';

const props = defineProps<{
  data: Array<{ month: str; count: number }>;
  showLegend?: boolean;
}>();

const year = ref(new Date().getFullYear());

/* Given the monthly data (in ISO string: ), we generate a dictionary with data per year
so that we can later get the years and filtr the shown data */
const yearlyData = computed(() => {
  const data = props.data;
  const yearlyData = {};
  for (let i = 0; i < data.length; i++) {
    const date = new Date(data[i].month);
    const year = date.getFullYear();
    if (yearlyData[year] === undefined) {
      yearlyData[year] = [];
    }
    yearlyData[year].push(data[i]);
  }
  return yearlyData;
});

const years = computed(() => {
  return Object.keys(yearlyData.value);
});

// get data with the structure: { x: [month1, month2, ...], y: [count1, count2, ...] }
// for years that have less than 12 months, we complete the data with empty months so we always have 12 months for a year with full name
// the montly data will be shown in bars, and the aggregated data in a line
var data = computed(() => {
  const data = yearlyData.value[year.value];
  const months = [];
  for (let i = 0; i < 12; i++) {
    months.push(new Date(2021, i, 1).toLocaleString('default', { month: 'short' }));
  }
  const counts = [];
  const totals = [];
  let total = 0;

  for (let i = 0; i < months.length; i++) {
    const monthData = data.find((d) => new Date(d.month).getMonth() === i);
    if (monthData === undefined) {
      counts.push(null);
      totals.push(total);
    } else {
      counts.push(monthData.count);
      total += monthData.count;
      totals.push(total);
    }
  }

  return [
    {
      name: 'Monthly',
      type: 'bar',
      x: months,
      y: counts,
      marker: {
        color: '#dddddd',
      },
    },
    {
      name: 'Total',
      type: 'scatter',
      mode: 'lines',
      connectgaps: true,
      x: months,
      y: totals,
      marker: {
        color: PRIMARY_COLOR,
      },
    },
  ];
});
</script>
