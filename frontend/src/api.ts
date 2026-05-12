/**
 * - Local dev: `''` (Vite proxies `/api` to uvicorn).
 * - Vercel: `''` — same-origin `/api` is handled by `api/[...path].ts` → set **API_UPSTREAM** on Vercel (server env).
 * - Elsewhere: set **VITE_API_BASE** at build time to your API origin (no trailing slash).
 */
function resolveApiBase(): string {
  if (import.meta.env.DEV) return ''
  if (import.meta.env.VERCEL) return ''
  return import.meta.env.VITE_API_BASE ?? ''
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
