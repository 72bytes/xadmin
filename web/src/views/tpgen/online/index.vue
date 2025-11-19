<template>
  <div class="tpgen-container">
    <div class="tpgen-header">
      <div class="header-content">
        <h1>
          <icon-experiment />
          TPGen - Test Plan Generator
        </h1>
        <div v-if="activeTab === 'custom'" class="progress-info">
          Progress: {{ progress }}%
        </div>
      </div>
    </div>

    <div class="tpgen-main">
      <a-tabs v-model:active-key="activeTab" type="rounded" class="tpgen-tabs">
        <a-tab-pane key="upload" title="上传测试计划">
          <template #title>
            <icon-upload />
            Upload Test Plan
          </template>
          <UploadPlan />
        </a-tab-pane>

        <a-tab-pane key="custom" title="自定义测试计划">
          <template #title>
            <icon-settings />
            Generate Test Plan
          </template>
          <CustomPlan @progress-change="handleProgressChange" />
        </a-tab-pane>
      </a-tabs>










    </div>
  </div>
</template>
<script setup lang="ts">
import { ref } from 'vue'
import UploadPlan from './components/UploadPlan.vue'
import CustomPlan from './components/CustomPlan.vue'

defineOptions({ name: 'TPGenOnline' })

const activeTab = ref('upload')
const progress = ref(0)

const handleProgressChange = (val: number) => {
  progress.value = val
}
</script>

<style scoped lang="scss">
@import './index.scss';
</style>
