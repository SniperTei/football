import api from './index'

export interface WCTeam {
  id: number
  name: string
  flag_url?: string
  group_name: string
  fifa_ranking?: number
  confederation?: string
  recent_wins: number
  recent_draws: number
  recent_losses: number
  recent_gf: number
  recent_ga: number
  wc_appearances: number
  wc_best_result?: string
  wc_titles: number
  key_players?: string
  notes?: string
}

export interface WCPrediction {
  id: number
  match_id: number
  home_win_prob: number
  draw_prob: number
  away_win_prob: number
  predicted_home_score?: number
  predicted_away_score?: number
  reasoning?: string
  model_version: string
}

export interface WCMatch {
  id: number
  match_number: number
  home_team_id: number
  away_team_id: number
  home_team_name?: string
  away_team_name?: string
  home_team_flag?: string
  away_team_flag?: string
  stage: string
  group_name?: string
  match_date?: string
  venue?: string
  home_score?: number
  away_score?: number
  status: string
  prediction?: WCPrediction
}

export interface GroupStandingItem {
  team: WCTeam
  predicted_points: number
  predicted_gf: number
  predicted_ga: number
  position: number
}

export interface GroupView {
  group_name: string
  teams: GroupStandingItem[]
  matches: WCMatch[]
}

export const wcApi = {
  // 公开接口
  getTeams: (group?: string) => api.get('/wc/teams', { params: { group } }),
  getTeam: (id: number) => api.get(`/wc/teams/${id}`),
  getGroups: () => api.get('/wc/groups'),
  getGroup: (name: string) => api.get(`/wc/groups/${name}`),
  getMatches: (params?: { stage?: string; group?: string }) =>
    api.get('/wc/matches', { params }),
  getMatch: (id: number) => api.get(`/wc/matches/${id}`),
  getPredictions: (params?: { stage?: string; group?: string }) =>
    api.get('/wc/predictions', { params }),

  // 管理接口
  createTeam: (data: Partial<WCTeam>) => api.post('/wc/teams', data),
  updateTeam: (id: number, data: Partial<WCTeam>) => api.put(`/wc/teams/${id}`, data),
  deleteTeam: (id: number) => api.delete(`/wc/teams/${id}`),
  createMatch: (data: any) => api.post('/wc/matches', data),
  updateMatch: (id: number, data: any) => api.put(`/wc/matches/${id}`, data),
  generatePredictions: (data?: { match_ids?: number[]; force_regenerate?: boolean }) =>
    api.post('/wc/predictions/generate', data || {}, { timeout: 180000 }),
}
