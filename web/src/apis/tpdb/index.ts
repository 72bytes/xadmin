/**
 * TPDB API
 * Test Plan Database Management API
 */

import type * as T from './type'
import http from '@/utils/http'

export type * from './type'

const BASE_URL = '/tp/api'

// ============================================================================
// SUT Device API (测试设备)
// ============================================================================

/** @desc 获取测试设备列表 */
export function listSutDevices(query?: T.SutDeviceQuery) {
  return http.get<PageRes<T.SutDevice[]>>(`${BASE_URL}/sut-device/list`, query)
}

/** @desc 获取单个测试设备详情 */
export function getSutDevice(id: number) {
  return http.get<T.SutDevice>(`${BASE_URL}/sut-device/${id}`)
}

/** @desc 创建测试设备 */
export function createSutDevice(data: T.SutDeviceForm) {
  return http.post(`${BASE_URL}/sut-device`, data)
}

/** @desc 更新测试设备 */
export function updateSutDevice(id: number, data: T.SutDeviceForm) {
  return http.put(`${BASE_URL}/sut-device/${id}`, data)
}

/** @desc 删除测试设备 */
export function deleteSutDevice(ids: number | number[]) {
  const idStr = Array.isArray(ids) ? ids.join(',') : String(ids)
  return http.del(`${BASE_URL}/sut-device/${idStr}`)
}

// ============================================================================
// OS Config API (操作系统配置)
// ============================================================================

/** @desc 获取操作系统配置列表 */
export function listOsConfigs(query?: T.OsConfigQuery) {
  return http.get<PageRes<T.OsConfig[]>>(`${BASE_URL}/os-config/list`, query)
}

/** @desc 创建操作系统配置 */
export function createOsConfig(data: T.OsConfigForm) {
  return http.post(`${BASE_URL}/os-config`, data)
}

/** @desc 更新操作系统配置 */
export function updateOsConfig(id: number, data: T.OsConfigForm) {
  return http.put(`${BASE_URL}/os-config/${id}`, data)
}

/** @desc 删除操作系统配置 */
export function deleteOsConfig(ids: number | number[]) {
  const idStr = Array.isArray(ids) ? ids.join(',') : String(ids)
  return http.del(`${BASE_URL}/os-config/${idStr}`)
}

// ============================================================================
// Test Type API (测试类型)
// ============================================================================

/** @desc 获取测试类型列表 */
export function listTestTypes() {
  return http.get<T.TestType[]>(`${BASE_URL}/test-type/list`)
}

/** @desc 创建测试类型 */
export function createTestType(data: T.TestTypeForm) {
  return http.post(`${BASE_URL}/test-type`, data)
}

/** @desc 更新测试类型 */
export function updateTestType(id: number, data: T.TestTypeForm) {
  return http.put(`${BASE_URL}/test-type/${id}`, data)
}

/** @desc 删除测试类型 */
export function deleteTestType(ids: number | number[]) {
  const idStr = Array.isArray(ids) ? ids.join(',') : String(ids)
  return http.del(`${BASE_URL}/test-type/${idStr}`)
}

// ============================================================================
// Test Component API (测试组件)
// ============================================================================

/** @desc 获取测试组件列表 */
export function listTestComponents(query?: T.TestComponentQuery) {
  return http.get<T.TestComponent[]>(`${BASE_URL}/test-component/list`, query)
}

/** @desc 创建测试组件 */
export function createTestComponent(data: T.TestComponentForm) {
  return http.post(`${BASE_URL}/test-component`, data)
}

/** @desc 更新测试组件 */
export function updateTestComponent(id: number, data: T.TestComponentForm) {
  return http.put(`${BASE_URL}/test-component/${id}`, data)
}

/** @desc 删除测试组件 */
export function deleteTestComponent(ids: number | number[]) {
  const idStr = Array.isArray(ids) ? ids.join(',') : String(ids)
  return http.del(`${BASE_URL}/test-component/${idStr}`)
}

// ============================================================================
// Test Case API (测试用例)
// ============================================================================

/** @desc 获取测试用例列表 */
export function listTestCases(query?: T.TestCaseQuery) {
  return http.get<PageRes<T.TestCase[]>>(`${BASE_URL}/test-case/list`, query)
}

/** @desc 创建测试用例 */
export function createTestCase(data: T.TestCaseForm) {
  return http.post(`${BASE_URL}/test-case`, data)
}

/** @desc 更新测试用例 */
export function updateTestCase(id: number, data: T.TestCaseForm) {
  return http.put(`${BASE_URL}/test-case/${id}`, data)
}

/** @desc 删除测试用例 */
export function deleteTestCase(ids: number | number[]) {
  const idStr = Array.isArray(ids) ? ids.join(',') : String(ids)
  return http.del(`${BASE_URL}/test-case/${idStr}`)
}

// ============================================================================
// Test Plan API (测试计划)
// ============================================================================

/** @desc 获取测试计划列表 */
export function listTestPlans(query?: T.TestPlanQuery) {
  return http.get<PageRes<T.TestPlan[]>>(`${BASE_URL}/test-plan/list`, query)
}

/** @desc 获取单个测试计划详情 */
export function getTestPlan(id: number) {
  return http.get<T.TestPlan>(`${BASE_URL}/test-plan/${id}`)
}

/** @desc 创建测试计划 */
export function createTestPlan(data: T.TestPlanForm) {
  return http.post(`${BASE_URL}/test-plan`, data)
}

/** @desc 更新测试计划 */
export function updateTestPlan(id: number, data: T.TestPlanForm) {
  return http.put(`${BASE_URL}/test-plan/${id}`, data)
}

/** @desc 删除测试计划 */
export function deleteTestPlan(ids: number | number[]) {
  const idStr = Array.isArray(ids) ? ids.join(',') : String(ids)
  return http.del(`${BASE_URL}/test-plan/${idStr}`)
}

// ============================================================================
// TPGEN Online 专用 API (用于在线测试计划生成器)
// ============================================================================

/** @desc 获取可用测试设备（带筛选） */
export function getAvailableDevices(query?: {
  gpuModel?: string
  gpuSeries?: string
  asicName?: string
}) {
  return http.get<T.SutDevice[]>(`${BASE_URL}/sut-device/list`, query)
}

/** @desc 获取测试用例树形结构 */
export function getTestCaseTree() {
  return http.get(`${BASE_URL}/test-case/tree`)
}

/** @desc 获取 OS 配置选项列表 */
export function getOsOptions() {
  return http.get<Array<{ label: string, value: string }>>(`${BASE_URL}/os-config/options`)
}

/** @desc 获取内核版本选项 */
export function getKernelOptions(osConfigId?: number) {
  return http.get<Array<{ label: string, value: string }>>(`${BASE_URL}/os-config/kernel-options`, { osConfigId })
}
