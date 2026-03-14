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

        <el-table :data="goalRankings" stripe>
          <el-table-column label="排名" width="80" align="center">
            <template #default="{ row }">
              <span class="rank-badge" :class="'rank-' + getRankClass(row.rank)">{{ row.rank }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="player_name" label="球员" min-width="120" />
          <el-table-column prop="jersey_number" label="号码" width="80" align="center" />
          <el-table-column prop="team_name" label="球队" min-width="120" />
          <el-table-column prop="total_goals" label="进球" width="80" align="center">
            <template #default="{ row }">
              <span class="highlight-value">{{ row.total_goals }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="total_assists" label="助攻" width="80" align="center" />
          <el-table-column prop="played_matches" label="出场" width="80" align="center" />
          <el-table-column prop="attendance_rate" label="出勤率" width="100" align="center">
            <template #default="{ row }">
              <span :class="{ 'high-rate': row.attendance_rate >= 80 }">
                {{ row.attendance_rate }}%
              </span>
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

        <el-table :data="assistRankings" stripe>
          <el-table-column label="排名" width="80" align="center">
            <template #default="{ row }">
              <span class="rank-badge" :class="'rank-' + getRankClass(row.rank)">{{ row.rank }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="player_name" label="球员" min-width="120" />
          <el-table-column prop="jersey_number" label="号码" width="80" align="center" />
          <el-table-column prop="team_name" label="球队" min-width="120" />
          <el-table-column prop="total_goals" label="进球" width="80" align="center" />
          <el-table-column prop="total_assists" label="助攻" width="80" align="center">
            <template #default="{ row }">
              <span class="highlight-value">{{ row.total_assists }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="played_matches" label="出场" width="80" align="center" />
          <el-table-column prop="attendance_rate" label="出勤率" width="100" align="center">
            <template #default="{ row }">
              <span :class="{ 'high-rate': row.attendance_rate >= 80 }">
                {{ row.attendance_rate }}%
              </span>
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

        <el-table :data="attendanceRankings" stripe>
          <el-table-column label="排名" width="80" align="center">
            <template #default="{ row }">
              <span class="rank-badge" :class="'rank-' + getRankClass(row.rank)">{{ row.rank }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="player_name" label="球员" min-width="120" />
          <el-table-column prop="jersey_number" label="号码" width="80" align="center" />
          <el-table-column prop="team_name" label="球队" min-width="120" />
          <el-table-column prop="total_goals" label="进球" width="80" align="center" />
          <el-table-column prop="total_assists" label="助攻" width="80" align="center" />
          <el-table-column prop="played_matches" label="出场次数" width="100" align="center">
            <template #default="{ row }">
              <span class="highlight-value">{{ row.played_matches }}</span>
            </template>
          </el-table-column>
          <el-table-column prop="attendance_rate" label="出勤率" width="100" align="center">
            <template #default="{ row }">
              <span :class="{ 'high-rate': row.attendance_rate >= 80 }">
                {{ row.attendance_rate }}%
              </span>
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
    const data = res.data || res
    goalRankings.value = data.list || []
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
    const data = res.data || res
    assistRankings.value = data.list || []
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
    const data = res.data || res
    attendanceRankings.value = data.list || []
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
  grid-template-columns: repeat(auto-fit, minmax(400px, 1fr));
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

/* 响应式设计 */
@media (max-width: 768px) {
  .stats-grid {
    grid-template-columns: 1fr;
  }
}
</style>
