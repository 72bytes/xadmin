<template>
  <div class="configuration-form">
    <!-- OS 选择 -->
    <a-form-item label="OS Family">
      <a-select
        v-model="localConfig.osId"
        placeholder="Select OS"
        :loading="osLoading"
        @change="handleOsChange"
      >
        <a-option v-for="os in osOptions" :key="os.value" :value="os.value">
          {{ os.label }}
        </a-option>
      </a-select>
    </a-form-item>

    <!-- Deployment Method -->
    <a-form-item label="Deployment Method">
      <a-radio-group v-model="localConfig.deploymentMethod" @change="emitUpdate">
        <a-radio value="bare_metal">Bare Metal</a-radio>
        <a-radio value="vm">VM</a-radio>
        <a-radio value="wsl">WSL</a-radio>
      </a-radio-group>
    </a-form-item>

    <!-- Kernel 选择（依赖 OS） -->
    <a-form-item label="Kernel Version">
      <a-select
        v-model="localConfig.kernelVersion"
        placeholder="Select Kernel"
        :disabled="!localConfig.osId"
        :loading="kernelLoading"
        @change="emitUpdate"
      >
        <a-option v-for="kernel in kernelOptions" :key="kernel.value" :value="kernel.value">
          {{ kernel.label }}
        </a-option>
      </a-select>
    </a-form-item>

    <!-- Test Type 选择 -->
    <a-form-item label="Test Type">
      <div class="test-type-selector">
        <a-select
          v-model="localConfig.testTypeId"
          placeholder="Select Test Type"
          :loading="testTypeLoading"
          @change="handleTestTypeChange"
          style="flex: 1;"
        >
          <a-option v-for="type in testTypeOptions" :key="type.value" :value="type.value">
            {{ type.label }}
          </a-option>
        </a-select>
        <a-link href="#" class="create-test-type-link" @click.prevent="handleCreateTestType">
          <icon-plus /> Click here to create your test type
        </a-link>
      </div>
    </a-form-item>

    <!-- Test Components 加载指示器 -->
    <a-form-item v-if="testComponentsLoading" label="Test Components">
      <div class="loading-container">
        <a-spin tip="Loading test components..." />
      </div>
    </a-form-item>

    <!-- Test Components（依赖 Test Type）-->
    <a-form-item 
      v-else-if="localConfig.testTypeId && Object.keys(componentsByCategory).length > 0" 
      label="Test Components"
    >
      <div class="test-components-container">
        <!-- Test Components 列表 -->
        <div class="components-list">
          <div 
            v-for="(components, category) in getFilteredComponents()" 
            :key="category" 
            class="category-group"
          >
            <!-- Category 标题 -->
            <div class="category-header">
              <icon-folder />
              {{ category || 'Uncategorized' }}
            </div>
            
            <!-- Components -->
            <div
              v-for="(component, compIndex) in components"
              :key="component.id"
              class="component-item"
              :draggable="true"
              @dragstart="(e: DragEvent) => handleDragStart(e, category, compIndex, component)"
              @dragover.prevent
              @drop="(e: DragEvent) => handleDrop(e, category, compIndex)"
            >
              <a-checkbox
                :model-value="selectedComponents[component.id]"
                @change="(checked: boolean | (string | boolean | number)[]) => handleComponentCheckChange(component.id, checked as boolean)"
              >
                <span class="component-name">
                  <icon-drag-dot class="drag-handle" />
                  {{ component.componentName }}
                </span>
              </a-checkbox>
              
              <!-- Test Cases -->
              <div v-if="testCases[component.id]?.length > 0" class="test-cases-sublist">
                <div
                  v-for="(testCase, caseIndex) in testCases[component.id]"
                  :key="testCase.id"
                  class="test-case-item"
                  :draggable="true"
                  @dragstart="(e: DragEvent) => handleCaseDragStart(e, component.id, caseIndex, testCase)"
                  @dragover.prevent
                  @drop="(e: DragEvent) => handleCaseDrop(e, component.id, caseIndex)"
                >
                  <a-checkbox
                    :model-value="selectedCases[testCase.id]"
                    @change="(checked: boolean | (string | boolean | number)[]) => handleCaseCheckChange(component, testCase, checked as boolean)"
                  >
                    <span class="test-case-name">
                      <icon-drag-dot class="drag-handle" />
                      {{ testCase.caseName }}
                    </span>
                  </a-checkbox>
                </div>
              </div>
            </div>
          </div>
        </div>
        
        <!-- 搜索所有 test cases（树形选择 + 搜索）-->
        <div class="search-all-cases" style="margin-top: 16px;">
          <a-alert type="info" style="margin-bottom: 12px;">
            Search and add test cases from database
          </a-alert>
          
          <a-tree-select
            v-model="searchSelectedCase"
            :data="searchTreeData"
            :loading="searchLoading"
            placeholder="Click to select or type to search test cases..."
            allow-search
            allow-clear
            :filter-tree-node="(searchValue: string, nodeData: any) => {
              if (!searchValue) return true
              const lowerSearch = searchValue.toLowerCase()
              return nodeData.title?.toLowerCase().includes(lowerSearch) || 
                     nodeData.label?.toLowerCase().includes(lowerSearch)
            }"
            @change="(value: string) => handleTreeSelectChange(value)"
            @search="(value: string) => handleSearchWithDebounce(value)"
            @dropdown-visible-change="(visible: boolean) => handleDropdownVisibleChange(visible)"
          >
            <template #prefix>
              <icon-search />
            </template>
          </a-tree-select>
          
          <!-- 显示已添加的搜索 cases -->
          <div v-if="addedSearchCases.length > 0" class="added-search-cases">
            <div class="added-cases-title">Added from search:</div>
            <div class="added-cases-list">
              <a-tag
                v-for="testCase in addedSearchCases"
                :key="testCase.id"
                color="arcoblue"
                closable
                @close="handleRemoveAddedSearchCase(testCase.id)"
              >
                <template #icon>
                  <icon-plus />
                </template>
                {{ testCase.caseName }}
                <span style="opacity: 0.7; margin-left: 4px; font-size: 12px;">
                  ({{ testCase.category }})
                </span>
              </a-tag>
            </div>
          </div>
        </div>
        
        <!-- 搜索框（原有的搜索功能）-->
        <a-input-search
          v-model="searchKeyword"
          placeholder="Search test components or test cases..."
          allow-clear
          style="margin-top: 12px;"
          @search="handleSearch"
          @clear="handleSearch"
        >
          <template #prefix>
            <icon-search />
          </template>
        </a-input-search>
      </div>
    </a-form-item>

    <!-- Test Case Execution Order (拖拽排序) -->
    <a-form-item 
      v-if="localConfig.testTypeId && localConfig.orderedTestCases.length > 0" 
      label="Test Case Execution Order"
    >
      <div class="execution-order-container">
        <a-alert type="info" style="margin-bottom: 12px;">
          Drag test cases to reorder their execution sequence
        </a-alert>
        
        <VueDraggable
          v-model="localConfig.orderedTestCases"
          :animation="200"
          handle=".drag-handle"
          ghostClass="ghost"
          class="execution-order-list"
          @end="emitUpdate"
        >
          <div
            v-for="(testCase, index) in localConfig.orderedTestCases"
            :key="testCase.id"
            class="execution-order-item"
          >
            <div class="order-number">{{ index + 1 }}</div>
            <icon-drag-dot class="drag-handle" />
            <div class="case-info">
              <div class="case-name">{{ testCase.caseName }}</div>
              <div class="case-meta">
                <span class="category-badge">{{ testCase.category }}</span>
                <span class="component-badge">{{ testCase.componentName }}</span>
              </div>
            </div>
            <a-button
              type="text"
              size="small"
              status="danger"
              @click="removeCaseFromOrder(testCase.id)"
            >
              <template #icon>
                <icon-close />
              </template>
            </a-button>
          </div>
        </VueDraggable>
      </div>
    </a-form-item>
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, watch, onMounted, computed } from 'vue'
import { VueDraggable } from 'vue-draggable-plus'
import { getOsOptions, getOsKernels } from '@/apis/osConfig'
import { getTestTypeOptions, getTestComponents, getTestCases } from '@/apis/testType'
import type { TestComponent, TestCase } from '@/apis/testType'
import { searchTestCases } from '@/apis/testCase'
import type { TestCase as SearchTestCase } from '@/apis/testCase'
import { Message } from '@arco-design/web-vue'
import type { MachineConfiguration } from '../types'

defineOptions({ name: 'ConfigurationForm' })

const props = defineProps<{
  config: MachineConfiguration
  machineId?: number
}>()

// const emit = defineEmits<{
//   'update': [config: MachineConfiguration]
// }>()

const emit = defineEmits<{
  'update': [config: MachineConfiguration]
  'loading-change': [loading: boolean]
}>()



const localConfig = reactive<MachineConfiguration>({ ...props.config })
const osOptions = ref<Array<{label: string, value: string, osFamily?: string, version?: string}>>([])
const kernelOptions = ref<Array<{label: string, value: string}>>([])
const testTypeOptions = ref<Array<{label: string, value: string}>>([])

// Components 数据
const componentsByCategory = ref<Record<string, TestComponent[]>>({})
const testCases = ref<Record<number, TestCase[]>>({})

// 选中状态
const selectedComponents = ref<Record<number, boolean>>({})
const selectedCases = ref<Record<number, boolean>>({})

// 搜索
const searchKeyword = ref('')
const searchSelectedCase = ref<string>('')
const searchTreeData = ref<any[]>([])
const searchLoading = ref(false)
const addedSearchCases = ref<any[]>([])
let searchDebounceTimer: any = null
const testComponentsLoading = ref(false)
// 监听 testComponentsLoading 变化，通知父组件
watch(testComponentsLoading, (newVal) => {
  emit('loading-change', newVal)
})
const allTestCasesCache = ref<SearchTestCase[]>([])

// Loading 状态
const osLoading = ref(false)
const kernelLoading = ref(false)
const testTypeLoading = ref(false)


// Drag & Drop state
let draggedItem: any = null

// 防止循环加载的标志位
let isInitialLoad = true
let isLoadingFromProps = false

// 加载选项
onMounted(async () => {
  await loadOsOptions()
  await loadTestTypeOptions()
  
  if (localConfig.osId) {
    await loadKernels(localConfig.osId)
  }
  
  if (localConfig.testTypeId) {
    await loadTestComponents(localConfig.testTypeId)
  }
  
  // 初始化选中状态
  syncSelectedStates()
})

// 同步选中状态
function syncSelectedStates() {
  selectedComponents.value = {}
  selectedCases.value = {}
  
  for (const comp of localConfig.testComponents || []) {
    selectedComponents.value[comp.id] = true
  }
  
  for (const testCase of localConfig.orderedTestCases || []) {
    selectedCases.value[testCase.id] = true
  }
}

// 加载 OS 选项
async function loadOsOptions() {
  osLoading.value = true
  try {
    const configs = await getOsOptions()
    osOptions.value = configs.map(c => ({
      label: c.label,
      value: String(c.id),
      osFamily: c.osFamily,
      version: c.version
    }))
  } catch (error) {
    console.error('[ConfigurationForm] 加载 OS 选项失败:', error)
    Message.error('Failed to load OS options')
  } finally {
    osLoading.value = false
  }
}

// 加载 Test Type 选项
async function loadTestTypeOptions() {
  testTypeLoading.value = true
  try {
    const options = await getTestTypeOptions()
    testTypeOptions.value = options
  } catch (error) {
    console.error('[ConfigurationForm] 加载 Test Type 失败:', error)
    Message.error('Failed to load Test Types')
  } finally {
    testTypeLoading.value = false
  }
}

// OS 变化
async function handleOsChange(osId: string) {
  const selectedOs = osOptions.value.find(o => o.value === osId)
  if (selectedOs) {
    localConfig.osFamily = selectedOs.osFamily || ''
    localConfig.osVersion = selectedOs.version || ''
  }
  
  localConfig.kernelVersion = ''
  await loadKernels(osId)
  emitUpdate()
}

// 加载 Kernel
async function loadKernels(osId: string) {
  kernelLoading.value = true
  try {
    kernelOptions.value = await getOsKernels(Number(osId))
  } catch (error) {
    console.error('[ConfigurationForm] 加载 Kernel 失败:', error)
    Message.error('Failed to load kernels')
  } finally {
    kernelLoading.value = false
  }
}

// Test Type 变化
async function handleTestTypeChange(testTypeId: string) {
  const selectedType = testTypeOptions.value.find(t => t.value === testTypeId)
  if (selectedType) {
    localConfig.testTypeName = selectedType.label
  }
  
  // 重置
  localConfig.testComponents = []
  localConfig.orderedTestCases = []
  componentsByCategory.value = {}
  testCases.value = {}
  selectedComponents.value = {}
  selectedCases.value = {}
  
  await loadTestComponents(testTypeId)
  emitUpdate()
}

// 加载 Test Components
async function loadTestComponents(testTypeId: string) {
  testComponentsLoading.value = true
  try {
    const components = await getTestComponents(parseInt(testTypeId))
    
    // 按 category 分组
    const categoryMap = new Map<string, TestComponent[]>()
    
    for (const comp of components) {
      const category = comp.componentCategory || 'Uncategorized'
      if (!categoryMap.has(category)) {
        categoryMap.set(category, [])
      }
      categoryMap.get(category)!.push(comp)
      
      // 加载 test cases
      try {
        const cases = await getTestCases(comp.id)
        testCases.value[comp.id] = cases
        
        // 🆕 默认勾选所有 components 和 cases
        selectedComponents.value[comp.id] = true
        localConfig.testComponents.push(comp)
        
        // 默认勾选所有 cases（检查是否已存在，避免重复添加）
        for (const testCase of cases) {
          selectedCases.value[testCase.id] = true
          // 检查是否已经存在，避免重复添加
          if (!localConfig.orderedTestCases.some((c: any) => c.id === testCase.id)) {
            localConfig.orderedTestCases.push({
              ...testCase,
              category: comp.componentCategory || 'Uncategorized',
              componentName: comp.componentName
            } as any)
          }
        }
      } catch (error) {
        console.error(`[ConfigurationForm] 加载 Component ${comp.id} 的 Cases 失败:`, error)
      }
    }
    
    // 转换为对象
    componentsByCategory.value = Object.fromEntries(categoryMap)
    
    // 触发更新以保存默认选中状态
    emitUpdate()
  } catch (error) {
    console.error('[ConfigurationForm] 加载 Test Components 失败:', error)
    Message.error('Failed to load test components')
  } finally {
    testComponentsLoading.value = false
  }
}

// 过滤组件（搜索）
function getFilteredComponents() {
  if (!searchKeyword.value) {
    return componentsByCategory.value
  }
  
  const keyword = searchKeyword.value.toLowerCase()
  const filtered: Record<string, TestComponent[]> = {}
  
  for (const [category, comps] of Object.entries(componentsByCategory.value)) {
    const components = comps as TestComponent[]
    const matchedComps = components.filter(comp => 
      comp.componentName.toLowerCase().includes(keyword) ||
      testCases.value[comp.id]?.some(tc => tc.caseName.toLowerCase().includes(keyword))
    )
    
    if (matchedComps.length > 0) {
      filtered[category] = matchedComps
    }
  }
  
  return filtered
}

// 搜索处理
function handleSearch() {
  // 触发重新渲染过滤结果
}

// Component checkbox 变化
function handleComponentCheckChange(componentId: number, checked: boolean) {
  selectedComponents.value[componentId] = checked
  
  // 找到 component
  let component: TestComponent | undefined
  for (const comps of Object.values(componentsByCategory.value)) {
    component = comps.find(c => c.id === componentId)
    if (component) break
  }
  
  if (!component) return
  
  if (checked) {
    // 添加 component
    if (!localConfig.testComponents.some((c: any) => c.id === componentId)) {
      localConfig.testComponents.push(component)
    }
    
    // 添加所有 test cases
    const cases = testCases.value[componentId] || []
    for (const testCase of cases) {
      selectedCases.value[testCase.id] = true
      if (!localConfig.orderedTestCases.some((c: any) => c.id === testCase.id)) {
        localConfig.orderedTestCases.push({
          ...testCase,
          category: component.componentCategory || 'Uncategorized',
          componentName: component.componentName
        } as any)
      }
    }
  } else {
    // 移除 component
    localConfig.testComponents = localConfig.testComponents.filter((c: any) => c.id !== componentId)
    
    // 移除所有 test cases
    const caseIds = (testCases.value[componentId] || []).map(c => c.id)
    for (const caseId of caseIds) {
      selectedCases.value[caseId] = false
    }
    localConfig.orderedTestCases = localConfig.orderedTestCases.filter((c: any) => !caseIds.includes(c.id))
  }
  
  emitUpdate()
}

// Case checkbox 变化
function handleCaseCheckChange(component: TestComponent, testCase: TestCase, checked: boolean) {
  selectedCases.value[testCase.id] = checked
  
  if (checked) {
    // 添加 case
    if (!localConfig.orderedTestCases.some((c: any) => c.id === testCase.id)) {
      localConfig.orderedTestCases.push({
        ...testCase,
        category: component.componentCategory || 'Uncategorized',
        componentName: component.componentName
      } as any)
    }
    
    // 确保 component 也被选中
    if (!selectedComponents.value[component.id]) {
      selectedComponents.value[component.id] = true
      if (!localConfig.testComponents.some((c: any) => c.id === component.id)) {
        localConfig.testComponents.push(component)
      }
    }
  } else {
    // 移除 case
    localConfig.orderedTestCases = localConfig.orderedTestCases.filter((c: any) => c.id !== testCase.id)
    
    // 检查是否还有该 component 的其他 case
    const hasOtherCases = (testCases.value[component.id] || []).some(c => 
      c.id !== testCase.id && selectedCases.value[c.id]
    )
    
    // 如果没有其他 case，移除 component
    if (!hasOtherCases) {
      selectedComponents.value[component.id] = false
      localConfig.testComponents = localConfig.testComponents.filter((c: any) => c.id !== component.id)
    }
  }
  
  emitUpdate()
}

// 从执行列表移除
function removeCaseFromOrder(caseId: number) {
  localConfig.orderedTestCases = localConfig.orderedTestCases.filter((c: any) => c.id !== caseId)
  selectedCases.value[caseId] = false
  emitUpdate()
}

// Drag & Drop handlers for components
function handleDragStart(e: DragEvent, category: string, index: number, component: TestComponent) {
  draggedItem = { type: 'component', category, index, data: component }
  if (e.dataTransfer) {
    e.dataTransfer.effectAllowed = 'move'
  }
}

function handleDrop(e: DragEvent, category: string, index: number) {
  if (!draggedItem || draggedItem.type !== 'component') return
  
  if (draggedItem.category === category && draggedItem.index !== index) {
    const items = [...componentsByCategory.value[category]]
    const [removed] = items.splice(draggedItem.index, 1)
    items.splice(index, 0, removed)
    componentsByCategory.value[category] = items
  }
  
  draggedItem = null
}

// Drag & Drop handlers for cases
function handleCaseDragStart(e: DragEvent, componentId: number, index: number, testCase: TestCase) {
  draggedItem = { type: 'case', componentId, index, data: testCase }
  if (e.dataTransfer) {
    e.dataTransfer.effectAllowed = 'move'
  }
}

function handleCaseDrop(e: DragEvent, componentId: number, index: number) {
  if (!draggedItem || draggedItem.type !== 'case' || draggedItem.componentId !== componentId) return
  
  const items = [...testCases.value[componentId]]
  const [removed] = items.splice(draggedItem.index, 1)
  items.splice(index, 0, removed)
  testCases.value[componentId] = items
  
  draggedItem = null
}

// 树形选择器处理
async function handleDropdownVisibleChange(visible: boolean) {
  if (visible && allTestCasesCache.value.length === 0) {
    await loadAllTestCases()
  }
}

async function loadAllTestCases() {
  searchLoading.value = true
  try {
    const cases = await searchTestCases('')
    allTestCasesCache.value = cases
    buildTreeData(cases)
  } catch (error) {
    console.error('[ConfigurationForm] 加载所有 test cases 失败:', error)
  } finally {
    searchLoading.value = false
  }
}

function buildTreeData(cases: SearchTestCase[]) {
  const tree: any[] = []
  const categoryMap = new Map<string, Map<string, SearchTestCase[]>>()
  
  for (const testCase of cases) {
    const category = testCase.category || 'Uncategorized'
    const component = testCase.componentName || 'Unknown'
    
    if (!categoryMap.has(category)) {
      categoryMap.set(category, new Map())
    }
    const compMap = categoryMap.get(category)!
    
    if (!compMap.has(component)) {
      compMap.set(component, [])
    }
    compMap.get(component)!.push(testCase)
  }
  
  for (const [category, compMap] of categoryMap) {
    const categoryNode: any = {
      key: `category-${category}`,
      title: category,
      selectable: false,
      children: []
    }
    
    for (const [component, cases] of compMap) {
      const compNode: any = {
        key: `component-${component}`,
        title: component,
        selectable: false,
        children: []
      }
      
      for (const testCase of cases) {
        compNode.children.push({
          key: `case-${testCase.id}`,
          title: testCase.caseName,
          value: String(testCase.id),
          selectable: true,
          isLeaf: true,
          data: testCase
        })
      }
      
      categoryNode.children.push(compNode)
    }
    
    tree.push(categoryNode)
  }
  
  searchTreeData.value = tree
}

function handleSearchWithDebounce(value: string) {
  clearTimeout(searchDebounceTimer)
  searchDebounceTimer = setTimeout(async () => {
    if (value && value.trim()) {
      searchLoading.value = true
      try {
        const cases = await searchTestCases(value)
        buildTreeData(cases)
      } catch (error) {
        console.error('[ConfigurationForm] 搜索失败:', error)
      } finally {
        searchLoading.value = false
      }
    } else if (allTestCasesCache.value.length > 0) {
      buildTreeData(allTestCasesCache.value)
    }
  }, 2000)
}

function handleTreeSelectChange(value: string) {
  if (!value) return
  
  // 找到选中的 test case
  const caseId = parseInt(value)
  const testCase = allTestCasesCache.value.find(c => c.id === caseId)
  
  if (!testCase) return
  
  // 检查是否已添加
  if (localConfig.orderedTestCases.some(c => c.id === caseId)) {
    Message.warning('This test case is already added')
    searchSelectedCase.value = ''
    return
  }
  
  // 添加到执行列表
  localConfig.orderedTestCases.push({
    id: testCase.id,
    caseName: testCase.caseName,
    category: testCase.category || 'Uncategorized',
    componentName: testCase.componentName || 'Unknown'
  } as any)
  
  selectedCases.value[caseId] = true
  
  // 添加到搜索列表
  addedSearchCases.value.push({
    id: testCase.id,
    caseName: testCase.caseName,
    category: testCase.category || 'Uncategorized'
  })
  
  searchSelectedCase.value = ''
  emitUpdate()
}

function handleRemoveAddedSearchCase(caseId: number) {
  addedSearchCases.value = addedSearchCases.value.filter(c => c.id !== caseId)
  localConfig.orderedTestCases = localConfig.orderedTestCases.filter(c => c.id !== caseId)
  selectedCases.value[caseId] = false
  emitUpdate()
}

// 创建 Test Type
function handleCreateTestType() {
  Message.info('Please create test type in the system management')
}

// 触发更新
function emitUpdate() {
  // 如果正在从 props 加载数据，不触发更新（避免循环）
  if (isLoadingFromProps) {
    console.log('[ConfigurationForm] 正在从 props 加载，跳过 emit update')
    return
  }
  emit('update', { ...localConfig })
}

// 监听 props 变化
watch(() => props.config, async (newConfig, oldConfig) => {
  Object.assign(localConfig, newConfig)
  syncSelectedStates()
  
  // 如果 osId 变化了，重新加载 kernel options
  if (newConfig.osId && newConfig.osId !== oldConfig?.osId) {
    await loadKernels(newConfig.osId)
  }
  
  // 如果 testTypeId 变化了，重新加载 test components
  if (newConfig.testTypeId && newConfig.testTypeId !== oldConfig?.testTypeId) {
    await loadTestComponents(newConfig.testTypeId)
  }
}, { deep: true })

// 监听 osId 变化（用于处理用户手动选择 OS 的情况）
watch(() => localConfig.osId, async (newOsId, oldOsId) => {
  // 如果 osId 有值（不管是初始化还是变化），都加载 kernel options
  if (newOsId) {
    // 如果 osId 变化了，或者 kernel options 为空，则加载
    if (newOsId !== oldOsId || kernelOptions.value.length === 0) {
      console.log('[ConfigurationForm] Loading kernels for osId:', newOsId)
      await loadKernels(newOsId)
    }
  } else {
    // 如果 osId 被清空，清空 kernel options
    kernelOptions.value = []
    localConfig.kernelVersion = ''
  }
}, { immediate: true })  // immediate: true 确保初始化时也会执行

// 监听 props.config 的关键字段变化（支持编辑模式数据加载）
// 只监听 configId 变化来判断是否是新的配置对象（避免循环触发）
watch(() => props.config.configId, async (newConfigId, oldConfigId) => {
  // 只在 configId 变化或首次加载时执行
  if (newConfigId !== oldConfigId || isInitialLoad) {
    console.log('[ConfigurationForm] configId 变化，重新加载配置:', newConfigId)
    isInitialLoad = false
    isLoadingFromProps = true  // 设置标志位
    
    const newConfig = props.config
    const oldTestTypeId = localConfig.testTypeId
    
    // 更新 localConfig
    Object.assign(localConfig, newConfig)
    
    // 重新加载相关选项
    if (newConfig.osId) {
      await loadKernels(newConfig.osId)
    }
    
    // 只有当 testTypeId 真正变化时才重新加载 test components
    // 如果已有数据（编辑模式），不重新加载，避免覆盖
    if (newConfig.testTypeId && newConfig.testTypeId !== oldTestTypeId) {
      // 检查是否已经有 test components 数据（编辑模式）
      if (!newConfig.testComponents || newConfig.testComponents.length === 0) {
        // 没有数据，需要加载
        await loadTestComponents(newConfig.testTypeId)
      } else {
        // 已有数据（编辑模式），只需要加载选项，不调用 loadTestComponents
        console.log('[ConfigurationForm] 编辑模式：跳过 loadTestComponents，直接同步选中状态')
        try {
          const components = await getTestComponents(parseInt(newConfig.testTypeId))
          // 只加载 components 和 cases 结构，不修改选中状态
          const categoryMap = new Map<string, TestComponent[]>()
          for (const comp of components) {
            const category = comp.componentCategory || 'Uncategorized'
            if (!categoryMap.has(category)) {
              categoryMap.set(category, [])
            }
            categoryMap.get(category)!.push(comp)
            
            // 加载 test cases（但不修改选中状态）
            try {
              const cases = await getTestCases(comp.id)
              testCases.value[comp.id] = cases
            } catch (error) {
              console.error(`[ConfigurationForm] 加载 Component ${comp.id} 的 Cases 失败:`, error)
            }
          }
          componentsByCategory.value = Object.fromEntries(categoryMap)
        } catch (error) {
          console.error('[ConfigurationForm] 加载 test components 选项失败:', error)
        }
      }
    }
    
    // 重新同步选中状态（基于已有的 testComponents 和 orderedTestCases）
    syncSelectedStates()
    
    console.log('[ConfigurationForm] localConfig 更新完成:', localConfig)
    
    // 重置标志位
    setTimeout(() => {
      isLoadingFromProps = false
    }, 100)
  }
}, { immediate: false })  // 不使用 immediate，因为 onMounted 已经处理了初始化
</script>

<style scoped lang="scss">
.configuration-form {
  .test-type-selector {
    display: flex;
    align-items: center;
    gap: 12px;
    
    .create-test-type-link {
      flex-shrink: 0;
      white-space: nowrap;
      font-size: 13px;
    }
  }
  
  .loading-container {
    display: flex;
    justify-content: center;
    padding: 40px 0;
  }
  
  .test-components-container {
    .components-list {
      .category-group {
        margin-bottom: 20px;
        
        .category-header {
          display: flex;
          align-items: center;
          gap: 8px;
          font-weight: 600;
          font-size: 14px;
          color: #1d2129;
          margin-bottom: 12px;
          padding: 8px 12px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          border-radius: 4px;
        }
        
        .component-item {
          margin-bottom: 8px;
          padding: 8px 12px;
          background: #f7f8fa;
          border-radius: 4px;
          cursor: move;
          transition: all 0.2s;
          
          &:hover {
            background: #e5e6eb;
          }
          
          .component-name {
            display: flex;
            align-items: center;
            gap: 8px;
            font-weight: 500;
            
            .drag-handle {
              cursor: move;
              color: #86909c;
            }
          }
          
          .test-cases-sublist {
            margin-top: 8px;
            margin-left: 24px;
            display: flex;
            flex-direction: column;
            gap: 6px;
            
            .test-case-item {
              padding: 6px 8px;
              background: white;
              border-radius: 3px;
              border: 1px solid #e5e6eb;
              cursor: move;
              transition: all 0.2s;
              
              &:hover {
                border-color: #165dff;
                box-shadow: 0 2px 4px rgba(22, 93, 255, 0.1);
              }
              
              .test-case-name {
                display: flex;
                align-items: center;
                gap: 6px;
                font-size: 13px;
                
                .drag-handle {
                  cursor: move;
                  color: #86909c;
                  font-size: 12px;
                }
              }
            }
          }
        }
      }
    }
    
    .search-all-cases {
      .added-search-cases {
        margin-top: 12px;
        
        .added-cases-title {
          font-size: 13px;
          color: #4e5969;
          margin-bottom: 8px;
        }
        
        .added-cases-list {
          display: flex;
          flex-wrap: wrap;
          gap: 8px;
        }
      }
    }
  }
  
  .execution-order-container {
    .execution-order-list {
      display: flex;
      flex-direction: column;
      gap: 8px;
      
      .execution-order-item {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px;
        background: #f7f8fa;
        border-radius: 4px;
        border: 1px solid #e5e6eb;
        transition: all 0.2s;
        cursor: move;
        
        &:hover {
          background: #ffffff;
          border-color: #165dff;
          box-shadow: 0 2px 8px rgba(22, 93, 255, 0.1);
        }
        
        .order-number {
          display: flex;
          align-items: center;
          justify-content: center;
          width: 28px;
          height: 28px;
          background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
          color: white;
          border-radius: 50%;
          font-weight: 600;
          font-size: 14px;
          flex-shrink: 0;
        }
        
        .drag-handle {
          cursor: move;
          color: #86909c;
          flex-shrink: 0;
        }
        
        .case-info {
          flex: 1;
          min-width: 0;
          
          .case-name {
            font-weight: 500;
            color: #1d2129;
            margin-bottom: 4px;
          }
          
          .case-meta {
            display: flex;
            gap: 8px;
            font-size: 12px;
            
            .category-badge, .component-badge {
              padding: 2px 8px;
              border-radius: 3px;
              background: #e8f3ff;
              color: #165dff;
            }
            
            .component-badge {
              background: #f2f3f5;
              color: #4e5969;
            }
          }
        }
      }
      
      .ghost {
        opacity: 0.5;
        background: #e8f3ff;
      }
    }
  }
}
</style>
