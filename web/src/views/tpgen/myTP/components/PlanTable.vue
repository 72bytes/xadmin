<template>
  <GiTable
    row-key="id"
    :data="dataList"
    :columns="columns"
    :loading="loading"
    :scroll="{ x: '100%', y: '100%', minWidth: 1800 }"
    :pagination="pagination"
    :row-selection="rowSelection"
    :selected-keys="selectedKeys"
    :disabled-tools="['size']"
    :row-class="getRowClass"
    @select="handleSelect"
    @select-all="handleSelectAll"
    @refresh="emit('refresh')"
  >
    <template #top>
      <GiForm
        :model-value="queryForm"
        :options="options"
        :columns="queryFormColumns"
        @update:model-value="handleQueryFormUpdate"
        @search="emit('search')"
        @reset="emit('reset')"
      />
    </template>

    <template #toolbar-left>
      <a-button
        :disabled="!selectedKeys.length"
        status="danger"
        @click="emit('batch-delete')"
      >
        <template #icon><icon-delete /></template>
        <template #default>DELETE</template>
      </a-button>
    </template>

    <template #category="{ record }">
      <a-tag v-if="record.category === 'Benchmark'" color="blue">Benchmark</a-tag>
      <a-tag v-else-if="record.category === 'Functional'" color="green">Functional</a-tag>
      <a-tag v-else-if="record.category === 'Performance'" color="orange">Performance</a-tag>
      <a-tag v-else-if="record.category === 'Stress'" color="red">Stress</a-tag>
      <a-tag v-else color="purple">Custom</a-tag>
    </template>

    <template #status="{ record }">
      <a-tag v-if="record.status === 1" color="gray">PRIVATE</a-tag>
      <a-tag v-else-if="record.status === 2" color="green">PUBLIC</a-tag>
    </template>

    <!-- 标签列暂时隐藏 -->
    <!-- <template #tags="{ record }">
      <a-space v-if="record.tags" wrap :size="4">
        <a-tag v-for="tag in record.tags.split(',')" :key="tag" size="small">
          {{ tag }}
        </a-tag>
      </a-space>
      <span v-else class="text-gray-400">-</span>
    </template> -->

    <!-- <template #hardware="{ record }">
      <div class="hardware-info">
        <div v-if="record.cpu" class="info-item">
          <icon-code-square />
          <span>{{ record.cpu }}</span>
        </div>
        <div v-if="record.gpu" class="info-item">
          <icon-computer />
          <span>{{ record.gpu }}</span>
        </div>
        <div v-if="record.machineCount" class="info-item">
          <icon-desktop />
          <span>{{ record.machineCount }} machines</span>
        </div>
      </div>
    </template> -->

    <template #stats="{ record }">
      <div class="stats-info">
        <a-space :size="8">
          <a-tooltip content="TEST CASE COUNT">
            <a-tag size="small">
              <icon-file />
              {{ record.testCaseCount }}
            </a-tag>
          </a-tooltip>
          <a-tooltip content="USE COUNT">
            <a-tag size="small" color="blue">
              <icon-eye />
              {{ record.useCount }}
            </a-tag>
          </a-tooltip>
        </a-space>
      </div>
    </template>

    <template #action="{ record }">
      <a-space>
        <a-link title="PREVIEW" @click="emit('preview', record)">
          <icon-eye />
          PREVIEW
        </a-link>
        <!-- <a-link title="使用" @click="emit('use', record)">
          <icon-check-circle />
          使用
        </a-link> -->
        <a-link title="EDIT" @click="emit('update', record)">
          <icon-edit />
          EDIT
        </a-link>
        <a-link status="danger" title="DELETE" @click="emit('delete', record)">
          <icon-delete />
          DELETE
        </a-link>
      </a-space>
    </template>
  </GiTable>
</template>

<script setup lang="ts">
import { CATEGORY_OPTIONS, STATUS_OPTIONS } from '../types'
import type { QueryForm } from '../types'
import type { SavedPlanResp } from '@/apis/tpgen'
import type { Columns, Options } from '@/components/GiForm'
import type { TableInstanceColumns } from '@/components/GiTable/type'

interface Props {
  dataList: SavedPlanResp[]
  loading: boolean
  pagination: any
  selectedKeys: (string | number)[]
  queryForm: QueryForm
  highlightId?: string  // 需要高亮的行 ID
}

const props = defineProps<Props>()

// 为高亮行添加 CSS 类
const getRowClass = (record: SavedPlanResp) => {
  return record.id === props.highlightId ? 'highlight-row' : ''
}

const emit = defineEmits<{
  'refresh': []
  'search': []
  'reset': []
  'batch-delete': []
  'preview': [record: SavedPlanResp]
  'use': [record: SavedPlanResp]
  'update': [record: SavedPlanResp]
  'delete': [record: SavedPlanResp]
  'update:queryForm': [value: any]
  'update:selectedKeys': [keys: (string | number)[]]
}>()

const handleQueryFormUpdate = (value: any) => {
  emit('update:queryForm', value)
}

// 处理表格行选择
const handleSelect = (rowKeys: (string | number)[]) => {
  emit('update:selectedKeys', rowKeys)
}

// 处理全选/取消全选
const handleSelectAll = (checked: boolean) => {
  if (checked) {
    emit('update:selectedKeys', props.dataList.map(item => item.id))
  } else {
    emit('update:selectedKeys', [])
  }
}

const options: Options = reactive({
  form: { layout: 'inline' },
  grid: { cols: { xs: 1, sm: 1, md: 2, lg: 3, xl: 3, xxl: 3 } },
  fold: { enable: true, index: 2, defaultCollapsed: true },
})

const queryFormColumns: Columns = reactive([
  {
    type: 'input',
    field: 'name',
    formItemProps: {
      hideLabel: true,
    },
    props: {
      placeholder: 'search by name',
    },
  },
  {
    type: 'select',
    field: 'status',
    formItemProps: {
      hideLabel: true,
    },
    props: {
      placeholder: 'select status',
      options: STATUS_OPTIONS,
      allowClear: true,
    },
  },
])

const columns: TableInstanceColumns[] = [
  {
    title: 'PLAN NAME',
    dataIndex: 'name',
    slotName: 'name',
    width: 200,
    ellipsis: true,
    tooltip: true,
  },
  // {
  //   title: 'HARDWARE CONFIGURATION',
  //   dataIndex: 'hardware',
  //   slotName: 'hardware',
  //   width: 250,
  // },
  {
    title: 'STATS',
    dataIndex: 'stats',
    slotName: 'stats',
    width: 120,
  },
  // 标签列暂时隐藏
  // {
  //   title: '标签',
  //   dataIndex: 'tags',
  //   slotName: 'tags',
  //   width: 180,
  //   ellipsis: true,
  //   tooltip: true,
  // },
  {
    title: 'STATUS',
    dataIndex: 'status',
    slotName: 'status',
    width: 100,
  },
  {
    title: 'CREATOR',
    dataIndex: 'createUserString',
    slotName: 'createUserString',
    width: 120,
  },
  {
    title: 'CREATE TIME',
    dataIndex: 'createTime',
    slotName: 'createTime',
    width: 180,
  },
  {
    title: 'ACTION',
    slotName: 'action',
    fixed: 'right',
    width: 240,
  },
]

const rowSelection = reactive({
  type: 'checkbox',
  showCheckedAll: true,
  onlyCurrent: false,
})
</script>

<style scoped lang="scss">
.hardware-info {
  display: flex;
  flex-direction: column;
  gap: 4px;

  .info-item {
    display: flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    color: var(--color-text-2);

    .arco-icon {
      font-size: 14px;
    }
  }
}

.stats-info {
  .arco-tag {
    display: inline-flex;
    align-items: center;
    gap: 4px;
  }
}

// 高亮行样式
:deep(.highlight-row) {
  background-color: rgba(var(--primary-6), 0.1) !important;
  animation: highlight-fade 3s ease-out forwards;
  
  td {
    background-color: rgba(var(--primary-6), 0.1) !important;
  }
}

@keyframes highlight-fade {
  0% {
    background-color: rgba(var(--primary-6), 0.2);
  }
  100% {
    background-color: transparent;
  }
}
</style>
