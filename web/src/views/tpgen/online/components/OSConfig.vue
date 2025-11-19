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
        <a-radio value="individual">Individual OS configuration</a-radio>
        <a-radio value="same">Same OS for all machines</a-radio>
      </a-radio-group>
    </a-form-item>

    <!-- 统一配置 -->
    <template v-if="localConfigMethod === 'same'">
      <a-form-item label="OS Family" field="os">
        <a-select 
          v-model="localOs" 
          placeholder="Select an OS" 
          :loading="osLoading"
          @change="handleUpdate"
        >
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

          <a-form-item label="OS Family">
            <a-select
              v-model="localIndividualConfig[machineId].os"
              placeholder="Select an OS"
              :loading="osLoading"
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
import { computed, watch, ref, onMounted } from 'vue'
import { getOsOptions } from '@/apis/osConfig'
import { Message } from '@arco-design/web-vue'

defineOptions({ name: 'OSConfig' })

const props = defineProps<{
  configMethod: 'same' | 'individual'
  os?: string
  deployment?: string
  individualConfig: Record<number, { os: string; deployment: string }>
  selectedMachines: number[]
  machinesMap?: Record<number, any>
}>()

const emit = defineEmits<{
  'update:configMethod': [value: 'same' | 'individual']
  'update:os': [value: string]
  'update:deployment': [value: string]
  'update:individualConfig': [value: Record<number, { os: string; deployment: string }>]
  'update': []
}>()

// OS 选项（从数据库加载）
const osOptions = ref<Array<{label: string, value: string}>>([])
const osLoading = ref(false)

// Deployment 选项（Bare Metal / VM / WSL）
const deploymentOptions = ref([
  { label: 'Bare Metal', value: 'bare_metal' },
  { label: 'VM', value: 'vm' },
  { label: 'WSL', value: 'wsl' },
])

const localConfigMethod = computed({
  get: () => props.configMethod,
  set: val => emit('update:configMethod', val),
})

const localOs = computed({
  get: () => props.os || '',
  set: val => emit('update:os', val),
})

const localDeployment = computed({
  get: () => props.deployment || '',
  set: val => emit('update:deployment', val),
})

const localIndividualConfig = computed({
  get: () => props.individualConfig,
  set: val => emit('update:individualConfig', val),
})

// 加载 OS 选项
const loadOsOptions = async () => {
  osLoading.value = true
  try {
    const configs = await getOsOptions()
    osOptions.value = configs.map(c => ({
      label: c.label,
      value: c.value
    }))
  } catch (error) {
    console.error('[OSConfig] 加载 OS 选项失败:', error)
    Message.error('Failed to load OS options')
  } finally {
    osLoading.value = false
  }
}

// 确保每个选中的机器都有配置
watch(() => props.selectedMachines, (machines) => {
  const config = { ...localIndividualConfig.value }
  machines.forEach((id) => {
    if (!config[id]) {
      config[id] = {
        os: osOptions.value[0]?.value || '',
        deployment: deploymentOptions.value[0]?.value || ''
      }
    }
  })
  emit('update:individualConfig', config)
}, { immediate: true })

const getMachineName = (id: number) => {
  const machine = props.machinesMap?.[id]
  return machine?.hostname || `Machine ${id}`
}

const handleUpdate = () => {
  emit('update')
}

onMounted(() => {
  loadOsOptions()
})
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
  grid-template-columns: repeat(auto-fill, minmax(450px, 1fr));
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

