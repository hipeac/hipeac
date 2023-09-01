<template>
  <plotly-graph :data="data" />
  {{ data }}
</template>

<script setup lang="ts">
import { computed, ref } from 'vue';
import PlotlyGraph from './PlotlyGraph.vue';

const props = defineProps<{
  data: Array<{ month: str; count: number }>;
}>();

// First, sort the data array by month in ascending order
const odata = ref(props.data);
const sortedData = odata.value.sort((a, b) => {
  const aDate = new Date(a.month);
  const bDate = new Date(b.month);
  return aDate - bDate;
});

// Create an object to store the counts for each year
const countsByYear = {};

// Loop through the sorted data array and group the counts by year
sortedData.forEach(({ month, count }) => {
  const year = new Date(month).getFullYear();
  if (!countsByYear[year]) {
    countsByYear[year] = Array(12).fill(null); // Initialize an array with 12 zeroes
  }
  const monthIndex = new Date(month).getMonth();
  countsByYear[year][monthIndex] += count;
});

// Define the x and y axis labels using the getMonth() and getFullYear() methods
const xLabels = new Array(12).fill().map((_, index) => new Date(0, index).toLocaleString('default', { month: 'long' }));
const yLabels = Object.keys(countsByYear).map((year) => new Date(parseInt(year), 0).getFullYear());

// Convert the counts by year object to a Plotly heatmap data array
const heatmapData = Object.keys(countsByYear).map((year) => {
  return countsByYear[year];
});

// Create the Plotly heatmap trace
const heatmapTrace = {
  x: xLabels,
  y: yLabels,
  z: heatmapData,
  type: 'heatmap',
  hoverongaps: false,
};

// based on props.data, distribute monthly data in a Plotly heatmap
// x axis contains the years and y contains the months, with the count as value
// z is a collection of arrays for the years, each array contains the counts for the months
// months should be ordered on the correct order
const data = computed(() => {
  return [heatmapTrace];
});
</script>
