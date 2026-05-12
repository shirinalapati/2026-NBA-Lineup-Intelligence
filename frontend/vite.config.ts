import { defineConfig } from 'vite'
import react from '@vitejs/plugin-react'

/** Baked into the client bundle on `vite build` (Vercel injects env here). No trailing slash. */
function productionApiOrigin(): string {
  const raw = process.env.API_UPSTREAM || process.env.VITE_API_BASE || ''
  return raw.replace(/\/$/, '')
}

// https://vite.dev/config/
export default defineConfig({
  // Plain Vite on Vercel does not run `api/*.ts` serverless routes (unlike Next/Nitro)—use cross-origin API + CORS.
  define: {
    __API_ORIGIN__: JSON.stringify(process.env.NODE_ENV === 'production' ? productionApiOrigin() : ''),
  },
  plugins: [react()],
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://127.0.0.1:8000',
        changeOrigin: true,
      },
    },
  },
})
