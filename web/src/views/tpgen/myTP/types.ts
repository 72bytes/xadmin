import type { SavedPlanResp } from '@/apis/tpgen'

// 查询表单
export interface QueryForm {
  name?: string
  category?: string
  status?: number
  createUser?: number  // 创建人 ID，用于过滤当前用户的测试计划
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
  { label: 'PRIVATE', value: 1 },
  { label: 'PUBLIC', value: 2 },
]

// 导出 SavedPlanResp 类型
export type { SavedPlanResp }
