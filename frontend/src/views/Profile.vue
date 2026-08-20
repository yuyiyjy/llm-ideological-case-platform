<template>
  <div class="page">
    <!-- 个人信息卡 -->
    <div class="info-card card">
      <el-avatar :size="72" :src="user.avatar" class="avatar">{{ user.nickName.charAt(0) }}</el-avatar>
      <div class="info-main">
        <div class="name-row">
          <span class="name">{{ user.nickName }}</span>
          <el-tag :type="roleTag" size="small" effect="light">{{ roleName }}</el-tag>
        </div>
        <div class="info-line">账号：{{ user.userInfo?.username }}</div>
        <div class="info-line">简介：{{ user.userInfo?.intro || '这个人很懒，还没有填写简介' }}</div>
        <div class="info-line">手机号：{{ user.userInfo?.phone || '未填写' }}</div>
      </div>
      <div class="info-actions">
        <el-button @click="editVisible = true">
          <el-icon class="mr-4"><Edit /></el-icon>编辑资料
        </el-button>
        <el-button @click="pwdVisible = true">
          <el-icon class="mr-4"><Key /></el-icon>修改密码
        </el-button>
      </div>
    </div>

    <!-- 标签切换面板 -->
    <el-tabs v-model="activeTab" class="tabs">
      <el-tab-pane label="我的收藏" name="favorites">
        <el-row v-loading="favLoading" :gutter="16">
          <el-col v-for="c in favorites" :key="c.id" :xs="24" :sm="12" :md="8" class="col">
            <CaseCard :item="c" @detail="openDetail" @favorite="removeFav" />
          </el-col>
        </el-row>
        <el-empty v-if="!favLoading && !favorites.length" description="暂无收藏，去案例库逛逛吧" />
        <div class="pagination">
          <el-pagination
            v-if="favTotal > favPageSize"
            background
            layout="total, prev, pager, next"
            :total="favTotal"
            :page-size="favPageSize"
            :current-page="favPage"
            @current-change="loadFavorites"
          />
        </div>
      </el-tab-pane>

      <el-tab-pane v-if="user.canAI" label="我的生成记录" name="records">
        <el-table v-loading="recLoading" :data="records" stripe :header-cell-style="{ textAlign: 'center' }" :cell-style="{ textAlign: 'center' }">
          <el-table-column label="生成时间" width="150">
            <template #default="{ row }">{{ row.createTime }}</template>
          </el-table-column>
          <el-table-column label="适用专业" width="150">
            <template #default="{ row }">
              <span class="clamp-1">{{ (row.profession || []).join(' / ') }}</span>
            </template>
          </el-table-column>
          <el-table-column label="思政方向" width="110">
            <template #default="{ row }">
              <el-tag size="small" type="success" effect="light">{{ row.ideological_direction }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="内容预览" min-width="220">
            <template #default="{ row }">
              <div class="clamp-2 preview">{{ row.contentPreview }}</div>
            </template>
          </el-table-column>
          <el-table-column label="操作" width="160">
            <template #default="{ row }">
              <el-button size="small" @click="viewRecord(row)">查看</el-button>
              <el-button size="small" type="danger" plain @click="deleteRecord(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
      </el-tab-pane>

      <el-tab-pane v-if="user.canAI" label="我提交的待审核案例" name="submits">
        <el-table v-loading="subLoading" :data="submits" stripe :header-cell-style="{ textAlign: 'center' }" :cell-style="{ textAlign: 'center' }">
          <el-table-column label="案例标题" prop="title" min-width="200" />
          <el-table-column label="提交时间" prop="submitTime" width="160" />
          <el-table-column label="审核状态" width="120">
            <template #default="{ row }">
              <el-tag :type="statusMap[row.status].type" size="small">
                {{ statusMap[row.status].name }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="驳回原因" min-width="160">
            <template #default="{ row }">
              <span class="reject">{{ row.status === '审核驳回' ? row.rejectReason : '-' }}</span>
            </template>
          </el-table-column>
        </el-table>
        <el-empty v-if="!subLoading && !submits.length" description="暂无提交记录" />
      </el-tab-pane>
    </el-tabs>

    <!-- 编辑资料 -->
    <el-dialog v-model="editVisible" title="编辑个人资料" width="520px">
      <el-form ref="editFormRef" :model="editForm" label-width="80px">
        <el-form-item label="昵称">
          <el-input v-model="editForm.nickName" placeholder="请输入昵称" />
        </el-form-item>
        <el-form-item label="手机号">
          <el-input v-model="editForm.phone" placeholder="请输入手机号" />
        </el-form-item>
        <el-form-item label="个人简介">
          <el-input v-model="editForm.intro" type="textarea" :rows="3" placeholder="一句话介绍自己" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" :loading="editSaving" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>

    <!-- 修改密码 -->
    <el-dialog v-model="pwdVisible" title="修改密码" width="480px">
      <el-form ref="pwdFormRef" :model="pwdForm" :rules="pwdRules" label-width="90px">
        <el-form-item label="原密码" prop="oldPwd">
          <el-input v-model="pwdForm.oldPwd" type="password" show-password placeholder="请输入原密码" />
        </el-form-item>
        <el-form-item label="新密码" prop="newPwd">
          <el-input v-model="pwdForm.newPwd" type="password" show-password placeholder="请输入新密码" />
        </el-form-item>
        <el-form-item label="确认密码" prop="confirmPwd">
          <el-input v-model="pwdForm.confirmPwd" type="password" show-password placeholder="请再次输入新密码" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pwdVisible = false">取消</el-button>
        <el-button type="primary" :loading="pwdSaving" @click="savePwd">确认修改</el-button>
      </template>
    </el-dialog>

    <!-- 收藏详情弹窗 -->
    <CaseDetailDialog v-model="detailVisible" :case-id="detailId" />
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import {
  getFavoriteListApi,
  getAiRecordListApi,
  getSubmitListApi,
  removeFavoriteApi,
  deleteAiRecordApi,
} from '@/api'
import { useUserStore } from '@/stores/user'
import CaseCard from '@/components/CaseCard.vue'
import CaseDetailDialog from '@/components/CaseDetailDialog.vue'

const user = useUserStore()

const roleMap = { student: { name: '学生', tag: 'success' }, teacher: { name: '教师', tag: 'warning' }, admin: { name: '管理员', tag: 'danger' } }
const roleName = roleMap[user.role]?.name || '未知'
const roleTag = roleMap[user.role]?.tag || 'info'

const statusMap = {
  待处理: { name: '待处理', type: 'info' },
  待审核: { name: '待审核', type: 'warning' },
  审核通过: { name: '审核通过', type: 'success' },
  审核驳回: { name: '审核驳回', type: 'danger' },
  需补充: { name: '需补充', type: 'warning' },
  已归档: { name: '已归档', type: 'info' },
}

// 收藏
const activeTab = ref('favorites')
const favorites = ref([])
const favTotal = ref(0)
const favPage = ref(1)
const favPageSize = 9
const favLoading = ref(false)

async function loadFavorites(p = 1) {
  favPage.value = p
  favLoading.value = true
  try {
    const res = await getFavoriteListApi({ page: p, size: favPageSize })
    if (res.code === 200) {
      favorites.value = res.data.records
      favTotal.value = res.data.total
    }
  } finally {
    favLoading.value = false
  }
}

async function removeFav(c) {
  const res = await removeFavoriteApi(c.id)
  if (res.code === 200) {
    ElMessage.success('已取消收藏')
    loadFavorites(favPage.value)
  }
}

// 生成记录
const records = ref([])
const recLoading = ref(false)
async function loadRecords() {
  recLoading.value = true
  try {
    const res = await getAiRecordListApi({ page: 1, size: 20 })
    if (res.code === 200) records.value = res.data.records
  } finally {
    recLoading.value = false
  }
}
function viewRecord(row) {
  ElMessageBox.alert(row.content, '生成内容', { confirmButtonText: '关闭', dangerouslyUseHTMLString: false })
}
async function deleteRecord(row) {
  try {
    await ElMessageBox.confirm('确定删除该记录吗？', '提示', { type: 'warning' })
  } catch {
    return
  }
  await deleteAiRecordApi(row.id)
  ElMessage.success('已删除')
  loadRecords()
}

// 我提交的
const submits = ref([])
const subLoading = ref(false)
async function loadSubmits() {
  subLoading.value = true
  try {
    const res = await getSubmitListApi({ page: 1, size: 20 })
    if (res.code === 200) submits.value = res.data.records
  } finally {
    subLoading.value = false
  }
}

// 编辑资料
const editVisible = ref(false)
const editSaving = ref(false)
const editForm = reactive({ nickName: '', phone: '', intro: '' })
async function saveEdit() {
  editSaving.value = true
  try {
    const ok = await user.updateInfo(editForm)
    if (ok) {
      ElMessage.success('资料已更新')
      editVisible.value = false
    }
  } finally {
    editSaving.value = false
  }
}

// 修改密码
const pwdVisible = ref(false)
const pwdSaving = ref(false)
const pwdForm = reactive({ oldPwd: '', newPwd: '', confirmPwd: '' })
const pwdRules = {
  oldPwd: [{ required: true, message: '请输入原密码', trigger: 'blur' }],
  newPwd: [
    { required: true, message: '请输入新密码', trigger: 'blur' },
    { min: 6, message: '密码至少 6 位', trigger: 'blur' },
  ],
  confirmPwd: [
    { required: true, message: '请再次输入新密码', trigger: 'blur' },
    {
      validator: (rule, value, callback) => {
        if (value !== pwdForm.newPwd) callback(new Error('两次输入的密码不一致'))
        else callback()
      },
      trigger: 'blur',
    },
  ],
}
async function savePwd() {
  const ok = await user.changePassword({ oldPwd: pwdForm.oldPwd, newPwd: pwdForm.newPwd })
  if (ok) {
    pwdVisible.value = false
    pwdForm.oldPwd = ''
    pwdForm.newPwd = ''
    pwdForm.confirmPwd = ''
  }
}

// 收藏详情
const detailVisible = ref(false)
const detailId = ref(null)
function openDetail(c) {
  detailId.value = c.id
  detailVisible.value = true
}

onMounted(() => {
  editForm.nickName = user.userInfo?.nickName || ''
  editForm.phone = user.userInfo?.phone || ''
  editForm.intro = user.userInfo?.intro || ''
  loadFavorites()
  if (user.canAI) {
    loadRecords()
    loadSubmits()
  }
})
</script>

<style scoped>
.mr-4 {
  margin-right: 4px;
}
.info-card {
  display: flex;
  align-items: center;
  gap: 24px;
  padding: 28px;
}
.avatar {
  background: #409eff;
  flex-shrink: 0;
}
.info-main {
  flex: 1;
}
.name-row {
  display: flex;
  align-items: center;
  gap: 10px;
  margin-bottom: 8px;
}
.name {
  font-size: 20px;
  font-weight: 700;
}
.info-line {
  font-size: 13px;
  color: #606266;
  line-height: 1.9;
}
.info-actions {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.tabs {
  margin-top: 20px;
  background: #fff;
  border-radius: 8px;
  padding: 0 20px 20px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}
.col {
  margin-bottom: 16px;
}
.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}
.preview {
  font-size: 13px;
  color: #606266;
}
.reject {
  font-size: 12px;
  color: #f56c6c;
}
</style>
