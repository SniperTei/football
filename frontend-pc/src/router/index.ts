import { createRouter, createWebHistory, RouteRecordRaw } from 'vue-router'
import { useAuthStore } from '@/stores/auth'

const routes: RouteRecordRaw[] = [
  {
    path: '/',
    redirect: '/dashboard'
  },
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { requiresAuth: false }
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

  if (to.meta.requiresAuth && !authStore.isAuthenticated) {
    next('/login')
  } else {
    next()
  }
})

export default router
