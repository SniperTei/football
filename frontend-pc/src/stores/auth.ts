import { defineStore } from 'pinia'
import { ref, computed, watch } from 'vue'
import { authApi, type User } from '@/api'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('token'))
  const user = ref<User | null>(null)

  const isAuthenticated = computed(() => !!token.value)

  const setToken = (newToken: string) => {
    token.value = newToken
    localStorage.setItem('token', newToken)
    console.log('Token set:', newToken.substring(0, 20) + '...')
  }

  const setUser = (newUser: User) => {
    user.value = newUser
    localStorage.setItem('user', JSON.stringify(newUser))
    console.log('User set:', newUser)
  }

  const clearAuth = () => {
    token.value = null
    user.value = null
    localStorage.removeItem('token')
    localStorage.removeItem('user')
    console.log('Auth cleared')
  }

  const login = async (username: string, password: string) => {
    const response = await authApi.login(username, password)
    // 响应拦截器已经提取了 data 字段，所以直接用 response.data
    setToken(response.data.access_token)
    setUser(response.data.user)
    console.log('Login successful, user:', response.data.user)
    console.log('isAuthenticated should be true now')
  }

  const register = async (username: string, email: string, password: string) => {
    await authApi.register(username, email, password)
  }

  const logout = () => {
    clearAuth()
  }

  // 初始化时从 localStorage 恢复用户信息
  if (token.value) {
    const savedUser = localStorage.getItem('user')
    if (savedUser) {
      try {
        user.value = JSON.parse(savedUser)
        console.log('Restored user from localStorage:', user.value)
      } catch (e) {
        console.error('Failed to parse saved user', e)
        clearAuth()
      }
    }
  }

  // 监听 logout 事件（当 API 请求返回 401 时）
  window.addEventListener('auth:logout', () => {
    clearAuth()
  })

  return {
    token,
    user,
    isAuthenticated,
    login,
    register,
    logout,
    clearAuth
  }
})
