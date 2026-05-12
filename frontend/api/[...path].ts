/**
 * Vercel serverless proxy: browser calls same-origin `/api/...`, this forwards to Render (no CORS).
 * Set **API_UPSTREAM** on Vercel: `https://your-service.onrender.com` (no trailing slash). Apply to Production + Preview.
 */
import type { VercelRequest, VercelResponse } from '@vercel/node'

function stripHopByHop(h: VercelRequest['headers']): Record<string, string> {
  const skip = new Set([
    'connection',
    'keep-alive',
    'proxy-authenticate',
    'proxy-authorization',
    'te',
    'trailers',
    'transfer-encoding',
    'upgrade',
    'host',
  ])
  const out: Record<string, string> = {}
  for (const [k, v] of Object.entries(h)) {
    if (v == null || skip.has(k.toLowerCase())) continue
    out[k] = Array.isArray(v) ? v.join(',') : v
  }
  return out
}

export default async function handler(req: VercelRequest, res: VercelResponse) {
  const upstream = process.env.API_UPSTREAM?.replace(/\/$/, '')
  if (!upstream) {
    res.status(502).json({
      detail:
        'Vercel: set API_UPSTREAM to your Render API origin (e.g. https://….onrender.com), no trailing slash, then redeploy.',
    })
    return
  }

  const raw = req.url || '/'
  let pathname: string
  let search: string
  try {
    const u = new URL(raw, 'https://vercel.local')
    pathname = u.pathname
    search = u.search
  } catch {
    res.status(400).send('Bad URL')
    return
  }

  if (!pathname.startsWith('/api')) {
    res.status(404).send('Not found')
    return
  }

  const target = `${upstream}${pathname}${search}`
  const method = (req.method || 'GET').toUpperCase()

  let body: string | Buffer | undefined
  if (method !== 'GET' && method !== 'HEAD') {
    if (typeof req.body === 'string' || Buffer.isBuffer(req.body)) {
      body = req.body
    } else if (req.body != null) {
      body = JSON.stringify(req.body)
    }
  }

  const headers = new Headers()
  const fwd = stripHopByHop(req.headers)
  for (const [k, v] of Object.entries(fwd)) {
    if (k.toLowerCase() === 'content-length') continue
    headers.set(k, v)
  }
  if (body != null && typeof body === 'string' && !headers.has('content-type')) {
    headers.set('content-type', 'application/json')
  }

  let r: Response
  try {
    r = await fetch(target, { method, headers, body: body as BodyInit | undefined })
  } catch (e) {
    res.status(502).json({
      detail: `Upstream fetch failed: ${e instanceof Error ? e.message : String(e)}`,
    })
    return
  }

  res.status(r.status)
  r.headers.forEach((value, key) => {
    const lk = key.toLowerCase()
    if (lk === 'content-encoding' || lk === 'transfer-encoding') return
    res.setHeader(key, value)
  })
  const buf = Buffer.from(await r.arrayBuffer())
  res.send(buf)
}
