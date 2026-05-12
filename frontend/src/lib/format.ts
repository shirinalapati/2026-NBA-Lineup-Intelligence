export function fmt1(n: number | null | undefined): string {
  if (n == null || Number.isNaN(n)) return '—'
  return n.toFixed(1)
}

export function fmt2(n: number | null | undefined): string {
  if (n == null || Number.isNaN(n)) return '—'
  return n.toFixed(2)
}

/** e.g. 1 → "1st", 22 → "22nd" */
export function ordinal(n: number): string {
  if (n % 100 >= 11 && n % 100 <= 13) return `${n}th`
  switch (n % 10) {
    case 1:
      return `${n}st`
    case 2:
      return `${n}nd`
    case 3:
      return `${n}rd`
    default:
      return `${n}th`
  }
}

type TeamLike = { team_abbr: string }

/**
 * Competition ranking (1,2,2,4) within `teams` using non-null values only.
 * Use higherIsBetter for ORtg, net, pace; lowerIsBetter for DRtg.
 */
export function leagueTeamRank<T extends TeamLike>(
  teams: T[],
  teamAbbr: string,
  getValue: (t: T) => number | null | undefined,
  higherIsBetter: boolean,
): { rank: number; total: number } | null {
  const rows = teams
    .map((t) => ({ abbr: t.team_abbr, v: getValue(t) }))
    .filter((r): r is { abbr: string; v: number } => r.v != null && !Number.isNaN(r.v))
  if (rows.length === 0) return null
  rows.sort((a, b) => (higherIsBetter ? b.v - a.v : a.v - b.v))
  const ranks = new Map<string, number>()
  for (let i = 0; i < rows.length; i++) {
    const r =
      i === 0 || rows[i].v !== rows[i - 1].v ? i + 1 : ranks.get(rows[i - 1].abbr) ?? i + 1
    ranks.set(rows[i].abbr, r)
  }
  const rank = ranks.get(teamAbbr)
  if (rank == null) return null
  return { rank, total: rows.length }
}

export function rankSlashTotal(r: { rank: number; total: number } | null): string | null {
  if (!r) return null
  return `${ordinal(r.rank)} / ${r.total}`
}

export function lineupNames(l: {
  player_1_name: string | null
  player_2_name: string | null
  player_3_name: string | null
  player_4_name: string | null
  player_5_name: string | null
}): string {
  return [l.player_1_name, l.player_2_name, l.player_3_name, l.player_4_name, l.player_5_name]
    .filter(Boolean)
    .join(' · ')
}

/** Name on the lineup row for `playerId` (when roster API omits that player for this team, e.g. trade lag). */
export function lineupPlayerNameById(
  l: {
    player_1_id: number | null
    player_1_name: string | null
    player_2_id: number | null
    player_2_name: string | null
    player_3_id: number | null
    player_3_name: string | null
    player_4_id: number | null
    player_4_name: string | null
    player_5_id: number | null
    player_5_name: string | null
  },
  playerId: number,
): string | null {
  const slots: [number | null, string | null][] = [
    [l.player_1_id, l.player_1_name],
    [l.player_2_id, l.player_2_name],
    [l.player_3_id, l.player_3_name],
    [l.player_4_id, l.player_4_name],
    [l.player_5_id, l.player_5_name],
  ]
  for (const [id, name] of slots) {
    if (id != null && Number(id) === Number(playerId) && name) return name
  }
  return null
}
