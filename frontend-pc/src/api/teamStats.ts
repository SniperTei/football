import api from './index'

/**
 * 球队统计信息
 */
export interface TeamStatistics {
  total_matches: number
  wins: number
  draws: number
  losses: number
  win_rate: number
  goals_for: number
  goals_against: number
  goal_difference: number
  clean_sheets: number
  home_wins: number
  home_draws: number
  home_losses: number
  away_wins: number
  away_draws: number
  away_losses: number
  recent_form: RecentMatch[]
}

/**
 * 最近比赛记录
 */
export interface RecentMatch {
  match_id: number
  date: string
  opponent: string
  result: 'W' | 'D' | 'L'
  score: string
  venue: string
}

/**
 * 对战历史统计
 */
export interface HeadToHeadStats {
  total_matches: number
  team_wins: number
  team_draws: number
  team_losses: number
  team_goals_for: number
  team_goals_against: number
  recent_matches: RecentMatch[]
}

/**
 * 获取球队统计信息
 * @param teamId 球队ID
 * @param days 天数筛选（可选）
 */
export function getTeamStats(teamId: number, days?: number) {
  return api.get<{ data: TeamStatistics }>(`/stats/team/${teamId}/stats`, {
    params: days ? { days } : undefined
  })
}

/**
 * 获取两个球队之间的对战历史
 * @param teamId 球队ID
 * @param opponentId 对手ID
 */
export function getHeadToHeadStats(teamId: number, opponentId: number) {
  return api.get<{ data: HeadToHeadStats }>(`/stats/team/${teamId}/head-to-head/${opponentId}`)
}
