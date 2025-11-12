// 机器信息（匹配数据库 SutDevice 字段）
export interface Machine {
  id: number
  hostname: string // 对应数据库的 hostname
  asicName?: string // 对应数据库的 asic_name
  ipAddress?: string // 对应数据库的 ip_address
  deviceId?: string // 对应数据库的 device_id
  revId?: string // 对应数据库的 rev_id
  gpuSeries?: string // 对应数据库的 gpu_series
  gpuModel?: string // 对应数据库的 gpu_model
  createdAt?: string
  updatedAt?: string
  // 以下为兼容旧代码的字段映射
  name?: string // 映射到 hostname
  gpu?: string // 映射到 gpuModel
  status?: 'Available' | 'Unavailable' // 根据设备是否存在判断
}

// 测试用例（匹配数据库 TestCase 字段）
export interface TestCase {
  id: number
  caseName: string // 对应数据库的 case_name
  caseConfig?: Record<string, any> // 对应数据库的 case_config (JSON)
  testComponentId?: number // 对应数据库的 test_component_id
  createdAt?: string
  updatedAt?: string
  // 以下为扩展字段，用于前端展示
  name?: string // 兼容旧代码，映射到 caseName
  description?: string // 从 caseConfig 中提取
  testType?: string // 测试类型名称（从关联表获取）
  testTypeName?: string // 测试类型名称
  componentName?: string // 测试组件名称（从关联表获取）
  componentCategory?: string // 组件分类（从关联表获取）
  subgroup?: string // 兼容旧代码，映射到 componentName
  customGroup?: string
}

// 测试用例组
export interface TestCaseGroup {
  [testType: string]: {
    [subgroup: string]: TestCase[]
  }
}

// 自定义组
export interface CustomGroup {
  name: string
  testCases: TestCase[]
  selectedExistingCases: number[]
}

// 表单数据
export interface FormData {
  cpu: string
  gpu: string
  selectedMachines: number[]
  osConfigMethod: 'same' | 'individual'
  os?: string
  deployment?: string
  individualOsConfig: Record<number, { os: string, deployment: string }>
  kernelConfigMethod: 'same' | 'individual'
  kernelType?: string
  kernelVersion?: string
  individualKernelConfig: Record<number, { type: string, version: string }>
  firmwareVersion: string
  versionComparison: boolean
  selectedTestCases: TestCase[]
}

// YAML数据结构
export interface YamlData {
  metadata: {
    generated: string
    version: string
  }
  hardware: {
    cpu: string
    gpu: string
    machines: Array<{
      id: number
      name: string
      specs: {
        motherboard: string
        gpu: string
        cpu: string
      }
    }>
  }
  environment: {
    os: any
    kernel: any
  }
  firmware: {
    gpu_version: string
    comparison: boolean
  }
  test_suites: Array<{
    id: number
    name: string
    description: string
    type: string
    subgroup: string
    order: number
  }>
}

// 分析结果
export interface AnalysisResult {
  compatibleMachines: Machine[]
  incompatibleMachines: Array<{
    machine: Machine
    reasons: string[]
  }>
  missingConfigurations: string[]
  warnings: string[]
}
