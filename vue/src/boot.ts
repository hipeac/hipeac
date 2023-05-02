import 'vite/modulepreload-polyfill';

import { createApp, h } from 'vue';
import { createRouter, createWebHashHistory, RouteRecordRaw } from 'vue-router';
import { createPinia } from 'pinia';
import { createInertiaApp } from '@inertiajs/vue3';
import { Quasar, Dialog, Notify } from 'quasar';
import * as Sentry from '@sentry/vue';

import { axios, api } from './axios.ts';

const bootApp = (routes: RouteRecordRaw[]) => {
  createInertiaApp({
    resolve: () => {
      return import('./layouts/MainLayout.vue');
    },
    setup({ el, App, props, plugin }) {
      // router
      const Router = createRouter({
        history: createWebHashHistory(),
        routes,
      });

      // pinia
      const Store = createPinia();

      // app
      const app = createApp({ render: () => h(App, props) });
      app.use(plugin);
      app.use(Quasar, {
        plugins: { Dialog, Notify },
      });
      app.use(Router);
      app.use(Store);

      // axios
      api.interceptors.request.use(
        (config) => {
          if (['post', 'put', 'patch', 'delete'].includes(config.method?.toLowerCase() || '')) {
            config.headers['X-CSRFTOKEN'] = props.initialPage.props.django_csrf_token;
          }
          config.headers['Accept-Language'] = props.initialPage.props.django_locale;
          return config;
        },
        (error) => {
          return Promise.reject(error);
        }
      );
      app.config.globalProperties.$axios = axios;
      app.config.globalProperties.$api = api;

      if (!props.initialPage.props.django_debug) {
        // sentry
        Sentry.init({
          app,
          dsn: 'https://ca3e62d60cfb404fb5a64bd13e0e162e@o124046.ingest.sentry.io/291640',
          release: props.initialPage.props.git_commit_hash,
          environment: 'production',
          integrations: [
            new Sentry.BrowserTracing({
              routingInstrumentation: Sentry.vueRouterInstrumentation(Router),
              tracePropagationTargets: ['localhost', 'www.hipeac.net', /^\//],
            }),
          ],
          tracesSampleRate: 0.1,
          // Ignore some errors: https://docs.sentry.io/platforms/javascript/configuration/filtering/
          // - ResizeObserver loop errors
          ignoreErrors: ['ResizeObserver loop'],
        });
      }

      // mount
      app.mount(el);
    },
  });
};

export { bootApp };
