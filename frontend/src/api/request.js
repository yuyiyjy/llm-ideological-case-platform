/**
 * axios 封装 —— 预留，等后端接口就绪后启用
 *
 * 当前 api/index.js 使用 Mock 数据，不经过本文件。
 * 联调时：在 api/index.js 中把各函数体替换为 get/post/put/del 调用即可。
 */
import axios from 'axios'
import { ElMessage, ElMessageBox } from 'element-plus'

const service = axios.create({
  baseURL: '/api',
  timeout: 30000,
  withCredentials: true,
})

// 请求拦截器：注入 Token
service.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem('token')
    if (token) {
      config.headers['Authorization'] = `Bearer ${token}`
    }
    if (config.method === 'post' && !config.headers['Content-Type']) {
      config.headers['Content-Type'] = 'application/json'
    }
    return config
  },
  (error) => Promise.reject(error)
)

// 响应拦截器：统一处理 code/401/403/500
service.interceptors.response.use(
  (response) => {
    const res = response.data
    if (res.code !== 200) {
      if (res.code === 401) {
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
        ElMessage.warning('登录已过期，请重新登录')
        window.location.href = '/login'
      } else if (res.code === 403) {
        ElMessageBox.alert('无操作权限', '提示', { confirmButtonText: '知道了', type: 'warning' })
      } else if (res.code === 500) {
        ElMessage.error('服务异常，请稍后重试')
      } else {
        ElMessage.error(res.msg || '请求失败')
      }
      return Promise.reject(new Error(res.msg || 'Error'))
    }
    return res
  },
  (error) => {
    if (error.response) {
      const { status } = error.response
      if (status === 401) {
        localStorage.removeItem('token')
        localStorage.removeItem('userInfo')
        window.location.href = '/login'
      } else if (status === 403) {
        ElMessageBox.alert('无操作权限', '提示', { confirmButtonText: '知道了', type: 'warning' })
      } else if (status === 500) {
        ElMessage.error('服务异常，请稍后重试')
      } else {
        ElMessage.error('请求失败')
      }
    } else if (error.code === 'ECONNABORTED') {
      ElMessage.error('请求超时')
    } else {
      ElMessage.error('网络异常，请检查网络连接')
    }
    return Promise.reject(error)
  }
)

export function get(url, params, config) {
  return service.get(url, { params, ...config })
}
export function post(url, data, config) {
  return service.post(url, data, config)
}
export function put(url, data, config) {
  return service.put(url, data, config)
}
export function del(url, config) {
  return service.delete(url, config)
}

export default service
