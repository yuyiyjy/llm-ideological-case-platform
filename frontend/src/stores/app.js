import { defineStore } from 'pinia'

export const useAppStore = defineStore('app', {
  state: () => ({
    // 案例列表筛选条件（跨页面跳转时回填）
    filter: {
      keyword: '',
      category: null,
      profession: null,
      tag: null,
      sort: 'new',
      page: 1,
      size: 9,
    },
    // AI 生成预填（详情弹窗「生成同类案例」、记录「编辑重生成」写入，AIGenerate 挂载读取后清空）
    aiPrefill: null,
  }),
  actions: {
    setFilter(obj) {
      this.filter = { ...this.filter, ...obj }
    },
    resetFilter() {
      this.filter = {
        keyword: '',
        category: null,
        profession: null,
        tag: null,
        sort: 'new',
        page: 1,
        size: 9,
      }
    },
    setAiPrefill(obj) {
      this.aiPrefill = { ...obj }
    },
  },
})
