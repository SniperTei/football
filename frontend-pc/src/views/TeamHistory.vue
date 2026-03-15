<template>
  <div class="team-history-page">
    <!-- 页面头部 -->
    <div class="header">
      <el-page-header @back="$router.back()" :content="team?.name || '球队历史战绩'" />
    </div>

    <!-- 时间筛选器 -->
    <el-card v-if="team" style="margin-top: 20px">
      <div class="filter-bar">
        <span class="filter-label">时间范围：</span>
        <el-radio-group v-model="timeRange" @change="loadStats">
          <el-radio-button :label="30">最近1个月</el-radio-button>
          <el-radio-button :label="90">最近3个月</el-radio-button>
          <el-radio-button :label="365">最近1年</el-radio-button>
          <el-radio-button :label="null">全部</el-radio-button>
        </el-radio-group>
      </div>
    </el-card>

    <!-- 统计概览 -->
    <div class="stats-overview" v-loading="loading">
      <!-- 胜负平卡片 -->
      <el-row :gutter="20">
        <el-col :span="6">
          <el-card class="stat-card wins">
            <div class="stat-content">
              <div class="stat-number">{{ stats.wins || 0 }}</div>
              <div class="stat-label">胜</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card draws">
            <div class="stat-content">
              <div class="stat-number">{{ stats.draws || 0 }}</div>
              <div class="stat-label">平</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card losses">
            <div class="stat-content">
              <div class="stat-number">{{ stats.losses || 0 }}</div>
              <div class="stat-label">负</div>
            </div>
          </el-card>
        </el-col>
        <el-col :span="6">
          <el-card class="stat-card win-rate">
            <div class="stat-content">
              <div class="stat-number">{{ stats.win_rate || 0 }}%</div>
              <div class="stat-label">胜率</div>
            </div>
          </el-card>
        </el-col>
      </el-row>

      <!-- ECharts 图表区域 -->
      <el-row :gutter="20" style="margin-top: 20px">
        <!-- 胜负平饼图 -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <span class="card-title">📊 胜负分布</span>
            </template>
            <div ref="pieChartRef" style="width: 100%; height: 300px"></div>
          </el-card>
        </el-col>

        <!-- 主客场对比柱状图 -->
        <el-col :span="12">
          <el-card>
            <template #header>
              <span class="card-title">🏟️ 主客场对比</span>
            </template>
            <div ref="barChartRef" style="width: 100%; height: 300px"></div>
          </el-card>
        </el-col>
      </el-row>

      <!-- 进球失球统计 -->
      <el-card style="margin-top: 20px">
        <template #header>
          <span class="card-title">⚽ 进球/失球统计</span>
        </template>
        <el-row :gutter="20">
          <el-col :span="8">
            <div class="stat-box">
              <div class="stat-label">进球</div>
              <div class="stat-value goals">{{ stats.goals_for || 0 }}</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="stat-box">
              <div class="stat-label">失球</div>
              <div class="stat-value conceded">{{ stats.goals_against || 0 }}</div>
            </div>
          </el-col>
          <el-col :span="8">
            <div class="stat-box">
              <div class="stat-label">净胜球</div>
              <div class="stat-value" :class="stats.goal_difference >= 0 ? 'positive' : 'negative'">
                {{ stats.goal_difference >= 0 ? '+' : '' }}{{ stats.goal_difference || 0 }}
              </div>
            </div>
          </el-col>
        </el-row>
      </el-card>

      <!-- 主客场详细战绩 -->
      <el-card style="margin-top: 20px">
        <template #header>
          <span class="card-title">🏟️ 主客场战绩详情</span>
        </template>
        <el-row :gutter="20">
          <el-col :span="12">
            <h4>主场</h4>
            <el-table :data="[homeStats]" size="small">
              <el-table-column prop="wins" label="胜" width="80" align="center">
                <template #default="{ row }">
                  <span class="result-win">{{ row.wins }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="draws" label="平" width="80" align="center">
                <template #default="{ row }">
                  <span class="result-draw">{{ row.draws }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="losses" label="负" width="80" align="center">
                <template #default="{ row }">
                  <span class="result-loss">{{ row.losses }}</span>
                </template>
              </el-table-column>
            </el-table>
          </el-col>
          <el-col :span="12">
            <h4>客场</h4>
            <el-table :data="[awayStats]" size="small">
              <el-table-column prop="wins" label="胜" width="80" align="center">
                <template #default="{ row }">
                  <span class="result-win">{{ row.wins }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="draws" label="平" width="80" align="center">
                <template #default="{ row }">
                  <span class="result-draw">{{ row.draws }}</span>
                </template>
              </el-table-column>
              <el-table-column prop="losses" label="负" width="80" align="center">
                <template #default="{ row }">
                  <span class="result-loss">{{ row.losses }}</span>
                </template>
              </el-table-column>
            </el-table>
          </el-col>
        </el-row>
      </el-card>

      <!-- 最近比赛记录 -->
      <el-card style="margin-top: 20px">
        <template #header>
          <span class="card-title">📈 最近比赛</span>
        </template>
        <el-table :data="recentMatches" stripe size="small">
          <el-table-column prop="date" label="日期" width="120">
            <template #default="{ row }">
              {{ formatDate(row.date) }}
            </template>
          </el-table-column>
          <el-table-column prop="opponent" label="对手" min-width="120" />
          <el-table-column prop="score" label="比分" width="100" align="center" />
          <el-table-column prop="venue" label="场地" width="80" align="center" />
          <el-table-column prop="result" label="结果" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="getResultTagType(row.result)" size="small">
                {{ getResultText(row.result) }}
              </el-tag>
            </template>
          </el-table-column>
        </el-table>
      </el-card>

      <!-- 对手选择 -->
      <el-card v-if="otherTeams.length > 0" style="margin-top: 20px">
        <template #header>
          <span class="card-title">⚔️ 选择对手查看对战历史</span>
        </template>
        <el-select
          v-model="selectedOpponentId"
          placeholder="选择对手球队"
          clearable
          filterable
          @change="loadHeadToHeadStats"
        >
          <el-option
            v-for="t in otherTeams"
            :key="t.id"
            :label="t.name"
            :value="t.id"
          />
        </el-select>
      </el-card>

      <!-- 对战历史 -->
      <el-card v-if="headToHeadStats.total_matches > 0" style="margin-top: 20px">
        <template #header>
          <span class="card-title">🆚 对战历史</span>
        </template>
        <el-descriptions :column="4" border>
          <el-descriptions-item label="总场次">{{ headToHeadStats.total_matches }}</el-descriptions-item>
          <el-descriptions-item label="胜">{{ headToHeadStats.team_wins }}</el-descriptions-item>
          <el-descriptions-item label="平">{{ headToHeadStats.team_draws }}</el-descriptions-item>
          <el-descriptions-item label="负">{{ headToHeadStats.team_losses }}</el-descriptions-item>
        </el-descriptions>

        <el-table :data="headToHeadStats.recent_matches" stripe style="margin-top: 15px" size="small">
          <el-table-column prop="date" label="日期" width="120">
            <template #default="{ row }">
              {{ formatDate(row.date) }}
            </template>
          </el-table-column>
          <el-table-column prop="opponent" label="对手" min-width="120" />
          <el-table-column prop="score" label="比分" width="100" align="center" />
          <el-table-column prop="venue" label="场地" width="80" align="center" />
          <el-table-column prop="result" label="结果" width="80" align="center">
            <template #default="{ row }">
              <el-tag :type="getResultTagType(row.result)" size="small">
                {{ getResultText(row.result) }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="competition" label="类型" width="100" align="center" />
        </el-table>
      </el-card>

      <!-- 无数据提示 -->
      <el-alert
        v-if="!loading && stats.total_matches === 0"
        title="暂无比赛记录"
        type="info"
        :closable="false"
        style="margin-top: 20px"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed, nextTick } from 'vue'
import { useRoute } from 'vue-router'
import { getTeamStats, getHeadToHeadStats, type TeamStatistics } from '@/api/teamStats'
import { teamsApi, type Team } from '@/api/teams'
import { ElMessage } from 'element-plus'
import * as echarts from 'echarts'
import dayjs from 'dayjs'

const route = useRoute()
const loading = ref(false)
const team = ref<Team | null>(null)
const stats = ref<Partial<TeamStatistics>>({})
const timeRange = ref<number | null>(null)
const otherTeams = ref<Team[]>([])
const selectedOpponentId = ref<number | null>(null)
const headToHeadStats = ref<any>({})

// ECharts 图表引用
const pieChartRef = ref<HTMLElement>()
const barChartRef = ref<HTMLElement>()
let pieChart: echarts.ECharts | null = null
let barChart: echarts.ECharts | null = null

// 计算属性
const homeStats = computed(() => ({
  wins: stats.value.home_wins || 0,
  draws: stats.value.home_draws || 0,
  losses: stats.value.home_losses || 0
}))

const awayStats = computed(() => ({
  wins: stats.value.away_wins || 0,
  draws: stats.value.away_draws || 0,
  losses: stats.value.away_losses || 0
}))

const recentMatches = computed(() => stats.value.recent_form || [])

// 方法
const formatDate = (date: string) => dayjs(date).format('YYYY-MM-DD')

const getResultTagType = (result: string) => {
  switch (result) {
    case 'W': return 'success'
    case 'D': return 'warning'
    case 'L': return 'danger'
    default: return 'info'
  }
}

const getResultText = (result: string) => {
  switch (result) {
    case 'W': return '胜'
    case 'D': return '平'
    case 'L': return '负'
    default: return result
  }
}

const initPieChart = () => {
  if (!pieChartRef.value) return

  pieChart = echarts.init(pieChartRef.value)
  updatePieChart()
}

const updatePieChart = () => {
  if (!pieChart) return

  const option = {
    tooltip: {
      trigger: 'item',
      formatter: '{b}: {c} ({d}%)'
    },
    legend: {
      orient: 'vertical',
      left: 'left'
    },
    series: [
      {
        name: '比赛结果',
        type: 'pie',
        radius: '60%',
        data: [
          { value: stats.value.wins || 0, name: '胜', itemStyle: { color: '#67c23a' } },
          { value: stats.value.draws || 0, name: '平', itemStyle: { color: '#e6a23c' } },
          { value: stats.value.losses || 0, name: '负', itemStyle: { color: '#f56c6c' } }
        ],
        emphasis: {
          itemStyle: {
            shadowBlur: 10,
            shadowOffsetX: 0,
            shadowColor: 'rgba(0, 0, 0, 0.5)'
          }
        }
      }
    ]
  }

  pieChart.setOption(option)
}

const initBarChart = () => {
  if (!barChartRef.value) return

  barChart = echarts.init(barChartRef.value)
  updateBarChart()
}

const updateBarChart = () => {
  if (!barChart) return

  const option = {
    tooltip: {
      trigger: 'axis',
      axisPointer: {
        type: 'shadow'
      }
    },
    legend: {
      data: ['胜', '平', '负']
    },
    xAxis: {
      type: 'category',
      data: ['主场', '客场']
    },
    yAxis: {
      type: 'value'
    },
    series: [
      {
        name: '胜',
        type: 'bar',
        data: [stats.value.home_wins || 0, stats.value.away_wins || 0],
        itemStyle: { color: '#67c23a' }
      },
      {
        name: '平',
        type: 'bar',
        data: [stats.value.home_draws || 0, stats.value.away_draws || 0],
        itemStyle: { color: '#e6a23c' }
      },
      {
        name: '负',
        type: 'bar',
        data: [stats.value.home_losses || 0, stats.value.away_losses || 0],
        itemStyle: { color: '#f56c6c' }
      }
    ]
  }

  barChart.setOption(option)
}

const loadTeamData = async () => {
  loading.value = true
  try {
    const teamId = Number(route.params.id)

    // 获取球队信息
    const teamRes = await teamsApi.getById(teamId)
    team.value = teamRes.data

    // 加载其他球队（用于对战选择）
    const teamsRes = await teamsApi.getAll()
    const allTeams = teamsRes.data.list || []
    otherTeams.value = allTeams.filter(t => t.id !== teamId)

    // 加载统计数据
    await loadStats()

  } catch (error) {
    console.error('加载数据失败:', error)
    ElMessage.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const loadStats = async () => {
  if (!team.value) return

  try {
    const statsRes = await getTeamStats(team.value.id, timeRange.value || undefined)
    stats.value = statsRes.data

    // 更新图表
    await nextTick()
    updatePieChart()
    updateBarChart()

  } catch (error) {
    console.error('加载统计失败:', error)
    ElMessage.error('加载统计失败')
  }
}

const loadHeadToHeadStats = async () => {
  if (!selectedOpponentId.value || !team.value) {
    headToHeadStats.value = {}
    return
  }

  try {
    const statsRes = await getHeadToHeadStats(team.value.id, selectedOpponentId.value)
    headToHeadStats.value = statsRes.data
  } catch (error) {
    console.error('加载对战历史失败:', error)
    ElMessage.error('加载对战历史失败')
  }
}

onMounted(async () => {
  await loadTeamData()
  await nextTick()
  initPieChart()
  initBarChart()

  // 响应式调整图表大小
  window.addEventListener('resize', () => {
    pieChart?.resize()
    barChart?.resize()
  })
})
</script>

<style scoped>
.team-history-page {
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
}

.header {
  margin-bottom: 20px;
}

.filter-bar {
  display: flex;
  align-items: center;
  gap: 15px;
}

.filter-label {
  font-weight: 600;
  color: #606266;
}

.stats-overview {
  margin-top: 20px;
}

.stat-card {
  text-align: center;
  transition: all 0.3s ease;
}

.stat-card:hover {
  transform: translateY(-4px);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
}

.stat-content {
  padding: 20px 0;
}

.stat-number {
  font-size: 36px;
  font-weight: bold;
  margin-bottom: 8px;
}

.stat-label {
  font-size: 14px;
  color: #666;
}

.wins .stat-number {
  color: #67c23a;
}

.draws .stat-number {
  color: #e6a23c;
}

.losses .stat-number {
  color: #f56c6c;
}

.win-rate .stat-number {
  color: #409eff;
}

.card-title {
  font-size: 16px;
  font-weight: 600;
}

.stat-box {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 20px;
  background: #f5f7fa;
  border-radius: 8px;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
}

.stat-value.goals {
  color: #67c23a;
}

.stat-value.conceded {
  color: #f56c6c;
}

.stat-value.positive {
  color: #67c23a;
}

.stat-value.negative {
  color: #f56c6c;
}

.result-win {
  color: #67c23a;
  font-weight: bold;
}

.result-draw {
  color: #e6a23c;
  font-weight: bold;
}

.result-loss {
  color: #f56c6c;
  font-weight: bold;
}

@media (max-width: 768px) {
  .team-history-page {
    padding: 10px;
  }

  .el-col {
    margin-bottom: 15px;
  }
}
</style>
