/**
 * TPDB API 类型定义
 * Test Plan Database Management - API Type Definitions
 */

// ============================================================================
// SUT Device (测试设备)
// ============================================================================

export interface SutDevice {
  id: number
  hostname: string
  asicName?: string
  ipAddress?: string
  deviceId?: string
  revId?: string
  gpuSeries?: string
  gpuModel?: string
  createdAt?: string
  updatedAt?: string
}

export interface SutDeviceForm {
  hostname: string
  asicName?: string
  ipAddress?: string
  deviceId?: string
  revId?: string
  gpuSeries?: string
  gpuModel?: string
}

export interface SutDeviceQuery {
  hostname?: string
  gpuModel?: string
  page?: number
  size?: number
}

// ============================================================================
// OS Config (操作系统配置)
// ============================================================================

export interface OsConfig {
  id: number
  osFamily: string
  version: string
  downloadUrl?: string
  createdAt?: string
  updatedAt?: string
}

export interface OsConfigForm {
  osFamily: string
  version: string
  downloadUrl?: string
}

export interface OsConfigQuery {
  osFamily?: string
  page?: number
  size?: number
}

// ============================================================================
// OS Supported Kernel (操作系统支持的内核)
// ============================================================================

export interface OsSupportedKernel {
  id: number
  osConfigId: number
  kernelVersion: string
}

export interface OsSupportedKernelForm {
  osConfigId: number
  kernelVersion: string
}

// ============================================================================
// Test Type (测试类型)
// ============================================================================

export interface TestType {
  id: number
  typeName: string
  createdAt?: string
  updatedAt?: string
}

export interface TestTypeForm {
  typeName: string
}

// ============================================================================
// Test Component (测试组件)
// ============================================================================

export interface TestComponent {
  id: number
  testTypeId: number
  componentCategory?: string
  componentName: string
}

export interface TestComponentForm {
  testTypeId: number
  componentCategory?: string
  componentName: string
}

export interface TestComponentQuery {
  test_type_id?: number  // 使用下划线命名以匹配后端 API
  component_category?: string
}

// ============================================================================
// Test Case (测试用例)
// ============================================================================

export interface TestCase {
  id: number
  testComponentId: number
  caseName: string
  caseConfig?: Record<string, any>
  createdAt?: string
  updatedAt?: string
}

export interface TestCaseForm {
  testComponentId: number
  caseName: string
  caseConfig?: Record<string, any>
}

export interface TestCaseQuery {
  test_component_id?: number  // 使用下划线命名以匹配后端 API
  page?: number
  size?: number
}

// ============================================================================
// Test Plan (测试计划)
// ============================================================================

export interface TestPlan {
  id: number
  planName: string
  planDescription?: string
  sutDeviceId: number
  osConfigId: number
  createdBy?: string
  createdAt?: string
  updatedAt?: string
  testCases?: TestPlanCase[]
}

export interface TestPlanCase {
  id: number
  caseName: string
  timeout?: number
}

export interface TestPlanForm {
  planName: string
  planDescription?: string
  sutDeviceId: number
  osConfigId: number
  createdBy?: string
}

export interface TestPlanQuery {
  planName?: string
  page?: number
  size?: number
}
