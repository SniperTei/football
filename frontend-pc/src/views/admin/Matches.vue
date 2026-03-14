<template>
  <div class="matches-admin">
    <div class="header">
      <h2>比赛管理</h2>
      <el-button type="primary" @click="showCreateDialog">
        <el-icon><Plus /></el-icon>
        添加比赛
      </el-button>
    </div>

    <!-- 比赛列表 -->
    <el-table :data="matches" stripe v-loading="loading">
      <el-table-column prop="match_date" label="日期" width="180">
        <template #default="{ row }">
          {{ formatDate(row.match_date) }}
        </template>
      </el-table-column>
      <el-table-column label="对阵" width="200">
        <template #default="{ row }">
          <span class="match-teams">
            {{ row.home_team_name }}
            <span v-if="row.home_score !== null && row.home_score !== undefined">
              {{ row.home_score }}
            </span>
            vs
            <span v-if="row.away_score !== null && row.away_score !== undefined">
              {{ row.away_score }}
            </span>
            {{ row.away_team_name }}
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="match_type" label="类型" width="100">
        <template #default="{ row }">
          {{ getMatchTypeText(row.match_type) }}
        </template>
      </el-table-column>
      <el-table-column prop="venue" label="场地" />
      <el-table-column prop="status" label="状态" width="100">
        <template #default="{ row }">
          <el-tag :type="getStatusType(row.status)">
            {{ getStatusText(row.status) }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="操作" width="200" fixed="right">
        <template #default="{ row }">
          <el-button link type="primary" size="small" @click="showPlayerStats(row)">
            球员统计
          </el-button>
          <el-button link type="primary" size="small" @click="showEditDialog(row)">
            编辑
          </el-button>
          <el-popconfirm
            title="确定删除这场比赛吗？"
            @confirm="handleDelete(row.id)"
          >
            <template #reference>
              <el-button link type="danger" size="small">删除</el-button>
            </template>
          </el-popconfirm>
        </template>
      </el-table-column>
    </el-table>

    <!-- 创建/编辑比赛对话框 -->
    <el-dialog
      v-model="dialogVisible"
      :title="dialogMode === 'create' ? '添加比赛' : '编辑比赛'"
      width="600px"
    >
      <el-form :model="formData" :rules="formRules" ref="formRef" label-width="100px">
        <el-form-item label="客队名称" prop="away_team_name">
          <el-input
            v-model="formData.away_team_name"
            placeholder="请输入客队名称"
            :disabled="dialogMode === 'edit'"
          />
          <div class="form-tip">
            主队自动使用您的球队
          </div>
        </el-form-item>

        <el-form-item label="比赛类型" prop="match_type">
          <el-select v-model="formData.match_type" placeholder="请选择比赛类型">
            <el-option label="友谊赛" value="friendly" />
            <el-option label="联赛" value="league" />
            <el-option label="杯赛" value="cup" />
            <el-option label="训练" value="training" />
          </el-select>
        </el-form-item>

        <el-form-item label="比赛时间" prop="match_date">
          <el-date-picker
            v-model="formData.match_date"
            type="datetime"
            placeholder="选择日期时间"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DDTHH:mm:ss[Z]"
            :disabled-date="disabledDate"
          />
        </el-form-item>

        <el-form-item label="场地">
          <el-input v-model="formData.venue" placeholder="请输入比赛场地" />
        </el-form-item>

        <el-form-item label="比分">
          <div class="score-inputs">
            <el-input-number
              v-model="formData.home_score"
              :min="0"
              placeholder="主队得分"
              controls-position="right"
            />
            <span class="score-separator">:</span>
            <el-input-number
              v-model="formData.away_score"
              :min="0"
              placeholder="客队得分"
              controls-position="right"
            />
          </div>
        </el-form-item>

        <el-form-item label="出场球员" v-if="dialogMode === 'create'">
          <el-select
            v-model="formData.player_ids"
            multiple
            filterable
            placeholder="请选择出场球员（可输入搜索）"
            style="width: 100%"
            @change="onSelectedPlayersChange"
          >
            <el-option
              v-for="player in teamPlayers"
              :key="player.id"
              :label="`${player.name} (#${player.jersey_number || '无号码'})`"
              :value="player.id"
            />
          </el-select>
          <div class="form-tip">
            选择将在本场比赛中出场的球员（可多选，可输入姓名或号码搜索）
          </div>
        </el-form-item>

        <el-form-item label="球员统计" v-if="dialogMode === 'create' && selectedPlayersStats.length > 0">
          <div class="form-tip" style="margin-bottom: 12px">
            为出场球员录入进球和助攻数据
          </div>
          <el-table :data="selectedPlayersStats" border style="width: 100%" max-height="250">
            <el-table-column label="球员" width="150">
              <template #default="{ row }">
                {{ row.player_name }}
                <span style="color: #909399; font-size: 12px">
                  #{{ row.jersey_number || '无号码' }}
                </span>
              </template>
            </el-table-column>
            <el-table-column label="进球" width="100" align="center">
              <template #default="{ row }">
                <el-input-number
                  v-model="row.goals"
                  :min="0"
                  controls-position="right"
                  size="small"
                />
              </template>
            </el-table-column>
            <el-table-column label="助攻" width="100" align="center">
              <template #default="{ row }">
                <el-input-number
                  v-model="row.assists"
                  :min="0"
                  controls-position="right"
                  size="small"
                />
              </template>
            </el-table-column>
          </el-table>
        </el-form-item>

        <el-form-item label="备注">
          <el-input
            v-model="formData.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="dialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleSubmit" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>

    <!-- 球员统计对话框 -->
    <el-dialog v-model="playerStatsVisible" title="球员统计" width="800px">
      <el-table :data="playerStats" stripe v-loading="loadingStats">
        <el-table-column prop="player_name" label="球员名称" />
        <el-table-column prop="jersey_number" label="号码" width="80" />
        <el-table-column prop="position" label="位置" width="100" />
        <el-table-column label="出场" width="80">
          <template #default="{ row }">
            <el-tag :type="row.played ? 'success' : 'info'" size="small">
              {{ row.played ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="goals" label="进球" width="80" />
        <el-table-column prop="assists" label="助攻" width="80" />
        <el-table-column label="操作" width="120">
          <template #default="{ row }">
            <el-button link type="primary" size="small" @click="showEditPlayerStats(row)">
              编辑
            </el-button>
          </template>
        </el-table-column>
      </el-table>
    </el-dialog>

    <!-- 编辑球员统计对话框 -->
    <el-dialog v-model="editPlayerStatsVisible" title="编辑球员统计" width="500px">
      <el-form :model="playerStatsData" label-width="100px">
        <el-form-item label="出场">
          <el-switch v-model="playerStatsData.played" />
        </el-form-item>
        <el-form-item label="进球数">
          <el-input-number v-model="playerStatsData.goals" :min="0" />
        </el-form-item>
        <el-form-item label="助攻数">
          <el-input-number v-model="playerStatsData.assists" :min="0" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editPlayerStatsVisible = false">取消</el-button>
        <el-button type="primary" @click="handleUpdatePlayerStats" :loading="submittingStats">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, reactive } from 'vue'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Plus } from '@element-plus/icons-vue'
import {
  getTeamMatches,
  createMatch,
  updateMatch,
  deleteMatch,
  getMatchPlayerStats,
  updateMatchPlayerStats,
  type Match,
  type MatchListItem,
  type CreateMatchRequest,
  type UpdateMatchRequest,
  type MatchPlayer,
  type UpdateMatchPlayerRequest
} from '@/api/matches'
import { playersApi, type Player } from '@/api/players'

const matches = ref<MatchListItem[]>([])
const loading = ref(false)
const dialogVisible = ref(false)
const dialogMode = ref<'create' | 'edit'>('create')
const formRef = ref<FormInstance>()
const teamPlayers = ref<Player[]>([])  // 球队球员列表

// 球员统计数据
interface PlayerStatData {
  player_id: number
  player_name: string
  jersey_number?: number
  played: boolean
  goals: number
  assists: number
}

// 表单数据
const formData = ref<CreateMatchRequest & { id?: number; player_stats?: PlayerStatData[]; player_ids?: number[] }>({
  away_team_name: '',
  match_type: 'friendly',
  match_date: '',
  venue: '',
  home_score: undefined,
  away_score: undefined,
  notes: '',
  player_ids: [],  // 出场球员ID列表
  player_stats: []  // 球员统计列表
})

// 选中的球员统计（用于表格显示）
const selectedPlayersStats = computed(() => {
  if (!formData.value.player_ids || formData.value.player_ids.length === 0) {
    return []
  }

  // 返回选中的球员数据
  return (formData.value.player_stats || []).filter(p =>
    formData.value.player_ids?.includes(p.player_id)
  )
})

const formRules: FormRules = {
  away_team_name: [{ required: true, message: '请输入客队名称', trigger: 'blur' }],
  match_type: [{ required: true, message: '请选择比赛类型', trigger: 'change' }],
  match_date: [{ required: true, message: '请选择比赛时间', trigger: 'change' }]
}

const submitting = ref(false)

// 球员统计相关
const playerStatsVisible = ref(false)
const playerStats = ref<MatchPlayer[]>([])
const loadingStats = ref(false)
const currentMatchId = ref<number>()

const editPlayerStatsVisible = ref(false)
const playerStatsData = ref<UpdateMatchPlayerRequest>({
  played: false,
  goals: 0,
  assists: 0
})
const currentPlayerId = ref<number>()
const submittingStats = ref(false)

// 从 localStorage 获取用户的球队 ID
const getUserTeamId = () => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    const user = JSON.parse(userStr)
    return user.my_team_id
  }
  return null
}

// 加载比赛列表
const loadMatches = async () => {
  const teamId = getUserTeamId()
  if (!teamId) {
    ElMessage.warning('您还没有球队，请先创建球队')
    return
  }

  loading.value = true
  try {
    const response = await getTeamMatches(teamId)
    // 响应拦截器已经提取了 data 字段
    const data = response.data || response
    matches.value = data.list || []
  } catch (error) {
    console.error('加载比赛列表失败:', error)
  } finally {
    loading.value = false
  }
}

// 显示创建对话框
const showCreateDialog = async () => {
  const teamId = getUserTeamId()
  if (!teamId) {
    ElMessage.warning('您还没有球队，请先创建球队')
    return
  }

  // 加载球队球员
  try {
    const response = await playersApi.getByTeam(teamId)
    const data = response.data || response
    teamPlayers.value = data.list || []
  } catch (error) {
    console.error('加载球员列表失败:', error)
    ElMessage.error('加载球员列表失败')
    return
  }

  // 初始化球员统计数据
  const playerStats = teamPlayers.value.map(player => ({
    player_id: player.id,
    player_name: player.name,
    jersey_number: player.jersey_number,
    played: false,
    goals: 0,
    assists: 0
  }))

  dialogMode.value = 'create'
  formData.value = {
    away_team_name: '',
    match_type: 'friendly',
    match_date: '',
    venue: '',
    home_score: undefined,
    away_score: undefined,
    notes: '',
    player_ids: [],
    player_stats: playerStats
  }
  dialogVisible.value = true
}

// 当选择的球员改变时
const onSelectedPlayersChange = () => {
  // 这里不需要做特殊处理，selectedPlayersStats 会自动更新
}

// 显示编辑对话框
const showEditDialog = (match: MatchListItem) => {
  dialogMode.value = 'edit'
  formData.value = {
    id: match.id,
    away_team_name: match.away_team_name,
    match_type: match.match_type,
    match_date: match.match_date,
    venue: match.venue || '',
    home_score: match.home_score,
    away_score: match.away_score,
    notes: '',
    player_stats: []  // 编辑时不修改球员统计信息
  }
  dialogVisible.value = true
}

// 禁用未来日期
const disabledDate = (time: Date) => {
  return time.getTime() > Date.now()
}

// 提交表单
const handleSubmit = async () => {
  if (!formRef.value) return

  await formRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      if (dialogMode.value === 'create') {
        // 根据选中的球员ID，提取他们的统计数据
        const playerStats = (formData.value.player_ids || []).map(playerId => {
          const playerStat = (formData.value.player_stats || []).find(p => p.player_id === playerId)
          return {
            player_id: playerId,
            played: true,
            goals: playerStat?.goals || 0,
            assists: playerStat?.assists || 0
          }
        })

        const createData = {
          ...formData.value,
          player_stats: playerStats
        }
        await createMatch(createData as CreateMatchRequest)
        ElMessage.success('创建成功')
      } else {
        const { id, player_stats, player_ids, ...updateData } = formData.value
        await updateMatch(id!, updateData as UpdateMatchRequest)
        ElMessage.success('更新成功')
      }
      dialogVisible.value = false
      loadMatches()
    } catch (error) {
      console.error('提交失败:', error)
    } finally {
      submitting.value = false
    }
  })
}

// 删除比赛
const handleDelete = async (id: number) => {
  try {
    await deleteMatch(id)
    ElMessage.success('删除成功')
    loadMatches()
  } catch (error) {
    console.error('删除失败:', error)
  }
}

// 显示球员统计
const showPlayerStats = async (match: MatchListItem) => {
  currentMatchId.value = match.id
  playerStatsVisible.value = true
  loadingStats.value = true
  try {
    const response = await getMatchPlayerStats(match.id)
    // 响应拦截器已经提取了 data 字段
    const data = response.data || response
    playerStats.value = data.list || []
  } catch (error) {
    console.error('加载球员统计失败:', error)
  } finally {
    loadingStats.value = false
  }
}

// 显示编辑球员统计
const showEditPlayerStats = (player: MatchPlayer) => {
  currentPlayerId.value = player.player_id
  playerStatsData.value = {
    played: player.played,
    goals: player.goals,
    assists: player.assists
  }
  editPlayerStatsVisible.value = true
}

// 更新球员统计
const handleUpdatePlayerStats = async () => {
  if (!currentMatchId.value || !currentPlayerId.value) return

  submittingStats.value = true
  try {
    await updateMatchPlayerStats(
      currentMatchId.value,
      currentPlayerId.value,
      playerStatsData.value
    )
    ElMessage.success('更新成功')
    editPlayerStatsVisible.value = false
    // 重新加载球员统计
    if (currentMatchId.value) {
      const response = await getMatchPlayerStats(currentMatchId.value)
      // 响应拦截器已经提取了 data 字段
      const data = response.data || response
      playerStats.value = data.list || []
    }
  } catch (error) {
    console.error('更新球员统计失败:', error)
  } finally {
    submittingStats.value = false
  }
}

// 格式化日期
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  return date.toLocaleString('zh-CN', {
    year: 'numeric',
    month: '2-digit',
    day: '2-digit',
    hour: '2-digit',
    minute: '2-digit'
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
  const map: Record<string, any> = {
    scheduled: 'info',
    in_progress: 'warning',
    completed: 'success',
    cancelled: 'danger'
  }
  return map[status] || ''
}

onMounted(() => {
  loadMatches()
})
</script>

<style scoped>
.matches-admin {
  padding: 20px;
}

.header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.match-teams {
  font-weight: 500;
}

.form-tip {
  font-size: 12px;
  color: #909399;
  margin-top: 4px;
}

.score-inputs {
  display: flex;
  align-items: center;
  gap: 10px;
}

.score-separator {
  font-size: 18px;
  font-weight: bold;
}
</style>
