<style lang="scss">
.hipeac__big_display {
  h1 {
    font-family: 'Roboto Slab', Georgia, 'Times New Roman', Times, serif;
    font-size: 1.65rem;
    font-weight: 600;
    color: #222;

    @media (min-width: 768px) {
      width: 85%;
      font-size: 2.35rem;
      line-height: 1.1;
    }
  }

  h2 {
    font-size: 1.1rem;
    font-weight: 300;
    line-height: 1.4;

    @media (min-width: 768px) {
      width: 90%;
      font-size: 1.25rem;
      padding-left: 24px;
    }

    span {
      background: linear-gradient(to bottom, transparent 80%, #ffe800 1%, #ffe800);
    }
  }
}
</style>

<template>
  <div class="hipeac__big_display">
    <h1 class="q-mb-lg">{{ title }}</h1>
    <h2>
      <span>{{ subtitle }}</span>
    </h2>
  </div>
</template>

<script setup lang="ts">
defineProps<{
  title?: string | undefined;
  subtitle?: string | undefined;
}>();
</script>
