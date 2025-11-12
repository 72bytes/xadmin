<template>
  <div class="tpdb-container">
    <div class="tpdb-header">
      <div class="header-content">
        <h1>
          <icon-database />
          TPDB - Test Plan Database
        </h1>
        <p class="header-desc">测试计划数据库管理</p>
      </div>
    </div>

    <div class="tpdb-main">
      <a-tabs v-model:active-key="activeTab" type="card-gutter" class="tpdb-tabs">
        <a-tab-pane key="sutDevice">
          <template #title>
            <icon-desktop />
            测试设备
          </template>
          <SutDeviceManager />
        </a-tab-pane>

        <a-tab-pane key="osConfig">
          <template #title>
            <icon-apps />
            操作系统配置
          </template>
          <OsConfigManager />
        </a-tab-pane>

        <a-tab-pane key="testType">
          <template #title>
            <icon-folder />
            测试类型
          </template>
          <TestTypeManager />
        </a-tab-pane>

        <a-tab-pane key="testComponent">
          <template #title>
            <icon-layers />
            测试组件
          </template>
          <TestComponentManager />
        </a-tab-pane>

        <a-tab-pane key="testCase">
          <template #title>
            <icon-file-text />
            测试用例
          </template>
          <TestCaseManager />
        </a-tab-pane>
      </a-tabs>
    </div>
  </div>
</template>

<script setup lang="ts">
import SutDeviceManager from './components/SutDeviceManager.vue'
import OsConfigManager from './components/OsConfigManager.vue'
import TestTypeManager from './components/TestTypeManager.vue'
import TestComponentManager from './components/TestComponentManager.vue'
import TestCaseManager from './components/TestCaseManager.vue'
import type { TabKey } from './types'

defineOptions({ name: 'TPDBManagement' })

const activeTab = ref<TabKey>('sutDevice')
</script>

<style scoped lang="scss">
@import './index.scss';
</style>
