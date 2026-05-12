import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchJson, API_BASE } from '../api'
import type { Lineup, SeasonScope, Team } from '../types'
import { StatCard } from '../components/StatCard'
import { TopNetBar, MinutesNetScatter } from '../components/Charts'
import { LineupTable } from '../components/LineupTable'

export function Home() {
  const [teams, setTeams] = useState<Team[]>([])
  const [top, setTop] = useState<Lineup[]>([])
  const [scatter, setScatter] = useState<Lineup[]>([])
  const [err, setErr] = useState<string | null>(null)
  const [scope, setScope] = useState<SeasonScope | null>(null)

  useEffect(() => {
    let cancelled = false
    ;(async () => {
      try {
        const [t, tp, sc] = await Promise.all([
          fetchJson<Team[]>('/api/teams'),
          fetchJson<Lineup[]>('/api/lineups/top?limit=10&min_minutes=100'),
          fetchJson<Lineup[]>('/api/lineups?min_minutes=0&sort=minutes&fetch_all=true'),
        ])
        if (!cancelled) {
          setTeams(t)
          setTop(tp)
          setScatter(sc)
          setErr(null)
        }
        // Optional: older backends may not have /api/scope — do not fail the whole page
        try {
          const scp = await fetchJson<SeasonScope>('/api/scope')
          if (!cancelled) setScope(scp)
        } catch {
          if (!cancelled) setScope(null)
        }
      } catch (e) {
        if (!cancelled) setErr(e instanceof Error ? e.message : 'Load failed')
      }
    })()
    return () => {
      cancelled = true
    }
  }, [])

  const avgNet =
    top.length > 0 ? (top.reduce((s, l) => s + (l.net_rating ?? 0), 0) / top.length).toFixed(1) : '—'

  return (
    <div className="space-y-10">
      <section className="max-w-3xl">
        <p className="text-court-line font-mono text-xs uppercase tracking-[0.2em] mb-3">Portfolio analytics product</p>
        <h1 className="font-display text-4xl sm:text-5xl text-court-950 dark:text-white leading-tight">
          2025-26 NBA Lineup Intelligence
        </h1>
        <p className="mt-4 text-slate-600 dark:text-slate-400 text-lg leading-relaxed">
          Evaluate five-man units across the <strong className="text-slate-800 dark:text-slate-200">2025-26 NBA regular
          season only</strong> (no playoffs or play-in). Discover the best lineups, surface under-used high-performers
          with ULS, and prototype substitution decisions with a transparent projection model.
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <Link
            to="/leaderboard"
            className="inline-flex items-center justify-center px-5 py-2.5 rounded-lg bg-court-accent text-court-950 font-semibold text-sm hover:opacity-90"
          >
            Open leaderboard
          </Link>
          <Link
            to="/simulator"
            className="inline-flex items-center justify-center px-5 py-2.5 rounded-lg border border-court-700 text-slate-200 font-medium text-sm hover:bg-court-800"
          >
            Substitution simulator
          </Link>
          <Link
            to="/underrated"
            className="inline-flex items-center justify-center px-5 py-2.5 rounded-lg border border-court-line/40 text-court-line font-medium text-sm hover:bg-court-line/10"
          >
            Underrated lineups
          </Link>
        </div>
        <p className="mt-5 text-sm text-slate-500 dark:text-slate-500 max-w-2xl">
          <Link to="/" className="text-court-accent font-medium hover:underline">
            Project introduction
          </Link>
          —problem framing, methodology, limitations, and roadmap (same as the app home).
        </p>
      </section>

      {err && (
        <div className="rounded-lg border border-amber-500/40 bg-amber-500/10 px-4 py-3 text-amber-200 text-sm space-y-2">
          <p>
            <strong className="text-amber-100">API unavailable:</strong> {err}
          </p>
          {import.meta.env.PROD && import.meta.env.VERCEL ? (
            <p className="text-amber-200/90 text-xs leading-relaxed">
              On Vercel, <code className="font-mono text-amber-100/90">/api</code> is proxied server-side to Render. In{' '}
              <strong className="text-amber-50">Vercel → Settings → Environment Variables</strong>, add{' '}
              <code className="font-mono text-amber-100/90">API_UPSTREAM</code> = your Render API origin (e.g.{' '}
              <code className="font-mono text-amber-100/90">https://two026-nba-lineup-intelligence.onrender.com</code>
              ), no trailing slash. Enable for <strong className="text-amber-50">Production</strong> (and Preview if you
              use it), then <strong className="text-amber-50">Redeploy</strong>. You do <em>not</em> need{' '}
              <code className="font-mono text-amber-100/90">VITE_API_BASE</code> for this setup (browser stays
              same-origin).
            </p>
          ) : import.meta.env.PROD && !API_BASE ? (
            <p className="text-amber-200/90 text-xs leading-relaxed">
              Production build has no API origin. In{' '}
              <strong className="text-amber-50">Vercel → Project → Settings → Environment Variables</strong>, add{' '}
              <code className="font-mono text-amber-100/90">VITE_API_BASE</code> = your Render URL (e.g.{' '}
              <code className="font-mono text-amber-100/90">https://two026-nba-lineup-intelligence.onrender.com</code>
              ), no trailing slash. Apply to <strong className="text-amber-50">Production</strong>, then trigger a new
              <strong className="text-amber-50"> Deploy</strong> so Vite bakes the value in.
            </p>
          ) : import.meta.env.PROD && API_BASE ? (
            <p className="text-amber-200/90 text-xs leading-relaxed">
              Requests go to <code className="font-mono text-amber-100/90">{API_BASE}</code>. If this persists: on
              Render set <code className="font-mono text-amber-100/90">CORS_ORIGINS</code> to this site’s origin (e.g.{' '}
              <code className="font-mono text-amber-100/90">https://2026-nba-lineup-intelligence.vercel.app</code>
              ). Free Render instances sleep—first load after idle can take a minute; retry once.
            </p>
          ) : (
            <>
              <p>
                The UI is up, but requests to <code className="text-amber-100/90 font-mono text-xs">/api</code> are
                proxied to <code className="text-amber-100/90 font-mono text-xs">127.0.0.1:8000</code>—start the backend
                there.
              </p>
              <p className="text-amber-200/90 text-xs leading-relaxed">
                From the repo root (with venv active):{' '}
                <code className="font-mono text-amber-100/90">uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000</code>
                . If the app errors on load, populate SQLite first:{' '}
                <code className="font-mono text-amber-100/90">python -m data_pipeline.ingest_all</code> (or{' '}
                <code className="font-mono text-amber-100/90">python -m data_pipeline.ingest_all --seed</code> for offline
                demo data only).
              </p>
            </>
          )}
        </div>
      )}

      {!err && scope && scope.data_source !== 'nba_stats_api' && (
        <div className="rounded-lg border border-rose-500/35 bg-rose-950/30 px-4 py-3 text-rose-100 text-sm space-y-1">
          <p>
            <strong className="text-rose-50">Not on live NBA data.</strong> Ingest source is{' '}
            <code className="font-mono text-xs text-rose-100/90">{scope.data_source}</code>
            {scope.roster_mode ? (
              <>
                {' '}
                (<code className="font-mono text-xs">{scope.roster_mode}</code>)
              </>
            ) : null}
            . Lineups and ratings are not real league observations—do not deploy this snapshot as production truth.
          </p>
          <p className="text-rose-100/85 text-xs leading-relaxed">
            For real data: from the repo root run{' '}
            <code className="font-mono text-rose-50/90">python -m data_pipeline.ingest_all</code>, restart the API, and
            confirm this page’s season card shows ingest <code className="font-mono text-rose-50/90">nba_stats_api</code>.
            See README “Deploying with real NBA data”.
          </p>
        </div>
      )}

      <section className="grid grid-cols-1 sm:grid-cols-3 gap-4">
        <StatCard label="Teams in scope" value={String(teams.length || '—')} hint="Regular season only" />
        <StatCard label="Top-10 avg net (sample)" value={avgNet} hint="Qualified lineups" />
        <StatCard
          label="Season scope"
          value={scope ? `${scope.season} · ${scope.season_type}` : '2025-26 · Regular Season'}
          hint={
            scope
              ? `Ingest: ${scope.data_source}${scope.roster_mode ? ` · ${scope.roster_mode}` : ''}`
              : 'No playoffs / play-in'
          }
        />
      </section>

      <section className="grid lg:grid-cols-2 gap-8">
        <div className="rounded-2xl border border-slate-200 dark:border-court-700 bg-white dark:bg-court-850 p-6 shadow-card">
          <h2 className="font-display text-xl text-court-950 dark:text-white mb-4">Top 10 lineups by net rating</h2>
          {top.length > 0 ? <TopNetBar lineups={top} /> : <p className="text-slate-500 text-sm">No data</p>}
        </div>
        <div className="rounded-2xl border border-slate-200 dark:border-court-700 bg-white dark:bg-court-850 p-6 shadow-card">
          <h2 className="font-display text-xl text-court-950 dark:text-white mb-2">Minutes vs net rating</h2>
          <p className="text-xs text-slate-500 dark:text-slate-500 mb-4 max-w-lg leading-relaxed">
            Every five-man lineup row in the database for this ingest (no minute floor; no row cap). Dense cloud on the
            left is normal—most combinations log limited time.
          </p>
          {scatter.length > 0 ? <MinutesNetScatter lineups={scatter} /> : <p className="text-slate-500 text-sm">No data</p>}
        </div>
      </section>

      <section>
        <div className="flex items-center justify-between gap-4 mb-4">
          <h2 className="font-display text-xl text-court-950 dark:text-white">Featured lineups</h2>
          <Link to="/leaderboard" className="text-sm font-medium text-court-accent hover:underline">
            Full table
          </Link>
        </div>
        {top.length > 0 ? <LineupTable lineups={top} showUls /> : null}
      </section>
    </div>
  )
}
