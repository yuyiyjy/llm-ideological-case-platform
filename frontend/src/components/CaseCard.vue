<template>
  <div class="case-card card card-hover">
    <div class="card-body" @click="$emit('detail', item)">
      <div class="title">{{ item.title }}</div>
      <div class="tags">
        <el-tag size="small" type="primary" effect="light">{{ item.category }}</el-tag>
        <el-tag
          v-for="t in ideological.slice(0, 2)"
          :key="t"
          size="small"
          type="success"
          effect="plain"
        >{{ t }}</el-tag>
      </div>
      <div class="summary clamp-2">{{ item.teaching_value || item.background }}</div>
      <div class="meta">
        <span class="profession clamp-1">{{ professionText }}</span>
        <span class="views">
          <el-icon><View /></el-icon>{{ item.views }}
        </span>
      </div>
    </div>
    <div class="card-actions">
      <el-button size="small" @click="$emit('detail', item)">查看详情</el-button>
      <el-button
        size="small"
        :type="isFav ? 'warning' : 'default'"
        :icon="isFav ? 'StarFilled' : 'Star'"
        @click="$emit('favorite', item)"
      >
        {{ isFav ? '已收藏' : '收藏' }}
      </el-button>
    </div>
  </div>
</template>

<script setup>
import { computed } from 'vue'

const props = defineProps({
  item: { type: Object, required: true },
})
defineEmits(['detail', 'favorite'])

const ideological = computed(() => props.item.ideological_elements || [])
const professionText = computed(() => (props.item.profession || []).join(' / '))
const isFav = computed(() => props.item.isFavorite)
</script>

<style scoped>
.case-card {
  display: flex;
  flex-direction: column;
  height: 100%;
  overflow: hidden;
}
.card-body {
  flex: 1;
  cursor: pointer;
  padding: 16px 16px 0;
}
.title {
  font-size: 16px;
  font-weight: 600;
  color: #303133;
  line-height: 1.4;
  margin-bottom: 8px;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.tags {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  margin-bottom: 10px;
}
.summary {
  font-size: 13px;
  color: #606266;
  line-height: 1.6;
  min-height: 42px;
  margin-bottom: 10px;
}
.meta {
  display: flex;
  justify-content: space-between;
  align-items: center;
  font-size: 12px;
  color: #909399;
  padding-bottom: 12px;
  gap: 8px;
}
.profession {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}
.views {
  display: inline-flex;
  align-items: center;
  gap: 4px;
  flex-shrink: 0;
}
.card-actions {
  display: flex;
  gap: 8px;
  padding: 12px 16px;
  border-top: 1px solid #f0f2f5;
  background: #fafbfc;
}
</style>
