import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchJson } from '../api'
import type { Lineup, Team } from '../types'
import { LineupTable } from '../components/LineupTable'

export function Underrated() {
  const [lineups, setLineups] = useState<Lineup[]>([])
  const [teams, setTeams] = useState<Team[]>([])
  const [team, setTeam] = useState('')
  const [min, setMin] = useState(50)
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
    let cancelled = false
    ;(async () => {
      try {
        const q = new URLSearchParams({ min_minutes: String(min), limit: '150', sort: 'underrated_lineup_score' })
        if (team) q.set('team', team)
        const lu = await fetchJson<Lineup[]>(`/api/lineups/underrated?${q.toString()}`)
        if (!cancelled) {
          setLineups(lu)
          setErr(null)
        }
      } catch (e) {
        if (!cancelled) setErr(e instanceof Error ? e.message : 'Error')
      }
    })()
    return () => {
      cancelled = true
    }
  }, [team, min])

  return (
    <div className="space-y-6">
      <div>
        <h1 className="font-display text-3xl text-court-950 dark:text-white">Underrated lineup score</h1>
        <p className="mt-2 text-slate-600 dark:text-slate-400 max-w-3xl">
          ULS blends normalized net, offense, inverted defense, a limited-minutes bonus (above a floor), and
          possessions. It highlights lineups that were efficient but not always leaned on—useful for rotation and
          roster planning conversations. Scores are only defined for lineups with{' '}
          <strong className="text-slate-700 dark:text-slate-300">≥ 50 minutes</strong> together; this page keeps the
          list floor at that same minimum so every row shows a ULS.{' '}
          <Link to="/#uls-formula" className="text-court-accent font-medium hover:underline">
            Full formula
          </Link>
          .
        </p>
      </div>

      <div className="flex flex-wrap gap-4 items-end">
        <label className="flex flex-col gap-1 text-xs font-mono uppercase text-slate-500 max-w-[13rem]">
          <span>Minutes floor (≥)</span>
          <input
            type="range"
            min={50}
            max={400}
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
            onChange={(e) => setTeam(e.target.value)}
            className="bg-white dark:bg-court-900 border border-slate-200 dark:border-court-700 rounded-lg px-3 py-2 text-sm"
          >
            <option value="">All teams</option>
            {teams.map((t) => (
              <option key={t.team_abbr} value={t.team_abbr}>
                {t.team_abbr}
              </option>
            ))}
          </select>
        </label>
      </div>

      {err && <p className="text-amber-400 text-sm">{err}</p>}

      <div className="rounded-lg border border-court-700 bg-court-900/50 px-4 py-3 text-sm text-slate-400">
        <strong className="text-court-line">Reading ULS:</strong> higher means stronger blend of efficiency signals with
        relatively lower minutes inside the qualified pool—not a raw “best lineup” ranking.
      </div>

      <LineupTable lineups={lineups} showUls />
    </div>
  )
}
