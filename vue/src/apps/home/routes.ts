import { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '',
    name: 'home',
    strict: true,
    components: {
      default: () => import('./HomeApp.vue'),
    }
  },
];

export default routes;
