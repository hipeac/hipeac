<template>
  <div>
    {{ session.rel_attendees }}
  </div>
</template>

<script setup lang="ts">
defineProps<{
  session: HipeacSession;
}>();
</script>
