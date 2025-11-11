<template>
  <div class="editor-tabs">
    <div v-if="tabs.length === 0" class="empty-tabs">
      <icon-file />
      <span>暂无打开的文件</span>
    </div>
    <div v-else class="tabs-container">
      <div
        v-for="tab in tabs"
        :key="tab.id"
        class="tab-item"
        :class="{ active: tab.id === activeTabId }"
        @click="$emit('switch', tab.id)"
      >
        <icon-file class="tab-icon" />
        <span class="tab-name">{{ tab.fileName }}</span>
        <span v-if="tab.isModified" class="modified-indicator"></span>
        <span class="close-btn" @click.stop="$emit('close', tab.id)">
          <icon-close />
        </span>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import type { EditorTab } from '@/apis/system/caseeditor-type'

interface Props {
  tabs: EditorTab[]
  activeTabId?: string | null
}

interface Emits {
  (e: 'switch', tabId: string): void
  (e: 'close', tabId: string): void
}

defineProps<Props>()
defineEmits<Emits>()
</script>

<style scoped lang="less">
.editor-tabs {
  display: flex;
  align-items: center;
  height: 40px;
  background-color: var(--color-bg-2);
  border-bottom: 1px solid var(--color-border-2);
  overflow-x: auto;
  overflow-y: hidden;

  &::-webkit-scrollbar {
    height: 4px;
  }

  &::-webkit-scrollbar-thumb {
    background-color: var(--color-fill-3);
    border-radius: 2px;
  }

  .empty-tabs {
    display: flex;
    align-items: center;
    padding: 0 16px;
    color: var(--color-text-3);
    font-size: 14px;
    gap: 8px;

    .arco-icon {
      font-size: 16px;
    }
  }

  .tabs-container {
    display: flex;
    flex: 1;
    height: 100%;
  }

  .tab-item {
    display: flex;
    align-items: center;
    gap: 6px;
    height: 100%;
    padding: 0 12px;
    min-width: 120px;
    max-width: 200px;
    background-color: transparent;
    border-right: 1px solid var(--color-border-2);
    cursor: pointer;
    transition: background-color 0.2s;
    position: relative;
    user-select: none;

    &:hover {
      background-color: var(--color-fill-2);

      .close-btn {
        opacity: 1;
      }
    }

    &.active {
      background-color: var(--color-bg-1);
      border-bottom: 2px solid rgb(var(--primary-6));

      .tab-name {
        color: rgb(var(--primary-6));
        font-weight: 500;
      }
    }

    .tab-icon {
      flex-shrink: 0;
      font-size: 14px;
      color: var(--color-text-2);
    }

    .tab-name {
      flex: 1;
      overflow: hidden;
      text-overflow: ellipsis;
      white-space: nowrap;
      font-size: 13px;
      color: var(--color-text-1);
    }

    .modified-indicator {
      flex-shrink: 0;
      width: 6px;
      height: 6px;
      border-radius: 50%;
      background-color: rgb(var(--primary-6));
    }

    .close-btn {
      display: flex;
      align-items: center;
      justify-content: center;
      flex-shrink: 0;
      width: 16px;
      height: 16px;
      border-radius: 2px;
      opacity: 0;
      transition: opacity 0.2s, background-color 0.2s;

      &:hover {
        background-color: var(--color-fill-3);
      }

      .arco-icon {
        font-size: 12px;
        color: var(--color-text-2);
      }
    }

    &.active .close-btn {
      opacity: 1;
    }
  }
}
</style>

