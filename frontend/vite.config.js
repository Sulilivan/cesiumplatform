import { fileURLToPath, URL } from 'node:url'

import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import vueDevTools from 'vite-plugin-vue-devtools'

// https://vite.dev/config/
export default defineConfig({
  plugins: [
    vue(),
    vueDevTools(),
  ],
  resolve: {
    alias: {
      '@': fileURLToPath(new URL('./src', import.meta.url))
    },
  },
  // Docker 开发环境配置
  server: {
    host: '0.0.0.0',  // 允许外部访问（Docker 容器需要）
    port: 5173,
    watch: {
      usePolling: true,  // Docker 中需要轮询监听文件变化
    },
  },
})
