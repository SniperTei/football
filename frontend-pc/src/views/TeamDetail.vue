<template>
  <div class="team-detail-page">
    <el-page-header @back="$router.back()" :content="team?.name || '球队详情'">
      <template #content>
        <div class="header-content">
          <TeamLogo :logo-url="team?.logo_url" size="36px" :team-name="team?.name" />
          <span>{{ team?.name || '球队详情' }}</span>
        </div>
      </template>
    </el-page-header>

    <!-- 操作按钮 -->
    <div class="action-buttons" v-if="team">
      <el-button type="primary" @click="viewHistory">
        <el-icon><TrendCharts /></el-icon>
        查看历史战绩
      </el-button>
      <el-button v-if="canManage" type="success" @click="showDialog('create')">
        <el-icon><Plus /></el-icon>
        添加球员
      </el-button>
    </div>

    <el-card v-loading="loading" style="margin-top: 20px">
      <el-descriptions v-if="team" :column="2" border>
        <el-descriptions-item label="球队名称">{{ team.name }}</el-descriptions-item>
        <el-descriptions-item label="成立年份">{{ team.founded_year || '-' }}</el-descriptions-item>
        <el-descriptions-item label="球队ID">{{ team.id }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(team.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="最后更新">{{ formatDate(team.updated_at) }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ team.description || '-' }}</el-descriptions-item>
      </el-descriptions>

      <el-divider>球队球员 ({{ players.length }})</el-divider>

      <el-alert
        v-if="!players || players.length === 0"
        title="暂无球员信息"
        type="info"
        :closable="false"
        style="margin-top: 20px"
      />

      <el-table v-else :data="players" style="width: 100%; margin-top: 20px">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="姓名" min-width="120">
          <template #default="{ row }">
            <span class="player-name-link" @click="router.push(`/players/${row.id}`)">{{ row.name }}</span>
          </template>
        </el-table-column>
        <el-table-column prop="position" label="位置" width="100" />
        <el-table-column prop="jersey_number" label="球衣号码" width="100" />
        <el-table-column v-if="canManage" label="操作" width="180" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text @click="showDialog('edit', row)">编辑</el-button>
            <el-button type="danger" text @click="handleDelete(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑球员弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="姓名" prop="name">
          <el-input v-model="form.name" placeholder="请输入球员姓名" />
        </el-form-item>
        <el-form-item label="位置" prop="position">
          <el-select v-model="form.position" placeholder="请选择位置" style="width: 100%">
            <el-option label="前锋" value="前锋" />
            <el-option label="中场" value="中场" />
            <el-option label="后卫" value="后卫" />
            <el-option label="门将" value="门将" />
          </el-select>
        </el-form-item>
        <el-form-item label="球衣号码" prop="jersey_number">
          <el-input-number v-model="form.jersey_number" :min="1" :max="99" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitLoading">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { TrendCharts, Plus } from '@element-plus/icons-vue'
import { teamsApi, playersApi } from '@/api'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'
import dayjs from 'dayjs'
import TeamLogo from '@/components/TeamLogo.vue'

const route = useRoute()
const router = useRouter()
const authStore = useAuthStore()
const loading = ref(false)
const submitLoading = ref(false)
const team = ref<any>(null)
const players = ref<any[]>([])

// 弹窗相关
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const editingId = ref<number>()
const formRef = ref<FormInstance>()

const form = reactive({
  name: '',
  position: '',
  jersey_number: undefined as number | undefined
})

const rules = {
  name: [{ required: true, message: '请输入球员姓名', trigger: 'blur' }],
  position: [{ required: true, message: '请选择位置', trigger: 'change' }]
}

const dialogTitle = computed(() => dialogMode.value === 'create' ? '添加球员' : '编辑球员')

const canManage = computed(() => {
  if (!authStore.isAuthenticated || !authStore.user) return false
  if (authStore.isAdmin) return true
  return authStore.user.my_team_id === team.value?.id
})

const formatDate = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

const viewHistory = () => {
  const teamId = route.params.id
  router.push(`/teams/${teamId}/history`)
}

const showDialog = (mode: 'create' | 'edit', data?: any) => {
  dialogMode.value = mode
  if (mode === 'edit' && data) {
    editingId.value = data.id
    form.name = data.name
    form.position = data.position
    form.jersey_number = data.jersey_number
  } else {
    editingId.value = undefined
    form.name = ''
    form.position = ''
    form.jersey_number = undefined
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return
    submitLoading.value = true
    try {
      const payload = { ...form, team_id: Number(route.params.id) }
      if (dialogMode.value === 'create') {
        await playersApi.create(payload)
        ElMessage.success('添加成功')
      } else {
        await playersApi.update(editingId.value!, payload)
        ElMessage.success('更新成功')
      }
      dialogVisible.value = false
      await loadPlayers()
    } catch (error: any) {
      ElMessage.error(error.message || '操作失败')
    } finally {
      submitLoading.value = false
    }
  })
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除球员 "${row.name}" 吗？此操作不可恢复。`,
      '删除确认',
      { confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning' }
    )
    loading.value = true
    await playersApi.delete(row.id)
    ElMessage.success('删除成功')
    await loadPlayers()
  } catch (error: any) {
    if (error !== 'cancel') {
      ElMessage.error(error.message || '删除失败')
    }
  } finally {
    loading.value = false
  }
}

const loadPlayers = async () => {
  const teamId = Number(route.params.id)
  const playersRes = await playersApi.getByTeam(teamId)
  players.value = playersRes.data.list || []
}

const loadData = async () => {
  loading.value = true
  try {
    const teamId = Number(route.params.id)
    const teamRes = await teamsApi.getById(teamId)
    team.value = teamRes.data
    await loadPlayers()
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.team-detail-page {
  max-width: 1000px;
  margin: 0 auto;
}

.action-buttons {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.player-name-link {
  color: #409eff;
  cursor: pointer;
}

.player-name-link:hover {
  text-decoration: underline;
}
</style>
