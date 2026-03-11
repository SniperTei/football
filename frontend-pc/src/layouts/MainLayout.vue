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
          router
        >
          <el-menu-item index="/dashboard">首页</el-menu-item>
          <el-menu-item index="/teams">球队</el-menu-item>
          <el-menu-item index="/players">球员</el-menu-item>
          <el-menu-item index="/matches">比赛</el-menu-item>
          <el-menu-item index="/stats">数据统计</el-menu-item>
          <el-menu-item index="/head-to-head">历史战绩</el-menu-item>
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
                  <el-dropdown-item @click="authStore.logout">
                    <el-icon><SwitchButton /></el-icon>
                    退出登录
                  </el-dropdown-item>
                </el-dropdown-menu>
              </template>
            </el-dropdown>
          </template>
          <template v-else>
            <el-button type="primary" @click="loginDialogVisible = true">登录</el-button>
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
        <el-button @click="loginDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleLogin" :loading="loginLoading">登录</el-button>
      </template>
    </el-dialog>
  </el-container>
</template>

<script setup lang="ts">
import { computed, ref, reactive, watch } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, type FormInstance } from 'element-plus'
import { storeToRefs } from 'pinia'
import { useAuthStore } from '@/stores/auth'

const route = useRoute()
const authStore = useAuthStore()

// 使用 storeToRefs 确保响应式
const { isAuthenticated, user } = storeToRefs(authStore)

const activeMenu = computed(() => route.path)

// 登录弹窗
const loginDialogVisible = ref(false)
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
        loginDialogVisible.value = false
        // 重置表单
        loginForm.username = ''
        loginForm.password = ''
        // 重置表单验证状态
        loginFormRef.value.clearValidate()
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
  loginDialogVisible.value = false
  loginForm.username = ''
  loginForm.password = ''
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
