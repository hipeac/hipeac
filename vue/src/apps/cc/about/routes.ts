import { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '',
    name: 'about',
    strict: true,
    components: {
      default: () => import('./AboutApp.vue' as string),
    },
  },
];

export default routes;
