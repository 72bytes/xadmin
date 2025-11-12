<template>
  <a-card class="form-section" :bordered="false">
    <template #title>
      <div class="section-title">
        <icon-cpu />
        Hardware Platform Configuration
      </div>
    </template>

    <!-- <a-form-item label="CPU Model" field="cpu">
      <a-select v-model="localCpu" placeholder="Select CPU" @change="handleUpdate">
        <a-option v-for="option in cpuOptions" :key="option.value" :value="option.value">
          {{ option.label }}
        </a-option>
      </a-select>
    </a-form-item> -->

    <a-form-item label="AMD GPU Product Line" field="gpu">
      <a-select
        v-model="localGpu"
        placeholder="Select GPU"
        :loading="gpuLoading"
        @change="handleUpdate"
      >
        <a-option
          v-for="option in gpuOptions"
          :key="option.value"
          :value="option.value"
        >
          {{ option.label }}
        </a-option>
      </a-select>
    </a-form-item>

    <a-form-item label="Available Test Machines">
      <a-spin :loading="machinesLoading" style="width: 100%">
        <div v-if="filteredMachines.length === 0" class="no-machines">
          <a-empty description="No machines match the selected criteria" />
        </div>
        <div v-else class="machine-list">
          <div
            v-for="machine in filteredMachines"
            :key="machine.id"
            class="machine-card"
            :class="{ selected: localSelectedMachines.includes(machine.id) }"
            @click="toggleMachine(machine.id)"
          >
            <h4>{{ machine.hostname || machine.name }}</h4>
            <p v-if="machine.asicName"><strong>ASIC:</strong> {{ machine.asicName }}</p>
            <p v-if="machine.gpuModel"><strong>GPU Model:</strong> {{ machine.gpuModel }}</p>
            <p v-if="machine.gpuSeries"><strong>GPU Series:</strong> {{ machine.gpuSeries }}</p>
            <p v-if="machine.ipAddress"><strong>IP:</strong> {{ machine.ipAddress }}</p>
            <a-tag color="green">Available</a-tag>
          </div>
        </div>
      </a-spin>
    </a-form-item>
  </a-card>
</template>

<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { Message } from '@arco-design/web-vue'
import type { Machine } from '../types'
import { getGpuOptions, getGpuSeriesOptions } from '@/apis/sutDevice'
import * as tpdbApi from '@/apis/tpdb'

defineOptions({ name: 'HardwareConfig' })

const props = defineProps<{
  cpu: string
  gpu: string
  selectedMachines: number[]
}>()

const emit = defineEmits<{
  'update:cpu': [value: string]
  'update:gpu': [value: string]
  'update:selectedMachines': [value: number[]]
  'update': []
}>()

// CPU 选项（静态数据）
const cpuOptions = ref([
  { label: 'Ryzen Threadripper', value: 'Ryzen Threadripper' },
  { label: 'Intel Xeon', value: 'Intel Xeon' },
  { label: 'AMD EPYC', value: 'AMD EPYC' },
])

// GPU 选项改为响应式数据
const gpuOptions = ref<Array<{ label: string, value: string }>>([])
const gpuLoading = ref(false)

// 真实机器数据（从数据库获取）
const machines = ref<Machine[]>([])
const machinesLoading = ref(false)

const localCpu = computed({
  get: () => props.cpu,
  set: (val) => emit('update:cpu', val),
})

const localGpu = computed({
  get: () => props.gpu,
  set: (val) => emit('update:gpu', val),
})

const localSelectedMachines = computed({
  get: () => props.selectedMachines,
  set: (val) => emit('update:selectedMachines', val),
})

// 加载 GPU 系列选项的函数
const loadGpuOptions = async () => {
  gpuLoading.value = true
  try {
    // 使用 GPU Series 选项
    const options = await getGpuSeriesOptions()
    gpuOptions.value = options
    console.log('[HardwareConfig] GPU 系列选项加载成功:', options)

    // 如果当前没有选中值，或者当前值不在新的选项列表中，自动选择第一个
    if (options.length > 0) {
      const currentValueExists = options.some((opt) => opt.value === localGpu.value)
      if (!localGpu.value || !currentValueExists) {
        localGpu.value = options[0].value
        console.log('[HardwareConfig] 自动选择第一个 GPU 选项:', options[0].value)
      }
    }
  } catch (error) {
    console.error('[HardwareConfig] 加载 GPU 选项失败:', error)
    Message.error('加载 GPU 选项失败')
    gpuOptions.value = []
  } finally {
    gpuLoading.value = false
  }
}

// 加载真实设备数据
const loadMachines = async () => {
  machinesLoading.value = true
  try {
    const response = await tpdbApi.listSutDevices({ page: 1, size: 100 })
    if (response.success && response.data) {
      // 转换数据格式，兼容旧的 Machine 接口
      machines.value = (response.data.list || []).map((device) => ({
        id: device.id,
        hostname: device.hostname,
        asicName: device.asicName,
        ipAddress: device.ipAddress,
        deviceId: device.deviceId,
        revId: device.revId,
        gpuSeries: device.gpuSeries,
        gpuModel: device.gpuModel,
        // 兼容旧字段
        name: device.hostname,
        gpu: device.gpuSeries || device.gpuModel || '',
        status: 'Available' as const,
      }))
      console.log('[HardwareConfig] 设备加载成功:', machines.value.length, '台')
    }
  } catch (error) {
    console.error('[HardwareConfig] 加载设备失败:', error)
    Message.error('加载设备数据失败')
    machines.value = []
  } finally {
    machinesLoading.value = false
  }
}

// 根据 GPU 系列过滤机器
const filteredMachines = computed(() => {
  if (!localGpu.value) {
    return machines.value
  }
  return machines.value.filter((machine) => {
    // 匹配 GPU 系列或 GPU 型号
    const gpuMatch = machine.gpuSeries === localGpu.value
      || machine.gpuModel === localGpu.value
      || machine.gpu === localGpu.value
    return gpuMatch
  })
})

// 切换机器选择
const toggleMachine = (id: number) => {
  const index = localSelectedMachines.value.indexOf(id)
  if (index === -1) {
    localSelectedMachines.value = [...localSelectedMachines.value, id]
  } else {
    localSelectedMachines.value = localSelectedMachines.value.filter((mid) => mid !== id)
  }
  handleUpdate()
}

const handleUpdate = () => {
  emit('update')
}

// 组件挂载时加载数据
onMounted(async () => {
  await Promise.all([
    loadGpuOptions(),
    loadMachines(),
  ])
})

// 监听 GPU 变化，重新过滤选中的机器
watch(localGpu, () => {
  const validMachineIds = filteredMachines.value.map((m) => m.id)
  localSelectedMachines.value = localSelectedMachines.value.filter((id) => validMachineIds.includes(id))
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

.no-machines {
  padding: 40px;
  text-align: center;
}

.machine-list {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(280px, 1fr));
  gap: 20px;
  margin-top: 15px;

  .machine-card {
    border: 2px solid #e1e5eb;
    border-radius: 12px;
    padding: 20px;
    cursor: pointer;
    transition: all 0.3s ease;
    background: white;
    position: relative;
    overflow: hidden;

    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: #3498db;
      transform: scaleX(0);
      transition: all 0.3s ease;
    }

    &:hover {
      border-color: #3498db;
      transform: translateY(-5px);
      box-shadow: 0 10px 20px rgba(0, 0, 0, 0.1);

      &::before {
        transform: scaleX(1);
      }
    }

    &.selected {
      border-color: #3498db;
      background: rgba(52, 152, 219, 0.05);
      box-shadow: 0 5px 15px rgba(52, 152, 219, 0.2);

      &::before {
        transform: scaleX(1);
        background: #27ae60;
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
  }
}

@media (max-width: 768px) {
  .machine-list {
    grid-template-columns: 1fr;
  }
}
</style>
