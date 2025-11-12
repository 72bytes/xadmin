<template>
  <a-card class="form-section" :bordered="false">
    <template #title>
      <div class="section-title">
        <icon-robot />
        Firmware Management
      </div>
    </template>

    <a-form-item label="GPU Firmware Version">
      <a-select
        v-model="localFirmwareVersion"
        placeholder="Select firmware version"
        @change="handleUpdate"
      >
        <a-option v-for="option in firmwareVersionOptions" :key="option.value" :value="option.value">
          {{ option.label }}
        </a-option>
      </a-select>
    </a-form-item>

    <a-form-item label="Version Comparison Testing">
      <a-checkbox v-model="localVersionComparison" @change="handleUpdate">
        Enable firmware version comparison testing
      </a-checkbox>
    </a-form-item>
  </a-card>
</template>

<script setup lang="ts">
import { firmwareVersionOptions } from '../mockData'

defineOptions({ name: 'FirmwareConfig' })

const props = defineProps<{
  firmwareVersion: string
  versionComparison: boolean
}>()

const emit = defineEmits<{
  'update:firmwareVersion': [value: string]
  'update:versionComparison': [value: boolean]
  'update': []
}>()

const localFirmwareVersion = computed({
  get: () => props.firmwareVersion,
  set: (val) => emit('update:firmwareVersion', val),
})

const localVersionComparison = computed({
  get: () => props.versionComparison,
  set: (val) => emit('update:versionComparison', val),
})

const handleUpdate = () => {
  emit('update')
}
</script>

<style scoped lang="scss">
.form-section {
  background: white;
  border-radius: 12px;
  margin-bottom: 25px;
  box-shadow: 0 8px 30px rgba(0, 0, 0, 0.08);
  border-left: 5px solid #3498db;
  transition: all 0.3s ease;

  &:hover {
    transform: translateY(-5px);
    box-shadow: 0 12px 40px rgba(0, 0, 0, 0.12);
  }

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
</style>
