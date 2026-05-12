import path from 'node:path'
import { fileURLToPath } from 'node:url'

import { defineConfig, loadEnv } from 'vite'
import react from '@vitejs/plugin-react'

const __dirname = path.dirname(fileURLToPath(import.meta.url))

/** Baked into the client bundle on `vite build` (Vercel injects env at build time). No trailing slash. */
function resolveApiUpstream(mode: string): string {
  const fromFiles = loadEnv(mode, __dirname, '')
  const raw =
    fromFiles.API_UPSTREAM ||
    fromFiles.VITE_API_BASE ||
    process.env.API_UPSTREAM ||
    process.env.VITE_API_BASE ||
    ''
  return String(raw).trim().replace(/\/$/, '')
}

// https://vite.dev/config/
export default defineConfig(({ mode }) => {
  const apiOrigin = mode === 'production' ? resolveApiUpstream(mode) : ''
  if (mode === 'production' && !apiOrigin) {
    console.warn(
      '\n[vite] Production build has no API_UPSTREAM or VITE_API_BASE. ' +
        'Add one in Vercel → Settings → Environment Variables (enable Production), then Redeploy.\n'
    )
  }

  return {
    // Plain Vite on Vercel does not run `api/*.ts` serverless routes (unlike Next/Nitro)—use cross-origin API + CORS.
    define: {
      __API_ORIGIN__: JSON.stringify(apiOrigin),
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
  }
})
