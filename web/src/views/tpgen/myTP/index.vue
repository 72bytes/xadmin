<template>
  <div class="table-page">
    <a-row justify="space-between" align="center" class="header page_header">
      <a-space wrap>
        <div class="title">我的测试计划</div>
      </a-space>
    </a-row>
    
    <a-row class="h-full page_content">
      <a-col :span="24" class="h-full ov-hidden">
        <PlanTable
          :data-list="dataList"
          :loading="loading"
          :pagination="pagination"
          :selected-keys="selectedKeys"
          v-model:query-form="queryForm"
          @refresh="search"
          @search="search"
          @reset="reset"
          @batch-delete="onBatchDelete"
          @preview="onPreview"
          @use="onUse"
          @update="onUpdate"
          @delete="onDelete"
        />
      </a-col>
    </a-row>

    <!-- 预览抽屉 -->
    <PlanPreviewDrawer
      v-model="previewDrawerVisible"
      :record="currentRecord"
    />

    <!-- 编辑对话框 -->
    <PlanEditModal
      v-model="editModalVisible"
      :form="editForm"
      @ok="handleUpdateConfirm"
      @cancel="handleUpdateCancel"
    />
  </div>
</template>

<script setup lang="ts">
import { useResetReactive } from '@/hooks'
import PlanTable from './components/PlanTable.vue'
import PlanPreviewDrawer from './components/PlanPreviewDrawer.vue'
import PlanEditModal from './components/PlanEditModal.vue'
import { usePlanData, usePlanPreview, usePlanUsage, usePlanEdit, usePlanDelete } from './composables/usePlanData'

defineOptions({ name: 'MyTestPlans' })

// 查询表单
const [queryForm, resetForm] = useResetReactive({
  sort: ['createTime,desc'],
})

// 数据管理
const { loading, dataList, pagination, selectedKeys, search, refresh } = usePlanData(queryForm)

// 重置
const reset = () => {
  resetForm()
  search()
}

// 预览功能
const { previewDrawerVisible, currentRecord, onPreview } = usePlanPreview()

// 使用功能
const { onUse } = usePlanUsage()

// 编辑功能
const { editModalVisible, editForm, onUpdate, handleUpdateConfirm, handleUpdateCancel } = usePlanEdit(search)

// 删除功能
const { onDelete, onBatchDelete } = usePlanDelete(refresh, selectedKeys)

// 初始化
onMounted(() => {
  search()
})
</script>

<style scoped lang="scss">
@import './index.scss';
</style>
