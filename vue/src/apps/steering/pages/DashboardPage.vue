<template>
  <div class="row q-col-gutter-lg">
    <div class="col-12 col-md-8">
      <q-card flat bordered>
        <q-tabs dense no-caps switch-indicator indicator-color="primary">
          <q-tab name="all" label="All" />
          <q-tab name="open" label="Open" />
          <q-tab name="closed" label="Closed" />
        </q-tabs>
        <plotly-monthly-graph :data="$page.props.stats_jobs_per_month" :show-legend="false" />
      </q-card>
    </div>
    <div class="col-12 col-md-8"></div>
  </div>
</template>

<script setup lang="ts">
import PlotlyMonthlyGraph from '@/components/plotly/PlotlyMonthlyGraph.vue';
</script>
