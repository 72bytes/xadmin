// 机器信息
export interface Machine {
  id: number
  name: string
  motherboard: string
  gpu: string
  cpu: string
  status: 'Available' | 'Unavailable'
}

// 测试用例
export interface TestCase {
  id: number
  name: string
  description: string
  testType?: string
  subgroup?: string
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
  individualOsConfig: Record<number, { os: string; deployment: string }>
  kernelConfigMethod: 'same' | 'individual'
  kernelType?: string
  kernelVersion?: string
  individualKernelConfig: Record<number, { type: string; version: string }>
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

