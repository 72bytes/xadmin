<template>
  <a-card class="form-section" :bordered="false">
    <template #title>
      <div class="section-title">
        <icon-computer />
        Hardware Platform Configuration
      </div>
    </template>

    <!-- Product Name 选择 -->
    <a-form-item label="Product Name" field="productName">
      <a-select 
        v-model="localProductName" 
        placeholder="Select Product Name" 
        :loading="productNameLoading"
        allow-clear
        @change="handleProductNameChange"
      >
        <a-option 
          v-for="option in productNameOptions" 
          :key="option.value" 
          :value="option.value"
        >
          {{ option.label }}
        </a-option>
      </a-select>
    </a-form-item>

    <!-- ASIC Name 选择（根据 Product Name 过滤） -->
    <a-form-item label="ASIC Name" field="asicName">
      <a-select 
        v-model="localAsicName" 
        placeholder="Select ASIC Name" 
        :loading="asicNameLoading"
        :disabled="!localProductName"
        allow-clear
        @change="handleAsicNameChange"
      >
        <a-option 
          v-for="option in asicNameOptions" 
          :key="option.value" 
          :value="option.value"
        >
          {{ option.label }}
        </a-option>
      </a-select>
      <template #extra>
        <span v-if="!localProductName" style="color: #999; font-size: 12px;">
          Please select Product Name first
        </span>
      </template>
    </a-form-item>

    <!-- Available Test Machines -->
    <a-form-item label="Available Test Machines">
      <div v-if="machinesLoading" class="loading-container">
        <a-spin />
      </div>
      <div v-else-if="machines.length === 0" class="no-machines">
        <a-empty description="No machines match the selected criteria" />
      </div>
      <div v-else class="machine-list">
        <div
          v-for="machine in machines"
          :key="machine.id"
          class="machine-card"
          :class="{ selected: localSelectedMachines.includes(machine.id) }"
          @click="toggleMachine(machine.id)"
        >
          <h4>{{ machine.hostname }}</h4>
          <p><strong>Product:</strong> {{ machine.productName || 'N/A' }}</p>
          <p><strong>ASIC:</strong> {{ machine.asicName || 'N/A' }}</p>
          <p><strong>GPU:</strong> {{ machine.gpuModel || 'N/A' }}</p>
          <p><strong>IP:</strong> {{ machine.ipAddress || 'N/A' }}</p>
          <a-tag color="green">Available</a-tag>
        </div>
      </div>
    </a-form-item>

    <!-- Selected Test Machines -->
    <a-form-item label="Selected Test Machines" v-if="allSelectedMachinesList.length > 0">
      <div class="selected-machines-container">
        <div class="selected-count">
          <a-tag color="arcoblue" size="large">
            <template #icon><icon-check-circle /></template>
            {{ allSelectedMachinesList.length }} machine(s) selected
          </a-tag>
        </div>
        <div class="selected-machine-cards">
          <div
            v-for="machine in allSelectedMachinesList"
            :key="machine.id"
            class="selected-machine-card"
          >
            <div class="card-header">
              <h4>{{ machine.hostname }}</h4>
              <a-button
                type="text"
                size="small"
                class="remove-btn"
                @click="removeMachine(machine.id)"
              >
                <template #icon><icon-close /></template>
              </a-button>
            </div>
            <div class="card-content">
              <p><strong>Product:</strong> {{ machine.productName || 'N/A' }}</p>
              <p><strong>ASIC:</strong> {{ machine.asicName || 'N/A' }}</p>
              <p><strong>GPU:</strong> {{ machine.gpuModel || 'N/A' }}</p>
              <p><strong>IP:</strong> {{ machine.ipAddress || 'N/A' }}</p>
            </div>
            <a-tag color="green" class="card-status">Selected</a-tag>
          </div>
        </div>
      </div>
    </a-form-item>
  </a-card>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted } from 'vue'
import { getProductNames, getAsicNames, getMachinesBySelection, type SutDevice } from '@/apis/sutDevice'
import { Message } from '@arco-design/web-vue'
import { IconCheckCircle, IconDesktop, IconClose } from '@arco-design/web-vue/es/icon'

defineOptions({ name: 'HardwareConfig' })

const props = defineProps<{
  productName: string
  asicName: string
  selectedMachines: number[]
}>()

const emit = defineEmits<{
  'update:productName': [value: string]
  'update:asicName': [value: string]
  'update:selectedMachines': [value: number[]]
  'update': []
  'machinesUpdate': [machines: SutDevice[]]
}>()

// Product Name 选项
const productNameOptions = ref<Array<{label: string, value: string}>>([])
const productNameLoading = ref(false)

// ASIC Name 选项
const asicNameOptions = ref<Array<{label: string, value: string}>>([])
const asicNameLoading = ref(false)

// Machines 数据
const machines = ref<SutDevice[]>([])
const machinesLoading = ref(false)

const localProductName = computed({
  get: () => props.productName,
  set: val => emit('update:productName', val),
})

const localAsicName = computed({
  get: () => props.asicName,
  set: val => emit('update:asicName', val),
})

const localSelectedMachines = computed({
  get: () => props.selectedMachines,
  set: val => emit('update:selectedMachines', val),
})

// 已选择的机器列表（用于显示）
const selectedMachinesList = computed(() => {
  return machines.value.filter(machine => localSelectedMachines.value.includes(machine.id))
})

// 全局机器缓存（保存所有已选机器的完整信息，支持跨类型选择）
const machinesCache = ref<Record<number, SutDevice>>({})

// 所有已选机器列表（包括不在当前 Available 列表中的机器）
const allSelectedMachinesList = computed(() => {
  const selectedIds = localSelectedMachines.value
  const allMachines: SutDevice[] = []
  
  selectedIds.forEach(id => {
    // 优先从当前列表获取（保证是最新数据）
    const currentMachine = machines.value.find(m => m.id === id)
    if (currentMachine) {
      allMachines.push(currentMachine)
    } else if (machinesCache.value[id]) {
      // 如果当前列表没有，从缓存获取
      allMachines.push(machinesCache.value[id])
    }
  })
  
  return allMachines
})

// 加载 Product Name 选项
const loadProductNames = async () => {
  productNameLoading.value = true
  try {
    const options = await getProductNames()
    productNameOptions.value = options
  } catch (error) {
    console.error('[HardwareConfig] 加载 Product Name 失败:', error)
    Message.error('Failed to load Product Names')
  } finally {
    productNameLoading.value = false
  }
}

// 加载 ASIC Name 选项（根据 Product Name 过滤）
const loadAsicNames = async (productName: string) => {
  if (!productName) {
    asicNameOptions.value = []
    return
  }
  asicNameLoading.value = true
  try {
    const options = await getAsicNames(productName)
    asicNameOptions.value = options
  } catch (error) {
    console.error('[HardwareConfig] 加载 ASIC Name 失败:', error)
    Message.error('Failed to load ASIC Names')
  } finally {
    asicNameLoading.value = false
  }
}

// 加载机器列表
const loadMachines = async () => {
  machinesLoading.value = true
  try {
    const result = await getMachinesBySelection(localProductName.value, localAsicName.value)
    machines.value = result
    // 通知父组件机器列表已更新
    emit('machinesUpdate', result)
  } catch (error) {
    console.error('[HardwareConfig] 加载机器列表失败:', error)
    Message.error('Failed to load machines')
    machines.value = []
    emit('machinesUpdate', [])
  } finally {
    machinesLoading.value = false
  }
}

// Product Name 改变时的处理
const handleProductNameChange = (value: string) => {
  localAsicName.value = '' // 清空 ASIC Name
  // 不清空已选机器，支持跨类型选择
  if (value) {
    loadAsicNames(value)
    loadMachines()
  } else {
    asicNameOptions.value = []
    machines.value = []
  }
  handleUpdate()
}

// ASIC Name 改变时的处理
const handleAsicNameChange = () => {
  // 不清空已选机器，支持跨类型选择
  loadMachines()
  handleUpdate()
}

// 切换机器选择
const toggleMachine = (id: number) => {
  const machine = machines.value.find(m => m.id === id)
  if (!machine) return
  
  const index = localSelectedMachines.value.indexOf(id)
  if (index === -1) {
    // 选择机器时，缓存机器信息
    machinesCache.value[id] = machine
    localSelectedMachines.value = [...localSelectedMachines.value, id]
  } else {
    // 取消选择
    localSelectedMachines.value = localSelectedMachines.value.filter(mid => mid !== id)
  }
  handleUpdate()
}

// 移除已选机器
const removeMachine = (id: number) => {
  localSelectedMachines.value = localSelectedMachines.value.filter(mid => mid !== id)
  handleUpdate()
}

const handleUpdate = () => {
  emit('update')
  // 传递所有已选机器的完整信息（包括缓存中的机器）
  emit('machinesUpdate', allSelectedMachinesList.value)
}

// 监听 machines 变化，缓存所有机器信息并立即同步到父组件
watch(machines, (newMachines) => {
  newMachines.forEach(machine => {
    machinesCache.value[machine.id] = machine
  })
  // 立即更新父组件的 machinesMap
  handleUpdate()
}, { deep: true })

// 监听已选机器列表变化，立即同步到父组件
watch(localSelectedMachines, () => {
  handleUpdate()
}, { deep: true })

// 组件挂载时加载 Product Name 选项
onMounted(() => {
  loadProductNames()
  // 如果有初始值，加载对应的数据
  if (localProductName.value) {
    loadAsicNames(localProductName.value)
    loadMachines()
  }
})
</script>

<style scoped lang="scss">
// 覆盖 Arco Design 表单项样式，确保横向布局
:deep(.arco-form-item-content) {
  display: block !important;
  width: 100%;
}

:deep(.arco-form-item-content-flex) {
  display: block !important;
  width: 100%;
}

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

.loading-container {
  padding: 40px;
  text-align: center;
}

.no-machines {
  padding: 40px;
  text-align: center;
}

.machine-list {
  display: grid !important;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)) !important;
  gap: 16px;
  margin-top: 15px;
  width: 100%;

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

.selected-machines-container {
  margin-top: 10px;

  .selected-count {
    margin-bottom: 16px;
  }

  .selected-machine-cards {
    display: grid !important;
    grid-template-columns: repeat(auto-fill, minmax(220px, 1fr)) !important;
    gap: 16px;
    width: 100%;
  }

  .selected-machine-card {
    border: 2px solid #27ae60;
    border-radius: 12px;
    padding: 16px;
    background: rgba(39, 174, 96, 0.05);
    position: relative;
    transition: all 0.3s ease;
    box-shadow: 0 4px 12px rgba(39, 174, 96, 0.15);

    &::before {
      content: '';
      position: absolute;
      top: 0;
      left: 0;
      right: 0;
      height: 4px;
      background: #27ae60;
    }

    &:hover {
      transform: translateY(-5px);
      box-shadow: 0 8px 20px rgba(39, 174, 96, 0.25);
    }

    .card-header {
      display: flex;
      justify-content: space-between;
      align-items: flex-start;
      margin-bottom: 12px;
      padding-bottom: 12px;
      border-bottom: 1px solid rgba(39, 174, 96, 0.2);

      h4 {
        margin: 0;
        color: #2c3e50;
        font-size: 1.2rem;
        font-weight: 600;
      }

      .remove-btn {
        color: #e74c3c;
        transition: all 0.2s ease;

        &:hover {
          color: #c0392b;
          transform: scale(1.1);
        }
      }
    }

    .card-content {
      p {
        margin: 6px 0;
        color: #555;
        font-size: 0.9rem;

        strong {
          color: #2c3e50;
          margin-right: 8px;
        }
      }
    }

    .card-status {
      position: absolute;
      bottom: 16px;
      right: 16px;
      font-size: 12px;
    }
  }
}

/* 移除媒体查询，始终保持横向布局 */
@media (max-width: 768px) {
  .machine-list {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)) !important;
  }
  
  .selected-machine-cards {
    grid-template-columns: repeat(auto-fill, minmax(180px, 1fr)) !important;
  }
}
</style>

