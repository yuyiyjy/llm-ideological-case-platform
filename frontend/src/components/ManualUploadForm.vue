<template>
  <div class="card upload-form">
    <el-form ref="formRef" :model="form" :rules="rules" label-width="100px">
      <el-form-item label="案例标题" prop="title">
        <el-input v-model="form.title" placeholder="10-20 字，体现核心事件与成果" />
      </el-form-item>
      <el-form-item label="案例分类" prop="category">
        <el-select v-model="form.category" placeholder="请选择" style="width: 100%">
          <el-option v-for="c in CASE_CATEGORIES" :key="c" :label="c" :value="c" />
        </el-select>
      </el-form-item>
      <el-form-item label="来源">
        <el-input v-model="form.source" placeholder="权威媒体全名，如：新华社" />
      </el-form-item>
      <el-form-item label="适用专业">
        <el-select v-model="form.profession" multiple filterable placeholder="选填 1-6 个" style="width: 100%">
          <el-option v-for="p in PROFESSIONS" :key="p" :label="p" :value="p" />
        </el-select>
      </el-form-item>
      <el-form-item label="技术关键词">
        <el-select
          v-model="form.keywords"
          multiple
          filterable
          allow-create
          default-first-option
          placeholder="输入后回车，3-6 个技术关键词"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="思政元素">
        <el-select v-model="form.ideological_elements" multiple filterable placeholder="选择 2-5 个思政标签" style="width: 100%">
          <el-option v-for="t in IDEOLOGICAL_TAGS" :key="t" :label="t" :value="t" />
        </el-select>
      </el-form-item>
      <el-form-item label="专业知识点">
        <el-select
          v-model="form.professional_knowledge"
          multiple
          filterable
          allow-create
          default-first-option
          placeholder="输入后回车，如：系统工程方法论"
          style="width: 100%"
        />
      </el-form-item>
      <el-form-item label="案例背景">
        <el-input v-model="form.background" type="textarea" :rows="3" placeholder="100-300 字，交代事件起因与时代背景" />
      </el-form-item>
      <el-form-item label="实施过程">
        <el-input v-model="form.process" type="textarea" :rows="3" placeholder="100-300 字，描述关键经过与技术突破" />
      </el-form-item>
      <el-form-item label="实施结果">
        <el-input v-model="form.result" type="textarea" :rows="3" placeholder="100-300 字，说明最终成果与影响" />
      </el-form-item>
      <el-form-item label="教学价值">
        <el-input v-model="form.teaching_value" type="textarea" :rows="2" placeholder="50-150 字，适用课程与育人作用" />
      </el-form-item>
      <el-form-item label="原文链接">
        <el-input v-model="form.content" placeholder="案例原文 PDF 链接（选填）" />
      </el-form-item>
      <el-form-item>
        <el-button type="primary" :loading="submitting" @click="handleSubmit">提交审核</el-button>
        <el-button @click="resetForm">清空重填</el-button>
      </el-form-item>
    </el-form>
  </div>
</template>

<script setup>
import { ref, reactive } from 'vue'
import { ElMessage } from 'element-plus'
import { submitCaseApi } from '@/api'
import { CASE_CATEGORIES, PROFESSIONS, IDEOLOGICAL_TAGS } from '@/api/mockData'

const emit = defineEmits(['submitted'])

const formRef = ref(null)
const submitting = ref(false)
const emptyForm = () => ({
  title: '',
  category: '',
  source: '',
  profession: [],
  keywords: [],
  ideological_elements: [],
  professional_knowledge: [],
  background: '',
  process: '',
  result: '',
  teaching_value: '',
  content: '',
})
const form = reactive(emptyForm())
const rules = {
  title: [{ required: true, message: '请输入案例标题', trigger: 'blur' }],
  category: [{ required: true, message: '请选择案例分类', trigger: 'change' }],
}

async function handleSubmit() {
  await formRef.value.validate()
  submitting.value = true
  try {
    const res = await submitCaseApi(form)
    if (res.code === 200) {
      ElMessage.success(res.msg || '提交成功，等待审核')
      emit('submitted')
      resetForm()
    } else {
      ElMessage.error(res.msg)
    }
  } finally {
    submitting.value = false
  }
}

function resetForm() {
  formRef.value?.resetFields()
  Object.assign(form, emptyForm())
}
</script>

<style scoped>
.upload-form {
  max-width: 760px;
}
</style>
