/**
 * Case Browser API Service
 */
import http from '@/utils/http'
import type {
  CaseMetadata,
  CaseDetail,
  AddTagRequest,
  AddOptionRequest,
  UpdateOptionRequest,
} from './casebrowser-type'

export * from './casebrowser-type'

const BASE_URL = '/case/casebrowser'

/**
 * 获取指定 casespace 下所有 case 的元数据（包含 tags）
 */
export function getCasesMetadata(casespace: string) {
  return http.get<CaseMetadata[]>(`${BASE_URL}/casespaces/${casespace}/cases`)
}

/**
 * 获取单个 case 的详细信息，包含 tags 和 options
 */
export function getCaseDetail(casespace: string, caseName: string) {
  return http.get<CaseDetail>(`${BASE_URL}/casespaces/${casespace}/cases/${caseName}`)
}

/**
 * 添加 tag 到 case
 */
export function addTag(data: AddTagRequest) {
  return http.post(`${BASE_URL}/cases/tags`, data)
}

/**
 * 删除 case 的 tag
 */
export function deleteTag(casespace: string, caseName: string, tag: string) {
  return http.del(`${BASE_URL}/cases/tags`, undefined, {
    params: { casespace, case_name: caseName, tag }
  })
}

/**
 * 添加 option 到 case
 */
export function addOption(data: AddOptionRequest) {
  return http.post(`${BASE_URL}/cases/options`, data)
}

/**
 * 更新 case 的 option
 */
export function updateOption(data: UpdateOptionRequest) {
  return http.put(`${BASE_URL}/cases/options`, data)
}

/**
 * 删除 case 的 option
 */
export function deleteOption(casespace: string, caseName: string, key: string) {
  return http.del(`${BASE_URL}/cases/options`, undefined, {
    params: { casespace, case_name: caseName, key }
  })
}

