<template>
  <div class="page home">
    <!-- 横幅 -->
    <div class="hero">
      <div class="hero-content">
        <h1>基于大语言模型的课程思政案例库信息化平台</h1>
        <p>汇聚优质课程思政案例，AI 赋能智慧备课，助力知识传授与价值塑造同频共振。</p>
      </div>
    </div>

    <!-- 热门案例 -->
    <div class="section">
      <div class="section-header">
        <div class="section-title">热门案例推荐</div>
        <el-button text type="primary" @click="$router.push('/cases')">更多 &gt;</el-button>
      </div>
      <div v-loading="hotLoading" class="hot-list">
        <div v-for="c in hotCases" :key="c.id" class="hot-card card card-hover" @click="openDetail(c)">
          <div class="hot-title">{{ c.title }}</div>
          <div class="hot-tags">
            <el-tag v-for="t in tagsOf(c).slice(0, 2)" :key="t" size="small" effect="plain">{{ t }}</el-tag>
          </div>
          <div class="hot-summary clamp-2">{{ c.teaching_value || c.background }}</div>
          <div class="hot-meta">
            <el-tag size="small" type="primary" effect="light">{{ c.category }}</el-tag>
            <span class="views"><el-icon><View /></el-icon>{{ c.views }}</span>
          </div>
        </div>
        <el-empty v-if="!hotLoading && !hotCases.length" description="暂无热门案例" />
      </div>
    </div>

    <!-- 平台数据 -->
    <div class="section">
      <div class="section-title">平台数据</div>
      <div class="stat-grid">
        <div class="stat-card card">
          <div class="stat-num">{{ indexData.totalCases }}</div>
          <div class="stat-label">案例总数</div>
        </div>
        <div class="stat-card card">
          <div class="stat-num">{{ indexData.totalTags }}</div>
          <div class="stat-label">思政标签数量</div>
        </div>
        <div class="stat-card card">
          <div class="stat-num">{{ indexData.totalAiGenerated }}</div>
          <div class="stat-label">AI 生成总量</div>
        </div>
      </div>
    </div>

    <CaseDetailDialog
      v-model="detailVisible"
      :case-id="detailId"
      @generate-similar="goGenerate"
    />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { getHotCaseApi, getHomeIndexApi } from '@/api'
import { useAppStore } from '@/stores/app'
import CaseDetailDialog from '@/components/CaseDetailDialog.vue'

const router = useRouter()
const appStore = useAppStore()

const hotCases = ref([])
const hotLoading = ref(false)
const indexData = ref({ totalCases: 0, totalTags: 0, totalAiGenerated: 0 })

const detailVisible = ref(false)
const detailId = ref(null)

function tagsOf(c) {
  return c.ideological_elements || []
}

function openDetail(c) {
  detailId.value = c.id
  detailVisible.value = true
}

/** 详情弹窗「生成同类案例」：预填思政标签为该案例的首个思政元素 */
function goGenerate(c) {
  appStore.setAiPrefill({
    ideological: (c.ideological_elements && c.ideological_elements[0]) || '',
    knowledge: '',
    profession: c.profession || [],
    length: 'medium',
  })
  router.push('/ai-generate')
}

onMounted(async () => {
  hotLoading.value = true
  try {
    const [h, d] = await Promise.all([getHotCaseApi(), getHomeIndexApi()])
    hotCases.value = h.data || []
    indexData.value = d.data || {}
  } finally {
    hotLoading.value = false
  }
})
</script>

<style scoped>
.hero {
  border-radius: 12px;
  background: linear-gradient(120deg, #1e3a8a 0%, #3b82f6 60%, #60a5fa 100%);
  padding: 56px 40px;
  color: #fff;
  position: relative;
  overflow: hidden;
}
.hero-content h1 {
  font-size: 30px;
  margin: 0 0 16px;
}
.hero-content p {
  font-size: 15px;
  color: rgba(255, 255, 255, 0.9);
  max-width: 560px;
  margin: 0;
  line-height: 1.7;
}
.section {
  margin-top: 28px;
}
.section-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.section-title {
  font-size: 19px;
  font-weight: 700;
  margin-bottom: 16px;
  position: relative;
  padding-left: 12px;
}
.section-title::before {
  content: '';
  position: absolute;
  left: 0;
  top: 2px;
  bottom: 2px;
  width: 4px;
  background: #409eff;
  border-radius: 2px;
}
.hot-list {
  display: flex;
  gap: 16px;
  overflow-x: auto;
  padding-bottom: 8px;
  align-items: stretch;
}
.hot-card {
  flex: none;
  width: 250px;
  min-width: 250px;
  max-width: 250px;
  cursor: pointer;
  padding: 16px;
  display: flex;
  flex-direction: column;
}
.hot-title {
  font-size: 15px;
  font-weight: 600;
  line-height: 22px;
  height: 22px; /* 单行固定高度，长标题省略号截断 */
  overflow: hidden;
  white-space: nowrap;
  text-overflow: ellipsis;
  text-align: center;
  margin-bottom: 8px;
}
.hot-tags {
  display: flex;
  gap: 6px;
  margin-bottom: 8px;
}
.hot-summary {
  flex: 1;
  font-size: 12px;
  color: #606266;
  line-height: 1.6;
  margin-bottom: 10px;
}
.hot-meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
}
.views {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  font-size: 12px;
  color: #909399;
}
.stat-grid {
  display: grid;
  grid-template-columns: repeat(3, 1fr);
  gap: 16px;
}
.stat-card {
  text-align: center;
  padding: 32px 20px;
}
.stat-num {
  font-size: 40px;
  font-weight: 700;
  color: #409eff;
  line-height: 1;
}
.stat-label {
  margin-top: 10px;
  font-size: 14px;
  color: #606266;
}
</style>
