<template>
  <div class="case-list">
    <!-- 左侧筛选栏 -->
    <aside class="sidebar">
      <div class="filter-title">案例筛选</div>
      <div class="filter-group">
        <div class="group-label">全文搜索</div>
        <el-input
          v-model="form.keyword"
          placeholder="输入关键词检索"
          clearable
          :prefix-icon="Search"
          @keyup.enter="doSearch"
        />
      </div>
      <div class="filter-group">
        <div class="group-label">案例分类</div>
        <el-select v-model="form.category" placeholder="全部分类" clearable style="width: 100%">
          <el-option v-for="c in CASE_CATEGORIES" :key="c" :label="c" :value="c" />
        </el-select>
      </div>
      <div class="filter-group">
        <div class="group-label">专业</div>
        <el-select
          v-model="form.profession"
          placeholder="全部专业"
          clearable
          filterable
          style="width: 100%"
        >
          <el-option v-for="p in PROFESSIONS" :key="p" :label="p" :value="p" />
        </el-select>
      </div>
      <div class="filter-group">
        <div class="group-label">思政标签</div>
        <el-select
          v-model="form.tag"
          placeholder="全部标签"
          clearable
          filterable
          style="width: 100%"
        >
          <el-option v-for="t in tags" :key="t.id" :label="t.name" :value="t.name" />
        </el-select>
      </div>
      <div class="filter-actions">
        <el-button style="flex: 1" @click="reset">重置筛选</el-button>
        <el-button style="flex: 1" type="primary" @click="doSearch">搜索</el-button>
      </div>
    </aside>

    <!-- 右侧内容 -->
    <div class="content">
      <div class="content-header">
        <div class="result-count">共 <b>{{ total }}</b> 条案例</div>
        <el-radio-group v-model="form.sort" @change="doSearch">
          <el-radio-button value="new">最新发布</el-radio-button>
          <el-radio-button value="views">浏览最多</el-radio-button>
        </el-radio-group>
      </div>
      <div v-loading="loading" class="case-grid">
        <el-row :gutter="16">
          <el-col v-for="c in list" :key="c.id" :xs="24" :sm="12" :md="8" class="col">
            <CaseCard :item="c" @detail="openDetail" @favorite="toggleFav" />
          </el-col>
        </el-row>
        <el-empty v-if="!loading && !list.length" description="没有符合条件的案例" />
      </div>
      <div class="pagination">
        <el-pagination
          background
          layout="total, prev, pager, next, sizes"
          :total="total"
          :page-size="form.size"
          :current-page="form.page"
          :page-sizes="[9, 18, 30]"
          @current-change="onPageChange"
          @size-change="onSizeChange"
        />
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
import { ref, reactive, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { Search } from '@element-plus/icons-vue'
import { getCaseListApi, getTagListApi, addFavoriteApi, removeFavoriteApi } from '@/api'
import { CASE_CATEGORIES, PROFESSIONS } from '@/api/mockData'
import { useAppStore } from '@/stores/app'
import CaseCard from '@/components/CaseCard.vue'
import CaseDetailDialog from '@/components/CaseDetailDialog.vue'

const router = useRouter()
const appStore = useAppStore()

const tags = ref([])
const list = ref([])
const total = ref(0)
const loading = ref(false)

const form = reactive({
  keyword: '',
  category: null,
  profession: null,
  tag: null,
  sort: 'new',
  page: 1,
  size: 9,
})

const detailVisible = ref(false)
const detailId = ref(null)
const submitVisible = ref(false)

async function fetchList() {
  loading.value = true
  try {
    const params = {
      keyword: form.keyword,
      category: form.category,
      profession: form.profession,
      tag: form.tag,
      sort: form.sort,
      page: form.page,
      size: form.size,
    }
    const res = await getCaseListApi(params)
    if (res.code === 200) {
      list.value = res.data.records
      total.value = res.data.total
    }
  } finally {
    loading.value = false
  }
}

function doSearch() {
  form.page = 1
  fetchList()
}

function reset() {
  Object.assign(form, {
    keyword: '',
    category: null,
    profession: null,
    tag: null,
    sort: 'new',
    page: 1,
    size: 9,
  })
  appStore.resetFilter()
  fetchList()
}

function onPageChange(p) {
  form.page = p
  fetchList()
}
function onSizeChange(s) {
  form.size = s
  form.page = 1
  fetchList()
}

function openDetail(c) {
  detailId.value = c.id
  detailVisible.value = true
}

async function toggleFav(c) {
  if (c.isFavorite) {
    const res = await removeFavoriteApi(c.id)
    if (res.code === 200) c.isFavorite = false
  } else {
    const res = await addFavoriteApi(c.id)
    if (res.code === 200) c.isFavorite = true
  }
}

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
  // 从首页指标卡片跳转时回填筛选条件
  const pre = appStore.filter
  Object.assign(form, {
    keyword: pre.keyword || '',
    category: pre.category || null,
    profession: pre.profession || null,
    tag: pre.tag || null,
    sort: pre.sort || 'new',
    page: 1,
    size: pre.size || 9,
  })
  const t = await getTagListApi()
  tags.value = t.data || []
  fetchList()
})
</script>

<style scoped>
.case-list {
  display: flex;
  gap: 20px;
  max-width: 1200px;
  margin: 0 auto;
  padding: 20px;
  align-items: flex-start;
}
.sidebar {
  width: 260px;
  flex-shrink: 0;
  position: sticky;
  top: 84px;
  background: #fff;
  border-radius: 8px;
  padding: 16px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.06);
}
.filter-title {
  font-size: 16px;
  font-weight: 700;
  margin-bottom: 12px;
}
.filter-group {
  margin-bottom: 16px;
}
.group-label {
  font-size: 13px;
  color: #606266;
  margin-bottom: 8px;
  font-weight: 500;
}
.filter-actions {
  display: flex;
  gap: 8px;
}
.content {
  flex: 1;
  min-width: 0;
}
.content-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 16px;
}
.header-actions {
  display: flex;
  align-items: center;
  gap: 12px;
}
.mr-4 {
  margin-right: 4px;
}
.result-count {
  font-size: 14px;
  color: #606266;
}
.case-grid {
  min-height: 200px;
}
.col {
  margin-bottom: 16px;
}
.pagination {
  display: flex;
  justify-content: flex-end;
  margin-top: 8px;
}
</style>
