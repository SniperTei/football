<template>
  <div class="worldcup-page">
    <el-tabs v-model="activeTab">
      <!-- Tab 1: 小组赛况 -->
      <el-tab-pane label="小组赛况" name="groups">
        <div class="groups-grid" v-loading="loading">
          <el-card
            v-for="group in groups"
            :key="group.group_name"
            class="group-card"
          >
            <template #header>
              <div class="group-header">
                <span class="group-label">{{ group.group_name }} 组</span>
                <el-tag size="small" type="info">{{ group.teams.length }} 队</el-tag>
              </div>
            </template>
            <div class="mobile-scroll-table">
            <el-table :data="group.teams" size="small" :show-header="true">
              <el-table-column label="#" width="40" align="center">
                <template #default="{ row }">
                  <span :class="row.position <= 2 ? 'qualify-pos' : ''">{{ row.position }}</span>
                </template>
              </el-table-column>
              <el-table-column label="球队" min-width="120">
                <template #default="{ row }">
                  <div class="team-cell">
                    <span class="team-flag">{{ row.team.flag_url || '⚽' }}</span>
                    <span class="team-name">{{ row.team.name }}</span>
                  </div>
                </template>
              </el-table-column>
              <el-table-column label="排名" width="60" align="center" prop="team.fifa_ranking" />
              <el-table-column label="预测分" width="80" align="center">
                <template #default="{ row }">
                  <span class="points">{{ row.predicted_points }}</span>
                </template>
              </el-table-column>
              <el-table-column label="±" width="60" align="center">
                <template #default="{ row }">
                  <span :class="row.predicted_gf - row.predicted_ga > 0 ? 'goal-positive' : 'goal-negative'">
                    {{ (row.predicted_gf - row.predicted_ga).toFixed(1) }}
                  </span>
                </template>
              </el-table-column>
            </el-table>
            </div>
          </el-card>
        </div>
      </el-tab-pane>

      <!-- Tab 2: 比赛预测 -->
      <el-tab-pane label="比赛预测" name="matches">
        <div class="matches-toolbar">
          <el-select v-model="selectedGroup" placeholder="筛选小组" clearable style="width: 120px">
            <el-option v-for="g in groupNames" :key="g" :label="g + ' 组'" :value="g" />
          </el-select>
          <el-button type="primary" @click="loadMatches">
            <el-icon><Search /></el-icon>
            查询
          </el-button>
        </div>
        <div class="mobile-scroll-table">
        <el-table :data="matches" v-loading="loading" style="width: 100%">
          <el-table-column label="场次" width="70" prop="match_number" align="center" />
          <el-table-column label="小组" width="70" prop="group_name" align="center" />
          <el-table-column label="主队" min-width="130" align="right">
            <template #default="{ row }">
              <span>{{ row.home_team_flag || '' }} {{ row.home_team_name }}</span>
            </template>
          </el-table-column>
          <el-table-column label="预测" width="220" align="center">
            <template #default="{ row }">
              <div v-if="row.prediction" class="prob-bar">
                <div class="prob-segment home" :style="{ width: row.prediction.home_win_prob + '%' }">
                  {{ row.prediction.home_win_prob.toFixed(0) }}%
                </div>
                <div class="prob-segment draw" :style="{ width: row.prediction.draw_prob + '%' }">
                  {{ row.prediction.draw_prob.toFixed(0) }}%
                </div>
                <div class="prob-segment away" :style="{ width: row.prediction.away_win_prob + '%' }">
                  {{ row.prediction.away_win_prob.toFixed(0) }}%
                </div>
              </div>
              <span v-else class="no-pred">未预测</span>
            </template>
          </el-table-column>
          <el-table-column label="客队" min-width="130" align="left">
            <template #default="{ row }">
              <span>{{ row.away_team_name }} {{ row.away_team_flag || '' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="预测比分" width="100" align="center">
            <template #default="{ row }">
              <span v-if="row.prediction">
                {{ Math.round(row.prediction.predicted_home_score) }} - {{ Math.round(row.prediction.predicted_away_score) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column label="期望进球" width="110" align="center">
            <template #default="{ row }">
              <span v-if="row.prediction" style="color: #909399; font-size: 12px;">
                {{ row.prediction.predicted_home_score?.toFixed(1) }} - {{ row.prediction.predicted_away_score?.toFixed(1) }}
              </span>
            </template>
          </el-table-column>
          <el-table-column type="expand">
            <template #default="{ row }">
              <div v-if="row.prediction?.reasoning" class="reasoning-box">
                <strong>AI 分析：</strong>{{ row.prediction.reasoning }}
              </div>
            </template>
          </el-table-column>
        </el-table>
        </div>
      </el-tab-pane>

      <!-- Tab 3: 数据管理 (管理员) -->
      <el-tab-pane label="数据管理" name="admin" v-if="isAdmin">
        <div class="admin-section">
          <el-card>
            <template #header>
              <div class="card-header">
                <span>AI 预测生成</span>
              </div>
            </template>
            <p style="color: #909399; margin-bottom: 16px;">
              点击按钮调用 AI 预测所有未预测的小组赛。每次生成约需 2-5 分钟。
            </p>
            <el-button
              type="primary"
              @click="handleGeneratePredictions()"
              :loading="generating"
              :disabled="generating"
            >
              {{ generating ? '生成中...' : '生成预测' }}
            </el-button>
            <div v-if="taskProgress" style="margin-top: 12px; color: #606266;">
              {{ taskProgress }}
            </div>
            <el-button @click="handleGeneratePredictions(true)" :loading="generating">
              强制重新生成
            </el-button>
          </el-card>

          <el-card style="margin-top: 20px">
            <template #header>
              <div class="card-header">
                <span>球队管理</span>
                <el-button type="primary" size="small" @click="showTeamDialog()">添加球队</el-button>
              </div>
            </template>
            <div class="mobile-scroll-table">
            <el-table :data="teams" size="small" v-loading="loading">
              <el-table-column prop="id" label="ID" width="60" />
              <el-table-column label="国旗" width="60">
                <template #default="{ row }">{{ row.flag_url || '⚽' }}</template>
              </el-table-column>
              <el-table-column prop="name" label="名称" min-width="120" />
              <el-table-column prop="group_name" label="小组" width="60" />
              <el-table-column prop="fifa_ranking" label="FIFA排名" width="90" />
              <el-table-column label="近期战绩" min-width="120">
                <template #default="{ row }">
                  {{ row.recent_wins }}W {{ row.recent_draws }}D {{ row.recent_losses }}L
                </template>
              </el-table-column>
              <el-table-column label="操作" width="120" fixed="right">
                <template #default="{ row }">
                  <el-button type="primary" text size="small" @click="showTeamDialog(row)">编辑</el-button>
                  <el-button type="danger" text size="small" @click="handleDeleteTeam(row)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
            </div>
          </el-card>
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 球队编辑弹窗 -->
    <el-dialog v-model="teamDialogVisible" :title="editingTeamId ? '编辑球队' : '添加球队'" width="600px">
      <el-form :model="teamForm" :rules="teamRules" ref="teamFormRef" label-width="100px">
        <el-form-item label="球队名称" prop="name">
          <el-input v-model="teamForm.name" placeholder="国家名" />
        </el-form-item>
        <el-form-item label="国旗" prop="flag_url">
          <el-input v-model="teamForm.flag_url" placeholder="emoji 或图片 URL" />
        </el-form-item>
        <el-form-item label="小组" prop="group_name">
          <el-select v-model="teamForm.group_name" placeholder="选择小组">
            <el-option v-for="g in 'ABCDEFGHIJKL'.split('')" :key="g" :label="g + ' 组'" :value="g" />
          </el-select>
        </el-form-item>
        <el-form-item label="FIFA排名" prop="fifa_ranking">
          <el-input-number v-model="teamForm.fifa_ranking" :min="1" :max="300" />
        </el-form-item>
        <el-form-item label="洲际" prop="confederation">
          <el-select v-model="teamForm.confederation" placeholder="选择洲际" clearable>
            <el-option label="UEFA (欧洲)" value="UEFA" />
            <el-option label="CONMEBOL (南美)" value="CONMEBOL" />
            <el-option label="CONCACAF (中北美)" value="CONCACAF" />
            <el-option label="CAF (非洲)" value="CAF" />
            <el-option label="AFC (亚洲)" value="AFC" />
            <el-option label="OFC (大洋洲)" value="OFC" />
          </el-select>
        </el-form-item>
        <el-divider>近期战绩（近10场）</el-divider>
        <el-row :gutter="10">
          <el-col :span="8">
            <el-form-item label="胜" prop="recent_wins">
              <el-input-number v-model="teamForm.recent_wins" :min="0" :max="10" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="平" prop="recent_draws">
              <el-input-number v-model="teamForm.recent_draws" :min="0" :max="10" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="负" prop="recent_losses">
              <el-input-number v-model="teamForm.recent_losses" :min="0" :max="10" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-row :gutter="10">
          <el-col :span="12">
            <el-form-item label="进球" prop="recent_gf">
              <el-input-number v-model="teamForm.recent_gf" :min="0" />
            </el-form-item>
          </el-col>
          <el-col :span="12">
            <el-form-item label="失球" prop="recent_ga">
              <el-input-number v-model="teamForm.recent_ga" :min="0" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-divider>世界杯历史</el-divider>
        <el-row :gutter="10">
          <el-col :span="8">
            <el-form-item label="参赛次数" prop="wc_appearances">
              <el-input-number v-model="teamForm.wc_appearances" :min="0" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="夺冠次数" prop="wc_titles">
              <el-input-number v-model="teamForm.wc_titles" :min="0" />
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="最好成绩" prop="wc_best_result">
              <el-input v-model="teamForm.wc_best_result" placeholder="如：冠军" />
            </el-form-item>
          </el-col>
        </el-row>
        <el-form-item label="核心球员" prop="key_players">
          <el-input v-model="teamForm.key_players" placeholder='如：["Messi", "Alvarez"]' />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="teamDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSaveTeam" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { wcApi } from '@/api'
import { useAuthStore } from '@/stores/auth'
import { ElMessage, ElMessageBox, type FormInstance } from 'element-plus'

const authStore = useAuthStore()
const isAdmin = computed(() => authStore.isAdmin)
const loading = ref(false)
const generating = ref(false)
const saving = ref(false)
const activeTab = ref('groups')

// 小组数据
const groups = ref<any[]>([])
const matches = ref<any[]>([])
const teams = ref<any[]>([])
const selectedGroup = ref<string>('')

const groupNames = 'ABCDEFGHIJKL'.split('')

// 球队弹窗
const teamDialogVisible = ref(false)
const editingTeamId = ref<number>()
const teamFormRef = ref<FormInstance>()
const teamForm = reactive({
  name: '',
  flag_url: '',
  group_name: '',
  fifa_ranking: undefined as number | undefined,
  confederation: '',
  recent_wins: 0,
  recent_draws: 0,
  recent_losses: 0,
  recent_gf: 0,
  recent_ga: 0,
  wc_appearances: 0,
  wc_best_result: '',
  wc_titles: 0,
  key_players: '',
})

const teamRules = {
  name: [{ required: true, message: '请输入球队名称', trigger: 'blur' }],
  group_name: [{ required: true, message: '请选择小组', trigger: 'change' }],
}

const loadGroups = async () => {
  loading.value = true
  try {
    const res = await wcApi.getGroups()
    groups.value = res.data || []
  } catch (e) {
    console.error('加载小组数据失败:', e)
  } finally {
    loading.value = false
  }
}

const loadMatches = async () => {
  loading.value = true
  try {
    const params: any = {}
    if (selectedGroup.value) params.group = selectedGroup.value
    const res = await wcApi.getMatches(params)
    matches.value = res.data?.list || []
  } catch (e) {
    console.error('加载比赛失败:', e)
  } finally {
    loading.value = false
  }
}

const loadTeams = async () => {
  try {
    const res = await wcApi.getTeams()
    teams.value = res.data?.list || []
  } catch (e) {
    console.error('加载球队失败:', e)
  }
}

const taskProgress = ref('')
let pollTimer: ReturnType<typeof setInterval> | null = null

const pollStatus = () => {
  pollTimer = setInterval(async () => {
    try {
      const res = await wcApi.getPredictionStatus()
      const status = res.data
      taskProgress.value = status.progress || ''
      if (!status.running) {
        if (pollTimer) clearInterval(pollTimer)
        pollTimer = null
        generating.value = false
        if (status.result && !status.result.error) {
          ElMessage.success(taskProgress.value)
        }
        await Promise.all([loadGroups(), loadMatches()])
      }
    } catch {
      if (pollTimer) clearInterval(pollTimer)
      pollTimer = null
      generating.value = false
    }
  }, 30000)
}

const handleGeneratePredictions = async (force = false) => {
  generating.value = true
  taskProgress.value = '已提交，等待开始...'
  try {
    const res = await wcApi.generatePredictions({ force_regenerate: force })
    if (res.data?.status === 'started') {
      pollStatus()
    }
  } catch (e: any) {
    generating.value = false
    ElMessage.error(e.message || e.msg || '生成失败')
  }
}

// 球队 CRUD
const showTeamDialog = (team?: any) => {
  if (team) {
    editingTeamId.value = team.id
    Object.assign(teamForm, {
      name: team.name,
      flag_url: team.flag_url || '',
      group_name: team.group_name,
      fifa_ranking: team.fifa_ranking,
      confederation: team.confederation || '',
      recent_wins: team.recent_wins || 0,
      recent_draws: team.recent_draws || 0,
      recent_losses: team.recent_losses || 0,
      recent_gf: team.recent_gf || 0,
      recent_ga: team.recent_ga || 0,
      wc_appearances: team.wc_appearances || 0,
      wc_best_result: team.wc_best_result || '',
      wc_titles: team.wc_titles || 0,
      key_players: team.key_players || '',
    })
  } else {
    editingTeamId.value = undefined
    Object.assign(teamForm, {
      name: '', flag_url: '', group_name: '', fifa_ranking: undefined, confederation: '',
      recent_wins: 0, recent_draws: 0, recent_losses: 0, recent_gf: 0, recent_ga: 0,
      wc_appearances: 0, wc_best_result: '', wc_titles: 0, key_players: '',
    })
  }
  teamDialogVisible.value = true
}

const handleSaveTeam = async () => {
  if (!teamFormRef.value) return
  await teamFormRef.value.validate(async (valid) => {
    if (!valid) return
    saving.value = true
    try {
      const data = { ...teamForm, fifa_ranking: teamForm.fifa_ranking || null }
      if (editingTeamId.value) {
        await wcApi.updateTeam(editingTeamId.value, data)
        ElMessage.success('更新成功')
      } else {
        await wcApi.createTeam(data)
        ElMessage.success('添加成功')
      }
      teamDialogVisible.value = false
      await loadTeams()
    } catch (e: any) {
      ElMessage.error(e.message || '操作失败')
    } finally {
      saving.value = false
    }
  })
}

const handleDeleteTeam = async (row: any) => {
  try {
    await ElMessageBox.confirm(`确定删除球队 "${row.name}"？`, '删除确认', {
      confirmButtonText: '确定', cancelButtonText: '取消', type: 'warning'
    })
    await wcApi.deleteTeam(row.id)
    ElMessage.success('删除成功')
    await loadTeams()
  } catch (e: any) {
    if (e !== 'cancel') ElMessage.error(e.message || '删除失败')
  }
}

onMounted(() => {
  loadGroups()
  loadMatches()
  if (isAdmin.value) loadTeams()
})
</script>

<style scoped>
.worldcup-page {
  max-width: 1200px;
  margin: 0 auto;
}

.groups-grid {
  display: grid;
  grid-template-columns: repeat(4, 1fr);
  gap: 16px;
  margin-top: 16px;
}

@media (max-width: 1100px) {
  .groups-grid { grid-template-columns: repeat(3, 1fr); }
}
@media (max-width: 800px) {
  .groups-grid { grid-template-columns: repeat(2, 1fr); }
}
@media (max-width: 500px) {
  .groups-grid { grid-template-columns: 1fr; }
}

.group-card {
  min-width: 0;
}

.group-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.group-label {
  font-weight: bold;
  font-size: 16px;
}

.team-cell {
  display: flex;
  align-items: center;
  gap: 6px;
}

.team-flag {
  font-size: 18px;
}

.team-name {
  font-size: 13px;
}

.points {
  font-weight: bold;
  color: #409eff;
}

.qualify-pos {
  color: #67c23a;
  font-weight: bold;
}

.goal-positive { color: #67c23a; }
.goal-negative { color: #f56c6c; }

/* 概率条 */
.prob-bar {
  display: flex;
  height: 24px;
  border-radius: 4px;
  overflow: hidden;
  font-size: 11px;
  line-height: 24px;
  text-align: center;
  color: #fff;
}

.prob-segment.home { background: #409eff; }
.prob-segment.draw { background: #909399; }
.prob-segment.away { background: #f56c6c; }

.no-pred {
  color: #c0c4cc;
  font-size: 12px;
}

.reasoning-box {
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 4px;
  color: #606266;
  line-height: 1.6;
}

.matches-toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
  align-items: center;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

@media (max-width: 768px) {
  .matches-toolbar {
    flex-wrap: wrap;
    gap: 8px;
  }
}
</style>
