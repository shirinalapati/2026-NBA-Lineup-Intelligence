import { useEffect, useMemo, useState } from 'react'
import { Link } from 'react-router-dom'
import { fetchJson, API_BASE } from '../api'
import type { Lineup, Player, SimulateResult, Team } from '../types'
import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
  Legend,
} from 'recharts'
import { fmt1, fmt2, lineupNames, lineupPlayerNameById } from '../lib/format'

function samePlayerId(a: number, b: number): boolean {
  return Number(a) === Number(b)
}

/** Lineup choices for this page: API `min_minutes` + `limit` (see About → minute floors). */
const SIM_LINEUP_MIN_MINUTES = 30
const SIM_LINEUP_FETCH_LIMIT = 100

export function Simulator() {
  const [teams, setTeams] = useState<Team[]>([])
  const [team, setTeam] = useState('BOS')
  const [lineups, setLineups] = useState<Lineup[]>([])
  const [players, setPlayers] = useState<Player[]>([])
  const [lineupId, setLineupId] = useState('')
  const [outId, setOutId] = useState<number | ''>('')
  const [inId, setInId] = useState<number | ''>('')
  const [result, setResult] = useState<SimulateResult | null>(null)
  const [err, setErr] = useState<string | null>(null)

  useEffect(() => {
    fetchJson<Team[]>('/api/teams')
      .then(setTeams)
      .catch((e) => setErr(String(e)))
  }, [])

  useEffect(() => {
    let c = false
    ;(async () => {
      try {
        const [lu, pl] = await Promise.all([
          fetchJson<Lineup[]>(
            `/api/lineups/team/${team}?min_minutes=${SIM_LINEUP_MIN_MINUTES}&limit=${SIM_LINEUP_FETCH_LIMIT}&sort=minutes`,
          ),
          fetchJson<Player[]>(`/api/players?team=${team}`),
        ])
        if (!c) {
          setLineups(lu)
          setPlayers(pl)
          if (lu.length) {
            setLineupId(lu[0].lineup_id)
          }
          setResult(null)
          setOutId('')
          setInId('')
        }
      } catch (e) {
        if (!c) setErr(e instanceof Error ? e.message : 'Error')
      }
    })()
    return () => {
      c = true
    }
  }, [team])

  const selected = useMemo(() => lineups.find((l) => l.lineup_id === lineupId), [lineups, lineupId])

  const lineupPlayerIds = useMemo(() => {
    if (!selected) return []
    return [
      selected.player_1_id,
      selected.player_2_id,
      selected.player_3_id,
      selected.player_4_id,
      selected.player_5_id,
    ].filter((x): x is number => x != null && x > 0)
  }, [selected])

  const replacementPool = useMemo(
    () => players.filter((p) => !lineupPlayerIds.some((lid) => samePlayerId(lid, p.player_id))),
    [players, lineupPlayerIds],
  )

  async function runSim() {
    if (!lineupId || outId === '' || inId === '') {
      setErr('Select lineup, player out, and replacement.')
      return
    }
    setErr(null)
    try {
      const res = await fetch(`${API_BASE}/api/simulate-substitution`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          team_abbr: team,
          lineup_id: lineupId,
          player_out_id: outId,
          player_in_id: inId,
        }),
      })
      if (!res.ok) throw new Error(await res.text())
      const data = (await res.json()) as SimulateResult
      setResult(data)
    } catch (e) {
      setErr(e instanceof Error ? e.message : 'Simulation failed')
    }
  }

  const chartData =
    result &&
    [
      { name: 'Offense', before: result.baseline_offensive_rating, after: result.projected_offensive_rating },
      { name: 'Defense', before: result.baseline_defensive_rating, after: result.projected_defensive_rating },
      { name: 'Net', before: result.baseline_net_rating, after: result.projected_net_rating },
    ]

  return (
    <div className="space-y-8 max-w-4xl">
      <div>
        <h1 className="font-display text-3xl text-court-950 dark:text-white">Substitution simulator</h1>
        <p className="mt-2 text-slate-600 dark:text-slate-400">
          Prototype decision support: start from an observed lineup’s efficiency, then adjust using player-level OBPM
          (Offensive Box Plus/Minus), DBPM (Defensive Box Plus/Minus), TS% (True Shooting Percentage), AST% (Assist
          Percentage), TOV% (Turnover Percentage), STL% (Steal Percentage), and BLK% (Block Percentage) deltas (formulas
          on the{' '}
          <Link to="/#substitution-simulator" className="text-court-accent hover:underline">
            About
          </Link>{' '}
          page). Not a calibrated forecast. Lineup list: this team’s five-man units with{' '}
          <strong className="text-slate-700 dark:text-slate-300">≥ {SIM_LINEUP_MIN_MINUTES} minutes</strong> together, up
          to <strong className="text-slate-700 dark:text-slate-300">{SIM_LINEUP_FETCH_LIMIT}</strong> rows, sorted by
          minutes (heaviest-used first).
        </p>
        <aside
          className="mt-4 rounded-lg border border-slate-200 dark:border-court-700 bg-slate-50/90 dark:bg-court-950/50 px-4 py-3 text-sm text-slate-700 dark:text-slate-300"
          aria-label="How to read lineup efficiency in this tool"
        >
          <strong className="text-slate-900 dark:text-slate-100">Lineup numbers are not a “who’s better” ranking.</strong>{' '}
          Net, ORtg, and DRtg here describe the <em>entire five-man unit</em> while those five shared the floor—who they
          played with and against, role, and small-sample noise all matter. A bench or specialist grouping can out-net a
          star-heavy lineup in the data without contradicting common sense about individual players. The simulator uses
          your selected lineup only as a <em>baseline unit</em>, then layers simple player-skill deltas on the swap—it is
          not re-deriving MVP order from the dropdown labels.
        </aside>
      </div>

      <div className="grid sm:grid-cols-2 gap-4">
        <label className="flex flex-col gap-1 text-xs font-mono uppercase text-slate-500">
          Team
          <select
            value={team}
            onChange={(e) => setTeam(e.target.value)}
            className="bg-white dark:bg-court-900 border border-slate-200 dark:border-court-700 rounded-lg px-3 py-2 text-sm"
          >
            {teams.map((t) => (
              <option key={t.team_abbr} value={t.team_abbr}>
                {t.team_abbr}
              </option>
            ))}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-xs font-mono uppercase text-slate-500 sm:col-span-2">
          <span>
            Lineup{' '}
            <span className="font-sans normal-case text-[11px] text-slate-500 font-normal">
              (≥{SIM_LINEUP_MIN_MINUTES} min together · up to {SIM_LINEUP_FETCH_LIMIT} by minutes)
            </span>
          </span>
          <select
            value={lineupId}
            onChange={(e) => setLineupId(e.target.value)}
            className="bg-white dark:bg-court-900 border border-slate-200 dark:border-court-700 rounded-lg px-3 py-2 text-sm"
          >
            {lineups.map((l) => {
              const label = `${lineupNames(l) || l.team_abbr} · ${l.minutes.toFixed(0)} min · net ${fmt1(l.net_rating)}`
              return (
                <option key={l.lineup_id} value={l.lineup_id} title={label}>
                  {label}
                </option>
              )
            })}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-xs font-mono uppercase text-slate-500">
          Player out
          <select
            value={outId === '' ? '' : String(outId)}
            onChange={(e) => setOutId(e.target.value ? Number(e.target.value) : '')}
            className="bg-white dark:bg-court-900 border border-slate-200 dark:border-court-700 rounded-lg px-3 py-2 text-sm"
          >
            <option value="">Select</option>
            {lineupPlayerIds.map((id) => {
              const pl = players.find((p) => samePlayerId(p.player_id, id))
              const label =
                pl?.player_name ?? (selected ? lineupPlayerNameById(selected, id) : null) ?? `Player #${id}`
              return (
                <option key={id} value={id}>
                  {label}
                </option>
              )
            })}
          </select>
        </label>
        <label className="flex flex-col gap-1 text-xs font-mono uppercase text-slate-500">
          Replacement in
          <select
            value={inId === '' ? '' : String(inId)}
            onChange={(e) => setInId(e.target.value ? Number(e.target.value) : '')}
            className="bg-white dark:bg-court-900 border border-slate-200 dark:border-court-700 rounded-lg px-3 py-2 text-sm"
          >
            <option value="">Select</option>
            {replacementPool.map((p) => (
              <option key={p.player_id} value={p.player_id}>
                {p.player_name} ({p.position ?? '—'})
              </option>
            ))}
          </select>
        </label>
      </div>

      <button
        type="button"
        onClick={runSim}
        className="px-6 py-2.5 rounded-lg bg-court-accent text-court-950 font-semibold text-sm hover:opacity-90"
      >
        Run simulation
      </button>

      {err && <p className="text-amber-400 text-sm">{err}</p>}

      {result && chartData && (
        <div className="space-y-6">
          <div className="grid sm:grid-cols-3 gap-4">
            <div className="rounded-xl border border-court-700 bg-court-900/40 p-4">
              <p className="text-xs font-mono text-slate-500 uppercase">Δ Net</p>
              <p className="text-3xl font-display text-court-line">{fmt2(result.delta_net_rating)}</p>
            </div>
            <div className="rounded-xl border border-court-700 bg-court-900/40 p-4">
              <p className="text-xs font-mono text-slate-500 uppercase">Δ Offense</p>
              <p className="text-3xl font-display text-white">{fmt2(result.delta_offensive_rating)}</p>
            </div>
            <div className="rounded-xl border border-court-700 bg-court-900/40 p-4">
              <p className="text-xs font-mono text-slate-500 uppercase">Δ Defense</p>
              <p className="text-3xl font-display text-white">{fmt2(result.delta_defensive_rating)}</p>
            </div>
          </div>

          <div className="h-64">
            <ResponsiveContainer>
              <BarChart data={chartData}>
                <CartesianGrid stroke="#334155" strokeOpacity={0.4} />
                <XAxis dataKey="name" tick={{ fill: '#94a3b8', fontSize: 11 }} />
                <YAxis tick={{ fill: '#94a3b8', fontSize: 11 }} domain={['auto', 'auto']} />
                <Tooltip
                  contentStyle={{ background: '#131d28', border: '1px solid #243044' }}
                  formatter={(value) => Number(value).toFixed(2)}
                />
                <Legend />
                <Bar dataKey="before" fill="#8b9aad" name="Before" radius={[4, 4, 0, 0]} />
                <Bar dataKey="after" fill="#3d9a7a" name="Projected" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      )}
    </div>
  )
}
