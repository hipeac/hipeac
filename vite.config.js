const { resolve } = require('path');

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// https://vitejs.dev/config/
export default defineConfig({
  plugins: [vue()],
  root: resolve('./vue/src'),
  base: '/static/vite/',
  server: {
    host: 'localhost',
    port: 3000,
    open: false,
    watch: {
      usePolling: true,
      disableGlobbing: false,
    },
  },
  resolve: {
    extensions: ['.vue', '.js', '.json'],
    alias:{
      '@' : resolve(__dirname, './vue/src')
    },
  },
  build: {
    outDir: resolve('./vue/dist'),
    assetsDir: '',
    manifest: true,
    emptyOutDir: true,
    target: 'es2015',
    rollupOptions: {
      input: {
        home: resolve('./vue/src/apps/home/main.ts'),
      },
      output: {
        chunkFileNames: undefined,
        manualChunks: {
          helpers: ['axios', 'date-fns', 'lodash-es', '@sentry/vue'],
          quasar: ['quasar'],
          vue: ['vue', 'vue-router', 'pinia']
        }
      },
    },
  },
  define: {
    __VUE_I18N_FULL_INSTALL__: true,
    __VUE_I18N_LEGACY_API__: false,
    __INTLIFY_PROD_DEVTOOLS__: false,
  },
})
