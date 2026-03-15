<template>
  <el-container class="main-layout">
    <el-header class="header">
      <div class="header-content">
        <div class="logo" @click="$router.push('/')">
          <el-icon><Football /></el-icon>
          <span>足球数据平台</span>
        </div>
        <el-menu
          :default-active="activeMenu"
          mode="horizontal"
          :ellipsis="false"
          class="menu"
        >
          <el-menu-item index="/dashboard" @click="$router.push('/dashboard')">首页</el-menu-item>
          <el-menu-item :index="teamsMenuIndex" @click="handleTeamsClick">球队</el-menu-item>
          <el-menu-item index="/players" @click="$router.push('/players')">球员</el-menu-item>
          <el-menu-item index="/matches" @click="$router.push('/matches')">比赛</el-menu-item>
          <el-menu-item index="/stats" @click="$router.push('/stats')">数据统计</el-menu-item>
          <el-menu-item index="/head-to-head" @click="$router.push('/head-to-head')">历史战绩</el-menu-item>
        </el-menu>
        <div class="user-section">
          <template v-if="isAuthenticated">
            <el-dropdown>
              <span class="user-name">
                <el-icon><User /></el-icon>
                {{ user?.username || '用户' }}
              </span>
              <template #dropdown>
                <el-dropdown-menu>
                  <template v-if="isAdmin">
                    <el-dropdown-item @click="$router.push('/admin/teams')">
                      <el-icon><Management /></el-icon>
                      管理球队
                    </el-dropdown-item>
                    <el-dropdown-item @click="$router.push('/admin/players')">
                      <el-icon><Management /></el-icon>
                      管理球员
                    </el-dropdown-item>
                    <el-dropdown-item @click="$router.push('/admin/matches')">
                      <el-icon><Management /></el-icon>
                      管理比赛
                    </el-dropdown-item>
                    <el-dropdown-item divided @click="authStore.logout">
                      <el-icon><SwitchButton /></el-icon>
                      退出登录
                    </el-dropdown-item>
                  </template>
                  <template v-else>
                    <el-dropdown-item @click="authStore.logout">
                      <el-icon><SwitchButton /></el-icon>
                      退出登录
                    </el-dropdown-item>
                  </template>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <el-button type="primary" @click="authStore.showLoginDialog()">登录</el-button>
            <el-button @click="$router.push('/register')">注册</el-button>
          </template>
        </div>
      </div>
    </el-header>
    <el-main class="main-content">
      <router-view />
    </el-main>
    <el-footer class="footer">
      <p>&copy; 2025 足球球队数据管理平台</p>
    </el-footer>

    <!-- 登录弹窗 -->
    <el-dialog v-model="loginDialogVisible" title="用户登录" width="400px" :close-on-click-modal="false">
      <el-form :model="loginForm" :rules="loginRules" ref="loginFormRef" label-width="80px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="loginForm.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="loginForm.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item>
          <div style="text-align: right; width: 100%;">
            <el-button text @click="showRegister">还没有账号？立即注册</el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="authStore.hideLoginDialog()">取消</el-button>
        <el-button type="primary" @click="handleLogin" :loading="loginLoading">登录</el-button>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup lang="ts">
import { computed, ref, reactive } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { ElMessage, type FormInstance } from 'element-plus'
import { User, Management, SwitchButton } from '@element-plus/icons-vue'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()

// 使用 storeToRefs 确保响应式
const { isAuthenticated, isAdmin, user, loginDialogRequired } = storeToRefs(authStore)

const activeMenu = computed(() => route.path)

const teamsMenuIndex = computed(() => {
  // 管理员在 /admin/teams 或 /teams 时都高亮"球队"菜单
  if (isAdmin.value && (route.path === '/admin/teams' || route.path === '/teams')) {
    return route.path
  }
  return '/teams'
})

const handleTeamsClick = () => {
  // 管理员点击"球队"跳转到 /admin/teams，普通用户跳转到 /teams
  if (isAdmin.value) {
    router.push('/admin/teams')
  } else {
    router.push('/teams')
  }
}

// 登录弹窗 - 使用 store 中的状态
const loginDialogVisible = computed({
  get: () => loginDialogRequired.value,
  set: (val) => {
    if (!val) authStore.hideLoginDialog()
  }
})
const loginLoading = ref(false)
const loginFormRef = ref<FormInstance>()

const loginForm = reactive({
  username: '',
  password: ''
})

const loginRules = {
  username: [{ required: true, message: '请输入用户名', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }]
}

const handleLogin = async () => {
  if (!loginFormRef.value) return

  await loginFormRef.value.validate(async (valid) => {
    if (valid) {
      loginLoading.value = true
      try {
        await authStore.login(loginForm.username, loginForm.password)
        ElMessage.success('登录成功')
        // 关闭弹窗
        authStore.hideLoginDialog()
        // 重置表单
        loginForm.username = ''
        loginForm.password = ''
        // 重置表单验证状态
        loginFormRef.value.clearValidate()
        // 跳转到之前尝试访问的页面
        const redirectPath = sessionStorage.getItem('redirectPath')
        if (redirectPath) {
          sessionStorage.removeItem('redirectPath')
          router.push(redirectPath)
        }
      } catch (error: any) {
        console.error('Login failed:', error)
        // 登录失败，保持弹窗打开
      } finally {
        loginLoading.value = false
      }
    }
  })
}

const showRegister = () => {
  authStore.hideLoginDialog()
  loginForm.username = ''
  loginForm.password = ''
  router.push('/register')
}
</script>

<style scoped>
.main-layout {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
}

.header {
  background: #fff;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
  padding: 0;
}

.header-content {
  display: flex;
  align-items: center;
  max-width: 1400px;
  margin: 0 auto;
  width: 100%;
  height: 60px;
}

.logo {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 20px;
  font-weight: bold;
  color: #409eff;
  cursor: pointer;
  padding: 0 20px;
  white-space: nowrap;
}

.menu {
  flex: 1;
  border: none;
}

.user-section {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 0 20px;
}

.user-name {
  display: flex;
  align-items: center;
  gap: 6px;
  cursor: pointer;
  font-size: 14px;
}

.main-content {
  max-width: 1400px;
  width: 100%;
  margin: 20px auto;
  padding: 0 20px;
}

.footer {
  background: #fff;
  border-top: 1px solid #e4e7ed;
  text-align: center;
  color: #909399;
  margin-top: auto;
}
</style>
