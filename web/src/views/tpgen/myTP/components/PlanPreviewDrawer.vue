<template>
  <a-drawer
    v-model:visible="visible"
    :width="800"
    title="测试计划配置详情"
    :footer="false"
  >
    <template v-if="record">
      <a-descriptions :column="2" bordered>
        <a-descriptions-item label="计划名称" :span="2">
          <a-typography-text copyable>{{ record.name }}</a-typography-text>
        </a-descriptions-item>

        <a-descriptions-item label="类别">
          <a-tag v-if="record.category === 'Benchmark'" color="blue">Benchmark</a-tag>
          <a-tag v-else-if="record.category === 'Functional'" color="green">Functional</a-tag>
          <a-tag v-else-if="record.category === 'Performance'" color="orange">Performance</a-tag>
          <a-tag v-else-if="record.category === 'Stress'" color="red">Stress</a-tag>
          <a-tag v-else color="purple">Custom</a-tag>
        </a-descriptions-item>

        <a-descriptions-item label="状态">
          <a-tag v-if="record.status === 1" color="gray">草稿</a-tag>
          <a-tag v-else-if="record.status === 2" color="green">已发布</a-tag>
          <a-tag v-else color="arcoblue">归档</a-tag>
        </a-descriptions-item>

        <a-descriptions-item label="描述" :span="2">
          {{ record.description || '-' }}
        </a-descriptions-item>

        <a-descriptions-item label="CPU">
          {{ record.cpu || '-' }}
        </a-descriptions-item>

        <a-descriptions-item label="GPU">
          {{ record.gpu || '-' }}
        </a-descriptions-item>

        <a-descriptions-item label="机器数量">
          {{ record.machineCount }}
        </a-descriptions-item>

        <a-descriptions-item label="操作系统">
          {{ record.osType || '-' }}
        </a-descriptions-item>

        <a-descriptions-item label="内核类型">
          {{ record.kernelType || '-' }}
        </a-descriptions-item>

        <a-descriptions-item label="测试用例数">
          {{ record.testCaseCount }}
        </a-descriptions-item>

        <a-descriptions-item label="使用次数">
          {{ record.useCount }}
        </a-descriptions-item>

        <a-descriptions-item label="最后使用">
          {{ record.lastUsedTime || '-' }}
        </a-descriptions-item>

        <a-descriptions-item label="标签" :span="2">
          <a-space v-if="record.tags" wrap :size="4">
            <a-tag v-for="tag in record.tags.split(',')" :key="tag" size="small">
              {{ tag }}
            </a-tag>
          </a-space>
          <span v-else>-</span>
        </a-descriptions-item>

        <a-descriptions-item label="创建人">
          {{ record.createUserString }}
        </a-descriptions-item>

        <a-descriptions-item label="创建时间">
          {{ record.createTime }}
        </a-descriptions-item>
      </a-descriptions>

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
  if (!props.record?.configData) return ''
  return jsToYaml(props.record.configData)
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
