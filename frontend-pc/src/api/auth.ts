import api from './index'

export interface User {
  id: number
  username: string
  email: string
  my_team_id?: number
  is_admin: boolean
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export interface EnhancedRegisterSelectExisting {
  register_type: 'select_existing'
  username: string
  email: string
  password: string
  team_id: number
}

export interface EnhancedRegisterCreateNew {
  register_type: 'create_new'
  username: string
  email: string
  password: string
  team_name: string
  team_description?: string
  founded_year?: number
}

export interface EnhancedRegisterResponse {
  user: User
  team: {
    id: number
    name: string
    description?: string
    founded_year?: number
  }
  is_team_owner?: boolean
  message: string
}

export const authApi = {
  // 用户登录
  login: (username: string, password: string) =>
    api.post<LoginResponse>('/auth/login', { username, password }),

  // 用户注册（简单版本，不选择球队）
  register: (username: string, email: string, password: string) =>
    api.post<User>('/auth/register', { username, email, password }),

  // 增强用户注册（支持选择球队或创建新球队）
  registerEnhanced: (data: EnhancedRegisterSelectExisting | EnhancedRegisterCreateNew) =>
    api.post<EnhancedRegisterResponse>('/auth/register/enhanced', data)
}
