<template>
  <div>
    <router-view />
  </div>
</template>

<script setup lang="ts">
import { usePage } from '@inertiajs/vue3';

import { useStore } from './store';

const page = usePage();
const store = useStore();

store.init(page.props.django_user as DjangoAuthenticatedUser | null);
</script>
