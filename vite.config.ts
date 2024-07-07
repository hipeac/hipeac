const fs = require('fs');
const { resolve } = require('path');

import { defineConfig } from 'vite';
import vue from '@vitejs/plugin-vue';

// read apps folder and create a list of entries
const appsToBuild = {};
const apps = fs.readdirSync(resolve(__dirname, './vue/src/apps/'));
apps.forEach((app: string) => {
  appsToBuild[app] = resolve(__dirname, `./vue/src/apps/${app}/main.ts`);
});

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  root: resolve('./vue/src'),
  base: '/static/vite/',
  server: {
    host: 'localhost',
    port: 5173,
    open: false,
    watch: {
      usePolling: true,
      disableGlobbing: false,
    },
  },
  resolve: {
    extensions: ['.vue', '.ts', '.js', '.json'],
    alias: {
      '@': resolve(__dirname, './vue/src'),
    },
  },
  build: {
    outDir: resolve('./vue/dist'),
    assetsDir: '',
    manifest: true,
    emptyOutDir: true,
    target: 'es2015',
    rollupOptions: {
      input: appsToBuild,
      output: {
        chunkFileNames: undefined,
        manualChunks: {
          helpers: ['axios', '@sentry/vue'],
          quasar: ['quasar'],
          vue: ['vue', 'vue-router', 'pinia']
        }
      },
    },
  },
})
