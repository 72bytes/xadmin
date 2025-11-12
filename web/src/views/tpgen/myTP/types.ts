import type { SavedPlanResp } from '@/apis/tpgen'

// 查询表单
export interface QueryForm {
  name?: string
  category?: string
  status?: number
  sort: string[]
}

// 编辑表单
export interface EditForm {
  name: string
  category: string
  description?: string
  tags?: string
  status: number
}

// 分类选项
export const CATEGORY_OPTIONS = [
  { label: 'Benchmark', value: 'Benchmark' },
  { label: 'Functional', value: 'Functional' },
  { label: 'Performance', value: 'Performance' },
  { label: 'Stress', value: 'Stress' },
  { label: 'Custom', value: 'Custom' },
]

// 状态选项
export const STATUS_OPTIONS = [
  { label: '草稿', value: 1 },
  { label: '已发布', value: 2 },
  { label: '归档', value: 3 },
]

// 导出 SavedPlanResp 类型
export type { SavedPlanResp }
