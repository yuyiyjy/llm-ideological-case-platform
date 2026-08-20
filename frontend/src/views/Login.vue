<template>
  <div class="login-page">
    <div class="login-box">
      <div class="brand">
        <div class="brand-logo">
          <el-icon :size="40"><Reading /></el-icon>
        </div>
        <h1>基于大语言模型的<br />课程思政案例库平台</h1>
        <p>智能生成 · 精准检索 · 共建共享</p>
        <div class="brand-tags">
          <el-tag effect="dark" type="primary" round>AI 智能生成</el-tag>
          <el-tag effect="dark" type="success" round>多维度检索</el-tag>
          <el-tag effect="dark" type="warning" round>角色权限管理</el-tag>
        </div>
      </div>
      <div class="form-area">
        <el-card class="login-card">
          <div class="form-title">账号登录</div>
          <el-form ref="formRef" :model="form" :rules="rules" size="large">
            <el-form-item prop="username">
              <el-input v-model="form.username" placeholder="请输入账号" :prefix-icon="User" />
            </el-form-item>
            <el-form-item prop="password">
              <el-input
                v-model="form.password"
                type="password"
                placeholder="请输入密码"
                show-password
                :prefix-icon="Lock"
                @keyup.enter="handleLogin"
              />
            </el-form-item>
            <el-form-item>
              <el-radio-group v-model="form.role" class="role-group">
                <el-radio-button value="student">学生</el-radio-button>
                <el-radio-button value="teacher">教师</el-radio-button>
                <el-radio-button value="admin">管理员</el-radio-button>
              </el-radio-group>
            </el-form-item>
            <el-button type="primary" size="large" class="submit" :loading="loading" @click="handleLogin">
              登 录
            </el-button>
          </el-form>
          <div class="hint">请根据您的身份选择对应角色登录</div>
          <el-divider>测试账号</el-divider>
          <div class="test-accounts">
            <span class="acc" @click="fill('student01', '学生')">学生 student01</span>
            <span class="acc" @click="fill('teacher01', '教师')">教师 teacher01</span>
            <span class="acc" @click="fill('admin01', '管理员')">管理员 admin01</span>
          </div>
          <div class="pwd-hint">密码均为 123456</div>
        </el-card>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { useRouter, useRoute } from 'vue-router'
import { User, Lock } from '@element-plus/icons-vue'
import { ElMessage } from 'element-plus'
import { useUserStore } from '@/stores/user'

const router = useRouter()
const route = useRoute()
const userStore = useUserStore()

const formRef = ref(null)
const loading = ref(false)
const form = reactive({ username: '', password: '', role: 'student' })
const rules = {
  username: [{ required: true, message: '请输入账号', trigger: 'blur' }],
  password: [{ required: true, message: '请输入密码', trigger: 'blur' }],
}

async function handleLogin() {
  await formRef.value.validate()
  loading.value = true
  try {
    const ok = await userStore.login(form)
    if (ok) {
      router.push(route.query.redirect || '/')
    }
  } finally {
    loading.value = false
  }
}

function fill(username, roleName) {
  form.username = username
  form.password = '123456'
  form.role = { 学生: 'student', 教师: 'teacher', 管理员: 'admin' }[roleName]
  ElMessage.info(`已填入${roleName}测试账号`)
}
</script>

<style scoped>
.login-page {
  min-height: 100vh;
  display: flex;
  align-items: center;
  justify-content: center;
  background: linear-gradient(135deg, #1f2d5a 0%, #3a6ea5 55%, #5b8dd6 100%);
  position: relative;
  overflow: hidden;
}
.login-box {
  display: flex;
  background: rgba(255, 255, 255, 0.96);
  border-radius: 16px;
  box-shadow: 0 20px 60px rgba(0, 0, 0, 0.25);
  overflow: hidden;
  width: 860px;
  min-height: 500px;
}
.brand {
  width: 46%;
  background: linear-gradient(150deg, #1e3a8a, #3b82f6);
  color: #fff;
  padding: 48px 36px;
  display: flex;
  flex-direction: column;
  justify-content: center;
  gap: 18px;
}
.brand-logo {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 72px;
  height: 72px;
  background: rgba(255, 255, 255, 0.15);
  border-radius: 16px;
}
.brand h1 {
  font-size: 26px;
  line-height: 1.5;
  margin: 0;
  font-weight: 700;
}
.brand p {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.85);
  margin: 0;
}
.brand-tags {
  display: flex;
  gap: 8px;
  flex-wrap: wrap;
}
.form-area {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px;
}
.login-card {
  width: 100%;
  border: none;
  box-shadow: none;
}
.form-title {
  font-size: 22px;
  font-weight: 700;
  color: #303133;
  text-align: center;
  margin-bottom: 24px;
}
.role-group {
  display: flex;
  justify-content: space-between;
  width: 100%;
}
.submit {
  width: 100%;
  letter-spacing: 6px;
  font-weight: 600;
}
.hint {
  text-align: center;
  font-size: 12px;
  color: #909399;
  margin-top: 12px;
}
.test-accounts {
  display: flex;
  justify-content: center;
  gap: 16px;
}
.acc {
  font-size: 13px;
  color: #409eff;
  cursor: pointer;
  border-bottom: 1px dashed #409eff;
}
.acc:hover {
  color: #1f6fd6;
}
.pwd-hint {
  text-align: center;
  font-size: 12px;
  color: #b0b3b8;
  margin-top: 8px;
}
</style>
