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

      <!-- 固件管理 -->
      <FirmwareConfig
        v-model:firmware-version="formData.firmwareVersion"
        v-model:version-comparison="formData.versionComparison"
        @update="updateProgress"
      />

      <!-- 测试用例管理 -->
      <TestCaseManager
        v-model:selected-test-cases="formData.selectedTestCases"
        @update="updateProgress"
      />

      <!-- 操作按钮 -->
      <div class="actions">
        <a-button @click="handleReset">
          <template #icon><icon-refresh /></template>
          Reset Form
        </a-button>
        <a-button type="primary" @click="handleGenerate">
          <template #icon><icon-settings /></template>
          Generate Test Plan
        </a-button>
      </div>
    </a-form>

    <!-- YAML 预览 -->
    <YamlPreview v-if="generatedYaml" :yaml-data="generatedYaml" @close="generatedYaml = null" />
  </div>
</template>

<script setup lang="ts">
import type { FormData, YamlData } from '../types'
import { mockMachines } from '../mockData'
import HardwareConfig from './HardwareConfig.vue'
import OSConfig from './OSConfig.vue'
import KernelConfig from './KernelConfig.vue'
import FirmwareConfig from './FirmwareConfig.vue'
import TestCaseManager from './TestCaseManager.vue'
import YamlPreview from './YamlPreview.vue'

defineOptions({ name: 'CustomPlan' })

const emit = defineEmits<{
  progressChange: [value: number]
}>()

const formData = reactive<FormData>({
  cpu: 'Ryzen Threadripper',
  gpu: 'Radeon RX 7900 Series',
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
  formData.gpu = 'Radeon RX 7900 Series'
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

// 生成 YAML
const handleGenerate = () => {
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

  // 滚动到预览区域
  setTimeout(() => {
    document.querySelector('.yaml-preview')?.scrollIntoView({ behavior: 'smooth' })
  }, 100)
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
}
</style>

