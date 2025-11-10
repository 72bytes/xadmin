<template>
  <div class="table-page">
    <a-row justify="space-between" align="center" class="header page_header">
      <a-space wrap>
        <div class="title">测试计划</div>
      </a-space>
    </a-row>
    <a-row class="h-full page_content">
      <a-col :span="24" class="h-full ov-hidden">
        <GiTable
          row-key="id"
          :data="dataList"
          :columns="columns"
          :loading="loading"
          :scroll="{ x: '100%', y: '100%', minWidth: 1500 }"
          :pagination="pagination"
          :row-selection="rowSelection"
          :disabled-tools="['size']"
          @refresh="search"
        >
          <template #top>
            <GiForm v-model="queryForm" :options="options" :columns="queryFormColumns" @search="search" @reset="reset"></GiForm>
          </template>
          <template #toolbar-left>
            <a-button type="primary" @click="onAdd">
              <template #icon><icon-plus /></template>
              <template #default>新增</template>
            </a-button>
            <a-button :disabled="!selectedKeys.length" status="danger" @click="onBatchDelete">
              <template #icon><icon-delete /></template>
              <template #default>删除</template>
            </a-button>
          </template>
          <template #priority="{ record }">
            <a-tag v-if="record.priority === 1" color="red">高</a-tag>
            <a-tag v-else-if="record.priority === 2" color="orange">中</a-tag>
            <a-tag v-else color="blue">低</a-tag>
          </template>
          <template #status="{ record }">
            <a-tag v-if="record.status === 1" color="gray">未开始</a-tag>
            <a-tag v-else-if="record.status === 2" color="blue">进行中</a-tag>
            <a-tag v-else-if="record.status === 3" color="green">已完成</a-tag>
            <a-tag v-else color="red">已取消</a-tag>
          </template>
          <template #action="{ record }">
            <a-space>
              <a-link title="详情" @click="onDetail(record)">详情</a-link>
              <a-link title="修改" @click="onUpdate(record)">修改</a-link>
              <a-link status="danger" title="删除" @click="onDelete(record)">删除</a-link>
            </a-space>
          </template>
        </GiTable>
      </a-col>
    </a-row>

    <TestPlanAddModal ref="TestPlanAddModalRef" @save-success="search" />
    <TestPlanUpdateModal ref="TestPlanUpdateModalRef" @save-success="search" />
    <TestPlanDetailDrawer ref="TestPlanDetailDrawerRef" />
  </div>
</template>

<script setup lang="ts">
import TestPlanAddModal from './TestPlanAddModal.vue'
import TestPlanUpdateModal from './TestPlanUpdateModal.vue'
import TestPlanDetailDrawer from './TestPlanDetailDrawer.vue'
import { type TestPlanResp, deleteTestPlan, listTestPlan } from '@/apis/test/plan'
import type { Columns, Options } from '@/components/GiForm'
import type { TableInstanceColumns } from '@/components/GiTable/type'
import { useResetReactive, useTable } from '@/hooks'
import { Message, Modal } from '@arco-design/web-vue'

defineOptions({ name: 'TestPlan' })

const options: Options = reactive({
  form: { layout: 'inline' },
  grid: { cols: { xs: 1, sm: 1, md: 2, lg: 3, xl: 3, xxl: 3 } },
  fold: { enable: true, index: 1, defaultCollapsed: true },
})

const [queryForm, resetForm] = useResetReactive({
  sort: ['createTime,desc'],
})

const queryFormColumns: Columns = reactive([
  {
    type: 'input',
    field: 'name',
    formItemProps: {
      hideLabel: true,
    },
    props: {
      placeholder: '搜索名称',
    },
  },
  {
    type: 'input',
    field: 'code',
    formItemProps: {
      hideLabel: true,
    },
    props: {
      placeholder: '搜索编号',
    },
  },
  {
    type: 'select',
    field: 'status',
    options: [
      { label: '未开始', value: 1 },
      { label: '进行中', value: 2 },
      { label: '已完成', value: 3 },
      { label: '已取消', value: 4 },
    ],
    formItemProps: {
      hideLabel: true,
    },
    props: {
      placeholder: '请选择状态',
    },
  },
  {
    type: 'select',
    field: 'priority',
    options: [
      { label: '高', value: 1 },
      { label: '中', value: 2 },
      { label: '低', value: 3 },
    ],
    formItemProps: {
      hideLabel: true,
    },
    props: {
      placeholder: '请选择优先级',
    },
  },
])

const columns: TableInstanceColumns[] = reactive([
  { title: '名称', dataIndex: 'name', slotName: 'name', align: 'left', ellipsis: true, tooltip: true, width: 180 },
  { title: '编号', dataIndex: 'code', slotName: 'code', align: 'left', width: 150 },
  { title: '负责人', dataIndex: 'ownerName', slotName: 'ownerName', align: 'center', width: 120 },
  { title: '优先级', dataIndex: 'priority', slotName: 'priority', align: 'center', width: 100 },
  { title: '状态', dataIndex: 'status', slotName: 'status', align: 'center', width: 100 },
  { title: '开始时间', dataIndex: 'startTime', slotName: 'startTime', align: 'center', width: 180 },
  { title: '结束时间', dataIndex: 'endTime', slotName: 'endTime', align: 'center', width: 180 },
  { title: '创建时间', dataIndex: 'createTime', slotName: 'createTime', align: 'center', width: 180 },
  { title: '操作', slotName: 'action', align: 'center', fixed: 'right', width: 200 },
])

const {
  tableData: dataList,
  loading,
  pagination,
  selectedKeys,
  rowSelection,
  search,
  handleDelete,
} = useTable((data) => listTestPlan(data), { queryForm })

// 重置
const reset = () => {
  resetForm()
  search()
}

// 组件引用
const TestPlanAddModalRef = ref()
const TestPlanUpdateModalRef = ref()
const TestPlanDetailDrawerRef = ref()

// 新增
const onAdd = () => {
  TestPlanAddModalRef.value?.onOpen()
}

// 详情
const onDetail = (record: TestPlanResp) => {
  TestPlanDetailDrawerRef.value?.onOpen(record.id)
}

// 修改
const onUpdate = (record: TestPlanResp) => {
  TestPlanUpdateModalRef.value?.onOpen(record.id)
}

// 删除
const onDelete = (record: TestPlanResp) => {
  Modal.confirm({
    title: '删除确认',
    content: `确定要删除测试计划"${record.name}"吗？`,
    okText: '确定',
    cancelText: '取消',
    onOk: async () => {
      await handleDelete(() => deleteTestPlan(record.id))
    },
  })
}

// 批量删除
const onBatchDelete = () => {
  Modal.confirm({
    title: '批量删除确认',
    content: `确定要删除选中的 ${selectedKeys.value.length} 条测试计划吗？`,
    okText: '确定',
    cancelText: '取消',
    onOk: async () => {
      await handleDelete(() => deleteTestPlan(selectedKeys.value as string[]))
    },
  })
}
</script>

<style scoped lang="scss">
.table-page {
  height: 100%;
  display: flex;
  flex-direction: column;
}

.page_header {
  padding: 16px;
  background-color: var(--color-bg-2);
  margin-bottom: 14px;
  border-radius: 4px;
}

.page_content {
  flex: 1;
  overflow: hidden;
}

.title {
  font-size: 16px;
  font-weight: 500;
}
</style>

