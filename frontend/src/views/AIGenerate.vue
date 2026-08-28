<template>
  <div class="page ai-page">
    <div class="page-header">
      <div class="page-title">生成和上传案例</div>
      <el-button text type="primary" @click="$router.push('/ai-records')">
        <el-icon class="mr-4"><Document /></el-icon>我的生成记录
      </el-button>
    </div>

    <el-tabs v-model="activeTab" class="gen-tabs">
      <el-tab-pane label="AI 智能生成" name="ai">
        <div class="ai-layout">
      <!-- 左侧参数配置 -->
      <div class="config card">
        <el-form label-position="top">
          <el-form-item label="思政方向" required>
            <el-select v-model="form.ideological" placeholder="请选择思政标签" style="width: 100%">
              <el-option v-for="t in IDEOLOGICAL_TAGS" :key="t" :label="t" :value="t" />
            </el-select>
          </el-form-item>
          <el-form-item label="专业知识点 / 主题" required>
            <el-input
              v-model="form.knowledge"
              type="textarea"
              :rows="4"
              placeholder="请输入您想生成的案例主题，例如：软件工程中的代码安全"
            />
          </el-form-item>
          <el-form-item label="适用专业">
            <el-select
              v-model="form.profession"
              placeholder="选填，可多选"
              multiple
              filterable
              style="width: 100%"
            >
              <el-option v-for="p in PROFESSIONS" :key="p" :label="p" :value="p" />
            </el-select>
          </el-form-item>
          <el-form-item label="篇幅选择">
            <el-radio-group v-model="form.length">
              <el-radio-button value="short">短</el-radio-button>
              <el-radio-button value="medium">中</el-radio-button>
              <el-radio-button value="long">长</el-radio-button>
            </el-radio-group>
          </el-form-item>
          <el-button
            type="primary"
            size="large"
            class="generate-btn"
            :loading="generating"
            :disabled="!form.ideological || !form.knowledge"
            @click="handleGenerate"
          >
            <el-icon class="mr-4"><MagicStick /></el-icon>{{ generating ? '正在生成…' : '生成案例' }}
          </el-button>
        </el-form>
      </div>

      <!-- 右侧结果展示 -->
      <div class="result card">
        <div class="result-title">
          生成结果
          <template v-if="done">
            <el-tag size="small" type="success" effect="light">生成完成</el-tag>
          </template>
        </div>
        <div v-loading="generating" class="result-body">
          <div v-if="!resultText && !generating" class="placeholder">
            <el-icon :size="48" color="#c0c4cc"><DocumentAdd /></el-icon>
            <p>配置左侧参数后点击「生成案例」，AI 将流式生成专属思政案例</p>
          </div>
          <div v-else class="stream-text" :class="{ typing: generating }">{{ resultText }}</div>
        </div>
        <div v-if="done" class="result-actions">
          <el-button @click="reGenerate">
            <el-icon class="mr-4"><Refresh /></el-icon>重新生成
          </el-button>
          <el-button @click="copyText">
            <el-icon class="mr-4"><CopyDocument /></el-icon>复制文本
          </el-button>
          <el-button @click="exportDoc">
            <el-icon class="mr-4"><Download /></el-icon>导出文档
          </el-button>
          <el-button type="primary" @click="submitVisible = true">
            <el-icon class="mr-4"><Upload /></el-icon>提交审核
          </el-button>
        </div>
        </div>
      </div>
      </el-tab-pane>

      <el-tab-pane label="手动输入" name="manual">
        <ManualUploadForm />
      </el-tab-pane>
    </el-tabs>

    <!-- 提交审核弹窗 -->
    <el-dialog v-model="submitVisible" title="提交案例审核" width="720px">
      <el-form ref="submitFormRef" :model="submitForm" :rules="submitRules" label-width="100px">
        <el-form-item label="案例标题" prop="title">
          <el-input v-model="submitForm.title" placeholder="请输入案例标题" />
        </el-form-item>
        <el-form-item label="案例分类" prop="category">
          <el-select v-model="submitForm.category" placeholder="请选择" style="width: 100%">
            <el-option v-for="c in CASE_CATEGORIES" :key="c" :label="c" :value="c" />
          </el-select>
        </el-form-item>
        <el-form-item label="适用专业">
          <el-select v-model="submitForm.profession" multiple filterable placeholder="选填" style="width: 100%">
            <el-option v-for="p in PROFESSIONS" :key="p" :label="p" :value="p" />
          </el-select>
        </el-form-item>
        <el-form-item label="思政元素">
          <el-select v-model="submitForm.ideological_elements" multiple filterable placeholder="选择思政标签" style="width: 100%">
            <el-option v-for="t in IDEOLOGICAL_TAGS" :key="t" :label="t" :value="t" />
          </el-select>
        </el-form-item>
        <el-form-item label="案例背景">
          <el-input v-model="submitForm.background" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="实施过程">
          <el-input v-model="submitForm.process" type="textarea" :rows="3" />
        </el-form-item>
        <el-form-item label="实施结果">
          <el-input v-model="submitForm.result" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="教学价值">
          <el-input v-model="submitForm.teaching_value" type="textarea" :rows="2" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="submitVisible = false">取消</el-button>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">确认提交</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<script setup>
import { ref, reactive, onMounted, watch } from 'vue'
import { generateCaseStreamApi, submitCaseApi } from '@/api'
import { CASE_CATEGORIES, PROFESSIONS, IDEOLOGICAL_TAGS } from '@/api/mockData'
import { useAppStore } from '@/stores/app'
import { ElMessage } from 'element-plus'
import ManualUploadForm from '@/components/ManualUploadForm.vue'

const appStore = useAppStore()

const activeTab = ref('ai')

const generating = ref(false)
const done = ref(false)
const resultText = ref('')
const currentRecord = ref(null)

const form = reactive({
  ideological: '',
  knowledge: '',
  profession: [],
  length: 'medium',
})

async function handleGenerate() {
  if (!form.ideological || !form.knowledge) {
    ElMessage.warning('请填写完整的生成参数')
    return
  }
  generating.value = true
  done.value = false
  resultText.value = ''
  try {
    const res = await generateCaseStreamApi(form, {
      onChunk: (seg, received) => {
        resultText.value = received
      },
    })
    if (res.code === 200) {
      currentRecord.value = { id: res.data.id, content: res.data.content }
      done.value = true
    } else {
      ElMessage.error(res.msg)
    }
  } finally {
    generating.value = false
  }
}

function reGenerate() {
  resultText.value = ''
  done.value = false
  currentRecord.value = null
  handleGenerate()
}

async function copyText() {
  try {
    await navigator.clipboard.writeText(resultText.value)
    ElMessage.success('已复制到剪贴板')
  } catch {
    ElMessage.error('复制失败，请手动复制')
  }
}

function exportDoc() {
  const content = resultText.value
  const blob = new Blob(['﻿' + content], { type: 'text/markdown;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `AI生成案例_${Date.now()}.md`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  ElMessage.success('文档已导出')
}

// 提交审核
const submitVisible = ref(false)
const submitting = ref(false)
const submitFormRef = ref(null)
const submitForm = reactive({
  title: '',
  category: '',
  profession: [],
  ideological_elements: [],
  background: '',
  process: '',
  result: '',
  teaching_value: '',
})
const submitRules = {
  title: [{ required: true, message: '请输入标题', trigger: 'blur' }],
  category: [{ required: true, message: '请选择案例分类', trigger: 'change' }],
}

function parseGeneratedContent(text) {
  const sections = {}
  const lines = text.split('\n')
  let current = ''
  for (const line of lines) {
    const m = line.match(/^【(.+?)】$/)
    if (m) {
      current = m[1]
      sections[current] = []
    } else if (current && line.trim()) {
      sections[current].push(line.trim())
    }
  }
  const join = (key) => (sections[key] || []).join('\n')
  const ideological = join('思政切入点')
    .split(/[、,，;；]/)
    .map((s) => s.trim())
    .filter((s) => IDEOLOGICAL_TAGS.includes(s))
  return {
    title: sections['案例标题']?.[0] || '',
    background: join('案例背景'),
    process: join('案例正文'),
    result: join('教学成效'),
    teaching_value: join('配套思考题'),
    ideological,
  }
}

function openSubmit() {
  const parsed = parseGeneratedContent(resultText.value)
  Object.assign(submitForm, {
    title: parsed.title,
    category: '行业案例',
    profession: [...form.profession],
    ideological_elements: parsed.ideological.length ? parsed.ideological : [form.ideological].filter(Boolean),
    background: parsed.background,
    process: parsed.process,
    result: parsed.result,
    teaching_value: parsed.teaching_value,
  })
}

async function handleSubmit() {
  await submitFormRef.value.validate()
  submitting.value = true
  try {
    const res = await submitCaseApi(submitForm)
    if (res.code === 200) {
      ElMessage.success(res.msg || '提交成功')
      submitVisible.value = false
    } else {
      ElMessage.error(res.msg)
    }
  } finally {
    submitting.value = false
  }
}

onMounted(() => {
  // 详情弹窗/生成记录跳转时预填参数
  const pre = appStore.aiPrefill
  if (pre) {
    form.ideological = pre.ideological || ''
    form.knowledge = pre.knowledge || ''
    form.profession = pre.profession || []
    form.length = pre.length || 'medium'
    appStore.setAiPrefill(null)
  }
})

// 打开提交弹窗时预填
watch(submitVisible, (v) => {
  if (v) openSubmit()
})
</script>

<style scoped>
.mr-4 {
  margin-right: 4px;
}
.ai-layout {
  display: flex;
  gap: 20px;
  align-items: flex-start;
}
.config {
  width: 320px;
  flex-shrink: 0;
}
.index-radio {
  display: flex;
  flex-direction: column;
  gap: 8px;
}
.generate-btn {
  width: 100%;
}
.result {
  flex: 1;
  min-width: 0;
}
.result-title {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 16px;
  font-weight: 600;
  margin-bottom: 12px;
}
.result-body {
  min-height: 360px;
  background: #fafbfc;
  border: 1px solid #ebeef5;
  border-radius: 8px;
  padding: 16px;
  position: relative;
}
.placeholder {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  min-height: 320px;
  color: #c0c4cc;
  gap: 8px;
  text-align: center;
}
.stream-text {
  white-space: pre-wrap;
  font-size: 14px;
  line-height: 1.9;
  color: #303133;
  min-height: 320px;
}
.stream-text.typing::after {
  content: '▋';
  color: #409eff;
  animation: blink 1s step-end infinite;
}
@keyframes blink {
  50% {
    opacity: 0;
  }
}
.result-actions {
  display: flex;
  gap: 10px;
  margin-top: 16px;
  flex-wrap: wrap;
}
</style>
