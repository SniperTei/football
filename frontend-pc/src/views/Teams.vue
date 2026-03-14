<template>
  <div class="teams-page">
    <el-card>
      <template #header>
        <div class="card-header">
          <span>球队列表</span>
          <el-button v-if="authStore.isAuthenticated" type="primary" @click="showDialog('create')">
            <el-icon><Plus /></el-icon>
            添加球队
          </el-button>
        </div>
      </template>

      <el-table :data="teams" v-loading="loading" style="width: 100%">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="球队名称" min-width="150" />
        <el-table-column prop="description" label="描述" show-overflow-tooltip />
        <el-table-column prop="founded_year" label="成立年份" width="120" />
        <el-table-column label="操作" width="250" fixed="right">
          <template #default="{ row }">
            <el-button type="primary" text @click="$router.push(`/teams/${row.id}`)">
              查看详情
            </el-button>
            <el-button v-if="canEditTeam(row)" type="primary" text @click="showDialog('edit', row)">
              编辑
            </el-button>
            <el-button v-if="canEditTeam(row)" type="danger" text @click="handleDelete(row)">
              删除
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-card>

    <!-- 添加/编辑弹窗 -->
    <el-dialog v-model="dialogVisible" :title="dialogTitle" width="500px">
      <el-form :model="form" :rules="rules" ref="formRef" label-width="100px">
        <el-form-item label="球队名称" prop="name">
          <el-input v-model="form.name" placeholder="请输入球队名称" />
        </el-form-item>
        <el-form-item label="描述" prop="description">
          <el-input v-model="form.description" type="textarea" placeholder="请输入球队描述" />
        </el-form-item>
        <el-form-item label="成立年份" prop="founded_year">
          <el-input-number v-model="form.founded_year" :min="1800" :max="2100" />
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
import { teamsApi } from '@/api'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'

const authStore = useAuthStore()
const loading = ref(false)
const submitLoading = ref(false)
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const formRef = ref<FormInstance>()
const teams = ref<any[]>([])
const editingId = ref<number>()

const dialogTitle = computed(() => dialogMode.value === 'create' ? '添加球队' : '编辑球队')

// 判断是否可以编辑球队（只有球队的拥有者可以编辑）
const canEditTeam = (team: any) => {
  if (!authStore.isAuthenticated || !authStore.user) {
    return false
  }
  // 只有当球队是当前用户的球队时才能编辑
  return authStore.user.my_team_id === team.id
}

const form = reactive({
  name: '',
  description: '',
  founded_year: undefined as number | undefined
})

const rules = {
  name: [{ required: true, message: '请输入球队名称', trigger: 'blur' }]
}

const loadTeams = async () => {
  loading.value = true
  try {
    const res = await teamsApi.getAll()
    teams.value = res.data.list
  } finally {
    loading.value = false
  }
}

const showDialog = (mode: 'create' | 'edit', data?: any) => {
  dialogMode.value = mode
  if (mode === 'edit' && data) {
    editingId.value = data.id
    form.name = data.name
    form.description = data.description || ''
    form.founded_year = data.founded_year
  } else {
    editingId.value = undefined
    form.name = ''
    form.description = ''
    form.founded_year = undefined
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
          await teamsApi.create(form)
          ElMessage.success('添加成功')
        } else {
          await teamsApi.update(editingId.value!, form)
          ElMessage.success('更新成功')
        }
        dialogVisible.value = false
        await loadTeams()
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
      `确定要删除球队 "${row.name}" 吗？此操作不可恢复。`,
      '删除确认',
      {
        confirmButtonText: '确定',
        cancelButtonText: '取消',
        type: 'warning'
      }
    )

    loading.value = true
    await teamsApi.delete(row.id)
    ElMessage.success('删除成功')
    await loadTeams()
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
})
</script>

<style scoped>
.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
