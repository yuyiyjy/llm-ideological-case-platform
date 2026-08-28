<template>
  <div>
    <!-- 顶部数字卡片 -->
    <el-row :gutter="16" class="stat-row">
      <el-col :xs="12" :sm="6">
        <div class="stat-card card">
          <div class="stat-value">{{ stats.totalCases }}</div>
          <div class="stat-label">平台总案例数</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card card">
          <div class="stat-value">{{ stats.totalUsers }}</div>
          <div class="stat-label">平台用户总数</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card card">
          <div class="stat-value">{{ stats.todayAiCount }}</div>
          <div class="stat-label">今日 AI 生成量</div>
        </div>
      </el-col>
      <el-col :xs="12" :sm="6">
        <div class="stat-card card">
          <div class="stat-value">{{ stats.pendingReviewCount }}</div>
          <div class="stat-label">待审核案例数</div>
        </div>
      </el-col>
    </el-row>

    <!-- 图表 -->
    <el-row :gutter="16">
      <el-col :xs="24" :md="14">
        <div class="card">
          <div class="chart-title">各案例分类数量分布</div>
          <div ref="barRef" class="chart"></div>
        </div>
      </el-col>
      <el-col :xs="24" :md="10">
        <div class="card">
          <div class="chart-title">五大思政指标案例占比</div>
          <div ref="pieRef" class="chart"></div>
        </div>
      </el-col>
    </el-row>
  </div>
</template>

<script setup>
import { ref, onMounted, onBeforeUnmount } from 'vue'
import * as echarts from 'echarts'
import { getStatisticsApi } from '@/api'

const stats = ref({ totalCases: 0, totalUsers: 0, todayAiCount: 0, pendingReviewCount: 0 })
const barRef = ref(null)
const pieRef = ref(null)
let barChart = null
let pieChart = null

function renderCharts(data) {
  // 柱状图
  if (barRef.value) {
    barChart = echarts.init(barRef.value)
    barChart.setOption({
      tooltip: { trigger: 'axis' },
      grid: { left: 40, right: 20, top: 20, bottom: 30 },
      xAxis: {
        type: 'category',
        data: data.categoryDistribution.map((d) => d.name),
        axisLabel: { interval: 0, rotate: 20, fontSize: 11 },
      },
      yAxis: { type: 'value' },
      series: [
        {
          type: 'bar',
          data: data.categoryDistribution.map((d) => d.count),
          itemStyle: { color: '#409eff', borderRadius: [4, 4, 0, 0] },
          barWidth: 28,
        },
      ],
    })
  }
  // 饼图
  if (pieRef.value) {
    pieChart = echarts.init(pieRef.value)
    pieChart.setOption({
      tooltip: { trigger: 'item', formatter: '{b}: {c} ({d}%)' },
      legend: { bottom: 0, textStyle: { fontSize: 12 } },
      series: [
        {
          type: 'pie',
          radius: ['42%', '68%'],
          center: ['50%', '46%'],
          itemStyle: { borderRadius: 6, borderColor: '#fff', borderWidth: 2 },
          label: { formatter: '{b}: {d}%' },
          data: data.indexRatio.map((d) => ({ name: d.name, value: d.value })),
        },
      ],
    })
  }
}

function handleResize() {
  barChart?.resize()
  pieChart?.resize()
}

onMounted(async () => {
  const res = await getStatisticsApi()
  if (res.code === 200) {
    stats.value = res.data
    renderCharts(res.data)
  }
  window.addEventListener('resize', handleResize)
})

onBeforeUnmount(() => {
  window.removeEventListener('resize', handleResize)
  barChart?.dispose()
  pieChart?.dispose()
})
</script>

<style scoped>
.stat-row {
  margin-bottom: 16px;
}
.stat-card {
  text-align: center;
  padding: 24px 12px;
  margin-bottom: 8px;
}
.stat-value {
  font-size: 32px;
  font-weight: 700;
  color: #409eff;
  line-height: 1.2;
}
.stat-label {
  margin-top: 8px;
  font-size: 13px;
  color: #606266;
}
.chart-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: 12px;
}
.chart {
  height: 340px;
}
</style>
