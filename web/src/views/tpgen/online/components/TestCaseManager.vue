<template>
  <a-card class="form-section" :bordered="false">
    <template #title>
      <div class="section-title">
        <icon-check-square />
        Test Case Select
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

    <!-- 测试用例组 -->
    <div class="test-type-groups">
      <a-card
        v-for="(subgroups, testType) in testCaseGroups"
        :key="testType"
        class="test-type-group"
        :bordered="false"
      >
        <template #title>
          <div class="group-title">
            <icon-layers />
            {{ testType }}
          </div>
        </template>

        <div v-for="(testCases, subgroupName) in subgroups" :key="subgroupName" class="test-case-subgroup">
          <h5>{{ subgroupName }}</h5>
          <div class="checkbox-list">
            <a-checkbox
              v-for="testCase in testCases"
              :key="testCase.id"
              :model-value="isSelected(testCase.id, testType, subgroupName)"
              @change="(checked) => handleCheckboxChange(checked as boolean, testCase, testType, subgroupName)"
            >
              {{ testCase.name }}
            </a-checkbox>
          </div>
        </div>
      </a-card>

      <!-- 自定义组 -->
      <a-card
        v-for="(testCases, groupName) in customGroups"
        :key="groupName"
        class="test-type-group custom"
        :bordered="false"
      >
        <template #title>
          <div class="group-title">
            <icon-star />
            {{ groupName }}
            <a-tag color="orangered" size="small">Custom</a-tag>
          </div>
        </template>

        <div class="checkbox-list">
          <a-checkbox
            v-for="testCase in testCases"
            :key="testCase.id"
            :model-value="isSelected(testCase.id, 'Custom', groupName)"
            @change="(checked) => handleCheckboxChange(checked as boolean, testCase, 'Custom', groupName)"
          >
            {{ testCase.name }}
          </a-checkbox>
        </div>
      </a-card>
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
import { ref, computed } from 'vue'
import type { TestCase } from '../types'
import { VueDraggable } from 'vue-draggable-plus'
import CustomGroupModal from './CustomGroupModal.vue'

// Test Case Groups - 从数据库获取（暂时为空数组）
const testCaseGroups = ref<any[]>([])

defineOptions({ name: 'TestCaseManager' })

const props = defineProps<{
  selectedTestCases: TestCase[]
}>()

const emit = defineEmits<{
  'update:selectedTestCases': [value: TestCase[]]
  'update': []
}>()

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

// 检查测试用例是否被选中
const isSelected = (id: number, testType: string, subgroup: string) => {
  return localSelectedTestCases.value.some(
    tc => tc.id === id && tc.testType === testType && tc.subgroup === subgroup,
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
  }
  else {
    localSelectedTestCases.value = localSelectedTestCases.value.filter(
      tc => !(tc.id === testCase.id && tc.testType === testType && tc.subgroup === subgroup),
    )
  }
}

// 获取所有测试用例
const getAllTestCases = () => {
  const allCases: TestCase[] = []

  // 添加预定义的测试用例
  Object.entries(testCaseGroups).forEach(([testType, subgroups]) => {
    Object.entries(subgroups).forEach(([subgroupName, testCases]) => {
      testCases.forEach((testCase) => {
        allCases.push({
          ...testCase,
          testType,
          subgroup: subgroupName,
        })
      })
    })
  })

  // 添加自定义组的测试用例
  Object.entries(customGroups.value).forEach(([groupName, testCases]) => {
    testCases.forEach((testCase) => {
      allCases.push({
        ...testCase,
        testType: 'Custom',
        subgroup: groupName,
      })
    })
  })

  return allCases
}

// 处理搜索
const handleSearch = () => {
  // 搜索逻辑可以在这里实现，暂时作为展示
  console.log('Searching for:', searchKeyword.value)
}

// 添加自定义组
const handleAddCustomGroup = (groupName: string, testCases: TestCase[]) => {
  customGroups.value[groupName] = testCases
  showCustomGroupModal.value = false
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

.test-type-groups {
  display: grid;
  gap: 20px;
  margin-bottom: 20px;

  .test-type-group {
    border: 2px solid #e1e5eb;
    border-radius: 12px;
    transition: all 0.3s ease;

    &:hover {
      border-color: #3498db;
    }

    &.custom {
      border-color: #e67e22;
    }

    .group-title {
      display: flex;
      align-items: center;
      gap: 10px;
      color: #2c3e50;
      font-weight: 600;
      font-size: 1.3rem;
    }

    .test-case-subgroup {
      margin-bottom: 20px;

      &:last-child {
        margin-bottom: 0;
      }

      h5 {
        margin: 15px 0 10px 0;
        color: #555;
        font-size: 1.1rem;
        padding-bottom: 5px;
        border-bottom: 1px dashed #e1e5eb;
      }

      .checkbox-list {
        display: grid;
        gap: 10px;

        :deep(.arco-checkbox) {
          background: #f8f9fa;
          padding: 12px 18px;
          border-radius: 8px;
          transition: all 0.3s ease;
          border: 1px solid #e1e5eb;

          &:hover {
            background: #e9ecef;
            transform: translateY(-2px);
          }
        }
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

