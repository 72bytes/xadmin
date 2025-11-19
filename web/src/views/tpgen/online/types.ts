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

// 单个机器配置（支持多配置）
export interface MachineConfiguration {
  configId: number  // 唯一标识
  osId: number
  osFamily: string
  osVersion: string
  deploymentMethod: 'bare_metal' | 'vm' | 'wsl'
  kernelVersion: string
  testTypeId: string
  testTypeName: string
  testComponents: any[]  // 选中的测试组件
  orderedTestCases: any[]  // 排序后的测试用例
}

// 表单数据
export interface FormData {
  cpu: string
  gpu: string
  productName: string   // 产品系列名称
  asicName: string      // ASIC 名称
  selectedMachines: number[]
  
  // 多配置模式
  machineConfigurations: Record<number, MachineConfiguration[]>
  
  // 保留旧字段以兼容（可选）
  osConfigMethod?: 'same' | 'individual'
  os?: string
  deployment?: string
  individualOsConfig?: Record<number, { os: string; deployment: string }>
  kernelConfigMethod?: 'same' | 'individual'
  kernelType?: string
  kernelVersion?: string
  individualKernelConfig?: Record<number, { type: string; version: string }>
  testType?: string      // 测试类型 (Same 模式)
  testTypeConfigMethod?: 'same' | 'individual'  // Test Type 配置方法
  individualTestTypeConfig?: Record<number, { testType: string }>  // Individual Test Type 配置
  firmwareVersion?: string
  versionComparison?: boolean
  selectedTestCases?: TestCase[]
}

// YAML数据结构
export interface YamlData {
  metadata: {
    generated: string
    version: string
    description?: string
  }
  hardware: {
    productName?: string
    asicName?: string
    machines: Array<{
      id: number
      hostname: string
      productName: string
      asicName: string
      ipAddress?: string
      gpuModel?: string
    }>
  }
  environment: {
    os?: any
    kernel?: any
    machines?: {
      [hostname: string]: {
        configurations: Array<{
          config_id: number
          os: any
          deployment_method: string
          kernel: any
          test_type: string
          execution_case_list: string[]
        }>
      }
    }
  }
  testConfiguration?: any
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

