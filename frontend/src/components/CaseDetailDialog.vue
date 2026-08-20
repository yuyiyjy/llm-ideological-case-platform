<template>
  <el-dialog
    :model-value="modelValue"
    :title="detail ? detail.title : '案例详情'"
    width="880px"
    top="6vh"
    destroy-on-close
    @update:model-value="$emit('update:modelValue', $event)"
    @open="loadDetail"
  >
    <div v-loading="loading" class="detail">
      <template v-if="detail">
        <!-- 基础信息 -->
        <div class="info-row">
          <span class="info-item"><el-icon><CollectionTag /></el-icon>案例分类：{{ detail.category }}</span>
          <span class="info-item"><el-icon><Link /></el-icon>来源：{{ detail.source }}</span>
          <span class="info-item"><el-icon><Calendar /></el-icon>发布时间：{{ formatDate(detail.publish_date) }}</span>
          <span class="info-item"><el-icon><Document /></el-icon>版本：{{ detail.version }}</span>
          <span class="info-item">
            <el-icon><Checked /></el-icon>状态：
            <el-tag size="small" :type="statusType(detail.review_status)">{{ detail.review_status }}</el-tag>
          </span>
        </div>

        <!-- 思政元素 -->
        <div class="module">
          <div class="module-title">思政元素</div>
          <div class="module-body">
            <el-tag
              v-for="t in detail.ideological_elements || []"
              :key="t"
              type="success"
              effect="light"
              class="mr-8"
            >{{ t }}</el-tag>
          </div>
        </div>

        <!-- 案例背景 -->
        <div class="module">
          <div class="module-title">案例背景</div>
          <div class="module-body">{{ detail.background }}</div>
        </div>

        <!-- 实施过程 -->
        <div class="module">
          <div class="module-title">实施过程</div>
          <div class="module-body">{{ detail.process }}</div>
        </div>

        <!-- 实施结果 -->
        <div class="module">
          <div class="module-title">实施结果</div>
          <div class="module-body">{{ detail.result }}</div>
        </div>

        <!-- 技术关键词 & 专业知识点 -->
        <div class="module">
          <div class="module-title">技术关键词</div>
          <div class="module-body">
            <el-tag v-for="k in detail.keywords || []" :key="k" effect="plain" class="mr-8">{{ k }}</el-tag>
          </div>
        </div>
        <div class="module">
          <div class="module-title">专业知识点</div>
          <ul class="knowledge-list">
            <li v-for="p in detail.professional_knowledge || []" :key="p">{{ p }}</li>
          </ul>
        </div>

        <!-- 教学价值 -->
        <div class="module">
          <div class="module-title">教学价值 / 配套思考题</div>
          <div class="module-body" style="white-space: pre-wrap">{{ detail.teaching_value }}</div>
        </div>

        <!-- 原始资料链接 -->
        <div v-if="detail.content" class="module">
          <div class="module-title">原始资料</div>
          <el-button type="primary" plain :icon="Link" @click="openPdf">
            查看案例原文（PDF）
          </el-button>
        </div>

        <!-- 相关推荐 -->
        <div v-if="recommends.length" class="recommend">
          <div class="recommend-title">相关推荐</div>
          <div class="recommend-list">
            <div
              v-for="r in recommends"
              :key="r.id"
              class="recommend-card"
              @click="switchTo(r.id)"
            >
              <div class="r-title clamp-2">{{ r.title }}</div>
              <el-tag size="small" type="primary" effect="light">{{ r.category }}</el-tag>
            </div>
          </div>
        </div>

        <!-- 底部操作 -->
        <div class="footer">
          <el-button
            :type="detail.isFavorite ? 'warning' : 'primary'"
            :icon="detail.isFavorite ? 'StarFilled' : 'Star'"
            @click="toggleFav"
          >
            {{ detail.isFavorite ? '取消收藏' : '收藏' }}
          </el-button>
          <el-button type="primary" plain @click="$emit('generate-similar', detail)">
            <el-icon class="mr-4"><MagicStick /></el-icon>生成同类案例
          </el-button>
        </div>
      </template>
      <el-empty v-else-if="!loading" description="案例不存在" />
    </div>
  </el-dialog>
</template>

<script setup>
import { ref, watch } from 'vue'
import { Link } from '@element-plus/icons-vue'
import { getCaseDetailApi, getRecommendApi, addFavoriteApi, removeFavoriteApi } from '@/api'
import { ElMessage } from 'element-plus'

const props = defineProps({
  modelValue: { type: Boolean, default: false },
  caseId: { type: [Number, String], default: null },
})
const emit = defineEmits(['update:modelValue', 'generate-similar'])

const loading = ref(false)
const detail = ref(null)
const recommends = ref([])

const statusTypeMap = {
  待处理: 'info',
  待审核: 'warning',
  审核通过: 'success',
  审核驳回: 'danger',
  需补充: 'warning',
  已归档: 'info',
}
const statusType = (s) => statusTypeMap[s] || 'info'

function formatDate(d) {
  const s = String(d || '')
  return s.length === 8 ? `${s.slice(0, 4)}-${s.slice(4, 6)}-${s.slice(6, 8)}` : s
}

function openPdf() {
  window.open(detail.value?.content, '_blank')
}

async function loadDetail() {
  if (!props.caseId) return
  loading.value = true
  detail.value = null
  recommends.value = []
  try {
    const [d, r] = await Promise.all([
      getCaseDetailApi(props.caseId),
      getRecommendApi(props.caseId),
    ])
    if (d.code === 200) detail.value = d.data
    if (r.code === 200) recommends.value = r.data
  } finally {
    loading.value = false
  }
}

async function switchTo(id) {
  const d = await getCaseDetailApi(id)
  if (d.code === 200) {
    detail.value = d.data
    const r = await getRecommendApi(id)
    recommends.value = r.data || []
  }
}

async function toggleFav() {
  if (!detail.value) return
  if (detail.value.isFavorite) {
    const res = await removeFavoriteApi(detail.value.id)
    if (res.code === 200) detail.value.isFavorite = false
  } else {
    const res = await addFavoriteApi(detail.value.id)
    if (res.code === 200) detail.value.isFavorite = true
  }
}

watch(
  () => props.caseId,
  () => {
    if (props.modelValue && props.caseId) loadDetail()
  }
)
</script>

<style scoped>
.mr-4 {
  margin-right: 4px;
}
.mr-8 {
  margin-right: 8px;
  margin-bottom: 8px;
}
.detail {
  min-height: 200px;
}
.info-row {
  display: flex;
  flex-wrap: wrap;
  gap: 16px;
  padding: 12px 16px;
  background: #f5f7fa;
  border-radius: 8px;
  margin-bottom: 16px;
  align-items: center;
}
.info-item {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 13px;
  color: #606266;
}
.module {
  margin-bottom: 16px;
}
.module-title {
  font-size: 15px;
  font-weight: 600;
  color: #303133;
  padding-left: 10px;
  border-left: 3px solid #409eff;
  margin-bottom: 8px;
}
.module-body {
  font-size: 14px;
  color: #303133;
  line-height: 1.8;
  padding: 0 4px;
}
.knowledge-list {
  margin: 4px 0 0;
  padding-left: 20px;
  line-height: 2;
  font-size: 14px;
  color: #303133;
}
.recommend {
  margin-top: 8px;
}
.recommend-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 8px;
}
.recommend-list {
  display: flex;
  gap: 10px;
  overflow-x: auto;
}
.recommend-card {
  flex: 0 0 200px;
  padding: 10px;
  border: 1px solid #e4e7ed;
  border-radius: 8px;
  cursor: pointer;
  transition: all 0.2s;
}
.recommend-card:hover {
  border-color: #409eff;
  box-shadow: 0 2px 8px rgba(64, 158, 255, 0.15);
}
.r-title {
  font-size: 13px;
  font-weight: 500;
  margin-bottom: 6px;
}
.footer {
  margin-top: 16px;
  padding-top: 16px;
  border-top: 1px solid #f0f2f5;
  display: flex;
  gap: 12px;
}
</style>
