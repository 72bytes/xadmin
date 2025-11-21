<template>
  <GiTable
    row-key="id"
    :data="dataList"
    :columns="columns"
    :loading="loading"
    :scroll="{ x: '100%', y: '100%', minWidth: 1800 }"
    :pagination="pagination"
    :row-selection="isAdmin ? rowSelection : undefined"
    :selected-keys="selectedKeys"
    :disabled-tools="['size']"
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

    <template v-if="isAdmin" #toolbar-left>
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

    <template #stats="{ record }">
      <div class="stats-info">
        <a-space :size="8">
          <a-tooltip content="TEST CASE COUNT">
            <a-tag size="small">
              <icon-file />
              {{ record.testCaseCount }}
            </a-tag>
          </a-tooltip>
          <a-tooltip content="REFERENCE COUNT">
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
        <a-link title="COPY" @click="emit('copy', record)">
          <icon-copy />
          COPY
        </a-link>
        <template v-if="isAdmin">
          <a-link title="EDIT" @click="emit('update', record)">
            <icon-edit />
            EDIT
          </a-link>
          <a-link status="danger" title="DELETE" @click="emit('delete', record)">
            <icon-delete />
            DELETE
          </a-link>
        </template>
      </a-space>
    </template>
  </GiTable>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { QueryForm } from '../types'
import type { SavedPlanResp } from '@/apis/tpgen'
import type { Columns, Options } from '@/components/GiForm'
import type { TableInstanceColumns } from '@/components/GiTable/type'
import { useUserStore } from '@/stores'

interface Props {
  dataList: SavedPlanResp[]
  loading: boolean
  pagination: any
  selectedKeys: (string | number)[]
  queryForm: QueryForm
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'refresh': []
  'search': []
  'reset': []
  'batch-delete': []
  'preview': [record: SavedPlanResp]
  'copy': [record: SavedPlanResp]
  'update': [record: SavedPlanResp]
  'delete': [record: SavedPlanResp]
  'update:queryForm': [value: any]
  'update:selectedKeys': [keys: (string | number)[]]
}>()

// 检查是否为管理员
const userStore = useUserStore()
const isAdmin = computed(() => userStore.roles.includes('admin'))

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
  grid: { cols: { xs: 1, sm: 1, md: 2, lg: 3, xl: 2, xxl: 2 } },
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
  {
    title: 'STATS',
    dataIndex: 'stats',
    slotName: 'stats',
    width: 120,
  },
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
    width: isAdmin.value ? 300 : 200,
  },
]

const rowSelection = reactive({
  type: 'checkbox',
  showCheckedAll: true,
  onlyCurrent: false,
})
</script>

<style scoped lang="scss">
.stats-info {
  .arco-tag {
    display: inline-flex;
    align-items: center;
    gap: 4px;
  }
}
</style>

