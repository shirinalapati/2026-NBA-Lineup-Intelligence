const BASE = import.meta.env.VITE_API_BASE ?? ''

export async function fetchJson<T>(path: string): Promise<T> {
  const res = await fetch(`${BASE}${path}`)
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
