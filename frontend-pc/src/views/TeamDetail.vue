<template>
  <div class="team-detail-page">
    <el-page-header @back="$router.back()" :content="team?.name || '球队详情'" />

    <!-- 添加操作按钮 -->
    <div class="action-buttons" v-if="team">
      <el-button type="primary" @click="viewHistory">
        <el-icon><TrendCharts /></el-icon>
        查看历史战绩
      </el-button>
    </div>

    <el-card v-loading="loading" style="margin-top: 20px">
      <el-descriptions v-if="team" :column="2" border>
        <el-descriptions-item label="球队名称">{{ team.name }}</el-descriptions-item>
        <el-descriptions-item label="成立年份">{{ team.founded_year || '-' }}</el-descriptions-item>
        <el-descriptions-item label="球队ID">{{ team.id }}</el-descriptions-item>
        <el-descriptions-item label="创建时间">{{ formatDate(team.created_at) }}</el-descriptions-item>
        <el-descriptions-item label="最后更新">{{ formatDate(team.updated_at) }}</el-descriptions-item>
        <el-descriptions-item label="描述" :span="2">{{ team.description || '-' }}</el-descriptions-item>
      </el-descriptions>

      <el-divider>球队球员 ({{ players.length }})</el-divider>

      <el-alert
        v-if="!players || players.length === 0"
        title="暂无球员信息"
        type="info"
        :closable="false"
        style="margin-top: 20px"
      />

      <el-table v-else :data="players" style="width: 100%; margin-top: 20px">
        <el-table-column prop="id" label="ID" width="80" />
        <el-table-column prop="name" label="姓名" min-width="120" />
        <el-table-column prop="position" label="位置" width="100" />
        <el-table-column prop="jersey_number" label="球衣号码" width="100" />
      </el-table>
    </el-card>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { TrendCharts } from '@element-plus/icons-vue'
import { teamsApi, playersApi } from '@/api'
import dayjs from 'dayjs'

const route = useRoute()
const router = useRouter()
const loading = ref(false)
const team = ref<any>(null)
const players = ref<any[]>([])

const formatDate = (date: string) => {
  return dayjs(date).format('YYYY-MM-DD HH:mm:ss')
}

const viewHistory = () => {
  const teamId = route.params.id
  router.push(`/teams/${teamId}/history`)
}

const loadData = async () => {
  loading.value = true
  try {
    const teamId = Number(route.params.id)

    // 获取球队基本信息
    const teamRes = await teamsApi.getById(teamId)
    team.value = teamRes.data

    // 获取球队球员信息
    const playersRes = await playersApi.getByTeam(teamId)
    players.value = playersRes.data.list || []
  } catch (error) {
    console.error('加载数据失败:', error)
  } finally {
    loading.value = false
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.team-detail-page {
  max-width: 1000px;
  margin: 0 auto;
}

.action-buttons {
  margin-top: 20px;
  display: flex;
  gap: 10px;
}
</style>
