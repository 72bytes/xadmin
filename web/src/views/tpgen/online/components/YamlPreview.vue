<template>
  <a-card class="form-section yaml-preview" :bordered="false">
    <template #title>
      <div class="section-title">
        <icon-file-code />
        Generated Test Plan (YAML)
      </div>
    </template>

    <div class="yaml-content">
      <pre>{{ yamlString }}</pre>
    </div>

    <div class="actions">
      <a-button @click="handleCopy">
        <template #icon><icon-copy /></template>
        Copy to Clipboard
      </a-button>
      <a-button type="primary" @click="handleDownload">
        <template #icon><icon-download /></template>
        Download YAML
      </a-button>
    </div>
  </a-card>
</template>

<script setup lang="ts">
import type { YamlData } from '../types'
import { Message } from '@arco-design/web-vue'

defineOptions({ name: 'YamlPreview' })

const props = defineProps<{
  yamlData: YamlData
}>()

const emit = defineEmits<{
  close: []
}>()

// 将 JavaScript 对象转换为 YAML 字符串
const yamlString = computed(() => {
  return jsToYaml(props.yamlData)
})

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
            }
            else {
              yaml += `${spaces}    ${line.trim()}\n`
            }
          })
        }
        else {
          yaml += `${spaces}  - ${item}\n`
        }
      })
    }
    else if (typeof value === 'object' && value !== null) {
      yaml += `${spaces}${key}:\n${jsToYaml(value, indent + 1)}`
    }
    else {
      yaml += `${spaces}${key}: ${value}\n`
    }
  }

  return yaml
}

// 复制到剪贴板
const handleCopy = async () => {
  try {
    await navigator.clipboard.writeText(yamlString.value)
    Message.success('YAML copied to clipboard!')
  }
  catch (error) {
    Message.error('Failed to copy to clipboard')
  }
}

// 下载 YAML 文件
const handleDownload = () => {
  const blob = new Blob([yamlString.value], { type: 'text/yaml' })
  const url = URL.createObjectURL(blob)
  const a = document.createElement('a')
  a.href = url
  a.download = 'test_plan.yaml'
  document.body.appendChild(a)
  a.click()
  document.body.removeChild(a)
  URL.revokeObjectURL(url)

  Message.success('YAML file downloaded!')
}
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
  padding: 25px;
  border-radius: 12px;
  font-family: 'Fira Code', 'Courier New', monospace;
  max-height: 500px;
  overflow-y: auto;
  margin-bottom: 20px;
  box-shadow: inset 0 2px 10px rgba(0, 0, 0, 0.3);
  border: 1px solid #4a5568;

  pre {
    margin: 0;
    white-space: pre-wrap;
    word-wrap: break-word;
    font-size: 0.9rem;
    line-height: 1.6;
  }
}

.actions {
  display: flex;
  gap: 15px;
  justify-content: flex-end;

  @media (max-width: 768px) {
    flex-direction: column;

    button {
      width: 100%;
    }
  }
}
</style>

