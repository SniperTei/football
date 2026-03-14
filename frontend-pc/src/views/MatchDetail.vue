<template>
  <div class="match-detail-page">
    <el-page-header @back="$router.back()" content="比赛详情" />

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
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { ElMessage } from 'element-plus'
import {
  getMatchDetail,
  getMatchPlayerStats,
  getTeamAttendanceRates,
  type Match,
  type MatchPlayer,
  type AttendanceRate
} from '@/api/matches'

const route = useRoute()
const loading = ref(false)
const loadingStats = ref(false)
const match = ref<Match | null>(null)
const playerStats = ref<MatchPlayer[]>([])
const attendanceRates = ref<Map<number, AttendanceRate>>(new Map())
const activeTab = ref('home')

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
