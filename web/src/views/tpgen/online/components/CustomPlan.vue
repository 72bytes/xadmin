<template>
  <div class="custom-plan">


    <a-form :model="formData" layout="vertical">
      <!-- 硬件平台配置 -->
      <HardwareConfig
        v-model:product-name="formData.productName"
        v-model:asic-name="formData.asicName"
        v-model:selected-machines="formData.selectedMachines"

        @machines-update="handleMachinesUpdate"
      />

      <!-- 多配置管理（新版本） -->
      <!-- <MachineTestConfig
        :selected-machines="formData.selectedMachines"
        :machines-map="machinesMap"
        v-model:machine-configurations="formData.machineConfigurations"
        @update="updateProgress"
      /> -->

      <MachineTestConfig
        :selected-machines="formData.selectedMachines"
        :machines-map="machinesMap"
        v-model:machine-configurations="formData.machineConfigurations"
   
        @test-components-loading="handleTestComponentsLoading"
      />


      <!-- 操作按钮 -->
      <div class="actions">
        <a-button type="primary" @click="handleReset" :disabled="isGenerating">
          <template #icon><icon-refresh /></template>
          Reset Form
        </a-button>
      
        <a-space>
          <a-button 
            type="primary" 
            @click="handleGenerate"
            :loading="isGenerating"
            :disabled="isGenerating"
          >
            <!-- <template #icon v-if="!isGenerating"><icon-settings /></template> -->
            <template #icon v-if="!isGenerating"><icon-eye /></template>
            {{ isGenerating ? 'Previewing...' : 'Preview Test Plan' }}
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
      :is-edit-mode="!!editingPlanId"
      :editing-plan-id="editingPlanId || ''"
      @close="generatedYaml = null"
      @copy="handleCopy"
      @download="handleDownload"
      @save="handleSavePlan"
      @update="handleUpdatePlan"
    />

    <!-- 保存对话框 -->
    <a-modal
      v-model:visible="saveDialogVisible"
      title="SAVE TEST PLAN"
      @ok="handleSaveConfirm"
      @cancel="handleSaveCancel"
      :ok-loading="isSaving"
      :ok-text="'SAVE'"
      :cancel-text="'CANCEL'"
    >
      <a-form :model="saveForm" layout="vertical">
        <a-form-item label="PLAN NAME" required>
          <a-input v-model="saveForm.name" placeholder="please input plan name" />
        </a-form-item>
        
        <!-- <a-form-item label="类别" required>
          <a-select v-model="saveForm.category" placeholder="请选择类别">
            <a-option value="Benchmark">Benchmark</a-option>
            <a-option value="Stress">Stress</a-option>
            <a-option value="Functional">Functional</a-option>
            <a-option value="Performance">Performance</a-option>
          </a-select>
        </a-form-item> -->
        
        <a-form-item label="DESCRIPTION">
          <a-textarea 
            v-model="saveForm.description" 
            placeholder="please input description"
            :rows="3"
          />
        </a-form-item>
        
        <!-- <a-form-item label="TAGS">
          <a-input 
            v-model="saveForm.tags" 
            placeholder="please input tags, multiple tags separated by commas"
          />
        </a-form-item> -->
        <a-form-item label="STATUS">
          <a-radio-group v-model="saveForm.status">
            <a-radio :value="1">private</a-radio>
            <a-radio :value="2">public</a-radio>
          </a-radio-group>
        </a-form-item>
      </a-form>
    </a-modal>
  </div>

</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted, nextTick } from 'vue'
import { Message } from '@arco-design/web-vue'
import type { FormData, YamlData } from '../types'
import { addSavedPlan, updateSavedPlan } from '@/apis/tpgen'
import { getTestTypes } from '@/apis/testType'
import { getOsOptions } from '@/apis/osConfig'
import HardwareConfig from './HardwareConfig.vue'
import OSConfig from './OSConfig.vue'
import KernelConfig from './KernelConfig.vue'
import MachineTestConfig from './MachineTestConfig.vue'
import YamlPreview from './YamlPreview.vue'
import { jsToYaml } from '../utils/yamlConverter'
import { useTpgenStore } from '@/stores'

// 导入兼容性分析函数和通知函数
import { showNotification } from '../check_yaml'  // 保留 showNotification
import { validateYaml } from '@/apis/yamlCheck'
import { useMachines } from '../composables/useMachines'

defineOptions({ name: 'CustomPlan' })

// 使用 machines composable
const { machines, getMachineById, loadMachines } = useMachines()

// 使用 tpgen store 管理编辑状态
const tpgenStore = useTpgenStore()

// 编辑计划的 ID（用于更新操作）
const editingPlanId = ref<string | null>(null)

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


/**
 * 从错误信息中提取 key 路径
 * @param errorMessage 错误信息，如 "E002 Unsupported: empty value for [hardware.machines]"
 * @returns key 路径，如 "hardware.machines"，未找到返回 null
 */

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
    // 生成 YAML 文本用于准确的行号查找
    const yamlText = jsToYaml(yamlData)
    const result = await validateYaml(yamlData, yamlText)
    console.log('[CustomPlan] 后端验证结果:', result)

    return result
  } catch (error: any) {
    console.error('[CustomPlan] 兼容性检查异常:', error)
    return {
      success: false,
      error: {
        code: 'E999',
        message: error?.message || 'Unknown error during compatibility check',
      },
    }
  }
}


const emit = defineEmits<{
  // progressChange: [value: number]
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

// const progress = ref(0)
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

// Test Components 加载状态
const isTestComponentsLoading = ref(false)

// 保存相关状态
const saveDialogVisible = ref(false)
const isSaving = ref(false)
const saveForm = reactive({
  name: '',
  category: 'Benchmark',
  description: '',
  tags: '',
  status: 1,
})


// // 处理机器列表更新
// const handleMachinesUpdate = (machines: any[]) => {
//   // 将机器数组转换为 ID -> Machine 的映射
//   const newMap: Record<number, any> = {}
//   machines.forEach(machine => {
//     newMap[machine.id] = machine
//   })
//   machinesMap.value = newMap
//   console.log('[CustomPlan] 机器数据已更新:', machinesMap.value)
// }

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

// 处理 Test Components 加载状态变化
const handleTestComponentsLoading = (loading: boolean) => {
  isTestComponentsLoading.value = loading
  console.log('[CustomPlan] Test Components Loading:', loading)
}




// // 更新进度
// const updateProgress = () => {
//   // 计算表单完成度
//   let filledFields = 0
//   let totalFields = 10

//   if (formData.cpu)
//     filledFields++
//   if (formData.gpu)
//     filledFields++
//   if (formData.selectedMachines.length > 0)
//     filledFields++
//   if (formData.os || Object.keys(formData.individualOsConfig).length > 0)
//     filledFields++
//   if (formData.deployment || Object.keys(formData.individualOsConfig).length > 0)
//     filledFields++
//   if (formData.kernelType || Object.keys(formData.individualKernelConfig).length > 0)
//     filledFields++
//   if (formData.kernelVersion || Object.keys(formData.individualKernelConfig).length > 0)
//     filledFields++
//   if (formData.firmwareVersion)
//     filledFields++
//   if (formData.selectedTestCases.length > 0)
//     filledFields++

//   progress.value = Math.round((filledFields / totalFields) * 100)
//   emit('progressChange', progress.value)
// }

// 处理 Test Components 和 Test Cases 数据更新
const handleTestDataUpdate = (selectedData: any) => {
  testComponentsData.value = selectedData
  console.log('[CustomPlan] Test Components Data updated:', selectedData)
  // updateProgress()
}

// // 重置表单
// const handleReset = () => {
//   formData.cpu = 'Ryzen Threadripper'
//   formData.gpu = '' // 重置为空，让用户重新选择
//   formData.selectedMachines = []
//   formData.osConfigMethod = 'same'
//   formData.os = ''
//   formData.deployment = ''
//   formData.individualOsConfig = {}
//   formData.kernelConfigMethod = 'same'
//   formData.kernelType = ''
//   formData.kernelVersion = ''
//   formData.individualKernelConfig = {}
//   formData.firmwareVersion = ''
//   formData.versionComparison = false
//   formData.selectedTestCases = []
//   generatedYaml.value = null
//   updateProgress()
//   showNotification('Reset form successfully!')
// }

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
  
  // 多配置模式的字段
  formData.machineConfigurations = {}
  
  generatedYaml.value = null
  errorLineNumbers.value = []  // ← 添加这一行！清空错误高亮行
  // updateProgress()
  showNotification('Reset form successfully!')  // ← 添加这一行！用户提示
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
  console.log('[handleGenerate] 🚀 开始生成...')

  // 检查是否有配置正在加载 Test Components
  if (isTestComponentsLoading.value) {
    console.log('[handleGenerate] ⏳ Test Components are loading')
    showNotification('Loading Test Components, please click later', 'error')
    return
  }

  isGenerating.value = true

  try {
    // ============ 数据验证 ============
    console.log('[handleGenerate] 开始数据验证（多配置模式）...')
    console.log('[handleGenerate] formData:', {
      selectedMachines: formData.selectedMachines,
      productName: formData.productName,
      asicName: formData.asicName,
      machineConfigurations: formData.machineConfigurations
    })
    
    // 1. 验证机器选择
    if (!formData.selectedMachines || formData.selectedMachines.length === 0) {
      console.error('[handleGenerate] ❌ 没有选择机器')
      showNotification('Please select at least one machine', 'error')
      isGenerating.value = false
      return
    }
    
    // 2. 验证 Product Name 和 ASIC Name
    if (!formData.productName || !formData.asicName) {
      // Message.error('Please select Product Name and ASIC Name')
      showNotification('Please select Product Name and ASIC Name', 'error')
      isGenerating.value = false  // ← 添加
      return  // ← 改为 return
    }
    
    // 3. 验证每台机器至少有一个配置
    for (const machineId of formData.selectedMachines) {
      const configs = formData.machineConfigurations[machineId]
      if (!configs || configs.length === 0) {
        const machineName = machinesMap.value[machineId]?.hostname || `Machine ${machineId}`
        // Message.error(`${machineName} has no configuration. Please add at least one configuration.`)
        showNotification(`${machineName}  has no configuration. Please add at least one configuration.`, 'error')
        isGenerating.value = false  // ← 添加
        return  // ← 改为 return
      }
      
      // 验证每个配置的必填字段
      for (let i = 0; i < configs.length; i++) {
        const config = configs[i]
        if (!config.osId || !config.kernelVersion || !config.testTypeId ) {
          const machineName = machinesMap.value[machineId]?.hostname || `Machine ${machineId}`
          // Message.error(`${machineName} Configuration ${i + 1} is incomplete. Please fill in all required fields.`)
          showNotification(`${machineName} Configuration ${i + 1} is incomplete`, 'error')
          isGenerating.value = false  // ← 添加
          return  // ← 改为 return
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
              id: Number(config.osId),  // 正确转换为数字类型
              // id: config.osId,  // 注入故障用
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
      // Message.error('No valid machine data found. Please select machines again.')
      showNotification('No valid machine data found. Please select machines again.', 'error')
      isGenerating.value = false  // ← 添加
      return  // ← 改为 return
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
                id: Number(config.environment.os.id),  // 确保为数字类型
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
    showNotification('Test plan generated successfully!', 'success')
    console.log('[handleGenerate] ✅ 生成成功')

    // 更新进度
    // progress.value = 100
    // emit('progressChange', 100)

    // 滚动到预览区域
    setTimeout(() => {
      document.querySelector('.yaml-preview')?.scrollIntoView({ behavior: 'smooth' })
    }, 100)

  } catch (error: any) {
    console.error('[handleGenerate] ❌ 生成失败:', error)
    console.error('[handleGenerate] 错误堆栈:', error.stack)
    // Message.error(`Failed to generate test plan: ${error.message || 'Unknown error'}`)
    showNotification(`Failed to generate: ${error.message || 'Unknown error'}`, 'error')

  } finally {
    console.log('[handleGenerate] 🏁 完成，重置 isGenerating')
    isGenerating.value = false
  }
}

const copyToClipboard = async (text) => {
  // 方法1: 优先使用 Clipboard API（现代浏览器 + HTTPS/localhost）
  if (navigator.clipboard && window.isSecureContext) {
    try {
      await navigator.clipboard.writeText(text)
      return { success: true, method: 'clipboard-api' }
    } catch (err) {
      console.warn('[copyToClipboard] Clipboard API 失败，尝试降级方案:', err)
      // 继续尝试降级方案
    }
  }

  // 方法2: 降级使用 execCommand（兼容 HTTP 环境）
  try {
    const textarea = document.createElement('textarea')
    textarea.value = text
    
    // 避免影响页面布局和可见性
    textarea.style.position = 'fixed'
    textarea.style.top = '-9999px'
    textarea.style.left = '-9999px'
    textarea.style.opacity = '0'
    textarea.style.pointerEvents = 'none'
    textarea.setAttribute('readonly', '')
    
    document.body.appendChild(textarea)
    
    // 选中文本
    textarea.select()
    textarea.setSelectionRange(0, textarea.value.length)
    
    // 执行复制
    const successful = document.execCommand('copy')
    // 执行复制

    // 清理
    document.body.removeChild(textarea)
    
    if (successful) {
      return { success: true, method: 'execCommand' }
    } else {
      throw new Error('execCommand 返回 false')
    }
  } catch (err) {
    console.error('[copyToClipboard] 所有复制方法都失败:', err)
    return { success: false, error: err.message }
  }
}



/**
 * 处理复制到剪贴板
 * 包含完整的兼容性验证逻辑（来自 check_yaml.ts）
 */
const handleCopy = async () => {
  try {
    console.log('[CustomPlan handleCopy] 🚀 开始复制流程...')
    console.log('navigator.clipboard:', navigator.clipboard);
    // 检查1: navigator.clipboard 是否存在
    console.log('navigator.clipboard:', navigator.clipboard);

    // 检查2: 是否在安全上下文中
    console.log('isSecureContext:', window.isSecureContext);

    // 检查3: 当前协议
    console.log('protocol:', window.location.protocol);

    // 检查4: 当前 hostname
    console.log('hostname:', window.location.hostname);

    // 检查5: 浏览器信息
    console.log('userAgent:', navigator.userAgent);
    
    if (!generatedYaml.value) {
      console.error('[CustomPlan handleCopy] ❌ 没有 YAML 数据')
      // Message.error('No YAML data to copy!')
      showNotification('No YAML data to copy!', 'error')
      return
    }

    // // 检查浏览器是否支持 Clipboard API
    // if (!navigator.clipboard) {
    //   console.error('[CustomPlan handleCopy] ❌ 浏览器不支持剪贴板 API')
    //   // Message.error('Browser does not support clipboard operation!')
    //   showNotification('Browser does not support clipboard operation!', 'error')
    //   return
    // }
    
    // // 检查是否在安全上下文中（HTTPS 或 localhost）
    // if (!window.isSecureContext) {
    //   console.error('[CustomPlan handleCopy] ❌ 需要 HTTPS 环境')
    //   // Message.error('HTTPS required for clipboard access!')
    //   showNotification('HTTPS required for clipboard access!', 'error')
    //   return
    // }
    
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
      // Message.error(`Compatibility Check Failed: ${errorMsgWithLine}`)
      showNotification(`Compatibility Check Failed: ${errorMsgWithLine}`, 'error')
      return  // 🚫 重要：这里必须返回，阻止后续复制操作
    }
    
    // ✅ 验证通过，清除错误行号并复制
    errorLineNumbers.value = []
    console.log('[CustomPlan] ✅ 兼容性验证通过，开始复制...')
    
    // 将对象转换为 YAML 字符串
    const yamlText = jsToYaml(generatedYaml.value).trimEnd()
    console.log('[CustomPlan handleCopy] 📋 生成的 YAML 文本 (前 500 字符):', yamlText.substring(0, 500))
    
    // await navigator.clipboard.writeText(yamlText)
    // 🎯 使用降级方案复制
    const result = await copyToClipboard(yamlText)
    
    // emit('copy')
    // Message.success('Test plan copied to clipboard!')
    showNotification('Test plan copied to clipboard!', 'success')
    // console.log('[CustomPlan] ✅ 复制成功')
    if (result.success) {
      console.log(`[CustomPlan] ✅ 复制成功 (使用 ${result.method})`)
      emit('copy')
      showNotification('Test plan copied to clipboard!', 'success')
    } else {
      throw new Error(result.error || 'Copy failed')
    }
    
  } catch (error) {
    console.error('[CustomPlan] Copy error:', error)
    // Message.error(`Failed to copy to clipboard: ${error.message || 'Unknown error'}`)
    showNotification(`Failed to copy to clipboard: ${error.message || 'Unknown error'}`, 'error')
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
      // Message.error('No YAML data to download!')
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
      // Message.error(`Compatibility Check Failed: ${errorMsgWithLine}`)
      showNotification(`Compatibility Check Failed: ${errorMsgWithLine}`, 'error')
      return  // 🚫 重要：这里必须返回，阻止后续下载操作
    }
    
    // ✅ 验证通过，清除错误行号并开始下载
    errorLineNumbers.value = []
    console.log('[CustomPlan] ✅ 兼容性验证通过，开始下载...')
    
    // 生成带时间戳的文件名
    const timestamp = getTimestamp()
    
    // 从 YAML 数据中提取 Test Type 和 Product Name
    let testType = 'Unknown'
    let productName = 'Unknown'
    
    try {
      // 提取第一个机器的 Product Name
      if (generatedYaml.value?.hardware?.machines?.length > 0) {
        const firstMachine = generatedYaml.value.hardware.machines[0]
        if (firstMachine.productName) {
          productName = firstMachine.productName
        }
      }
      
      // 提取第一个配置的 Test Type
      if (generatedYaml.value?.environment?.machines) {
        const machineNames = Object.keys(generatedYaml.value.environment.machines)
        if (machineNames.length > 0) {
          const firstMachineConfig = generatedYaml.value.environment.machines[machineNames[0]]
          if (firstMachineConfig?.configurations?.length > 0) {
            const firstConfig = firstMachineConfig.configurations[0]
            if (firstConfig.test_type) {
              testType = firstConfig.test_type
            }
          }
        }
      }
    } catch (error) {
      console.warn('[CustomPlan handleDownload] 提取文件名信息失败:', error)
    }
    
    // 格式化为文件名安全的字符串（移除特殊字符，替换空格）
    const safeTestType = testType.replace(/[^a-zA-Z0-9-]/g, '')
    const safeProductName = productName.replace(/[^a-zA-Z0-9-]/g, '')
    
    const filename = `test-plan_${safeProductName}_${safeTestType}_${timestamp}.yaml`
    
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
    // Message.success(`Test plan downloaded: ${filename}`)
    showNotification(`Test plan downloaded: ${filename}`, 'success')
    console.log('[CustomPlan] ✅ YAML 文件已下载:', filename)
  } catch (error) {
    console.error('[CustomPlan] Download error:', error)
    // Message.error(`Failed to download YAML file: ${error.message || 'Unknown error'}`)
    showNotification(`Failed to download: ${error.message || 'Unknown error'}`, 'error')
  }
}

// 处理保存计划 - 显示保存对话框
const handleSavePlan = async () => {
  console.log('[CustomPlan handleSavePlan] 打开保存对话框')
  
  // 验证是否有生成的 YAML 数据
  if (!generatedYaml.value) {
    Message.warning('请先生成测试计划') 
    return
  }

  const response = await checkCompatibility(generatedYaml.value)
  console.log('[CustomPlan handleSave] 📊 兼容性验证结果:', response)
  
  if (!response.success) {
    // 验证失败，显示详细错误信息
    const errorCode = response.error?.code || 'E999'
    const errorMsg = response.error?.message || 'Unknown compatibility error'
    const lineNumber = response.error?.lineNumber
    
    console.error('[CustomPlan handleSave] ❌ 兼容性验证失败:', `[${errorCode}] ${errorMsg}`)
    console.error('[CustomPlan handleSave] ❌❌❌ 阻止保存操作！')
    
    // 更新错误行号（用于高亮显示）
    console.log('[CustomPlan handleSave] 收到的 lineNumber:', lineNumber)
    if (lineNumber) {
      errorLineNumbers.value = [lineNumber]
      console.log('[CustomPlan handleSave] ✅ 设置错误行号:', lineNumber)
      console.log('[CustomPlan handleSave] errorLineNumbers.value:', errorLineNumbers.value)
    } else {
      console.log('[CustomPlan handleSave] ⚠️ lineNumber 为空，未设置错误行号')
    }
    
    // 显示友好的错误消息
    const errorMsgWithLine = lineNumber ? `${errorMsg} (Line ${lineNumber})` : errorMsg
    // Message.error(`Compatibility Check Failed: ${errorMsgWithLine}`)
    showNotification(`Compatibility Check Failed: ${errorMsgWithLine}`, 'error')
    return  // 🚫 重要：这里必须返回，阻止后续下载操作
  }
  
  // ✅ 验证通过，清除错误行号并开始下载
  errorLineNumbers.value = []
  console.log('[CustomPlan] ✅ 兼容性验证通过，开始下载...')

  // 显示保存对话框
  saveDialogVisible.value = true
}

// 确认保存
const handleSaveConfirm = async () => {
  const isUpdate = !!editingPlanId.value
  console.log(isUpdate ? 'start to update' : 'start to save')
  
  // 验证必填字段
  if (!saveForm.name) {
    Message.warning('please input plan name')
    return
  }
  
  isSaving.value = true
  
  try {
    // 统计 execution_case_list 中的测试用例总数
    let testCaseCount = 0
    if (generatedYaml.value?.environment?.machines) {
      Object.values(generatedYaml.value.environment.machines).forEach((machine: any) => {
        if (machine.configurations) {
          machine.configurations.forEach((config: any) => {
            if (config.execution_case_list) {
              testCaseCount += config.execution_case_list.length
            }
          })
        }
      })
    }
    
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
      testCaseCount: testCaseCount,
      status: saveForm.status,
    }
    
    console.log(`[CustomPlan handleSaveConfirm] ${isUpdate ? '更新' : '保存'}数据:`, saveData)
    
    // 调用 API 保存或更新
    const res = isUpdate 
      ? await updateSavedPlan(saveData, editingPlanId.value!)
      : await addSavedPlan(saveData)
    
    if (res.code === 200) {
      // Message.success(isUpdate ? 'Updated successfully' : 'Saved successfully')
      showNotification(isUpdate ? 'Test plan updated successfully!' : 'Test plan saved successfully!', 'success')
      saveDialogVisible.value = false
      
      if (!isUpdate) {
        // 只有新建时才重置表单
        saveForm.name = ''
        saveForm.description = ''
        saveForm.tags = ''
        saveForm.status = 1
        saveForm.category = 'Benchmark'
      }
      
      // 清除编辑模式
      if (isUpdate) {
        tpgenStore.clearEditMode()
        editingPlanId.value = null
      }
      
      console.log(`[CustomPlan handleSaveConfirm] ✅ ${isUpdate ? '更新' : '保存'}成功`)
    } else {
      showNotification(res.data || `Failed to ${isUpdate ? 'update' : 'save'} test plan`, 'error')
      console.error(`[CustomPlan handleSaveConfirm] ❌ ${isUpdate ? '更新' : '保存'}失败:`, res.data)
    }
  } catch (error: any) {
    showNotification(`Failed to ${isUpdate ? 'update' : 'save'}: ` + (error.message || 'Unknown error'), 'error')
  } finally {
    isSaving.value = false
  }
}

// 取消保存
const handleSaveCancel = () => {
  console.log('[CustomPlan handleSaveCancel] 取消保存')
  saveDialogVisible.value = false
  
  // 重置表单（可选）
  // saveForm.name = ''
  // saveForm.description = ''
  // saveForm.tags = ''
}

// 处理更新计划
const handleUpdatePlan = async () => {
  console.log('[CustomPlan handleUpdatePlan] 开始更新计划')
  
  // 验证是否有生成的 YAML 数据
  if (!generatedYaml.value) {
    Message.warning('Please generate test plan first')
    return
  }
  
  if (!editingPlanId.value) {
    Message.error('No plan ID found for updating')
    return
  }
  
  // 验证兼容性
  const response = await checkCompatibility(generatedYaml.value)
  console.log('[CustomPlan handleUpdatePlan] 兼容性验证结果:', response)
  
  if (!response.success) {
    const errorCode = response.error?.code || 'E999'
    const errorMsg = response.error?.message || 'Unknown compatibility error'
    const lineNumber = response.error?.lineNumber
    
    console.error('[CustomPlan handleUpdatePlan] ❌ 兼容性验证失败:', `[${errorCode}] ${errorMsg}`)
    
    if (lineNumber) {
      errorLineNumbers.value = [lineNumber]
    }
    
    const errorMsgWithLine = lineNumber ? `${errorMsg} (Line ${lineNumber})` : errorMsg
    showNotification(`Compatibility Check Failed: ${errorMsgWithLine}`, 'error')
    return
  }
  
  errorLineNumbers.value = []
  
  // 显示更新对话框
  saveDialogVisible.value = true
}

// 加载编辑数据
const loadEditData = async () => {
  if (!tpgenStore.editMode || !tpgenStore.editingPlan) {
    console.log('[CustomPlan loadEditData] 不是编辑模式')
    return
  }
  
  const plan = tpgenStore.editingPlan
  console.log('[CustomPlan loadEditData] 加载编辑数据:', plan)
  
  // 保存编辑计划的 ID
  editingPlanId.value = plan.id
  
  // 填充保存表单
  saveForm.name = plan.name
  saveForm.category = plan.category || 'Benchmark'
  saveForm.description = plan.description || ''
  saveForm.tags = plan.tags || ''
  saveForm.status = plan.status || 1
  
  // 如果有 configData，填充表单数据
  if (plan.configData) {
    try {
      const config = typeof plan.configData === 'string' 
        ? JSON.parse(plan.configData) 
        : plan.configData
      
      console.log('[CustomPlan loadEditData] 解析的配置数据:', config)
      
      // 先填充 productName 和 asicName，它们会触发 HardwareConfig 的 watch 加载机器列表
      if (config.productName) formData.productName = config.productName
      if (config.asicName) formData.asicName = config.asicName
      
      // 使用 nextTick 确保 HardwareConfig 的 watch 先执行
      await nextTick()
      
      // 然后填充其他字段
      if (config.cpu) formData.cpu = config.cpu
      if (config.gpu) formData.gpu = config.gpu
      
      // 先设置机器配置，再设置已选机器列表
      // 这样可以避免 MachineTestConfig 的 watch 创建默认空配置
      if (config.machineConfigurations) {
        console.log('[CustomPlan loadEditData] 原始机器配置:', config.machineConfigurations)
        formData.machineConfigurations = JSON.parse(JSON.stringify(config.machineConfigurations))
        console.log('[CustomPlan loadEditData] 设置后的 formData.machineConfigurations:', formData.machineConfigurations)
        
        // 打印每个机器的配置详情
        Object.keys(config.machineConfigurations).forEach(machineId => {
          const configs = config.machineConfigurations[Number(machineId)]
          console.log(`[CustomPlan loadEditData] 机器 ${machineId} 的配置:`, configs)
          if (configs && configs.length > 0) {
            configs.forEach((cfg, idx) => {
              console.log(`[CustomPlan loadEditData]   配置 ${idx + 1}:`, {
                osId: cfg.osId,
                osFamily: cfg.osFamily,
                osVersion: cfg.osVersion,
                kernelVersion: cfg.kernelVersion,
                testTypeId: cfg.testTypeId,
                testTypeName: cfg.testTypeName,
                testCaseCount: cfg.orderedTestCases?.length || 0
              })
            })
          }
        })
      }
      
      // 再等一个 tick 确保配置已设置
      await nextTick()
      
      if (config.selectedMachines) {
        formData.selectedMachines = [...config.selectedMachines]
        console.log('[CustomPlan loadEditData] 设置已选机器:', config.selectedMachines)
      }
      
      // 更新进度
      // updateProgress()
      
      // 再等一次，确保所有数据都更新完毕
      await nextTick()
      
      Message.success('Plan data loaded successfully')
      console.log('[CustomPlan loadEditData] ✅ 数据加载完成')
    } catch (error) {
      console.error('[CustomPlan loadEditData] 解析配置数据失败:', error)
      Message.warning('Failed to load some configuration data')
    }
  }
  
  // 如果有 yamlData，直接显示预览
  if (plan.yamlData) {
    try {
      const yaml = typeof plan.yamlData === 'string' 
        ? JSON.parse(plan.yamlData) 
        : plan.yamlData
      generatedYaml.value = yaml
      console.log('[CustomPlan loadEditData] 加载 YAML 数据成功')
    } catch (error) {
      console.error('[CustomPlan loadEditData] 解析 YAML 数据失败:', error)
    }
  }
}



// 监听表单变化
// watch(() => formData, updateProgress, { deep: true })
// watch(formData, updateProgress, { deep: true })

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
  // updateProgress()
  loadOsConfigMap()
  loadTestTypeMap()
  
  // 如果是编辑模式，加载编辑数据
  loadEditData()
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
    justify-content: space-between;  // ← 改这里！从 center 改为 space-between
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

