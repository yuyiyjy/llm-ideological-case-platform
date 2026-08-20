/**
 * API 函数层 —— Mock 实现，函数与 3B02 接口规范端点一一对应
 *
 * 案例字段与筛选逻辑对齐 docs/prompt_generate_v2.txt 字段规范。
 * 每个函数顶部注释了真实后端端点，联调时把函数体替换为 request.js 的调用即可。
 * 全局返回结构：{ code, msg, data }，分页 data 为 { total, records, page, size }
 */
import {
  delay,
  deepClone,
  now,
  todayCompact,
  CASE_CATEGORIES,
  REVIEW_STATUSES,
  IDEOLOGICAL_TAGS,
  PROFESSIONS,
  mockUsers,
  mockCases,
  getFavorites,
  toggleFavorite,
  mockAiRecords,
  mockSubmits,
  mockStats,
  mockHomeIndex,
} from './mockData.js'

// ============ 统一返回包装 ============
export function mockResponse(data, code = 200, msg = 'success') {
  return { code, msg, data }
}

async function mock({ data, code = 200, msg = 'success', delayMs = 300 }) {
  await delay(delayMs)
  return mockResponse(data, code, msg)
}

function findUser(username) {
  return mockUsers.find((u) => u.username === username)
}

function currentUser() {
  try {
    return JSON.parse(localStorage.getItem('userInfo') || 'null')
  } catch {
    return null
  }
}

/** 思政标签列表（可被管理页增删，初始为规范中的 17 个） */
let tagList = IDEOLOGICAL_TAGS.map((name, i) => ({ id: i + 1, name, useCount: 0, createTime: '2026-08-01' }))

function nextCaseId() {
  let max = 0
  for (const c of mockCases) {
    const num = Number(String(c.id).replace('case_', ''))
    if (num > max) max = num
  }
  return 'case_' + String(max + 1).padStart(3, '0')
}

// ============ 模块1：登录与用户信息 ============

// POST /api/login
export async function loginApi({ username, password, role }) {
  const user = mockUsers.find(
    (u) => u.username === username && u.password === password && u.role === role
  )
  if (!user) {
    return mock({ code: 400, msg: '账号、密码或角色不匹配', data: null, delayMs: 500 })
  }
  if (user.status === 1) {
    return mock({ code: 400, msg: '该账号已被冻结，请联系管理员', data: null, delayMs: 500 })
  }
  return mock({
    delayMs: 600,
    data: {
      token: `mock-token-${user.id}-${Date.now()}`,
      username: user.username,
      role: user.role,
      avatar: user.avatar,
    },
  })
}

// POST /api/logout
export async function logoutApi() {
  return mock({ data: null, delayMs: 200 })
}

// GET /api/user/info
export async function getUserInfoApi() {
  const info = currentUser()
  if (!info) return mock({ code: 401, msg: '未登录', data: null })
  const user = findUser(info.username)
  if (!user) return mock({ code: 401, msg: '用户不存在', data: null })
  return mock({
    data: {
      username: user.username,
      role: user.role,
      avatar: user.avatar,
      nickName: user.nickName,
      phone: user.phone,
      intro: user.intro,
    },
  })
}

// PUT /api/user/info  body: nickName/phone/intro/avatar
export async function updateUserInfoApi(payload) {
  const info = currentUser()
  if (!info) return mock({ code: 401, msg: '未登录', data: null })
  const user = findUser(info.username)
  if (!user) return mock({ code: 401, msg: '用户不存在', data: null })
  Object.assign(user, {
    nickName: payload.nickName ?? user.nickName,
    phone: payload.phone ?? user.phone,
    intro: payload.intro ?? user.intro,
    avatar: payload.avatar ?? user.avatar,
  })
  const updated = {
    username: user.username,
    role: user.role,
    avatar: user.avatar,
    nickName: user.nickName,
    phone: user.phone,
    intro: user.intro,
  }
  localStorage.setItem('userInfo', JSON.stringify(updated))
  return mock({ data: updated })
}

// PUT /api/user/password  body: oldPwd/newPwd
export async function changePasswordApi({ oldPwd, newPwd }) {
  const info = currentUser()
  if (!info) return mock({ code: 401, msg: '未登录', data: null })
  const user = findUser(info.username)
  if (!user) return mock({ code: 401, msg: '用户不存在', data: null })
  if (user.password !== oldPwd) return mock({ code: 400, msg: '原密码不正确', data: null })
  user.password = newPwd
  return mock({ data: null, msg: '密码修改成功' })
}

// ============ 模块2：案例浏览、检索、收藏 ============

/**
 * GET /api/case/list
 * query: keyword / category / profession / tag(思政标签) / page / size / sort
 * 公开列表默认只返回 review_status === '审核通过' 的案例
 */
export async function getCaseListApi({
  keyword = '',
  category,
  profession,
  tag,
  page = 1,
  size = 9,
  sort = 'new',
  includeAll = false,
  status,
} = {}) {
  let list = mockCases.filter(
    (c) => includeAll || (c.review_status === '审核通过' && c.review_status !== '已归档')
  )
  if (status) list = list.filter((c) => c.review_status === status)

  if (keyword) {
    const kw = keyword.toLowerCase()
    list = list.filter(
      (c) =>
        c.title.toLowerCase().includes(kw) ||
        c.keywords.some((k) => k.toLowerCase().includes(kw)) ||
        c.profession.some((p) => p.toLowerCase().includes(kw)) ||
        c.teaching_value.includes(keyword) ||
        c.content.includes(keyword)
    )
  }
  if (category) list = list.filter((c) => c.category === category)
  if (profession) list = list.filter((c) => c.profession.includes(profession))
  if (tag) list = list.filter((c) => c.ideological_elements.includes(tag))

  if (sort === 'views') {
    list = [...list].sort((a, b) => b.views - a.views)
  } else {
    list = [...list].sort((a, b) => b.publish_date.localeCompare(a.publish_date))
  }

  const total = list.length
  const start = (page - 1) * size
  const records = list.slice(start, start + size).map((c) => {
    const user = currentUser()
    if (user) c.isFavorite = getFavorites(user.username).includes(c.id)
    return c
  })
  return mock({ data: { total, records, page: Number(page), size: Number(size) } })
}

// GET /api/case/detail/{id}
export async function getCaseDetailApi(id) {
  const c = mockCases.find((item) => item.id === String(id))
  if (!c) return mock({ code: 404, msg: '案例不存在', data: null })
  const user = currentUser()
  const detail = deepClone(c)
  if (user) detail.isFavorite = getFavorites(user.username).includes(detail.id)
  return mock({ data: detail })
}

// POST /api/case/favorite  body: caseId
export async function addFavoriteApi(caseId) {
  const user = currentUser()
  if (!user) return mock({ code: 401, msg: '未登录', data: null })
  toggleFavorite(user.username, String(caseId))
  return mock({ data: { caseId, favorited: true }, msg: '收藏成功' })
}

// DELETE /api/case/favorite/{caseId}
export async function removeFavoriteApi(caseId) {
  const user = currentUser()
  if (!user) return mock({ code: 401, msg: '未登录', data: null })
  toggleFavorite(user.username, String(caseId))
  return mock({ data: { caseId, favorited: false }, msg: '已取消收藏' })
}

// GET /api/case/favorite/list  query: page/size
export async function getFavoriteListApi({ page = 1, size = 9 } = {}) {
  const user = currentUser()
  if (!user) return mock({ code: 401, msg: '未登录', data: null })
  const ids = getFavorites(user.username)
  let list = mockCases.filter((c) => ids.includes(c.id))
  const total = list.length
  const start = (page - 1) * size
  const records = list.slice(start, start + size).map((c) => ({ ...c, isFavorite: true }))
  return mock({ data: { total, records, page: Number(page), size: Number(size) } })
}

// GET /api/case/recommend/{caseId}  （同思政标签 / 同分类 / 同课程）
export async function getRecommendApi(caseId) {
  const c = mockCases.find((item) => item.id === String(caseId))
  if (!c) return mock({ data: [] })
  const list = mockCases
    .filter(
      (item) =>
        item.review_status === '审核通过' &&
        item.id !== c.id &&
        (item.category === c.category ||
          item.ideological_elements.some((t) => c.ideological_elements.includes(t)))
    )
    .slice(0, 4)
  return mock({ data: list })
}

// ============ 模块3：AI 案例生成（SSE 流式） ============

/**
 * 按 prompt_generate_v2 规范拼装生成内容
 * 输出结构：id/title/source/source_url/publish_date/collect_date/version/category/
 *           review_status/background/content/process/result/profession/keywords/
 *           professional_knowledge/ideological_elements/teaching_value
 */
function buildGeneratedCase({ ideologicalDirection, topic, profession, length }) {
  const paraCount = { short: 2, medium: 4, long: 6 }[length] || 3
  const professionName = Array.isArray(profession) && profession.length ? profession[0] : '相关专业'
  const paras = []
  for (let i = 1; i <= paraCount; i++) {
    paras.push(
      `在第${i}阶段，围绕"${topic}"这一主题，教学团队将专业知识点与"${ideologicalDirection}"有机融合，设计递进式教学环节，引导学生在分析问题、解决问题的过程中，内化价值认同，实现知识传授与价值塑造的同向同行。`
    )
  }
  const background =
    `本案例面向${professionName}领域，聚焦专业知识点"${topic}"，结合当前经济社会发展中的鲜活实践，挖掘其中蕴含的思政元素，使专业教学与价值引领深度融合。`
  const process = paras.join('\n')
  const result =
    `通过本案例教学，学生能够运用专业知识分析现实问题，深化对"${ideologicalDirection}"的理解与认同，达到"润物细无声"的育人效果。`
  const teachingValue =
    `适用于${professionName}等相关专业课程。结合"${topic}"知识点，引导学生思考${ideologicalDirection}的时代价值与实践路径，发挥课程思政育人作用。`
  // 主方向外再补充 2 个思政标签
  const extraTags = IDEOLOGICAL_TAGS.filter((t) => t !== ideologicalDirection).slice(0, 2)

  return {
    id: 'case_' + String(Math.floor(Math.random() * 9000) + 1000),
    title: `基于"${ideologicalDirection}"的${professionName}教学案例`,
    source: 'AI生成',
    source_url: '',
    publish_date: todayCompact(),
    collect_date: todayCompact(),
    version: 'V1.1',
    category: '行业案例',
    review_status: '待审核',
    background,
    content: 'https://case.example.com/files/generated.pdf',
    process,
    result,
    profession: Array.isArray(profession) && profession.length ? profession : ['软件工程'],
    keywords: [topic, '课程思政', '教学案例'],
    professional_knowledge: [topic],
    ideological_elements: [ideologicalDirection, ...extraTags],
    teaching_value: teachingValue,
  }
}

// POST /api/ai/generate  body: ideological/knowledge/length/profession
// 采用 SSE 流式分段返回，mock 用「分段 + setTimeout」模拟打字机效果。
export async function generateCaseStreamApi(params, { onChunk } = {}) {
  const { ideological, knowledge, length = 'medium', profession } = params
  if (!ideological || !knowledge) {
    return mock({ code: 400, msg: '请选择思政方向并填写知识点', data: null })
  }
  const ideologicalDirection = ideological

  const generated = buildGeneratedCase({ ideologicalDirection, topic: knowledge, profession, length })
  const text = [
    `【案例标题】${generated.title}`,
    '',
    `【案例背景】${generated.background}`,
    '',
    `【思政切入点】${generated.ideological_elements.join('、')}`,
    '',
    `【案例正文】`,
    generated.process,
    '',
    `【教学成效】${generated.result}`,
    '',
    `【配套思考题】1. 结合本案例，谈谈你对"${knowledge}"中蕴含思政价值的理解；2. 请从专业角度分析这一思政导向在同类场景中的迁移应用。`,
  ].join('\n')

  // 按 2~4 个字符切成小块，模拟流式
  const segments = []
  for (let i = 0; i < text.length; ) {
    const step = 2 + Math.floor(Math.random() * 3)
    segments.push(text.slice(i, i + step))
    i += step
  }

  let received = ''
  for (const seg of segments) {
    await delay(30 + Math.floor(Math.random() * 60))
    received += seg
    if (onChunk) onChunk(seg, received)
  }

  // 后端自动存储生成记录
  const user = currentUser()
  const record = {
    id: Date.now(),
    username: user ? user.username : 'guest',
    createTime: now(),
    category: generated.category,
    topic: knowledge,
    ideological_direction: ideologicalDirection,
    profession: generated.profession,
    length,
    contentPreview: generated.process.slice(0, 120) + '……',
    content: text,
    publish_date: generated.publish_date,
    version: generated.version,
    generatedData: generated,
  }
  mockAiRecords.unshift(record)

  return mockResponse({ id: record.id, content: text, data: generated }, 200, '生成完成')
}

// GET /api/ai/record/list  query: page/size
export async function getAiRecordListApi({ page = 1, size = 10 } = {}) {
  const user = currentUser()
  if (!user) return mock({ code: 401, msg: '未登录', data: null })
  const list = mockAiRecords.filter((r) => r.username === user.username)
  const total = list.length
  const start = (page - 1) * size
  const records = list.slice(start, start + size)
  return mock({ data: { total, records, page: Number(page), size: Number(size) } })
}

// GET /api/ai/record/{id}
export async function getAiRecordApi(id) {
  const rec = mockAiRecords.find((r) => r.id === Number(id))
  if (!rec) return mock({ code: 404, msg: '记录不存在', data: null })
  return mock({ data: rec })
}

// DELETE /api/ai/record/{id}
export async function deleteAiRecordApi(id) {
  const idx = mockAiRecords.findIndex((r) => r.id === Number(id))
  if (idx >= 0) mockAiRecords.splice(idx, 1)
  return mock({ data: null, msg: '删除成功' })
}

// ============ 模块4：案例提交审核 ============

// POST /api/case/submit  （字段对齐 prompt_generate_v2）
export async function submitCaseApi(data) {
  if (!data.title || !data.category) {
    return mock({ code: 400, msg: '请填写标题与案例分类', data: null })
  }
  const user = currentUser()
  const record = {
    id: Date.now(),
    username: user ? user.username : 'guest',
    submitterName: user ? user.nickName : '未知用户',
    title: data.title,
    source: data.source || '教师投稿',
    category: data.category,
    submitTime: now(),
    status: '待审核',
    rejectReason: '',
    profession: data.profession || [],
    keywords: data.keywords || [],
    professional_knowledge: data.professional_knowledge || [],
    ideological_elements: data.ideological_elements || [],
    teaching_value: data.teaching_value || '',
    background: data.background || '',
    process: data.process || '',
    result: data.result || '',
    content: data.content || '',
  }
  mockSubmits.unshift(record)
  return mock({ data: { submitId: record.id, status: '待审核' }, msg: '提交成功，等待审核' })
}

// GET /api/case/submit/list  query: page/size
export async function getSubmitListApi({ page = 1, size = 10 } = {}) {
  const user = currentUser()
  if (!user) return mock({ code: 401, msg: '未登录', data: null })
  const list = mockSubmits.filter((s) => s.username === user.username)
  const total = list.length
  const start = (page - 1) * size
  const records = list.slice(start, start + size)
  return mock({ data: { total, records, page: Number(page), size: Number(size) } })
}

// ============ 模块5：管理员后台 ============

// 5.1 案例审核管理

// GET /api/admin/case/review-list  query: page/size/status
export async function getReviewListApi({ page = 1, size = 10, status } = {}) {
  let list = deepClone(mockSubmits)
  if (status && status !== '') {
    list = list.filter((s) => s.status === status)
  }
  const total = list.length
  const start = (page - 1) * size
  const records = list.slice(start, start + size)
  return mock({ data: { total, records, page: Number(page), size: Number(size) } })
}

// POST /api/admin/case/review  body: caseSubmitId/status(审核通过/审核驳回)/rejectReason
export async function reviewCaseApi({ caseSubmitId, status, rejectReason = '' }) {
  const rec = mockSubmits.find((s) => s.id === Number(caseSubmitId))
  if (!rec) return mock({ code: 404, msg: '提交记录不存在', data: null })
  rec.status = status
  rec.rejectReason = rejectReason
  if (status === '审核通过') {
    // 通过：并入案例库
    mockCases.push({
      id: nextCaseId(),
      title: rec.title,
      source: rec.source,
      source_url: '',
      publish_date: todayCompact(),
      collect_date: todayCompact(),
      version: 'V1.1',
      category: rec.category,
      review_status: '审核通过',
      background: rec.background,
      content: rec.content,
      process: rec.process,
      result: rec.result,
      profession: rec.profession,
      keywords: rec.keywords,
      professional_knowledge: rec.professional_knowledge,
      ideological_elements: rec.ideological_elements,
      teaching_value: rec.teaching_value,
      isFavorite: false,
      views: 0,
      createTime: rec.submitTime,
      submitterName: rec.submitterName,
    })
  }
  return mock({ data: { caseSubmitId, status: rec.status }, msg: '操作成功' })
}

// PUT /api/admin/case/{id}
export async function updateCaseApi(id, data) {
  const c = mockCases.find((item) => item.id === String(id))
  if (!c) return mock({ code: 404, msg: '案例不存在', data: null })
  Object.assign(c, data, { id: c.id })
  return mock({ data: c, msg: '更新成功' })
}

// DELETE /api/admin/case/{id}
export async function deleteCaseApi(id) {
  const idx = mockCases.findIndex((item) => item.id === String(id))
  if (idx >= 0) mockCases.splice(idx, 1)
  return mock({ data: null, msg: '删除成功' })
}

// POST /api/admin/case/import  Form: Excel/CSV 文件流（mock 用 JSON/CSV 行）
export async function importCasesApi(rows) {
  let success = 0
  const fail = []
  for (const row of rows) {
    if (!row.title || !row.category) {
      fail.push(row.title || '(未命名)')
      continue
    }
    mockCases.push({
      id: nextCaseId(),
      title: row.title,
      source: row.source || '批量导入',
      source_url: row.source_url || '',
      publish_date: row.publish_date || todayCompact(),
      collect_date: todayCompact(),
      version: row.version || 'V1.1',
      category: row.category,
      review_status: '审核通过',
      background: row.background || '',
      content: row.content || '',
      process: row.process || '',
      result: row.result || '',
      profession: Array.isArray(row.profession) ? row.profession : (row.profession ? String(row.profession).split('|') : []),
      keywords: Array.isArray(row.keywords) ? row.keywords : (row.keywords ? String(row.keywords).split('|') : []),
      professional_knowledge: row.professional_knowledge || [],
      ideological_elements: Array.isArray(row.ideological_elements) ? row.ideological_elements : (row.ideological_elements ? String(row.ideological_elements).split('|') : []),
      teaching_value: row.teaching_value || '',
      isFavorite: false,
      views: 0,
      createTime: now(),
      submitterName: '批量导入',
    })
    success++
  }
  return mock({ data: { success, fail }, msg: `导入完成：成功 ${success} 条` })
}

// GET /api/admin/case/export  → 直接返回文件流（mock 用 CSV 下载）
export async function exportCasesApi() {
  const header = ['id', 'title', 'source', 'publish_date', 'category', 'review_status', 'profession', 'keywords', 'ideological_elements']
  const lines = mockCases
    .filter((c) => c.review_status === '审核通过')
    .map((c) =>
      [
        c.id, c.title, c.source, c.publish_date, c.category, c.review_status,
        (c.profession || []).join('|'), (c.keywords || []).join('|'), (c.ideological_elements || []).join('|'),
      ].join(',')
    )
  const csv = '﻿' + [header.join(','), ...lines].join('\n')
  const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = `思政案例导出_${todayCompact()}.csv`
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)
  return mock({ data: null, msg: `已导出 ${lines.length} 条案例` })
}

// 5.2 分类体系（思政标签）

// GET /api/category/tag  （思政标签）
export async function getTagListApi() {
  return mock({ data: deepClone(tagList) })
}
// POST /api/category/tag
export async function addTagApi(data) {
  const id = Math.max(...tagList.map((t) => t.id)) + 1
  tagList.push({ id, name: data.name, useCount: 0, createTime: now().slice(0, 10) })
  return mock({ data: tagList.find((t) => t.id === id), msg: '新增成功' })
}
// PUT /api/category/tag/{id}
export async function updateTagApi(id, data) {
  const t = tagList.find((item) => item.id === Number(id))
  if (!t) return mock({ code: 404, msg: '标签不存在', data: null })
  Object.assign(t, data, { id: t.id })
  return mock({ data: t, msg: '更新成功' })
}
// DELETE /api/category/tag/{id}
export async function deleteTagApi(id) {
  const idx = tagList.findIndex((item) => item.id === Number(id))
  if (idx >= 0) tagList.splice(idx, 1)
  return mock({ data: null, msg: '删除成功' })
}

// 5.3 用户管理

// GET /api/admin/user/list  query: page/size/keyword/role
export async function getUserListApi({ page = 1, size = 10, keyword = '', role = '' } = {}) {
  let list = mockUsers
  if (keyword) list = list.filter((u) => u.username.includes(keyword) || u.nickName.includes(keyword))
  if (role) list = list.filter((u) => u.role === role)
  const total = list.length
  const start = (page - 1) * size
  const records = list.slice(start, start + size).map((u) => ({
    id: u.id,
    username: u.username,
    nickName: u.nickName,
    role: u.role,
    status: u.status,
    phone: u.phone,
    createTime: u.createTime,
  }))
  return mock({ data: { total, records, page: Number(page), size: Number(size) } })
}

// PUT /api/admin/user  body: userId/role/status
export async function updateUserApi({ userId, role, status }) {
  const u = mockUsers.find((item) => item.id === Number(userId))
  if (!u) return mock({ code: 404, msg: '用户不存在', data: null })
  if (role !== undefined) u.role = role
  if (status !== undefined) u.status = Number(status)
  return mock({ data: u, msg: '更新成功' })
}

// POST /api/admin/user/reset-pwd  body: userId
export async function resetUserPwdApi(userId) {
  const u = mockUsers.find((item) => item.id === Number(userId))
  if (!u) return mock({ code: 404, msg: '用户不存在', data: null })
  u.password = '123456'
  return mock({ data: { userId: u.id, initialPwd: '123456' }, msg: '密码已重置为 123456' })
}

// 5.4 数据统计

// GET /api/admin/statistics/home
export async function getStatisticsApi() {
  return mock({ data: deepClone(mockStats) })
}

// ============ 模块6：首页数据 ============

// GET /api/home/hot-case
export async function getHotCaseApi() {
  const list = mockCases
    .filter((c) => c.review_status === '审核通过')
    .sort((a, b) => b.views - a.views)
    .slice(0, 10)
  return mock({ data: list })
}

// GET /api/home/index-data
export async function getHomeIndexApi() {
  return mock({ data: deepClone(mockHomeIndex) })
}
