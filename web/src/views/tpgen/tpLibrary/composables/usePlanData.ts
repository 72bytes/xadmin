import { computed, ref, type Ref } from 'vue'
import { Message, Modal } from '@arco-design/web-vue'
import { useRouter } from 'vue-router'
import type { QueryForm } from '../types'
import type { SavedPlanResp } from '@/apis/tpgen'
import { addSavedPlan, deleteSavedPlan, getSavedPlan, listSavedPlan, useSavedPlan } from '@/apis/tpgen'
import { useTable } from '@/hooks'
import { useTpgenStore } from '@/stores'

/**
 * 测试计划库数据管理 - 仅显示公共测试计划（status=2）
 */
export function usePlanData(queryForm: QueryForm) {
  // 表格数据管理
  const { loading, tableData, pagination, selectedKeys, search: tableSearch, refresh } = useTable(
    (params) =>
      listSavedPlan({
        ...params,
        ...queryForm,
        status: 2, // 只查询公共的测试计划
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
 * 生成时间戳字符串（用于文件名或命名）
 * @returns {string} 格式：YYYYMMDDHHmmss
 */
const getTimestamp = () => {
  const now = new Date()
  const year = now.getFullYear()
  const month = String(now.getMonth() + 1).padStart(2, '0')
  const day = String(now.getDate()).padStart(2, '0')
  const hours = String(now.getHours()).padStart(2, '0')
  const minutes = String(now.getMinutes()).padStart(2, '0')
  const seconds = String(now.getSeconds()).padStart(2, '0')
  return `${year}${month}${day}${hours}${minutes}${seconds}`
}

/**
 * 复制计划到我的测试计划功能
 */
export function usePlanCopy(refresh: () => void) {
  const router = useRouter()

  const onCopy = async (record: SavedPlanResp) => {
    try {
      Modal.confirm({
        title: 'Copy Test Plan',
        content: `Do you want to copy "${record.name}" to My Test Plans?`,
        okText: 'Confirm',
        cancelText: 'Cancel',
        onOk: async () => {
          try {
            // 获取完整的计划详情
            const detailRes = await getSavedPlan(record.id)
            if (detailRes.code !== 200) {
              Message.error('Failed to load plan details')
              return
            }

            const planData = detailRes.data as SavedPlanResp
            
            // 生成带时间戳的名称，防止重复
            const timestamp = getTimestamp()
            const newName = `${planData.name}_${timestamp}_COPY`
            
            // 创建新的私有计划
            const newPlan = {
              name: newName,
              category: planData.category,
              description: planData.description,
              configData: planData.configData,
              yamlData: planData.yamlData,
              cpu: planData.cpu,
              gpu: planData.gpu,
              machineCount: planData.machineCount,
              osType: planData.osType,
              kernelType: planData.kernelType,
              testCaseCount: planData.testCaseCount,
              status: 1, // 设置为私有
              tags: planData.tags,
            }

            const res = await addSavedPlan(newPlan)
            if (res.code === 200) {
              // 调用使用接口，增加原test plan的使用计数
              await useSavedPlan(record.id)
              
              Message.success('Successfully copied to My Test Plans')
              
              // 跳转到 MyTestPlan 页面，并传递新创建的计划 ID 用于高亮
              const newPlanId = res.data?.id || res.data
              router.push({
                path: '/tpgen/my-plans',
                query: { highlight: newPlanId }
              })
            } else {
              Message.error(res.data || 'Copy failed')
            }
          } catch (error) {
            Message.error('Copy failed')
            console.error(error)
          }
        },
      })
    } catch (error) {
      Message.error('Operation failed')
      console.error(error)
    }
  }

  return {
    onCopy,
  }
}

/**
 * 编辑计划功能（仅管理员）
 */
export function usePlanEdit(refresh: () => void) {
  const router = useRouter()
  const tpgenStore = useTpgenStore()

  const onUpdate = async (record: SavedPlanResp) => {
    try {
      // 获取完整的计划详情数据
      const res = await getSavedPlan(record.id)
      if (res.code === 200) {
        // 设置编辑模式并保存完整数据
        tpgenStore.setEditMode(res.data as SavedPlanResp)
        // 跳转到 Online 页面
        router.push({ path: '/tpgen/online' })
      } else {
        Message.error('Failed to load plan details')
      }
    } catch (error) {
      Message.error('Failed to load plan details')
      console.error(error)
    }
  }

  return {
    onUpdate,
  }
}

/**
 * 删除计划功能（仅管理员）
 */
export function usePlanDelete(refresh: () => void, selectedKeys: Ref<(string | number)[]>) {
  const handleDelete = async (deleteFn: () => Promise<any>, tip: string) => {
    Modal.confirm({
      title: 'Confirm Delete',
      content: tip,
      onOk: async () => {
        try {
          const res = await deleteFn()
          if (res.code === 200) {
            Message.success('Deleted successfully')
            refresh()
          } else {
            Message.error(res.data || 'Delete failed')
          }
        } catch (error) {
          Message.error('Delete failed')
          console.error(error)
        }
      },
    })
  }

  const handleBatchDelete = async (deleteFn: () => Promise<any>) => {
    if (selectedKeys.value.length === 0) {
      Message.warning('Please select data to delete first')
      return
    }

    Modal.confirm({
      title: 'Confirm Delete',
      content: `Are you sure to delete ${selectedKeys.value.length} selected item(s)?`,
      onOk: async () => {
        try {
          const res = await deleteFn()
          if (res.code === 200) {
            Message.success('Deleted successfully')
            selectedKeys.value = []
            refresh()
          } else {
            Message.error(res.data || 'Delete failed')
          }
        } catch (error) {
          Message.error('Delete failed')
          console.error(error)
        }
      },
    })
  }

  const onDelete = (record: SavedPlanResp) => {
    handleDelete(() => deleteSavedPlan(record.id), `Are you sure to delete test plan "${record.name}"?`)
  }

  const onBatchDelete = () => {
    handleBatchDelete(() => deleteSavedPlan(selectedKeys.value.join(',')))
  }

  return {
    onDelete,
    onBatchDelete,
  }
}

