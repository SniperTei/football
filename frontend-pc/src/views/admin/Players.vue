<template>
  <div class="coming-soon-page">
    <el-result icon="info" title="功能开发中" sub-title="球员管理功能正在开发中，敬请期待...">
      <template #extra>
        <el-button type="primary" @click="$router.push('/admin/teams')">返回球队管理</el-button>
      </template>
    </el-result>
  </div>
</template>

<style scoped>
.coming-soon-page {
  display: flex;
  justify-content: center;
  align-items: center;
  min-height: 400px;
}
</style>
