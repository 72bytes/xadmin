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
  asicName?: string
  productName?: string
  ipAddress?: string
  deviceId?: string
  revId?: string
  gpuSeries?: string
  gpuModel?: string
  createdAt?: string
  updatedAt?: string
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

/**
 * 获取产品系列名称列表
 */
export async function getProductNames(): Promise<OptionItem[]> {
  const res = await http.get<OptionItem[]>('/tp/api/sut-device/product-names')
  return res.data || []
}

/**
 * 获取 ASIC 名称列表（可选根据 productName 过滤）
 */
export async function getAsicNames(productName?: string): Promise<OptionItem[]> {
  const params = productName ? { productName } : {}
  const res = await http.get<OptionItem[]>('/tp/api/sut-device/asic-names', params)
  return res.data || []
}

/**
 * 根据 productName 和 asicName 获取机器列表
 */
export async function getMachinesBySelection(productName?: string, asicName?: string): Promise<SutDevice[]> {
  const params: any = {}
  if (productName) params.productName = productName
  if (asicName) params.asicName = asicName
  const res = await http.get<SutDevice[]>('/tp/api/sut-device/machines', params)
  return res.data || []
}