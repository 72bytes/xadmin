<template>
  <a-drawer
    v-model:visible="visibleModel"
    :title="`管理选项 - ${caseName}`"
    width="500px"
    @cancel="handleClose"
  >
    <div class="options-drawer">
      <!-- Options Table -->
      <div class="options-section">
        <div class="section-title">当前选项</div>
        
        <div v-if="localOptions.length === 0" class="empty-options">
          <icon-settings :size="32" />
          <p>暂无选项</p>
        </div>

        <a-table
          v-else
          :data="localOptions"
          :pagination="false"
          :bordered="false"
          :scroll="{ y: 300 }"
        >
          <template #columns>
            <a-table-column title="键" data-index="key" :width="150">
              <template #cell="{ record }">
                <span class="key-cell">{{ record.key }}</span>
              </template>
            </a-table-column>
            
            <a-table-column title="值" data-index="value">
              <template #cell="{ record }">
                <a-input
                  v-if="editingKey === record.key"
                  v-model="editingValue"
                  size="small"
                  @press-enter="handleSaveEdit(record.key)"
                />
                <span v-else class="value-cell">{{ record.value }}</span>
              </template>
            </a-table-column>
            
            <a-table-column title="操作" :width="120">
              <template #cell="{ record }">
                <a-space :size="8">
                  <a-button
                    v-if="editingKey === record.key"
                    type="primary"
                    size="mini"
                    @click="handleSaveEdit(record.key)"
                  >
                    保存
                  </a-button>
                  <a-button
                    v-else
                    type="text"
                    size="mini"
                    @click="handleStartEdit(record.key, record.value)"
                  >
                    <icon-edit />
                  </a-button>
                  
                  <a-button
                    v-if="editingKey === record.key"
                    type="text"
                    size="mini"
                    @click="handleCancelEdit"
                  >
                    取消
                  </a-button>
                  <a-popconfirm
                    v-else
                    content="确定要删除此选项吗？"
                    @ok="handleDeleteOption(record.key)"
                  >
                    <a-button
                      type="text"
                      status="danger"
                      size="mini"
                    >
                      <icon-delete />
                    </a-button>
                  </a-popconfirm>
                </a-space>
              </template>
            </a-table-column>
          </template>
        </a-table>
      </div>

      <!-- Add Option Form -->
      <div class="add-section">
        <div class="section-title">添加选项</div>
        
        <a-space direction="vertical" :style="{ width: '100%' }" :size="12">
          <a-input
            v-model="newOptionKey"
            placeholder="输入选项键"
            allow-clear
          >
            <template #prefix>
              <icon-code />
            </template>
          </a-input>
          
          <a-input
            v-model="newOptionValue"
            placeholder="输入选项值"
            allow-clear
            @press-enter="handleAddOption"
          >
            <template #prefix>
              <icon-file />
            </template>
          </a-input>
          
          <a-button
            type="primary"
            long
            :disabled="!newOptionKey.trim() || !newOptionValue.trim()"
            :loading="adding"
            @click="handleAddOption"
          >
            <template #icon>
              <icon-plus />
            </template>
            添加选项
          </a-button>
        </a-space>
      </div>
    </div>
  </a-drawer>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Message } from '@arco-design/web-vue'
import * as caseBrowserAPI from '@/apis/system/casebrowser'
import type { CaseOption } from '@/apis/system/casebrowser-type'

interface Props {
  visible: boolean
  casespace: string
  caseName: string
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'refresh'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// State
const localOptions = ref<CaseOption[]>([])
const newOptionKey = ref('')
const newOptionValue = ref('')
const adding = ref(false)

// Edit state
const editingKey = ref<string>()
const editingValue = ref('')

// Computed
const visibleModel = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value),
})

// Watch visible prop to load options
watch(
  () => props.visible,
  async (newVisible) => {
    if (newVisible) {
      await loadOptions()
    }
  }
)

// Load options
const loadOptions = async () => {
  if (!props.casespace || !props.caseName) {
    return
  }

  try {
    const { data } = await caseBrowserAPI.getCaseDetail(
      props.casespace,
      props.caseName
    )
    localOptions.value = data.options || []
  }
  catch (error: any) {
    console.error('Failed to load options:', error)
    Message.error('加载选项失败')
  }
}

// Handle add option
const handleAddOption = async () => {
  const key = newOptionKey.value.trim()
  const value = newOptionValue.value.trim()

  if (!key || !value) {
    Message.warning('请输入键和值')
    return
  }

  // Check if key already exists
  if (localOptions.value.some(opt => opt.key === key)) {
    Message.warning('该键已存在，请使用编辑功能修改')
    return
  }

  adding.value = true
  try {
    await caseBrowserAPI.addOption({
      casespace: props.casespace,
      caseName: props.caseName,
      key,
      value,
    })
    
    localOptions.value.push({ key, value })
    newOptionKey.value = ''
    newOptionValue.value = ''
    Message.success(`已添加选项: ${key}`)
    emit('refresh')
  }
  catch (error: any) {
    console.error('Failed to add option:', error)
    Message.error(error.message || '添加选项失败')
  }
  finally {
    adding.value = false
  }
}

// Handle start edit
const handleStartEdit = (key: string, value: string) => {
  editingKey.value = key
  editingValue.value = value
}

// Handle cancel edit
const handleCancelEdit = () => {
  editingKey.value = undefined
  editingValue.value = ''
}

// Handle save edit
const handleSaveEdit = async (key: string) => {
  const value = editingValue.value.trim()
  
  if (!value) {
    Message.warning('值不能为空')
    return
  }

  try {
    await caseBrowserAPI.updateOption({
      casespace: props.casespace,
      caseName: props.caseName,
      key,
      value,
    })
    
    const option = localOptions.value.find(opt => opt.key === key)
    if (option) {
      option.value = value
    }
    
    Message.success(`已更新选项: ${key}`)
    emit('refresh')
    handleCancelEdit()
  }
  catch (error: any) {
    console.error('Failed to update option:', error)
    Message.error(error.message || '更新选项失败')
  }
}

// Handle delete option
const handleDeleteOption = async (key: string) => {
  try {
    await caseBrowserAPI.deleteOption(props.casespace, props.caseName, key)
    
    const index = localOptions.value.findIndex(opt => opt.key === key)
    if (index > -1) {
      localOptions.value.splice(index, 1)
    }
    
    Message.success(`已删除选项: ${key}`)
    emit('refresh')
  }
  catch (error: any) {
    console.error('Failed to delete option:', error)
    Message.error(error.message || '删除选项失败')
  }
}

// Handle close
const handleClose = () => {
  newOptionKey.value = ''
  newOptionValue.value = ''
  handleCancelEdit()
  visibleModel.value = false
}
</script>

<style scoped lang="scss">
.options-drawer {
  display: flex;
  flex-direction: column;
  gap: 24px;

  .section-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--color-text-1);
    margin-bottom: 12px;
  }

  .options-section {
    .empty-options {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 40px 20px;
      color: var(--color-text-3);

      p {
        margin-top: 12px;
        font-size: 14px;
      }
    }

    .key-cell {
      font-weight: 500;
      color: var(--color-text-1);
    }

    .value-cell {
      color: var(--color-text-2);
      word-break: break-all;
    }
  }

  .add-section {
    padding-top: 24px;
    border-top: 1px solid var(--color-border-2);
  }
}
</style>

