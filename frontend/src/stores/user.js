import { defineStore } from 'pinia'
import {
  loginApi,
  logoutApi,
  getUserInfoApi,
  updateUserInfoApi,
  changePasswordApi,
} from '@/api'
import { ElMessage } from 'element-plus'

export const useUserStore = defineStore('user', {
  state: () => ({
    token: localStorage.getItem('token') || '',
    userInfo: JSON.parse(localStorage.getItem('userInfo') || 'null'),
  }),
  getters: {
    isLogin: (state) => !!state.token,
    role: (state) => (state.userInfo ? state.userInfo.role : ''),
    isStudent: (state) => state.userInfo?.role === 'student',
    isTeacher: (state) => state.userInfo?.role === 'teacher',
    isAdmin: (state) => state.userInfo?.role === 'admin',
    canAI: (state) => ['teacher', 'admin'].includes(state.userInfo?.role),
    canAdmin: (state) => state.userInfo?.role === 'admin',
    nickName: (state) => state.userInfo?.nickName || state.userInfo?.username || '用户',
    avatar: (state) => state.userInfo?.avatar || '',
  },
  actions: {
    async login(form) {
      const res = await loginApi(form)
      if (res.code !== 200) {
        ElMessage.error(res.msg)
        return false
      }
      this.token = res.data.token
      localStorage.setItem('token', res.data.token)
      // 登录返回只有 token/username/role/avatar，补充拉取完整用户信息
      const infoRes = await getUserInfoApi()
      if (infoRes.code === 200) {
        this.userInfo = infoRes.data
        localStorage.setItem('userInfo', JSON.stringify(infoRes.data))
      } else {
        this.userInfo = {
          username: res.data.username,
          role: res.data.role,
          avatar: res.data.avatar,
        }
        localStorage.setItem('userInfo', JSON.stringify(this.userInfo))
      }
      ElMessage.success('登录成功')
      return true
    },
    async logout() {
      try {
        await logoutApi()
      } catch {
        // 忽略退出接口错误
      }
      this.token = ''
      this.userInfo = null
      localStorage.removeItem('token')
      localStorage.removeItem('userInfo')
    },
    async updateInfo(data) {
      const res = await updateUserInfoApi(data)
      if (res.code === 200) {
        this.userInfo = res.data
        localStorage.setItem('userInfo', JSON.stringify(res.data))
        return true
      }
      return false
    },
    async changePassword(payload) {
      const res = await changePasswordApi(payload)
      if (res.code !== 200) {
        ElMessage.error(res.msg)
        return false
      }
      ElMessage.success(res.msg || '密码修改成功')
      return true
    },
    hasRole(roles) {
      const list = Array.isArray(roles) ? roles : [roles]
      return list.includes(this.role)
    },
  },
})
