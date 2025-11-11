/**
 * Case Editor Type Definitions
 */

/** 文件树节点 */
export interface FileNode {
  path: string
  name: string
  type: 'file' | 'folder'
  children?: FileNode[]
}

/** 文件内容 */
export interface FileContent {
  path: string
  content: string
  language?: string
}

/** Casespace 项 */
export interface CasespaceItem {
  name: string
  path: string
}

/** Case 项 */
export interface CaseItem {
  name: string
  path: string
}

/** 编辑器标签页 */
export interface EditorTab {
  id: string
  filePath: string
  fileName: string
  content: string
  language?: string
  isModified: boolean
  originalContent: string
}

/** 保存文件请求 */
export interface SaveFileRequest {
  path: string
  content: string
}

/** 创建文件请求 */
export interface CreateFileRequest {
  parentPath: string
  name: string
}

/** 创建文件夹请求 */
export interface CreateFolderRequest {
  parentPath: string
  name: string
}

/** 重命名请求 */
export interface RenameRequest {
  oldPath: string
  newName: string
}

/** 上传文件项 */
export interface UploadFileItem {
  name: string
  content: string
}

/** 上传文件请求 */
export interface UploadFilesRequest {
  parentPath: string
  files: UploadFileItem[]
}

/** 对话框类型 */
export type DialogType = 'createFile' | 'createFolder' | 'rename' | 'delete' | 'upload' | 'uploadCase' | 'deleteCase' | null

/** 语言类型映射 */
export const LANGUAGE_MAP: Record<string, string> = {
  '.json': 'json',
  '.yaml': 'yaml',
  '.yml': 'yaml',
  '.py': 'python',
  '.sh': 'shell',
  '.bash': 'shell',
  '.zsh': 'shell',
  '.js': 'javascript',
  '.ts': 'typescript',
  '.jsx': 'javascript',
  '.tsx': 'typescript',
  '.html': 'html',
  '.css': 'css',
  '.xml': 'xml',
  '.sql': 'sql',
  '.md': 'markdown',
  '.txt': 'text',
}

/**
 * 从文件名获取语言类型
 */
export function getLanguageFromFileName(fileName: string): string | undefined {
  const ext = fileName.substring(fileName.lastIndexOf('.')).toLowerCase()
  return LANGUAGE_MAP[ext]
}

