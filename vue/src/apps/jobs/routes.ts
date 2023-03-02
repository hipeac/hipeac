import { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '',
    redirect: { name: 'openPositions' },
    components: {
      default: () => import('./JobsApp.vue'),
      menu: () => import('./JobsMenu.vue' as string),
    },
    children: [
      {
        path: '/',
        name: 'openPositions',
        strict: true,
        component: () => import('./pages/OpenPositionsPage.vue' as string),
      },
      {
        path: '/recruitment/',
        name: 'about',
        strict: true,
        component: () => import('./pages/AboutPage.vue' as string),
      },
    ],
  },
];

export default routes;
