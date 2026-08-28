<template>
  <div class="card">
    <el-tabs v-model="activeTab">
      <!-- 审核管理 -->
      <el-tab-pane label="审核管理" name="audit">
        <div class="toolbar">
          <el-radio-group v-model="statusFilter" @change="reloadAudit">
            <el-radio-button value="待审核">待审核</el-radio-button>
            <el-radio-button value="审核通过">审核通过</el-radio-button>
            <el-radio-button value="审核驳回">审核驳回</el-radio-button>
          </el-radio-group>
        </div>
        <el-table v-loading="auditLoading" :data="auditList" stripe>
          <el-table-column label="案例标题" min-width="200" align="center">
            <template #default="{ row }">
              <el-link type="primary" :underline="false" @click="viewSubmit(row)">{{ row.title }}</el-link>
            </template>
          </el-table-column>
          <el-table-column label="提交人" prop="submitterName" width="100" align="center" />
          <el-table-column label="案例分类" prop="category" width="110" align="center" />
          <el-table-column label="提交时间" prop="submitTime" width="160" align="center" />
          <el-table-column label="审核状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="statusType(row.status)" size="small">{{ row.status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="驳回原因" min-width="140" align="center">
            <template #default="{ row }">
              <span class="reject">{{ row.status === '审核驳回' ? row.rejectReason : '-' }}</span>
            </template>
          </el-table-column>
          <el-table-column label="审核操作" width="200" fixed="right" align="center">
            <template #default="{ row }">
              <template v-if="row.status === '待审核'">
                <el-button size="small" type="success" :icon="Check" @click="passAudit(row)">通过</el-button>
                <el-button size="small" type="danger" plain :icon="Close" @click="openReject(row)">驳回</el-button>
              </template>
              <el-tag v-else size="small" type="info">已处理</el-tag>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination">
          <el-pagination
            background
            layout="total, prev, pager, next"
            :total="auditTotal"
            :page-size="auditForm.size"
            :current-page="auditForm.page"
            @current-change="auditPageChange"
          />
        </div>
      </el-tab-pane>

      <!-- 全部案例管理 -->
      <el-tab-pane label="全部案例管理" name="all">
        <div class="toolbar">
          <el-button type="primary" @click="importVisible = true">
            <el-icon class="mr-4"><Upload /></el-icon>批量导入
          </el-button>
          <el-button @click="exportCases">
            <el-icon class="mr-4"><Download /></el-icon>导出案例
          </el-button>
        </div>
        <el-table v-loading="caseLoading" :data="caseList" stripe>
          <el-table-column label="标题" prop="title" min-width="200" align="center" />
          <el-table-column label="案例分类" prop="category" width="110" align="center" />
          <el-table-column label="专业" width="150" align="center">
            <template #default="{ row }">
              <span class="clamp-1">{{ (row.profession || []).join(' / ') }}</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100" align="center">
            <template #default="{ row }">
              <el-tag :type="statusType(row.review_status)" size="small">{{ row.review_status }}</el-tag>
            </template>
          </el-table-column>
          <el-table-column label="来源" prop="source" width="100" align="center" />
          <el-table-column label="发布时间" width="100" align="center">
            <template #default="{ row }">{{ formatDate(row.publish_date) }}</template>
          </el-table-column>
          <el-table-column label="操作" width="220" fixed="right" align="center">
            <template #default="{ row }">
              <el-button size="small" @click="openEdit(row)">编辑</el-button>
              <el-button
                size="small"
                :type="row.review_status === '已归档' ? 'success' : 'warning'"
                plain
                @click="toggleStatus(row)"
              >
                {{ row.review_status === '已归档' ? '恢复上架' : '归档' }}
              </el-button>
              <el-button size="small" type="danger" plain @click="removeCase(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>
        <div class="pagination">
          <el-pagination
            background
            layout="total, prev, pager, next"
            :total="caseTotal"
            :page-size="caseForm.size"
            :current-page="caseForm.page"
            @current-change="casePageChange"
          />
        </div>
      </el-tab-pane>
    </el-tabs>

    <!-- 查看提交详情 -->
    <el-dialog v-model="viewVisible" title="提交详情" width="720px">
      <el-descriptions :column="2" border size="small">
        <el-descriptions-item label="标题">{{ viewRow?.title }}</el-descriptions-item>
        <el-descriptions-item label="提交人">{{ viewRow?.submitterName }}</el-descriptions-item>
        <el-descriptions-item label="案例分类">{{ viewRow?.category }}</el-descriptions-item>
        <el-descriptions-item label="专业">{{ (viewRow?.profession || []).join(' / ') }}</el-descriptions-item>
        <el-descriptions-item label="提交时间">{{ viewRow?.submitTime }}</el-descriptions-item>
        <el-descriptions-item label="来源">{{ viewRow?.source }}</el-descriptions-item>
      </el-descriptions>
      <div class="view-body">
        <p><strong>思政元素：</strong>{{ (viewRow?.ideological_elements || []).join('、') }}</p>
        <p><strong>案例背景：</strong>{{ viewRow?.background }}</p>
        <p><strong>实施过程：</strong>{{ viewRow?.process }}</p>
        <p><strong>实施结果：</strong>{{ viewRow?.result }}</p>
        <p><strong>教学价值：</strong>{{ viewRow?.teaching_value }}</p>
      </div>
    </el-dialog>

    <!-- 驳回弹窗 -->
    <el-dialog v-model="rejectVisible" title="驳回案例" width="480px">
      <el-input
        v-model="rejectReason"
        type="textarea"
        :rows="4"
        placeholder="请填写驳回原因，将反馈给提交人"
      />
      <template #footer>
        <el-button @click="rejectVisible = false">取消</el-button>
        <el-button type="danger" @click="confirmReject">确认驳回</el-button>
      </template>
    </el-dialog>

    <!-- 编辑案例 -->
    <el-dialog v-model="editVisible" title="编辑案例" width="720px">
      <el-form :model="editForm" label-width="100px">
        <el-form-item label="标题">
          <el-input v-model="editForm.title" />
        </el-form-item>
        <el-form-item label="案例分类">
          <el-select v-model="editForm.category" style="width: 100%">
            <el-option v-for="c in CASE_CATEGORIES" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>
        <el-form-item label="来源">
          <el-input v-model="editForm.source" />
        </el-form-item>
        <el-form-item label="专业">
          <el-select v-model="editForm.profession" multiple filterable style="width: 100%">
            <el-option v-for="p in PROFESSIONS" :key="p" :label="p" :value="p" />
          </el-select>
        </el-form-item>
        <el-form-item label="背景">
          <el-input v-model="editForm.background" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="实施过程">
          <el-input v-model="editForm.process" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="实施结果">
          <el-input v-model="editForm.result" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="editVisible = false">取消</el-button>
        <el-button type="primary" @click="saveEdit">保存</el-button>
      </template>
    </el-dialog>

    <!-- 批量导入 -->
    <el-dialog v-model="importVisible" title="批量导入案例" width="560px">
      <el-upload
        drag
        :auto-upload="false"
        :limit="1"
        accept=".csv,.json"
        :on-change="onImportFile"
        :on-remove="() => (importFile = null)"
      >
        <el-icon class="upload-icon" :size="48"><UploadFilled /></el-icon>
        <div class="el-upload__text">将 CSV / JSON 文件拖到此处，或<em>点击选择</em></div>
        <template #tip>
          <div class="el-upload__tip">支持 CSV（列：title,category,profession,content 等）或 JSON 数组</div>
        </template>
      </el-upload>
      <template #footer>
        <el-button @click="importVisible = false">取消</el-button>
        <el-button type="primary" :loading="importing" :disabled="!importFile" @click="doImport">
          开始导入
        </el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Check, Close } from '@element-plus/icons-vue'
import {
  getReviewListApi,
  reviewCaseApi,
  getCaseListApi,
  updateCaseApi,
  deleteCaseApi,
  importCasesApi,
  exportCasesApi,
} from '@/api'
import { CASE_CATEGORIES, PROFESSIONS } from '@/api/mockData'

const statusTypeMap = {
  待处理: 'info', 待审核: 'warning', 审核通过: 'success',
  审核驳回: 'danger', 需补充: 'warning', 已归档: 'info',
}
const statusType = (s) => statusTypeMap[s] || 'info'

function formatDate(d) {
  const s = String(d || '')
  return s.length === 8 ? `${s.slice(0, 4)}-${s.slice(4, 6)}-${s.slice(6, 8)}` : s
}

// ===== 审核管理 =====
const activeTab = ref('audit')
const statusFilter = ref('待审核')
const auditList = ref([])
const auditTotal = ref(0)
const auditLoading = ref(false)
const auditForm = reactive({ page: 1, size: 10 })

async function loadAudit() {
  auditLoading.value = true
  try {
    const res = await getReviewListApi({ page: auditForm.page, size: auditForm.size, status: statusFilter.value })
    if (res.code === 200) {
      auditList.value = res.data.records
      auditTotal.value = res.data.total
    }
  } finally {
    auditLoading.value = false
  }
}
function reloadAudit() {
  auditForm.page = 1
  loadAudit()
}
function auditPageChange(p) {
  auditForm.page = p
  loadAudit()
}

const viewVisible = ref(false)
const viewRow = ref(null)
function viewSubmit(row) {
  viewRow.value = row
  viewVisible.value = true
}

async function passAudit(row) {
  try {
    await ElMessageBox.confirm(`确认通过「${row.title}」吗？通过后将进入案例库。`, '审核确认', { type: 'warning' })
  } catch {
    return
  }
  const res = await reviewCaseApi({ caseSubmitId: row.id, status: '审核通过' })
  if (res.code === 200) {
    ElMessage.success('已通过，案例已入库')
    loadAudit()
  }
}

const rejectVisible = ref(false)
const rejectReason = ref('')
const rejectRow = ref(null)
function openReject(row) {
  rejectRow.value = row
  rejectReason.value = ''
  rejectVisible.value = true
}
async function confirmReject() {
  if (!rejectReason.value.trim()) {
    ElMessage.warning('请填写驳回原因')
    return
  }
  const res = await reviewCaseApi({ caseSubmitId: rejectRow.value.id, status: '审核驳回', rejectReason: rejectReason.value })
  if (res.code === 200) {
    ElMessage.success('已驳回')
    rejectVisible.value = false
    loadAudit()
  }
}

// ===== 全部案例管理 =====
const caseList = ref([])
const caseTotal = ref(0)
const caseLoading = ref(false)
const caseForm = reactive({ page: 1, size: 10 })

async function loadCases() {
  caseLoading.value = true
  try {
    const res = await getCaseListApi({ page: caseForm.page, size: caseForm.size, includeAll: true })
    if (res.code === 200) {
      caseList.value = res.data.records
      caseTotal.value = res.data.total
    }
  } finally {
    caseLoading.value = false
  }
}
function casePageChange(p) {
  caseForm.page = p
  loadCases()
}

const editVisible = ref(false)
const editForm = reactive({ id: null, title: '', category: '', source: '', profession: [], background: '', process: '', result: '' })
function openEdit(row) {
  Object.assign(editForm, {
    id: row.id,
    title: row.title,
    category: row.category,
    source: row.source,
    profession: row.profession || [],
    background: row.background,
    process: row.process,
    result: row.result,
  })
  editVisible.value = true
}
async function saveEdit() {
  const res = await updateCaseApi(editForm.id, editForm)
  if (res.code === 200) {
    ElMessage.success('保存成功')
    editVisible.value = false
    loadCases()
  }
}

async function toggleStatus(row) {
  const target = row.review_status === '已归档' ? '审核通过' : '已归档'
  const action = target === '已归档' ? '归档' : '恢复上架'
  try {
    await ElMessageBox.confirm(`确定${action}「${row.title}」吗？`, '提示', { type: 'warning' })
  } catch {
    return
  }
  const res = await updateCaseApi(row.id, { review_status: target })
  if (res.code === 200) {
    ElMessage.success(`已${action}`)
    loadCases()
  }
}

async function removeCase(row) {
  try {
    await ElMessageBox.confirm(`确定删除「${row.title}」吗？删除后不可恢复。`, '删除确认', { type: 'warning' })
  } catch {
    return
  }
  const res = await deleteCaseApi(row.id)
  if (res.code === 200) {
    ElMessage.success('已删除')
    loadCases()
  }
}

// ===== 导入导出 =====
const importVisible = ref(false)
const importFile = ref(null)
const importing = ref(false)
function onImportFile(file) {
  importFile.value = file.raw
}
async function doImport() {
  importing.value = true
  try {
    const text = await importFile.value.text()
    let rows = []
    if (importFile.value.name.endsWith('.json')) {
      rows = JSON.parse(text)
    } else {
      const lines = text.split(/\r?\n/).filter(Boolean)
      const header = lines[0].split(',').map((h) => h.trim())
      rows = lines.slice(1).map((line) => {
        const cells = line.split(',')
        const obj = {}
        header.forEach((h, i) => (obj[h] = (cells[i] || '').trim()))
        return obj
      })
    }
    const res = await importCasesApi(rows)
    if (res.code === 200) {
      ElMessage.success(res.msg)
      importVisible.value = false
      importFile.value = null
      loadCases()
    }
  } catch (e) {
    ElMessage.error('文件解析失败：' + e.message)
  } finally {
    importing.value = false
  }
}

async function exportCases() {
  const res = await exportCasesApi()
  if (res.code === 200) ElMessage.success(res.msg)
}

onMounted(() => {
  loadAudit()
  loadCases()
})
</script>

<style scoped>
.mr-4 {
  margin-right: 4px;
}
.toolbar {
  display: flex;
  gap: 10px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}
.reject {
  font-size: 12px;
  color: #f56c6c;
}
.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
.view-body {
  margin-top: 16px;
  background: #fafbfc;
  border-radius: 8px;
  padding: 16px;
  font-size: 13px;
  line-height: 1.8;
  max-height: 300px;
  overflow-y: auto;
}
.upload-icon {
  color: #c0c4cc;
}
.clamp-1 {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
</style>
