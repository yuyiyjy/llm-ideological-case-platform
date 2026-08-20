<template>
  <div class="not-found">
    <div class="code">404</div>
    <div class="text">页面不存在或已被移除</div>
    <el-button type="primary" size="large" @click="$router.push('/')">
      返回首页
    </el-button>
  </div>
</template>

<script setup>
</script>

<style scoped>
.not-found {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 16px;
  background: #f5f7fa;
}
.code {
  font-size: 96px;
  font-weight: 700;
  color: #409eff;
  line-height: 1;
}
.text {
  font-size: 16px;
  color: #909399;
  margin-bottom: 8px;
}
</style>
