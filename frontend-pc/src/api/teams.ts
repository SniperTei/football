import api, { ListData } from './index'

export interface Team {
  id: number
  name: string
  description?: string
  logo_url?: string
  founded_year?: number
  created_at: string
  updated_at: string
}

export const teamsApi = {
  // 获取所有球队
  getAll: () => api.get<ListData<Team>>('/teams'),

  // 获取球队详情
  getById: (id: number) => api.get<Team>(`/teams/${id}`),

  // 创建球队
  create: (data: Partial<Team>) => api.post<Team>('/teams', data),

  // 更新球队
  update: (id: number, data: Partial<Team>) => api.put<Team>(`/teams/${id}`, data),

  // 删除球队
  delete: (id: number) => api.delete(`/teams/${id}`)
}
