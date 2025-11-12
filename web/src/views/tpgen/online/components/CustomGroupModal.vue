<template>
  <a-modal
    v-model:visible="localVisible"
    title="Create Custom Test Group"
    width="800px"
    @cancel="handleCancel"
  >
    <template #title>
      <div class="modal-title">
        <icon-plus-circle />
        Create Custom Test Group
      </div>
    </template>

    <a-form :model="formData" layout="vertical">
      <a-form-item label="Group Name" field="groupName" required>
        <a-input v-model="formData.groupName" placeholder="Enter group name" />
      </a-form-item>

      <a-form-item label="Add Existing Test Cases">
        <a-input-search
          v-model="searchKeyword"
          placeholder="Search existing test cases..."
          @search="handleSearch"
        />
        <div class="existing-cases-list">
          <div
            v-for="testCase in filteredCases"
            :key="`${testCase.id}-${testCase.testType}-${testCase.subgroup}`"
            class="case-item"
            :class="{ selected: isSelected(testCase) }"
            @click="toggleCase(testCase)"
          >
            <div>
              <strong>{{ testCase.name }}</strong>
              <p>{{ testCase.description }}</p>
              <small>
                {{ testCase.testType }} - {{ testCase.subgroup }}
                <a-tag
                  :color="testCase.testType === 'Custom' ? 'orangered' : 'arcoblue'"
                  size="small"
                >
                  {{ testCase.testType === 'Custom' ? 'Custom' : 'Standard' }}
                </a-tag>
              </small>
            </div>
            <icon-check-circle v-if="isSelected(testCase)" class="check-icon" />
          </div>
        </div>
      </a-form-item>

      <a-form-item label="Or Create New Test Cases">
        <a-space direction="vertical" fill>
          <a-input v-model="newTestCase.name" placeholder="Test case name" />
          <a-input v-model="newTestCase.description" placeholder="Test case description" />
          <a-button type="outline" @click="handleAddNewTestCase">
            <template #icon><icon-plus /></template>
            Add Test Case
          </a-button>
        </a-space>
      </a-form-item>

      <a-form-item label="Selected Test Cases">
        <div class="selected-cases-list">
          <div
            v-for="(testCase, index) in formData.selectedCases"
            :key="index"
            class="case-item"
          >
            <div>
              <strong>{{ testCase.name }}</strong>
              <p>{{ testCase.description }}</p>
              <small v-if="testCase.testType">
                {{ testCase.testType }} - {{ testCase.subgroup }}
              </small>
              <a-tag v-else color="orangered" size="small">New Custom</a-tag>
            </div>
            <a-button type="text" size="small" @click="removeCase(index)">
              <template #icon><icon-close /></template>
            </a-button>
          </div>
          <a-empty v-if="formData.selectedCases.length === 0" description="No test cases selected" />
        </div>
      </a-form-item>
    </a-form>

    <template #footer>
      <a-button @click="handleCancel">Cancel</a-button>
      <a-button type="primary" :disabled="!canSave" @click="handleSave">
        <template #icon><icon-save /></template>
        Save Group
      </a-button>
    </template>
  </a-modal>
</template>

<script setup lang="ts">
import { Message } from '@arco-design/web-vue'
import type { TestCase } from '../types'

defineOptions({ name: 'CustomGroupModal' })

const props = defineProps<{
  visible: boolean
  existingCases: TestCase[]
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
  'addGroup': [groupName: string, testCases: TestCase[]]
}>()

const localVisible = computed({
  get: () => props.visible,
  set: (val) => emit('update:visible', val),
})

const formData = reactive({
  groupName: '',
  selectedCases: [] as TestCase[],
})

const searchKeyword = ref('')
const newTestCase = reactive({
  name: '',
  description: '',
})
let nextCustomId = 1000

const filteredCases = computed(() => {
  if (!searchKeyword.value) {
    return props.existingCases
  }

  const keyword = searchKeyword.value.toLowerCase()
  return props.existingCases.filter((testCase) =>
    testCase.name.toLowerCase().includes(keyword)
    || testCase.description.toLowerCase().includes(keyword)
    || testCase.testType?.toLowerCase().includes(keyword)
    || testCase.subgroup?.toLowerCase().includes(keyword),
  )
})

const canSave = computed(() => {
  return formData.groupName.trim() && formData.selectedCases.length > 0
})

const isSelected = (testCase: TestCase) => {
  return formData.selectedCases.some(
    (c) => c.id === testCase.id && c.testType === testCase.testType && c.subgroup === testCase.subgroup,
  )
}

const toggleCase = (testCase: TestCase) => {
  const index = formData.selectedCases.findIndex(
    (c) => c.id === testCase.id && c.testType === testCase.testType && c.subgroup === testCase.subgroup,
  )

  if (index === -1) {
    formData.selectedCases.push(testCase)
  } else {
    formData.selectedCases.splice(index, 1)
  }
}

const handleAddNewTestCase = () => {
  if (!newTestCase.name.trim()) {
    Message.warning('Please enter a test case name')
    return
  }

  const testCase: TestCase = {
    id: nextCustomId++,
    name: newTestCase.name,
    description: newTestCase.description,
  }

  formData.selectedCases.push(testCase)

  // 清空输入
  newTestCase.name = ''
  newTestCase.description = ''
  Message.success('Test case added')
}

const removeCase = (index: number) => {
  formData.selectedCases.splice(index, 1)
}

const handleSearch = () => {
  // 搜索在 computed 中处理
}

const handleSave = () => {
  if (!canSave.value) {
    return
  }

  emit('addGroup', formData.groupName, formData.selectedCases)

  // 重置表单
  formData.groupName = ''
  formData.selectedCases = []
  searchKeyword.value = ''

  Message.success('Custom group created successfully')
}

const handleCancel = () => {
  localVisible.value = false
  // 重置表单
  formData.groupName = ''
  formData.selectedCases = []
  searchKeyword.value = ''
}
</script>

<style scoped lang="scss">
.modal-title {
  display: flex;
  align-items: center;
  gap: 10px;
  font-size: 1.2rem;
  font-weight: 600;
}

.existing-cases-list,
.selected-cases-list {
  max-height: 300px;
  overflow-y: auto;
  border: 2px solid #e1e5eb;
  border-radius: 10px;
  padding: 15px;
  background: #f8f9fa;
  margin-top: 10px;

  .case-item {
    padding: 12px 15px;
    border-radius: 8px;
    margin-bottom: 8px;
    background: white;
    transition: all 0.3s ease;
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 15px;

    &:last-child {
      margin-bottom: 0;
    }

    &:hover {
      background: #f1f3f5;
      transform: translateX(5px);
    }

    &.selected {
      background: rgba(52, 152, 219, 0.1);
      border-left: 4px solid #3498db;
    }

    strong {
      display: block;
      margin-bottom: 5px;
      color: #2c3e50;
    }

    p {
      margin: 5px 0;
      font-size: 0.9rem;
      color: #666;
    }

    small {
      font-size: 0.85rem;
      color: #999;
    }

    .check-icon {
      color: #27ae60;
      font-size: 1.5rem;
      flex-shrink: 0;
    }
  }
}

.existing-cases-list {
  .case-item {
    cursor: pointer;
  }
}
</style>
