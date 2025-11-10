<template>
  <div class="upload-plan">
    <a-card class="form-section" :bordered="false">
      <template #title>
        <div class="section-title">
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
        <a-alert type="success">
          <template #icon><icon-check-circle /></template>
          <div>
            <strong>File uploaded successfully!</strong>
            <p>{{ uploadedFile.name }} ({{ formatFileSize(uploadedFile.size) }})</p>
          </div>
        </a-alert>
      </div>

      <div v-if="validationResults.length > 0" class="validation-results">
        <h3><icon-info-circle /> Uploaded Plan Analysis</h3>
        <div
          v-for="(result, index) in validationResults"
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
        <a-alert type="success">
          <template #icon><icon-check-circle /></template>
          <div>
            <strong>Compatible Machines ({{ analysisResult.compatibleMachines.length }})</strong>
            <p>The following machines match your test plan requirements:</p>
          </div>
        </a-alert>
        <div class="machine-grid">
          <div
            v-for="machine in analysisResult.compatibleMachines"
            :key="machine.id"
            class="machine-card compatible"
          >
            <h4>{{ machine.name }}</h4>
            <p><strong>Motherboard:</strong> {{ machine.motherboard }}</p>
            <p><strong>GPU:</strong> {{ machine.gpu }}</p>
            <p><strong>CPU:</strong> {{ machine.cpu }}</p>
            <a-tag color="green">Compatible</a-tag>
          </div>
        </div>
      </div>

      <!-- 不兼容的机器 -->
      <div v-if="analysisResult.incompatibleMachines.length > 0" class="analysis-section">
        <a-alert type="warning">
          <template #icon><icon-exclamation-circle /></template>
          <div>
            <strong>Incompatible Machines ({{ analysisResult.incompatibleMachines.length }})</strong>
            <p>The following machines do not match your test plan requirements:</p>
          </div>
        </a-alert>
        <div class="machine-grid">
          <div
            v-for="item in analysisResult.incompatibleMachines"
            :key="item.machine.id"
            class="machine-card incompatible"
          >
            <h4>{{ item.machine.name }}</h4>
            <p><strong>Motherboard:</strong> {{ item.machine.motherboard }}</p>
            <p><strong>GPU:</strong> {{ item.machine.gpu }}</p>
            <p><strong>CPU:</strong> {{ item.machine.cpu }}</p>
            <a-tag color="red">Incompatible</a-tag>
            <ul class="reasons">
              <li v-for="(reason, idx) in item.reasons" :key="idx">{{ reason }}</li>
            </ul>
          </div>
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
  { id: 1, name: 'Machine A', motherboard: 'ASUS Pro WS X570-ACE', gpu: 'Radeon RX 7900 Series', cpu: 'Ryzen Threadripper', status: 'Available' },
  { id: 2, name: 'Machine B', motherboard: 'Gigabyte B550 AORUS', gpu: 'Radeon RX 7900 Series', cpu: 'Ryzen Threadripper', status: 'Available' },
  { id: 3, name: 'Machine C', motherboard: 'ASRock X570 Taichi', gpu: 'Radeon RX 6800 Series', cpu: 'Ryzen 7', status: 'Available' },
  { id: 4, name: 'Machine D', motherboard: 'MSI MEG X570 GODLIKE', gpu: 'Radeon Pro W7800', cpu: 'EPYC', status: 'Available' },
  { id: 5, name: 'Machine E', motherboard: 'ASUS Pro WS X570-ACE', gpu: 'Radeon Pro W6800', cpu: 'Ryzen Threadripper', status: 'Available' },
]

const fileInputRef = ref<HTMLInputElement>()
const isDragOver = ref(false)
const uploadedFile = ref<File | null>(null)
const analyzing = ref(false)
const validationResults = ref<Array<{ type: string; title: string; message?: string; items?: string[] }>>([])
const analysisResult = ref<AnalysisResult | null>(null)

const handleClickUpload = () => {
  fileInputRef.value?.click()
}

const handleFileChange = (event: Event) => {
  const target = event.target as HTMLInputElement
  if (target.files && target.files.length > 0) {
    handleFile(target.files[0])
  }
}

const handleDrop = (event: DragEvent) => {
  isDragOver.value = false
  if (event.dataTransfer?.files && event.dataTransfer.files.length > 0) {
    handleFile(event.dataTransfer.files[0])
  }
}

const handleFile = (file: File) => {
  if (!file.name.endsWith('.yaml') && !file.name.endsWith('.yml')) {
    Message.error('Please upload a YAML file')
    return
  }

  uploadedFile.value = file
  validationResults.value = []
  analysisResult.value = null
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
  if (!uploadedFile.value)
    return

  analyzing.value = true
  try {
    // 读取文件内容
    const text = await uploadedFile.value.text()
    const yamlData = parseYaml(text)

    // 验证和分析
    const result = validateYamlConfig(yamlData)
    analysisResult.value = result

    validationResults.value = [
      {
        type: 'success',
        title: 'YAML File Parsed Successfully',
        message: 'Click below to see detailed analysis',
      },
    ]

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

// 验证 YAML 配置
function validateYamlConfig(yamlData: any): AnalysisResult {
  const result: AnalysisResult = {
    compatibleMachines: [],
    incompatibleMachines: [],
    missingConfigurations: [],
    warnings: [],
  }

  const requiredCPU = yamlData.hardware?.cpu
  const requiredGPU = yamlData.hardware?.gpu

  if (!requiredCPU || !requiredGPU) {
    result.missingConfigurations.push('Hardware configuration (CPU/GPU) is missing in the YAML file')
  }

  // 检查机器兼容性
  mockMachines.forEach((machine) => {
    const cpuMatch = !requiredCPU || machine.cpu === requiredCPU
    const gpuMatch = !requiredGPU || machine.gpu === requiredGPU

    if (cpuMatch && gpuMatch) {
      result.compatibleMachines.push(machine)
    }
    else {
      result.incompatibleMachines.push({
        machine,
        reasons: [
          ...(!cpuMatch ? [`CPU mismatch: required ${requiredCPU}, found ${machine.cpu}`] : []),
          ...(!gpuMatch ? [`GPU mismatch: required ${requiredGPU}, found ${machine.gpu}`] : []),
        ],
      })
    }
  })

  // 检查其他配置
  if (!yamlData.environment?.os) {
    result.warnings.push('OS configuration is not specified')
  }

  if (!yamlData.environment?.kernel) {
    result.warnings.push('Kernel configuration is not specified')
  }

  if (!yamlData.firmware?.gpu_version) {
    result.warnings.push('GPU firmware version is not specified')
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
</script>

<style scoped lang="scss">
.upload-plan {
  .form-section {
    background: white;
    border-radius: 12px;
    margin-bottom: 25px;
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
    margin-bottom: 20px;
  }

  .validation-results {
    margin-top: 25px;

    h3 {
      display: flex;
      align-items: center;
      gap: 10px;
      margin-bottom: 15px;
      color: #2c3e50;
    }

    .validation-item {
      padding: 15px;
      border-radius: 8px;
      margin-bottom: 15px;
      display: flex;
      align-items: flex-start;
      gap: 15px;

      .arco-icon {
        font-size: 1.5rem;
        flex-shrink: 0;
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
  }

  .analysis-output {
    .analysis-section {
      margin-bottom: 25px;

      &:last-child {
        margin-bottom: 0;
      }

      .machine-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
        gap: 20px;
        margin-top: 15px;

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
    }
  }
}
</style>

