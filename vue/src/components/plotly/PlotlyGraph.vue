<style lang="scss">
.plotly__canvas {
  height: 350px;
}
</style>

<template>
  <div ref="canvas" class="plotly__canvas"></div>
</template>

<script setup lang="ts">
import { onMounted, ref, watch } from 'vue';
import { BarChart } from '@toast-ui/chart';

import '@toast-ui/chart/dist/toastui-chart.min.css';
import { PRIMARY_COLOR } from '@/colors.ts';

const props = defineProps<{
  data: Any;
  showLegend?: boolean;
}>();

const canvas = ref(null);
const data = {
  categories: ['Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'],
  series: [
    {
      name: 'Budget',
      data: [5000, 3000, 5000, 7000, 6000, 4000, 1000],
    },
    {
      name: 'Income',
      data: [8000, 4000, 7000, 2000, 6000, 3000, 5000],
    },
  ],
};
const options = {
  chart: { width: 700, height: 400 },
};

onMounted(() => {
  new BarChart({ el: canvas.value, data, options });
});

watch(
  () => props.data,
  (newData) => {
    new BarChart({ el: canvas.value, newData, options });
  }
);
</script>
