<template>
  <div class="file-tree">
    <div v-if="!fileTree || fileTree.length === 0" class="empty-state">
      <icon-folder />
      <p>请选择 Casespace 和 Case</p>
    </div>
    <div v-else class="tree-content">
      <!-- Case 标题区域 -->
      <div 
        v-if="caseName" 
        class="case-header"
        @contextmenu="handleCaseContextMenu"
      >
        <icon-folder class="case-icon" />
        <span class="case-name">{{ caseName }}</span>
      </div>
      
      <!-- 文件树 -->
      <FileTreeNode
        v-for="node in fileTree"
        :key="node.path"
        :node="node"
        :level="0"
        @select="handleNodeSelect"
        @context-menu="handleContextMenu"
      />
    </div>

    <!-- 右键菜单 -->
    <a-dropdown
      v-model:popup-visible="contextMenuVisible"
      trigger="manual"
      :popup-translate="contextMenuPosition"
      @select="handleMenuAction"
    >
      <div style="position: fixed; left: 0; top: 0; pointer-events: none"></div>
      <template #content>
        <template v-if="contextMenuNode?.type === 'folder'">
          <a-doption value="newFile">
            <icon-file />
            <span>新建文件</span>
          </a-doption>
          <a-doption value="newFolder">
            <icon-folder-add />
            <span>新建文件夹</span>
          </a-doption>
          <a-doption value="upload">
            <icon-upload />
            <span>上传文件</span>
          </a-doption>
          <a-divider style="margin: 4px 0" />
          <a-doption value="rename">
            <icon-edit />
            <span>重命名</span>
          </a-doption>
          <a-doption value="delete">
            <icon-delete />
            <span>删除</span>
          </a-doption>
        </template>
        <template v-else>
          <a-doption value="rename">
            <icon-edit />
            <span>重命名</span>
          </a-doption>
          <a-doption value="delete">
            <icon-delete />
            <span>删除</span>
          </a-doption>
        </template>
      </template>
    </a-dropdown>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { FileNode } from '@/apis/system/caseeditor-type'
import FileTreeNode from './FileTreeNode.vue'

interface Props {
  fileTree: FileNode[]
  casespace?: string
  caseName?: string
}

interface Emits {
  (e: 'select', node: FileNode): void
  (e: 'action', action: string, node: FileNode | null): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const contextMenuVisible = ref(false)
const contextMenuNode = ref<FileNode | null>(null)
const contextMenuPosition = ref([0, 0])

const handleNodeSelect = (node: FileNode) => {
  emit('select', node)
}

const handleContextMenu = (event: MouseEvent, node: FileNode) => {
  event.preventDefault()
  contextMenuNode.value = node
  contextMenuPosition.value = [event.clientX, event.clientY]
  contextMenuVisible.value = true
}

const handleCaseContextMenu = (event: MouseEvent) => {
  event.preventDefault()
  // 创建一个表示整个 case 目录的虚拟节点
  // 使用正确的 case 路径
  const casePath = props.casespace && props.caseName 
    ? `/${props.casespace}/${props.caseName}` 
    : '/'
  const caseNode: FileNode = {
    path: casePath,
    name: props.caseName || '',
    type: 'folder',
    children: []
  }
  contextMenuNode.value = caseNode
  contextMenuPosition.value = [event.clientX, event.clientY]
  contextMenuVisible.value = true
}

const handleMenuAction = (value: string | number | Record<string, any> | undefined) => {
  if (typeof value === 'string') {
    emit('action', value, contextMenuNode.value)
  }
  contextMenuVisible.value = false
}
</script>

<style scoped lang="less">
.file-tree {
  height: 100%;
  overflow-y: auto;
  padding: 8px;
  background-color: var(--color-bg-2);
  border-radius: 4px;

  .empty-state {
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    height: 200px;
    color: var(--color-text-3);

    .arco-icon {
      font-size: 48px;
      margin-bottom: 12px;
    }

    p {
      margin: 0;
      font-size: 14px;
    }
  }

  .tree-content {
    min-height: 100%;
    
    .case-header {
      display: flex;
      align-items: center;
      padding: 8px 12px;
      margin-bottom: 8px;
      background-color: var(--color-fill-2);
      border-radius: 4px;
      cursor: context-menu;
      user-select: none;
      
      &:hover {
        background-color: var(--color-fill-3);
      }
      
      .case-icon {
        font-size: 18px;
        color: var(--color-primary-light-2);
        margin-right: 8px;
      }
      
      .case-name {
        font-size: 14px;
        font-weight: 600;
        color: var(--color-text-1);
      }
    }
  }
}
</style>

