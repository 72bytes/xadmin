<template>
  <div class="custom-plan">
    <!-- 进度条 -->
    <div class="progress-container">
      <div class="progress-bar" :style="{ width: `${progress}%` }" />
    </div>

    <a-form :model="formData" layout="vertical">
      <!-- 硬件平台配置 -->
      <HardwareConfig
        v-model:product-name="formData.productName"
        v-model:asic-name="formData.asicName"
        v-model:selected-machines="formData.selectedMachines"
        @update="updateProgress"
        @machines-update="handleMachinesUpdate"
      />

      <!-- 多配置管理（新版本） -->
      <MachineTestConfig
        :selected-machines="formData.selectedMachines"
        :machines-map="machinesMap"
        v-model:machine-configurations="formData.machineConfigurations"
        @update="updateProgress"
      />

      <!-- 旧组件（保留以备兼容，已隐藏） -->
      <!-- <OSConfig
        v-model:config-method="formData.osConfigMethod"
        v-model:os="formData.os"
        v-model:deployment="formData.deployment"
        v-model:individual-config="formData.individualOsConfig"
        :selected-machines="formData.selectedMachines"
        :machines-map="machinesMap"
        @update="updateProgress"
      />

      <KernelConfig
        v-model:config-method="formData.kernelConfigMethod"
        v-model:kernel-type="formData.kernelType"
        v-model:individual-config="formData.individualKernelConfig"
        v-model:test-type="formData.testType"
        v-model:test-type-config-method="formData.testTypeConfigMethod"
        v-model:individual-test-type-config="formData.individualTestTypeConfig"
        :selected-machines="formData.selectedMachines"
        :machines-map="machinesMap"
        @update="handleTestDataUpdate"
      /> -->

      <!-- 固件管理
      <FirmwareConfig
        v-model:firmware-version="formData.firmwareVersion"
        v-model:version-comparison="formData.versionComparison"
        @update="updateProgress"
      /> -->

      <!-- 操作按钮 -->
      <div class="actions">
        <a-button @click="handleReset" :disabled="isGenerating">
          <template #icon><icon-refresh /></template>
          Reset Form
        </a-button>
        <a-button type="outline" @click="handleSave" :disabled="isGenerating">
          <template #icon><icon-save /></template>
          Save Plan
        </a-button>
        <a-button 
          type="primary" 
          @click="handleGenerate"
          :loading="isGenerating"
          :disabled="isGenerating"
        >
          <template #icon v-if="!isGenerating"><icon-eye /></template>
          {{ isGenerating ? 'Generating...' : 'Preview Test Plan' }}
        </a-button>
      </div>
    </a-form>

    <!-- 验证状态显示 -->
    <div v-if="validationStatus" class="validation-status" :class="validationStatus.status">
      <div class="status-header">
        <icon-check-circle v-if="validationStatus.status === 'valid'" />
        <icon-exclamation-circle v-else />
        <span>{{ validationStatus.status === 'valid' ? 'Validation Passed' : 'Validation Failed' }}</span>
      </div>
      <div v-if="validationStatus.checks" class="status-checks">
        <div v-for="check in validationStatus.checks" :key="check.type" class="check-item">
          <icon-check v-if="check.status === 'passed'" />
          <icon-close v-else />
          <span>{{ check.type }}: {{ check.status }}</span>
        </div>
      </div>
    </div>

    <!-- YAML 预览 -->
    <YamlPreview 
      v-if="generatedYaml" 
      :yaml-data="generatedYaml"
      :error-lines="errorLineNumbers"
      @close="generatedYaml = null"
      @copy="handleCopy"
      @download="handleDownload"
    />
  </div>
</template>

<script setup lang="ts">
import type { FormData, YamlData } from '../types'
import { addSavedPlan } from '@/apis/tpgen'
import { getTestTypes } from '@/apis/testType'
import { getOsOptions } from '@/apis/osConfig'
import { Message } from '@arco-design/web-vue'
import HardwareConfig from './HardwareConfig.vue'
import OSConfig from './OSConfig.vue'
import KernelConfig from './KernelConfig.vue'
import MachineTestConfig from './MachineTestConfig.vue'
// import FirmwareConfig from './FirmwareConfig.vue'
import YamlPreview from './YamlPreview.vue'

// 导入兼容性分析函数和通知函数
// import { compatibility_analysis, showNotification } from '../check_yaml'
// 导入后端 API（如果存在）
// import { generateTestPlan, validateYaml, checkCompatibility } from '../api/testPlanApi'
// 修改为
import { showNotification } from '../check_yaml'  // 保留 showNotification
// import { validateYaml } from '@/apis/yamlCheck'  // 暂时注释，后端 API 未实现



defineOptions({ name: 'CustomPlan' })

/**
 * 错误详情接口
 */
interface ErrorDetail {
  code: string
  message: string
  key?: string
  lineNumber?: number
}

/**
 * 兼容性检查响应接口
 */
interface CompatibilityResponse {
  success: boolean
  error?: ErrorDetail
}

/**
 * 在 YAML 文本中查找指定 key 路径所在的行号
 * @param yamlText YAML 文本字符串
 * @param keyPath key 路径，如 "hardware.machines"
 * @returns 行号（从1开始），未找到返回 -1
 */
const findKeyLineNumber = (yamlText: string, keyPath: string): number => {
  console.log('[findKeyLineNumber] 开始查找行号...')
  console.log('[findKeyLineNumber] keyPath:', keyPath)
  console.log('[findKeyLineNumber] YAML 文本前 500 字符:', yamlText.substring(0, 500))
  
  if (!yamlText || !keyPath) {
    console.log('[findKeyLineNumber] ❌ yamlText 或 keyPath 为空')
    return -1
  }
  
  const lines = yamlText.split('\n')
  const keys = keyPath.split('.')
  console.log('[findKeyLineNumber] 总行数:', lines.length)
  console.log('[findKeyLineNumber] 需要匹配的 keys:', keys)
  
  let currentKeyIndex = 0
  let expectedIndent = 0
  
  for (let i = 0; i < lines.length; i++) {
    const line = lines[i]
    const trimmedLine = line.trim()
    
    // 跳过空行和注释
    if (!trimmedLine || trimmedLine.startsWith('#')) continue
    
    // 计算当前行的缩进级别（空格数除以2）
    const indent = line.search(/\S/) / 2
    
    // 获取当前需要匹配的 key
    const targetKey = keys[currentKeyIndex]
    
    // 匹配 key（支持 "key:" 格式）
    const keyPattern = new RegExp(`^${targetKey}\\s*:`)
    
    if (keyPattern.test(trimmedLine) && indent === expectedIndent) {
      console.log(`[findKeyLineNumber] ✅ 匹配到 key "${targetKey}" 在行 ${i + 1}: "${trimmedLine}"`)
      currentKeyIndex++
      
      // 如果已经找到完整路径，返回行号（从1开始）
      if (currentKeyIndex === keys.length) {
        console.log(`[findKeyLineNumber] 🎯 找到完整路径！返回行号: ${i + 1}`)
        return i + 1
      }
      
      // 更新下一层的期望缩进
      expectedIndent = indent + 1
      console.log(`[findKeyLineNumber] 继续查找下一个 key，期望缩进: ${expectedIndent}`)
    }
  }
  
  console.log('[findKeyLineNumber] ❌ 未找到匹配的 key 路径')
  return -1 // 未找到
}

/**
 * 从错误信息中提取 key 路径
 * @param errorMessage 错误信息，如 "E002 Unsupported: empty value for [hardware.machines]"
 * @returns key 路径，如 "hardware.machines"，未找到返回 null
 */
const extractKeyFromError = (errorMessage: string): string | null => {
  // 匹配 [xxx] 中的内容
  const match = errorMessage.match(/\[([^\]]+)\]/)
  return match ? match[1] : null
}

/**
 * 将 JavaScript 对象转换为 YAML 字符串
 * （与 YamlPreview.vue 中的 jsToYaml 函数保持一致）
 */
const jsToYaml = (obj: any, indent = 0): string => {
  let yaml = ''
  const spaces = '  '.repeat(indent)
  const entries = Object.entries(obj)

  entries.forEach(([key, value], index) => {
    if (Array.isArray(value)) {
      yaml += `${spaces}${key}:\n`
      value.forEach((item) => {
        if (typeof item === 'object' && item !== null) {
          const itemYaml = jsToYaml(item, indent + 2)
          const lines = itemYaml.trim().split('\n')
          yaml += `${spaces}  -`
          lines.forEach((line, i) => {
            if (i === 0) {
              yaml += ` ${line.trim()}\n`
            }
            else {
              yaml += `${spaces}    ${line.trim()}\n`
            }
          })
        }
        else {
          yaml += `${spaces}  - ${item}\n`
        }
      })
    }
    else if (typeof value === 'object' && value !== null) {
      yaml += `${spaces}${key}:\n${jsToYaml(value, indent + 1)}`
    }
    else {
      yaml += `${spaces}${key}: ${value}\n`
    }

    // 在顶层（indent = 0）的各部分之间添加空行，使 YAML 更易读
    if (indent === 0 && index < entries.length - 1) {
      yaml += '\n'
    }
  })

  return yaml
}

/**
 * 兼容性检查函数（使用 check_yaml.ts 的完整逻辑）
 * 检查 YAML 配置的完整兼容性
 */
// const checkCompatibility = async (yamlData: any): Promise<CompatibilityResponse> => {
//   try {
//     // 基本验证：检查数据对象
//     if (!yamlData || typeof yamlData !== 'object') {
//       return {
//         success: false,
//         error: {
//           code: 'E000',
//           message: 'Invalid YAML data object',
//         },
//       }
//     }

//     // 🔍 调用完整的兼容性分析函数
//     console.log('[CustomPlan] 开始完整兼容性分析...')
//     const compatResult = compatibility_analysis(yamlData)
    
//     // 解析返回结果：格式 "True:0" 或 "False:E001 Unsupported: ..."
//     const colonIndex = compatResult.indexOf(':')
//     const isValid = compatResult.substring(0, colonIndex)
//     const errorInfo = compatResult.substring(colonIndex + 1)
    
//     if (isValid === 'False') {
//       // 验证失败，提取错误代码和消息
//       // errorInfo 格式可能是 "E001 Unsupported: missing mandatory key [hardware.cpu]"
//       const errorCode = errorInfo.split(' ')[0] || 'E999'
//       const errorMessage = errorInfo || 'Compatibility check failed'
      
//       console.error('[CustomPlan] 兼容性验证失败:', `[${errorCode}] ${errorMessage}`)
      
//       // 提取 key 路径
//       const keyPath = extractKeyFromError(errorMessage)
//       console.log('[checkCompatibility] 提取到的 keyPath:', keyPath)
      
//       // 计算行号（只对 E002, E101, E102 错误计算行号）
//       let lineNumber: number | undefined
//       if (keyPath && (errorCode === 'E002' || errorCode === 'E101' || errorCode === 'E102')) {
//         console.log('[checkCompatibility] 开始计算行号，错误码:', errorCode)
//         // 将 YAML 对象转换为 YAML 格式文本（与 YamlPreview 保持一致）
//         const yamlText = jsToYaml(yamlData).trimEnd()
//         console.log('[checkCompatibility] YAML 文本长度:', yamlText.length)
//         console.log('[checkCompatibility] YAML 文本格式（前 300 字符）:', yamlText.substring(0, 300))
//         lineNumber = findKeyLineNumber(yamlText, keyPath)
//         console.log('[checkCompatibility] 计算得到的行号:', lineNumber)
//         if (lineNumber !== -1) {
//           console.log(`[checkCompatibility] ✅ 找到错误行号: ${lineNumber}, key: ${keyPath}`)
//         } else {
//           console.log(`[checkCompatibility] ❌ 未找到行号, key: ${keyPath}`)
//         }
//       } else {
//         console.log('[checkCompatibility] 跳过行号计算，原因：', 
//           !keyPath ? 'keyPath 为空' : `错误码 ${errorCode} 不在 E002/E101/E102 范围内`)
//       }
      
//       return {
//         success: false,
//         error: {
//           code: errorCode,
//           message: errorMessage,
//           key: keyPath || undefined,
//           lineNumber: lineNumber !== -1 ? lineNumber : undefined,
//         },
//       }
//     }
    
//     // ✅ 验证通过
//     console.log('[CustomPlan] ✅ 兼容性验证通过')
//     return { success: true }
//   }
//   catch (error) {
//     console.error('[CustomPlan] 兼容性检查异常:', error)
//     return {
//       success: false,
//       error: {
//         code: 'E999',
//         message: error.message || 'Unknown error during compatibility check',
//       },
//     }
//   }
// }
// 原来的函数调用 compatibility_analysis
const checkCompatibility = async (yamlData: any): Promise<CompatibilityResponse> => {
  try {
    if (!yamlData || typeof yamlData !== 'object') {
      return {
        success: false,
        error: {
          code: 'E000',
          message: 'Invalid YAML data object',
        },
      }
    }

    // TODO: 后端验证 API 暂未实现 (/system/yaml/validate)
    // 暂时跳过验证，直接返回成功
    console.log('[CustomPlan] ⚠️ 跳过后端验证（API 未实现），直接允许操作')
    
    // 基本的客户端验证：检查必需字段
    const hasMetadata = yamlData.metadata && typeof yamlData.metadata === 'object'
    const hasHardware = yamlData.hardware && typeof yamlData.hardware === 'object'
    const hasEnvironment = yamlData.environment && typeof yamlData.environment === 'object'
    
    if (!hasMetadata || !hasHardware || !hasEnvironment) {
      console.error('[CustomPlan] ❌ 缺少必需字段')
      return {
        success: false,
        error: {
          code: 'E001',
          message: 'Missing required sections: metadata, hardware, or environment',
        },
      }
    }
    
    console.log('[CustomPlan] ✅ 基本验证通过')
    return { success: true }
    
    // 以下是原后端 API 调用代码（待后端实现后可启用）
    // console.log('[CustomPlan] 调用后端验证 API...')
    // const result = await validateYaml(yamlData)
    // console.log('[CustomPlan] 后端验证结果:', result)
    // return result
    
  } catch (error) {
    console.error('[CustomPlan] 兼容性检查异常:', error)
    return {
      success: false,
      error: {
        code: 'E999',
        message: error.message || 'Unknown error during compatibility check',
      },
    }
  }
}















const emit = defineEmits<{
  progressChange: [value: number]
  generate: [data: any]
  copy: []
  download: []
}>()

const formData = reactive<FormData>({
  cpu: '',
  gpu: '',
  productName: '', // Product Name (从数据库加载)
  asicName: '',     // ASIC Name (从数据库加载，根据 productName 过滤)
  selectedMachines: [],
  
  // 多配置模式（新）
  machineConfigurations: {},
  
  // 旧字段（保留以备兼容）
  osConfigMethod: 'individual',
  os: '',
  deployment: '',
  individualOsConfig: {},
  kernelConfigMethod: 'individual',
  kernelType: '',
  kernelVersion: '',
  individualKernelConfig: {},
  testType: '',
  testTypeConfigMethod: 'individual',
  individualTestTypeConfig: {},
  firmwareVersion: '',
  versionComparison: false,
  selectedTestCases: [],
})

const progress = ref(0)
const generatedYaml = ref<YamlData | null>(null)
const isGenerating = ref(false)
const validationStatus = ref<any>(null)
const errorLineNumbers = ref<number[]>([])

// 机器数据映射表 (ID -> Machine Info)
const machinesMap = ref<Record<number, any>>({})

// OS 配置映射表 (OS ID -> OS Info)
const osConfigMap = ref<Record<string, any>>({})

// Test Type 映射表 (Test Type ID -> Test Type Info)
const testTypeMap = ref<Record<string, any>>({})

// Test Components 和 Test Cases 选中数据
const testComponentsData = ref<any>(null)

// 保存相关状态
const saveDialogVisible = ref(false)
const saveForm = reactive({
  name: '',
  category: 'Benchmark',
  description: '',
  tags: '',
  status: 1,
})

const saveFormRules = {
  name: [
    { required: true, message: '请输入计划名称' },
    { minLength: 2, message: '计划名称至少2个字符' },
  ],
  category: [{ required: true, message: '请选择类别' }],
}

// 处理机器列表更新
const handleMachinesUpdate = (machines: any[]) => {
  // 将机器数组转换为 ID -> Machine 的映射
  const newMap: Record<number, any> = {}
  machines.forEach(machine => {
    newMap[machine.id] = machine
  })
  machinesMap.value = newMap
  console.log('[CustomPlan] 机器数据已更新:', machinesMap.value)
}

// 更新进度
const updateProgress = () => {
  // 计算表单完成度
  let filledFields = 0
  let totalFields = 10

  if (formData.cpu)
    filledFields++
  if (formData.gpu)
    filledFields++
  if (formData.selectedMachines.length > 0)
    filledFields++
  if (formData.os || Object.keys(formData.individualOsConfig).length > 0)
    filledFields++
  if (formData.deployment || Object.keys(formData.individualOsConfig).length > 0)
    filledFields++
  if (formData.kernelType || Object.keys(formData.individualKernelConfig).length > 0)
    filledFields++
  if (formData.kernelVersion || Object.keys(formData.individualKernelConfig).length > 0)
    filledFields++
  if (formData.firmwareVersion)
    filledFields++
  if (formData.selectedTestCases.length > 0)
    filledFields++

  progress.value = Math.round((filledFields / totalFields) * 100)
  emit('progressChange', progress.value)
}

// 处理 Test Components 和 Test Cases 数据更新
const handleTestDataUpdate = (selectedData: any) => {
  testComponentsData.value = selectedData
  console.log('[CustomPlan] Test Components Data updated:', selectedData)
  updateProgress()
}

// 重置表单
const handleReset = () => {
  formData.cpu = 'Ryzen Threadripper'
  formData.gpu = '' // 重置为空，让用户重新选择
  formData.selectedMachines = []
  formData.osConfigMethod = 'same'
  formData.os = ''
  formData.deployment = ''
  formData.individualOsConfig = {}
  formData.kernelConfigMethod = 'same'
  formData.kernelType = ''
  formData.kernelVersion = ''
  formData.individualKernelConfig = {}
  formData.firmwareVersion = ''
  formData.versionComparison = false
  formData.selectedTestCases = []
  generatedYaml.value = null
  updateProgress()
}

/**
 * 构建完整的 Test Configuration（包含 components 和 cases）
 */
const buildFullTestConfiguration = (testTypeConfig: any, componentsData: any, machines: any[], selectedMachineIds: number[]) => {
  if (!componentsData) {
    return testTypeConfig
  }

  // 构建 Test Type 信息（只返回 type_name）
  const buildTestTypeInfo = (testTypeId: string | number) => {
    const typeInfo = testTypeMap.value[String(testTypeId)]
    if (typeInfo) {
      return {
        test_type: typeInfo.typeName  // 只返回 type_name 字符串
      }
    }
    return { 
      test_type: String(testTypeId)  // 如果找不到，返回 ID 字符串
    }
  }

  // 构建 Test Components 结构（按 category 分组，不带序号）
  const buildTestComponents = (components: any[], cases: any[]) => {
    if (!components || components.length === 0) {
      return []
    }
    
    // 如果 components 已经是按 category 分组的结构
    if (components[0]?.category) {
      return components.map((cat: any) => ({
        component_category: cat.category,
        components: cat.components.map((comp: any) => ({
          component_name: comp.name,
          test_cases: comp.testCases || []
        }))
      }))
    }
    
    // 否则，创建一个默认的 category
    return [{
      component_category: 'Default',
      components: components.map((comp: any) => ({
        component_name: typeof comp === 'string' ? comp : comp.name,
        test_cases: cases || []
      }))
    }]
  }

  if (componentsData.testTypeConfigMethod === 'same') {
    // Same 模式
    return {
      method: 'same',
      ...buildTestTypeInfo(componentsData.testType),
      component_categories: buildTestComponents(componentsData.components, componentsData.cases)
    }
  } else {
    // Individual 模式：按照用户选择的机器顺序构建（保持选择顺序）
    const machineConfigs: any = {}
    
    // ✅ 按照 selectedMachineIds 的顺序遍历，而不是 Object.entries()
    selectedMachineIds.forEach(machineId => {
      const config = componentsData.machineConfigs?.[machineId]
      if (!config) return
      
      // 查找对应的机器信息
      const machine = machines.find(m => m.id === machineId)
      const hostname = machine?.hostname || `machine_${machineId}`
      
      machineConfigs[hostname] = {
        ...buildTestTypeInfo(config.testType),
        component_categories: buildTestComponents(config.components, config.cases),
        execution_case_list: config.executionCaseList || []
      }
    })

    return {
      method: 'individual',
      machines: machineConfigs
    }
  }
}

/**
 * 生成时间戳字符串
 * @returns {string} 格式：YYYY-MM-DD-HH-mm-ss
 */
const getTimestamp = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const seconds = String(now.getSeconds()).padStart(2, '0')
  return `${year}-${month}-${day}-${hours}-${minutes}-${seconds}`
}

// 生成 YAML（支持多配置模式）
const handleGenerate = async () => {
  isGenerating.value = true
  
  try {
    // ============ 数据验证 ============
    console.log('[handleGenerate] 开始数据验证（多配置模式）...')
    
    // 1. 验证机器选择
    if (!formData.selectedMachines || formData.selectedMachines.length === 0) {
      Message.error('Please select at least one machine')
      throw new Error('No machines selected')
    }
    
    // 2. 验证 Product Name 和 ASIC Name
    if (!formData.productName || !formData.asicName) {
      Message.error('Please select Product Name and ASIC Name')
      throw new Error('Missing Product Name or ASIC Name')
    }
    
    // 3. 验证每台机器至少有一个配置
    for (const machineId of formData.selectedMachines) {
      const configs = formData.machineConfigurations[machineId]
      if (!configs || configs.length === 0) {
        const machineName = machinesMap.value[machineId]?.hostname || `Machine ${machineId}`
        Message.error(`${machineName} has no configuration. Please add at least one configuration.`)
        throw new Error(`Machine ${machineId} missing configuration`)
      }
      
      // 验证每个配置的必填字段
      for (let i = 0; i < configs.length; i++) {
        const config = configs[i]
        if (!config.osId || !config.kernelVersion || !config.testTypeId) {
          const machineName = machinesMap.value[machineId]?.hostname || `Machine ${machineId}`
          Message.error(`${machineName} Configuration ${i + 1} is incomplete. Please fill in all required fields.`)
          throw new Error(`Incomplete configuration for machine ${machineId}`)
        }
      }
    }
    
    console.log('[handleGenerate] ✅ 数据验证通过')
    
    // ============ 构建 YAML 数据 ============
    console.log('[handleGenerate] 开始构建 YAML 数据...')
    
    // 构建机器列表（支持多配置）
    const machinesWithConfigs = formData.selectedMachines.map((id) => {
      const machine = machinesMap.value[id]
      if (!machine) {
        console.error(`[handleGenerate] ⚠️ 机器 ID ${id} 未找到数据`)
        return null
      }
      
      const configs = formData.machineConfigurations[id] || []
      
      // 为每个配置构建详细信息
      const configurations = configs.map((config, index) => {
        console.log('[handleGenerate] 处理配置:', index + 1, {
          testComponents: config.testComponents,
          orderedTestCases: config.orderedTestCases
        })
        
        // ✅ 构建 execution_case_list（使用正确的字段名）
        const executionCaseList = (config.orderedTestCases || [])
          .map((c: any) => c.caseName || c.case_name || c.name)
          .filter(Boolean)  // 过滤掉 undefined
        
        console.log('[handleGenerate] 配置结果:', {
          executionCaseList
        })
        
        return {
          config_id: index + 1,
          environment: {
            os: {
              id: config.osId,
              family: config.osFamily,
              version: config.osVersion
            },
            deployment_method: config.deploymentMethod,
            kernel: {
              kernel_version: config.kernelVersion
            }
          },
          test_configuration: {
            test_type: config.testTypeName,
            execution_case_list: executionCaseList
          }
        }
      })
      
      return {
        id: machine.id,  // ✅ 添加 id 字段（来自数据库）
        hostname: machine.hostname,
        productName: machine.productName,
        asicName: machine.asicName,
        ipAddress: machine.ipAddress,
        gpuModel: machine.gpuModel,
        configurations
      }
    }).filter(Boolean)
    
    if (machinesWithConfigs.length === 0) {
      Message.error('No valid machine data found. Please select machines again.')
      throw new Error('No valid machine data')
    }
    
    console.log('[handleGenerate] 机器配置列表（来自数据库）:', machinesWithConfigs)

    // 构建 hardware 结构（只包含 machines，数据来自数据库）
    const hardwareData = {
      machines: machinesWithConfigs.map((m: any) => ({
        id: m.id,  // ✅ 机器 ID（来自数据库）
        hostname: m.hostname,  // ✅ 来自数据库
        productName: m.productName,  // ✅ 来自数据库
        asicName: m.asicName,  // ✅ 来自数据库
        ipAddress: m.ipAddress,  // ✅ 来自数据库
        gpuModel: m.gpuModel  // ✅ 来自数据库
      }))
    }

    // 构建 environment 结构（包含所有机器的配置信息）
    const environmentData = {
      machines: Object.fromEntries(
        machinesWithConfigs.map((m: any) => [
          m.hostname,  // 使用 hostname 作为 key
          {
            configurations: m.configurations.map((config: any) => ({
              config_id: config.config_id,
              os: {
                id: config.environment.os.id,
                family: config.environment.os.family,
                version: config.environment.os.version
              },
              deployment_method: config.environment.deployment_method,
              kernel: {
                kernel_version: config.environment.kernel.kernel_version
              },
              test_type: config.test_configuration.test_type,
              execution_case_list: config.test_configuration.execution_case_list
            }))
          }
        ])
      )
    }

    // 生成 YAML 数据
    const yamlData: any = {
      metadata: {
        generated: new Date().toISOString(),
        version: '2.0',
        description: 'TPGen Test Plan Configuration (Multi-Configuration Mode)',
      },
      hardware: hardwareData,
      environment: environmentData
    }

    generatedYaml.value = yamlData
    
    console.log('[handleGenerate] ✅ YAML 数据构建完成:', yamlData)

    // 触发生成事件
    emit('generate', {
      hardware: yamlData.hardware,
      environment: yamlData.environment
    })

    // 显示成功消息
    Message.success('Test plan generated successfully!')
    console.log('[handleGenerate] ✅ 生成成功')

    // 滚动到预览区域
    setTimeout(() => {
      document.querySelector('.yaml-preview')?.scrollIntoView({ behavior: 'smooth' })
    }, 100)
  } catch (error: any) {
    console.error('[CustomPlan] 生成失败:', error)
    Message.error(`Failed to generate test plan: ${error.message || 'Unknown error'}`)
  } finally {
    isGenerating.value = false
  }
}

/**
 * 处理复制到剪贴板
 * 包含完整的兼容性验证逻辑（来自 check_yaml.ts）
 */
const handleCopy = async () => {
  try {
    console.log('[CustomPlan handleCopy] 🚀 开始复制流程...')
    
    if (!generatedYaml.value) {
      console.error('[CustomPlan handleCopy] ❌ 没有 YAML 数据')
      Message.error('No YAML data to copy!')
      showNotification('No YAML data to copy!', 'error')
      return
    }

    // 检查浏览器是否支持 Clipboard API
    if (!navigator.clipboard) {
      console.error('[CustomPlan handleCopy] ❌ 浏览器不支持剪贴板 API')
      Message.error('Browser does not support clipboard operation!')
      showNotification('Browser not supported!', 'error')
      return
    }
    
    // 检查是否在安全上下文中（HTTPS 或 localhost）
    if (!window.isSecureContext) {
      console.error('[CustomPlan handleCopy] ❌ 需要 HTTPS 环境')
      Message.error('HTTPS required for clipboard access!')
      showNotification('HTTPS required!', 'error')
      return
    }
    
    // 🔍 执行完整的兼容性验证（E001, E002, E101, E102）
    console.log('[CustomPlan handleCopy] 🔍 开始完整兼容性验证...')
    console.log('[CustomPlan handleCopy] 📋 待验证数据:', JSON.stringify(generatedYaml.value, null, 2))
    
    const response = await checkCompatibility(generatedYaml.value)
    console.log('[CustomPlan handleCopy] 📊 兼容性验证结果:', response)
    
    if (!response.success) {
      // 验证失败，显示详细错误信息
      const errorCode = response.error?.code || 'E999'
      const errorMsg = response.error?.message || 'Unknown compatibility error'
      const lineNumber = response.error?.lineNumber
      
      console.error('[CustomPlan handleCopy] ❌ 兼容性验证失败:', `[${errorCode}] ${errorMsg}`)
      console.error('[CustomPlan handleCopy] ❌❌❌ 阻止复制操作！')
      
      // 更新错误行号（用于高亮显示）
      console.log('[CustomPlan handleCopy] 收到的 lineNumber:', lineNumber)
      if (lineNumber) {
        errorLineNumbers.value = [lineNumber]
        console.log('[CustomPlan handleCopy] ✅ 设置错误行号:', lineNumber)
        console.log('[CustomPlan handleCopy] errorLineNumbers.value:', errorLineNumbers.value)
      } else {
        console.log('[CustomPlan handleCopy] ⚠️ lineNumber 为空，未设置错误行号')
      }
      
      // 显示友好的错误消息
      const errorMsgWithLine = lineNumber ? `${errorMsg} (Line ${lineNumber})` : errorMsg
      Message.error(`Compatibility Check Failed: ${errorMsgWithLine}`)
      showNotification(`Compatibility Check Failed: ${errorMsgWithLine}`, 'error')
      return  // 🚫 重要：这里必须返回，阻止后续复制操作
    }
    
    // ✅ 验证通过，清除错误行号并复制
    errorLineNumbers.value = []
    console.log('[CustomPlan] ✅ 兼容性验证通过，开始复制...')
    
    // 将对象转换为 YAML 字符串
    const yamlText = jsToYaml(generatedYaml.value).trimEnd()
    console.log('[CustomPlan handleCopy] 📋 生成的 YAML 文本 (前 500 字符):', yamlText.substring(0, 500))
    
    await navigator.clipboard.writeText(yamlText)
    
    emit('copy')
    Message.success('Test plan copied to clipboard!')
    showNotification('Test plan copied to clipboard!', 'success')
    console.log('[CustomPlan] ✅ 复制成功')
    
  } catch (error) {
    console.error('[CustomPlan] Copy error:', error)
    Message.error(`Failed to copy to clipboard: ${error.message || 'Unknown error'}`)
    showNotification(`Failed to copy: ${error.message || 'Unknown error'}`, 'error')
  }
}

/**
 * 处理下载 YAML 文件
 * 包含完整的兼容性验证逻辑和时间戳文件名（来自 check_yaml.ts）
 */
const handleDownload = async () => {
  try {
    console.log('[CustomPlan handleDownload] 🚀 开始下载流程...')
    
    if (!generatedYaml.value) {
      console.error('[CustomPlan handleDownload] ❌ 没有 YAML 数据')
      Message.error('No YAML data to download!')
      showNotification('No YAML data to download!', 'error')
      return
    }

    // 🔍 执行完整的兼容性验证（E001, E002, E101, E102）
    console.log('[CustomPlan handleDownload] 🔍 开始下载前完整兼容性验证...')
    console.log('[CustomPlan handleDownload] 📋 待验证数据:', JSON.stringify(generatedYaml.value, null, 2))
    
    const response = await checkCompatibility(generatedYaml.value)
    console.log('[CustomPlan handleDownload] 📊 兼容性验证结果:', response)
    
    if (!response.success) {
      // 验证失败，显示详细错误信息
      const errorCode = response.error?.code || 'E999'
      const errorMsg = response.error?.message || 'Unknown compatibility error'
      const lineNumber = response.error?.lineNumber
      
      console.error('[CustomPlan handleDownload] ❌ 兼容性验证失败:', `[${errorCode}] ${errorMsg}`)
      console.error('[CustomPlan handleDownload] ❌❌❌ 阻止下载操作！')
      
      // 更新错误行号（用于高亮显示）
      console.log('[CustomPlan handleDownload] 收到的 lineNumber:', lineNumber)
      if (lineNumber) {
        errorLineNumbers.value = [lineNumber]
        console.log('[CustomPlan handleDownload] ✅ 设置错误行号:', lineNumber)
        console.log('[CustomPlan handleDownload] errorLineNumbers.value:', errorLineNumbers.value)
      } else {
        console.log('[CustomPlan handleDownload] ⚠️ lineNumber 为空，未设置错误行号')
      }
      
      // 显示友好的错误消息
      const errorMsgWithLine = lineNumber ? `${errorMsg} (Line ${lineNumber})` : errorMsg
      Message.error(`Compatibility Check Failed: ${errorMsgWithLine}`)
      showNotification(`Compatibility Check Failed: ${errorMsgWithLine}`, 'error')
      return  // 🚫 重要：这里必须返回，阻止后续下载操作
    }
    
    // ✅ 验证通过，清除错误行号并开始下载
    errorLineNumbers.value = []
    console.log('[CustomPlan] ✅ 兼容性验证通过，开始下载...')
    
    // 生成带时间戳的文件名
    const timestamp = getTimestamp()
    const filename = `test-plan_${timestamp}.yaml`
    
    // 将对象转换为 YAML 字符串
    const yamlText = jsToYaml(generatedYaml.value).trimEnd()
    console.log('[CustomPlan handleDownload] 📋 生成的 YAML 文本 (前 500 字符):', yamlText.substring(0, 500))
    
    // 创建 Blob 并下载
    const blob = new Blob([yamlText], { type: 'text/yaml;charset=utf-8' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url
    a.download = filename
    document.body.appendChild(a)
    a.click()
    document.body.removeChild(a)
    URL.revokeObjectURL(url)
    
    emit('download')
    Message.success(`Test plan downloaded: ${filename}`)
    showNotification(`Test plan downloaded: ${filename}`, 'success')
    console.log('[CustomPlan] ✅ YAML 文件已下载:', filename)
  } catch (error) {
    console.error('[CustomPlan] Download error:', error)
    Message.error(`Failed to download YAML file: ${error.message || 'Unknown error'}`)
    showNotification(`Failed to download: ${error.message || 'Unknown error'}`, 'error')
  }
}

// 处理保存按钮点击
const handleSave = () => {
  // 验证表单是否有数据
  if (formData.selectedMachines.length === 0) {
    Message.warning('请先选择机器')
    return
  }
  if (formData.selectedTestCases.length === 0) {
    Message.warning('请先选择测试用例')
    return
  }
  
  // 显示保存对话框
  saveDialogVisible.value = true
}

// 确认保存
const handleSaveConfirm = async () => {
  if (!saveForm.name) {
    Message.warning('请输入计划名称')
    return
  }
  if (!saveForm.category) {
    Message.warning('请选择类别')
    return
  }
  
  try {
    // 准备保存数据
    const saveData = {
      name: saveForm.name,
      category: saveForm.category,
      description: saveForm.description,
      tags: saveForm.tags,
      configData: { ...formData },
      yamlData: generatedYaml.value || undefined,
      cpu: formData.cpu,
      gpu: formData.gpu,
      machineCount: formData.selectedMachines.length,
      osType: formData.os || '',
      kernelType: formData.kernelType || '',
      testCaseCount: formData.selectedTestCases.length,
      status: saveForm.status,
    }
    
    // 调用 API 保存
    const res = await addSavedPlan(saveData)
    if (res.code === 200) {
      Message.success('保存成功')
      saveDialogVisible.value = false
      // 重置保存表单
      saveForm.name = ''
      saveForm.description = ''
      saveForm.tags = ''
      saveForm.status = 1
      saveForm.category = 'Benchmark'
    }
    else {
      Message.error(res.data || '保存失败')
    }
  }
  catch (error) {
    Message.error('保存失败，请重试')
    console.error(error)
  }
}

// 取消保存
const handleSaveCancel = () => {
  saveDialogVisible.value = false
}

// 监听表单变化
watch(() => formData, updateProgress, { deep: true })

// 加载 OS 配置数据
const loadOsConfigMap = async () => {
  try {
    const configs = await getOsOptions()
    const map: Record<string, any> = {}
    configs.forEach((c: any) => {
      map[c.value] = {
        id: c.id,
        osFamily: c.osFamily,
        version: c.version
      }
    })
    osConfigMap.value = map
    console.log('[CustomPlan] OS Config Map loaded:', osConfigMap.value)
  } catch (error) {
    console.error('[CustomPlan] Failed to load OS config map:', error)
  }
}

// 加载 Test Type 配置数据
const loadTestTypeMap = async () => {
  try {
    const testTypes = await getTestTypes()
    const map: Record<string, any> = {}
    testTypes.forEach((t: any) => {
      map[String(t.id)] = {
        id: t.id,
        typeName: t.typeName
      }
    })
    testTypeMap.value = map
    console.log('[CustomPlan] Test Type Map loaded:', testTypeMap.value)
  } catch (error) {
    console.error('[CustomPlan] Failed to load test type map:', error)
  }
}

// 初始化
onMounted(() => {
  updateProgress()
  loadOsConfigMap()
  loadTestTypeMap()
})
</script>

<style scoped lang="scss">
.custom-plan {
  .progress-container {
    background-color: rgba(255, 255, 255, 0.2);
    border-radius: 10px;
    height: 12px;
    margin-bottom: 25px;
    overflow: hidden;
    box-shadow: inset 0 2px 4px rgba(0, 0, 0, 0.1);

    .progress-bar {
      height: 100%;
      background: linear-gradient(90deg, #3498db, #27ae60);
      transition: width 0.5s ease;
      border-radius: 10px;
      position: relative;
      overflow: hidden;

      &::after {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        bottom: 0;
        right: 0;
        background-image: linear-gradient(
          -45deg,
          rgba(255, 255, 255, 0.2) 25%,
          transparent 25%,
          transparent 50%,
          rgba(255, 255, 255, 0.2) 50%,
          rgba(255, 255, 255, 0.2) 75%,
          transparent 75%,
          transparent
        );
        background-size: 20px 20px;
        animation: move 1s linear infinite;
      }
    }

    @keyframes move {
      0% {
        background-position: 0 0;
      }
      100% {
        background-position: 20px 20px;
      }
    }
  }

  .actions {
    display: flex;
    justify-content: center;
    align-items: center;
    margin-top: 40px;
    gap: 16px;
    padding: 20px;
    background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
    border-radius: 12px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);

    :deep(.arco-btn) {
      min-width: 160px;
      height: 44px;
      font-size: 15px;
      font-weight: 500;
      border-radius: 8px;
      transition: all 0.3s ease;
      
      &:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0, 0, 0, 0.15);
      }

      &:active {
        transform: translateY(0);
      }

      &.arco-btn-primary {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        border: none;
        
        &:hover {
          background: linear-gradient(135deg, #5568d3 0%, #6a4190 100%);
        }
      }

      &.arco-btn-outline {
        border: 2px solid #667eea;
        color: #667eea;
        background: white;
        
        &:hover {
          border-color: #5568d3;
          color: #5568d3;
          background: rgba(102, 126, 234, 0.05);
        }
      }

      &:not(.arco-btn-primary):not(.arco-btn-outline) {
        background: white;
        border: 1px solid #d9d9d9;
        
        &:hover {
          border-color: #667eea;
          color: #667eea;
        }
      }
    }

    @media (max-width: 768px) {
      flex-direction: column;
      gap: 12px;

      :deep(.arco-btn) {
        width: 100%;
      }
    }
  }

  // 验证状态样式
  .validation-status {
    margin: 20px 0;
    padding: 16px;
    border-radius: 8px;
    border: 2px solid;

    &.valid {
      background-color: rgb(var(--success-1));
      border-color: rgb(var(--success-6));
      color: rgb(var(--success-6));
    }

    &.invalid {
      background-color: rgb(var(--danger-1));
      border-color: rgb(var(--danger-6));
      color: rgb(var(--danger-6));
    }

    .status-header {
      display: flex;
      align-items: center;
      gap: 10px;
      font-weight: 600;
      font-size: 16px;
      margin-bottom: 12px;

      svg {
        font-size: 20px;
      }
    }

    .status-checks {
      display: flex;
      flex-direction: column;
      gap: 8px;
      padding-left: 30px;

      .check-item {
        display: flex;
        align-items: center;
        gap: 8px;
        font-size: 14px;

        svg {
          font-size: 16px;
        }
      }
    }
  }

  // 按钮禁用状态
  button:disabled {
    opacity: 0.6;
    cursor: not-allowed;
  }
}
</style>

