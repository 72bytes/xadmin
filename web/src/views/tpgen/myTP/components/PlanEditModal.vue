<template>
  <a-modal
    v-model:visible="visible"
    title="编辑测试计划"
    :width="600"
    @ok="handleOk"
    @cancel="handleCancel"
  >
    <a-form v-if="form" :model="form" layout="vertical">
      <a-form-item label="计划名称" required>
        <a-input
          v-model="form.name"
          placeholder="请输入计划名称"
          :max-length="100"
          show-word-limit
        />
      </a-form-item>

      <a-form-item label="类别" required>
        <a-select v-model="form.category" placeholder="请选择类别">
          <a-option value="Benchmark">Benchmark - 基准测试</a-option>
          <a-option value="Functional">Functional - 功能测试</a-option>
          <a-option value="Performance">Performance - 性能测试</a-option>
          <a-option value="Stress">Stress - 压力测试</a-option>
          <a-option value="Custom">Custom - 自定义</a-option>
        </a-select>
      </a-form-item>

      <a-form-item label="描述">
        <a-textarea
          v-model="form.description"
          placeholder="请输入描述信息"
          :rows="4"
          :max-length="500"
          show-word-limit
        />
      </a-form-item>

      <a-form-item label="标签">
        <a-input
          v-model="form.tags"
          placeholder="多个标签用逗号分隔"
          :max-length="200"
        />
      </a-form-item>

      <a-form-item label="状态">
        <a-radio-group v-model="form.status">
          <a-radio :value="1">草稿</a-radio>
          <a-radio :value="2">已发布</a-radio>
          <a-radio :value="3">归档</a-radio>
        </a-radio-group>
      </a-form-item>
    </a-form>
  </a-modal>
</template>

<script setup lang="ts">
import type { EditForm } from '../types'

interface Props {
  modelValue: boolean
  form: EditForm | null
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'update:modelValue': [value: boolean]
  'ok': []
  'cancel': []
}>()

const visible = computed({
  get: () => props.modelValue,
  set: (val) => emit('update:modelValue', val),
})

const handleOk = () => {
  emit('ok')
}

const handleCancel = () => {
  emit('cancel')
}
</script>
