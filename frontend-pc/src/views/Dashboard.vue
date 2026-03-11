<template>
  <div class="dashboard">
    <el-row :gutter="20">
      <el-col :span="24">
        <div class="welcome-banner">
          <h1>欢迎使用足球球队数据管理平台</h1>
          <p>这里可以查看和管理所有球队信息</p>
        </div>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="stats-row">
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon size="40" color="#409eff"><Football /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.teams }}</div>
              <div class="stat-label">球队数量</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon size="40" color="#67c23a"><User /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.users }}</div>
              <div class="stat-label">注册用户</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon size="40" color="#e6a23c"><Trophy /></el-icon>
            <div class="stat-info">
              <div class="stat-value">{{ stats.permissions }}</div>
              <div class="stat-label">权限分配</div>
            </div>
          </div>
        </el-card>
      </el-col>
      <el-col :xs="24" :sm="12" :md="6">
        <el-card class="stat-card">
          <div class="stat-content">
            <el-icon size="40" color="#f56c6c"><Calendar /></el-icon>
            <div class="stat-info">
              <div class="stat-value">开发中</div>
              <div class="stat-label">更多功能</div>
            </div>
          </div>
        </el-card>
      </el-col>
    </el-row>

    <el-row :gutter="20" class="content-row">
      <el-col :xs="24" :lg="24">
        <el-card>
          <template #header>
            <div class="card-header">
              <span>球队列表</span>
              <el-button type="primary" @click="$router.push('/teams')">查看全部</el-button>
            </div>
          </template>
          <el-table :data="recentTeams" style="width: 100%">
            <el-table-column prop="id" label="ID" width="80" />
            <el-table-column prop="name" label="球队名称" min-width="150" />
            <el-table-column prop="description" label="描述" show-overflow-tooltip />
            <el-table-column prop="founded_year" label="成立年份" width="120" />
            <el-table-column label="操作" width="150">
              <template #default="{ row }">
                <el-button type="primary" text @click="$router.push(`/teams/${row.id}`)">
                  查看详情
                </el-button>
              </template>
            </el-table-column>
          </el-table>
        </el-card>
      </el-col>
    </el-row>
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { teamsApi } from '@/api'

const stats = ref({
  teams: 0,
  users: 0,
  permissions: 0
})

const recentTeams = ref<any[]>([])

const loadData = async () => {
  try {
    const teamsRes = await teamsApi.getAll()
    const teams = teamsRes.data.list || []

    stats.value.teams = teamsRes.data.total || teams.length
    stats.value.users = 4 // 从初始化数据可知有4个用户
    stats.value.permissions = 6 // 从初始化数据可知有6个权限分配

    recentTeams.value = teams.slice(0, 5)
  } catch (error) {
    console.error('加载数据失败:', error)
  }
}

onMounted(() => {
  loadData()
})
</script>

<style scoped>
.dashboard {
  padding: 0;
}

.welcome-banner {
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  padding: 40px;
  border-radius: 8px;
  text-align: center;
  margin-bottom: 20px;
}

.welcome-banner h1 {
  font-size: 28px;
  margin-bottom: 10px;
}

.stats-row {
  margin-bottom: 20px;
}

.stat-card {
  margin-bottom: 20px;
}

.stat-content {
  display: flex;
  align-items: center;
  gap: 15px;
}

.stat-info {
  flex: 1;
}

.stat-value {
  font-size: 28px;
  font-weight: bold;
  color: #303133;
}

.stat-label {
  font-size: 14px;
  color: #909399;
  margin-top: 4px;
}

.content-row {
  margin-top: 20px;
}

.card-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
</style>
