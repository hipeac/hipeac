import { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '',
    redirect: { name: 'upcomingWebinars' },
    components: {
      default: () => import('./WebinarsApp.vue'),
      menu: () => import('./WebinarsMenu.vue'),
    },
    children: [
      {
        path: '/:sessionId(\\d+)?/',
        name: 'upcomingWebinars',
        strict: true,
        component: () => import('./pages/UpcomingWebinarsPage.vue'),
      },
      {
        path: '/previous/:sessionId(\\d+)?/',
        name: 'pastWebinars',
        strict: true,
        component: () => import('./pages/PastWebinarsPage.vue'),
      },
      {
        path: '/logistics/',
        name: 'logistics',
        strict: true,
        component: () => import('./pages/LogisticsPage.vue'),
      },
    ],
  },
];

export default routes;
