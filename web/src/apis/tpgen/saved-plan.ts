import type * as T from './type'
import http from '@/utils/http'

export type * from './type'

const BASE_URL = '/tpgen/saved-plans'  // 注意：与后端保持一致，使用复数形式

/** @desc 查询保存的测试计划列表 */
export function listSavedPlan(query: T.SavedPlanPageQuery) {
  return http.get<PageRes<T.SavedPlanResp[]>>(`${BASE_URL}/list`, query)
}

/** @desc 查询保存的测试计划详情 */
export function getSavedPlan(id: string) {
  return http.get<T.SavedPlanDetailResp>(`${BASE_URL}/${id}`)
}

/** @desc 新增保存的测试计划 */
export function addSavedPlan(data: T.SavedPlanForm) {
  return http.post(`${BASE_URL}`, data)
}

/** @desc 修改保存的测试计划 */
export function updateSavedPlan(data: Partial<T.SavedPlanForm>, id: string) {
  return http.put(`${BASE_URL}/${id}`, data)
}

/** @desc 删除保存的测试计划 */
export function deleteSavedPlan(ids: string | Array<string>) {
  return http.del(`${BASE_URL}/${ids}`)
}

/** @desc 使用保存的测试计划（增加使用计数） */
export function useSavedPlan(id: string) {
  return http.post(`${BASE_URL}/${id}/use`)
}

/** @desc 获取所有类别列表 */
export function getCategories() {
  return http.get<string[]>(`${BASE_URL}/categories/list`)
}
