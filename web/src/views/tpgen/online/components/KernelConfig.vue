<template>
  <a-card class="form-section" :bordered="false">
    <template #title>
      <div class="section-title">
        <icon-code />
        Kernel Configuration
      </div>
    </template>

    <a-form-item label="Kernel Configuration Method">
      <a-radio-group v-model="localConfigMethod" @change="handleUpdate">
        <a-radio value="individual">Individual kernel configuration</a-radio>
        <a-radio value="same">Same kernel for all machines</a-radio>
      </a-radio-group>
    </a-form-item>

    <!-- 统一配置 -->
    <template v-if="localConfigMethod === 'same'">
      <a-row :gutter="16">
        <a-col :span="24">
          <a-form-item label="Kernel Version">
            <a-select
              v-model="localKernelType"
              placeholder="Select kernel type"
              :loading="kernelTypeLoading"
              @change="handleUpdate"
            >
              <a-option v-for="option in kernelTypeOptions" :key="option.value" :value="option.value">
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
            <a-col :span="24">
              <a-form-item label="Kernel Version">
                <a-select
                  v-model="localIndividualConfig[machineId].type"
                  placeholder="Select kernel type"
                  :loading="kernelTypeLoading"
                  @change="handleUpdate"
                >
                  <a-option v-for="option in kernelTypeOptions" :key="option.value" :value="option.value">
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

  <!-- Test Type 模块 -->
  <a-card class="form-section" :bordered="false" style="margin-top: 25px;">
    <template #title>
      <div class="section-title">
        <icon-check-circle />
        Test Type Configuration
      </div>
    </template>

    <a-form-item label="Test Type Configuration Method">
      <a-radio-group v-model="localTestTypeConfigMethod" @change="handleUpdate">
        <a-radio value="individual">Individual test type configuration</a-radio>
        <a-radio value="same">Same test type for all machines</a-radio>
      </a-radio-group>
    </a-form-item>

    <!-- 统一配置 -->
    <template v-if="localTestTypeConfigMethod === 'same'">
      <a-form-item label="Test Type">
        <div class="test-type-selector">
                <a-select
            v-model="localTestType"
            placeholder="Select Test Type"
            :loading="testTypeLoading"
            @change="handleTestTypeChange"
            style="flex: 1;"
          >
            <a-option v-for="option in testTypeOptions" :key="option.value" :value="option.value">
                    {{ option.label }}
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

      <!-- 显示选中的 Test Components (平铺列表) -->
      <a-form-item v-else-if="Object.keys(sharedComponentsByCategory).length > 0" label="Test Components">
        <div class="test-components-container">
          <!-- Test Components 列表 -->
          <div class="components-list">
            <div v-for="(components, category) in getFilteredSharedComponents()" :key="category" class="category-group">
              <!-- Category 标题 -->
              <div class="category-header">{{ category || 'Uncategorized' }}</div>
              
              <!-- Components -->
              <div
                v-for="(component, compIndex) in components"
                :key="component.id"
                class="component-item"
                :draggable="true"
                @dragstart="(e) => handleDragStart(e, 'shared', category, compIndex, component)"
                @dragover.prevent
                @drop="(e) => handleDrop(e, 'shared', category, compIndex)"
              >
                <a-checkbox
                  v-model="sharedSelectedComponents[component.id]"
                  @change="(checked) => handleComponentCheckChange(component.id, checked, 'shared')"
                >
                  <span class="component-name">
                    <icon-drag-dot class="drag-handle" />
                    {{ component.componentName }}
                  </span>
                </a-checkbox>
                
                <!-- Test Cases -->
                <div v-if="sharedTestCases[component.id]?.length > 0" class="test-cases-sublist">
                  <div
                    v-for="(testCase, caseIndex) in sharedTestCases[component.id]"
                    :key="testCase.id"
                    class="test-case-item"
                    :draggable="true"
                    @dragstart="(e) => handleDragStart(e, 'shared-case', component.id, caseIndex, testCase)"
                    @dragover.prevent
                    @drop="(e) => handleDrop(e, 'shared-case', component.id, caseIndex)"
                  >
                    <a-checkbox
                      v-model="sharedSelectedCases[testCase.id]"
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
          
          <!-- 搜索框移到下面 -->
          <a-input-search
            v-model="sharedSearchKeyword"
            placeholder="Search test components or test cases..."
            allow-clear
            style="margin-top: 12px;"
            @search="handleSharedSearch"
            @clear="handleSharedSearch"
          >
            <template #prefix>
              <icon-search />
            </template>
          </a-input-search>
        </div>
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

          <a-form-item label="Test Type">
            <div class="test-type-selector">
              <a-select
                v-model="localIndividualTestTypeConfig[machineId].testType"
                placeholder="Select test type"
                :loading="testTypeLoading"
                @change="() => handleMachineTestTypeChange(machineId)"
                style="flex: 1;"
              >
                <a-option v-for="option in testTypeOptions" :key="option.value" :value="option.value">
                  {{ option.label }}
                </a-option>
              </a-select>
              <a-link href="#" class="create-test-type-link" @click.prevent="handleCreateTestType">
                <icon-plus /> Click here to create your test type
              </a-link>
            </div>
          </a-form-item>

          <!-- 显示该机器选中的 Test Components (平铺列表) -->
          <a-form-item 
            v-if="localIndividualTestTypeConfig[machineId].testType && machineComponentsByCategory[machineId] && Object.keys(machineComponentsByCategory[machineId]).length > 0" 
            label="Test Components"
          >
            <div class="test-components-container">
              <!-- Test Components 列表 -->
              <div class="components-list">
                <div v-for="(components, category) in getFilteredMachineComponentsByCategory(machineId)" :key="category" class="category-group">
                  <!-- Category 标题 -->
                  <div class="category-header">{{ category || 'Uncategorized' }}</div>
                  
                  <!-- Components -->
                  <div
                    v-for="(component, compIndex) in components"
                    :key="component.id"
                    class="component-item"
                    :draggable="true"
                    @dragstart="(e) => handleDragStart(e, 'machine', { machineId, category }, compIndex, component)"
                    @dragover.prevent
                    @drop="(e) => handleDrop(e, 'machine', { machineId, category }, compIndex)"
                  >
                    <a-checkbox
                      v-model="machineSelectedComponents[machineId][component.id]"
                      @change="(checked) => handleComponentCheckChange(component.id, checked, 'machine', machineId)"
                    >
                      <span class="component-name">
                        <icon-drag-dot class="drag-handle" />
                        {{ component.componentName }}
                      </span>
                    </a-checkbox>
                    
                    <!-- Test Cases -->
                    <div v-if="machineTestCases[machineId]?.[component.id]?.length > 0" class="test-cases-sublist">
                      <div
                        v-for="(testCase, caseIndex) in machineTestCases[machineId][component.id]"
                        :key="testCase.id"
                        class="test-case-item"
                        :draggable="true"
                        @dragstart="(e) => handleDragStart(e, 'machine-case', { machineId, componentId: component.id }, caseIndex, testCase)"
                        @dragover.prevent
                        @drop="(e) => handleDrop(e, 'machine-case', { machineId, componentId: component.id }, caseIndex)"
                      >
                        <a-checkbox
                          v-model="machineSelectedCases[machineId][testCase.id]"
                          @change="() => handleMachineTestCaseCheckChange(machineId, testCase.id)"
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
              
              <!-- 搜索所有 test cases（新功能：树形选择 + 搜索）-->
              <div class="search-all-cases" style="margin-top: 16px;">
                <a-alert type="info" style="margin-bottom: 12px;">
                  Search and add test cases from database
                </a-alert>
                
                <a-tree-select
                  v-model="machineSearchSelectedCase[machineId]"
                  :data="machineSearchTreeData[machineId] || []"
                  :loading="machineSearchLoading[machineId]"
                  placeholder="Click to select or type to search test cases..."
                  allow-search
                  allow-clear
                  :filter-tree-node="(searchValue: string, nodeData: any) => {
                    if (!searchValue) return true
                    const lowerSearch = searchValue.toLowerCase()
                    return nodeData.title?.toLowerCase().includes(lowerSearch) || 
                           nodeData.label?.toLowerCase().includes(lowerSearch)
                  }"
                  @change="(value: string) => handleTreeSelectChange(machineId, value)"
                  @search="(value: string) => handleSearchWithDebounce(machineId, value)"
                  @dropdown-visible-change="(visible: boolean) => handleDropdownVisibleChange(machineId, visible)"
                >
                  <template #prefix>
                    <icon-search />
                  </template>
                </a-tree-select>
                
                <!-- 显示已添加的搜索 cases -->
                <div v-if="machineAddedSearchCases[machineId]?.length > 0" class="added-search-cases">
                  <div class="added-cases-title">Added from search:</div>
                  <div class="added-cases-list">
                    <a-tag
                      v-for="testCase in machineAddedSearchCases[machineId]"
                      :key="testCase.id"
                      color="arcoblue"
                      closable
                      @close="handleRemoveAddedSearchCase(machineId, testCase.id)"
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
            </div>
          </a-form-item>

          <!-- Test Case Execution Order (拖拽排序) -->
          <a-form-item 
            v-if="localIndividualTestTypeConfig[machineId].testType && machineOrderedTestCases[machineId]?.length > 0" 
            label="Test Case Execution Order"
          >
            <div class="execution-order-container">
              <a-alert type="info" style="margin-bottom: 12px;">
                Drag test cases to reorder their execution sequence
              </a-alert>
              
              <VueDraggable
                v-model="machineOrderedTestCases[machineId]"
                :animation="200"
                handle=".drag-handle"
                ghostClass="ghost"
                class="execution-order-list"
                @end="handleUpdate"
              >
                <div
                  v-for="(testCase, index) in machineOrderedTestCases[machineId]"
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
                </div>
              </VueDraggable>
            </div>
          </a-form-item>
        </a-card>
      </div>
    </template>
  </a-card>
</template>

<script setup lang="ts">
import { computed, watch, ref, onMounted } from 'vue'
import { getAllKernelTypes } from '@/apis/osConfig'
import { getTestTypeOptions, getTestComponents, getTestCases, type TestComponent, type TestCase } from '@/apis/testType'
import { searchTestCases, type TestCase as SearchTestCase } from '@/apis/testCase'
import { Message } from '@arco-design/web-vue'
import { IconPlus, IconSearch, IconDragDot, IconClose } from '@arco-design/web-vue/es/icon'
import { VueDraggable } from 'vue-draggable-plus'

defineOptions({ name: 'KernelConfig' })

const props = defineProps<{
  configMethod: 'same' | 'individual'
  kernelType?: string
  individualConfig: Record<number, { type: string; version: string }>
  selectedMachines: number[]
  testType?: string
  testTypeConfigMethod?: 'same' | 'individual'
  individualTestTypeConfig?: Record<number, { testType: string }>
  machinesMap?: Record<number, any>
}>()

const emit = defineEmits<{
  'update:configMethod': [value: 'same' | 'individual']
  'update:kernelType': [value: string]
  'update:individualConfig': [value: Record<number, { type: string; version: string }>]
  'update:testType': [value: string]
  'update:testTypeConfigMethod': [value: 'same' | 'individual']
  'update:individualTestTypeConfig': [value: Record<number, { testType: string }>]
  'update': []
}>()

// Kernel Type 选项（从 OsSupportedKernel 数据库加载）
const kernelTypeOptions = ref<Array<{label: string, value: string}>>([])
const kernelTypeLoading = ref(false)

// Test Type 选项（从 TestType 数据库加载）
const testTypeOptions = ref<Array<{label: string, value: string}>>([])
const testTypeLoading = ref(false)

// Test Components 加载状态
const testComponentsLoading = ref(false)

// 预加载的 Test Type 数据（key: testTypeId, value: {components, cases, etc}）
const preloadedTestData = ref<Record<string, {
  components: TestComponent[],
  componentsByCategory: Record<string, TestComponent[]>,
  testCases: Record<number, TestCase[]>,
  selectedComponents: Record<number, boolean>,
  selectedCases: Record<number, boolean>
}>>({})

const localConfigMethod = computed({
  get: () => props.configMethod,
  set: val => emit('update:configMethod', val),
})

const localKernelType = computed({
  get: () => props.kernelType || '',
  set: val => emit('update:kernelType', val),
})

const localIndividualConfig = computed({
  get: () => props.individualConfig,
  set: val => emit('update:individualConfig', val),
})

const localTestType = computed({
  get: () => props.testType || '',
  set: val => emit('update:testType', val),
})

const localTestTypeConfigMethod = computed({
  get: () => props.testTypeConfigMethod || 'individual',
  set: val => emit('update:testTypeConfigMethod', val),
})

const localIndividualTestTypeConfig = computed({
  get: () => props.individualTestTypeConfig || {},
  set: val => emit('update:individualTestTypeConfig', val),
})

// Test Components 数据
const sharedTestComponents = ref<TestComponent[]>([])
const machineTestComponents = ref<Record<number, TestComponent[]>>({})

// Test Components 按 Category 分组 (Same 模式)
const sharedComponentsByCategory = ref<Record<string, TestComponent[]>>({})

// Test Cases 数据 (Same 模式: componentId -> TestCase[])
const sharedTestCases = ref<Record<number, TestCase[]>>({})

// Test Components 按 Category 分组 (Individual 模式: machineId -> category -> TestComponent[])
const machineComponentsByCategory = ref<Record<number, Record<string, TestComponent[]>>>({})

// Test Cases 数据 (Individual 模式: machineId -> componentId -> TestCase[])
const machineTestCases = ref<Record<number, Record<number, TestCase[]>>>({})

// 搜索关键词（旧的，用于过滤当前 test type 的 components）
const sharedSearchKeyword = ref('')
const machineSearchKeywords = ref<Record<number, string>>({})

// 新的搜索功能：搜索所有 test cases（树形选择 + 搜索）
const machineSearchInput = ref<Record<number, string>>({})  // 输入框内容
const machineSearchResults = ref<Record<number, SearchTestCase[]>>({})  // 搜索结果
const machineSearchLoading = ref<Record<number, boolean>>({})  // 加载状态
const machineAddedSearchCases = ref<Record<number, SearchTestCase[]>>({})  // 已添加的搜索 test cases
const machineSearchTreeData = ref<Record<number, any[]>>({})  // 树形数据（category -> component -> case）
const machineSearchSelectedCase = ref<Record<number, string>>({})  // 当前选中的 case
const machineSearchDebounceTimers = ref<Record<number, any>>({})  // 防抖定时器
const machineAllTestCases = ref<Record<number, SearchTestCase[]>>({})  // 所有 test cases（缓存）

// 过滤后的数据
const filteredSharedComponentsByCategory = ref<Record<string, TestComponent[]>>({})
const filteredMachineComponentsByCategory = ref<Record<number, Record<string, TestComponent[]>>>({})

// 复选框状态 (默认全部勾选)
const sharedSelectedComponents = ref<Record<number, boolean>>({})
const sharedSelectedCases = ref<Record<number, boolean>>({})
const machineSelectedComponents = ref<Record<number, Record<number, boolean>>>({})
const machineSelectedCases = ref<Record<number, Record<number, boolean>>>({})

// Test Case 执行顺序（展平的列表，用于拖拽排序）
interface OrderedTestCase {
  id: number
  caseName: string
  componentId: number
  componentName: string
  category: string
}
const machineOrderedTestCases = ref<Record<number, OrderedTestCase[]>>({})

// 拖拽相关
const draggedItem = ref<any>(null)
const dragType = ref<string>('')
const dragContext = ref<any>(null)

// 加载 Kernel Type 选项
const loadKernelTypes = async () => {
  kernelTypeLoading.value = true
  try {
    const options = await getAllKernelTypes()
    kernelTypeOptions.value = options
  } catch (error) {
    console.error('[KernelConfig] 加载 Kernel Type 失败:', error)
    Message.error('Failed to load Kernel Types')
  } finally {
    kernelTypeLoading.value = false
  }
}

// 加载 Test Type 选项并预加载所有数据
const loadTestTypes = async () => {
  testTypeLoading.value = true
  try {
    const options = await getTestTypeOptions()
    testTypeOptions.value = options
    
    // 预加载所有 Test Types 的 Components 和 Cases
    console.log('[KernelConfig] 开始预加载所有 Test Types 的数据...')
    const preloadPromises = options.map(async (option) => {
      try {
        const testTypeId = option.value
        console.log(`[KernelConfig] 预加载 Test Type ${testTypeId}...`)
        
        // 加载 Components
        const components = await getTestComponents(parseInt(testTypeId))
        const componentsByCategory = groupComponentsByCategory(components)
        
        // 加载所有 Components 的 Test Cases
        const testCases = await loadTestCasesForComponents(components)
        
        // 初始化选中状态（默认全部选中）
        const selectedComponents: Record<number, boolean> = {}
        const selectedCases: Record<number, boolean> = {}
        
        components.forEach(comp => {
          selectedComponents[comp.id] = true
          const cases = testCases[comp.id] || []
          cases.forEach(c => {
            selectedCases[c.id] = true
          })
        })
        
        // 存储预加载的数据
        preloadedTestData.value[testTypeId] = {
          components,
          componentsByCategory,
          testCases,
          selectedComponents,
          selectedCases
        }
        
        console.log(`[KernelConfig] Test Type ${testTypeId} 预加载完成`)
      } catch (error) {
        console.error(`[KernelConfig] 预加载 Test Type ${option.value} 失败:`, error)
      }
    })
    
    await Promise.all(preloadPromises)
    console.log('[KernelConfig] 所有 Test Types 预加载完成')
  } catch (error) {
    console.error('[KernelConfig] 加载 Test Type 失败:', error)
    Message.error('Failed to load Test Types')
  } finally {
    testTypeLoading.value = false
  }
}

// 按 Category 分组 Components
const groupComponentsByCategory = (components: TestComponent[]): Record<string, TestComponent[]> => {
  const grouped: Record<string, TestComponent[]> = {}
  components.forEach(component => {
    const category = component.componentCategory || 'Uncategorized'
    if (!grouped[category]) {
      grouped[category] = []
    }
    grouped[category].push(component)
  })
  return grouped
}

// 加载 Test Cases for Components
const loadTestCasesForComponents = async (components: TestComponent[]): Promise<Record<number, TestCase[]>> => {
  const casesMap: Record<number, TestCase[]> = {}
  
  // 并行加载所有 components 的 test cases
  await Promise.all(
    components.map(async (component) => {
      try {
        const cases = await getTestCases(component.id)
        casesMap[component.id] = cases
      } catch (error) {
        console.error(`[KernelConfig] 加载 Component ${component.id} 的 Test Cases 失败:`, error)
        casesMap[component.id] = []
      }
    })
  )
  
  return casesMap
}

// 加载共享的 Test Components (Same 模式) - 从预加载数据中获取
const loadSharedTestComponents = async (testTypeId: string) => {
  if (!testTypeId) {
    sharedTestComponents.value = []
    sharedComponentsByCategory.value = {}
    sharedTestCases.value = {}
    sharedSelectedComponents.value = {}
    sharedSelectedCases.value = {}
    return
  }
  
  try {
    // 从预加载的数据中获取
    const preloadedData = preloadedTestData.value[testTypeId]
    
    if (preloadedData) {
      // 使用预加载的数据
      console.log('[KernelConfig] 使用预加载的数据 (Test Type:', testTypeId, ')')
      sharedTestComponents.value = preloadedData.components
      sharedComponentsByCategory.value = preloadedData.componentsByCategory
      sharedTestCases.value = preloadedData.testCases
      sharedSelectedComponents.value = { ...preloadedData.selectedComponents }
      sharedSelectedCases.value = { ...preloadedData.selectedCases }
      
      console.log('[KernelConfig] 共享 Test Components 加载成功 (预加载):', preloadedData.components)
      console.log('[KernelConfig] Test Cases 加载成功 (预加载):', preloadedData.testCases)
    } else {
      // 如果预加载数据不存在，动态加载（fallback）
      console.log('[KernelConfig] 预加载数据不存在，动态加载 Test Type:', testTypeId)
      const components = await getTestComponents(parseInt(testTypeId))
      sharedTestComponents.value = components
      
      // 按 category 分组
      sharedComponentsByCategory.value = groupComponentsByCategory(components)
      
      // 加载所有 components 的 test cases
      sharedTestCases.value = await loadTestCasesForComponents(components)
      
      // 初始化复选框状态（默认全部勾选）
      initializeCheckboxStates(components, sharedTestCases.value, 'shared')
      
      console.log('[KernelConfig] 共享 Test Components 加载成功 (动态):', components)
      console.log('[KernelConfig] Test Cases 加载成功 (动态):', sharedTestCases.value)
    }
  } catch (error) {
    console.error('[KernelConfig] 加载 Test Components 失败:', error)
    Message.error('Failed to load Test Components')
    sharedTestComponents.value = []
    sharedComponentsByCategory.value = {}
    sharedTestCases.value = {}
    sharedSelectedComponents.value = {}
    sharedSelectedCases.value = {}
  }
}

// 加载机器的 Test Components (Individual 模式) - 从预加载数据中获取
const loadMachineTestComponents = async (machineId: number, testTypeId: string) => {
  if (!testTypeId) {
    if (machineTestComponents.value[machineId]) {
      delete machineTestComponents.value[machineId]
    }
    if (machineComponentsByCategory.value[machineId]) {
      delete machineComponentsByCategory.value[machineId]
    }
    if (machineTestCases.value[machineId]) {
      delete machineTestCases.value[machineId]
    }
    if (machineSelectedComponents.value[machineId]) {
      delete machineSelectedComponents.value[machineId]
    }
    if (machineSelectedCases.value[machineId]) {
      delete machineSelectedCases.value[machineId]
    }
    return
  }
  
  try {
    // 从预加载的数据中获取
    const preloadedData = preloadedTestData.value[testTypeId]
    
    if (preloadedData) {
      // 使用预加载的数据
      console.log(`[KernelConfig] Machine ${machineId} 使用预加载的数据 (Test Type: ${testTypeId})`)
      machineTestComponents.value = {
        ...machineTestComponents.value,
        [machineId]: preloadedData.components
      }
      
      machineComponentsByCategory.value = {
        ...machineComponentsByCategory.value,
        [machineId]: preloadedData.componentsByCategory
      }
      
      machineTestCases.value = {
        ...machineTestCases.value,
        [machineId]: preloadedData.testCases
      }
      
      // 复制选中状态（每个机器独立）
      machineSelectedComponents.value = {
        ...machineSelectedComponents.value,
        [machineId]: { ...preloadedData.selectedComponents }
      }
      
      machineSelectedCases.value = {
        ...machineSelectedCases.value,
        [machineId]: { ...preloadedData.selectedCases }
      }
      
      console.log(`[KernelConfig] Machine ${machineId} Test Components 加载成功 (预加载):`, preloadedData.components)
    } else {
      // 如果预加载数据不存在，动态加载（fallback）
      console.log(`[KernelConfig] Machine ${machineId} 预加载数据不存在，动态加载 Test Type: ${testTypeId}`)
      const components = await getTestComponents(parseInt(testTypeId))
      machineTestComponents.value = {
        ...machineTestComponents.value,
        [machineId]: components
      }
      
      // 按 category 分组
      machineComponentsByCategory.value = {
        ...machineComponentsByCategory.value,
        [machineId]: groupComponentsByCategory(components)
      }
      
      // 加载所有 components 的 test cases
      const casesMap = await loadTestCasesForComponents(components)
      machineTestCases.value = {
        ...machineTestCases.value,
        [machineId]: casesMap
      }
      
      // 初始化复选框状态（默认全部勾选）
      initializeCheckboxStates(components, casesMap, 'machine', machineId)
      
      console.log(`[KernelConfig] Machine ${machineId} Test Components 加载成功 (动态):`, components)
      console.log(`[KernelConfig] Machine ${machineId} Test Cases 加载成功 (动态):`, casesMap)
    }
    
    // 更新 test case 执行顺序
    updateMachineOrderedTestCases(machineId)
  } catch (error) {
    console.error(`[KernelConfig] 加载 Machine ${machineId} Test Components 失败:`, error)
    Message.error('Failed to load Test Components')
  }
}

// 处理 Test Type 改变 (Same 模式)
const handleTestTypeChange = async (value: string) => {
  console.log('[KernelConfig] handleTestTypeChange called with value:', value)
  testComponentsLoading.value = true
  try {
    await loadSharedTestComponents(value)
    console.log('[KernelConfig] loadSharedTestComponents completed')
    console.log('[KernelConfig] sharedComponentsByCategory:', sharedComponentsByCategory.value)
  } finally {
    testComponentsLoading.value = false
  }
  handleUpdate()
}

// 处理机器的 Test Type 改变 (Individual 模式)
const handleMachineTestTypeChange = async (machineId: number) => {
  const testTypeId = localIndividualTestTypeConfig.value[machineId]?.testType
  if (testTypeId) {
    await loadMachineTestComponents(machineId, testTypeId)
  }
  handleUpdate()
}

watch(() => props.selectedMachines, (machines) => {
  // 初始化 Kernel 配置
  const kernelConfig = { ...localIndividualConfig.value }
  machines.forEach((id) => {
    if (!kernelConfig[id]) {
      kernelConfig[id] = {
        type: kernelTypeOptions.value[0]?.value || '',
        version: ''
      }
    }
  })
  emit('update:individualConfig', kernelConfig)

  // 初始化 Test Type 配置
  const testTypeConfig = { ...localIndividualTestTypeConfig.value }
  machines.forEach((id) => {
    if (!testTypeConfig[id]) {
      testTypeConfig[id] = {
        testType: ''
      }
    }
  })
  emit('update:individualTestTypeConfig', testTypeConfig)
}, { immediate: true })

const getMachineName = (id: number) => {
  const machine = props.machinesMap?.[id]
  return machine?.hostname || `Machine ${id}`
}

const handleUpdate = () => {
  // 收集选中的 test components 和 test cases
  const selectedData = collectSelectedData()
  emit('update', selectedData)
}

// 收集选中的数据
const collectSelectedData = () => {
  const result: any = {
    testTypeConfigMethod: props.testTypeConfigMethod,
    components: []
  }
  
  if (props.testTypeConfigMethod === 'same') {
    // Same 模式
    result.testType = props.testType
    result.components = collectComponentsForShared()  // 返回按 category 分组的结构
  } else {
    // Individual 模式
    result.machineConfigs = {}
    props.selectedMachines.forEach(machineId => {
      const testType = localIndividualTestTypeConfig.value[machineId]?.testType
      if (testType) {
        result.machineConfigs[machineId] = {
          testType,
          components: collectComponentsForMachine(machineId),  // 返回按 category 分组的结构
          executionCaseList: collectExecutionCaseList(machineId)  // 返回按拖拽顺序的 test case 列表
        }
      }
    })
  }
  
  return result
}

// 收集 Shared 模式的选中 components（按 category 分组，带序号）
const collectComponentsForShared = () => {
  const categorizedComponents: Array<{ 
    category: string; 
    components: Array<{ name: string; testCases: Array<{ order: number; name: string }> }> 
  }> = []
  
  // 先收集所有选中的 test cases，用于全局编号
  const allSelectedCases: Array<{ componentId: number; caseName: string }> = []
  Object.entries(sharedComponentsByCategory.value).forEach(([category, components]) => {
    components.forEach(component => {
      if (sharedSelectedComponents.value[component.id]) {
        const cases = sharedTestCases.value[component.id] || []
        cases
          .filter(testCase => sharedSelectedCases.value[testCase.id])
          .forEach(testCase => {
            allSelectedCases.push({
              componentId: component.id,
              caseName: testCase.caseName
            })
          })
      }
    })
  })
  
  // 创建一个 Map 来存储每个 component 的 test cases 及其全局序号
  const componentCasesMap = new Map<number, Array<{ order: number; name: string }>>()
  let globalOrder = 1
  
  Object.entries(sharedComponentsByCategory.value).forEach(([category, components]) => {
    components.forEach(component => {
      if (sharedSelectedComponents.value[component.id]) {
        const cases = sharedTestCases.value[component.id] || []
        const orderedCases = cases
          .filter(testCase => sharedSelectedCases.value[testCase.id])
          .map(testCase => ({
            order: globalOrder++,
            name: testCase.caseName
          }))
        
        componentCasesMap.set(component.id, orderedCases)
      }
    })
  })
  
  // 按 category 分组收集
  Object.entries(sharedComponentsByCategory.value).forEach(([category, components]) => {
    const componentsInCategory: Array<{ name: string; testCases: Array<{ order: number; name: string }> }> = []
    
    components.forEach(component => {
      if (sharedSelectedComponents.value[component.id]) {
        const orderedCases = componentCasesMap.get(component.id) || []
        
        componentsInCategory.push({
          name: component.componentName,
          testCases: orderedCases
        })
      }
    })
    
    // 只添加有选中 components 的 category
    if (componentsInCategory.length > 0) {
      categorizedComponents.push({
        category: category,
        components: componentsInCategory
      })
    }
  })
  
  return categorizedComponents
}

// 收集 Shared 模式的选中 test cases（废弃，已合并到 collectComponentsForShared）
const collectCasesForShared = () => {
  return []
}

// 收集 Individual 模式指定机器的选中 components（按 category 分组，不带序号）
const collectComponentsForMachine = (machineId: number) => {
  const categorizedComponents: Array<{ 
    category: string; 
    components: Array<{ name: string; testCases: string[] }> 
  }> = []
  const componentsByCategory = machineComponentsByCategory.value[machineId] || {}
  const orderedCases = machineOrderedTestCases.value[machineId] || []
  
  // 创建一个 Map 来存储每个 component 的 test cases（不带序号）
  const componentCasesMap = new Map<number, string[]>()
  
  // 按照 orderedCases 的顺序，为每个 component 收集其 test cases（只要名称）
  orderedCases.forEach((orderedCase) => {
    const cases = componentCasesMap.get(orderedCase.componentId) || []
    cases.push(orderedCase.caseName)
    componentCasesMap.set(orderedCase.componentId, cases)
  })
  
  Object.entries(componentsByCategory).forEach(([category, components]) => {
    const componentsInCategory: Array<{ name: string; testCases: string[] }> = []
    
    components.forEach(component => {
      if (machineSelectedComponents.value[machineId]?.[component.id]) {
        // 使用 ordered test cases（如果存在），否则使用原始顺序
        let selectedCases = componentCasesMap.get(component.id) || []
        
        // 如果 ordered cases 为空，fallback 到原始逻辑
        if (selectedCases.length === 0) {
          const cases = machineTestCases.value[machineId]?.[component.id] || []
          selectedCases = cases
            .filter(testCase => machineSelectedCases.value[machineId]?.[testCase.id])
            .map(testCase => testCase.caseName)
        }
        
        componentsInCategory.push({
          name: component.componentName,
          testCases: selectedCases
        })
      }
    })
    
    // 只添加有选中 components 的 category
    if (componentsInCategory.length > 0) {
      categorizedComponents.push({
        category: category,
        components: componentsInCategory
      })
    }
  })
  
  return categorizedComponents
}

// 收集 Individual 模式指定机器的选中 test cases（废弃，已合并到 collectComponentsForMachine）
const collectCasesForMachine = (machineId: number) => {
  return []
}

// 收集 Individual 模式指定机器的 test case 执行顺序列表
const collectExecutionCaseList = (machineId: number): string[] => {
  const orderedCases = machineOrderedTestCases.value[machineId] || []
  return orderedCases.map(testCase => testCase.caseName)
}

// 构建树形数据结构（category -> component -> case）
const buildTreeDataFromCases = (cases: SearchTestCase[]) => {
  const categoryMap = new Map<string, Map<string, SearchTestCase[]>>()
  
  // 按 category -> component 分组
  cases.forEach(testCase => {
    const category = testCase.category || 'Uncategorized'
    const componentName = testCase.componentName || 'Unknown Component'
    
    if (!categoryMap.has(category)) {
      categoryMap.set(category, new Map())
    }
    
    const componentMap = categoryMap.get(category)!
    if (!componentMap.has(componentName)) {
      componentMap.set(componentName, [])
    }
    
    componentMap.get(componentName)!.push(testCase)
  })
  
  // 构建树形结构
  const treeData: any[] = []
  categoryMap.forEach((componentMap, category) => {
    const categoryNode: any = {
      key: `category-${category}`,
      title: category,
      value: `category-${category}`,
      selectable: false,
      children: []
    }
    
    componentMap.forEach((testCases, componentName) => {
      const componentNode: any = {
        key: `component-${componentName}`,
        title: componentName,
        value: `component-${componentName}`,
        selectable: false,
        children: []
      }
      
      testCases.forEach(testCase => {
        componentNode.children.push({
          key: `case-${testCase.id}`,
          title: testCase.caseName,
          value: `case-${testCase.id}`,
          label: testCase.caseName,
          selectable: true,
          raw: testCase
        })
      })
      
      categoryNode.children.push(componentNode)
    })
    
    treeData.push(categoryNode)
  })
  
  return treeData
}

// 加载所有 test cases（首次展开下拉框时调用）
const loadAllTestCases = async (machineId: number) => {
  // 如果已经加载过，直接使用缓存
  if (machineAllTestCases.value[machineId]?.length > 0) {
    return
  }
  
  machineSearchLoading.value[machineId] = true
  
  try {
    const results = await searchTestCases('')  // 空字符串返回所有 cases
    machineAllTestCases.value[machineId] = results
    machineSearchTreeData.value[machineId] = buildTreeDataFromCases(results)
  } catch (error) {
    console.error('[loadAllTestCases] 加载失败:', error)
    Message.error('加载 test cases 失败')
    machineAllTestCases.value[machineId] = []
    machineSearchTreeData.value[machineId] = []
  } finally {
    machineSearchLoading.value[machineId] = false
  }
}

// 防抖搜索（2秒）
const handleSearchWithDebounce = (machineId: number, searchValue: string) => {
  // 清除之前的定时器
  if (machineSearchDebounceTimers.value[machineId]) {
    clearTimeout(machineSearchDebounceTimers.value[machineId])
  }
  
  // 如果搜索值为空，显示所有数据
  if (!searchValue || searchValue.trim().length === 0) {
    const allCases = machineAllTestCases.value[machineId] || []
    machineSearchTreeData.value[machineId] = buildTreeDataFromCases(allCases)
    return
  }
  
  // 设置新的定时器（2秒后执行）
  machineSearchDebounceTimers.value[machineId] = setTimeout(async () => {
    machineSearchLoading.value[machineId] = true
    
    try {
      const results = await searchTestCases(searchValue.trim())
      machineSearchTreeData.value[machineId] = buildTreeDataFromCases(results)
    } catch (error) {
      console.error('[handleSearchWithDebounce] 搜索失败:', error)
      Message.error('搜索 test case 失败')
    } finally {
      machineSearchLoading.value[machineId] = false
    }
  }, 2000)  // 2秒防抖
}

// 下拉框展开时加载数据
const handleDropdownVisibleChange = async (machineId: number, visible: boolean) => {
  if (visible) {
    await loadAllTestCases(machineId)
  }
}

// 树形选择变化时的处理
const handleTreeSelectChange = (machineId: number, value: string) => {
  if (!value || !value.startsWith('case-')) {
    return
  }
  
  // 从 value 中提取 case ID
  const caseId = parseInt(value.replace('case-', ''))
  
  // 从树形数据中找到对应的 test case
  const allCases = machineAllTestCases.value[machineId] || []
  const testCase = allCases.find(c => c.id === caseId)
  
  if (!testCase) {
    return
  }
  
  // 检查是否已经在执行列表中
  const orderedCases = machineOrderedTestCases.value[machineId] || []
  const exists = orderedCases.some(c => c.id === testCase.id)
  
  if (exists) {
    Message.warning(`"${testCase.caseName}" 已经在执行列表中`)
    machineSearchSelectedCase.value[machineId] = ''
    return
  }
  
  // 添加到已选择的搜索 cases 列表
  const addedCases = machineAddedSearchCases.value[machineId] || []
  if (!addedCases.some(c => c.id === testCase.id)) {
    machineAddedSearchCases.value[machineId] = [...addedCases, testCase]
  }
  
  // 添加到执行顺序列表
  const newOrderedCase: OrderedTestCase = {
    id: testCase.id,
    caseName: testCase.caseName,
    componentId: testCase.componentId,
    componentName: testCase.componentName,
    category: testCase.category
  }
  
  machineOrderedTestCases.value[machineId] = [...orderedCases, newOrderedCase]
  
  // 清空选择
  machineSearchSelectedCase.value[machineId] = ''
  
  Message.success(`已添加 "${testCase.caseName}"`)
}

// 移除已添加的搜索 test case
const handleRemoveAddedSearchCase = (machineId: number, testCaseId: number) => {
  // 从已添加列表中移除
  const addedCases = machineAddedSearchCases.value[machineId] || []
  machineAddedSearchCases.value[machineId] = addedCases.filter(c => c.id !== testCaseId)
  
  // 从执行顺序列表中移除
  const orderedCases = machineOrderedTestCases.value[machineId] || []
  machineOrderedTestCases.value[machineId] = orderedCases.filter(c => c.id !== testCaseId)
}

// 处理创建 Test Type
const handleCreateTestType = () => {
  Message.info({
    content: 'Test Type management page is under construction. You will be redirected when it\'s ready.',
    duration: 3000
  })
  // TODO: 导航到 test type 编辑页面
  // router.push('/tpgen/test-type/create')
}

// 搜索过滤逻辑
const filterComponentsAndCases = (
  componentsByCategory: Record<string, TestComponent[]>,
  testCases: Record<number, TestCase[]>,
  keyword: string
): Record<string, TestComponent[]> => {
  if (!keyword.trim()) {
    return componentsByCategory
  }

  const lowerKeyword = keyword.toLowerCase().trim()
  const filtered: Record<string, TestComponent[]> = {}

  Object.entries(componentsByCategory).forEach(([category, components]) => {
    const filteredComponents = components.filter(component => {
      // 检查 component name 是否匹配
      if (component.componentName.toLowerCase().includes(lowerKeyword)) {
        return true
      }
      
      // 检查该 component 下的 test cases 是否有匹配的
      const cases = testCases[component.id] || []
      return cases.some(testCase => 
        testCase.caseName.toLowerCase().includes(lowerKeyword)
      )
    })

    if (filteredComponents.length > 0) {
      filtered[category] = filteredComponents
    }
  })

  return filtered
}

// 处理 Shared (Same 模式) 搜索
const handleSharedSearch = () => {
  filteredSharedComponentsByCategory.value = filterComponentsAndCases(
    sharedComponentsByCategory.value,
    sharedTestCases.value,
    sharedSearchKeyword.value
  )
}

// 处理 Machine (Individual 模式) 搜索
const handleMachineSearch = (machineId: number) => {
  const keyword = machineSearchKeywords.value[machineId] || ''
  const componentsByCategory = machineComponentsByCategory.value[machineId] || {}
  const testCases = machineTestCases.value[machineId] || {}
  
  const filtered = filterComponentsAndCases(componentsByCategory, testCases, keyword)
  
  filteredMachineComponentsByCategory.value = {
    ...filteredMachineComponentsByCategory.value,
    [machineId]: filtered
  }
}

// 获取过滤后的 Shared Components
const getFilteredSharedComponents = (): Record<string, TestComponent[]> => {
  if (!sharedSearchKeyword.value || !sharedSearchKeyword.value.trim()) {
    return sharedComponentsByCategory.value
  }
  return filteredSharedComponentsByCategory.value
}

// 获取过滤后的 Machine Components
const getFilteredMachineComponentsByCategory = (machineId: number): Record<string, TestComponent[]> => {
  const keyword = machineSearchKeywords.value[machineId]
  if (!keyword || !keyword.trim()) {
    return machineComponentsByCategory.value[machineId] || {}
  }
  return filteredMachineComponentsByCategory.value[machineId] || {}
}

// 初始化复选框状态（默认全部勾选）
const initializeCheckboxStates = (components: TestComponent[], testCases: Record<number, TestCase[]>, target: 'shared' | 'machine', machineId?: number) => {
  components.forEach(component => {
    if (target === 'shared') {
      sharedSelectedComponents.value[component.id] = true
      
      const cases = testCases[component.id] || []
      cases.forEach(testCase => {
        sharedSelectedCases.value[testCase.id] = true
      })
    } else if (target === 'machine' && machineId !== undefined) {
      if (!machineSelectedComponents.value[machineId]) {
        machineSelectedComponents.value[machineId] = {}
      }
      if (!machineSelectedCases.value[machineId]) {
        machineSelectedCases.value[machineId] = {}
      }
      
      machineSelectedComponents.value[machineId][component.id] = true
      
      const cases = testCases[component.id] || []
      cases.forEach(testCase => {
        machineSelectedCases.value[machineId][testCase.id] = true
      })
    }
  })
}

// 更新机器的 Test Case 执行顺序（展平所有选中的 test cases）
const updateMachineOrderedTestCases = (machineId: number) => {
  const componentsByCategory = machineComponentsByCategory.value[machineId] || {}
  const testCases = machineTestCases.value[machineId] || {}
  const selectedComponents = machineSelectedComponents.value[machineId] || {}
  const selectedCases = machineSelectedCases.value[machineId] || {}
  
  const orderedCases: OrderedTestCase[] = []
  
  // 遍历所有 categories 和 components，按当前顺序收集选中的 test cases
  Object.entries(componentsByCategory).forEach(([category, components]) => {
    components.forEach(component => {
      // 只处理选中的 component
      if (selectedComponents[component.id]) {
        const cases = testCases[component.id] || []
        cases.forEach(testCase => {
          // 只添加选中的 test case
          if (selectedCases[testCase.id]) {
            orderedCases.push({
              id: testCase.id,
              caseName: testCase.caseName,
              componentId: component.id,
              componentName: component.componentName,
              category: category
            })
          }
        })
      }
    })
  })
  
  // 如果已经存在排序列表，保留用户的拖拽顺序，只添加新的或移除不再选中的
  const existingOrder = machineOrderedTestCases.value[machineId] || []
  const existingIds = new Set(existingOrder.map(c => c.id))
  const newIds = new Set(orderedCases.map(c => c.id))
  
  // 保留现有顺序中仍然选中的 cases
  const preservedOrder = existingOrder.filter(c => newIds.has(c.id))
  
  // 添加新选中的 cases（未在现有顺序中的）
  const newCases = orderedCases.filter(c => !existingIds.has(c.id))
  
  machineOrderedTestCases.value[machineId] = [...preservedOrder, ...newCases]
  
  console.log(`[KernelConfig] 更新机器 ${machineId} 的 Test Case 执行顺序:`, machineOrderedTestCases.value[machineId])
}

// 处理复选框变化（Component 控制所有子 Test Cases 的选中状态）
const handleComponentCheckChange = (componentId: number, isChecked: boolean, mode: 'shared' | 'machine', machineId?: number) => {
  if (mode === 'shared') {
    // Shared 模式：更新该 component 下所有 test cases 的选中状态
    const cases = sharedTestCases.value[componentId] || []
    cases.forEach(testCase => {
      sharedSelectedCases.value[testCase.id] = isChecked
    })
  } else if (mode === 'machine' && machineId !== undefined) {
    // Individual 模式：更新该机器的该 component 下所有 test cases 的选中状态
    if (!machineSelectedCases.value[machineId]) {
      machineSelectedCases.value[machineId] = {}
    }
    
    const cases = machineTestCases.value[machineId]?.[componentId] || []
    cases.forEach(testCase => {
      machineSelectedCases.value[machineId][testCase.id] = isChecked
    })
    
    // 更新 test case 执行顺序
    updateMachineOrderedTestCases(machineId)
  }
  
  handleUpdate()
}

// 处理 Individual 模式下 test case 复选框变化
const handleMachineTestCaseCheckChange = (machineId: number, testCaseId: number) => {
  // 更新 test case 执行顺序
  updateMachineOrderedTestCases(machineId)
  handleUpdate()
}

// 拖拽开始
const handleDragStart = (event: DragEvent, type: string, context: any, index: number, item: any) => {
  dragType.value = type
  dragContext.value = context
  draggedItem.value = { index, item }
  
  if (event.dataTransfer) {
    event.dataTransfer.effectAllowed = 'move'
    event.dataTransfer.setData('text/html', event.target as any)
  }
}

// 拖拽放置
const handleDrop = (event: DragEvent, type: string, context: any, targetIndex: number) => {
  event.preventDefault()
  
  if (!draggedItem.value || dragType.value !== type) {
    return
  }
  
  const sourceIndex = draggedItem.value.index
  
  if (sourceIndex === targetIndex) {
    return
  }
  
  try {
    if (type === 'shared') {
      // Shared Components 拖拽
      const category = context
      const components = [...sharedComponentsByCategory.value[category]]
      const [removed] = components.splice(sourceIndex, 1)
      components.splice(targetIndex, 0, removed)
      sharedComponentsByCategory.value[category] = components
      
    } else if (type === 'shared-case') {
      // Shared Test Cases 拖拽
      const componentId = context
      const cases = [...sharedTestCases.value[componentId]]
      const [removed] = cases.splice(sourceIndex, 1)
      cases.splice(targetIndex, 0, removed)
      sharedTestCases.value[componentId] = cases
      
    } else if (type === 'machine') {
      // Machine Components 拖拽
      const { machineId, category } = context
      const components = [...machineComponentsByCategory.value[machineId][category]]
      const [removed] = components.splice(sourceIndex, 1)
      components.splice(targetIndex, 0, removed)
      machineComponentsByCategory.value[machineId][category] = components
      
    } else if (type === 'machine-case') {
      // Machine Test Cases 拖拽
      const { machineId, componentId } = context
      const cases = [...machineTestCases.value[machineId][componentId]]
      const [removed] = cases.splice(sourceIndex, 1)
      cases.splice(targetIndex, 0, removed)
      machineTestCases.value[machineId][componentId] = cases
    }
    
    console.log('[KernelConfig] 拖拽排序成功')
  } catch (error) {
    console.error('[KernelConfig] 拖拽排序失败:', error)
  }
  
  draggedItem.value = null
  dragType.value = ''
  dragContext.value = null
}

onMounted(() => {
  loadKernelTypes()
  loadTestTypes()
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

.test-type-selector {
  display: flex;
  align-items: center;
  gap: 12px;
  
  .create-test-type-link {
    white-space: nowrap;
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 14px;
    
    &:hover {
      text-decoration: underline;
    }
  }
}

/* Test Components 容器 */
.loading-container {
  display: flex;
  justify-content: center;
  align-items: center;
  padding: 40px 0;
  min-height: 200px;
}

.test-components-container {
  width: 100%;
}

.components-list {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  background: #ffffff;
  max-height: 600px;
  overflow-y: auto;
}

/* Category 分组 */
.category-group {
  margin-bottom: 24px;
  
  &:last-child {
    margin-bottom: 0;
  }
}

.category-header {
  font-size: 16px;
  font-weight: 600;
  color: #2c3e50;
  padding: 8px 12px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 6px;
  margin-bottom: 12px;
}

/* Component 项 */
.component-item {
  padding: 10px 12px;
  margin-bottom: 8px;
  background: #f8f9fa;
  border: 1px solid #e1e5eb;
  border-radius: 6px;
  cursor: move;
  transition: all 0.2s ease;
  
  &:hover {
    background: #e8f4fd;
    border-color: #3498db;
    box-shadow: 0 2px 8px rgba(52, 152, 219, 0.15);
  }
  
  &:last-child {
    margin-bottom: 0;
  }
  
  &[draggable="true"] {
    user-select: none;
  }
}

.component-name {
  display: flex;
  align-items: center;
  gap: 8px;
  font-weight: 500;
  color: #2c3e50;
  font-size: 14px;
}

/* Test Cases 子列表 */
.test-cases-sublist {
  margin-top: 8px;
  margin-left: 24px;
  padding-left: 12px;
  border-left: 2px solid #d1d5db;
}

.test-case-item {
  padding: 6px 10px;
  margin-bottom: 6px;
  background: #ffffff;
  border: 1px solid #d1d5db;
  border-radius: 4px;
  cursor: move;
  transition: all 0.2s ease;
  
  &:hover {
    background: #f0f9ff;
    border-color: #60a5fa;
    transform: translateX(4px);
  }
  
  &:last-child {
    margin-bottom: 0;
  }
  
  &[draggable="true"] {
    user-select: none;
  }
}

.test-case-name {
  display: flex;
  align-items: center;
  gap: 6px;
  font-size: 13px;
  color: #4b5563;
}

/* 拖拽图标 */
.drag-handle {
  color: #9ca3af;
  font-size: 12px;
  cursor: grab;
  
  &:active {
    cursor: grabbing;
  }
}

/* Checkbox 样式调整 */
:deep(.arco-checkbox) {
  .arco-checkbox-text {
    color: inherit;
  }
  
  &.arco-checkbox-disabled {
    .arco-checkbox-text {
      color: #d1d5db;
    }
  }
}

/* 滚动条美化 */
.components-list::-webkit-scrollbar {
  width: 8px;
}

.components-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.components-list::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
  
  &:hover {
    background: #555;
  }
}

/* 搜索所有 test cases 样式 */
.search-all-cases {
  padding: 16px;
  background: #f7f8fa;
  border-radius: 8px;
  border: 1px dashed #d0d5dd;
}

.added-search-cases {
  margin-top: 16px;
  
  .added-cases-title {
    font-size: 14px;
    font-weight: 500;
    color: #1d2129;
    margin-bottom: 8px;
  }
  
  .added-cases-list {
    display: flex;
    flex-wrap: wrap;
    gap: 8px;
  }
}

/* Test Case Execution Order 样式 */
.execution-order-container {
  width: 100%;
}

.execution-order-list {
  border: 1px solid #e5e7eb;
  border-radius: 8px;
  padding: 16px;
  background: #ffffff;
  max-height: 500px;
  overflow-y: auto;
}

.execution-order-item {
  display: flex;
  align-items: center;
  gap: 12px;
  padding: 12px 16px;
  margin-bottom: 8px;
  background: #f8f9fa;
  border: 1px solid #e1e5eb;
  border-radius: 6px;
  cursor: move;
  transition: all 0.2s ease;
  
  &:hover {
    background: #e8f4fd;
    border-color: #3498db;
    box-shadow: 0 2px 8px rgba(52, 152, 219, 0.15);
    transform: translateY(-2px);
  }
  
  &:last-child {
    margin-bottom: 0;
  }
}

.ghost {
  opacity: 0.5;
  background: #c3e7ff;
  border: 2px dashed #3498db;
}

.order-number {
  display: flex;
  align-items: center;
  justify-content: center;
  min-width: 32px;
  height: 32px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  font-weight: 600;
  font-size: 14px;
  border-radius: 50%;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.case-info {
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 6px;
}

.case-name {
  font-size: 14px;
  font-weight: 500;
  color: #2c3e50;
}

.case-meta {
  display: flex;
  align-items: center;
  gap: 8px;
  font-size: 12px;
}

.category-badge {
  padding: 2px 10px;
  background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
  color: white;
  border-radius: 12px;
  font-weight: 500;
}

.component-badge {
  padding: 2px 10px;
  background: #e8f4fd;
  color: #3498db;
  border: 1px solid #3498db;
  border-radius: 12px;
  font-weight: 500;
}

/* 滚动条美化（Execution Order List） */
.execution-order-list::-webkit-scrollbar {
  width: 8px;
}

.execution-order-list::-webkit-scrollbar-track {
  background: #f1f1f1;
  border-radius: 4px;
}

.execution-order-list::-webkit-scrollbar-thumb {
  background: #888;
  border-radius: 4px;
  
  &:hover {
    background: #555;
  }
}
</style>

