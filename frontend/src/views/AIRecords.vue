<template>
  <div class="page">
    <div class="page-header">
      <div class="page-title">我的生成记录</div>
      <el-button type="primary" @click="$router.push('/ai-generate')">
        <el-icon class="mr-4"><Plus /></el-icon>新建生成
      </el-button>
    </div>

    <div class="card">
      <el-table v-loading="loading" :data="list" stripe :header-cell-style="{ textAlign: 'center' }" :cell-style="{ textAlign: 'center' }">
        <el-table-column label="生成时间" width="160">
          <template #default="{ row }">{{ row.createTime }}</template>
        </el-table-column>
        <el-table-column label="适用专业" width="150">
          <template #default="{ row }">
            <span class="clamp-1">{{ (row.profession || []).join(' / ') }}</span>
          </template>
        </el-table-column>
        <el-table-column label="思政方向" width="120">
          <template #default="{ row }">
            <el-tag size="small" type="success" effect="light">{{ row.ideological_direction }}</el-tag>
          </template>
        </el-table-column>
        <el-table-column label="内容预览" min-width="240">
          <template #default="{ row }">
            <div class="preview clamp-2">{{ row.contentPreview }}</div>
          </template>
        </el-table-column>
        <el-table-column label="操作" width="220" fixed="right">
          <template #default="{ row }">
            <el-button size="small" @click="viewDetail(row)">查看完整</el-button>
            <el-button size="small" type="primary" plain @click="editRegenerate(row)">编辑重生成</el-button>
            <el-button size="small" type="danger" plain @click="removeRecord(row)">删除</el-button>
          </template>
        </el-table-column>
      </el-table>
      <el-empty v-if="!loading && !list.length" description="暂无生成记录" class="mt-24" />
      <div class="pagination">
        <el-pagination
          background
          layout="total, prev, pager, next"
          :total="total"
          :page-size="form.size"
          :current-page="form.page"
          @current-change="onPageChange"
        />
      </div>
    </div>

    <!-- 查看完整内容 -->
    <el-dialog v-model="viewVisible" title="生成内容" width="760px" top="6vh">
      <div class="view-content" style="white-space: pre-wrap">{{ viewRecord?.content }}</div>
      <template #footer>
        <el-button @click="copyContent">复制文本</el-button>
        <el-button type="primary" @click="viewVisible = false">关闭</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getAiRecordListApi, deleteAiRecordApi } from '@/api'
import { useAppStore } from '@/stores/app'
import { ElMessage, ElMessageBox } from 'element-plus'

const router = useRouter()
const appStore = useAppStore()

const list = ref([])
const total = ref(0)
const loading = ref(false)
const form = reactive({ page: 1, size: 10 })

const viewVisible = ref(false)
const viewRecord = ref(null)

async function fetchList() {
  loading.value = true
  try {
    const res = await getAiRecordListApi(form)
    if (res.code === 200) {
      list.value = res.data.records
      total.value = res.data.total
    }
  } finally {
    loading.value = false
  }
}

function onPageChange(p) {
  form.page = p
  fetchList()
}

function viewDetail(row) {
  viewRecord.value = row
  viewVisible.value = true
}

async function copyContent() {
  try {
    await navigator.clipboard.writeText(viewRecord.value?.content || '')
    ElMessage.success('已复制')
  } catch {
    ElMessage.error('复制失败')
  }
}

function editRegenerate(row) {
  appStore.setAiPrefill({
    ideological: row.ideological_direction || '',
    knowledge: row.knowledge,
    profession: row.profession || [],
    length: row.length,
  })
  router.push('/ai-generate')
}

async function removeRecord(row) {
  try {
    await ElMessageBox.confirm('确定删除该生成记录吗？', '提示', { type: 'warning' })
  } catch {
    return
  }
  const res = await deleteAiRecordApi(row.id)
  if (res.code === 200) {
    ElMessage.success(res.msg || '删除成功')
    fetchList()
  }
}

onMounted(fetchList)
</script>

<style scoped>
.mr-4 {
  margin-right: 4px;
}
.preview {
  font-size: 13px;
  color: #606266;
  line-height: 1.5;
}
.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 16px;
}
.view-content {
  max-height: 60vh;
  overflow-y: auto;
  font-size: 14px;
  line-height: 1.9;
  background: #fafbfc;
  border-radius: 8px;
  padding: 16px;
  white-space: pre-wrap;
}
</style>
