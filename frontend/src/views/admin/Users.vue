<template>
  <div class="card">
    <div class="toolbar">
      <el-input
        v-model="form.keyword"
        placeholder="搜索账号 / 姓名"
        clearable
        :prefix-icon="Search"
        style="width: 220px"
        @keyup.enter="search"
      />
      <el-select v-model="form.role" placeholder="全部角色" clearable style="width: 140px" @change="search">
        <el-option label="学生" value="student" />
        <el-option label="教师" value="teacher" />
        <el-option label="管理员" value="admin" />
      </el-select>
      <el-button type="primary" @click="search">查询</el-button>
    </div>

    <el-table v-loading="loading" :data="list" stripe :header-cell-style="{ textAlign: 'center' }" :cell-style="{ textAlign: 'center' }">
      <el-table-column label="姓名" prop="nickName" width="130" />
      <el-table-column label="账号" prop="username" width="140" />
      <el-table-column label="角色" width="130">
        <template #default="{ row }">
          <el-tag :type="roleTag(row.role)" size="small" effect="light">{{ roleName(row.role) }}</el-tag>
        </template>
      </el-table-column>
      <el-table-column label="启用状态" width="110">
        <template #default="{ row }">
          <el-tag :type="row.status === 0 ? 'success' : 'danger'" size="small">
            {{ row.status === 0 ? '正常' : '已冻结' }}
          </el-tag>
        </template>
      </el-table-column>
      <el-table-column label="手机号" prop="phone" width="140" />
      <el-table-column label="创建时间" prop="createTime" width="120" />
      <el-table-column label="操作" width="120" fixed="right" align="center">
        <template #default="{ row }">
          <el-dropdown trigger="click" @command="(cmd) => handleAction(cmd, row)">
            <el-button size="small" type="primary" plain>
              操作<el-icon class="el-icon--right"><ArrowDown /></el-icon>
            </el-button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item command="role">
                  <el-icon><User /></el-icon>修改角色
                </el-dropdown-item>
                <el-dropdown-item command="freeze">
                  <el-icon><Lock /></el-icon>{{ row.status === 0 ? '冻结账号' : '解除冻结' }}
                </el-dropdown-item>
                <el-dropdown-item command="reset" divided>
                  <el-icon><RefreshRight /></el-icon>重置密码
                </el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </template>
      </el-table-column>
    </el-table>
    <el-empty v-if="!loading && !list.length" description="暂无用户" />
    <div class="pagination">
      <el-pagination
        background
        layout="total, prev, pager, next"
        :total="total"
        :page-size="form.size"
        :current-page="form.page"
        @current-change="pageChange"
      />
    </div>

    <!-- 修改角色弹窗 -->
    <el-dialog v-model="roleDialogVisible" title="修改用户角色" width="420px">
      <div class="role-row">
        <span>用户：<b>{{ roleForm.username }}</b></span>
        <el-select v-model="roleForm.role" style="width: 160px">
          <el-option label="学生" value="student" />
          <el-option label="教师" value="teacher" />
          <el-option label="管理员" value="admin" />
        </el-select>
      </div>
      <template #footer>
        <el-button @click="roleDialogVisible = false">取消</el-button>
        <el-button type="primary" @click="confirmRole">确定</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { Search } from '@element-plus/icons-vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { getUserListApi, updateUserApi, resetUserPwdApi } from '@/api'

const roleNames = { student: '学生', teacher: '教师', admin: '管理员' }
const roleTags = { student: 'success', teacher: 'warning', admin: 'danger' }
const roleName = (r) => roleNames[r] || '未知'
const roleTag = (r) => roleTags[r] || 'info'

const list = ref([])
const total = ref(0)
const loading = ref(false)
const form = reactive({ keyword: '', role: '', page: 1, size: 10 })

async function fetchList() {
  loading.value = true
  try {
    const res = await getUserListApi(form)
    if (res.code === 200) {
      list.value = res.data.records
      total.value = res.data.total
    }
  } finally {
    loading.value = false
  }
}
function search() {
  form.page = 1
  fetchList()
}
function pageChange(p) {
  form.page = p
  fetchList()
}

const roleDialogVisible = ref(false)
const roleForm = reactive({ userId: null, username: '', role: '' })

function handleAction(cmd, row) {
  if (cmd === 'role') {
    roleForm.userId = row.id
    roleForm.username = row.username
    roleForm.role = row.role
    roleDialogVisible.value = true
  } else if (cmd === 'freeze') {
    toggleFreeze(row)
  } else if (cmd === 'reset') {
    resetPwd(row)
  }
}

async function confirmRole() {
  const res = await updateUserApi({ userId: roleForm.userId, role: roleForm.role })
  if (res.code === 200) {
    ElMessage.success(`已将 ${roleForm.username} 的角色改为${roleName(roleForm.role)}`)
    roleDialogVisible.value = false
    fetchList()
  }
}

async function toggleFreeze(row) {
  const target = row.status === 0 ? 1 : 0
  const action = target === 1 ? '冻结' : '解冻'
  try {
    await ElMessageBox.confirm(`确定${action}账号「${row.username}」吗？`, '提示', { type: 'warning' })
  } catch {
    return
  }
  const res = await updateUserApi({ userId: row.id, status: target })
  if (res.code === 200) {
    ElMessage.success(`已${action}`)
    fetchList()
  }
}

async function resetPwd(row) {
  try {
    await ElMessageBox.confirm(`确定重置「${row.username}」的密码吗？重置后为默认密码 123456。`, '提示', { type: 'warning' })
  } catch {
    return
  }
  const res = await resetUserPwdApi(row.id)
  if (res.code === 200) {
    ElMessage.success(res.data?.initialPwd ? `密码已重置为 ${res.data.initialPwd}` : '密码已重置')
  }
}

onMounted(fetchList)
</script>

<style scoped>
.toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
}
.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
.role-row {
  display: flex;
  align-items: center;
  justify-content: space-between;
}
</style>
