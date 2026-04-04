<template>
  <div class="player-detail-page">
    <el-page-header @back="$router.back()">
      <template #content>
        <div class="header-content">
          <span>{{ player?.name || '球员详情' }}</span>
          <el-tag v-if="player?.jersey_number" type="primary" size="small">
            #{{ player.jersey_number }}
          </el-tag>
        </div>
      </template>
    </el-page-header>

    <el-card v-loading="loading" style="margin-top: 20px">
      <!-- 基本信息 -->
      <el-descriptions v-if="player" :column="2" border>
        <el-descriptions-item label="球员姓名">{{ player.name }}</el-descriptions-item>
        <el-descriptions-item label="位置">{{ player.position }}</el-descriptions-item>
        <el-descriptions-item label="球衣号码">{{ player.jersey_number || '-' }}</el-descriptions-item>
        <el-descriptions-item label="所属球队">
          <el-link
            v-if="player.team_id"
            type="primary"
            @click="$router.push(`/teams/${player.team_id}`)"
          >
            <div class="team-link">
              <TeamLogo :logo-url="player.team_logo_url ?? undefined" size="20px" :team-name="player.team_name" />
              {{ player.team_name }}
            </div>
          </el-link>
          <span v-else>-</span>
        </el-descriptions-item>
      </el-descriptions>

      <!-- 统计卡片 -->
      <div v-if="player" class="stats-cards">
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ player.career_stats.total_matches }}</div>
          <div class="stat-label">总出场记录</div>
        </el-card>
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ player.career_stats.played_matches }}</div>
          <div class="stat-label">实际出场</div>
        </el-card>
        <el-card shadow="hover" class="stat-card accent-goal">
          <div class="stat-value">{{ player.career_stats.total_goals }}</div>
          <div class="stat-label">进球</div>
        </el-card>
        <el-card shadow="hover" class="stat-card accent-assist">
          <div class="stat-value">{{ player.career_stats.total_assists }}</div>
          <div class="stat-label">助攻</div>
        </el-card>
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ player.attendance_rate }}%</div>
          <div class="stat-label">出勤率</div>
        </el-card>
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ player.career_stats.total_yellow_cards }}</div>
          <div class="stat-label">黄牌</div>
        </el-card>
        <el-card shadow="hover" class="stat-card">
          <div class="stat-value">{{ player.career_stats.total_red_cards }}</div>
          <div class="stat-label">红牌</div>
        </el-card>
      </div>

      <!-- 最近比赛记录 -->
      <el-divider>最近比赛记录 ({{ player?.recent_matches?.length || 0 }})</el-divider>

      <el-alert
        v-if="!player?.recent_matches || player.recent_matches.length === 0"
        title="暂无比赛记录"
        type="info"
        :closable="false"
        style="margin-top: 10px"
      />

      <el-table
        v-else
        :data="player.recent_matches"
        style="width: 100%; margin-top: 10px"
        @row-click="(row: PlayerRecentMatch) => $router.push(`/matches/${row.match_id}`)"
        class="match-table"
      >
        <el-table-column label="日期" width="120">
          <template #default="{ row }">
            {{ row.match_date ? formatDate(row.match_date) : '-' }}
          </template>
        </el-table-column>
        <el-table-column label="对手" min-width="120">
          <template #default="{ row }">
            {{ row.is_home ? '主' : '客' }} vs {{ row.opponent_name }}
          </template>
        </el-table-column>
        <el-table-column label="比分" width="100" align="center">
          <template #default="{ row }">
            <span v-if="typeof row.home_score === 'number'" class="score">
              <span :class="{ 'score-win': isPlayerTeamWin(row) }">{{ row.home_score }}</span>
              :
              <span :class="{ 'score-win': !isPlayerTeamWin(row) }">{{ row.away_score }}</span>
            </span>
            <span v-else class="score">{{ row.home_score }} : {{ row.away_score }}</span>
          </template>
        </el-table-column>
        <el-table-column label="出场" width="70" align="center">
          <template #default="{ row }">
            <el-tag :type="row.played ? 'success' : 'info'" size="small">
              {{ row.played ? '是' : '否' }}
            </el-tag>
          </template>
        </el-table-column>
        <el-table-column prop="goals" label="进球" width="70" align="center" />
        <el-table-column prop="assists" label="助攻" width="70" align="center" />
        <el-table-column label="黄/红牌" width="90" align="center">
          <template #default="{ row }">
            <span v-if="row.yellow_cards || row.red_cards">
              <el-tag v-if="row.yellow_cards" type="warning" size="small">{{ row.yellow_cards }}</el-tag>
              <el-tag v-if="row.red_cards" type="danger" size="small" style="margin-left: 4px">{{ row.red_cards }}</el-tag>
            </span>
            <span v-else>-</span>
          </template>
        </el-table-column>
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import { playersApi, type PlayerDetailData, type PlayerRecentMatch } from '@/api/players'
import { ElMessage } from 'element-plus'
import dayjs from 'dayjs'
import TeamLogo from '@/components/TeamLogo.vue'

const route = useRoute()
const loading = ref(false)
const player = ref<PlayerDetailData | null>(null)

const formatDate = (date: string) => dayjs(date).format('YYYY-MM-DD')

const isPlayerTeamWin = (row: PlayerRecentMatch) => {
  if (typeof row.home_score !== 'number' || typeof row.away_score !== 'number') return false
  return row.is_home ? row.home_score > row.away_score : row.away_score > row.home_score
}

const loadData = async () => {
  loading.value = true
  try {
    const playerId = Number(route.params.id)
    const res = await playersApi.getDetail(playerId)
    player.value = res.data
  } catch (error: any) {
    player.value = null
    ElMessage.error(error?.response?.data?.msg || '加载球员详情失败')
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})

watch(() => route.params.id, () => {
  if (route.params.id) loadData()
})
</script>

<style scoped>
.player-detail-page {
  max-width: 1000px;
  margin: 0 auto;
}

.header-content {
  display: flex;
  align-items: center;
  gap: 10px;
}

.team-link {
  display: flex;
  align-items: center;
  gap: 6px;
}

.stats-cards {
  display: flex;
  gap: 16px;
  margin-top: 20px;
  flex-wrap: wrap;
}

.stat-card {
  flex: 1;
  min-width: 100px;
  text-align: center;
}

.stat-card .stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-card .stat-label {
  font-size: 13px;
  color: #909399;
  margin-top: 4px;
}

.stat-card.accent-goal .stat-value {
  color: #e6a23c;
}

.stat-card.accent-assist .stat-value {
  color: #409eff;
}

.score {
  font-weight: bold;
  font-family: monospace;
}

.score-win {
  color: #67c23a;
}

.match-table {
  cursor: pointer;
}

.match-table :deep(.el-table__row:hover) {
  background-color: #ecf5ff;
}
</style>
