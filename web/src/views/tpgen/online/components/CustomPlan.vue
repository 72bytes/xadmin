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
            <template #icon v-if="!isGenerating"><icon-settings /></template>
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
      @close="generatedYaml = null"
      @copy="handleCopy"
      @download="handleDownload"
      @save="handleSavePlan"
    />



    <!-- 保存对话框 -->
    <a-modal
      v-model:visible="saveDialogVisible"
      title="保存测试计划"
      @ok="handleSaveConfirm"
      @cancel="handleSaveCancel"
      :ok-loading="isSaving"
    >
      <a-form :model="saveForm" layout="vertical">
        <a-form-item label="计划名称" required>
          <a-input v-model="saveForm.name" placeholder="请输入计划名称" />
        </a-form-item>
        
        <a-form-item label="类别" required>
          <a-select v-model="saveForm.category" placeholder="请选择类别">
            <a-option value="Benchmark">Benchmark</a-option>
            <a-option value="Stress">Stress</a-option>
            <a-option value="Functional">Functional</a-option>
            <a-option value="Performance">Performance</a-option>
          </a-select>
        </a-form-item>
        
        <a-form-item label="描述">
          <a-textarea 
            v-model="saveForm.description" 
            placeholder="请输入描述信息"
            :rows="3"
          />
        </a-form-item>
        
        <a-form-item label="标签">
          <a-input 
            v-model="saveForm.tags" 
            placeholder="多个标签用逗号分隔"
          />
        </a-form-item>
      </a-form>
    </a-modal>





    <!-- 保存对话框 -->
    <a-modal
      v-model:visible="saveDialogVisible"
      title="保存测试计划"
      @ok="handleSaveConfirm"
      @cancel="handleSaveCancel"
      :ok-loading="isSaving"
    >
      <a-form :model="saveForm" layout="vertical">
        <a-form-item label="计划名称" required>
          <a-input v-model="saveForm.name" placeholder="请输入计划名称" />
        </a-form-item>
        
        <a-form-item label="类别" required>
          <a-select v-model="saveForm.category" placeholder="请选择类别">
            <a-option value="Benchmark">Benchmark</a-option>
            <a-option value="Stress">Stress</a-option>
            <a-option value="Functional">Functional</a-option>
            <a-option value="Performance">Performance</a-option>
          </a-select>
        </a-form-item>
        
        <a-form-item label="描述">
          <a-textarea 
            v-model="saveForm.description" 
            placeholder="请输入描述信息"
            :rows="3"
          />
        </a-form-item>
        
        <a-form-item label="标签">
          <a-input 
            v-model="saveForm.tags" 
            placeholder="多个标签用逗号分隔"
          />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>

  <!-- 保存对话框 -->
  <a-modal
      v-model:visible="saveDialogVisible"
      title="保存测试计划配置"
      :width="600"
      @ok="handleSaveConfirm"
      @cancel="handleSaveCancel"
    >
      <a-form :model="saveForm" layout="vertical" :rules="saveFormRules">
        <a-form-item label="计划名称" field="name" required>
          <a-input
            v-model="saveForm.name"
            placeholder="请输入计划名称"
            :max-length="100"
            show-word-limit
          />
        </a-form-item>
        <a-form-item label="类别" field="category" required>
          <a-select v-model="saveForm.category" placeholder="请选择类别">
            <a-option value="Benchmark">Benchmark - 基准测试</a-option>
            <a-option value="Functional">Functional - 功能测试</a-option>
            <a-option value="Performance">Performance - 性能测试</a-option>
            <a-option value="Stress">Stress - 压力测试</a-option>
            <a-option value="Custom">Custom - 自定义</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="描述" field="description">
          <a-textarea
            v-model="saveForm.description"
            placeholder="请输入描述信息"
            :rows="4"
            :max-length="500"
            show-word-limit
          />
        </a-form-item>
        <a-form-item label="标签" field="tags">
          <a-input
            v-model="saveForm.tags"
            placeholder="多个标签用逗号分隔，例如：gpu,ubuntu,benchmark"
            :max-length="200"
          />
        </a-form-item>
        <a-form-item label="状态" field="status">
          <a-radio-group v-model="saveForm.status">
            <a-radio :value="1">草稿</a-radio>
            <a-radio :value="2">已发布</a-radio>
          </a-radio-group>
        </a-form-item>
      </a-form>
    </a-modal>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import type { FormData, YamlData } from '../types'
import { addSavedPlan } from '@/apis/tpgen'
import { getTestTypes } from '@/apis/testType'
import { getOsOptions } from '@/apis/osConfig'
import HardwareConfig from './HardwareConfig.vue'
import OSConfig from './OSConfig.vue'
import KernelConfig from './KernelConfig.vue'
import MachineTestConfig from './MachineTestConfig.vue'
import YamlPreview from './YamlPreview.vue'
import { jsToYaml } from '../utils/yamlConverter'

// 导入兼容性分析函数和通知函数
import { showNotification } from '../check_yaml'  // 保留 showNotification
import { validateYaml } from '@/apis/yamlCheck'
import { useMachines } from '../composables/useMachines'

defineOptions({ name: 'CustomPlan' })

// 使用 machines composable
const { machines, getMachineById, loadMachines } = useMachines()

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
const isSaving = ref(false)
const saveForm = reactive({
  name: '',
  category: 'Benchmark',
  description: '',
  tags: '',
  status: 1,
})


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
  updateProgress()
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
        if (!config.osId || !config.kernelVersion || !config.testTypeId) {
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
    progress.value = 100
    emit('progressChange', 100)

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

/**
 * 处理复制到剪贴板
 * 包含完整的兼容性验证逻辑（来自 check_yaml.ts）
 */
const handleCopy = async () => {
  try {
    console.log('[CustomPlan handleCopy] 🚀 开始复制流程...')
    
    if (!generatedYaml.value) {
      console.error('[CustomPlan handleCopy] ❌ 没有 YAML 数据')
      // Message.error('No YAML data to copy!')
      showNotification('No YAML data to copy!', 'error')
      return
    }

    // 检查浏览器是否支持 Clipboard API
    if (!navigator.clipboard) {
      console.error('[CustomPlan handleCopy] ❌ 浏览器不支持剪贴板 API')
      // Message.error('Browser does not support clipboard operation!')
      showNotification('Browser does not support clipboard operation!', 'error')
      return
    }
    
    // 检查是否在安全上下文中（HTTPS 或 localhost）
    if (!window.isSecureContext) {
      console.error('[CustomPlan handleCopy] ❌ 需要 HTTPS 环境')
      // Message.error('HTTPS required for clipboard access!')
      showNotification('HTTPS required for clipboard access!', 'error')
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
    
    await navigator.clipboard.writeText(yamlText)
    
    emit('copy')
    Message.success('Test plan copied to clipboard!')
    showNotification('Test plan copied to clipboard!', 'success')
    console.log('[CustomPlan] ✅ 复制成功')
    
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
  console.log('[CustomPlan handleSaveConfirm] 开始保存')
  
  // 验证必填字段
  if (!saveForm.name) {
    Message.warning('请输入计划名称')
    return
  }
  if (!saveForm.category) {
    Message.warning('请选择类别')
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

    
    console.log('[CustomPlan handleSaveConfirm] 保存数据:', saveData)
    



    // 调用 API 保存
    const res = await addSavedPlan(saveData)
    
    if (res.code === 200) {
      Message.success('保存成功')
      showNotification('Test plan saved successfully!', 'success')
      saveDialogVisible.value = false
      
      // 重置保存表单
      saveForm.name = ''
      saveForm.description = ''
      saveForm.tags = ''
      saveForm.status = 1
      saveForm.category = 'Benchmark'

      
      console.log('[CustomPlan handleSaveConfirm] ✅ 保存成功')
    }
    else {

      // Message.error(res.data || '保存失败')
      showNotification(res.data || 'Failed to save test plan', 'error')
      console.error('[CustomPlan handleSaveConfirm] ❌ 保存失败:', res.data)
    }

  }

  catch (error) {

    // Message.error('保存失败，请重试')
    showNotification('Failed to save: ' + (error.message || 'Unknown error'), 'error')
  }
  finally {
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



// 监听表单变化
// watch(() => formData, updateProgress, { deep: true })
watch(formData, updateProgress, { deep: true })

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

