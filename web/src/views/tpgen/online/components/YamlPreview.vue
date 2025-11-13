<template>
  <a-card class="form-section yaml-preview" :bordered="false">
    <template #title>
      <div class="section-title">
        <icon-code />
        Generated Test Plan (YAML)
      </div>
    </template>

    <div class="yaml-content">

      <div class="yaml-display" :style="{ maxHeight: `${dynamicHeight}px` }">
        <div 
          class="yaml-line-numbers" 
          ref="lineNumbersRef" 
          @scroll="syncScroll"
          :style="{ maxHeight: `${dynamicHeight}px` }"
        >

          <div
            v-for="(line, index) in yamlLines"
            :key="index"
            class="line-number"
            :class="{ error: isErrorLine(index + 1) }"
          >
            {{ index + 1 }}
          </div>
        </div>

        <div 
          class="yaml-code-content" 
          ref="yamlContentRef" 
          @scroll="handleYamlScroll"
          :style="{ maxHeight: `${dynamicHeight}px` }"
        >

          <div
            v-for="(line, index) in yamlLines"
            :key="index"
            :ref="isErrorLine(index + 1) ? 'errorLineRef' : undefined"
            class="code-line"
            :class="{ 'error-line': isErrorLine(index + 1) }"
          >
            {{ line }}
          </div>
        </div>
      </div>
    </div>

    <div class="actions">

      <a-button  type="primary" @click="handleCopy">
        <template #icon><icon-copy /></template>
        Copy to Clipboard
      </a-button>



      <a-space>

      <a-button type="primary" @click="handleSave">
        <template #icon><icon-save /></template>
        Save Plan
      </a-button>




      <a-button type="primary" @click="handleDownload">
        <template #icon><icon-download /></template>
        Download YAML
      </a-button>
    </a-space>



    </div>
  </a-card>
</template>

<script setup lang="ts">

import { Message } from '@arco-design/web-vue'

import type { YamlData } from '../types'

defineOptions({ name: 'YamlPreview' })

const props = defineProps<{
  yamlData: YamlData
  errorLines?: number[]
}>()

const emit = defineEmits<{
  close: []
  copy: []
  download: []
  save: []
}>()

// 监听 props 变化
watch(() => props.errorLines, (newVal) => {
  console.log('[YamlPreview props] errorLines prop 收到:', newVal)
}, { immediate: true })

// Refs for line numbers and content
const lineNumbersRef = ref<HTMLElement | null>(null)
const yamlContentRef = ref<HTMLElement | null>(null)
const errorLineRef = ref<HTMLElement | null>(null)

// 将 JavaScript 对象转换为 YAML 字符串
const yamlString = computed(() => {
  const yaml = jsToYaml(props.yamlData)
  // 去除末尾多余的换行符，保持格式统一
  return yaml.trimEnd()
})

// 将 YAML 字符串按行分割
const yamlLines = computed(() => {
  if (!yamlString.value) return []
  const lines = yamlString.value.split('\n')
  console.log('[YamlPreview yamlLines] 总行数:', lines.length)
  console.log('[YamlPreview yamlLines] 前 10 行:', lines.slice(0, 10))
  return lines
})

// 动态计算预览区高度
const dynamicHeight = computed(() => {
  const lineCount = yamlLines.value.length
  const lineHeight = 25.6 // 每行高度（px）
  const padding = 50 // 上下内边距总和（px）
  const minHeight = 200 // 最小高度
  const maxHeight = 800 // 最大高度
  
  // 计算内容高度
  const contentHeight = lineCount * lineHeight + padding
  
  // 限制在最小和最大高度之间
  if (contentHeight < minHeight) return minHeight
  if (contentHeight > maxHeight) return maxHeight
  return contentHeight
})

// 保存按钮 - 触发父组件的保存逻辑
function handleSave() {
  console.log('[YamlPreview handleSave] 触发保存事件')
  emit('save')
}

// 检查指定行是否是错误行
const isErrorLine = (lineNumber: number): boolean => {
  const isError = props.errorLines?.includes(lineNumber) || false
  if (isError) {
    console.log(`[YamlPreview isErrorLine] 行 ${lineNumber} 是错误行`)
  }
  return isError
}

function jsToYaml(obj: any, indent = 0): string {
  let yaml = ''
  const spaces = '  '.repeat(indent)

  for (const [key, value] of Object.entries(obj)) {
    if (Array.isArray(value)) {
      yaml += `${spaces}${key}:\n`
      value.forEach((item) => {
        if (typeof item === 'object' && item !== null) {
          const itemYaml = jsToYaml(item, indent + 2)
          const lines = itemYaml.trim().split('\n')
          yaml += `${spaces}  -`
          lines.forEach((line, i) => {
            if (i === 0) {
              yaml += ` ${line.trim()}\n`
            } else {
              yaml += `${spaces}    ${line.trim()}\n`
            }
          })
        } else {
          yaml += `${spaces}  - ${item}\n`
        }
      })
    } else if (typeof value === 'object' && value !== null) {
      yaml += `${spaces}${key}:\n${jsToYaml(value, indent + 1)}`
    } else {
      yaml += `${spaces}${key}: ${value}\n`
    }
  }

  return yaml
}

// 复制到剪贴板 - 触发父组件的验证逻辑
const handleCopy = () => {
  emit('copy')
}

// 下载 YAML 文件 - 触发父组件的验证逻辑
const handleDownload = () => {
  emit('download')
}

// 处理 YAML 内容滚动，同步行号滚动
const handleYamlScroll = () => {
  if (lineNumbersRef.value && yamlContentRef.value) {
    lineNumbersRef.value.scrollTop = yamlContentRef.value.scrollTop
  }
}

// 同步滚动
const syncScroll = () => {
  if (lineNumbersRef.value && yamlContentRef.value) {
    yamlContentRef.value.scrollTop = lineNumbersRef.value.scrollTop
  }
}

// 滚动到错误行
const scrollToErrorLine = () => {
  console.log('[YamlPreview scrollToErrorLine] 开始滚动到错误行')
  console.log('[YamlPreview scrollToErrorLine] props.errorLines:', props.errorLines)

  if (!props.errorLines || props.errorLines.length === 0) {
    console.log('[YamlPreview scrollToErrorLine] ⚠️ 没有错误行，跳过滚动')
    return
  }

  nextTick(() => {
    console.log('[YamlPreview scrollToErrorLine] nextTick 执行')
    const errorLine = errorLineRef.value
    console.log('[YamlPreview scrollToErrorLine] errorLineRef.value:', errorLine)

    if (errorLine && yamlContentRef.value) {
      // 如果 errorLineRef 是数组（多个错误行），取第一个
      const target = Array.isArray(errorLine) ? errorLine[0] : errorLine
      console.log('[YamlPreview scrollToErrorLine] 滚动目标元素:', target)

      if (target) {
        console.log('[YamlPreview scrollToErrorLine] ✅ 执行滚动')
        target.scrollIntoView({ behavior: 'smooth', block: 'center' })
      } else {
        console.log('[YamlPreview scrollToErrorLine] ❌ 目标元素为空')
      }
    } else {
      console.log('[YamlPreview scrollToErrorLine] ❌ errorLineRef 或 yamlContentRef 为空')
    }
  })
}

// 监听错误行变化，自动滚动
watch(() => props.errorLines, (newErrorLines, oldErrorLines) => {
  console.log('[YamlPreview watch] errorLines 变化')
  console.log('[YamlPreview watch] 旧值:', oldErrorLines)
  console.log('[YamlPreview watch] 新值:', newErrorLines)

  if (newErrorLines && newErrorLines.length > 0) {
    console.log('[YamlPreview watch] ✅ 检测到错误行:', newErrorLines)
    scrollToErrorLine()
  } else {
    console.log('[YamlPreview watch] ⚠️ 错误行为空')
  }
}, { immediate: true, deep: true })
</script>

<style scoped lang="scss">
.form-section {
  background: white;
  border-radius: 12px;
  margin-bottom: 25px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  border-left: 5px solid #3498db;

  .section-title {
    display: flex;
    align-items: center;
    gap: 10px;
    font-size: 1.5rem;
    font-weight: 600;
    color: #2c3e50;

    .arco-icon {
      color: #3498db;
      background: #f8f9fa;
      padding: 8px;
      border-radius: 8px;
    }
  }
}

.yaml-content {
  background: #2d3748;
  color: #e2e8f0;
  border-radius: 12px;
  font-family: 'Fira Code', 'Courier New', monospace;
  margin-bottom: 20px;
  box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.3);
  border: 1px solid #4a5568;
  overflow: hidden;

  .yaml-display {
    display: flex;
    height: auto;
    transition: max-height 0.3s ease; // 平滑过渡效果
  }

  .yaml-line-numbers {
    background: #1e2530;
    color: #718096;
    padding-top: 25px;
    padding-bottom: 25px;
    padding-left: 10px;
    padding-right: 15px;
    text-align: right;
    user-select: none;
    border-right: 2px solid #4a5568;
    overflow-y: auto;
    overflow-x: hidden;
    flex-shrink: 0;
    min-width: 60px;
    position: relative;
    transition: max-height 0.3s ease; // 平滑过渡效果

    .line-number {
      font-family: 'Fira Code', 'Courier New', monospace;
      font-size: 14.4px;
      line-height: 25.6px;
      font-weight: 500;
      padding: 0 5px;
      transition: all 0.3s ease;

      &.error {
        color: #ff4d4f;
        font-weight: bold;
        background-color: rgba(255, 77, 79, 0.15);
      }
    }

    /* 隐藏滚动条但保持滚动功能 */
    &::-webkit-scrollbar {
      width: 0;
      height: 0;
    }
  }

  .yaml-code-content {
    flex: 1;
    padding-top: 25px;
    padding-bottom: 25px;
    padding-left: 25px;
    padding-right: 25px;
    overflow-y: auto;
    overflow-x: auto;
    transition: max-height 0.3s ease; // 平滑过渡效果

    .code-line {
      font-family: 'Fira Code', 'Courier New', monospace;
      font-size: 14.4px;
      line-height: 25.6px;
      color: #e2e8f0;
      white-space: pre;
      padding: 0 5px;
      margin: 0;
      transition: all 0.3s ease;

      // &.error-line {
      //   background-color: rgba(255, 77, 79, 0.15);
      //   border-left: 4px solid #ff4d4f;
      //   padding-left: 10px;
      //   animation: pulse-error 1.5s ease-in-out infinite;
      //   box-shadow: 0 0 10px rgba(255, 77, 79, 0.3);
      // }
    }
    &.error-line {
      background-color: rgba(255, 77, 79, 0.15);
      box-shadow: inset 4px 0 0 0 #ff4d4f;  // 内阴影模拟左边框
      // 不需要 padding-left 和 border-left
    }
  }

  /* 错误行脉冲动画 */
  @keyframes pulse-error {
    0%, 100% {
      background-color: rgba(255, 77, 79, 0.15);
      box-shadow: 0 0 10px rgba(255, 77, 79, 0.3);
    }
    50% {
      background-color: rgba(255, 77, 79, 0.25);
      box-shadow: 0 0 20px rgba(255, 77, 79, 0.5);
    }
  }

  // 自定义滚动条样式
  .yaml-code-content::-webkit-scrollbar {
    width: 10px;
    height: 10px;
  }

  .yaml-code-content::-webkit-scrollbar-track {
    background: #1e2530;
    border-radius: 5px;
  }

  .yaml-code-content::-webkit-scrollbar-thumb {
    background: #4a5568;
    border-radius: 5px;

    &:hover {
      background: #718096;
    }
  }
}

.actions {
  display: flex;
  gap: 15px;
  justify-content: space-between;;

  @media (max-width: 768px) {
    flex-direction: column;

    button {
      width: 100%;
    }
  }
}
</style>
