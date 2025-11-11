<template>
  <div class="code-editor-wrapper">
    <vue-monaco-editor
      v-model:value="localValue"
      :language="monacoLanguage"
      :options="editorOptions"
      :theme="'vs'"
      @change="handleEditorChange"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { VueMonacoEditor } from '@guolao/vue-monaco-editor'

interface Props {
  modelValue?: string
  language?: string
  readonly?: boolean
}

interface Emits {
  (e: 'change', value: string): void
}

const props = withDefaults(defineProps<Props>(), {
  modelValue: '',
  language: 'text',
  readonly: false,
})

const emit = defineEmits<Emits>()

// 本地值，用于 v-model
const localValue = ref(props.modelValue)

// 监听 props 变化，同步到本地值
watch(() => props.modelValue, (newValue) => {
  if (newValue !== localValue.value) {
    localValue.value = newValue
  }
})

// 语言映射：将文件扩展名映射到 Monaco Editor 支持的语言
const monacoLanguage = computed(() => {
  const lang = props.language?.toLowerCase() || 'text'
  
  // 语言映射表
  const languageMap: Record<string, string> = {
    'json': 'json',
    'yaml': 'yaml',
    'yml': 'yaml',
    'sh': 'shell',
    'bash': 'shell',
    'shell': 'shell',
    'python': 'python',
    'py': 'python',
  }
  
  return languageMap[lang] || 'plaintext'
})

// Monaco Editor 配置选项
const editorOptions = computed(() => ({
  automaticLayout: true, // 自动布局
  fontSize: 14,
  tabSize: 2,
  lineNumbers: 'on' as const, // 显示行号
  folding: true, // 代码折叠
  minimap: { enabled: false }, // 关闭小地图
  scrollBeyondLastLine: false,
  readOnly: props.readonly,
  wordWrap: 'on' as const, // 自动换行
  theme: 'vs', // 明亮主题
}))

// 防抖更新
let updateTimer: ReturnType<typeof setTimeout> | null = null

const handleEditorChange = (value: string) => {
  if (updateTimer) {
    clearTimeout(updateTimer)
  }
  
  updateTimer = setTimeout(() => {
    emit('change', value)
  }, 300)
}
</script>

<style scoped lang="less">
.code-editor-wrapper {
  height: 100%;
  width: 100%;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}
</style>
