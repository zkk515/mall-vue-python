import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

// 环境变量：API地址
// 本地Mac: http://localhost:8000
// Docker内: http://mall-backend:8000
const apiUrl = process.env.VITE_API_URL || 'http://localhost:8000'

export default defineConfig({
  plugins: [vue()],
  server: {
    host: '0.0.0.0',
    port: 8080,
    proxy: {
      '/api': {
        target: apiUrl,
        changeOrigin: true
      }
    }
  }
})
