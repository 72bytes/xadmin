<template>
  <div class="table-page">
    <a-row justify="space-between" align="center" class="header page_header">
      <a-space wrap>
        <div class="title">My Test Plans</div>
      </a-space>
    </a-row>

    <a-row class="h-full page_content">
      <a-col :span="24" class="h-full ov-hidden">
        <PlanTable
          v-model:query-form="queryForm"
          v-model:selected-keys="selectedKeys"
          :data-list="dataList"
          :loading="loading"
          :pagination="pagination"
          :highlight-id="highlightId"
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
import { ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import PlanTable from './components/PlanTable.vue'
import PlanPreviewDrawer from './components/PlanPreviewDrawer.vue'
import PlanEditModal from './components/PlanEditModal.vue'
import { usePlanData, usePlanDelete, usePlanEdit, usePlanPreview, usePlanUsage } from './composables/usePlanData'
import { useResetReactive } from '@/hooks'
import { useUserStore } from '@/stores'

defineOptions({ name: 'MyTestPlans' })

// 获取路由信息
const route = useRoute()

// 获取当前用户信息
const userStore = useUserStore()

// 高亮 ID（从 URL 查询参数获取）
const highlightId = ref<string>('')

// 查询表单 - 只显示当前用户创建的测试计划
const [queryForm, resetForm] = useResetReactive({
  createUser: Number(userStore.userInfo.id),  // 设置创建人为当前用户
  sort: ['createTime,desc'],
})

// 数据管理
const { loading, dataList, pagination, selectedKeys, search, refresh } = usePlanData(queryForm)

// 监听路由查询参数的变化，更新高亮 ID
watch(
  () => route.query.highlight,
  (newHighlight) => {
    if (newHighlight) {
      highlightId.value = String(newHighlight)
      // 3秒后清除高亮效果
      setTimeout(() => {
        highlightId.value = ''
      }, 3000)
    }
  },
  { immediate: true }
)

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
