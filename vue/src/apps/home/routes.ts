import { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '',
    name: 'home',
    strict: true,
    components: {
      default: () => import('./HomeApp.vue'),
      menu: () => import('./HomeMenu.vue'),
    },
  },
];

export default routes;
