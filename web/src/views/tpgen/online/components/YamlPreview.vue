<template>
  <a-card class="form-section yaml-preview" :bordered="false">
    <!-- <template #title> -->
      <!-- <div class="section-title">
        <icon-code />
        Generated Test Plan (YAML)
      </div> -->
    <!-- </template> -->

    <div class="yaml-content">
      <div 
        ref="editorContainer" 
        class="monaco-editor-container"
        :style="{ height: `${dynamicHeight}px` }"
      />
    </div>

    <!-- ✅ 新增：固定在右下角的按钮组 -->
    <div class="floating-actions">
      <a-button type="primary" @click="handleCopy" class="action-btn">
        <template #icon><icon-copy /></template>
        Copy
      </a-button>

      <a-button v-if="isEditMode" type="primary" @click="handleUpdate" class="action-btn">
        <template #icon><icon-edit /></template>
        Update
      </a-button>
      <a-button v-else type="primary" @click="handleSave" class="action-btn">
        <template #icon><icon-save /></template>
        Save
      </a-button>

      <a-button type="primary" @click="handleDownload" class="action-btn">
        <template #icon><icon-download /></template>
        Download
      </a-button>
    </div>

    
  </a-card>
</template>

<script setup lang="ts">
import { computed, ref, watch, nextTick, shallowRef, onMounted, onBeforeUnmount } from 'vue'
import { Message } from '@arco-design/web-vue'
import type { YamlData } from '../types'
import { jsToYaml } from '../utils/yamlConverter'
import * as monaco from 'monaco-editor'
import editorWorker from 'monaco-editor/esm/vs/editor/editor.worker?worker'
import jsonWorker from 'monaco-editor/esm/vs/language/json/json.worker?worker'

// 配置 Monaco Editor 的 worker
self.MonacoEnvironment = {
  getWorker(_: any, label: string) {
    if (label === 'json') {
      return new jsonWorker()
    }
    return new editorWorker()
  },
}

defineOptions({ name: 'YamlPreview' })

const props = defineProps<{
  yamlData: YamlData
  errorLines?: number[]
  isEditMode?: boolean
  editingPlanId?: string
}>()

// 监听 props 变化
watch(() => props.errorLines, (newVal) => {
  console.log('[YamlPreview props] errorLines prop 收到:', newVal)
}, { immediate: true })

const emit = defineEmits<{
  close: []
  copy: []
  download: []
  save: []
  update: []
}>()




// Monaco Editor 相关 refs
const editorContainer = ref<HTMLElement>()
const editorInstance = shallowRef<monaco.editor.IStandaloneCodeEditor>()
const decorations = ref<string[]>([])

// 编辑器配置选项
const editorOptions = {
  readOnly: true,
  fontSize: 14.4,
  lineHeight: 25.6,
  fontFamily: "'Fira Code', 'Courier New', monospace",
  minimap: { enabled: false },
  scrollBeyondLastLine: false,
  automaticLayout: true,
  lineNumbers: 'on' as const,

  // ✅ 添加滚动优化配置
  stickyScroll: {
    enabled: false,  // ✅ 关键：禁用 sticky scroll，解决第一行冻结问题
  },
  
  scrollbar: {
    vertical: 'visible' as const,
    horizontal: 'visible' as const,
    verticalScrollbarSize: 20,
    horizontalScrollbarSize: 10,
  },
  glyphMargin: true,
  folding: true,
  lineDecorationsWidth: 0,
  lineNumbersMinChars: 4,
}

// 将 JavaScript 对象转换为 YAML 字符串
const yamlString = computed({
  get: () => {
    const yaml = jsToYaml(props.yamlData)
    return yaml.trimEnd()
  },
  set: () => {
    // 只读模式，不允许修改
  },
})

// 将 YAML 字符串按行分割（用于计算高度）
const yamlLines = computed(() => {
  if (!yamlString.value) return []
  return yamlString.value.split('\n')
})

// 动态计算预览区高度
const dynamicHeight = computed(() => {
  const lineCount = yamlLines.value.length
  const lineHeight = 25.6 // 每行高度（px）
  const padding = 30 // 上下内边距总和（px）
  const minHeight = 200 // 最小高度
  const maxHeight = 690 // 最大高度
  
  // 计算内容高度
  const contentHeight = lineCount * lineHeight + padding
  
  // 限制在最小和最大高度之间
  if (contentHeight < minHeight) return minHeight
  if (contentHeight > maxHeight) return maxHeight
  return contentHeight
})

// 定义自定义深色主题（匹配现有样式）
function defineCustomTheme() {
  monaco.editor.defineTheme('custom-dark', {
    base: 'vs-dark',
    inherit: true,
    rules: [
      { token: '', foreground: 'e2e8f0' },
      { token: 'comment', foreground: '718096' },
      { token: 'keyword', foreground: '63b3ed' },
      { token: 'string', foreground: '68d391' },
      { token: 'number', foreground: 'f6ad55' },
    ],
    colors: {
      'editor.background': '#2d3748',
      'editor.foreground': '#e2e8f0',
      'editorLineNumber.foreground': '#718096',
      'editorLineNumber.activeForeground': '#cbd5e0',
      'editor.lineHighlightBackground': '#374151',
      'editorGutter.background': '#1e2530',
      'scrollbarSlider.background': '#4a556866',
      'scrollbarSlider.hoverBackground': '#71809699',
      'scrollbarSlider.activeBackground': '#718096cc',
      'editorCursor.foreground': '#63b3ed',
      'editor.selectionBackground': '#4a556866',
    },
  })
}

// 初始化 Monaco Editor
function initMonacoEditor() {
  if (!editorContainer.value) return

  try {
    // 定义自定义主题
    defineCustomTheme()

    // 创建编辑器实例
    const editor = monaco.editor.create(editorContainer.value, {
      value: yamlString.value,
      language: 'yaml',
      theme: 'custom-dark',
      ...editorOptions,
    })

    editorInstance.value = editor

    console.log('[YamlPreview] Monaco Editor initialized')

    // 初始化时如果有错误行，立即高亮
    if (props.errorLines && props.errorLines.length > 0) {
      updateErrorDecorations()
      scrollToErrorLine()
    }
  } catch (error) {
    console.error('[YamlPreview] Failed to initialize Monaco Editor:', error)
    Message.error('Failed to load code editor')
  }
}

// 更新错误行装饰
function updateErrorDecorations() {
  if (!editorInstance.value || !props.errorLines?.length) {
    if (editorInstance.value && decorations.value.length > 0) {
      decorations.value = editorInstance.value.deltaDecorations(decorations.value, [])
    }
    return
  }

  console.log('[YamlPreview] 更新错误行装饰:', props.errorLines)

  const newDecorations: monaco.editor.IModelDeltaDecoration[] = props.errorLines.map(lineNumber => ({
    range: new monaco.Range(lineNumber, 1, lineNumber, 1),
    options: {
      isWholeLine: true,
      className: 'error-line-decoration',
      glyphMarginClassName: 'error-line-glyph',
      overviewRuler: {
        color: '#ff4d4f',
        position: monaco.editor.OverviewRulerLane.Full,
      },
    },
  }))

  decorations.value = editorInstance.value.deltaDecorations(decorations.value, newDecorations)
}

// 滚动到错误行
function scrollToErrorLine() {
  if (!editorInstance.value || !props.errorLines?.length) {
    return
  }

  console.log('[YamlPreview] 滚动到错误行:', props.errorLines[0])

  nextTick(() => {
    const lineNumber = props.errorLines![0]
    editorInstance.value!.revealLineInCenter(lineNumber, 1) // 1 = Smooth scroll
  })
}

// 复制到剪贴板 - 触发父组件的验证逻辑
const handleCopy = () => {
  emit('copy')
}

// 下载 YAML 文件 - 触发父组件的验证逻辑
const handleDownload = () => {
  emit('download')
}

// 保存按钮 - 触发父组件的保存逻辑
function handleSave() {
  console.log('[YamlPreview handleSave] 触发保存事件')
  emit('save')
}

// 更新按钮 - 触发父组件的更新逻辑
function handleUpdate() {
  console.log('[YamlPreview handleUpdate] 触发更新事件')
  emit('update')
}

// 计算是否为编辑模式
const isEditMode = computed(() => props.isEditMode || false)

// 监听 YAML 内容变化，更新编辑器
watch(() => yamlString.value, (newValue) => {
  if (editorInstance.value) {
    const currentValue = editorInstance.value.getValue()
    if (currentValue !== newValue) {
      editorInstance.value.setValue(newValue)
    }
  }
})

// 监听错误行变化
watch(() => props.errorLines, (newErrorLines) => {
  console.log('[YamlPreview watch] errorLines 变化:', newErrorLines)
  
  if (newErrorLines && newErrorLines.length > 0) {
    console.log('[YamlPreview watch] ✅ 检测到错误行:', newErrorLines)
    updateErrorDecorations()
    scrollToErrorLine()
  } else {
    console.log('[YamlPreview watch] ⚠️ 错误行为空，清除装饰')
    if (editorInstance.value) {
      decorations.value = editorInstance.value.deltaDecorations(decorations.value, [])
    }
  }
}, { immediate: true, deep: true })

// 生命周期钩子
onMounted(() => {
  initMonacoEditor()
})

onBeforeUnmount(() => {
  editorInstance.value?.dispose()
})
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
  border-radius: 12px;
  margin-bottom: 20px;
  box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.3);
  border: 1px solid #4a5568;
  overflow: hidden;
  position: relative; // ✅ 关键：设置为相对定位，作为按钮的定位参考
  
  // Monaco Editor 容器样式
  .monaco-editor-container {
    width: 100%;
    border-radius: 12px;
  }
  
  :deep(.monaco-editor) {
    .margin {
      background-color: #1e2530 !important;
    }
    
    .monaco-scrollable-element {
      .scrollbar {
        .slider {
          background: rgba(74, 85, 104, 0.4) !important;
          
          &:hover {
            background: rgba(113, 128, 150, 0.6) !important;
          }
          
          &.active {
            background: rgba(113, 128, 150, 0.8) !important;
          }
        }
      }
    }
  }
  
  // 错误行装饰样式
  :deep(.error-line-decoration) {
    background-color: rgba(255, 77, 79, 0.15) !important;
    border-left: 4px solid #ff4d4f !important;
    animation: pulse-error 1.5s ease-in-out infinite;
  }
  
  :deep(.error-line-glyph) {
    background-color: #ff4d4f !important;
    width: 3px !important;
    margin-left: 3px;
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
}

// .actions {
//   display: flex;
//   gap: 15px;
//   justify-content: space-between;  // ← 改这里！从 flex-end 改为 space-between

//   @media (max-width: 768px) {
//     flex-direction: column;

//     button {
//       width: 100%;
//     }
//   }
// }


// ✅ 新增：浮动按钮组样式
.floating-actions {
  position: absolute;
  bottom: 50px;
  right: 20px;
  display: flex;
  flex-direction: column; // 垂直排列
  gap: 12px; // 按钮之间的间距
  z-index: 10; // 确保在编辑器内容之上
  pointer-events: none; // 让容器不阻挡鼠标事件
  
  .action-btn {
    pointer-events: auto; // 但按钮本身可以点击
    min-width: 180px;
    height: 44px;
    font-size: 15px;
    font-weight: 500;
    border-radius: 8px;
    backdrop-filter: blur(10px); // 毛玻璃效果
    background: rgba(52, 152, 219, 0.9) !important; // 半透明背景
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%) !important;  // ✅ 紫色渐变

    border: 1px solid rgba(255, 255, 255, 0.2);
    box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15);
    transition: all 0.3s ease;
    
    &:hover {
      transform: translateX(-5px); // 悬停时向左移动
      // background: rgba(41, 128, 185, 0.95) !important;
      background: linear-gradient(135deg, #5568d3 0%, #6a4190 100%) !important;  // ✅ 悬停时稍微深一点的紫色

      box-shadow: 0 6px 20px rgba(52, 152, 219, 0.4);
      
    }
    
    &:active {
      transform: translateX(-5px) scale(0.98);
    }
  }
  
  // 响应式：小屏幕时调整位置
  @media (max-width: 768px) {
    right: 10px;
    bottom: 10px;
    gap: 8px;
    
    .action-btn {
      min-width: 100px;
      height: 36px;
      font-size: 13px;
    }
  }
}

</style>

