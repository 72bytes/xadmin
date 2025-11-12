/**
 * TPDB 视图类型定义
 * Test Plan Database Management - View Type Definitions
 */

import type * as API from '@/apis/tpdb'

// 重新导出 API 类型
export type {
  SutDevice,
  SutDeviceForm,
  SutDeviceQuery,
  OsConfig,
  OsConfigForm,
  OsConfigQuery,
  TestType,
  TestTypeForm,
  TestComponent,
  TestComponentForm,
  TestComponentQuery,
  TestCase,
  TestCaseForm,
  TestCaseQuery,
  TestPlan,
  TestPlanForm,
  TestPlanQuery,
} from '@/apis/tpdb'

// Tab 类型定义
export type TabKey = 'sutDevice' | 'osConfig' | 'testType' | 'testComponent' | 'testCase'

// 表单模式
export type FormMode = 'add' | 'edit' | 'view'

// 通用表格列配置
export interface TableColumn {
  title: string
  dataIndex: string
  width?: number
  align?: 'left' | 'center' | 'right'
  ellipsis?: boolean
  tooltip?: boolean
}
