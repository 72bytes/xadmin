<template>
  <a-card class="form-section" :bordered="false">
    <template #title>
      <div class="section-title">
        <icon-check-square />
        Test Case Management
      </div>
    </template>

    <!-- 搜索框 -->
    <a-form-item label="Search Test Cases">
      <a-input-search
        v-model="searchKeyword"
        placeholder="Search for test cases..."
        @search="handleSearch"
        @input="handleSearch"
      />
    </a-form-item>

    <!-- 测试用例组 - 使用折叠面板减少初始显示 -->
    <div class="test-type-groups">
      <a-collapse
        :default-active-key="defaultExpandedKeys"
        :bordered="false"
        expand-icon-position="right"
      >
        <!-- 每个测试类型一个折叠面板 -->
        <a-collapse-item
          v-for="(subgroups, testType) in testCaseGroups"
          :key="testType"
        >
          <template #header>
            <div class="collapse-header">
              <icon-layers style="margin-right: 8px" />
              <span class="header-text">{{ testType }}</span>
              <a-tag color="purple" size="small" style="margin-left: 12px">
                {{ getTestTypeCount(subgroups) }} 个用例
              </a-tag>
            </div>
          </template>

          <!-- 子组件级别的折叠 -->
          <a-collapse :bordered="false" class="subgroup-collapse">
            <a-collapse-item
              v-for="(testCases, subgroupName) in subgroups"
              :key="subgroupName"
            >
              <template #header>
                <span class="subgroup-header">{{ subgroupName }}</span>
                <a-tag color="blue" size="small" style="margin-left: 8px">
                  {{ testCases.length }} 个
                </a-tag>
              </template>

              <div class="checkbox-list">
                <a-checkbox
                  v-for="testCase in testCases"
                  :key="testCase.id"
                  :model-value="isSelected(testCase.id, testType, subgroupName)"
                  @change="(checked) => handleCheckboxChange(checked as boolean, testCase, testType, subgroupName)"
                >
                  <span class="test-case-name">{{ testCase.caseName || testCase.name }}</span>
                  <span v-if="testCase.description || testCase.caseConfig?.description" class="test-case-desc">
                    - {{ testCase.description || testCase.caseConfig?.description }}
                  </span>
                </a-checkbox>
              </div>
            </a-collapse-item>
          </a-collapse>
        </a-collapse-item>

        <!-- 自定义组 -->
        <a-collapse-item
          v-if="Object.keys(customGroups).length > 0"
          key="custom-groups"
        >
          <template #header>
            <div class="collapse-header">
              <icon-star style="margin-right: 8px" />
              <span class="header-text">Custom Groups</span>
              <a-tag color="orange" size="small" style="margin-left: 12px">
                {{ Object.keys(customGroups).length }} 个自定义组
              </a-tag>
            </div>
          </template>

          <a-collapse :bordered="false" class="subgroup-collapse">
            <a-collapse-item
              v-for="(testCases, groupName) in customGroups"
              :key="groupName"
            >
              <template #header>
                <span class="subgroup-header">{{ groupName }}</span>
                <a-tag color="green" size="small" style="margin-left: 8px">
                  {{ testCases.length }} 个
                </a-tag>
              </template>

              <div class="checkbox-list">
                <a-checkbox
                  v-for="testCase in testCases"
                  :key="testCase.id"
                  :model-value="isSelected(testCase.id, 'Custom', groupName)"
                  @change="(checked) => handleCheckboxChange(checked as boolean, testCase, 'Custom', groupName)"
                >
                  {{ testCase.caseName || testCase.name }}
                </a-checkbox>
              </div>
            </a-collapse-item>
          </a-collapse>
        </a-collapse-item>
      </a-collapse>
    </div>

    <!-- 添加自定义组按钮 -->
    <a-button class="add-custom-group-btn" @click="showCustomGroupModal = true">
      <template #icon><icon-plus-circle /></template>
      Add Custom Test Group
    </a-button>

    <!-- 已选择的测试用例 -->
    <div v-if="localSelectedTestCases.length > 0" class="selected-test-cases">
      <h4>
        <icon-list />
        Selected Test Cases ({{ localSelectedTestCases.length }})
      </h4>
      <VueDraggable
        v-model="localSelectedTestCases"
        class="test-case-container"
        @end="handleUpdate"
      >
        <div
          v-for="testCase in localSelectedTestCases"
          :key="testCase.id"
          class="test-case-item"
        >
          <div>
            <strong>{{ testCase.name }}</strong>
            <p>{{ testCase.description }}</p>
          </div>
          <div class="test-case-info">
            {{ testCase.testType }} - {{ testCase.subgroup }}
            <a-tag :color="testCase.testType === 'Custom' ? 'orangered' : 'arcoblue'" size="small">
              {{ testCase.testType === 'Custom' ? 'Custom' : 'Standard' }}
            </a-tag>
          </div>
        </div>
      </VueDraggable>
    </div>

    <!-- 自定义组模态框 -->
    <CustomGroupModal
      v-model:visible="showCustomGroupModal"
      :existing-cases="getAllTestCases()"
      @add-group="handleAddCustomGroup"
    />
  </a-card>
</template>

<script setup lang="ts">
import { VueDraggable } from 'vue-draggable-plus'
import type { TestCase } from '../types'
import { useTestCases } from '../composables/useTestCases'
import CustomGroupModal from './CustomGroupModal.vue'

defineOptions({ name: 'TestCaseManager' })

const props = defineProps<{
  selectedTestCases: TestCase[]
}>()

const emit = defineEmits<{
  'update:selectedTestCases': [value: TestCase[]]
  'update': []
}>()

// 使用测试用例 composable
const { testCaseGroups, loadTestCases, getAllTestCases: getAllTestCasesFromDb } = useTestCases()

// 更新事件处理（定义在前面，避免 no-use-before-define 错误）
const handleUpdate = () => {
  emit('update')
}

const localSelectedTestCases = computed({
  get: () => props.selectedTestCases,
  set: (val) => {
    emit('update:selectedTestCases', val)
    handleUpdate()
  },
})

const searchKeyword = ref('')
const showCustomGroupModal = ref(false)
const customGroups = ref<Record<string, TestCase[]>>({})

// 默认展开的面板（只展开第一个测试类型）
const defaultExpandedKeys = computed(() => {
  const keys = Object.keys(testCaseGroups.value)
  return keys.length > 0 ? [keys[0]] : []
})

// 获取测试类型下的总用例数
const getTestTypeCount = (subgroups: any) => {
  let count = 0
  Object.values(subgroups).forEach((cases: any) => {
    count += cases.length
  })
  return count
}

// 检查测试用例是否被选中
const isSelected = (id: number, testType: string, subgroup: string) => {
  return localSelectedTestCases.value.some(
    (tc) => tc.id === id && tc.testType === testType && tc.subgroup === subgroup,
  )
}

// 处理复选框变化
const handleCheckboxChange = (checked: boolean, testCase: TestCase, testType: string, subgroup: string) => {
  const enhancedTestCase: TestCase = {
    ...testCase,
    testType,
    subgroup,
  }

  if (checked) {
    localSelectedTestCases.value = [...localSelectedTestCases.value, enhancedTestCase]
  } else {
    localSelectedTestCases.value = localSelectedTestCases.value.filter(
      (tc) => !(tc.id === testCase.id && tc.testType === testType && tc.subgroup === subgroup),
    )
  }
}

// 获取所有测试用例（包括自定义组）
const getAllTestCases = () => {
  const allCases: TestCase[] = []

  // 从数据库获取的测试用例
  allCases.push(...getAllTestCasesFromDb.value)

  // 添加自定义组的测试用例
  Object.entries(customGroups.value).forEach(([groupName, testCases]) => {
    testCases.forEach((testCase) => {
      allCases.push({
        ...testCase,
        testType: 'Custom',
        subgroup: groupName,
        customGroup: groupName,
      })
    })
  })

  return allCases
}

// 处理搜索
const handleSearch = () => {
  // 搜索逻辑可以在这里实现，根据 searchKeyword.value 过滤测试用例
  // 未来可扩展实时搜索过滤功能
}

// 添加自定义组
const handleAddCustomGroup = (groupName: string, testCases: TestCase[]) => {
  customGroups.value[groupName] = testCases
  showCustomGroupModal.value = false
}

// 组件挂载时加载测试用例
onMounted(async () => {
  await loadTestCases()
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

.test-type-groups {
  margin-bottom: 20px;

  :deep(.arco-collapse) {
    background: transparent;

    // 顶层折叠面板样式（测试类型）
    > .arco-collapse-item {
      margin-bottom: 16px;
      background: var(--color-bg-2);
      border-radius: 12px;
      overflow: hidden;
      box-shadow: 0 2px 8px rgba(0, 0, 0, 0.08);
      transition: all 0.3s ease;

      &:hover {
        box-shadow: 0 4px 16px rgba(0, 0, 0, 0.12);
      }

      &:last-child {
        margin-bottom: 0;
      }
    }

    // 顶层折叠面板头部
    > .arco-collapse-item > .arco-collapse-item-header {
      background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
      color: white;
      font-size: 1.1rem;
      font-weight: 600;
      padding: 16px 20px;

      &:hover {
        background: linear-gradient(135deg, #5568d3 0%, #653a8b 100%);
      }

      .collapse-header {
        display: flex;
        align-items: center;

        .header-text {
          font-weight: 600;
          flex: 1;
        }
      }
    }

    // 顶层折叠面板内容区
    > .arco-collapse-item > .arco-collapse-item-content {
      padding: 16px;
      background: white;
    }
  }

  // 子组件级别的折叠样式
  .subgroup-collapse {
    :deep(.arco-collapse-item) {
      margin-bottom: 12px;
      background: var(--color-fill-1);
      border-radius: 8px;
      border: 1px solid var(--color-border-2);

      &:last-child {
        margin-bottom: 0;
      }

      &:hover {
        border-color: rgb(var(--primary-5));
      }
    }

    :deep(.arco-collapse-item-header) {
      background: var(--color-fill-2);
      color: var(--color-text-1);
      font-size: 1rem;
      font-weight: 500;
      padding: 12px 16px;

      &:hover {
        background: var(--color-fill-3);
      }

      .subgroup-header {
        font-weight: 500;
      }
    }

    :deep(.arco-collapse-item-content) {
      padding: 12px 16px;
      background: white;
    }
  }

  // 复选框列表样式
  .checkbox-list {
    display: grid;
    gap: 8px;

    :deep(.arco-checkbox) {
      background: var(--color-fill-1);
      padding: 10px 14px;
      border-radius: 6px;
      transition: all 0.2s ease;
      border: 1px solid var(--color-border-2);

      &:hover {
        background: var(--color-fill-2);
        border-color: rgb(var(--primary-5));
        transform: translateX(3px);
      }

      .test-case-name {
        font-weight: 500;
        color: var(--color-text-1);
      }

      .test-case-desc {
        color: var(--color-text-3);
        font-size: 0.85rem;
        margin-left: 8px;
      }
    }
  }
}

.add-custom-group-btn {
  width: 100%;
  margin-bottom: 20px;
}

.selected-test-cases {
  margin-top: 30px;

  h4 {
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 15px;
    color: #2c3e50;
  }

  .test-case-container {
    border: 2px solid #e1e5eb;
    border-radius: 12px;
    padding: 20px;
    min-height: 200px;
    background: #f8f9fa;
    transition: all 0.3s ease;

    &:hover {
      border-color: #3498db;
    }

    .test-case-item {
      background: white;
      padding: 15px;
      margin-bottom: 12px;
      border-radius: 8px;
      cursor: move;
      display: flex;
      justify-content: space-between;
      align-items: center;
      box-shadow: 0 2px 5px rgba(0, 0, 0, 0.05);
      border-left: 4px solid #3498db;
      transition: all 0.3s ease;

      &:hover {
        transform: translateX(5px);
        box-shadow: 0 5px 15px rgba(0, 0, 0, 0.1);
      }

      &:last-child {
        margin-bottom: 0;
      }

      strong {
        display: block;
        margin-bottom: 5px;
        color: #2c3e50;
      }

      p {
        margin: 0;
        font-size: 0.9rem;
        color: #666;
      }

      .test-case-info {
        display: flex;
        align-items: center;
        gap: 10px;
        font-size: 0.9rem;
        color: #666;
        white-space: nowrap;
      }
    }
  }
}
</style>
