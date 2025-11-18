<template>
  <a-drawer
    v-model:visible="visible"
    :width="800"
    title="测试计划配置详情"
    :footer="false"
  >
    <template v-if="record">

      <a-divider>配置详情</a-divider>
      <div class="config-yaml">
        <pre>{{ yamlString }}</pre>
      </div>
    </template>
  </a-drawer>
</template>

<script setup lang="ts">
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

// 将 JavaScript 对象转换为 YAML 字符串
const yamlString = computed(() => {
  if (!props.record?.yamlData) return ''
  return jsToYaml(props.record.yamlData)
})

function jsToYaml(obj: any, indent = 0): string {
  let yaml = ''
  const spaces = '  '.repeat(indent)

  // 对键进行排序，将 metadata 放在最前面
  const entries = Object.entries(obj)
  const sortedEntries = entries.sort(([keyA], [keyB]) => {
    if (keyA === 'metadata') return -1
    if (keyB === 'metadata') return 1
    return 0
  })

  for (const [key, value] of sortedEntries) {
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
    } else if (value !== null && value !== undefined) {
      yaml += `${spaces}${key}: ${value}\n`
    }
  }

  return yaml
}
</script>

<style scoped lang="scss">
.config-yaml {
  max-height: 400px;
  overflow-y: auto;
  background: #2d3748;
  color: #e2e8f0;
  border-radius: 8px;
  padding: 16px;
  box-shadow: inset 0 2px 8px rgba(0, 0, 0, 0.2);
  border: 1px solid #4a5568;

  pre {
    margin: 0;
    font-size: 13px;
    font-family: 'Fira Code', 'Courier New', Courier, monospace;
    white-space: pre-wrap;
    word-wrap: break-word;
    line-height: 1.6;
    color: #e2e8f0;
  }
}
</style>
