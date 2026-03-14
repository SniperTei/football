import api, { ListData } from './index'

// 球员排名信息
export interface PlayerRanking {
  rank: number
  player_id: number
  player_name: string
  jersey_number?: number
  team_id: number
  team_name: string
  total_goals?: number
  total_assists?: number
  played_matches?: number
  total_matches?: number
  attendance_rate?: number
}

/**
 * 获取进球榜
 */
export function getTopScorers(params?: { limit?: number; team_id?: number }) {
  return api.get<ListData<PlayerRanking>>('/stats/goals', { params })
}

/**
 * 获取助攻榜
 */
export function getTopAssists(params?: { limit?: number; team_id?: number }) {
  return api.get<ListData<PlayerRanking>>('/stats/assists', { params })
}

/**
 * 获取出勤榜
 */
export function getTopAttendance(params?: { limit?: number; team_id?: number }) {
  return api.get<ListData<PlayerRanking>>('/stats/attendance', { params })
}
