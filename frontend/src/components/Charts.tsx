import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Scatter,
  ScatterChart,
  Tooltip,
  XAxis,
  YAxis,
  Cell,
} from 'recharts'
import type { Lineup } from '../types'
import { lineupNames } from '../lib/format'

const axis = { stroke: '#64748b', fontSize: 11 }
const grid = { stroke: '#334155', strokeOpacity: 0.3 }

export function TopNetBar({ lineups }: { lineups: Lineup[] }) {
  const data = lineups.slice(0, 10).map((l) => ({
    name: `${l.team_abbr}`,
    full: lineupNames(l).slice(0, 42) + (lineupNames(l).length > 42 ? '…' : ''),
    net: l.net_rating ?? 0,
  }))
  return (
    <div className="h-80 w-full">
      <ResponsiveContainer>
        <BarChart data={data} margin={{ top: 8, right: 8, left: 0, bottom: 48 }}>
          <CartesianGrid {...grid} />
          <XAxis dataKey="name" tick={axis} />
          <YAxis tick={axis} domain={['auto', 'auto']} />
          <Tooltip
            contentStyle={{ background: '#131d28', border: '1px solid #243044', borderRadius: 8 }}
            formatter={(value) => [Number(value).toFixed(2), 'Net']}
            labelFormatter={(label) => data.find((d) => d.name === label)?.full ?? label}
          />
          <Bar dataKey="net" radius={[4, 4, 0, 0]}>
            {data.map((_, i) => (
              <Cell key={i} fill={i < 3 ? '#c9a227' : '#3d9a7a'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

export function OffDefScatter({ lineups }: { lineups: Lineup[] }) {
  const data = lineups.map((l) => ({
    ortg: l.offensive_rating ?? 0,
    drtg: l.defensive_rating ?? 0,
    net: l.net_rating ?? 0,
    abbr: l.team_abbr,
  }))
  const axisLabel = { fill: '#64748b', fontSize: 11 }
  return (
    <div className="w-full">
      <div className="h-80 w-full">
        <ResponsiveContainer>
          <ScatterChart margin={{ top: 12, right: 12, bottom: 44, left: 28 }}>
            <CartesianGrid {...grid} />
            <XAxis
              type="number"
              dataKey="ortg"
              name="ORtg"
              tick={axis}
              domain={['auto', 'auto']}
              label={{
                value: 'ORtg — points scored per 100 poss. (higher → better offense)',
                position: 'bottom',
                offset: 22,
                style: axisLabel,
              }}
            />
            <YAxis
              type="number"
              dataKey="drtg"
              name="DRtg"
              tick={axis}
              domain={['auto', 'auto']}
              width={44}
              label={{
                value: 'DRtg — points allowed per 100 poss. (lower → better defense)',
                angle: -90,
                position: 'insideLeft',
                style: { ...axisLabel, textAnchor: 'middle' },
                offset: 0,
              }}
            />
            <Tooltip
              cursor={{ strokeDasharray: '3 3' }}
              content={({ active, payload }) => {
                if (!active || !payload?.[0]) return null
                const p = payload[0].payload as {
                  ortg: number
                  drtg: number
                  net: number
                  abbr: string
                }
                return (
                  <div
                    className="rounded-lg border border-slate-600 bg-[#131d28] px-3 py-2 text-xs shadow-lg"
                    style={{ color: '#e2e8f0' }}
                  >
                    <div className="font-mono text-court-accent">{p.abbr}</div>
                    <div>ORtg: {p.ortg.toFixed(1)}</div>
                    <div>DRtg: {p.drtg.toFixed(1)}</div>
                    <div>Net: {p.net.toFixed(1)}</div>
                  </div>
                )
              }}
            />
            <Scatter data={data} fill="#3d9a7a" />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-4 space-y-2 text-sm text-slate-600 dark:text-slate-400 leading-relaxed max-w-3xl">
        <p className="font-medium text-slate-700 dark:text-slate-300">How to read this chart</p>
        <p>
          Each point is one five-man lineup (same pool as the table above).{' '}
          <strong className="text-slate-700 dark:text-slate-300">Horizontal axis = ORtg</strong> (offensive efficiency:
          estimated points scored per 100 team possessions).{' '}
          <strong className="text-slate-700 dark:text-slate-300">Vertical axis = DRtg</strong> (defensive efficiency:
          estimated points allowed per 100 opponent possessions). Stronger offense is further{' '}
          <strong className="text-slate-700 dark:text-slate-300">right</strong>; stronger defense is further{' '}
          <strong className="text-slate-700 dark:text-slate-300">down</strong> (numerically lower DRtg). Lineups that look
          “good on both ends” tend toward the <strong className="text-slate-700 dark:text-slate-300">bottom-right</strong>{' '}
          (efficient offense, stingy defense). The opposite corner (top-left) is weaker on both axes at a glance—always
          pair the plot with minutes and the numeric table, since small samples can sit anywhere on the grid.
        </p>
      </div>
    </div>
  )
}

export function MinutesNetScatter({ lineups }: { lineups: Lineup[] }) {
  const data = lineups.map((l) => {
    const full = lineupNames(l)
    return {
      minutes: l.minutes,
      net: l.net_rating ?? 0,
      team: l.team_abbr,
      lineupShort: full.length > 48 ? `${full.slice(0, 48)}…` : full,
    }
  })
  const axisLabel = { fill: '#64748b', fontSize: 11 }
  return (
    <div className="w-full">
      <div className="h-72 w-full">
        <ResponsiveContainer>
          <ScatterChart margin={{ top: 12, right: 12, bottom: 44, left: 28 }}>
            <CartesianGrid {...grid} />
            <XAxis
              type="number"
              dataKey="minutes"
              name="Minutes"
              tick={axis}
              domain={['auto', 'auto']}
              label={{
                value: 'Minutes — time this five-man unit played together (season total)',
                position: 'bottom',
                offset: 22,
                style: axisLabel,
              }}
            />
            <YAxis
              type="number"
              dataKey="net"
              name="Net"
              tick={axis}
              domain={['auto', 'auto']}
              width={44}
              label={{
                value: 'Net rating — ORtg minus DRtg per 100 poss. (higher → better)',
                angle: -90,
                position: 'insideLeft',
                style: { ...axisLabel, textAnchor: 'middle' },
                offset: 0,
              }}
            />
            <Tooltip
              cursor={{ strokeDasharray: '3 3' }}
              content={({ active, payload }) => {
                if (!active || !payload?.[0]) return null
                const p = payload[0].payload as {
                  minutes: number
                  net: number
                  team: string
                  lineupShort: string
                }
                return (
                  <div
                    className="rounded-lg border border-slate-600 bg-[#131d28] px-3 py-2 text-xs shadow-lg max-w-xs"
                    style={{ color: '#e2e8f0' }}
                  >
                    <div className="font-mono text-court-accent">{p.team}</div>
                    <div className="mt-1 text-slate-300 leading-snug">{p.lineupShort}</div>
                    <div className="mt-2 space-y-0.5 tabular-nums">
                      <div>Minutes: {p.minutes.toFixed(0)}</div>
                      <div>Net: {p.net.toFixed(1)}</div>
                    </div>
                  </div>
                )
              }}
            />
            <Scatter data={data} fill="#8b5cf6" />
          </ScatterChart>
        </ResponsiveContainer>
      </div>
      <div className="mt-4 space-y-2 text-sm text-slate-600 dark:text-slate-400 leading-relaxed max-w-xl">
        <p className="font-medium text-slate-700 dark:text-slate-300">What you are looking at</p>
        <p>
          Each purple dot is <strong className="text-slate-700 dark:text-slate-300">one five-man lineup</strong> from the
          database (same season as the rest of the app). <strong className="text-slate-700 dark:text-slate-300">Horizontal
          position</strong> is how many <strong className="text-slate-700 dark:text-slate-300">total minutes</strong>{' '}
          that exact group was on the floor together. <strong className="text-slate-700 dark:text-slate-300">Vertical
          position</strong> is its <strong className="text-slate-700 dark:text-slate-300">net rating</strong>—roughly,
          how much that unit outscored opponents per 100 possessions (league-style ORtg − DRtg on the lineup row). Units
          toward the <strong className="text-slate-700 dark:text-slate-300">top</strong> were more effective; dots on the{' '}
          <strong className="text-slate-700 dark:text-slate-300">right</strong> played heavier minutes. Many dots pile up
          on the left because most five-man groups log modest time; a few staff-favorite lineups stretch far right. This
          is descriptive only—hover for team and names.
        </p>
      </div>
    </div>
  )
}
