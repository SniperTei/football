import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'
import { ElMessage } from 'element-plus'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/register',
    name: 'Register',
    component: () => import('@/views/Register.vue'),
    meta: { requiresAuth: false }
  },
  {
    path: '/',
    component: () => import('@/layouts/MainLayout.vue'),
    meta: { requiresAuth: false },
    children: [
      {
        path: 'dashboard',
        name: 'Dashboard',
        component: () => import('@/views/Dashboard.vue')
      },
      {
        path: 'teams',
        name: 'Teams',
        component: () => import('@/views/Teams.vue')
      },
      {
        path: 'teams/:id',
        name: 'TeamDetail',
        component: () => import('@/views/TeamDetail.vue')
      },
      {
        path: 'teams/:id/history',
        name: 'TeamHistory',
        component: () => import('@/views/TeamHistory.vue'),
        meta: { title: '球队历史战绩' }
      },
      {
        path: 'players',
        name: 'Players',
        component: () => import('@/views/Players.vue')
      },
      {
        path: 'matches',
        name: 'Matches',
        component: () => import('@/views/Matches.vue')
      },
      {
        path: 'matches/:id',
        name: 'MatchDetail',
        component: () => import('@/views/MatchDetail.vue')
      },
      {
        path: 'stats',
        name: 'Stats',
        component: () => import('@/views/Stats.vue')
      },
      {
        path: 'head-to-head',
        name: 'HeadToHead',
        component: () => import('@/views/HeadToHead.vue')
      },
      // 管理页面（需要登录）
      {
        path: 'admin/teams',
        name: 'AdminTeams',
        component: () => import('@/views/admin/Teams.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'admin/players',
        name: 'AdminPlayers',
        component: () => import('@/views/admin/Players.vue'),
        meta: { requiresAuth: true }
      },
      {
        path: 'admin/matches',
        name: 'AdminMatches',
        component: () => import('@/views/admin/Matches.vue'),
        meta: { requiresAuth: true }
      }
    ]
  }
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

// 路由守卫
router.beforeEach((to, from, next) => {
  const authStore = useAuthStore()

  // 检查是否是管理员路径
  const isAdminPath = to.path.startsWith('/admin/')

  // 如果访问管理员路径但不是管理员，阻止访问
  if (isAdminPath && !authStore.isAdmin) {
    if (!authStore.isAuthenticated) {
      // 未登录：显示登录弹窗
      authStore.showLoginDialog()
      sessionStorage.setItem('redirectPath', to.fullPath)
      next(false)
    } else {
      // 已登录但不是管理员：显示错误提示并跳转到首页
      ElMessage.error('您没有管理员权限')
      next('/dashboard')
    }
    return
  }

  // 检查是否需要登录
  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    // 显示登录弹窗
    authStore.showLoginDialog()
    // 保存目标路由，登录后可以跳转回去
    sessionStorage.setItem('redirectPath', to.fullPath)
    // 取消当前导航，停留在当前页面
    next(false)
  } else {
    next()
  }
})

export default router
