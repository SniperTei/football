<template>
  <div class="players-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>球员列表</span>
          <el-button v-if="authStore.isAuthenticated" type="primary" @click="showDialog('create')">
            <el-icon><Plus /></el-icon>
            添加球员
          </el-button>
        </div>
      </template>

      <el-table :data="players" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="姓名" min-width="120" />
        <el-table-column prop="position" label="位置" width="100" />
        <el-table-column prop="jersey_number" label="球衣号码" width="100" />
        <el-table-column prop="team_id" label="所属球队" min-width="150">
          <template #default="{ row }">
            {{ getTeamName(row.team_id) }}
          </template>
        </el-table-column>
        <el-table-column label="操作" width="200" fixed="right">
          <template #default="{ row }">
            <el-button v-if="authStore.isAuthenticated" type="primary" text @click="showDialog('edit', row)">
              编辑
            </el-button>
            <el-button v-if="authStore.isAuthenticated" type="danger" text @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑弹窗 -->
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
        <el-form-item label="所属球队" prop="team_id">
          <el-select v-model="form.team_id" placeholder="请选择球队" style="width: 100%">
            <el-option
              v-for="team in teams"
              :key="team.id"
              :label="team.name"
              :value="team.id"
            />
          </el-select>
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
import { playersApi, teamsApi } from '@/api'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'

const authStore = useAuthStore()
const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const formRef = ref<FormInstance>()
const players = ref<any[]>([])
const teams = ref<any[]>([])
const editingId = ref<number>()

const dialogTitle = computed(() => dialogMode.value === 'create' ? '添加球员' : '编辑球员')

const form = reactive({
  name: '',
  position: '',
  jersey_number: undefined as number | undefined,
  team_id: undefined as number | undefined
})

const rules = {
  name: [{ required: true, message: '请输入球员姓名', trigger: 'blur' }],
  position: [{ required: true, message: '请选择位置', trigger: 'change' }],
  team_id: [{ required: true, message: '请选择球队', trigger: 'change' }]
}

const getTeamName = (teamId: number) => {
  const team = teams.value.find(t => t.id === teamId)
  return team ? team.name : '-'
}

const loadPlayers = async () => {
  loading.value = true
  try {
    const res = await playersApi.getAll()
    players.value = res.data.list
  } finally {
    loading.value = false
  }
}

const loadTeams = async () => {
  try {
    const res = await teamsApi.getAll()
    teams.value = res.data.list
  } catch (error) {
    console.error('加载球队列表失败:', error)
  }
}

const showDialog = (mode: 'create' | 'edit', data?: any) => {
  dialogMode.value = mode
  if (mode === 'edit' && data) {
    editingId.value = data.id
    form.name = data.name
    form.position = data.position
    form.jersey_number = data.jersey_number
    form.team_id = data.team_id
  } else {
    editingId.value = undefined
    form.name = ''
    form.position = ''
    form.jersey_number = undefined
    form.team_id = undefined
  }
  dialogVisible.value = true
}

const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (valid) {
      submitLoading.value = true
      try {
        if (dialogMode.value === 'create') {
          await playersApi.create(form)
          ElMessage.success('添加成功')
        } else {
          await playersApi.update(editingId.value!, form)
          ElMessage.success('更新成功')
        }
        dialogVisible.value = false
        await loadPlayers()
      } catch (error: any) {
        ElMessage.error(error.message || '操作失败')
      } finally {
        submitLoading.value = false
      }
    }
  })
}

const handleDelete = async (row: any) => {
  try {
    await ElMessageBox.confirm(
      `确定要删除球员 "${row.name}" 吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
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

onMounted(() => {
  loadTeams()
  loadPlayers()
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
