import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

// https://vite.dev/config/
export default defineConfig({
  base: '/',
  plugins: [react(), tailwindcss()],
  define: {
    global: 'globalThis',
    'process.env': {},
  },
  build: {
    commonjsOptions: {
      transformMixedEsModules: true,
    },
    rollupOptions: {
      output: {
        manualChunks: {
          timeline: ['timelinejs-react'],
        },
      },
    },
  },
  optimizeDeps: {
    include: ['timelinejs-react'],
    esbuildOptions: {
      define: {
        global: 'globalThis',
      },
    },
  },
  server: {
    host: true, // cho phép truy cập từ ngoài (Docker, LAN,...)
    allowedHosts: ['seadev-1.ript.vn'], // thêm domain của bạn vào đây
  },
})
