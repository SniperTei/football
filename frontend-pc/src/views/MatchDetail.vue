<template>
  <div class="match-detail-page">
    <div class="page-header">
      <el-page-header @back="$router.back()" content="比赛详情" />
      <el-button
        v-if="canEditMatch"
        type="primary"
        @click="showEditDialog"
        :icon="Edit"
      >
        编辑比赛
      </el-button>
    </div>

    <el-card v-loading="loading" style="margin-top: 20px">
      <!-- 比赛基本信息 -->
      <div v-if="match" class="match-info">
        <!-- 计分板 -->
        <div class="score-board">
          <div class="team home">
            <div class="team-name">{{ match.home_team_name }}</div>
            <div class="team-score" v-if="match.home_score !== null && match.home_score !== undefined">
              {{ match.home_score }}
            </div>
            <div class="team-score" v-else>-</div>
          </div>

          <div class="versus">VS</div>

          <div class="team away">
            <div class="team-name">{{ match.away_team_name }}</div>
            <div class="team-score" v-if="match.away_score !== null && match.away_score !== undefined">
              {{ match.away_score }}
            </div>
            <div class="team-score" v-else>-</div>
          </div>
        </div>

        <!-- 进球详情 -->
        <div v-if="scorers.length > 0 || assistants.length > 0" class="goals-summary">
          <!-- 主队进球详情 -->
          <div v-if="homeTeamScorers.length > 0" class="team-goals home">
            <div class="goals-title">⚽ 进球</div>
            <div class="goals-list">
              <div v-for="scorer in homeTeamScorers" :key="scorer.player_id" class="goal-item">
                <span class="player-name">{{ scorer.player_name }}</span>
                <span v-if="scorer.assists > 0" class="assist-info">
                  (助攻: {{ getAssistNames(scorer) }})
                </span>
                <el-tag size="small" type="success" class="goal-count">
                  {{ scorer.goals }} 球
                </el-tag>
              </div>
            </div>
          </div>

          <!-- 客队进球详情 -->
          <div v-if="awayTeamScorers.length > 0" class="team-goals away">
            <div class="goals-title">⚽ 进球</div>
            <div class="goals-list">
              <div v-for="scorer in awayTeamScorers" :key="scorer.player_id" class="goal-item">
                <span class="player-name">{{ scorer.player_name }}</span>
                <span v-if="scorer.assists > 0" class="assist-info">
                  (助攻: {{ getAssistNames(scorer) }})
                </span>
                <el-tag size="small" type="success" class="goal-count">
                  {{ scorer.goals }} 球
                </el-tag>
              </div>
            </div>
          </div>
        </div>

        <!-- 助攻榜（单独展示） -->
        <div v-if="assistants.length > 0" class="assists-summary">
          <div class="assists-title">🎯 本场助攻</div>
          <div class="assists-list">
            <div v-for="assistant in assistants" :key="assistant.player_id" class="assist-item">
              <span class="player-name">{{ assistant.player_name }}</span>
              <span class="player-number">#{{ assistant.jersey_number || '?' }}</span>
              <el-tag size="small" type="warning" class="assist-count">
                {{ assistant.assists }} 次助攻
              </el-tag>
            </div>
          </div>
        </div>

        <!-- 比赛信息 -->
        <el-descriptions :column="2" border class="match-descriptions">
          <el-descriptions-item label="比赛时间">
            {{ formatDateTime(match.match_date) }}
          </el-descriptions-item>
          <el-descriptions-item label="比赛类型">
            <el-tag>{{ getMatchTypeText(match.match_type) }}</el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="比赛状态">
            <el-tag :type="getStatusType(match.status)">
              {{ getStatusText(match.status) }}
            </el-tag>
          </el-descriptions-item>
          <el-descriptions-item label="比赛场地">
            {{ match.venue || '-' }}
          </el-descriptions-item>
          <el-descriptions-item label="主队ID">
            {{ match.home_team_id }}
          </el-descriptions-item>
          <el-descriptions-item label="客队ID">
            {{ match.away_team_id }}
          </el-descriptions-item>
          <el-descriptions-item label="创建时间">
            {{ formatDateTime(match.created_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="更新时间">
            {{ formatDateTime(match.updated_at) }}
          </el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">
            {{ match.notes || '-' }}
          </el-descriptions-item>
        </el-descriptions>

        <!-- 球员统计 -->
        <el-divider content-position="left">
          <span class="divider-title">📊 球员统计</span>
        </el-divider>

        <el-tabs v-model="activeTab" class="stats-tabs">
          <!-- 主队统计 -->
          <el-tab-pane :label="match.home_team_name" name="home">
            <el-table
              :data="homeTeamStats"
              stripe
              v-loading="loadingStats"
              empty-text="暂无数据"
            >
              <el-table-column prop="player_name" label="球员名称" width="150">
                <template #default="{ row }">
                  {{ getPlayerName(row) }}
                </template>
              </el-table-column>
              <el-table-column prop="jersey_number" label="号码" width="80" align="center" />
              <el-table-column prop="position" label="位置" width="100" />
              <el-table-column label="是否出场" width="100" align="center">
                <template #default="{ row }">
                  <el-tag :type="row.played ? 'success' : 'info'" size="small">
                    {{ row.played ? '出场' : '未出场' }}
                  </el-tag>
                </template>
              </el-table-column>
              <el-table-column prop="goals" label="进球" width="80" align="center">
                <template #default="{ row }">
                  <span :class="{ 'has-goals': row.goals > 0 }">{{ row.goals }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="assists" label="助攻" width="80" align="center">
                <template #default="{ row }">
                  <span :class="{ 'has-assists': row.assists > 0 }">{{ row.assists }}</span>
                </template>
              </el-table-column>
              <el-table-column label="出勤率" width="100" align="center">
                <template #default="{ row }">
                  <span :class="{ 'high-attendance': hasHighAttendance(row.player_id) }">
                    {{ getPlayerAttendanceRate(row.player_id) }}
                  </span>
                </template>
              </el-table-column>
            </el-table>
          </el-tab-pane>

          <!-- 客队统计 -->
          <el-tab-pane :label="match.away_team_name" name="away">
            <el-empty description="客队统计暂不可见" />
          </el-tab-pane>
        </el-tabs>
      </div>
    </el-card>

    <!-- 编辑比赛对话框 -->
    <el-dialog
      v-model="editDialogVisible"
      title="编辑比赛"
      width="90%"
      :close-on-click-modal="false"
    >
      <el-tabs v-model="editActiveTab">
        <!-- 比赛信息 -->
        <el-tab-pane label="比赛信息" name="match">
          <el-form :model="editForm" :rules="editRules" ref="editFormRef" label-width="100px">
            <el-form-item label="主队比分" prop="home_score">
              <el-input-number v-model="editForm.home_score" :min="0" />
            </el-form-item>
            <el-form-item label="客队比分" prop="away_score">
              <el-input-number v-model="editForm.away_score" :min="0" />
            </el-form-item>
            <el-form-item label="比赛时间" prop="match_date">
              <el-date-picker
                v-model="editForm.match_date"
                type="datetime"
                format="YYYY-MM-DD HH:mm"
                value-format="YYYY-MM-DDTHH:mm:ss[Z]"
                :disabled-date="disabledDate"
              />
            </el-form-item>
            <el-form-item label="比赛场地" prop="venue">
              <el-input v-model="editForm.venue" placeholder="请输入比赛场地" />
            </el-form-item>
            <el-form-item label="比赛类型" prop="match_type">
              <el-select v-model="editForm.match_type">
                <el-option label="友谊赛" value="friendly" />
                <el-option label="联赛" value="league" />
                <el-option label="杯赛" value="cup" />
                <el-option label="训练" value="training" />
              </el-select>
            </el-form-item>
            <el-form-item label="比赛状态" prop="status">
              <el-select v-model="editForm.status">
                <el-option label="未开始" value="scheduled" />
                <el-option label="进行中" value="in_progress" />
                <el-option label="已完成" value="completed" />
                <el-option label="已取消" value="cancelled" />
              </el-select>
            </el-form-item>
            <el-form-item label="备注" prop="notes">
              <el-input v-model="editForm.notes" type="textarea" :rows="3" />
            </el-form-item>
          </el-form>
        </el-tab-pane>

        <!-- 球员统计 -->
        <el-tab-pane label="球员统计" name="players">
          <!-- 出场球员选择 -->
          <div style="margin-bottom: 20px">
            <label style="display: block; margin-bottom: 8px; font-weight: 500">出场球员</label>
            <el-select
              v-model="selectedPlayerIds"
              multiple
              filterable
              placeholder="选择将在本场比赛中出场的球员（可多选）"
              style="width: 100%"
              @change="onSelectedPlayersChange"
            >
              <el-option
                v-for="player in allTeamPlayers"
                :key="player.id"
                :label="`${player.name} #${player.jersey_number || '无号码'}`"
                :value="player.id"
              >
                <span style="float: left">{{ player.name }}</span>
                <span style="float: right; color: #8492a6; font-size: 13px">
                  #{{ player.jersey_number || '无号码' }}
                </span>
              </el-option>
            </el-select>
            <div style="color: #909399; font-size: 12px; margin-top: 4px">
              选择将在本场比赛中出场的球员（可多选，可输入姓名或号码搜索）
            </div>
          </div>

          <!-- 球员统计表格 -->
          <div v-if="selectedPlayersStats.length > 0">
            <div style="margin-bottom: 12px; font-weight: 500">球员统计</div>
            <div style="color: #909399; font-size: 12px; margin-bottom: 12px">
              为出场球员录入进球和助攻数据
            </div>
            <el-table :data="selectedPlayersStats" border max-height="350">
              <el-table-column label="球员" width="150">
                <template #default="{ row }">
                  {{ row.player_name }}
                  <span style="color: #909399; font-size: 12px">
                    #{{ row.jersey_number || '无号码' }}
                  </span>
                </template>
              </el-table-column>
              <el-table-column label="进球" width="120" align="center">
                <template #default="{ row }">
                  <el-input-number
                    v-model="row.goals"
                    :min="0"
                    controls-position="right"
                    size="small"
                  />
                </template>
              </el-table-column>
              <el-table-column label="助攻" width="120" align="center">
                <template #default="{ row }">
                  <el-input-number
                    v-model="row.assists"
                    :min="0"
                    controls-position="right"
                    size="small"
                  />
                </template>
              </el-table-column>
              <el-table-column label="位置" width="100">
                <template #default="{ row }">
                  {{ row.position || '-' }}
                </template>
              </el-table-column>
            </el-table>
          </div>

          <el-empty v-else description="请先选择出场球员" />
        </el-tab-pane>
      </el-tabs>

      <template #footer>
        <el-button @click="editDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSave" :loading="saving">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage, type FormInstance } from 'element-plus'
import { Edit } from '@element-plus/icons-vue'
import { useAuthStore } from '@/stores/auth'
import {
  getMatchDetail,
  getMatchPlayerStats,
  getTeamAttendanceRates,
  updateMatch,
  updateMatchPlayerStats,
  type Match,
  type MatchPlayer,
  type AttendanceRate
} from '@/api/matches'
import { playersApi, type Player } from '@/api/players'

const route = useRoute()
const authStore = useAuthStore()
const loading = ref(false)
const loadingStats = ref(false)
const match = ref<Match | null>(null)
const playerStats = ref<MatchPlayer[]>([])
const attendanceRates = ref<Map<number, AttendanceRate>>(new Map())
const activeTab = ref('home')

// 编辑相关
const editDialogVisible = ref(false)
const editActiveTab = ref('match')
const saving = ref(false)
const editFormRef = ref<FormInstance>()

// 编辑表单
const editForm = reactive({
  home_score: undefined as number | undefined,
  away_score: undefined as number | undefined,
  match_date: '',
  venue: '',
  match_type: '',
  status: '',
  notes: ''
})

const editRules = {
  home_score: [{ required: true, message: '请输入主队比分', trigger: 'blur' }],
  away_score: [{ required: true, message: '请输入客队比分', trigger: 'blur' }]
}

// 球队所有球员
const allTeamPlayers = ref<Player[]>([])

// 选中的球员ID列表
const selectedPlayerIds = ref<number[]>([])

// 球员统计数据接口
interface PlayerStatData {
  player_id: number
  player_name: string
  jersey_number?: number
  position?: string
  played: boolean
  goals: number
  assists: number
}

// 所有球员的统计数据
const allPlayerStats = ref<PlayerStatData[]>([])

// 选中的球员统计（用于表格显示）
const selectedPlayersStats = computed(() => {
  if (selectedPlayerIds.value.length === 0) {
    return []
  }
  // 返回选中的球员数据
  return allPlayerStats.value.filter(p =>
    selectedPlayerIds.value.includes(p.player_id)
  )
})

// 判断是否可以编辑比赛（管理员或主队拥有者）
const canEditMatch = computed(() => {
  if (!authStore.isAuthenticated || !match.value) return false
  // 管理员可以编辑
  if (authStore.isAdmin) return true
  // 主队拥有者可以编辑
  return authStore.user?.my_team_id === match.value.home_team_id
})

// 获取比赛详情
const loadMatchDetail = async () => {
  const matchId = Number(route.params.id)
  if (isNaN(matchId)) {
    ElMessage.error('无效的比赛ID')
    return
  }

  loading.value = true
  try {
    const response = await getMatchDetail(matchId)
    // 响应拦截器已经提取了 data 字段，但为了保险起见再检查一次
    match.value = response.data || response

    console.log('比赛详情数据:', match.value)

    // 加载完比赛详情后，加载球员统计
    loadPlayerStats(matchId)
    // 加载主队出勤率
    if (match.value?.home_team_id) {
      loadAttendanceRates(match.value.home_team_id)
    }
  } catch (error: any) {
    console.error('加载比赛详情失败:', error)
    ElMessage.error(error.response?.data?.msg || error.message || '加载比赛详情失败')
  } finally {
    loading.value = false
  }
}

// 获取球员统计
const loadPlayerStats = async (matchId: number) => {
  loadingStats.value = true
  try {
    const response = await getMatchPlayerStats(matchId)
    const data = response.data || response
    playerStats.value = data.list || []
  } catch (error: any) {
    console.error('加载球员统计失败:', error)
    ElMessage.error('加载球员统计失败')
  } finally {
    loadingStats.value = false
  }
}

// 获取球队出勤率
const loadAttendanceRates = async (teamId: number) => {
  try {
    const response = await getTeamAttendanceRates(teamId)
    const data = response.data || response
    const ratesMap = new Map<number, AttendanceRate>()
    data.list?.forEach((rate: AttendanceRate) => {
      ratesMap.set(rate.player_id, rate)
    })
    attendanceRates.value = ratesMap
  } catch (error: any) {
    console.error('加载出勤率失败:', error)
  }
}

// 主队统计数据
const homeTeamStats = computed(() => {
  if (!match.value) return []
  return playerStats.value.filter(p => p.team_id === match.value!.home_team_id)
})

// 获取所有进球者（有进球的球员）
const scorers = computed(() => {
  return playerStats.value.filter(p => p.goals > 0)
})

// 主队进球者
const homeTeamScorers = computed(() => {
  if (!match.value) return []
  return playerStats.value.filter(p =>
    p.team_id === match.value!.home_team_id && p.goals > 0
  )
})

// 客队进球者
const awayTeamScorers = computed(() => {
  if (!match.value) return []
  return playerStats.value.filter(p =>
    p.team_id === match.value!.away_team_id && p.goals > 0
  )
})

// 获取所有助攻者（有助攻的球员）
const assistants = computed(() => {
  return playerStats.value
    .filter(p => p.assists > 0)
    .sort((a, b) => b.assists - a.assists) // 按助攻数降序排序
})

// 获取助攻者姓名列表（用于显示在进球者旁边）
const getAssistNames = (scorer: MatchPlayer) => {
  // 这里简化处理，实际上无法知道具体哪个助攻对应哪个进球
  // 所以只显示该球员自己的助攻数，或者可以显示所有助攻者
  return scorer.assists > 0 ? `${scorer.assists}次` : ''
}

// 获取球员名称
const getPlayerName = (player: MatchPlayer) => {
  return player.player_name || `球员 #${player.player_id}`
}

// 获取球员出勤率
const getPlayerAttendanceRate = (playerId: number) => {
  const rate = attendanceRates.value.get(playerId)
  if (!rate) return '-'
  return `${rate.attendance_rate.toFixed(1)}%`
}

// 检查是否高出勤率（>= 80%）
const hasHighAttendance = (playerId: number) => {
  const rate = attendanceRates.value.get(playerId)
  if (!rate) return false
  return rate.attendance_rate >= 80
}

// 格式化日期时间
const formatDateTime = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit',
    weekday: 'long'
  })
}

// 获取比赛类型文本
const getMatchTypeText = (type: string) => {
  const map: Record<string, string> = {
    friendly: '友谊赛',
    league: '联赛',
    cup: '杯赛',
    training: '训练'
  }
  return map[type] || type
}

// 获取状态文本
const getStatusText = (status: string) => {
  const map: Record<string, string> = {
    scheduled: '未开始',
    in_progress: '进行中',
    completed: '已完成',
    cancelled: '已取消'
  }
  return map[status] || status
}

// 获取状态标签类型
const getStatusType = (status: string) => {
  const map: Record<string, string> = {
    scheduled: 'info',
    in_progress: 'warning',
    completed: 'success',
    cancelled: 'danger'
  }
  return map[status] || 'info'
}

// 禁用未来日期
const disabledDate = (time: Date) => {
  return time.getTime() > Date.now()
}

// 显示编辑对话框
const showEditDialog = async () => {
  if (!match.value) return

  // 填充比赛信息
  editForm.home_score = match.value.home_score ?? undefined
  editForm.away_score = match.value.away_score ?? undefined
  editForm.match_date = match.value.match_date
  editForm.venue = match.value.venue || ''
  editForm.match_type = match.value.match_type
  editForm.status = match.value.status
  editForm.notes = match.value.notes || ''

  // 加载球队所有球员
  try {
    const response = await playersApi.getByTeam(match.value.home_team_id)
    const data = response.data || response
    allTeamPlayers.value = data.list || []

    // 初始化所有球员的统计数据
    allPlayerStats.value = allTeamPlayers.value.map(player => {
      // 查找现有的球员统计
      const existingStat = playerStats.value.find(p => p.player_id === player.id)
      return {
        player_id: player.id,
        player_name: player.name,
        jersey_number: player.jersey_number,
        position: player.position,
        played: existingStat?.played || false,
        goals: existingStat?.goals || 0,
        assists: existingStat?.assists || 0
      }
    })

    // 设置已选中的球员ID（已出场的球员）
    selectedPlayerIds.value = allPlayerStats.value
      .filter(p => p.played)
      .map(p => p.player_id)

  } catch (error) {
    console.error('加载球队球员失败:', error)
    ElMessage.error('加载球队球员失败')
  }

  editDialogVisible.value = true
}

// 当选择的球员改变时
const onSelectedPlayersChange = () => {
  // 更新球员的 played 状态
  allPlayerStats.value.forEach(p => {
    p.played = selectedPlayerIds.value.includes(p.player_id)
  })
}

// 保存修改
const handleSave = async () => {
  if (!match.value) return

  saving.value = true
  try {
    // 1. 更新比赛信息
    const matchData = {
      home_score: editForm.home_score,
      away_score: editForm.away_score,
      match_date: editForm.match_date,
      venue: editForm.venue,
      match_type: editForm.match_type,
      status: editForm.status,
      notes: editForm.notes
    }

    await updateMatch(match.value.id, matchData)
    ElMessage.success('比赛信息更新成功')

    // 2. 更新球员统计
    const updatePromises = allPlayerStats.value.map(player =>
      updateMatchPlayerStats(match.value!.id, player.player_id, {
        played: player.played,
        goals: player.goals,
        assists: player.assists
      })
    )

    await Promise.all(updatePromises)
    ElMessage.success('球员统计更新成功')

    // 重新加载数据
    await loadMatchDetail()
    await loadPlayerStats(match.value.id)

    editDialogVisible.value = false
  } catch (error: any) {
    console.error('保存失败:', error)
    ElMessage.error(error.response?.data?.msg || error.message || '保存失败')
  } finally {
    saving.value = false
  }
}

onMounted(() => {
  loadMatchDetail()
})
</script>

<style scoped>
.match-detail-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.page-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.score-board {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 40px;
  padding: 40px 20px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  color: white;
  margin-bottom: 30px;
  box-shadow: 0 4px 20px rgba(102, 126, 234, 0.3);
}

.team {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 12px;
}

.team-name {
  font-size: 24px;
  font-weight: bold;
  text-align: center;
  word-break: break-word;
}

.team-score {
  font-size: 48px;
  font-weight: bold;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
}

.versus {
  font-size: 28px;
  font-weight: bold;
  opacity: 0.9;
  padding: 0 20px;
}

.match-descriptions {
  margin-top: 20px;
}

/* 进球详情 */
.goals-summary {
  display: flex;
  gap: 20px;
  margin-top: 30px;
  padding: 20px;
  background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
  border-radius: 12px;
}

.team-goals {
  flex: 1;
  padding: 15px;
  border-radius: 8px;
}

.team-goals.home {
  background: rgba(103, 194, 58, 0.1);
  border: 2px solid #67c23a;
}

.team-goals.away {
  background: rgba(245, 108, 108, 0.1);
  border: 2px solid #f56c6c;
}

.goals-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 12px;
  color: #303133;
}

.goals-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.goal-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: white;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.goal-item .player-name {
  font-weight: 500;
  color: #303133;
}

.goal-item .assist-info {
  font-size: 14px;
  color: #909399;
}

.goal-item .goal-count {
  margin-left: auto;
}

/* 助攻榜 */
.assists-summary {
  margin-top: 20px;
  padding: 20px;
  background: linear-gradient(135deg, #fff9e6 0%, #ffe6a7 100%);
  border-radius: 12px;
  border: 2px solid #e6a23c;
}

.assists-title {
  font-size: 18px;
  font-weight: bold;
  margin-bottom: 12px;
  color: #303133;
}

.assists-list {
  display: flex;
  flex-direction: column;
  gap: 8px;
}

.assist-item {
  display: flex;
  align-items: center;
  gap: 8px;
  padding: 8px 12px;
  background: white;
  border-radius: 6px;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.05);
}

.assist-item .player-name {
  font-weight: 500;
  color: #303133;
}

.assist-item .player-number {
  font-size: 12px;
  color: #909399;
  background: #f5f7fa;
  padding: 2px 6px;
  border-radius: 4px;
}

.assist-item .assist-count {
  margin-left: auto;
}

.divider-title {
  font-size: 18px;
  font-weight: 500;
}

.stats-tabs {
  margin-top: 20px;
}

.has-goals {
  color: #67c23a;
  font-weight: bold;
  font-size: 18px;
}

.has-assists {
  color: #409eff;
  font-weight: bold;
  font-size: 18px;
}

.high-attendance {
  color: #e6a23c;
  font-weight: bold;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .score-board {
    gap: 20px;
    padding: 30px 10px;
  }

  .team-name {
    font-size: 18px;
  }

  .team-score {
    font-size: 36px;
  }

  .versus {
    font-size: 20px;
    padding: 0 10px;
  }
}
</style>
