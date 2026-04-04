import api, { ListData } from './index'

export interface Player {
  id: number
  team_id: number
  name: string
  position: string
  jersey_number: number | null
  created_at: string
  updated_at: string
}

export interface PlayerRecentMatch {
  match_id: number
  match_date: string | null
  match_type: string
  status: string
  is_home: boolean
  opponent_name: string
  home_score: number | string
  away_score: number | string
  played: boolean
  goals: number
  assists: number
  yellow_cards: number
  red_cards: number
}

export interface PlayerDetailData {
  id: number
  name: string
  position: string
  jersey_number: number | null
  team_id: number
  team_name: string
  team_logo_url: string | null
  created_at: string | null
  updated_at: string | null
  career_stats: {
    total_matches: number
    played_matches: number
    total_goals: number
    total_assists: number
    total_yellow_cards: number
    total_red_cards: number
  }
  attendance_rate: number
  recent_matches: PlayerRecentMatch[]
}

export const playersApi = {
  // 获取所有球员
  getAll: (params?: { page_index?: number; page_count?: number }) =>
    api.get<ListData<Player>>('/players', { params }),

  // 获取球员详情
  getById: (id: number) => api.get<Player>(`/players/${id}`),

  // 获取球员详细信息（聚合数据）
  getDetail: (id: number) => api.get<PlayerDetailData>(`/players/${id}/detail`),

  // 搜索球员（通过姓名）
  search: (keyword: string) => api.get<ListData<Player>>(`/players/search/${keyword}`),

  // 获取指定球队的球员
  getByTeam: (teamId: number) => api.get<ListData<Player>>(`/players/team/${teamId}`),

  // 创建球员
  create: (data: Partial<Player>) => api.post<Player>('/players', data),

  // 更新球员
  update: (id: number, data: Partial<Player>) => api.put<Player>(`/players/${id}`, data),

  // 删除球员
  delete: (id: number) => api.delete(`/players/${id}`)
}
