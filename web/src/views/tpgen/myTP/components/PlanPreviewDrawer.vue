<template>
  <a-drawer
    v-model:visible="visible"
    :width="900"
    title="TEST PLAN CONFIGURATION DETAILS"
    :footer="false"
  >
    <template v-if="record">
      <a-divider>CONFIGURATION DETAILS</a-divider>
      <div class="yaml-viewer">
        <div class="yaml-content">
          <div v-for="(line, index) in highlightedLines" :key="index" class="yaml-line">
            <span class="line-number">{{ index + 1 }}</span>
            <span class="line-content" v-html="line"></span>
          </div>
        </div>
      </div>
    </template>
  </a-drawer>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { SavedPlanResp } from '../types'

interface Props {
  modelValue: boolean
  record: SavedPlanResp | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

// 将 JavaScript 对象转换为 YAML 字符串（修复版）
const yamlString = computed(() => {
  if (!props.record?.yamlData) return ''
  
  let dataObj = props.record.yamlData
  
  // 如果是字符串，尝试解析为对象
  if (typeof dataObj === 'string') {
    try {
      dataObj = JSON.parse(dataObj)
    } catch (error) {
      console.error('解析 yamlData 失败:', error)
      return dataObj // 如果解析失败，返回原字符串
    }
  }
  
  // 转换对象为 YAML 格式
  return jsToYaml(dataObj, 0)
})

/**
 * 将 JS 对象转换为 YAML 格式（修复层级问题）
 */
function jsToYaml(obj: any, indent = 0): string {
  if (obj === null || obj === undefined) return ''
  
  let yaml = ''
  const spaces = '  '.repeat(indent)

  const entries = Object.entries(obj)

  for (const [key, value] of entries) {
    if (Array.isArray(value)) {
      // 处理数组
      if (value.length === 0) {
        yaml += `${spaces}${key}: []\n`
      } else {
        yaml += `${spaces}${key}:\n`
        value.forEach((item) => {
          if (typeof item === 'object' && item !== null) {
            // 数组项是对象 - 使用专门的函数处理
            yaml += renderArrayItemObject(item, indent + 1)
          } else {
            // 数组项是简单值
            yaml += `${spaces}  - ${item}\n`
          }
        })
      }
    } else if (typeof value === 'object' && value !== null) {
      // 处理嵌套对象
      yaml += `${spaces}${key}:\n`
      yaml += jsToYaml(value, indent + 1)
    } else if (value !== null && value !== undefined) {
      // 处理简单值
      yaml += `${spaces}${key}: ${value}\n`
    }
  }

  return yaml
}

/**
 * 渲染数组项对象（特殊处理缩进）
 */
function renderArrayItemObject(obj: any, indent: number): string {
  let yaml = ''
  const spaces = '  '.repeat(indent)
  const entries = Object.entries(obj)
  
  entries.forEach(([key, value], index) => {
    if (index === 0) {
      // 第一个属性：紧跟 - 之后
      if (Array.isArray(value)) {
        yaml += `${spaces}- ${key}:\n`
        if (value.length === 0) {
          yaml += `${spaces}    []\n`
        } else {
          value.forEach((item) => {
            if (typeof item === 'object' && item !== null) {
              yaml += renderArrayItemObject(item, indent + 2)
            } else {
              yaml += `${spaces}    - ${item}\n`
            }
          })
        }
      } else if (typeof value === 'object' && value !== null) {
        yaml += `${spaces}- ${key}:\n`
        yaml += jsToYaml(value, indent + 2)
      } else {
        yaml += `${spaces}- ${key}: ${value}\n`
      }
    } else {
      // 其他属性：与第一个属性的键对齐（- 之后的位置）
      if (Array.isArray(value)) {
        yaml += `${spaces}  ${key}:\n`
        if (value.length === 0) {
          yaml += `${spaces}    []\n`
        } else {
          value.forEach((item) => {
            if (typeof item === 'object' && item !== null) {
              yaml += renderArrayItemObject(item, indent + 2)
            } else {
              yaml += `${spaces}    - ${item}\n`
            }
          })
        }
      } else if (typeof value === 'object' && value !== null) {
        yaml += `${spaces}  ${key}:\n`
        yaml += jsToYaml(value, indent + 2)
      } else {
        yaml += `${spaces}  ${key}: ${value}\n`
      }
    }
  })
  
  return yaml
}

/**
 * 语法高亮处理
 */
const highlightedLines = computed(() => {
  const yamlText = yamlString.value
  if (!yamlText) return []
  
  const lines = yamlText.split('\n')
  return lines.map(line => highlightYamlLine(line))
})

/**
 * 对单行 YAML 进行语法高亮
 */
function highlightYamlLine(line: string): string {
  if (!line.trim()) return '&nbsp;'
  
  // 匹配注释
  if (line.trim().startsWith('#')) {
    return `<span class="yaml-comment">${escapeHtml(line)}</span>`
  }
  
  // 匹配数组项（以 - 开头）
  const arrayMatch = line.match(/^(\s*)(- )(.*)$/)
  if (arrayMatch) {
    const [, spaces, dash, rest] = arrayMatch
    const highlightedRest = highlightKeyValue(rest)
    return `${escapeHtml(spaces)}<span class="yaml-array">${escapeHtml(dash)}</span>${highlightedRest}`
  }
  
  // 匹配键值对
  return highlightKeyValue(line)
}

/**
 * 高亮键值对
 */
function highlightKeyValue(line: string): string {
  const colonIndex = line.indexOf(':')
  if (colonIndex === -1) {
    return escapeHtml(line)
  }
  
  const beforeColon = line.substring(0, colonIndex)
  const afterColon = line.substring(colonIndex + 1)
  
  // 提取缩进
  const leadingSpaces = beforeColon.match(/^\s*/)?.[0] || ''
  const key = beforeColon.substring(leadingSpaces.length)
  
  // 处理值
  let highlightedValue = ''
  const trimmedValue = afterColon.trim()
  
  if (trimmedValue === '') {
    // 空值，可能是嵌套对象的开始
    highlightedValue = ''
  } else if (trimmedValue === 'true' || trimmedValue === 'false') {
    // 布尔值
    highlightedValue = `<span class="yaml-boolean">${escapeHtml(afterColon)}</span>`
  } else if (!isNaN(Number(trimmedValue)) && trimmedValue !== '') {
    // 数字
    highlightedValue = `<span class="yaml-number">${escapeHtml(afterColon)}</span>`
  } else if (trimmedValue.startsWith('"') || trimmedValue.startsWith("'")) {
    // 字符串（带引号）
    highlightedValue = `<span class="yaml-string">${escapeHtml(afterColon)}</span>`
  } else {
    // 普通字符串
    highlightedValue = `<span class="yaml-value">${escapeHtml(afterColon)}</span>`
  }
  
  return `${escapeHtml(leadingSpaces)}<span class="yaml-key">${escapeHtml(key)}</span><span class="yaml-colon">:</span>${highlightedValue}`
}

/**
 * HTML 转义
 */
function escapeHtml(text: string): string {
  const div = document.createElement('div')
  div.textContent = text
  return div.innerHTML
}
</script>

<style scoped lang="scss">
.yaml-viewer {
  background: #1e1e1e;
  border-radius: 8px;
  border: 1px solid #3e3e42;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.15);
}

.yaml-content {
  max-height: 600px;
  overflow-y: auto;
  overflow-x: auto;
  
  &::-webkit-scrollbar {
    width: 8px;
    height: 8px;
  }
  
  &::-webkit-scrollbar-track {
    background: #1e1e1e;
  }
  
  &::-webkit-scrollbar-thumb {
    background: #424242;
    border-radius: 4px;
    
    &:hover {
      background: #4e4e4e;
    }
  }
}

.yaml-line {
  display: flex;
  font-family: 'Consolas', 'Monaco', 'Courier New', monospace;
  font-size: 13px;
  line-height: 1.6;
  min-height: 21px;
  
  &:hover {
    background: rgba(255, 255, 255, 0.03);
  }
}

.line-number {
  flex-shrink: 0;
  width: 50px;
  padding: 2px 12px 2px 8px;
  text-align: right;
  color: #858585;
  background: #1e1e1e;
  border-right: 1px solid #3e3e42;
  user-select: none;
  font-size: 12px;
}

.line-content {
  flex: 1;
  padding: 2px 16px;
  color: #d4d4d4;
  white-space: pre;
  
  :deep(.yaml-key) {
    color: #9cdcfe;
    font-weight: 500;
  }
  
  :deep(.yaml-colon) {
    color: #d4d4d4;
  }
  
  :deep(.yaml-value) {
    color: #ce9178;
  }
  
  :deep(.yaml-string) {
    color: #ce9178;
  }
  
  :deep(.yaml-number) {
    color: #b5cea8;
  }
  
  :deep(.yaml-boolean) {
    color: #569cd6;
    font-weight: 500;
  }
  
  :deep(.yaml-array) {
    color: #d4d4d4;
    font-weight: bold;
  }
  
  :deep(.yaml-comment) {
    color: #6a9955;
    font-style: italic;
  }
}

// 暗色主题适配
[data-theme='dark'] {
  .yaml-viewer {
    background: #1e1e1e;
    border-color: #3e3e42;
  }
}

// 亮色主题适配
[data-theme='light'] {
  .yaml-viewer {
    background: #ffffff;
    border-color: #e5e7eb;
  }
  
  .line-number {
    background: #f9fafb;
    border-right-color: #e5e7eb;
    color: #6b7280;
  }
  
  .line-content {
    color: #1f2937;
    
    :deep(.yaml-key) {
      color: #0369a1;
    }
    
    :deep(.yaml-value) {
      color: #b45309;
    }
    
    :deep(.yaml-string) {
      color: #b45309;
    }
    
    :deep(.yaml-number) {
      color: #047857;
    }
    
    :deep(.yaml-boolean) {
      color: #2563eb;
    }
    
    :deep(.yaml-comment) {
      color: #059669;
    }
  }
  
  .yaml-line:hover {
    background: rgba(0, 0, 0, 0.02);
  }
  
  .yaml-content::-webkit-scrollbar-track {
    background: #f9fafb;
  }
  
  .yaml-content::-webkit-scrollbar-thumb {
    background: #d1d5db;
    
    &:hover {
      background: #9ca3af;
    }
  }
}
</style>
