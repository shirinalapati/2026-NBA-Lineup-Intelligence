import { useCallback, useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { fetchJson } from '../api'
import type { Lineup, SortMetric, Team } from '../types'
import { LineupTable } from '../components/LineupTable'

const SORTS: { v: SortMetric; label: string }[] = [
  { v: 'net_rating', label: 'Net' },
  { v: 'offensive_rating', label: 'ORtg' },
  { v: 'defensive_rating', label: 'DRtg' },
  { v: 'minutes', label: 'Minutes' },
  { v: 'possessions', label: 'Poss' },
]

/** Same as ULS eligibility—good default balance of sample size vs coverage. */
const RECOMMENDED_MINUTES_FLOOR = 50

export function Leaderboard() {
  const [params, setParams] = useSearchParams()
  const min = Number(params.get('min') ?? String(RECOMMENDED_MINUTES_FLOOR)) || RECOMMENDED_MINUTES_FLOOR
  const team = params.get('team') ?? ''
  const sort = (params.get('sort') ?? 'net_rating') as SortMetric
  const search = params.get('q') ?? ''

  const [lineups, setLineups] = useState<Lineup[]>([])
  const [teams, setTeams] = useState<Team[]>([])
  const [err, setErr] = useState<string | null>(null)

  const qs = useMemo(() => {
    const p = new URLSearchParams()
    p.set('min_minutes', String(min))
    p.set('sort', sort)
    p.set('limit', '300')
    if (team) p.set('team', team)
    if (search) p.set('search', search)
    return p.toString()
  }, [min, team, sort, search])

  useEffect(() => {
    let c = false
    ;(async () => {
      try {
        const [lu, tm] = await Promise.all([
          fetchJson<Lineup[]>(`/api/lineups?${qs}`),
          fetchJson<Team[]>('/api/teams'),
        ])
        if (!c) {
          setLineups(lu)
          setTeams(tm)
          setErr(null)
        }
      } catch (e) {
        if (!c) setErr(e instanceof Error ? e.message : 'Error')
      }
    })()
    return () => {
      c = true
    }
  }, [qs])

  const setMin = (v: number) => {
    const n = new URLSearchParams(params)
    n.set('min', String(v))
    setParams(n, { replace: true })
  }

  const exportCsv = useCallback(() => {
    const headers = ['team', 'lineup', 'min', 'poss', 'ortg', 'drtg', 'net', 'uls']
    const rows = lineups.map((l) => [
      l.team_abbr,
      [l.player_1_name, l.player_2_name, l.player_3_name, l.player_4_name, l.player_5_name].filter(Boolean).join(' | '),
      l.minutes,
      l.possessions ?? '',
      l.offensive_rating ?? '',
      l.defensive_rating ?? '',
      l.net_rating ?? '',
      l.underrated_lineup_score ?? '',
    ])
    const csv = [headers.join(','), ...rows.map((r) => r.map((x) => `"${String(x).replace(/"/g, '""')}"`).join(','))].join(
      '\n',
    )
    const blob = new Blob([csv], { type: 'text/csv' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = 'lineup-leaderboard.csv'
    a.click()
    URL.revokeObjectURL(a.href)
  }, [lineups])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-3xl text-court-950 dark:text-white">Lineup leaderboard</h1>
        <p className="mt-2 text-slate-600 dark:text-slate-400 max-w-2xl">
          The minutes slider is a <strong className="text-slate-700 dark:text-slate-300">minimum floor</strong>, not a cap:
          any lineup with <strong className="text-slate-700 dark:text-slate-300">at least</strong> that many shared minutes
          can appear—and often shows <em>more</em> than the floor (e.g. floor 120 with 125 minutes played). Use it to hide
          tiny-sample noise. Default floor{' '}
          <strong className="text-slate-700 dark:text-slate-300">50</strong> (aligned with the ULS eligibility floor). Other
          pages use different floors—e.g.
          substitution simulator uses 30; team views may go as low as 0.{' '}
          <strong className="text-slate-700 dark:text-slate-300">ULS</strong> is only computed for lineups with at least{' '}
          <strong className="text-slate-700 dark:text-slate-300">50</strong> minutes together (see About). If ULS still
          shows “—” because the database was enriched under an older threshold, re-run:{' '}
          <code className="font-mono text-xs text-slate-600 dark:text-slate-400">python -m data_pipeline.recompute_uls</code>
          . See{' '}
          <Link to="/#minute-floors" className="text-court-line hover:underline">
            About
          </Link>{' '}
          for the full breakdown.
        </p>
        <p className="text-sm text-slate-500 dark:text-slate-500 max-w-2xl">
          Sort by efficiency or usage. Search matches team abbreviation or player surname.
        </p>
      </div>

      {err && <p className="text-amber-400 text-sm">{err}</p>}

      <div className="flex flex-col lg:flex-row gap-4 lg:items-end flex-wrap">
        <label className="flex flex-col gap-1 text-xs font-mono uppercase text-slate-500 max-w-[13rem]">
          <span>
            Minutes floor (≥){' '}
            <span className="font-sans normal-case font-normal text-[11px] text-slate-500 dark:text-slate-400">
              (recommended {RECOMMENDED_MINUTES_FLOOR})
            </span>
          </span>
          <input
            type="range"
            min={0}
            max={600}
            step={10}
            value={min}
            onChange={(e) => setMin(Number(e.target.value))}
            className="w-full max-w-[12rem] accent-court-accent"
            aria-valuetext={`Show lineups with at least ${min} minutes together`}
          />
          <span className="text-court-accent tabular-nums">
            ≥ {min} <span className="text-[10px] font-sans normal-case text-slate-500">min together</span>
          </span>
        </label>
        <label className="flex flex-col gap-1 text-xs font-mono uppercase text-slate-500">
          Team
          <select
            value={team}
            onChange={(e) => {
              const n = new URLSearchParams(params)
              if (e.target.value) n.set('team', e.target.value)
              else n.delete('team')
              setParams(n, { replace: true })
            }}
            className="bg-white dark:bg-court-900 border border-slate-200 dark:border-court-700 rounded-lg px-3 py-2 text-sm"
          >
            <option value="">All</option>
            {teams.map((t) => (
              <option key={t.team_abbr} value={t.team_abbr}>
                {t.team_abbr}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-xs font-mono uppercase text-slate-500">
          Sort
          <select
            value={sort}
            onChange={(e) => {
              const n = new URLSearchParams(params)
              n.set('sort', e.target.value)
              setParams(n, { replace: true })
            }}
            className="bg-white dark:bg-court-900 border border-slate-200 dark:border-court-700 rounded-lg px-3 py-2 text-sm"
          >
            {SORTS.map((s) => (
              <option key={s.v} value={s.v}>
                {s.label}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-xs font-mono uppercase text-slate-500 flex-1 min-w-[200px]">
          Search
          <input
            value={search}
            onChange={(e) => {
              const n = new URLSearchParams(params)
              if (e.target.value) n.set('q', e.target.value)
              else n.delete('q')
              setParams(n, { replace: true })
            }}
            className="bg-white dark:bg-court-900 border border-slate-200 dark:border-court-700 rounded-lg px-3 py-2 text-sm"
          />
        </label>
        <button
          type="button"
          onClick={exportCsv}
          className="px-4 py-2 rounded-lg border border-court-700 text-sm font-medium hover:bg-court-800"
        >
          Export CSV
        </button>
      </div>

      <LineupTable lineups={lineups} showUls />
    </div>
  )
}
