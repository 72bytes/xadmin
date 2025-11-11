/**
 * Case Editor API Service
 */
import http from '@/utils/http'
import type {
  CasespaceItem,
  CaseItem,
  FileNode,
  FileContent,
  SaveFileRequest,
  CreateFileRequest,
  CreateFolderRequest,
  RenameRequest,
  UploadFilesRequest,
} from './caseeditor-type'

export * from './caseeditor-type'

const BASE_URL = '/case/caseeditor'

/**
 * 获取所有 casespace 列表
 */
export function getCasespaces() {
  return http.get<CasespaceItem[]>(`${BASE_URL}/casespaces`)
}

/**
 * 获取指定 casespace 的 case 列表
 */
export function getCases(casespace: string) {
  return http.get<CaseItem[]>(`${BASE_URL}/casespaces/${casespace}/cases`)
}

/**
 * 获取文件树
 */
export function getFileTree(params: {
  casespace?: string
  case?: string
  path?: string
}) {
  return http.get<FileNode[]>(`${BASE_URL}/files`, params)
}

/**
 * 获取文件内容
 */
export function getFileContent(path: string) {
  return http.get<FileContent>(`${BASE_URL}/files/content`, { path })
}

/**
 * 保存文件
 */
export function saveFile(data: SaveFileRequest) {
  return http.post(`${BASE_URL}/files/save`, data)
}

/**
 * 创建文件
 */
export function createFile(data: CreateFileRequest) {
  return http.post<FileNode>(`${BASE_URL}/files/create`, data)
}

/**
 * 创建文件夹
 */
export function createFolder(data: CreateFolderRequest) {
  return http.post<FileNode>(`${BASE_URL}/folders/create`, data)
}

/**
 * 重命名文件或文件夹
 */
export function renameItem(data: RenameRequest) {
  return http.put<FileNode>(`${BASE_URL}/files/rename`, data)
}

/**
 * 删除文件或文件夹
 */
export function deleteItem(path: string) {
  return http.del(`${BASE_URL}/files`, undefined, { params: { path } })
}

/**
 * 批量上传文件
 */
export function uploadFiles(data: UploadFilesRequest) {
  return http.post(`${BASE_URL}/files/upload`, data)
}

/**
 * 删除 case
 */
export function deleteCase(casespace: string, caseName: string) {
  return http.del(`${BASE_URL}/casespaces/${casespace}/cases/${caseName}`)
}

/**
 * 上传 case 压缩包
 */
export function uploadCase(casespace: string, caseName: string, file: File) {
  const formData = new FormData()
  formData.append('file', file)
  formData.append('case_name', caseName)
  
  // 不要手动设置 Content-Type，让浏览器自动设置（包括 boundary）
  return http.post(`${BASE_URL}/casespaces/${casespace}/upload-case`, formData)
}

/**
 * 下载 case 压缩包
 */
export function downloadCase(casespace: string, caseName: string) {
  return http.download(`${BASE_URL}/casespaces/${casespace}/cases/${caseName}/download`)
}

