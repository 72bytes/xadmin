/**
 * 机器数据管理 Composable
 * 统一管理从数据库获取的真实机器数据
 */

import { computed, ref } from 'vue'
import { Message } from '@arco-design/web-vue'
import type { Machine } from '../types'
import * as tpdbApi from '@/apis/tpdb'

// 全局机器数据缓存
const machinesCache = ref<Machine[]>([])
const loading = ref(false)
const loaded = ref(false)

export function useMachines() {
  /**
   * 加载机器数据
   */
  const loadMachines = async (force = false) => {
    // 如果已加载且不是强制刷新，直接返回缓存
    if (loaded.value && !force) {
      return machinesCache.value
    }

    loading.value = true
    try {
      const response = await tpdbApi.listSutDevices({ page: 1, size: 500 })
      if (response.success && response.data) {
        // 转换数据格式，兼容旧的 Machine 接口
        machinesCache.value = (response.data.list || []).map((device) => ({
          id: device.id,
          hostname: device.hostname,
          asicName: device.asicName,
          ipAddress: device.ipAddress,
          deviceId: device.deviceId,
          revId: device.revId,
          gpuSeries: device.gpuSeries,
          gpuModel: device.gpuModel,
          createdAt: device.createdAt,
          updatedAt: device.updatedAt,
          // 兼容旧字段
          name: device.hostname,
          gpu: device.gpuSeries || device.gpuModel || '',
          status: 'Available' as const,
        }))
        loaded.value = true
        console.log('[useMachines] 机器数据加载成功:', machinesCache.value.length, '台')
      }
      return machinesCache.value
    } catch (error) {
      console.error('[useMachines] 加载机器数据失败:', error)
      Message.error('加载机器数据失败')
      return []
    } finally {
      loading.value = false
    }
  }

  /**
   * 根据 ID 获取机器
   */
  const getMachineById = (id: number): Machine | undefined => {
    return machinesCache.value.find((m) => m.id === id)
  }

  /**
   * 根据 GPU 系列过滤机器
   */
  const getMachinesByGpu = (gpuSeries: string): Machine[] => {
    if (!gpuSeries) return machinesCache.value
    return machinesCache.value.filter((m) =>
      m.gpuSeries === gpuSeries
      || m.gpuModel === gpuSeries
      || m.gpu === gpuSeries,
    )
  }

  /**
   * 根据 ID 获取机器名称
   */
  const getMachineName = (id: number): string => {
    const machine = getMachineById(id)
    return machine?.hostname || machine?.name || `Machine ${id}`
  }

  /**
   * 批量获取机器信息
   */
  const getMachinesByIds = (ids: number[]): Machine[] => {
    return machinesCache.value.filter((m) => ids.includes(m.id))
  }

  return {
    machines: computed(() => machinesCache.value),
    loading: computed(() => loading.value),
    loaded: computed(() => loaded.value),
    loadMachines,
    getMachineById,
    getMachinesByGpu,
    getMachineName,
    getMachinesByIds,
  }
}
