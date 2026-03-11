<template>
  <div class="match-detail-page">
    <el-page-header @back="$router.back()" content="比赛详情" />
    <el-card v-loading="loading" style="margin-top: 20px">
      <div v-if="match" class="match-info">
        <div class="score-board">
          <div class="team">{{ match.team1_name }}</div>
          <div class="score">{{ match.team1_score }} : {{ match.team2_score }}</div>
          <div class="team">{{ match.team2_name }}</div>
        </div>
        <el-descriptions :column="2" border style="margin-top: 20px">
          <el-descriptions-item label="比赛日期">{{ match.match_date }}</el-descriptions-item>
          <el-descriptions-item label="比赛场地">{{ match.match_venue || '-' }}</el-descriptions-item>
          <el-descriptions-item label="备注" :span="2">{{ match.notes || '-' }}</el-descriptions-item>
        </el-descriptions>

        <el-divider>球员统计</el-divider>

        <el-table :data="match.player_stats" style="width: 100%">
          <el-table-column prop="player_name" label="球员" />
          <el-table-column prop="player_team" label="球队" />
          <el-table-column prop="goals" label="进球" width="80" />
          <el-table-column prop="assists" label="助攻" width="80" />
          <el-table-column prop="minutes_played" label="出场时间" width="100" />
        </el-table>
      </div>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute } from 'vue-router'
import { matchesApi } from '@/api'

const route = useRoute()
const loading = ref(false)
const match = ref<any>(null)

const loadData = async () => {
  loading.value = true
  try {
    const matchId = Number(route.params.id)
    const res = await matchesApi.getById(matchId)
    match.value = res.data
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.score-board {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 20px;
  padding: 30px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  border-radius: 8px;
  color: white;
}

.team {
  font-size: 20px;
  font-weight: bold;
  flex: 1;
  text-align: center;
}

.score {
  font-size: 32px;
  font-weight: bold;
  padding: 0 20px;
}
</style>
