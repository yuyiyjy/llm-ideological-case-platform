<template>
  <header class="navbar">
    <div class="navbar-inner">
      <div class="left">
        <router-link to="/" class="logo">
          <el-icon class="logo-icon"><Reading /></el-icon>
          <span class="logo-text">
            <span class="logo-name">思政案例库</span>
            <span class="logo-sub">SIZHENG CASE LIBRARY</span>
          </span>
        </router-link>
        <nav class="menu">
          <router-link
            v-for="m in visibleMenus"
            :key="m.path"
            :to="m.path"
            class="menu-item"
            :class="{ active: isActive(m.path) }"
          >
            <el-icon><component :is="m.icon" /></el-icon>
            <span>{{ m.name }}</span>
          </router-link>
        </nav>
      </div>
      <div class="right">
        <el-dropdown trigger="click" @command="handleCommand">
          <span class="user-info">
            <el-avatar :size="32" :src="user.avatar" class="avatar">
              {{ user.nickName.charAt(0) }}
            </el-avatar>
            <span class="name">{{ user.nickName }}</span>
            <el-tag size="small" :type="roleTagType" effect="light" class="role-tag">
              {{ roleName }}
            </el-tag>
            <el-icon class="arrow"><ArrowDown /></el-icon>
          </span>
          <template #dropdown>
            <el-dropdown-menu>
              <el-dropdown-item command="profile">
                <el-icon><User /></el-icon>个人中心
              </el-dropdown-item>
              <el-dropdown-item command="logout" divided>
                <el-icon><SwitchButton /></el-icon>退出登录
              </el-dropdown-item>
            </el-dropdown-menu>
          </template>
        </el-dropdown>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useUserStore } from '@/stores/user'

const route = useRoute()
const router = useRouter()
const user = useUserStore()

const menus = [
  { path: '/', name: '首页', icon: 'HomeFilled' },
  { path: '/cases', name: '案例库', icon: 'Reading' },
  { path: '/ai-generate', name: '生成和上传案例', icon: 'MagicStick', roles: ['teacher', 'admin'] },
  { path: '/profile', name: '个人中心', icon: 'User' },
  { path: '/admin', name: '后台管理', icon: 'Setting', roles: ['admin'] },
]

const visibleMenus = computed(() =>
  menus.filter((m) => !m.roles || m.roles.includes(user.role))
)

const roleMap = {
  student: { name: '学生', tag: 'success' },
  teacher: { name: '教师', tag: 'warning' },
  admin: { name: '管理员', tag: 'danger' },
}
const roleName = computed(() => roleMap[user.role]?.name || '未知')
const roleTagType = computed(() => roleMap[user.role]?.tag || 'info')

function isActive(path) {
  if (path === '/') return route.path === '/'
  return route.path.startsWith(path)
}

async function handleCommand(cmd) {
  if (cmd === 'profile') {
    router.push('/profile')
  } else if (cmd === 'logout') {
    await user.logout()
    router.push('/login')
  }
}
</script>

<style scoped>
.navbar {
  position: fixed;
  top: 0;
  left: 0;
  right: 0;
  height: 64px;
  background: #fff;
  box-shadow: 0 1px 4px rgba(0, 21, 41, 0.08);
  z-index: 1000;
}
.navbar-inner {
  max-width: 1200px;
  margin: 0 auto;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: space-between;
  padding: 0 20px;
}
.left {
  display: flex;
  align-items: center;
  gap: 32px;
}
.logo {
  display: flex;
  align-items: center;
  gap: 8px;
}
.logo-icon {
  font-size: 26px;
  color: #fff;
  background: linear-gradient(135deg, #409eff, #6a5af9);
  border-radius: 8px;
  padding: 4px;
  box-sizing: content-box;
}
.logo-text {
  display: flex;
  flex-direction: column;
  line-height: 1.2;
}
.logo-name {
  font-size: 18px;
  font-weight: 700;
  color: #303133;
}
.logo-sub {
  font-size: 10px;
  color: #909399;
  letter-spacing: 1px;
}
.menu {
  display: flex;
  gap: 8px;
}
.menu-item {
  position: relative;
  display: flex;
  align-items: center;
  gap: 4px;
  padding: 8px 14px;
  font-size: 15px;
  color: #606266;
  border-radius: 6px;
  transition: color 0.2s, background 0.2s;
}
.menu-item:hover {
  color: #409eff;
  background: #f5f7fa;
}
.menu-item.active {
  color: #409eff;
  font-weight: 600;
}
.menu-item.active::after {
  content: '';
  position: absolute;
  bottom: 0;
  left: 50%;
  transform: translateX(-50%);
  width: 20px;
  height: 3px;
  background: #409eff;
  border-radius: 2px;
}
.right {
  display: flex;
  align-items: center;
}
.user-info {
  display: flex;
  align-items: center;
  gap: 8px;
  cursor: pointer;
  padding: 4px 8px;
  border-radius: 6px;
}
.user-info:hover {
  background: #f5f7fa;
}
.name {
  font-size: 14px;
  color: #303133;
}
.avatar {
  background: #409eff;
}
.arrow {
  font-size: 12px;
  color: #909399;
}
</style>
