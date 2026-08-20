<template>
  <div class="admin-layout">
    <aside class="sidebar">
      <div class="sidebar-title">后台管理</div>
      <nav>
        <router-link
          v-for="item in items"
          :key="item.path"
          :to="item.path"
          class="side-item"
          :class="{ active: route.path === item.path }"
        >
          <el-icon><component :is="item.icon" /></el-icon>
          <span>{{ item.name }}</span>
        </router-link>
      </nav>
    </aside>
    <div class="admin-content">
      <el-breadcrumb separator="/" class="breadcrumb">
        <el-breadcrumb-item :to="{ path: '/' }">首页</el-breadcrumb-item>
        <el-breadcrumb-item>管理后台</el-breadcrumb-item>
        <el-breadcrumb-item>{{ route.meta.title }}</el-breadcrumb-item>
      </el-breadcrumb>
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { useRoute } from 'vue-router'

const route = useRoute()

const items = [
  { path: '/admin/review', name: '案例审核管理', icon: 'Checked' },
  { path: '/admin/manage', name: '课程 & 思政标签管理', icon: 'CollectionTag' },
  { path: '/admin/users', name: '用户管理', icon: 'UserFilled' },
  { path: '/admin/statistics', name: '数据统计看板', icon: 'DataAnalysis' },
]
</script>

<style scoped>
.admin-layout {
  min-height: calc(100vh - 64px);
}
.sidebar {
  position: fixed;
  top: 64px;
  bottom: 0;
  left: 0;
  width: 220px;
  background: #fff;
  box-shadow: 2px 0 8px rgba(0, 0, 0, 0.04);
  padding-top: 12px;
  z-index: 100;
}
.sidebar-title {
  font-size: 14px;
  font-weight: 700;
  color: #909399;
  padding: 12px 24px;
  letter-spacing: 1px;
}
.side-item {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 13px 24px;
  font-size: 14px;
  color: #606266;
  border-left: 3px solid transparent;
  transition: all 0.2s;
}
.side-item:hover {
  color: #409eff;
  background: #f5f7fa;
}
.side-item.active {
  color: #409eff;
  font-weight: 600;
  background: #ecf5ff;
  border-left-color: #409eff;
}
.admin-content {
  margin-left: 220px;
  padding: 20px;
}
.breadcrumb {
  margin-bottom: 16px;
}
</style>
