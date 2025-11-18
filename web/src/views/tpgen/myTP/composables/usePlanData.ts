import { computed, ref, type Ref } from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import type { EditForm, QueryForm } from '../types'
import type { SavedPlanResp } from '@/apis/tpgen'
import { deleteSavedPlan, getSavedPlan, listSavedPlan, updateSavedPlan, useSavedPlan } from '@/apis/tpgen'
import { useTable } from '@/hooks'

/**
 * 测试计划数据管理
 */
export function usePlanData(queryForm: QueryForm) {
  // 表格数据管理
  const { loading, tableData, pagination, selectedKeys, search: tableSearch, refresh } = useTable(
    (params) =>
      listSavedPlan({
        ...params,
        ...queryForm,
      }),
  )

  const dataList = computed(() => tableData.value as unknown as SavedPlanResp[])

  // 搜索
  const search = () => {
    tableSearch()
  }

  return {
    loading,
    dataList,
    pagination,
    selectedKeys,
    search,
    refresh,
  }
}

/**
 * 预览功能
 */
export function usePlanPreview() {
  const previewDrawerVisible = ref(false)
  const currentRecord = ref<SavedPlanResp | null>(null)

  const onPreview = async (record: SavedPlanResp) => {
    try {
      const res = await getSavedPlan(record.id)
      if (res.code === 200) {
        currentRecord.value = res.data as SavedPlanResp
        previewDrawerVisible.value = true
      } else {
        Message.error(String(res.data) || '获取详情失败')
      }
    } catch (error) {
      Message.error('获取详情失败')
      console.error(error)
    }
  }

  return {
    previewDrawerVisible,
    currentRecord,
    onPreview,
  }
}

/**
 * 使用计划功能
 */
export function usePlanUsage() {
  const onUse = async (record: SavedPlanResp) => {
    try {
      Modal.info({
        title: '使用测试计划',
        content: `即将加载配置 "${record.name}"，这将替换当前的表单数据。是否继续？`,
        okText: '确认',
        cancelText: '取消',
        onOk: async () => {
          // 调用使用接口，增加使用计数
          await useSavedPlan(record.id)

          // 获取完整配置
          const res = await getSavedPlan(record.id)
          if (res.code === 200) {
            // 这里可以触发一个事件或路由跳转到在线生成页面，并加载配置
            // 暂时先提示成功
            Message.success('配置已加载，请前往在线生成页面')
            // TODO: 实现配置加载逻辑
          } else {
            Message.error(String(res.data) || '加载配置失败')
          }
        },
      })
    } catch (error) {
      Message.error('操作失败')
      console.error(error)
    }
  }

  return {
    onUse,
  }
}

/**
 * 编辑计划功能
 */
export function usePlanEdit(refresh: () => void) {
  const editModalVisible = ref(false)
  const editForm = ref<EditForm | null>(null)
  const editingId = ref<string>('')

  const onUpdate = (record: SavedPlanResp) => {
    editingId.value = record.id
    editForm.value = {
      name: record.name,
      category: record.category,
      description: record.description,
      tags: record.tags,
      status: record.status,
    }
    editModalVisible.value = true
  }

  const handleUpdateConfirm = async () => {
    if (!editForm.value?.name) {
      Message.warning('请输入计划名称')
      return
    }
    if (!editForm.value?.category) {
      Message.warning('请选择类别')
      return
    }

    try {
      const res = await updateSavedPlan(editForm.value, editingId.value)
      if (res.code === 200) {
        Message.success('修改成功')
        editModalVisible.value = false
        refresh()
      } else {
        Message.error(res.data || '修改失败')
      }
    } catch (error) {
      Message.error('修改失败')
      console.error(error)
    }
  }

  const handleUpdateCancel = () => {
    editModalVisible.value = false
    editForm.value = null
  }

  return {
    editModalVisible,
    editForm,
    onUpdate,
    handleUpdateConfirm,
    handleUpdateCancel,
  }
}

/**
 * 删除计划功能
 */
export function usePlanDelete(refresh: () => void, selectedKeys: Ref<(string | number)[]>) {
  const handleDelete = async (deleteFn: () => Promise<any>, tip: string) => {
    Modal.confirm({
      title: '确认删除',
      content: tip,
      onOk: async () => {
        try {
          const res = await deleteFn()
          if (res.code === 200) {
            Message.success('删除成功')
            refresh()
          } else {
            Message.error(res.data || '删除失败')
          }
        } catch (error) {
          Message.error('删除失败')
          console.error(error)
        }
      },
    })
  }

  const handleBatchDelete = async (deleteFn: () => Promise<any>) => {
    if (selectedKeys.value.length === 0) {
      Message.warning('请先选择要删除的数据')
      return
    }

    Modal.confirm({
      title: '确认删除',
      content: `确认删除选中的 ${selectedKeys.value.length} 条数据吗？`,
      onOk: async () => {
        try {
          const res = await deleteFn()
          if (res.code === 200) {
            Message.success('删除成功')
            selectedKeys.value = []
            refresh()
          } else {
            Message.error(res.data || '删除失败')
          }
        } catch (error) {
          Message.error('删除失败')
          console.error(error)
        }
      },
    })
  }

  const onDelete = (record: SavedPlanResp) => {
    handleDelete(() => deleteSavedPlan(record.id), `确认删除测试计划 "${record.name}" 吗？`)
  }

  const onBatchDelete = () => {
    handleBatchDelete(() => deleteSavedPlan(selectedKeys.value.join(',')))
  }

  return {
    onDelete,
    onBatchDelete,
  }
}
