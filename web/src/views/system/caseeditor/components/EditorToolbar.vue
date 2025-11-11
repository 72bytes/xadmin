<template>
  <div class="editor-toolbar">
    <div class="toolbar-left">
      <h3 class="title">Case 编辑器</h3>
    </div>

    <div class="toolbar-center">
      <a-alert v-if="statusMessage" :type="statusType" :closable="false" banner>
        {{ statusMessage }}
      </a-alert>
    </div>

    <div class="toolbar-right">
      <a-select
        v-model="selectedCasespaceModel"
        :style="{ width: '160px' }"
        placeholder="选择 Casespace"
        allow-clear
        @change="handleCasespaceChange"
      >
        <a-option v-for="cs in casespaces" :key="cs.name" :value="cs.name">
          {{ cs.name }}
        </a-option>
      </a-select>

      <a-select
        v-model="selectedCaseModel"
        :style="{ width: '160px' }"
        placeholder="选择 Case"
        :disabled="!selectedCasespaceModel || cases.length === 0"
        allow-clear
        @change="handleCaseChange"
      >
        <a-option v-for="c in cases" :key="c.name" :value="c.name">
          {{ c.name }}
        </a-option>
      </a-select>

      <a-button
        type="primary"
        status="danger"
        :disabled="!selectedCase"
        @click="$emit('deleteCase')"
      >
        <template #icon><icon-delete /></template>
        <span>删除 Case</span>
      </a-button>

      <a-button
        type="primary"
        :disabled="!activeTab"
        @click="$emit('save')"
      >
        <template #icon><icon-save /></template>
        <span>保存</span>
      </a-button>

      <a-button
        :disabled="!hasModifiedFiles"
        @click="$emit('saveAll')"
      >
        <template #icon><icon-save /></template>
        <span>全部保存</span>
      </a-button>

      <a-button @click="$emit('upload')">
        <template #icon><icon-upload /></template>
        <span>上传</span>
      </a-button>

      <a-button 
        :disabled="!selectedCasespace"
        @click="$emit('uploadCase')"
      >
        <template #icon><icon-import /></template>
        <span>上传 Case</span>
      </a-button>

      <a-button 
        :disabled="!selectedCase"
        @click="$emit('downloadCase')"
      >
        <template #icon><icon-export /></template>
        <span>下载 Case</span>
      </a-button>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { CasespaceItem, CaseItem, EditorTab } from '@/apis/system/caseeditor-type'

interface Props {
  casespaces: CasespaceItem[]
  cases: CaseItem[]
  selectedCasespace?: string
  selectedCase?: string
  activeTab?: EditorTab | null
  hasModifiedFiles: boolean
  statusMessage?: string
  statusType?: 'success' | 'error' | 'info' | 'warning'
}

interface Emits {
  (e: 'update:selectedCasespace', value: string | undefined): void
  (e: 'update:selectedCase', value: string | undefined): void
  (e: 'save'): void
  (e: 'saveAll'): void
  (e: 'upload'): void
  (e: 'deleteCase'): void
  (e: 'uploadCase'): void
  (e: 'downloadCase'): void
}

const props = withDefaults(defineProps<Props>(), {
  statusType: 'info',
})

const emit = defineEmits<Emits>()

const selectedCasespaceModel = computed({
  get: () => props.selectedCasespace,
  set: (value) => emit('update:selectedCasespace', value),
})

const selectedCaseModel = computed({
  get: () => props.selectedCase,
  set: (value) => emit('update:selectedCase', value),
})

const handleCasespaceChange = (value: string | undefined) => {
  emit('update:selectedCasespace', value)
  emit('update:selectedCase', undefined)
}

const handleCaseChange = (value: string | undefined) => {
  emit('update:selectedCase', value)
}
</script>

<style scoped lang="less">
.editor-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 16px;
  background-color: var(--color-bg-2);
  border-bottom: 1px solid var(--color-border-2);
  gap: 16px;

  .toolbar-left {
    flex-shrink: 0;

    .title {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      color: var(--color-text-1);
    }
  }

  .toolbar-center {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    min-width: 0;

    :deep(.arco-alert) {
      max-width: 400px;
    }
  }

  .toolbar-right {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
  }
}
</style>

