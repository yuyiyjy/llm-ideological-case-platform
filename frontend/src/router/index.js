import { createRouter, createWebHistory } from 'vue-router'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const routes = [
  {
    path: '/login',
    name: 'Login',
    component: () => import('@/views/Login.vue'),
    meta: { noAuth: true, title: '登录' },
  },
  {
    path: '/',
    name: 'Home',
    component: () => import('@/views/Home.vue'),
    meta: { title: '首页' },
  },
  {
    path: '/cases',
    name: 'CaseList',
    component: () => import('@/views/CaseList.vue'),
    meta: { title: '案例库' },
  },
  {
    path: '/ai-generate',
    name: 'AIGenerate',
    component: () => import('@/views/AIGenerate.vue'),
    meta: { title: 'AI生成案例', roles: ['teacher', 'admin'] },
  },
  {
    path: '/ai-records',
    name: 'AIRecords',
    component: () => import('@/views/AIRecords.vue'),
    meta: { title: '我的生成记录', roles: ['teacher', 'admin'] },
  },
  {
    path: '/profile',
    name: 'Profile',
    component: () => import('@/views/Profile.vue'),
    meta: { title: '个人中心' },
  },
  {
    path: '/admin',
    component: () => import('@/views/admin/AdminLayout.vue'),
    redirect: '/admin/review',
    meta: { title: '管理后台', roles: ['admin'] },
    children: [
      {
        path: 'review',
        name: 'AdminReview',
        component: () => import('@/views/admin/Review.vue'),
        meta: { title: '案例审核', roles: ['admin'] },
      },
      {
        path: 'manage',
        name: 'AdminManage',
        component: () => import('@/views/admin/Manage.vue'),
        meta: { title: '课程标签管理', roles: ['admin'] },
      },
      {
        path: 'users',
        name: 'AdminUsers',
        component: () => import('@/views/admin/Users.vue'),
        meta: { title: '用户管理', roles: ['admin'] },
      },
      {
        path: 'statistics',
        name: 'AdminStatistics',
        component: () => import('@/views/admin/Statistics.vue'),
        meta: { title: '数据统计', roles: ['admin'] },
      },
    ],
  },
  {
    path: '/404',
    name: 'NotFound',
    component: () => import('@/views/NotFound.vue'),
    meta: { noAuth: true, title: '404' },
  },
  {
    path: '/:pathMatch(.*)*',
    redirect: '/404',
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes,
  scrollBehavior: () => ({ top: 0 }),
})

router.beforeEach((to, from, next) => {
  document.title = to.meta.title ? `${to.meta.title} - 思政案例库` : '思政案例库'
  const userStore = useUserStore()

  if (to.meta.noAuth) {
    // 已登录访问登录页 → 跳首页
    if (to.path === '/login' && userStore.isLogin) {
      next('/')
    } else {
      next()
    }
    return
  }

  if (!userStore.isLogin) {
    ElMessage.warning('请先登录')
    next({ path: '/login', query: { redirect: to.fullPath } })
    return
  }

  if (to.meta.roles && !to.meta.roles.includes(userStore.role)) {
    ElMessage.error('暂无访问权限')
    next('/')
    return
  }

  next()
})

export default router
