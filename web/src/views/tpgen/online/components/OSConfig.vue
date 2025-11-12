<template>
  <a-card class="form-section" :bordered="false">
    <template #title>
      <div class="section-title">
        <icon-computer />
        Operating System Environment
      </div>
    </template>

    <a-form-item label="OS Configuration Method">
      <a-radio-group v-model="localConfigMethod" @change="handleUpdate">
        <a-radio value="same">Same OS for all machines</a-radio>
        <a-radio value="individual">Individual OS configuration</a-radio>
      </a-radio-group>
    </a-form-item>

    <!-- 统一配置 -->
    <template v-if="localConfigMethod === 'same'">
      <a-form-item label="OS Distribution" field="os">
        <a-select v-model="localOs" placeholder="Select an OS" @change="handleUpdate">
          <a-option v-for="option in osOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </a-option>
        </a-select>
      </a-form-item>

      <a-form-item label="Deployment Method" field="deployment">
        <a-radio-group v-model="localDeployment" @change="handleUpdate">
          <a-radio v-for="option in deploymentOptions" :key="option.value" :value="option.value">
            {{ option.label }}
          </a-radio>
        </a-radio-group>
      </a-form-item>
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

          <a-form-item label="OS Distribution">
            <a-select
              v-model="localIndividualConfig[machineId].os"
              placeholder="Select an OS"
              @change="handleUpdate"
            >
              <a-option v-for="option in osOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </a-option>
            </a-select>
          </a-form-item>

          <a-form-item label="Deployment Method">
            <a-radio-group
              v-model="localIndividualConfig[machineId].deployment"
              @change="handleUpdate"
            >
              <a-radio v-for="option in deploymentOptions" :key="option.value" :value="option.value">
                {{ option.label }}
              </a-radio>
            </a-radio-group>
          </a-form-item>
        </a-card>
      </div>
    </template>
  </a-card>
</template>

<script setup lang="ts">
import { deploymentOptions, osOptions } from '../mockData'
import { useMachines } from '../composables/useMachines'

defineOptions({ name: 'OSConfig' })

const props = defineProps<{
  configMethod: 'same' | 'individual'
  os?: string
  deployment?: string
  individualConfig: Record<number, { os: string, deployment: string }>
  selectedMachines: number[]
}>()

const emit = defineEmits<{
  'update:configMethod': [value: 'same' | 'individual']
  'update:os': [value: string]
  'update:deployment': [value: string]
  'update:individualConfig': [value: Record<number, { os: string, deployment: string }>]
  'update': []
}>()

// 使用 machines composable
const { getMachineName } = useMachines()

const localConfigMethod = computed({
  get: () => props.configMethod,
  set: (val) => emit('update:configMethod', val),
})

const localOs = computed({
  get: () => props.os || '',
  set: (val) => emit('update:os', val),
})

const localDeployment = computed({
  get: () => props.deployment || '',
  set: (val) => emit('update:deployment', val),
})

const localIndividualConfig = computed({
  get: () => props.individualConfig,
  set: (val) => emit('update:individualConfig', val),
})

// 确保每个选中的机器都有配置
watch(() => props.selectedMachines, (machines) => {
  const config = { ...localIndividualConfig.value }
  machines.forEach((id) => {
    if (!config[id]) {
      config[id] = { os: '', deployment: '' }
    }
  })
  emit('update:individualConfig', config)
}, { immediate: true })

// getMachineName 现在从 composable 提供

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
