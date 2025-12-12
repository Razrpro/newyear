import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

// https://vite.dev/config/
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: '../public_html',
    emptyOutDir: true
  },
  server: {
    host: '127.0.0.1',
    port: 3000,
    allowedHosts: ['.zrok.io'],
    proxy: {
      '/api': {
        target: 'https://razr.freedynamicdns.org:5001',
        changeOrigin: true,
        rewrite: (path) => path.replace(/^\/api/, '')
      }
    }
  }
})
