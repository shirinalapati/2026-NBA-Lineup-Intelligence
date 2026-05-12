import { useEffect, useMemo, useState } from 'react'
import { Link, useSearchParams } from 'react-router-dom'
import { fetchJson } from '../api'
import type { Lineup, Team } from '../types'
import { StatCard } from '../components/StatCard'
import { LineupTable } from '../components/LineupTable'
import { OffDefScatter } from '../components/Charts'
import { fmt2, leagueTeamRank, rankSlashTotal } from '../lib/format'

export function TeamExplorer() {
  const [params, setParams] = useSearchParams()
  const team = params.get('team') ?? 'BOS'
  const [teams, setTeams] = useState<Team[]>([])
  const [best, setBest] = useState<Lineup[]>([])
  const [heavy, setHeavy] = useState<Lineup[]>([])
  const [under, setUnder] = useState<Lineup[]>([])
  const [all, setAll] = useState<Lineup[]>([])
  const [err, setErr] = useState<string | null>(null)

  useEffect(() => {
    let c = false
    ;(async () => {
      try {
        const tm = await fetchJson<Team[]>('/api/teams')
        if (!c) setTeams(tm)
      } catch (e) {
        if (!c) setErr(e instanceof Error ? e.message : 'Error')
      }
    })()
    return () => {
      c = true
    }
  }, [])

  useEffect(() => {
    let c = false
    ;(async () => {
      try {
        const [b, h, u, tlist] = await Promise.all([
          fetchJson<Lineup[]>(`/api/lineups/team/${team}?min_minutes=50&sort=net_rating&limit=5`),
          fetchJson<Lineup[]>(`/api/lineups/team/${team}?min_minutes=0&sort=minutes&limit=5`),
          fetchJson<Lineup[]>(`/api/lineups/underrated?team=${team}&limit=5&min_minutes=50`),
          fetchJson<Lineup[]>(`/api/lineups/team/${team}?min_minutes=40&sort=net_rating&limit=80`),
        ])
        if (!c) {
          setBest(b)
          setHeavy(h)
          setUnder(u)
          setAll(tlist)
          setErr(null)
        }
      } catch (e) {
        if (!c) setErr(e instanceof Error ? e.message : 'Error')
      }
    })()
    return () => {
      c = true
    }
  }, [team])

  const info = useMemo(() => teams.find((x) => x.team_abbr === team) ?? null, [teams, team])

  const ranks = useMemo(() => {
    if (!info || teams.length === 0) return null
    return {
      ortg: rankSlashTotal(leagueTeamRank(teams, team, (t) => t.offensive_rating, true)),
      drtg: rankSlashTotal(leagueTeamRank(teams, team, (t) => t.defensive_rating, false)),
      net: rankSlashTotal(leagueTeamRank(teams, team, (t) => t.net_rating, true)),
      pace: rankSlashTotal(leagueTeamRank(teams, team, (t) => t.pace, true)),
    }
  }, [teams, team, info])

  return (
    <div className="space-y-10">
      <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-4">
        <div>
          <h1 className="font-display text-3xl text-court-950 dark:text-white">Team lineup explorer</h1>
          <p className="mt-2 text-slate-600 dark:text-slate-400">
            Compare best-performing, heaviest-minute, and underrated five-man groups in context of team efficiency.
          </p>
        </div>
        <label className="flex flex-col gap-1 text-xs font-mono uppercase text-slate-500">
          Team
          <select
            value={team}
            onChange={(e) => {
              const n = new URLSearchParams(params)
              n.set('team', e.target.value)
              setParams(n, { replace: true })
            }}
            className="bg-white dark:bg-court-900 border border-slate-200 dark:border-court-700 rounded-lg px-4 py-2 text-sm min-w-[200px]"
          >
            {teams.map((t) => (
              <option key={t.team_abbr} value={t.team_abbr}>
                {t.team_abbr} — {t.team_name}
              </option>
            ))}
          </select>
        </label>
      </div>

      {err && <p className="text-amber-400 text-sm">{err}</p>}

      {info && (
        <>
          <section className="grid sm:grid-cols-4 gap-4">
          <StatCard
            label="Team ORtg"
            value={info.offensive_rating != null ? fmt2(info.offensive_rating) : '—'}
            rank={info.offensive_rating != null ? ranks?.ortg : null}
          />
          <StatCard
            label="Team DRtg"
            value={info.defensive_rating != null ? fmt2(info.defensive_rating) : '—'}
            rank={info.defensive_rating != null ? ranks?.drtg : null}
          />
          <StatCard
            label="Team net"
            value={info.net_rating != null ? fmt2(info.net_rating) : '—'}
            rank={info.net_rating != null ? ranks?.net : null}
          />
          <StatCard
            label="Pace"
            value={info.pace != null ? fmt2(info.pace) : '—'}
            rank={info.pace != null ? ranks?.pace : null}
            hint={
              <>
                Possessions per 48 min (tempo).{' '}
                <Link to="/#pace-and-tempo" className="text-court-accent hover:underline">
                  Definition
                </Link>
              </>
            }
          />
        </section>
        <p className="text-xs text-slate-500 dark:text-slate-500 -mt-2">
          League rank among teams in scope (typically 30). Higher is better for ORtg, net, and pace;{' '}
          <strong className="text-slate-600 dark:text-slate-400">lower DRtg is better defense</strong> (1st = stingiest
          allowed).
        </p>
        </>
      )}

      <section className="grid md:grid-cols-3 gap-6">
        <div>
          <h2 className="font-display text-lg text-court-950 dark:text-white">Best net (qualified)</h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 mb-2 leading-relaxed">
            <strong className="text-slate-600 dark:text-slate-300">Order:</strong> net rating (highest first), then minutes
            if tied. <strong className="text-slate-600 dark:text-slate-300">Min ≥ 50</strong> for this list.{' '}
            <strong className="text-slate-600 dark:text-slate-300">Ratings:</strong> ORtg / DRtg / Net = points per 100
            possessions (offense / defense allowed / difference).{' '}
            <strong className="text-slate-600 dark:text-slate-300">Pace</strong> (team strip above) is tempo:{' '}
            <Link to="/#pace-and-tempo" className="text-court-accent hover:underline">
              possessions per 48 minutes
            </Link>
            , not per-100. Scroll horizontally if columns are clipped.
          </p>
          <LineupTable lineups={best} showRank wide />
        </div>
        <div>
          <h2 className="font-display text-lg text-court-950 dark:text-white">Most minutes</h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 mb-2">
            <strong className="text-slate-600 dark:text-slate-300">Order:</strong> total minutes together (highest
            first). Same rating columns as above.
          </p>
          <LineupTable lineups={heavy} showRank wide />
        </div>
        <div>
          <h2 className="font-display text-lg text-court-950 dark:text-white">Most underrated (ULS)</h2>
          <p className="text-xs text-slate-500 dark:text-slate-400 mt-1 mb-2">
            <strong className="text-slate-600 dark:text-slate-300">Order:</strong> Underrated Lineup Score (higher =
            stronger efficiency + usage story). <strong className="text-slate-600 dark:text-slate-300">Min ≥ 50</strong>{' '}
            (same floor as ULS computation—every lineup here has a score).
          </p>
          <LineupTable lineups={under} showUls showRank wide />
        </div>
      </section>

      <section className="rounded-2xl border border-slate-200 dark:border-court-700 bg-white dark:bg-court-850 p-6">
        <h2 className="font-display text-xl text-court-950 dark:text-white mb-4">
          Team lineups: offensive vs defensive rating
        </h2>
        {all.length > 0 ? <OffDefScatter lineups={all} /> : <p className="text-slate-500">No data</p>}
      </section>
    </div>
  )
}
