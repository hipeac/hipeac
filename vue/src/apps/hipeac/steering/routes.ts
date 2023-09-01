import { RouteRecordRaw } from 'vue-router';

const routes: RouteRecordRaw[] = [
  {
    path: '',
    redirect: { name: 'dashboard' },
    components: {
      default: () => import('./SteeringApp.vue'),
      menu: () => import('./SteeringMenu.vue'),
    },
    children: [
      {
        path: '/',
        name: 'dashboard',
        strict: true,
        component: () => import('./pages/DashboardPage.vue'),
      },
      {
        path: '/action-points/',
        name: 'actionPoints',
        strict: true,
        component: () => import('./pages/ActionPointsPage.vue'),
      },
      {
        path: '/meetings/',
        name: 'meetings',
        strict: true,
        component: () => import('./pages/MeetingsPage.vue'),
        children: [
          {
            name: 'meetingDetail',
            path: ':meetingId/',
            component: import('./pages/MeetingDetailPage.vue'),
          },
        ],
      },
      {
        path: '/membership-requests/',
        name: 'membershipRequests',
        strict: true,
        component: () => import('./pages/MembershipRequestsPage.vue'),
      },
    ],
  },
];

export default routes;
