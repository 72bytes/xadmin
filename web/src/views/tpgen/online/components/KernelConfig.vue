<template>
  <a-card class="form-section" :bordered="false">
    <template #title>
      <div class="section-title">
        <icon-code />
        Kernel and Driver Configuration
      </div>
    </template>

    <a-form-item label="Kernel Configuration Method">
      <a-radio-group v-model="localConfigMethod" @change="handleUpdate">
        <a-radio value="same">Same kernel for all machines</a-radio>
        <a-radio value="individual">Individual kernel configuration</a-radio>
      </a-radio-group>
    </a-form-item>

    <!-- 统一配置 -->
    <template v-if="localConfigMethod === 'same'">
      <a-row :gutter="16">
        <a-col :span="12">
          <a-form-item label="Kernel Type">
            <a-select
              v-model="localKernelType"
              placeholder="Select kernel type"
              @change="handleUpdate"
            >
              <a-option v-for="option in kernelTypeOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </a-option>
            </a-select>
          </a-form-item>
        </a-col>
        <a-col :span="12">
          <a-form-item label="Kernel Version">
            <a-select
              v-model="localKernelVersion"
              placeholder="Select kernel version"
              @change="handleUpdate"
            >
              <a-option v-for="option in kernelVersionOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </a-option>
            </a-select>
          </a-form-item>
        </a-col>
      </a-row>
    </template>

    <!-- 独立配置 -->
    <template v-else>
      <div v-if="selectedMachines.length === 0" class="empty-tip">
        <a-alert type="info">Please select machines first</a-alert>
      </div>
      <div v-else class="individual-configs">
        <a-card
          v-for="machineId in selectedMachines"
          :key="machineId"
          class="machine-config"
          :bordered="false"
        >
          <template #title>
            <div class="machine-name">
              <icon-desktop />
              {{ getMachineName(machineId) }}
            </div>
          </template>

          <a-row :gutter="16">
            <a-col :span="12">
              <a-form-item label="Kernel Type">
                <a-select
                  v-model="localIndividualConfig[machineId].type"
                  placeholder="Select kernel type"
                  @change="handleUpdate"
                >
                  <a-option v-for="option in kernelTypeOptions" :key="option.value" :value="option.value">
                    {{ option.label }}
                  </a-option>
                </a-select>
              </a-form-item>
            </a-col>
            <a-col :span="12">
              <a-form-item label="Kernel Version">
                <a-select
                  v-model="localIndividualConfig[machineId].version"
                  placeholder="Select kernel version"
                  @change="handleUpdate"
                >
                  <a-option v-for="option in kernelVersionOptions" :key="option.value" :value="option.value">
                    {{ option.label }}
                  </a-option>
                </a-select>
              </a-form-item>
            </a-col>
          </a-row>
        </a-card>
      </div>
    </template>
  </a-card>
</template>

<script setup lang="ts">
import { kernelTypeOptions, kernelVersionOptions, mockMachines } from '../mockData'

defineOptions({ name: 'KernelConfig' })

const props = defineProps<{
  configMethod: 'same' | 'individual'
  kernelType?: string
  kernelVersion?: string
  individualConfig: Record<number, { type: string; version: string }>
  selectedMachines: number[]
}>()

const emit = defineEmits<{
  'update:configMethod': [value: 'same' | 'individual']
  'update:kernelType': [value: string]
  'update:kernelVersion': [value: string]
  'update:individualConfig': [value: Record<number, { type: string; version: string }>]
  'update': []
}>()

const localConfigMethod = computed({
  get: () => props.configMethod,
  set: val => emit('update:configMethod', val),
})

const localKernelType = computed({
  get: () => props.kernelType || '',
  set: val => emit('update:kernelType', val),
})

const localKernelVersion = computed({
  get: () => props.kernelVersion || '',
  set: val => emit('update:kernelVersion', val),
})

const localIndividualConfig = computed({
  get: () => props.individualConfig,
  set: val => emit('update:individualConfig', val),
})

watch(() => props.selectedMachines, (machines) => {
  const config = { ...localIndividualConfig.value }
  machines.forEach((id) => {
    if (!config[id]) {
      config[id] = { type: '', version: '' }
    }
  })
  emit('update:individualConfig', config)
}, { immediate: true })

const getMachineName = (id: number) => {
  return mockMachines.find(m => m.id === id)?.name || `Machine ${id}`
}

const handleUpdate = () => {
  emit('update')
}
</script>

<style scoped lang="scss">
.form-section {
  background: white;
  border-radius: 12px;
  margin-bottom: 25px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  border-left: 5px solid #3498db;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
  }

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

.empty-tip {
  padding: 20px;
}

.individual-configs {
  display: grid;
  gap: 20px;

  .machine-config {
    border: 2px solid #e1e5eb;
    border-radius: 10px;
    transition: all 0.3s ease;

    &:hover {
      border-color: #3498db;
    }

    .machine-name {
      display: flex;
      align-items: center;
      gap: 10px;
      color: #2c3e50;
      font-weight: 600;
    }
  }
}
</style>

