import api, { ApiResponse, ListData } from './index'

// 比赛类型
export enum MatchType {
  FRIENDLY = 'friendly',
  LEAGUE = 'league',
  CUP = 'cup',
  TRAINING = 'training'
}

// 比赛状态
export enum MatchStatus {
  SCHEDULED = 'scheduled',
  IN_PROGRESS = 'in_progress',
  COMPLETED = 'completed',
  CANCELLED = 'cancelled'
}

// 比赛信息
export interface Match {
  id: number
  home_team_id: number
  away_team_id: number
  home_team_name: string
  away_team_name: string
  match_type: string
  match_date: string
  venue?: string
  home_score?: number
  away_score?: number
  status: string
  notes?: string
  created_at: string
  updated_at: string
}

// 比赛列表项
export interface MatchListItem {
  id: number
  home_team_id: number
  away_team_id: number
  home_team_name: string
  away_team_name: string
  match_date: string
  home_score?: number
  away_score?: number
  status: string
  venue?: string
}

// 球员统计数据（创建比赛时使用）
export interface PlayerStatRequest {
  player_id: number
  played: boolean
  goals: number
  assists: number
}

// 创建比赛请求（简化版，不需要 home_team_id）
export interface CreateMatchRequest {
  away_team_name: string
  match_type: string
  match_date: string
  venue?: string
  home_score?: number
  away_score?: number
  notes?: string
  player_stats?: PlayerStatRequest[]  // 球员统计列表
}

// 更新比赛请求
export interface UpdateMatchRequest {
  match_type?: string
  match_date?: string
  venue?: string
  home_score?: number
  away_score?: number
  status?: string
  notes?: string
}

// 比赛球员统计
export interface MatchPlayer {
  id: number
  match_id: number
  player_id: number
  team_id: number
  player_name: string  // 球员名称
  played: boolean
  goals: number
  assists: number
  position?: string
  jersey_number?: number
  minutes_played?: number
  yellow_cards: number
  red_cards: number
}

// 更新球员统计请求
export interface UpdateMatchPlayerRequest {
  played?: boolean
  goals?: number
  assists?: number
  position?: string
  jersey_number?: number
  minutes_played?: number
  yellow_cards?: number
  red_cards?: number
}

// 出勤率信息
export interface AttendanceRate {
  player_id: number
  player_name: string
  total_matches: number
  played_matches: number
  attendance_rate: number
  total_goals: number
  total_assists: number
}

/**
 * 获取球队的所有比赛
 */
export function getTeamMatches(teamId: number, params?: {
  skip?: number
  limit?: number
}) {
  return api.get<ListData<MatchListItem>>(`/matches/team/${teamId}`, { params })
}

/**
 * 获取球队未来的比赛
 */
export function getUpcomingMatches(teamId: number) {
  return api.get<ListData<MatchListItem>>(`/matches/upcoming/${teamId}`)
}

/**
 * 获取球队最近的比赛
 */
export function getRecentMatches(teamId: number, days: number = 7) {
  return api.get<ListData<MatchListItem>>(`/matches/recent/${teamId}`, { params: { days } })
}

/**
 * 获取所有球队最近的比赛
 */
export function getAllRecentMatches(days: number = 7) {
  return api.get<ListData<MatchListItem>>('/matches/recent', { params: { days } })
}

/**
 * 获取所有比赛（不分时间）
 */
export function getAllMatches(params?: {
  skip?: number
  limit?: number
}) {
  return api.get<ListData<MatchListItem>>('/matches/all', { params })
}

/**
 * 获取比赛详情
 */
export function getMatchDetail(matchId: number) {
  return api.get<Match>(`/matches/${matchId}`)
}

/**
 * 创建比赛（简化版，home_team_id 自动从用户获取）
 */
export function createMatch(data: CreateMatchRequest) {
  return api.post<Match>('/matches', data)
}

/**
 * 更新比赛
 */
export function updateMatch(matchId: number, data: UpdateMatchRequest) {
  return api.put<Match>(`/matches/${matchId}`, data)
}

/**
 * 删除比赛
 */
export function deleteMatch(matchId: number) {
  return api.delete(`/matches/${matchId}`)
}

/**
 * 获取比赛的所有球员统计
 */
export function getMatchPlayerStats(matchId: number) {
  return api.get<ListData<MatchPlayer>>(`/match-players/match/${matchId}`)
}

/**
 * 更新球员在比赛中的统计
 */
export function updateMatchPlayerStats(
  matchId: number,
  playerId: number,
  data: UpdateMatchPlayerRequest
) {
  return api.put<MatchPlayer>(`/match-players/match/${matchId}/player/${playerId}`, data)
}

/**
 * 获取球员出勤率
 */
export function getPlayerAttendanceRate(teamId: number, playerId: number) {
  return api.get<AttendanceRate>(`/match-players/attendance/${teamId}/player/${playerId}`)
}

/**
 * 获取球队所有球员的出勤率
 */
export function getTeamAttendanceRates(teamId: number) {
  return api.get<ListData<AttendanceRate>>(`/match-players/attendance/${teamId}`)
}
