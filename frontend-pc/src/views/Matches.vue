<template>
  <div class="matches-page">
    <div class="header">
      <h2>比赛记录</h2>
      <el-button v-if="authStore.isAuthenticated" type="primary" @click="showCreateDialog">
        <el-icon><Plus /></el-icon>
        添加比赛
      </el-button>
    </div>

    <!-- 筛选器 -->
    <div class="filters">
      <el-select
        v-model="selectedTeamId"
        placeholder="选择球队"
        clearable
        filterable
        @change="onTeamChange"
        style="width: 200px"
      >
        <el-option
          v-for="team in allTeams"
          :key="team.id"
          :label="team.name"
          :value="team.id"
        />
      </el-select>

      <el-select
        v-model="selectedPlayerId"
        placeholder="选择球员（可选）"
        clearable
        filterable
        style="width: 200px"
        :disabled="!selectedTeamId"
      >
        <el-option
          v-for="player in teamPlayers"
          :key="player.id"
          :label="player.name"
          :value="player.id"
        />
      </el-select>

      <el-select
        v-model="daysFilter"
        placeholder="时间范围"
        style="width: 150px"
      >
        <el-option label="最近7天" :value="7" />
        <el-option label="最近30天" :value="30" />
        <el-option label="最近90天" :value="90" />
        <el-option label="全部" :value="0" />
      </el-select>

      <el-select v-model="filterType" placeholder="筛选类型" clearable>
        <el-option label="全部" value="" />
        <el-option label="友谊赛" value="friendly" />
        <el-option label="联赛" value="league" />
        <el-option label="杯赛" value="cup" />
        <el-option label="训练" value="training" />
      </el-select>

      <el-button type="primary" @click="loadMatches" :loading="loading">
        <el-icon><Search /></el-icon>
        查询
      </el-button>

      <el-button @click="resetFilters">
        <el-icon><Refresh /></el-icon>
        重置
      </el-button>
    </div>

    <!-- 比赛卡片列表 -->
    <div v-loading="loading" class="matches-list">
      <el-card
        v-for="match in filteredMatches"
        :key="match.id"
        class="match-card"
        @click="goToDetail(match.id)"
      >
        <div class="match-header">
          <span class="match-type">{{ getMatchTypeText(match.match_type) }}</span>
          <span class="match-date">{{ formatDate(match.match_date) }}</span>
        </div>

        <div class="match-content">
          <div class="team">
            <div class="team-name">{{ match.home_team_name }}</div>
            <div class="team-score" v-if="match.home_score !== null && match.home_score !== undefined">
              {{ match.home_score }}
            </div>
          </div>

          <div class="vs">VS</div>

          <div class="team">
            <div class="team-name">{{ match.away_team_name }}</div>
            <div class="team-score" v-if="match.away_score !== null && match.away_score !== undefined">
              {{ match.away_score }}
            </div>
          </div>
        </div>

        <div class="match-footer" v-if="match.venue">
          <el-icon><Location /></el-icon>
          <span>{{ match.venue }}</span>
        </div>
      </el-card>

      <el-empty v-if="!loading && filteredMatches.length === 0" description="暂无比赛记录" />
    </div>

    <!-- 创建比赛弹窗 -->
    <el-dialog v-model="createDialogVisible" title="添加比赛" width="600px">
      <el-form :model="createForm" :rules="createRules" ref="createFormRef" label-width="100px">
        <el-form-item label="客队名称" prop="away_team_name">
          <el-input
            v-model="createForm.away_team_name"
            placeholder="请输入客队名称"
          />
          <div class="form-tip">
            主队自动使用您的球队
          </div>
        </el-form-item>

        <el-form-item label="比赛类型" prop="match_type">
          <el-select v-model="createForm.match_type" placeholder="请选择比赛类型" style="width: 100%">
            <el-option label="友谊赛" value="friendly" />
            <el-option label="联赛" value="league" />
            <el-option label="杯赛" value="cup" />
            <el-option label="训练" value="training" />
          </el-select>
        </el-form-item>

        <el-form-item label="比赛时间" prop="match_date">
          <el-date-picker
            v-model="createForm.match_date"
            type="datetime"
            placeholder="选择日期时间"
            format="YYYY-MM-DD HH:mm"
            value-format="YYYY-MM-DDTHH:mm:ss[Z]"
            :disabled-date="disabledDate"
            style="width: 100%"
          />
        </el-form-item>

        <el-form-item label="场地">
          <el-input v-model="createForm.venue" placeholder="请输入比赛场地" />
        </el-form-item>

        <el-form-item label="比分">
          <div class="score-inputs">
            <el-input-number
              v-model="createForm.home_score"
              :min="0"
              placeholder="主队得分"
              controls-position="right"
            />
            <span class="score-separator">:</span>
            <el-input-number
              v-model="createForm.away_score"
              :min="0"
              placeholder="客队得分"
              controls-position="right"
            />
          </div>
        </el-form-item>

        <el-form-item label="出场球员">
          <el-select
            v-model="createForm.player_ids"
            multiple
            filterable
            placeholder="请选择出场球员（可输入搜索）"
            style="width: 100%"
            @change="onSelectedPlayersChange"
          >
            <el-option
              v-for="player in myTeamPlayers"
              :key="player.id"
              :label="`${player.name} (#${player.jersey_number || '无号码'})`"
              :value="player.id"
            />
          </el-select>
          <div class="form-tip">
            选择将在本场比赛中出场的球员（可多选，可输入姓名或号码搜索）
          </div>
        </el-form-item>

        <el-form-item label="球员统计" v-if="selectedPlayersStats.length > 0">
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
            v-model="createForm.notes"
            type="textarea"
            :rows="3"
            placeholder="请输入备注"
          />
        </el-form-item>
      </el-form>

      <template #footer>
        <el-button @click="createDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="handleCreateMatch" :loading="submitting">
          确定
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, reactive } from 'vue'
import { useRouter } from 'vue-router'
import { ElMessage, type FormInstance, type FormRules } from 'element-plus'
import { Location, Search, Refresh, Plus } from '@element-plus/icons-vue'
import { getTeamMatches, getRecentMatches, getAllRecentMatches, getAllMatches, createMatch, type MatchListItem, type CreateMatchRequest, type PlayerStatRequest } from '@/api/matches'
import { teamsApi, type Team } from '@/api/teams'
import { playersApi, type Player } from '@/api/players'
import { useAuthStore } from '@/stores/auth'

const router = useRouter()
const authStore = useAuthStore()
const matches = ref<MatchListItem[]>([])
const allTeams = ref<Team[]>([])
const teamPlayers = ref<Player[]>([])
const myTeamPlayers = ref<Player[]>([])
const loading = ref(false)

// 球员统计数据
interface PlayerStatData {
  player_id: number
  player_name: string
  jersey_number?: number
  played: boolean
  goals: number
  assists: number
}

// 创建比赛相关
const createDialogVisible = ref(false)
const createFormRef = ref<FormInstance>()
const submitting = ref(false)

const createForm = reactive<CreateMatchRequest & { player_stats?: PlayerStatData[]; player_ids?: number[] }>({
  away_team_name: '',
  match_type: 'friendly',
  match_date: '',
  venue: '',
  home_score: undefined,
  away_score: undefined,
  notes: '',
  player_ids: [],
  player_stats: []
})

// 选中的球员统计（用于表格显示）
const selectedPlayersStats = computed(() => {
  if (!createForm.player_ids || createForm.player_ids.length === 0) {
    return []
  }

  // 返回选中的球员数据
  return (createForm.player_stats || []).filter(p =>
    createForm.player_ids?.includes(p.player_id)
  )
})

const createRules: FormRules = {
  away_team_name: [{ required: true, message: '请输入客队名称', trigger: 'blur' }],
  match_type: [{ required: true, message: '请选择比赛类型', trigger: 'change' }],
  match_date: [{ required: true, message: '请选择比赛时间', trigger: 'change' }]
}

// 筛选条件
const selectedTeamId = ref<number | null>(null)
const selectedPlayerId = ref<number | null>(null)
const daysFilter = ref<number>(0) // 默认全部（0=不限制时间）
const filterType = ref('')

// 从 localStorage 获取用户的球队 ID
const getUserTeamId = () => {
  const userStr = localStorage.getItem('user')
  if (userStr) {
    const user = JSON.parse(userStr)
    return user.my_team_id
  }
  return null
}

// 过滤后的比赛列表
const filteredMatches = computed(() => {
  let result = matches.value

  if (filterType.value) {
    result = result.filter(m => m.match_type === filterType.value)
  }

  // 如果选择了球员，只包含该球员参与的比赛
  if (selectedPlayerId.value) {
    // 这里需要在后端支持按球员查询，暂时先显示所有比赛
    // TODO: 等后端添加按球员查询的接口后再实现
  }

  // 按日期倒序
  return result.sort((a, b) => {
    return new Date(b.match_date).getTime() - new Date(a.match_date).getTime()
  })
})

// 加载所有球队
const loadAllTeams = async () => {
  try {
    const response = await teamsApi.getAll()
    allTeams.value = response.list || []
  } catch (error) {
    console.error('加载球队列表失败:', error)
    ElMessage.error('加载球队列表失败')
  }
}

// 加载球队球员
const loadTeamPlayers = async (teamId: number) => {
  try {
    const response = await playersApi.getByTeam(teamId)
    teamPlayers.value = response.list || []
  } catch (error) {
    console.error('加载球员列表失败:', error)
  }
}

// 球队改变时
const onTeamChange = (teamId: number | null) => {
  selectedPlayerId.value = null // 清空球员选择
  if (teamId) {
    loadTeamPlayers(teamId)
  } else {
    teamPlayers.value = []
  }
  // 不自动加载，等待用户点击查询按钮
}

// 重置筛选条件
const resetFilters = () => {
  selectedTeamId.value = null
  selectedPlayerId.value = null
  daysFilter.value = 0 // 重置为全部
  filterType.value = ''
  teamPlayers.value = []

  loadMatches()
}

// 显示创建比赛对话框
const showCreateDialog = async () => {
  const teamId = authStore.user?.my_team_id
  if (!teamId) {
    ElMessage.warning('您还没有球队，请先创建球队')
    return
  }

  // 加载自己球队的球员
  try {
    const response = await playersApi.getByTeam(teamId)
    const data = response.data || response
    myTeamPlayers.value = data.list || []

    // 初始化球员统计数据
    const playerStats = myTeamPlayers.value.map(player => ({
      player_id: player.id,
      player_name: player.name,
      jersey_number: player.jersey_number,
      played: false,
      goals: 0,
      assists: 0
    }))
    createForm.player_stats = playerStats
  } catch (error) {
    console.error('加载球员列表失败:', error)
    ElMessage.error('加载球员列表失败')
    return
  }

  // 重置表单
  createForm.away_team_name = ''
  createForm.match_type = 'friendly'
  createForm.match_date = ''
  createForm.venue = ''
  createForm.home_score = undefined
  createForm.away_score = undefined
  createForm.notes = ''
  createForm.player_ids = []

  createDialogVisible.value = true
}

// 当选择的球员改变时
const onSelectedPlayersChange = () => {
  // 这里不需要做特殊处理，selectedPlayersStats 会自动更新
}

// 禁用未来日期
const disabledDate = (time: Date) => {
  return time.getTime() > Date.now()
}

// 创建比赛
const handleCreateMatch = async () => {
  if (!createFormRef.value) return

  await createFormRef.value.validate(async (valid) => {
    if (!valid) return

    submitting.value = true
    try {
      // 根据选中的球员ID，提取他们的统计数据
      const playerStats = (createForm.player_ids || []).map(playerId => {
        const playerStat = (createForm.player_stats || []).find(p => p.player_id === playerId)
        return {
          player_id: playerId,
          played: true,
          goals: playerStat?.goals || 0,
          assists: playerStat?.assists || 0
        }
      })

      const createData = {
        ...createForm,
        player_stats: playerStats
      }
      await createMatch(createData as CreateMatchRequest)
      ElMessage.success('创建成功')
      createDialogVisible.value = false
      loadMatches()
    } catch (error: any) {
      console.error('创建比赛失败:', error)
      ElMessage.error(error.message || '创建比赛失败')
    } finally {
      submitting.value = false
    }
  })
}

// 加载比赛列表
const loadMatches = async () => {
  loading.value = true
  try {
    let response

    // 判断是否选择了球队
    if (selectedTeamId.value) {
      // 查询指定球队的比赛
      if (daysFilter.value > 0) {
        response = await getRecentMatches(selectedTeamId.value, daysFilter.value)
      } else {
        response = await getTeamMatches(selectedTeamId.value)
      }
    } else {
      // 没有选择球队，查询所有球队的比赛
      if (daysFilter.value > 0) {
        response = await getAllRecentMatches(daysFilter.value)
      } else {
        // daysFilter = 0，查询所有比赛（不限制时间）
        response = await getAllMatches({ limit: 10000 })
      }
    }

    // 响应拦截器已经提取了 data 字段，所以 response.data 就是 { list: [...], total: ... }
    const data = response.data || response
    matches.value = data.list || []
  } catch (error: any) {
    console.error('加载比赛列表失败:', error)
    ElMessage.error(error.message || '加载比赛列表失败')
  } finally {
    loading.value = false
  }
}

// 跳转到详情页
const goToDetail = (matchId: number) => {
  router.push(`/matches/${matchId}`)
}

// 格式化日期
const formatDate = (dateStr: string) => {
  const date = new Date(dateStr)
  const now = new Date()
  const diffTime = now.getTime() - date.getTime()
  const diffDays = Math.floor(diffTime / (1000 * 60 * 60 * 24))

  if (diffDays === 0) {
    return '今天 ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } else if (diffDays === 1) {
    return '昨天 ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } else if (diffDays < 7) {
    const weekdays = ['周日', '周一', '周二', '周三', '周四', '周五', '周六']
    return weekdays[date.getDay()] + ' ' + date.toLocaleTimeString('zh-CN', { hour: '2-digit', minute: '2-digit' })
  } else {
    return date.toLocaleDateString('zh-CN', {
      month: '2-digit',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit'
    })
  }
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

onMounted(async () => {
  // 加载所有球队列表
  await loadAllTeams()

  // 不自动选择球队，让用户自己选择，或直接查询所有球队
  // 页面加载时会自动查询所有球队最近7天的比赛
  loadMatches()
})
</script>

<style scoped>
.matches-page {
  padding: 20px;
  max-width: 1200px;
  margin: 0 auto;
}

.header {
  margin-bottom: 20px;
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.filters {
  display: flex;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.matches-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(350px, 1fr));
  gap: 16px;
}

.match-card {
  cursor: pointer;
  transition: all 0.3s;
}

.match-card:hover {
  transform: translateY(-2px);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
}

.match-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
  padding-bottom: 12px;
  border-bottom: 1px solid #ebeef5;
}

.match-type {
  font-size: 14px;
  color: #606266;
}

.match-date {
  font-size: 14px;
  color: #909399;
}

.match-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px 0;
}

.team {
  flex: 1;
  text-align: center;
}

.team-name {
  font-size: 16px;
  font-weight: 500;
  margin-bottom: 8px;
  color: #303133;
}

.team-score {
  font-size: 32px;
  font-weight: bold;
  color: #409eff;
}

.vs {
  font-size: 14px;
  color: #909399;
  margin: 0 20px;
}

.match-footer {
  display: flex;
  align-items: center;
  gap: 4px;
  margin-top: 12px;
  padding-top: 12px;
  border-top: 1px solid #ebeef5;
  font-size: 14px;
  color: #909399;
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
