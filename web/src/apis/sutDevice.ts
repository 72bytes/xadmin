import http from '@/utils/http'

/**
 * 选项接口
 */
export interface OptionItem {
  label: string
  value: string
}

/**
 * SUT 设备接口
 */
export interface SutDevice {
  id: number
  hostname: string
  asic_name?: string
  ip_address?: string
  device_id?: string
  rev_id?: string
  gpu_series?: string
  gpu_model?: string
}

/**
 * 设备列表查询参数
 */
export interface DeviceQueryParams {
  asic_name?: string
  gpu_series?: string
  gpu_model?: string
  hostname?: string
}

/**
 * 获取 GPU 选项列表（ASIC 名称）
 */
export async function getGpuOptions(): Promise<OptionItem[]> {
  const res = await http.get<OptionItem[]>('/system/sut/device/gpu-options')
  return res.data || []
}

/**
 * 获取 GPU 系列选项
 */
export async function getGpuSeriesOptions(): Promise<OptionItem[]> {
  const res = await http.get<OptionItem[]>('/system/sut/device/gpu-series-options')
  return res.data || []
}

/**
 * 获取 GPU 型号选项
 */
export async function getGpuModelOptions(): Promise<OptionItem[]> {
  const res = await http.get<OptionItem[]>('/system/sut/device/gpu-model-options')
  return res.data || []
}

/**
 * 获取设备列表
 */
export async function getDevices(params?: DeviceQueryParams): Promise<SutDevice[]> {
  const res = await http.get<SutDevice[]>('/system/sut/device/devices', params)
  return res.data || []
}
