import axios from 'axios'
import { ElMessage } from 'element-plus'

// 统一响应格式
export interface ApiResponse<T = any> {
  code: number
  msg: string
  data: T
}

// 列表数据格式
export interface ListData<T = any> {
  list: T[]
  total: number
}

const api = axios.create({
  baseURL: '/api',
  timeout: 10000
})

// 请求拦截器
api.interceptors.request.use(
  (config) => {
    // 添加 token - 动态从 localStorage 读取
    const token = localStorage.getItem('token')
    if (token) {
      config.headers.Authorization = `Bearer ${token}`
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// 响应拦截器
api.interceptors.response.use(
  (response) => {
    const { data } = response

    // 处理统一的响应格式
    if (data && typeof data === 'object' && 'code' in data) {
      const apiResponse = data as ApiResponse

      // 成功响应
      if (apiResponse.code === 200) {
        // 返回 data 字段的内容
        response.data = apiResponse.data
        return response
      }

      // 业务错误
      const message = apiResponse.msg || '请求失败'
      ElMessage.error(message)

      // 特殊错误码处理
      if (apiResponse.code === 401) {
        // 清除所有认证信息
        localStorage.removeItem('token')
        localStorage.removeItem('user')
        // 触发事件通知其他组件
        window.dispatchEvent(new Event('auth:logout'))
        // 只在不是登录页时跳转
        if (!window.location.pathname.includes('/login')) {
          window.location.href = '/login'
        }
      }

      return Promise.reject(new Error(message))
    }

    return response
  },
  (error) => {
    const message = error.response?.data?.msg || error.response?.data?.detail || error.message || '请求失败'

    // 只在不是 401 错误时显示消息（401 的消息在业务错误处理中已经显示了）
    if (error.response?.status !== 401) {
      ElMessage.error(message)
    }

    if (error.response?.status === 401) {
      // 清除所有认证信息
      localStorage.removeItem('token')
      localStorage.removeItem('user')
      // 触发事件通知其他组件
      window.dispatchEvent(new Event('auth:logout'))
      // 只在不是登录页时跳转
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login'
      }
    }

    return Promise.reject(error)
  }
)

export default api

// 导出 API 模块
export * from './teams'
export * from './auth'
export * from './players'
