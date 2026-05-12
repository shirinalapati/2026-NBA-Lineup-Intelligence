/**
 * - Local dev: `''` (Vite proxies `/api` to uvicorn).
 * - Production: `__API_ORIGIN__` from `vite build` — set **API_UPSTREAM** or **VITE_API_BASE** on the host (e.g. Vercel) so `process.env` is populated at build time (no trailing slash). Render must allow this site in **CORS_ORIGINS** or set **CORS_ALLOW_VERCEL=1**.
 */
function resolveApiBase(): string {
  if (import.meta.env.DEV) return ''
  if (__API_ORIGIN__) return __API_ORIGIN__
  return (import.meta.env.VITE_API_BASE ?? '').replace(/\/$/, '')
}

export const API_BASE = resolveApiBase()

export async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${API_BASE}${path}`)
  if (!res.ok) {
    const raw = await res.text()
    let msg = raw || res.statusText
    try {
      const j = JSON.parse(raw) as { detail?: unknown }
      if (j?.detail != null) {
        msg = typeof j.detail === 'string' ? j.detail : JSON.stringify(j.detail)
      }
    } catch {
      /* use raw */
    }
    if (res.status === 404) {
      msg = `${msg} (${path})`
    }
    throw new Error(msg)
  }
  return res.json() as Promise<T>
}
