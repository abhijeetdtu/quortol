import path from 'node:path'
import { fileURLToPath } from 'node:url'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)
const proxy = {
  '/api': {
    target: 'http://127.0.0.1:5000',
    changeOrigin: true
  },
  '/data-storytelling-app': {
    target: 'http://127.0.0.1:5000',
    changeOrigin: true
  },
  '/static': {
    target: 'http://127.0.0.1:5000',
    changeOrigin: true
  }
}

export default defineConfig({
  plugins: [vue()],
  server: {
    port: 8050,
    allowedHosts: ['quortol.pokhi.in', 'pokhi.in', 'localhost', '127.0.0.1'],
    proxy
  },
  resolve: {
    alias: {
      '@': path.resolve(__dirname, './src')
    }
  }
})
