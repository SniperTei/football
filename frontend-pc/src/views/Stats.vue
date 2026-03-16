<template>
  <div class="stats-page">
    <div class="header">
      <h2>📊 数据统计</h2>
    </div>

    <!-- 筛选器 -->
    <div class="filters">
      <el-select
        v-model="selectedTeamId"
        placeholder="筛选球队（可选）"
        clearable
        filterable
        style="width: 200px"
        @change="loadAllStats"
      >
        <el-option
          v-for="team in teams"
          :key="team.id"
          :label="team.name"
          :value="team.id"
        />
      </el-select>

      <el-input-number
        v-model="limit"
        :min="5"
        :max="50"
        :step="5"
        controls-position="right"
        style="width: 150px"
      />
      <span style="margin-left: 8px; color: #909399">名</span>

      <el-button type="primary" @click="loadAllStats" :loading="loading">
        <el-icon><Refresh /></el-icon>
        刷新
      </el-button>
    </div>

    <!-- 统计卡片 -->
    <div class="stats-grid">
      <!-- 进球榜 -->
      <el-card class="stat-card" v-loading="loadingGoals">
        <template #header>
          <div class="card-header">
            <span class="card-title">⚽ 进球榜</span>
            <el-icon class="card-icon"><Trophy /></el-icon>
          </div>
        </template>

        <!-- 榜首数据展示 -->
        <div v-if="goalRankings.length > 0" class="top-player-highlight">
          <div class="highlight-content">
            <div class="player-info">
              <span class="player-name">{{ goalRankings[0].player_name }}</span>
              <span class="team-name">{{ goalRankings[0].team_name }}</span>
            </div>
            <div class="stat-highlight">
              <span class="stat-value">{{ goalRankings[0].total_goals }}</span>
              <span class="stat-label">球</span>
            </div>
          </div>
          <div class="highlight-subtitle">当前榜首进球数</div>
        </div>

        <el-table :data="goalRankings.slice(1)" stripe>
          <el-table-column label="排名" width="80" align="center">
            <template #default="{ row }">
              <span class="rank-badge" :class="'rank-' + getRankClass(row.rank)">{{ row.rank }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="player_name" label="球员" min-width="120" />
          <el-table-column label="号码" width="80" align="center">
            <template #default="{ row }">
              {{ row.jersey_number || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="team_name" label="球队" min-width="120" />
          <el-table-column label="进球" width="100" align="center">
            <template #default="{ row }">
              <span class="highlight-value">{{ row.total_goals }}</span>
            </template>
          </el-table-column>
        </el-table>

        <el-empty v-if="!loadingGoals && goalRankings.length === 0" description="暂无数据" />
      </el-card>

      <!-- 助攻榜 -->
      <el-card class="stat-card" v-loading="loadingAssists">
        <template #header>
          <div class="card-header">
            <span class="card-title">🎯 助攻榜</span>
            <el-icon class="card-icon"><Medal /></el-icon>
          </div>
        </template>

        <!-- 榜首数据展示 -->
        <div v-if="assistRankings.length > 0" class="top-player-highlight">
          <div class="highlight-content">
            <div class="player-info">
              <span class="player-name">{{ assistRankings[0].player_name }}</span>
              <span class="team-name">{{ assistRankings[0].team_name }}</span>
            </div>
            <div class="stat-highlight">
              <span class="stat-value">{{ assistRankings[0].total_assists }}</span>
              <span class="stat-label">次助攻</span>
            </div>
          </div>
          <div class="highlight-subtitle">当前榜首助攻数</div>
        </div>

        <el-table :data="assistRankings.slice(1)" stripe>
          <el-table-column label="排名" width="80" align="center">
            <template #default="{ row }">
              <span class="rank-badge" :class="'rank-' + getRankClass(row.rank)">{{ row.rank }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="player_name" label="球员" min-width="120" />
          <el-table-column label="号码" width="80" align="center">
            <template #default="{ row }">
              {{ row.jersey_number || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="team_name" label="球队" min-width="120" />
          <el-table-column label="助攻" width="100" align="center">
            <template #default="{ row }">
              <span class="highlight-value">{{ row.total_assists }}</span>
            </template>
          </el-table-column>
        </el-table>

        <el-empty v-if="!loadingAssists && assistRankings.length === 0" description="暂无数据" />
      </el-card>

      <!-- 出勤榜 -->
      <el-card class="stat-card" v-loading="loadingAttendance">
        <template #header>
          <div class="card-header">
            <span class="card-title">📈 出勤榜</span>
            <el-icon class="card-icon"><Calendar /></el-icon>
          </div>
        </template>

        <!-- 榜首数据展示 -->
        <div v-if="attendanceRankings.length > 0" class="top-player-highlight">
          <div class="highlight-content">
            <div class="player-info">
              <span class="player-name">{{ attendanceRankings[0].player_name }}</span>
              <span class="team-name">{{ attendanceRankings[0].team_name }}</span>
            </div>
            <div class="stat-highlight">
              <span class="stat-value">{{ attendanceRankings[0].played_matches }}</span>
              <span class="stat-label">次出勤</span>
            </div>
          </div>
          <div class="highlight-subtitle">
            出勤率 {{ attendanceRankings[0].attendance_rate }}%
          </div>
        </div>

        <el-table :data="attendanceRankings.slice(1)" stripe>
          <el-table-column label="排名" width="80" align="center">
            <template #default="{ row }">
              <span class="rank-badge" :class="'rank-' + getRankClass(row.rank)">{{ row.rank }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="player_name" label="球员" min-width="120" />
          <el-table-column label="号码" width="80" align="center">
            <template #default="{ row }">
              {{ row.jersey_number || '-' }}
            </template>
          </el-table-column>
          <el-table-column prop="team_name" label="球队" min-width="120" />
          <el-table-column label="出勤次数" width="120" align="center">
            <template #default="{ row }">
              <span class="highlight-value">{{ row.played_matches }}</span>
            </template>
          </el-table-column>
        </el-table>

        <el-empty v-if="!loadingAttendance && attendanceRankings.length === 0" description="暂无数据" />
      </el-card>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { getTopScorers, getTopAssists, getTopAttendance, type PlayerRanking } from '@/api/stats'
import { teamsApi, type Team } from '@/api/teams'
import { ElMessage } from 'element-plus'
import { Refresh, Trophy, Medal, Calendar } from '@element-plus/icons-vue'

const teams = ref<Team[]>([])
const selectedTeamId = ref<number | null>(null)
const limit = ref(10)

const goalRankings = ref<PlayerRanking[]>([])
const assistRankings = ref<PlayerRanking[]>([])
const attendanceRankings = ref<PlayerRanking[]>([])

const loading = ref(false)
const loadingGoals = ref(false)
const loadingAssists = ref(false)
const loadingAttendance = ref(false)

// 获取排名徽章的样式类
const getRankClass = (rank: number) => {
  if (rank === 1) return 'rank-1'
  if (rank === 2) return 'rank-2'
  if (rank === 3) return 'rank-3'
  return 'rank-other'
}

// 加载球队列表
const loadTeams = async () => {
  try {
    const res = await teamsApi.getAll()
    const data = res.data || res
    teams.value = data.list || []
  } catch (error) {
    console.error('加载球队列表失败:', error)
  }
}

// 加载进球榜
const loadGoalRankings = async () => {
  loadingGoals.value = true
  try {
    const params: any = { limit: limit.value }
    if (selectedTeamId.value) {
      params.team_id = selectedTeamId.value
    }

    const res = await getTopScorers(params)
    const data = res.data
    goalRankings.value = data?.list || []
  } catch (error: any) {
    console.error('加载进球榜失败:', error)
    ElMessage.error('加载进球榜失败')
  } finally {
    loadingGoals.value = false
  }
}

// 加载助攻榜
const loadAssistRankings = async () => {
  loadingAssists.value = true
  try {
    const params: any = { limit: limit.value }
    if (selectedTeamId.value) {
      params.team_id = selectedTeamId.value
    }

    const res = await getTopAssists(params)
    const data = res.data
    assistRankings.value = data?.list || []
  } catch (error: any) {
    console.error('加载助攻榜失败:', error)
    ElMessage.error('加载助攻榜失败')
  } finally {
    loadingAssists.value = false
  }
}

// 加载出勤榜
const loadAttendanceRankings = async () => {
  loadingAttendance.value = true
  try {
    const params: any = { limit: limit.value }
    if (selectedTeamId.value) {
      params.team_id = selectedTeamId.value
    }

    const res = await getTopAttendance(params)
    const data = res.data
    attendanceRankings.value = data?.list || []
  } catch (error: any) {
    console.error('加载出勤榜失败:', error)
    ElMessage.error('加载出勤榜失败')
  } finally {
    loadingAttendance.value = false
  }
}

// 加载所有统计数据
const loadAllStats = async () => {
  loading.value = true
  try {
    await Promise.all([
      loadGoalRankings(),
      loadAssistRankings(),
      loadAttendanceRankings()
    ])
  } finally {
    loading.value = false
  }
}

onMounted(async () => {
  await loadTeams()
  await loadAllStats()
})
</script>

<style scoped>
.stats-page {
  padding: 20px;
  max-width: 1400px;
  margin: 0 auto;
}

.header {
  margin-bottom: 20px;
}

.filters {
  display: flex;
  align-items: center;
  gap: 12px;
  margin-bottom: 20px;
  flex-wrap: wrap;
}

.stats-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 20px;
}

.stat-card {
  border-radius: 8px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}

.card-title {
  font-size: 18px;
  font-weight: 600;
}

.card-icon {
  font-size: 24px;
  color: #409eff;
}

.rank-badge {
  display: inline-block;
  width: 32px;
  height: 32px;
  line-height: 32px;
  text-align: center;
  border-radius: 50%;
  font-weight: bold;
}

.rank-1 {
  background: linear-gradient(135deg, #ffd700 0%, #ffed4e 100%);
  color: #8b5a00;
}

.rank-2 {
  background: linear-gradient(135deg, #c0c0c0 0%, #e0e0e0 100%);
  color: #5a5a5a;
}

.rank-3 {
  background: linear-gradient(135deg, #cd7f32 0%, #e6a04d 100%);
  color: #5a3a00;
}

.rank-other {
  background: #f0f0f0;
  color: #666;
}

.highlight-value {
  font-size: 18px;
  font-weight: bold;
  color: #67c23a;
}

.high-rate {
  color: #67c23a;
  font-weight: bold;
}

/* 榜首数据高亮 */
.top-player-highlight {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 12px;
  padding: 20px;
  margin-bottom: 20px;
  color: white;
  box-shadow: 0 4px 12px rgba(102, 126, 234, 0.3);
}

.highlight-content {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 8px;
}

.player-info {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.player-info .player-name {
  font-size: 20px;
  font-weight: bold;
}

.player-info .team-name {
  font-size: 14px;
  opacity: 0.9;
}

.stat-highlight {
  display: flex;
  align-items: baseline;
  gap: 8px;
}

.stat-highlight .stat-value {
  font-size: 36px;
  font-weight: bold;
  text-shadow: 2px 2px 4px rgba(0, 0, 0, 0.2);
}

.stat-highlight .stat-label {
  font-size: 14px;
  opacity: 0.9;
}

.highlight-subtitle {
  text-align: center;
  font-size: 14px;
  opacity: 0.8;
  font-style: italic;
}

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }

  .top-player-highlight {
    padding: 15px;
  }

  .highlight-content {
    flex-direction: column;
    align-items: flex-start;
    gap: 12px;
  }

  .stat-highlight .stat-value {
    font-size: 28px;
  }
}
</style>
