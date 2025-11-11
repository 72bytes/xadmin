<template>
  <div class="case-editor">
    <EditorToolbar
      v-model:selected-casespace="selectedCasespace"
      v-model:selected-case="selectedCase"
      :casespaces="casespaces"
      :cases="cases"
      :active-tab="activeTab"
      :has-modified-files="hasModifiedFiles"
      :status-message="statusMessage"
      :status-type="statusType"
      @save="handleSave"
      @save-all="handleSaveAll"
      @upload="handleUploadClick"
      @delete-case="handleDeleteCaseClick"
      @upload-case="handleUploadCaseClick"
      @download-case="handleDownloadCaseClick"
    />

    <div class="editor-content">
      <div class="sidebar">
        <FileTree
          :file-tree="fileTree"
          :casespace="selectedCasespace"
          :case-name="selectedCase"
          @select="handleFileSelect"
          @action="handleFileAction"
        />
      </div>

      <div class="main-area">
        <EditorTabs
          :tabs="openTabs"
          :active-tab-id="activeTabId"
          @switch="handleTabSwitch"
          @close="handleTabClose"
        />

        <div class="editor-container">
          <div v-if="!activeTab" class="empty-editor">
            <icon-code />
            <p>请选择一个文件开始编辑</p>
          </div>
          <CodeEditor
            v-else
            :key="activeTab.id"
            :model-value="editingContent"
            :language="activeTab.language"
            @change="handleEditorChange"
          />
        </div>
      </div>
    </div>

    <!-- 文件操作对话框 -->
    <FileDialog
      v-model:visible="dialogVisible"
      :dialog-type="dialogType"
      :title="dialogTitle"
      :message="dialogMessage"
      :default-value="dialogDefaultValue"
      @confirm="handleDialogConfirm"
      @cancel="dialogVisible = false"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, onMounted, onUnmounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import EditorToolbar from './components/EditorToolbar.vue'
import FileTree from './components/FileTree.vue'
import EditorTabs from './components/EditorTabs.vue'
import CodeEditor from './components/CodeEditor.vue'
import FileDialog from './components/FileDialog.vue'
import * as caseEditorAPI from '@/apis/system/caseeditor'
import type {
  FileNode,
  EditorTab,
  DialogType,
  CasespaceItem,
  CaseItem,
} from '@/apis/system/caseeditor-type'
import { getLanguageFromFileName } from '@/apis/system/caseeditor-type'

// 状态管理
const casespaces = ref<CasespaceItem[]>([])
const cases = ref<CaseItem[]>([])
const selectedCasespace = ref<string>()
const selectedCase = ref<string>()
const fileTree = ref<FileNode[]>([])
const openTabs = ref<EditorTab[]>([])
const activeTabId = ref<string | null>(null)
const statusMessage = ref('')
const statusType = ref<'success' | 'error' | 'info' | 'warning'>('info')

// 临时编辑内容缓存，避免频繁更新响应式数组
const editingContent = ref<string>('')
let contentUpdateTimer: ReturnType<typeof setTimeout> | null = null

// 对话框状态
const dialogVisible = ref(false)
const dialogType = ref<DialogType>(null)
const dialogTitle = ref('')
const dialogMessage = ref('')
const dialogDefaultValue = ref('')
const currentActionNode = ref<FileNode | null>(null)

// 计算属性
const activeTab = computed(() => {
  return openTabs.value.find(tab => tab.id === activeTabId.value) || null
})

const hasModifiedFiles = computed(() => {
  return openTabs.value.some(tab => tab.isModified)
})

// 监听 activeTab 变化，自动同步编辑内容到 editingContent
watch(() => activeTab.value, (newTab) => {
  if (newTab) {
    editingContent.value = newTab.content
  } else {
    editingContent.value = ''
  }
}, { immediate: true })

// 加载 casespaces
const loadCasespaces = async () => {
  try {
    const { data } = await caseEditorAPI.getCasespaces()
    casespaces.value = data
    
    // 默认选中第一个 casespace
    if (data.length > 0 && !selectedCasespace.value) {
      selectedCasespace.value = data[0].name
    }
  }
  catch (error) {
    console.error('Failed to load casespaces:', error)
    Message.error('加载 Casespace 列表失败')
  }
}

// 加载 cases
const loadCases = async (casespace: string) => {
  try {
    const { data } = await caseEditorAPI.getCases(casespace)
    cases.value = data
  }
  catch (error) {
    console.error('Failed to load cases:', error)
    Message.error('加载 Case 列表失败')
  }
}

// 加载文件树
const loadFileTree = async () => {
  if (!selectedCasespace.value || !selectedCase.value) {
    fileTree.value = []
    return
  }

  try {
    const { data } = await caseEditorAPI.getFileTree({
      casespace: selectedCasespace.value,
      case: selectedCase.value,
      path: '/',
    })
    fileTree.value = data
  }
  catch (error) {
    console.error('Failed to load file tree:', error)
    Message.error('加载文件树失败')
  }
}

// 监听 casespace 变化
watch(selectedCasespace, async (newValue) => {
  cases.value = []
  selectedCase.value = undefined
  fileTree.value = []
  // 关闭所有标签
  openTabs.value = []
  activeTabId.value = null

  if (newValue) {
    await loadCases(newValue)
    // 默认选中第一个 case
    if (cases.value.length > 0 && !selectedCase.value) {
      selectedCase.value = cases.value[0].name
    }
  }
})

// 监听 case 变化
watch(selectedCase, async (newValue) => {
  fileTree.value = []
  // 关闭所有标签
  openTabs.value = []
  activeTabId.value = null

  if (newValue) {
    await loadFileTree()
  }
})

// 处理文件选择
const handleFileSelect = async (file: FileNode) => {
  if (file.type !== 'file')
    return

  // 检查是否已打开
  const existingTab = openTabs.value.find(tab => tab.filePath === file.path)
  if (existingTab) {
    handleTabSwitch(existingTab.id)
    return
  }

  try {
    // 获取文件内容
    const { data: fileContent } = await caseEditorAPI.getFileContent(file.path)

    // 创建新标签
    const newTab: EditorTab = {
      id: `tab-${Date.now()}`,
      filePath: file.path,
      fileName: file.name,
      content: fileContent.content,
      language: fileContent.language || getLanguageFromFileName(file.name),
      isModified: false,
      originalContent: fileContent.content,
    }

    openTabs.value.push(newTab)
    activeTabId.value = newTab.id
    // watch 会自动更新 editingContent
  }
  catch (error) {
    console.error('Failed to load file:', error)
    Message.error('加载文件失败')
  }
}

// 处理标签切换
const handleTabSwitch = (tabId: string) => {
  // 切换前，同步当前编辑内容到 openTabs
  if (activeTabId.value && contentUpdateTimer) {
    clearTimeout(contentUpdateTimer)
    const currentTab = openTabs.value.find(t => t.id === activeTabId.value)
    if (currentTab && editingContent.value !== currentTab.content) {
      currentTab.content = editingContent.value
      currentTab.isModified = editingContent.value !== currentTab.originalContent
    }
  }
  
  // 切换到新标签（watch 会自动更新 editingContent）
  activeTabId.value = tabId
}

// 处理标签关闭
const handleTabClose = (tabId: string) => {
  const tab = openTabs.value.find(t => t.id === tabId)
  if (tab?.isModified) {
    Message.warning('文件有未保存的修改，请先保存')
    return
  }

  const index = openTabs.value.findIndex(t => t.id === tabId)
  if (index === -1)
    return

  openTabs.value.splice(index, 1)

  // 如果关闭的是当前标签，切换到前一个或后一个
  if (activeTabId.value === tabId) {
    if (openTabs.value.length > 0) {
      const newIndex = Math.max(0, index - 1)
      activeTabId.value = openTabs.value[newIndex]?.id || null
    }
    else {
      activeTabId.value = null
    }
  }
}

// 处理编辑器内容变化
const handleEditorChange = (value: string) => {
  if (!activeTabId.value)
    return

  // 立即更新临时编辑内容（不触发响应式数组更新）
  editingContent.value = value
  
  // 防抖更新 openTabs（500ms 后批量更新）
  if (contentUpdateTimer) {
    clearTimeout(contentUpdateTimer)
  }
  
  contentUpdateTimer = setTimeout(() => {
    const tab = openTabs.value.find(t => t.id === activeTabId.value)
    if (tab) {
      tab.content = value
      tab.isModified = value !== tab.originalContent
    }
  }, 500)
}

// 保存当前文件
const handleSave = async () => {
  if (!activeTab.value)
    return

  // 清除防抖定时器，立即同步最新的编辑内容
  if (contentUpdateTimer) {
    clearTimeout(contentUpdateTimer)
    contentUpdateTimer = null
  }
  
  // 同步最新的编辑内容到 activeTab
  if (editingContent.value !== activeTab.value.content) {
    activeTab.value.content = editingContent.value
  }

  try {
    await caseEditorAPI.saveFile({
      path: activeTab.value.filePath,
      content: activeTab.value.content,
    })

    // 更新标签状态
    activeTab.value.isModified = false
    activeTab.value.originalContent = activeTab.value.content

    showStatus('文件保存成功', 'success')
  }
  catch (error) {
    console.error('Failed to save file:', error)
    showStatus('文件保存失败', 'error')
  }
}

// 保存所有文件
const handleSaveAll = async () => {
  const modifiedTabs = openTabs.value.filter(tab => tab.isModified)
  if (modifiedTabs.length === 0)
    return

  let successCount = 0
  for (const tab of modifiedTabs) {
    try {
      await caseEditorAPI.saveFile({
        path: tab.filePath,
        content: tab.content,
      })
      tab.isModified = false
      tab.originalContent = tab.content
      successCount++
    }
    catch (error) {
      console.error(`Failed to save file ${tab.fileName}:`, error)
    }
  }

  if (successCount === modifiedTabs.length) {
    showStatus(`成功保存 ${successCount} 个文件`, 'success')
  }
  else {
    showStatus(`保存了 ${successCount}/${modifiedTabs.length} 个文件`, 'warning')
  }
}

// 显示状态消息
const showStatus = (message: string, type: 'success' | 'error' | 'info' | 'warning') => {
  statusMessage.value = message
  statusType.value = type

  setTimeout(() => {
    statusMessage.value = ''
  }, 3000)
}

// 处理文件操作
const handleFileAction = (action: string, node: FileNode) => {
  currentActionNode.value = node

  switch (action) {
    case 'newFile':
      dialogType.value = 'createFile'
      dialogTitle.value = '新建文件'
      dialogDefaultValue.value = ''
      dialogVisible.value = true
      break
    case 'newFolder':
      dialogType.value = 'createFolder'
      dialogTitle.value = '新建文件夹'
      dialogDefaultValue.value = ''
      dialogVisible.value = true
      break
    case 'rename':
      dialogType.value = 'rename'
      dialogTitle.value = '重命名'
      dialogDefaultValue.value = node.name
      dialogVisible.value = true
      break
    case 'delete':
      dialogType.value = 'delete'
      dialogTitle.value = '删除确认'
      dialogMessage.value = `确定要删除 "${node.name}" 吗？${node.type === 'folder' ? '文件夹及其内容将被永久删除。' : ''}`
      dialogVisible.value = true
      break
    case 'upload':
      dialogType.value = 'upload'
      dialogTitle.value = '上传文件'
      dialogVisible.value = true
      break
  }
}

// 处理上传按钮点击
const handleUploadClick = () => {
  if (!selectedCasespace.value || !selectedCase.value) {
    Message.warning('请先选择 Casespace 和 Case')
    return
  }

  currentActionNode.value = {
    path: `/${selectedCasespace.value}/${selectedCase.value}`,
    name: selectedCase.value,
    type: 'folder',
  }

  dialogType.value = 'upload'
  dialogTitle.value = '上传文件到根目录'
  dialogVisible.value = true
}

// 处理对话框确认
const handleDialogConfirm = async (value?: string | File[] | { caseName: string; file: File }) => {
  if (!currentActionNode.value && dialogType.value !== 'uploadCase' && dialogType.value !== 'deleteCase')
    return

  try {
    switch (dialogType.value) {
      case 'createFile':
        if (typeof value === 'string') {
          await caseEditorAPI.createFile({
            parentPath: currentActionNode.value.path,
            name: value,
          })
          Message.success('文件创建成功')
          await loadFileTree()
        }
        break

      case 'createFolder':
        if (typeof value === 'string') {
          await caseEditorAPI.createFolder({
            parentPath: currentActionNode.value.path,
            name: value,
          })
          Message.success('文件夹创建成功')
          await loadFileTree()
        }
        break

      case 'rename':
        if (typeof value === 'string') {
          await caseEditorAPI.renameItem({
            oldPath: currentActionNode.value.path,
            newName: value,
          })
          Message.success('重命名成功')
          await loadFileTree()
        }
        break

      case 'delete':
        await caseEditorAPI.deleteItem(currentActionNode.value.path)
        Message.success('删除成功')
        await loadFileTree()
        break

      case 'upload':
        if (Array.isArray(value) && value.length > 0) {
          const uploadFiles = await Promise.all(
            value.map(async (file) => {
              const content = await readFileAsText(file)
              return { name: file.name, content }
            })
          )

          await caseEditorAPI.uploadFiles({
            parentPath: currentActionNode.value.path,
            files: uploadFiles,
          })
          Message.success(`成功上传 ${uploadFiles.length} 个文件`)
          await loadFileTree()
        }
        break

      case 'deleteCase':
        if (!selectedCasespace.value || !selectedCase.value) {
          return
        }
        await caseEditorAPI.deleteCase(selectedCasespace.value, selectedCase.value)
        Message.success(`Case "${selectedCase.value}" 已删除`)
        
        // 关闭所有打开的标签页
        openTabs.value = []
        activeTabId.value = null
        
        // 清空选中的 case
        selectedCase.value = undefined
        
        // 重新加载 cases 列表
        if (selectedCasespace.value) {
          await loadCases(selectedCasespace.value)
        }
        break

      case 'uploadCase':
        console.log('uploadCase handler triggered, value:', value)
        if (!selectedCasespace.value) {
          Message.error('请先选择 Casespace')
          return
        }
        if (value && typeof value === 'object' && 'caseName' in value && 'file' in value) {
          const { caseName, file } = value as { caseName: string; file: File }
          
          console.log('Uploading case:', caseName, file)
          Message.info('正在上传...')
          
          await caseEditorAPI.uploadCase(selectedCasespace.value, caseName, file)
          Message.success(`Case "${caseName}" 上传成功`)
          
          // 重新加载 cases 列表
          await loadCases(selectedCasespace.value)
          
          // 自动选中新上传的 case
          selectedCase.value = caseName
        } else {
          console.error('Invalid uploadCase value:', value)
          Message.error('上传参数错误')
        }
        break
    }
  }
  catch (error: any) {
    console.error('File operation failed:', error)
    Message.error(error.message || '操作失败')
  }
}

// 读取文件内容为文本
const readFileAsText = (file: File): Promise<string> => {
  return new Promise((resolve, reject) => {
    const reader = new FileReader()
    reader.onload = e => resolve(e.target?.result as string)
    reader.onerror = reject
    reader.readAsText(file)
  })
}

// 删除 case
const handleDeleteCaseClick = () => {
  if (!selectedCasespace.value || !selectedCase.value) {
    return
  }
  
  dialogType.value = 'deleteCase'
  dialogTitle.value = '确认删除 Case'
  dialogMessage.value = `确定要删除 Case "${selectedCase.value}" 吗？\n\n此操作将删除整个 Case 目录及其所有文件，且无法恢复！`
  dialogDefaultValue.value = ''
  dialogVisible.value = true
}

// 上传 case
const handleUploadCaseClick = () => {
  if (!selectedCasespace.value) {
    Message.warning('请先选择 Casespace')
    return
  }
  
  dialogType.value = 'uploadCase'
  dialogTitle.value = '上传 Case'
  dialogMessage.value = ''
  dialogDefaultValue.value = ''
  dialogVisible.value = true
}

// Download case handler
const handleDownloadCaseClick = async () => {
  if (!selectedCasespace.value || !selectedCase.value) {
    Message.warning('请先选择 Case')
    return
  }

  try {
    Message.info('正在准备下载...')
    const response = await caseEditorAPI.downloadCase(selectedCasespace.value, selectedCase.value)
    
    // 从响应中获取 blob
    const blob = new Blob([response.data], { type: 'application/zip' })
    
    // 创建下载链接
    const url = window.URL.createObjectURL(blob)
    const link = document.createElement('a')
    link.href = url
    link.download = `${selectedCase.value}.zip`
    
    // 触发下载
    document.body.appendChild(link)
    link.click()
    
    // 清理
    document.body.removeChild(link)
    window.URL.revokeObjectURL(url)
    
    Message.success(`Case "${selectedCase.value}" 下载成功`)
  }
  catch (error: any) {
    console.error('Failed to download case:', error)
    Message.error(error.message || '下载失败')
  }
}

// 键盘快捷键
const handleKeyDown = (event: KeyboardEvent) => {
  // Ctrl+S / Cmd+S: 保存当前文件
  if ((event.ctrlKey || event.metaKey) && event.key === 's') {
    event.preventDefault()
    if (activeTab.value) {
      handleSave()
    }
  }

  // Ctrl+Shift+S / Cmd+Shift+S: 保存所有文件
  if ((event.ctrlKey || event.metaKey) && event.shiftKey && event.key === 'S') {
    event.preventDefault()
    if (hasModifiedFiles.value) {
      handleSaveAll()
    }
  }

  // Esc: 关闭对话框
  if (event.key === 'Escape') {
    dialogVisible.value = false
  }
}

// 生命周期
onMounted(async () => {
  await loadCasespaces()
  window.addEventListener('keydown', handleKeyDown)
})

onUnmounted(() => {
  window.removeEventListener('keydown', handleKeyDown)
  // 清理防抖定时器
  if (contentUpdateTimer) {
    clearTimeout(contentUpdateTimer)
  }
})
</script>

<style scoped lang="less">
.case-editor {
  display: flex;
  flex-direction: column;
  height: 100vh;
  background-color: var(--color-bg-1);

  .editor-content {
    display: flex;
    flex: 1;
    overflow: hidden;

    .sidebar {
      width: 280px;
      flex-shrink: 0;
      border-right: 1px solid var(--color-border-2);
      overflow: hidden;
    }

    .main-area {
      display: flex;
      flex-direction: column;
      flex: 1;
      overflow: hidden;

      .editor-container {
        flex: 1;
        overflow: hidden;
        position: relative;

        .empty-editor {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          height: 100%;
          color: var(--color-text-3);

          .arco-icon {
            font-size: 64px;
            margin-bottom: 16px;
          }

          p {
            margin: 0;
            font-size: 16px;
          }
        }
      }
    }
  }
}
</style>

