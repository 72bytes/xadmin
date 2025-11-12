import http from '@/utils/http'

/**
 * 验证响应接口
 */
export interface ValidationResponse {
  success: boolean
  error?: {
    code: string
    message: string
    key?: string
    lineNumber?: number
  }
}

/**
 * YAML 兼容性验证
 * @param yamlData YAML 数据对象
 * @returns ValidationResponse 验证结果
 */
export async function validateYaml(yamlData: any): Promise<ValidationResponse> {
  const response = await http.post<ValidationResponse>('/system/yaml/validate', { yamlData })
  return response.data // ← 关键：提取 data 字段
}
