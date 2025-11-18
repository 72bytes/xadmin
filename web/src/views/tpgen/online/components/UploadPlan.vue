<template>
  <div class="upload-plan">
    <a-card class="form-section" :bordered="false">
      <template #title>
        <div class="section-title" style="display: none;">
          <icon-file-add />
          Upload Your Test Plan
        </div>
      </template>

      <div
        class="upload-area"
        :class="{ dragover: isDragOver }"
        @click="handleClickUpload"
        @dragover.prevent="isDragOver = true"
        @dragleave.prevent="isDragOver = false"
        @drop.prevent="handleDrop"
      >
        <icon-cloud-upload :size="48" />
        <h3>Upload YAML Test Plan</h3>
        <p>Drag & drop your YAML file here or click to browse</p>
        <input
          ref="fileInputRef"
          type="file"
          accept=".yaml,.yml"
          style="display: none"
          @change="handleFileChange"
        >
      </div>

      <div v-if="uploadedFile" class="file-info">
        <div class="success-message">
          <div class="success-header">
            <icon-check-circle />
            <strong>{{ uploadedFile.name }} Uploaded Successfully!</strong>
          </div>
          <div class="success-details">
            Size: {{ formatFileSize(uploadedFile.size) }}
          </div>
        </div>
      </div>

      <div v-if="validationResults.length > 0" class="validation-results">
        <h3>Test Plan Analysis Result</h3>
        
        <!-- Error Summary (Collapsible) -->
        <div v-if="errorSummary.length > 0" class="error-summary">
          <a-collapse
            :default-active-key="[]"
            expand-icon-position="right"
            :bordered="false"
          >
            <a-collapse-item key="errors" class="error-collapse-item">
              <template #header>
                <div class="error-header">
                  <icon-close-circle />
                  <strong>YAML Syntax Error: YAML validation failed ({{ errorSummary.length }} errors detected)</strong>
                </div>
              </template>
              <ul class="error-list">
                <li v-for="(error, index) in errorSummary" :key="index">
                  Line {{ error.line }} [ERROR] --- {{ error.message }}
                </li>
              </ul>
            </a-collapse-item>
          </a-collapse>
        </div>

        <!-- File Content with Error Highlighting -->
        <!-- 只在有语法错误时显示文件内容和错误高亮 -->
        <div v-if="errorSummary.length > 0 && fileContent.length > 0" class="file-content-section">
          <a-collapse
            :default-active-key="['file-content']"
            expand-icon-position="right"
            :bordered="false"
          >
            <a-collapse-item key="file-content" class="file-content-collapse-item">
              <template #header>
                <div class="file-content-header-wrapper">
                  <div class="file-content-title">
                    <icon-file />
                    <strong>File Content (errors highlighted in red):</strong>
                  </div>
                  <a-button
                    type="text"
                    size="small"
                    class="copy-button"
                    @click.stop="handleCopyFileContent"
                  >
                    <template #icon><icon-copy /></template>
                    Copy
                  </a-button>
                </div>
              </template>
              <div class="file-content-box">
                <div
                  v-for="(line, index) in fileContent"
                  :key="index"
                  class="code-line"
                  :class="{ 
                    'error-line': errorLines.includes(index + 1),
                    'comment-line': line.trim().startsWith('#')
                  }"
                >
                  <span class="line-number">{{ index + 1 }}</span>
                  <pre class="line-content">{{ line || ' ' }}<span v-if="getErrorMessage(index + 1)" class="error-comment">{{ getErrorMessage(index + 1) }}</span></pre>
                </div>
              </div>
            </a-collapse-item>
          </a-collapse>
        </div>
        
        <div
          v-for="(result, index) in validationResults"
          v-show="result.title || result.message"
          :key="index"
          class="validation-item"
          :class="result.type"
        >
          <component :is="getResultIcon(result.type)" />
          <div>
            <strong>{{ result.title }}</strong>
            <p v-if="result.message">{{ result.message }}</p>
            <ul v-if="result.items && result.items.length > 0">
              <li v-for="(item, idx) in result.items" :key="idx">{{ item }}</li>
            </ul>
          </div>
        </div>
      </div>

      <div class="actions">
        <a-button
          type="primary"
          :disabled="!uploadedFile"
          :loading="analyzing"
          @click="handleAnalyze"
        >
          <template #icon><icon-search /></template>
          Analyze Test Plan
        </a-button>
        <a-button
          v-if="errorSummary.length > 0"
          type="outline"
          @click="handleDownloadYaml"
        >
          <template #icon><icon-download /></template>
          Download YAML
        </a-button>
      </div>
    </a-card>

    <!-- 双列对比视图（仅在无语法错误且标准模板已加载时显示） -->
    <a-card 
      v-if="standardLoaded && errorSummary.length === 0 && analysisResult" 
      class="form-section comparison-view" 
      :bordered="false"
    >
      <template #title>
        <div class="section-title">
          <icon-swap />
          Configuration Comparison
        </div>
      </template>

      <div class="comparison-container">
        <!-- 左侧：标准模板 -->
        <div class="comparison-column">
          <h4 class="column-title">
            <icon-file />
            Standard Template
          </h4>
          <div class="code-view-box">
            <div
              v-for="(line, index) in standardTemplate"
              :key="`std-${index}`"
              class="comparison-code-line"
            >
              <span class="comparison-line-number">{{ index + 1 }}</span>
              <pre class="comparison-line-content">{{ line || ' ' }}</pre>
            </div>
          </div>
        </div>

        <!-- 右侧：用户上传的文件 -->
        <div class="comparison-column">
          <h4 class="column-title">
            <icon-file />
            Uploaded File ({{ uploadedFile?.name }})
          </h4>
          <div class="code-view-box">
            <div
              v-for="(line, index) in fileContent"
              :key="`upload-${index}`"
              class="comparison-code-line"
            >
              <span class="comparison-line-number">{{ index + 1 }}</span>
              <pre class="comparison-line-content">{{ line || ' ' }}</pre>
            </div>
          </div>
        </div>
      </div>
    </a-card>

    <!-- 分析结果详情 -->
    <a-card v-if="analysisResult" class="form-section analysis-output" :bordered="false">
      <template #title>
        <div class="section-title">
          <icon-bar-chart />
          Analysis Results
        </div>
      </template>

      <!-- 兼容的机器 -->
      <div v-if="analysisResult.compatibleMachines.length > 0" class="analysis-section">
        <div class="machine-section-wrapper">
          <a-collapse
            :default-active-key="['compatible']"
            expand-icon-position="right"
            :bordered="false"
          >
            <a-collapse-item key="compatible" class="compatible-collapse-item">
              <template #header>
                <div class="section-header">
                  <icon-check-circle />
                  <strong>Compatible Machines ({{ analysisResult.compatibleMachines.length }})</strong>
                </div>
              </template>
              <div class="section-description">
                The following machines match your test plan requirements:
              </div>
              <div class="machine-grid">
                <div
                  v-for="machine in analysisResult.compatibleMachines"
                  :key="machine.id"
                  class="machine-card compatible"
                >
                  <h4>{{ machine.name }}</h4>
                  <p><strong>Product Name:</strong> {{ machine.productName }}</p>
                  <p><strong>ASIC Name:</strong> {{ machine.asicName }}</p>
                  <p><strong>GPU Model:</strong> {{ machine.gpuModel }}</p>
                  <p><strong>IP Address:</strong> {{ machine.ipAddress }}</p>
                  <a-tag color="green">Compatible</a-tag>
                </div>
              </div>
            </a-collapse-item>
          </a-collapse>
        </div>
      </div>

      <!-- 不兼容的机器 -->
      <div v-if="analysisResult.incompatibleMachines.length > 0" class="analysis-section">
        <div class="machine-section-wrapper">
          <a-collapse
            :default-active-key="['incompatible']"
            expand-icon-position="right"
            :bordered="false"
          >
            <a-collapse-item key="incompatible" class="incompatible-collapse-item">
              <template #header>
                <div class="section-header">
                  <icon-exclamation-circle />
                  <strong>Incompatible Machines ({{ analysisResult.incompatibleMachines.length }})</strong>
                </div>
              </template>
              <div class="section-description">
                The following machines do not match your test plan requirements:
              </div>
              <div class="machine-grid">
                <div
                  v-for="item in analysisResult.incompatibleMachines"
                  :key="item.machine.id"
                  class="machine-card incompatible"
                >
                  <h4>{{ item.machine.name }}</h4>
                  <p><strong>Product Name:</strong> {{ item.machine.productName }}</p>
                  <p><strong>ASIC Name:</strong> {{ item.machine.asicName }}</p>
                  <p><strong>GPU Model:</strong> {{ item.machine.gpuModel }}</p>
                  <p><strong>IP Address:</strong> {{ item.machine.ipAddress }}</p>
                  <a-tag color="red">Incompatible</a-tag>
                  <ul class="reasons">
                    <li v-for="(reason, idx) in item.reasons" :key="idx">{{ reason }}</li>
                  </ul>
                </div>
              </div>
            </a-collapse-item>
          </a-collapse>
        </div>
      </div>

      <!-- 缺失配置 -->
      <div v-if="analysisResult.missingConfigurations.length > 0" class="analysis-section">
        <a-alert type="error">
          <template #icon><icon-close-circle /></template>
          <div>
            <strong>Missing Configurations</strong>
            <ul>
              <li v-for="(config, idx) in analysisResult.missingConfigurations" :key="idx">
                {{ config }}
              </li>
            </ul>
          </div>
        </a-alert>
      </div>

      <!-- 警告 -->
      <div v-if="analysisResult.warnings.length > 0" class="analysis-section">
        <a-alert type="warning">
          <template #icon><icon-exclamation-circle /></template>
          <div>
            <strong>Configuration Warnings</strong>
            <ul>
              <li v-for="(warning, idx) in analysisResult.warnings" :key="idx">
                {{ warning }}
              </li>
            </ul>
          </div>
        </a-alert>
      </div>
    </a-card>
  </div>
</template>

<script setup lang="ts">
import type { AnalysisResult, Machine } from '../types'
import { Message } from '@arco-design/web-vue'

defineOptions({ name: 'UploadPlan' })

// Mock 机器数据 (实际项目中应该从 API 获取)
const mockMachines: Machine[] = [
  { id: 1, name: 'Machine A', productName: 'navi31', asicName: 'Navi31 GFX1200', ipAddress: '192.168.1.100', gpuModel: 'RX 7900 XT', status: 'Available' },
  { id: 2, name: 'Machine B', productName: 'navi32', asicName: 'Navi31 GFX1100', ipAddress: '192.168.1.101', gpuModel: 'RX 7900 XT', status: 'Available' },
  { id: 3, name: 'Machine C', productName: 'navi31', asicName: 'Navi31 GFX1100', ipAddress: '192.168.1.102', gpuModel: 'RX 7900 XT', status: 'Available' },
  { id: 4, name: 'Machine D', productName: 'navi33', asicName: 'Navi31 GFX1500', ipAddress: '192.168.1.103', gpuModel: 'RX 7900 XT', status: 'Available' },
  { id: 5, name: 'Machine E', productName: 'navi31', asicName: 'Navi31 GFX1300', ipAddress: '192.168.1.104', gpuModel: 'RX 7900 XT', status: 'Available' },
]

const fileInputRef = ref<HTMLInputElement>()
const isDragOver = ref(false)
const uploadedFile = ref<File | null>(null)
const uploadedFileBlob = ref<Blob | null>(null) // 存储文件的 Blob 副本
const uploadedFileName = ref<string>('') // 存储文件名
const uploadedFileSize = ref<number>(0) // 存储文件大小
const analyzing = ref(false)
const validationResults = ref<Array<{ type: string; title: string; message?: string; items?: string[] }>>([])
const analysisResult = ref<AnalysisResult | null>(null)
const errorSummary = ref<Array<{ line: number; column: number; message: string }>>([])
const fileContent = ref<string[]>([])
const errorLines = ref<number[]>([])
const standardTemplate = ref<string[]>([]) // 标准模板内容（按行分割）
const standardLoaded = ref(false) // 标准模板是否已加载

const handleClickUpload = () => {
  fileInputRef.value?.click()
}

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    handleFile(target.files[0])
    // 清空 input value，允许重复上传同一文件名
    target.value = ''
  }
}

const handleDrop = (event: DragEvent) => {
  isDragOver.value = false
  if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
    handleFile(event.dataTransfer.files[0])
    // 清空文件输入框的 value
    if (fileInputRef.value) {
      fileInputRef.value.value = ''
    }
  }
}

const handleFile = (file: File) => {
  if (!file.name.endsWith('.yaml') && !file.name.endsWith('.yml')) {
    Message.error('Please upload a YAML file')
    return
  }

  // 清理所有之前的状态
  uploadedFile.value = file
  uploadedFileBlob.value = file.slice(0, file.size) // 创建 Blob 副本
  uploadedFileName.value = file.name // 存储文件名
  uploadedFileSize.value = file.size // 存储文件大小
  validationResults.value = []
  analysisResult.value = null
  errorSummary.value = []
  fileContent.value = []
  errorLines.value = []
  standardLoaded.value = false // 清空标准模板加载状态，下次需要重新加载
  Message.success('File uploaded successfully')
}

const formatFileSize = (bytes: number): string => {
  if (bytes === 0)
    return '0 Bytes'
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  return `${Number.parseFloat((bytes / k ** i).toFixed(2))} ${sizes[i]}`
}

const handleAnalyze = async () => {
  if (!uploadedFileBlob.value || !uploadedFileName.value)
    return

  analyzing.value = true
  try {
    // 第一步：调用后端 API 进行严格的 YAML 语法验证
    const formData = new FormData()
    // 使用 Blob 副本和文件名创建新的 File 对象
    const fileToUpload = new File([uploadedFileBlob.value], uploadedFileName.value, {
      type: 'application/x-yaml',
    })
    formData.append('file', fileToUpload)

    const token = localStorage.getItem('token') || sessionStorage.getItem('token')
    const response = await fetch('/api/system/test/plan/yaml/upload', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
      body: formData,
    })

    const backendResult = await response.json()

    // 如果后端验证失败，显示详细错误信息
    if (!response.ok || backendResult.code !== 200) {
      const errorDetails = backendResult.data?.errors || []
      const lines = backendResult.data?.lines || []
      
      // 设置文件内容
      fileContent.value = lines
      
      // 设置错误摘要和错误行
      errorSummary.value = errorDetails
      errorLines.value = errorDetails
        .map((err: any) => err.line)
        .filter((line: number) => line > 0)

      // 只设置一个标记，让错误摘要区域显示
      validationResults.value = [
        {
          type: 'error',
          title: '', // 空标题，因为错误已在上面的 error-summary 中显示
          message: '',
        },
      ]

      return
    }

    // 第二步：后端验证通过，继续前端分析
    // 设置文件内容（用于双列对比显示）
    fileContent.value = backendResult.data?.lines || []
    
    // 使用后端返回的解析数据（而不是前端简单解析器）
    const yamlData = backendResult.data?.parsed_data || {}

    // 验证和分析
    const result = validateYamlConfig(yamlData)
    analysisResult.value = result

    validationResults.value = [
      {
        type: 'success',
        title: 'YAML File Parsed Successfully',
        message: '',
      },
    ]

    // 加载标准模板用于对比
    await loadStandardTemplate()

    // 滚动到分析结果
    setTimeout(() => {
      document.querySelector('.analysis-output')?.scrollIntoView({ behavior: 'smooth' })
    }, 100)
  }
  catch (error: any) {
    validationResults.value = [
      {
        type: 'error',
        title: 'Error parsing YAML file',
        message: error.message,
      },
    ]
  }
  finally {
    analyzing.value = false
  }
}

// 加载标准模板
async function loadStandardTemplate() {
  if (standardLoaded.value) {
    return // 已经加载过，直接返回
  }

  try {
    const token = localStorage.getItem('token') || sessionStorage.getItem('token')
    const response = await fetch('/api/system/test/plan/yaml/standard-template', {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    })

    const result = await response.json()

    if (response.ok && result.code === 200) {
      standardTemplate.value = result.data.lines || []
      standardLoaded.value = true
    } else {
      console.error('Failed to load standard template:', result.message)
    }
  } catch (error) {
    console.error('Error loading standard template:', error)
  }
}

// 简单的 YAML 解析器
function parseYaml(yamlContent: string): any {
  const lines = yamlContent.split('\n')
  const result: any = {}
  let currentSection: string | null = null

  for (const line of lines) {
    const trimmed = line.trim()

    if (!trimmed || trimmed.startsWith('#'))
      continue

    if (trimmed.endsWith(':')) {
      currentSection = trimmed.slice(0, -1).trim()
      result[currentSection] = {}
    }
    else if (trimmed.includes(':')) {
      const [key, value] = trimmed.split(':').map(s => s.trim())
      if (currentSection) {
        result[currentSection][key] = value
      }
      else {
        result[key] = value
      }
    }
  }

  return result
}

// 验证 YAML 配置（基于标准模板规则）
function validateYamlConfig(yamlData: any): AnalysisResult {
  const result: AnalysisResult = {
    compatibleMachines: [],
    incompatibleMachines: [],
    missingConfigurations: [],
    warnings: [],
  }

  // ============ 必需配置检查 (must) ============
  
  // 1. 检查 hardware 字段
  if (!yamlData.hardware) {
    result.missingConfigurations.push('hardware field is required but missing')
    return result
  }

  // 2. 检查 hardware.machines
  const machines = yamlData.hardware.machines
  if (!machines || !Array.isArray(machines) || machines.length === 0) {
    result.missingConfigurations.push('hardware.machines is required and must contain at least one machine')
    return result
  }

  // 3. 检查每个机器的必需字段
  machines.forEach((machine: any, index: number) => {
    const machinePrefix = `hardware.machines[${index}]`
    
    if (!machine.hostname) {
      result.missingConfigurations.push(`${machinePrefix}.hostname is required but missing`)
    }
    if (!machine.productName) {
      result.missingConfigurations.push(`${machinePrefix}.productName is required but missing`)
    }
    if (!machine.gpuModel) {
      result.missingConfigurations.push(`${machinePrefix}.gpuModel is required but missing`)
    }
  })

  // 4. 检查 environment 字段
  if (!yamlData.environment) {
    result.missingConfigurations.push('environment field is required but missing')
    return result
  }

  // 5. 检查 environment.machines
  if (!yamlData.environment.machines || typeof yamlData.environment.machines !== 'object') {
    result.missingConfigurations.push('environment.machines is required but missing')
    return result
  }

  // 6. 检查每个 hostname 是否在 environment.machines 中定义
  const envMachines = yamlData.environment.machines
  machines.forEach((machine: any, index: number) => {
    if (!machine.hostname) return // 已经在上面报错了

    const hostname = machine.hostname
    if (!envMachines[hostname]) {
      result.missingConfigurations.push(`environment.machines["${hostname}"] is required but missing (referenced in hardware.machines[${index}])`)
      return
    }

    // 7. 检查 configurations 数组
    const configurations = envMachines[hostname].configurations
    if (!configurations || !Array.isArray(configurations) || configurations.length === 0) {
      result.missingConfigurations.push(`environment.machines["${hostname}"].configurations is required and must contain at least one configuration`)
      return
    }

    // 8. 检查每个 configuration 的必需字段
    configurations.forEach((config: any, configIndex: number) => {
      const configPrefix = `environment.machines["${hostname}"].configurations[${configIndex}]`

      // 检查 os 字段
      if (!config.os || typeof config.os !== 'object') {
        result.missingConfigurations.push(`${configPrefix}.os is required but missing`)
      } else {
        if (!config.os.id && config.os.id !== 0) {
          result.missingConfigurations.push(`${configPrefix}.os.id is required but missing`)
        }
        if (!config.os.family) {
          result.missingConfigurations.push(`${configPrefix}.os.family is required but missing`)
        }
        if (!config.os.version) {
          result.missingConfigurations.push(`${configPrefix}.os.version is required but missing`)
        }
      }

      // 检查 kernel 字段
      if (!config.kernel || typeof config.kernel !== 'object') {
        result.missingConfigurations.push(`${configPrefix}.kernel is required but missing`)
      } else if (!config.kernel.kernel_version) {
        result.missingConfigurations.push(`${configPrefix}.kernel.kernel_version is required but missing`)
      }

      // 检查 execution_case_list（至少要有一个测试用例）
      if (!config.execution_case_list || !Array.isArray(config.execution_case_list) || config.execution_case_list.length === 0) {
        result.missingConfigurations.push(`${configPrefix}.execution_case_list is required and must contain at least one test case`)
      }
    })
  })

  // ============ 可选配置检查 (option) - 仅警告 ============
  
  // 检查 metadata
  if (!yamlData.metadata) {
    result.warnings.push('metadata field is recommended but not provided')
  } else {
    if (!yamlData.metadata.version) {
      result.warnings.push('metadata.version is recommended but not provided')
    }
    if (!yamlData.metadata.generated) {
      result.warnings.push('metadata.generated is recommended but not provided')
    }
    if (!yamlData.metadata.description) {
      result.warnings.push('metadata.description is recommended but not provided')
    }
  }

  // 检查每个机器的可选字段
  machines.forEach((machine: any, index: number) => {
    if (!machine.hostname) return // 没有 hostname 就跳过
    
    const machinePrefix = `hardware.machines[${index}] (${machine.hostname})`
    
    if (!machine.id && machine.id !== 0) {
      result.warnings.push(`${machinePrefix}.id is recommended but not provided`)
    }
    if (!machine.asicName) {
      result.warnings.push(`${machinePrefix}.asicName is recommended but not provided`)
    }
    if (!machine.ipAddress) {
      result.warnings.push(`${machinePrefix}.ipAddress is recommended but not provided`)
    }
  })

  // 检查每个 configuration 的可选字段
  machines.forEach((machine: any) => {
    if (!machine.hostname) return
    const hostname = machine.hostname
    const configurations = envMachines[hostname]?.configurations
    if (!configurations) return

    configurations.forEach((config: any, configIndex: number) => {
      const configPrefix = `environment.machines["${hostname}"].configurations[${configIndex}]`

      if (!config.config_id && config.config_id !== 0) {
        result.warnings.push(`${configPrefix}.config_id is recommended but not provided`)
      }
      if (!config.deployment_method) {
        result.warnings.push(`${configPrefix}.deployment_method is recommended but not provided`)
      }
      if (!config.test_type) {
        result.warnings.push(`${configPrefix}.test_type is recommended but not provided`)
      }
    })
  })

  // ============ 机器兼容性检查（与 mockMachines 对比）============
  
  // 只有在没有严重缺失配置时才检查兼容性
  if (result.missingConfigurations.length === 0) {
    mockMachines.forEach((mockMachine) => {
      const match = machines.find((um: any) => 
        um.productName === mockMachine.productName && um.gpuModel === mockMachine.gpuModel
      )

      if (match) {
        result.compatibleMachines.push(mockMachine)
      } else {
        result.incompatibleMachines.push({
          machine: mockMachine,
          reasons: ['No matching productName/gpuModel found in uploaded configuration'],
        })
      }
    })
  }

  return result
}

const getResultIcon = (type: string) => {
  const icons: Record<string, any> = {
    success: 'icon-check-circle',
    warning: 'icon-exclamation-circle',
    error: 'icon-close-circle',
  }
  return icons[type] || 'icon-info-circle'
}

const getErrorMessage = (lineNum: number): string => {
  // 查找该行的错误信息
  const error = errorSummary.value.find(err => err.line === lineNum)
  if (error) {
    return `    # ${error.message}`
  }
  return ''
}

const handleDownloadYaml = () => {
  if (!uploadedFileName.value || fileContent.value.length === 0)
    return

  // 从 fileContent 重新组合完整内容，并添加错误注释
  const contentWithComments = fileContent.value.map((line, index) => {
    const lineNumber = index + 1
    const errorMessage = getErrorMessage(lineNumber)
    // 如果该行有错误注释，将注释添加到行尾
    return errorMessage ? `${line}${errorMessage}` : line
  }).join('\n')
  
  // 创建 Blob 并下载
  const blob = new Blob([contentWithComments], { type: 'text/yaml;charset=utf-8' })
  const url = URL.createObjectURL(blob)
  const link = document.createElement('a')
  link.href = url
  link.download = uploadedFileName.value
  document.body.appendChild(link)
  link.click()
  document.body.removeChild(link)
  URL.revokeObjectURL(url)
  
  Message.success(`Downloaded: ${uploadedFileName.value}`)
}

const handleCopyFileContent = async () => {
  if (fileContent.value.length === 0) {
    Message.warning('No content to copy')
    return
  }

  try {
    // 组合文件内容，包含错误注释
    const contentWithComments = fileContent.value.map((line, index) => {
      const lineNumber = index + 1
      const errorMessage = getErrorMessage(lineNumber)
      // 如果该行有错误注释，将注释添加到行尾
      return errorMessage ? `${line}${errorMessage}` : line
    }).join('\n')

    // 使用 Clipboard API 复制到剪贴板
    await navigator.clipboard.writeText(contentWithComments)
    Message.success('Copy File Content Success.')
  }
  catch (error) {
    // 如果 Clipboard API 失败，使用传统方法
    try {
      const textarea = document.createElement('textarea')
      const contentWithComments = fileContent.value.map((line, index) => {
        const lineNumber = index + 1
        const errorMessage = getErrorMessage(lineNumber)
        return errorMessage ? `${line}${errorMessage}` : line
      }).join('\n')
      
      textarea.value = contentWithComments
      textarea.style.position = 'fixed'
      textarea.style.opacity = '0'
      document.body.appendChild(textarea)
      textarea.select()
      document.execCommand('copy')
      document.body.removeChild(textarea)
      Message.success('Copy File Content Success.')
    }
    catch (fallbackError) {
      Message.error('Failed to copy file content')
      console.error('Copy failed:', fallbackError)
    }
  }
}
</script>

<style scoped lang="scss">
.upload-plan {
  .form-section {
    background: white;
    border-radius: 12px;
    margin-bottom: 15px;
    box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
    border-left: 5px solid #3498db;

    .section-title {
      display: flex;
      align-items: center;
      gap: 10px;
      font-size: 1.5rem;
      font-weight: 600;
      color: #2c3e50;

      .arco-icon {
        color: #3498db;
        background: #f8f9fa;
        padding: 8px;
        border-radius: 8px;
      }
    }
  }

  .upload-area {
    border: 3px dashed #e1e5eb;
    border-radius: 12px;
    padding: 60px 30px;
    text-align: center;
    transition: all 0.3s ease;
    background: #f8f9fa;
    cursor: pointer;
    margin-bottom: 20px;

    &:hover,
    &.dragover {
      border-color: #3498db;
      background: rgba(52, 152, 219, 0.05);
    }

    .arco-icon {
      font-size: 3rem;
      color: #3498db;
      margin-bottom: 15px;
    }

    h3 {
      margin: 0 0 10px 0;
      color: #2c3e50;
    }

    p {
      margin: 0;
      color: #6c757d;
    }
  }

  .file-info {
    margin-bottom: 15px;

    .success-message {
      background: rgba(39, 174, 96, 0.1);
      border-left: 4px solid #27ae60;
      border-radius: 8px;
      padding: 15px 20px;
      display: flex;
      flex-direction: column;
      gap: 8px;

      .success-header {
        display: flex;
        align-items: center;
        gap: 12px;
        color: #27ae60;

        .arco-icon {
          font-size: 1.5rem;
          flex-shrink: 0;
          width: 24px;
          height: 24px;
        }

        strong {
          color: #2c3e50;
          font-size: 1rem;
        }
      }

      .success-details {
        margin: 0;
        margin-left: 36px; // 图标宽度 24px + gap 12px = 36px，精确对齐
        font-size: 1rem;
        line-height: 1.6;
        color: #2c3e50;
        font-weight: 600;
      }
    }
  }

  .validation-results {
    margin-top: 15px;

    h3 {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 15px;
      color: #2c3e50;
    }

    .error-summary {
      margin-bottom: 20px;

      :deep(.arco-collapse) {
        background: transparent;
        border: none;
      }

      :deep(.error-collapse-item) {
        background: rgba(231, 76, 60, 0.1);
        border-left: 4px solid #e74c3c;
        border-radius: 8px;
        margin-bottom: 0;

        .arco-collapse-item-header {
          padding: 15px 20px;
          background: transparent;
          border: none;

          .error-header {
            display: flex;
            align-items: center;
            gap: 12px;
            color: #e74c3c;

            .arco-icon {
              font-size: 1.5rem;
            }

            strong {
              color: #2c3e50;
            }
          }
        }

        .arco-collapse-item-content {
          padding: 0 20px 15px 20px;
          border: none;
        }
      }

      .error-list {
        margin: 0;
        padding: 0 0 0 20px;
        list-style: none;

        li {
          margin: 8px 0;
          padding-left: 0;
          font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
          font-size: 0.95rem;
          line-height: 1.6;
          color: #555;
        }
      }
    }

    .file-content-section {
      margin: 20px 0;
      border: 2px solid #e1e5eb;
      border-radius: 8px;
      overflow: hidden;
      background: #2d2d2d;

      :deep(.arco-collapse) {
        background: transparent;
        border: none;
      }

      :deep(.file-content-collapse-item) {
        background: transparent;
        border: none;
        margin-bottom: 0;

        .arco-collapse-item-header {
          padding: 12px 15px;
          background: #1e1e1e;
          border: none;
          border-bottom: 1px solid #3d3d3d;

          .file-content-header-wrapper {
            display: flex;
            align-items: center;
            justify-content: space-between;
            width: 100%;
            gap: 15px;

            .file-content-title {
              display: flex;
              align-items: center;
              gap: 10px;
              color: #fff;
              flex: 1;

              .arco-icon {
                font-size: 1.2rem;
              }
            }

            .copy-button {
              color: #3498db;
              padding: 4px 12px;
              transition: all 0.3s;

              &:hover {
                color: #2980b9;
                background: rgba(52, 152, 219, 0.1);
              }

              .arco-icon {
                font-size: 1rem;
              }
            }
          }
        }

        .arco-collapse-item-content {
          padding: 0;
          border: none;
          background: #2d2d2d;
        }
      }

      .file-content-header {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 12px 15px;
        background: #1e1e1e;
        color: #fff;
        border-bottom: 1px solid #3d3d3d;
      }

      .file-content-box {
        max-height: 1000px;
        overflow-y: auto;
        font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
        font-size: 13px;
        line-height: 1.5;

        .code-line {
          display: flex;
          align-items: stretch;
          min-height: 20px;
          transition: background-color 0.2s;

          &:hover {
            background: #3d3d3d;
          }

          &.comment-line {
            .line-content {
              color: #6a9955;
              font-style: italic;
            }
          }

          &.error-line {
            background: rgba(231, 76, 60, 0.2);
            border-left: 4px solid #e74c3c;

            .line-number {
              background: #e74c3c;
              color: #fff;
              font-weight: bold;
            }

            .line-content {
              color: #ff6b6b;
            }
          }

          .line-number {
            display: inline-block;
            width: 50px;
            text-align: right;
            padding: 0 10px;
            background: #252525;
            color: #858585;
            user-select: none;
            flex-shrink: 0;
          }

          .line-content {
            flex: 1;
            padding: 0 10px;
            color: #d4d4d4;
            white-space: pre;
            margin: 0;

            .error-comment {
              color: #ff6b6b;
              font-style: normal;
              font-family: inherit;
              font-size: inherit;
              font-weight: inherit;
            }
          }
        }
      }
    }

    .validation-item {
      padding: 15px 20px;
      border-radius: 8px;
      margin-bottom: 15px;
      display: flex;
      align-items: center;
      gap: 12px;

      .arco-icon {
        font-size: 1.5rem;
        flex-shrink: 0;
        width: 24px;
        height: 24px;
      }

      &.success {
        background: rgba(39, 174, 96, 0.1);
        border-left: 4px solid #27ae60;

        .arco-icon {
          color: #27ae60;
        }
      }

      &.warning {
        background: rgba(243, 156, 18, 0.1);
        border-left: 4px solid #f39c12;

        .arco-icon {
          color: #f39c12;
        }
      }

      &.error {
        background: rgba(231, 76, 60, 0.1);
        border-left: 4px solid #e74c3c;

        .arco-icon {
          color: #e74c3c;
        }
      }

      strong {
        display: block;
        margin-bottom: 5px;
        font-size: 1rem;
        font-weight: 600;
        color: #2c3e50;
      }

      p {
        margin: 5px 0;
      }

      ul {
        margin: 10px 0 0 20px;
        padding: 0;

        li {
          margin: 5px 0;
        }
      }
    }
  }

  .actions {
    margin-top: 20px;
    display: flex;
    gap: 12px;
    align-items: center;
  }

  .analysis-output {
    .analysis-section {
      margin-bottom: 25px;

      &:last-child {
        margin-bottom: 0;
      }

      .machine-section-wrapper {
        :deep(.arco-collapse) {
          background: transparent;
          border: none;
        }

        :deep(.compatible-collapse-item) {
          background: rgba(39, 174, 96, 0.1);
          border-left: 4px solid #27ae60;
          border-radius: 8px;
          margin-bottom: 0;

          .arco-collapse-item-header {
            padding: 15px 20px;
            background: transparent;
            border: none;

            .section-header {
              display: flex;
              align-items: center;
              gap: 12px;
              color: #27ae60;

              .arco-icon {
                font-size: 1.5rem;
              }

              strong {
                color: #2c3e50;
              }
            }
          }

          .arco-collapse-item-content {
            padding: 0 20px 15px 20px;
            border: none;
          }
        }

        :deep(.incompatible-collapse-item) {
          background: rgba(243, 156, 18, 0.1);
          border-left: 4px solid #f39c12;
          border-radius: 8px;
          margin-bottom: 0;

          .arco-collapse-item-header {
            padding: 15px 20px;
            background: transparent;
            border: none;

            .section-header {
              display: flex;
              align-items: center;
              gap: 12px;
              color: #f39c12;

              .arco-icon {
                font-size: 1.5rem;
              }

              strong {
                color: #2c3e50;
              }
            }
          }

          .arco-collapse-item-content {
            padding: 0 20px 15px 20px;
            border: none;
          }
        }

        .section-description {
          margin: 0 0 15px 0;
          padding: 0;
          font-size: 0.95rem;
          line-height: 1.6;
          color: #2c3e50;
        }
      }

      .machine-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 20px;
        margin-top: 0;

        .machine-card {
          border: 2px solid #e1e5eb;
          border-radius: 12px;
          padding: 20px;
          background: white;
          transition: all 0.3s ease;
          position: relative;
          overflow: hidden;

          &::before {
            content: '';
            position: absolute;
            top: 0;
            left: 0;
            right: 0;
            height: 4px;
            transition: all 0.3s ease;
          }

          &:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);
          }

          &.compatible {
            &::before {
              background: #27ae60;
            }

            &:hover {
              border-color: #27ae60;
            }
          }

          &.incompatible {
            opacity: 0.8;

            &::before {
              background: #e74c3c;
            }

            &:hover {
              border-color: #e74c3c;
            }
          }

          h4 {
            margin: 0 0 10px 0;
            color: #2c3e50;
            font-size: 1.3rem;
          }

          p {
            margin: 8px 0;
            color: #555;
            font-size: 0.9rem;
          }

          .reasons {
            margin: 10px 0 0 20px;
            padding: 0;
            font-size: 0.9rem;
            color: #666;

            li {
              margin: 5px 0;
            }
          }
        }
      }

      ul {
        margin: 10px 0 0 20px;
        padding: 0;

        li {
          margin: 5px 0;
        }
      }

      // 为 Missing Configurations 和 Configuration Warnings 添加圆角
      :deep(.arco-alert) {
        border-radius: 8px;
      }
    }
  }

  // 双列对比视图样式
  .comparison-view {
    margin-top: 20px;

    .comparison-container {
      display: grid;
      grid-template-columns: 1fr 1fr;
      gap: 20px;
      margin-top: 15px;
    }

    .comparison-column {
      background: #f7f9fc;
      border-radius: 8px;
      padding: 15px;
      border: 1px solid #e1e5eb;

      .column-title {
        display: flex;
        align-items: center;
        gap: 8px;
        margin: 0 0 12px 0;
        font-size: 1rem;
        font-weight: 600;
        color: #2c3e50;

        .arco-icon {
          font-size: 18px;
          color: #3498db;
        }
      }

      .code-view-box {
        background: white;
        border: 1px solid #dce0e6;
        border-radius: 6px;
        padding: 0;
        max-height: 500px;
        overflow-y: auto;

        .comparison-code-line {
          display: flex;
          min-height: 22px;
          line-height: 22px;
          border-bottom: 1px solid #f0f2f5;

          &:last-child {
            border-bottom: none;
          }

          &:hover {
            background: #f7f9fc;
          }
        }

        .comparison-line-number {
          flex-shrink: 0;
          width: 50px;
          padding: 0 12px;
          text-align: right;
          color: #86909c;
          background: #f7f9fc;
          border-right: 1px solid #e5e6eb;
          font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'Courier New', monospace;
          font-size: 12px;
          user-select: none;
        }

        .comparison-line-content {
          flex: 1;
          margin: 0;
          padding: 0 15px;
          font-family: 'Monaco', 'Menlo', 'Ubuntu Mono', 'Consolas', 'Courier New', monospace;
          font-size: 13px;
          color: #2c3e50;
          white-space: pre;
          word-wrap: normal;
          overflow-x: auto;
        }
      }
    }

    // 响应式：在小屏幕上改为单列
    @media (max-width: 768px) {
      .comparison-container {
        grid-template-columns: 1fr;
      }
    }
  }
}
</style>

