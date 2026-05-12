import type { Lineup } from '../types'
import { fmt1, fmt2, lineupNames } from '../lib/format'

type Props = {
  lineups: Lineup[]
  showUls?: boolean
  showRank?: boolean
  /** Wider min width so ORtg/DRtg/Net stay visible; scroll horizontally on small screens */
  wide?: boolean
}

export function LineupTable({ lineups, showUls, showRank = true, wide }: Props) {
  return (
    <div className="overflow-x-auto rounded-xl border border-slate-200 dark:border-court-700">
      <table className={`w-full text-sm text-left ${wide ? 'min-w-[720px]' : ''}`}>
        <thead>
          <tr className="border-b border-slate-200 dark:border-court-700 bg-slate-50 dark:bg-court-900/80 font-mono text-[11px] uppercase tracking-wider text-slate-500">
            {showRank && <th className="px-3 py-3 w-10">#</th>}
            <th className="px-3 py-3">Team</th>
            <th className="px-3 py-3 min-w-[280px]">Lineup</th>
            <th className="px-3 py-3 text-right">MIN</th>
            <th className="px-3 py-3 text-right">Poss</th>
            <th className="px-3 py-3 text-right">ORtg</th>
            <th className="px-3 py-3 text-right">DRtg</th>
            <th className="px-3 py-3 text-right">Net</th>
            {showUls && <th className="px-3 py-3 text-right">ULS</th>}
          </tr>
        </thead>
        <tbody>
          {lineups.map((l, i) => (
            <tr
              key={l.lineup_id}
              className="border-b border-slate-100 dark:border-court-800/80 hover:bg-slate-50/80 dark:hover:bg-court-800/40"
            >
              {showRank && <td className="px-3 py-2.5 font-mono text-slate-400">{i + 1}</td>}
              <td className="px-3 py-2.5 font-mono font-semibold text-court-accent">{l.team_abbr}</td>
              <td className="px-3 py-2.5 text-slate-700 dark:text-slate-300 max-w-md">{lineupNames(l)}</td>
              <td className="px-3 py-2.5 text-right tabular-nums">{fmt1(l.minutes)}</td>
              <td className="px-3 py-2.5 text-right tabular-nums">{fmt1(l.possessions)}</td>
              <td className="px-3 py-2.5 text-right tabular-nums">{fmt1(l.offensive_rating)}</td>
              <td className="px-3 py-2.5 text-right tabular-nums">{fmt1(l.defensive_rating)}</td>
              <td className="px-3 py-2.5 text-right tabular-nums font-medium text-court-line">{fmt2(l.net_rating)}</td>
              {showUls && (
                <td className="px-3 py-2.5 text-right tabular-nums text-slate-600 dark:text-slate-400">
                  {l.underrated_lineup_score != null ? fmt1(l.underrated_lineup_score) : '—'}
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
