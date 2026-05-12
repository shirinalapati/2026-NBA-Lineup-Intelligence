export type Lineup = {
  lineup_id: string
  team_abbr: string
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
  minutes: number
  possessions: number | null
  offensive_rating: number | null
  defensive_rating: number | null
  net_rating: number | null
  pace: number | null
  ast_pct: number | null
  reb_pct: number | null
  tov_pct: number | null
  efg_pct: number | null
  spacing_score: number | null
  playmaking_score: number | null
  defensive_activity_score: number | null
  rebounding_score: number | null
  underrated_lineup_score: number | null
}

export type Team = {
  team_abbr: string
  team_name: string
  offensive_rating: number | null
  defensive_rating: number | null
  net_rating: number | null
  pace: number | null
}

export type Player = {
  player_id: number
  player_name: string
  team_abbr: string
  position: string | null
  minutes_played: number | null
  ts_pct: number | null
  obpm: number | null
  dbpm: number | null
  offensive_rating: number | null
  defensive_rating: number | null
  ast_pct: number | null
}

export type SimulateResult = {
  team_abbr: string
  lineup_id: string
  baseline_offensive_rating: number
  baseline_defensive_rating: number
  baseline_net_rating: number
  projected_offensive_rating: number
  projected_defensive_rating: number
  projected_net_rating: number
  delta_offensive_rating: number
  delta_defensive_rating: number
  delta_net_rating: number
  summary: string
  removed_player: Player
  incoming_player: Player
}

export type SeasonScope = {
  season: string
  season_type: string
  data_source: string
  roster_mode?: string | null
  nba_stats_contract: string
}

export type SortMetric =
  | 'net_rating'
  | 'offensive_rating'
  | 'defensive_rating'
  | 'minutes'
  | 'possessions'
  | 'underrated_lineup_score'
