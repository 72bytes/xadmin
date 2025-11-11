<template>
  <div class="custom-plan">
    <!-- 进度条 -->
    <div class="progress-container">
      <div class="progress-bar" :style="{ width: `${progress}%` }" />
    </div>

    <a-form :model="formData" layout="vertical">
      <!-- 硬件平台配置 -->
      <HardwareConfig
        v-model:cpu="formData.cpu"
        v-model:gpu="formData.gpu"
        v-model:selected-machines="formData.selectedMachines"
        @update="updateProgress"
      />

      <!-- 操作系统环境 -->
      <OSConfig
        v-model:config-method="formData.osConfigMethod"
        v-model:os="formData.os"
        v-model:deployment="formData.deployment"
        v-model:individual-config="formData.individualOsConfig"
        :selected-machines="formData.selectedMachines"
        @update="updateProgress"
      />

      <!-- 内核和驱动配置 -->
      <KernelConfig
        v-model:config-method="formData.kernelConfigMethod"
        v-model:kernel-type="formData.kernelType"
        v-model:kernel-version="formData.kernelVersion"
        v-model:individual-config="formData.individualKernelConfig"
        :selected-machines="formData.selectedMachines"
        @update="updateProgress"
      />

      <!-- 固件管理
      <FirmwareConfig
        v-model:firmware-version="formData.firmwareVersion"
        v-model:version-comparison="formData.versionComparison"
        @update="updateProgress"
      /> -->

      <!-- 管理测试用例 -->
      <TestCaseManager
        v-model:selected-test-cases="formData.selectedTestCases"
        @update="updateProgress"
      />

      <!-- 操作按钮 -->
      <div class="actions">
        <a-button @click="handleReset" :disabled="isGenerating">
          <template #icon><icon-refresh /></template>
          Reset Form
        </a-button>
        <a-button 
          type="primary" 
          @click="handleGenerate"
          :loading="isGenerating"
          :disabled="isGenerating"
        >
          <template #icon v-if="!isGenerating"><icon-settings /></template>
          {{ isGenerating ? 'Generating...' : 'Generate Test Plan' }}
        </a-button>
        <a-space>
          <a-button type="outline" @click="handleSave">
            <template #icon><icon-save /></template>
            Save Plan
          </a-button>
          <a-button type="primary" @click="handleGenerate">
            <template #icon><icon-settings /></template>
            Generate Test Plan
          </a-button>
        </a-space>
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
import { mockMachines } from '../mockData'
import { addSavedPlan } from '@/apis/tpgen'
import { Message } from '@arco-design/web-vue'
import HardwareConfig from './HardwareConfig.vue'
import OSConfig from './OSConfig.vue'
import KernelConfig from './KernelConfig.vue'
// import FirmwareConfig from './FirmwareConfig.vue'
import TestCaseManager from './TestCaseManager.vue'
import YamlPreview from './YamlPreview.vue'

// 导入兼容性分析函数和通知函数
// import { compatibility_analysis, showNotification } from '../check_yaml'
// 导入后端 API（如果存在）
// import { generateTestPlan, validateYaml, checkCompatibility } from '../api/testPlanApi'
// 修改为
import { showNotification } from '../check_yaml'  // 保留 showNotification
import { validateYaml } from '@/apis/yamlCheck'  // 新增



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

  for (const [key, value] of Object.entries(obj)) {
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
  }

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

    // 旧代码：调用前端函数
    // const compatResult = compatibility_analysis(yamlData)
    
    // 新代码：调用后端 API
    console.log('[CustomPlan] 调用后端验证 API...')
    const result = await validateYaml(yamlData)
    console.log('[CustomPlan] 后端验证结果:', result)
    
    return result
    
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
  cpu: 'Ryzen Threadripper',
  gpu: '', // 初始为空，等待从数据库加载真实选项后自动选择
  selectedMachines: [],
  osConfigMethod: 'same',
  os: '',
  deployment: '',
  individualOsConfig: {},
  kernelConfigMethod: 'same',
  kernelType: '',
  kernelVersion: '',
  individualKernelConfig: {},
  firmwareVersion: '',
  versionComparison: false,
  selectedTestCases: [],
})

const progress = ref(0)
const generatedYaml = ref<YamlData | null>(null)
const isGenerating = ref(false)
const validationStatus = ref<any>(null)
const errorLineNumbers = ref<number[]>([])

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

// 生成 YAML
const handleGenerate = async () => {
  isGenerating.value = true
  
  try {
  // 获取操作系统配置
  const osConfig = formData.osConfigMethod === 'same'
    ? {
        method: 'same',
        os: formData.os,
        deployment: formData.deployment,
      }
    : {
        method: 'individual',
        machines: formData.individualOsConfig,
      }

  // 获取内核配置
  const kernelConfig = formData.kernelConfigMethod === 'same'
    ? {
        method: 'same',
        type: formData.kernelType,
        version: formData.kernelVersion,
      }
    : {
        method: 'individual',
        machines: formData.individualKernelConfig,
      }

  // 构建测试套件
  const testSuites = formData.selectedTestCases.map((testCase, index) => ({
    id: testCase.id,
    name: testCase.name,
    description: testCase.description,
    type: testCase.testType || '',
    subgroup: testCase.subgroup || '',
    order: index + 1,
  }))

  // 生成 YAML 数据
  const yamlData: YamlData = {
    metadata: {
      generated: new Date().toISOString(),
      version: '1.0',
    },
    hardware: {
      cpu: formData.cpu,
      gpu: formData.gpu,
      machines: formData.selectedMachines.map((id) => {
        const machine = mockMachines.find(m => m.id === id)!
        return {
          id: machine.id,
          name: machine.name,
          specs: {
            motherboard: machine.motherboard,
            gpu: machine.gpu,
            cpu: machine.cpu,
          },
        }
      }),
    },
    environment: {
      os: osConfig,
      kernel: kernelConfig,
    },
    firmware: {
      gpu_version: formData.firmwareVersion,
      comparison: formData.versionComparison,
    },
    test_suites: testSuites,
  }

  generatedYaml.value = yamlData

  // 触发生成事件
  emit('generate', {
    hardware: yamlData.hardware,
    environment: yamlData.environment,
    firmware: yamlData.firmware,
    testSuites: yamlData.test_suites,
  })

  // 显示成功消息
  Message.success('Test plan generated successfully!')

  // 滚动到预览区域
  setTimeout(() => {
    document.querySelector('.yaml-preview')?.scrollIntoView({ behavior: 'smooth' })
  }, 100)
  } catch (error) {
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
    const yamlText = JSON.stringify(generatedYaml.value, null, 2)
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
    
    // 将 YAML 对象转换为字符串
    const yamlText = JSON.stringify(generatedYaml.value, null, 2)
    
    // 创建 Blob 并下载
    const blob = new Blob([yamlText], { type: 'text/yaml' })
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

// 初始化
onMounted(() => {
  updateProgress()
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
    justify-content: space-between;
    margin-top: 40px;
    gap: 15px;

    @media (max-width: 768px) {
      flex-direction: column;
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

