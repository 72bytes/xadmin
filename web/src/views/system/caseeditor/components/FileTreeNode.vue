<template>
  <div class="file-tree-node">
    <div
      class="node-content"
      :style="{ paddingLeft: `${level * 16 + 8}px` }"
      @click="handleClick"
      @contextmenu="handleContextMenu"
    >
      <span v-if="node.type === 'folder'" class="expand-icon" @click.stop="toggleExpand">
        <icon-right v-if="!expanded" />
        <icon-down v-else />
      </span>
      <span v-else class="expand-icon-placeholder"></span>

      <icon-folder v-if="node.type === 'folder'" class="node-icon folder-icon" />
      <icon-file v-else class="node-icon file-icon" />

      <span class="node-name">{{ node.name }}</span>
    </div>

    <!-- 递归渲染子节点 -->
    <template v-if="node.type === 'folder' && expanded && node.children">
      <FileTreeNode
        v-for="child in node.children"
        :key="child.path"
        :node="child"
        :level="level + 1"
        @select="$emit('select', $event)"
        @context-menu="$emit('context-menu', $event, child)"
      />
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref } from 'vue'
import type { FileNode } from '@/apis/system/caseeditor-type'

interface Props {
  node: FileNode
  level: number
}

interface Emits {
  (e: 'select', node: FileNode): void
  (e: 'context-menu', event: MouseEvent, node: FileNode): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const expanded = ref(props.node.type === 'folder')

const toggleExpand = () => {
  if (props.node.type === 'folder') {
    expanded.value = !expanded.value
  }
}

const handleClick = () => {
  if (props.node.type === 'file') {
    emit('select', props.node)
  }
  else {
    toggleExpand()
  }
}

const handleContextMenu = (event: MouseEvent) => {
  emit('context-menu', event, props.node)
}
</script>

<style scoped lang="less">
.file-tree-node {
  .node-content {
    display: flex;
    align-items: center;
    height: 32px;
    padding-right: 8px;
    cursor: pointer;
    border-radius: 4px;
    transition: background-color 0.2s;
    user-select: none;

    &:hover {
      background-color: var(--color-fill-2);
    }

    .expand-icon {
      display: inline-flex;
      align-items: center;
      justify-content: center;
      width: 16px;
      height: 16px;
      margin-right: 4px;
      color: var(--color-text-2);
      flex-shrink: 0;

      .arco-icon {
        font-size: 12px;
      }
    }

    .expand-icon-placeholder {
      display: inline-block;
      width: 16px;
      margin-right: 4px;
      flex-shrink: 0;
    }

    .node-icon {
      margin-right: 6px;
      flex-shrink: 0;
      font-size: 16px;

      &.folder-icon {
        color: rgb(var(--warning-6));
      }

      &.file-icon {
        color: rgb(var(--primary-6));
      }
    }

    .node-name {
      flex: 1;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      font-size: 14px;
      color: var(--color-text-1);
    }
  }
}
</style>

