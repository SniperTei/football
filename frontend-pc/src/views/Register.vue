<template>
  <div class="register-container">
    <el-card class="register-card">
      <template #header>
        <div class="card-header">
          <el-icon><Football /></el-icon>
          <span>用户注册</span>
        </div>
      </template>
      <el-form :model="form" :rules="rules" ref="formRef" label-width="90px">
        <el-form-item label="用户名" prop="username">
          <el-input v-model="form.username" placeholder="请输入用户名" />
        </el-form-item>
        <el-form-item label="邮箱" prop="email">
          <el-input v-model="form.email" placeholder="请输入邮箱" />
        </el-form-item>
        <el-form-item label="密码" prop="password">
          <el-input v-model="form.password" type="password" placeholder="请输入密码" show-password />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPassword">
          <el-input v-model="form.confirmPassword" type="password" placeholder="请再次输入密码" show-password />
        </el-form-item>

        <!-- 球队选项 -->
        <el-form-item label="球队">
          <el-radio-group v-model="registerType" @change="handleRegisterTypeChange">
            <el-radio value="select_existing">加入现有球队</el-radio>
            <el-radio value="create_new">创建新球队</el-radio>
          </el-radio-group>
        </el-form-item>

        <!-- 选择现有球队 -->
        <el-form-item v-if="registerType === 'select_existing'" label="选择球队" prop="team_id">
          <el-select
            v-model="form.team_id"
            placeholder="请选择球队"
            filterable
            style="width: 100%"
            :loading="teamsLoading"
          >
            <el-option
              v-for="team in teams"
              :key="team.id"
              :label="team.name"
              :value="team.id"
            />
          </el-select>
        </el-form-item>

        <!-- 创建新球队 -->
        <template v-if="registerType === 'create_new'">
          <el-form-item label="球队名称" prop="team_name">
            <el-input v-model="form.team_name" placeholder="请输入球队名称" />
          </el-form-item>
          <el-form-item label="球队描述">
            <el-input
              v-model="form.team_description"
              type="textarea"
              placeholder="请输入球队描述（可选）"
              :rows="2"
            />
          </el-form-item>
          <el-form-item label="成立年份">
            <el-input-number
              v-model="form.founded_year"
              :min="1900"
              :max="2030"
              placeholder="可选"
              style="width: 100%"
            />
          </el-form-item>
        </template>

        <el-form-item>
          <el-button type="primary" @click="handleRegister" :loading="loading" style="width: 100%">
            注册
          </el-button>
        </el-form-item>
        <el-form-item>
          <el-button text @click="goToLogin">
            已有账号？立即登录
          </el-button>
        </el-form-item>
      </el-form>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance } from 'element-plus'
import { useAuthStore } from '@/stores/auth'
import { teamsApi, type Team } from '@/api'

const router = useRouter()
const authStore = useAuthStore()
const formRef = ref<FormInstance>()
const loading = ref(false)
const teamsLoading = ref(false)
const registerType = ref<'select_existing' | 'create_new'>('select_existing')
const teams = ref<Team[]>([])

const form = reactive({
  username: '',
  email: '',
  password: '',
  confirmPassword: '',
  team_id: undefined as number | undefined,
  team_name: '',
  team_description: '',
  founded_year: undefined as number | undefined
})

const validatePassword = (rule: any, value: any, callback: any) => {
  if (value === '') {
    callback(new Error('请再次输入密码'))
  } else if (value !== form.password) {
    callback(new Error('两次输入密码不一致'))
  } else {
    callback()
  }
}

const rules = {
  username: [
    { required: true, message: '请输入用户名', trigger: 'blur' },
    { min: 3, max: 20, message: '用户名长度在 3 到 20 个字符', trigger: 'blur' }
  ],
  email: [
    { required: true, message: '请输入邮箱', trigger: 'blur' },
    { type: 'email', message: '请输入正确的邮箱格式', trigger: 'blur' }
  ],
  password: [
    { required: true, message: '请输入密码', trigger: 'blur' },
    { min: 6, message: '密码长度不能少于 6 个字符', trigger: 'blur' }
  ],
  confirmPassword: [{ validator: validatePassword, trigger: 'blur' }],
  team_id: [
    { required: true, message: '请选择球队', trigger: 'change', type: 'number' }
  ],
  team_name: [
    { required: true, message: '请输入球队名称', trigger: 'blur' },
    { min: 2, max: 50, message: '球队名称长度在 2 到 50 个字符', trigger: 'blur' }
  ]
}

const handleRegisterTypeChange = () => {
  // 清空另一方的验证和值
  if (registerType.value === 'select_existing') {
    form.team_name = ''
    form.team_description = ''
    form.founded_year = undefined
    formRef.value?.clearValidate(['team_name'])
  } else {
    form.team_id = undefined
    formRef.value?.clearValidate(['team_id'])
  }
}

const loadTeams = async () => {
  teamsLoading.value = true
  try {
    const response = await teamsApi.getAll()
    teams.value = response.data.list || []
  } finally {
    teamsLoading.value = false
  }
}

const handleRegister = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      loading.value = true
      try {
        const result = await authStore.registerEnhanced(
          registerType.value === 'select_existing'
            ? {
                register_type: 'select_existing',
                username: form.username,
                email: form.email,
                password: form.password,
                team_id: form.team_id!
              }
            : {
                register_type: 'create_new',
                username: form.username,
                email: form.email,
                password: form.password,
                team_name: form.team_name,
                team_description: form.team_description || undefined,
                founded_year: form.founded_year
              }
        )
        ElMessage.success(result.message || '注册成功')

        // 自动登录
        await authStore.login(form.username, form.password)
        ElMessage.success('登录成功，欢迎使用！')
        router.push('/')
      } finally {
        loading.value = false
      }
    }
  })
}

const goToLogin = () => {
  router.push('/')
  authStore.showLoginDialog()
}

onMounted(() => {
  loadTeams()
})
</script>

<style scoped>
.register-container {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  padding: 20px;
}

.register-card {
  width: 100%;
  max-width: 400px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 8px;
  font-size: 20px;
  font-weight: bold;
  color: #409eff;
}
</style>
