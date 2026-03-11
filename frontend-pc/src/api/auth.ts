import api from './index'

export interface User {
  id: number
  username: string
  email: string
  is_admin: boolean
}

export interface LoginResponse {
  access_token: string
  token_type: string
  user: User
}

export const authApi = {
  // 用户登录
  login: (username: string, password: string) =>
    api.post<LoginResponse>('/auth/login', { username, password }),

  // 用户注册
  register: (username: string, email: string, password: string) =>
    api.post<User>('/auth/register', { username, email, password })
}
