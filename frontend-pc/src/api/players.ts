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

export const playersApi = {
  // 获取所有球员
  getAll: (params?: { skip?: number; limit?: number }) =>
    api.get<ListData<Player>>('/players', { params }),

  // 获取球员详情
  getById: (id: number) => api.get<Player>(`/players/${id}`),

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
