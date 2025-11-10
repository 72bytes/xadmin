<template>
  <a-drawer
    v-model:visible="visible"
    title="测试计划详情"
    :width="width >= 600 ? 600 : '100%'"
    :footer="false"
    unmount-on-close
    @close="reset"
  >
    <a-spin :loading="loading" style="width: 100%">
      <a-descriptions :column="1" bordered size="large">
        <a-descriptions-item label="ID">{{ detail.id }}</a-descriptions-item>
        <a-descriptions-item label="名称">{{ detail.name }}</a-descriptions-item>
        <a-descriptions-item label="编号">{{ detail.code }}</a-descriptions-item>
        <a-descriptions-item label="描述">
          <div style="white-space: pre-wrap">{{ detail.description || '-' }}</div>
        </a-descriptions-item>
        <a-descriptions-item label="开始时间">{{ detail.startTime || '-' }}</a-descriptions-item>
        <a-descriptions-item label="结束时间">{{ detail.endTime || '-' }}</a-descriptions-item>
        <a-descriptions-item label="负责人">{{ detail.ownerName || '-' }}</a-descriptions-item>
        <a-descriptions-item label="优先级">
          <a-tag v-if="detail.priority === 1" color="red">高</a-tag>
          <a-tag v-else-if="detail.priority === 2" color="orange">中</a-tag>
          <a-tag v-else-if="detail.priority === 3" color="blue">低</a-tag>
          <span v-else>-</span>
        </a-descriptions-item>
        <a-descriptions-item label="状态">
          <a-tag v-if="detail.status === 1" color="gray">未开始</a-tag>
          <a-tag v-else-if="detail.status === 2" color="blue">进行中</a-tag>
          <a-tag v-else-if="detail.status === 3" color="green">已完成</a-tag>
          <a-tag v-else-if="detail.status === 4" color="red">已取消</a-tag>
          <span v-else>-</span>
        </a-descriptions-item>
        <a-descriptions-item label="测试类型">{{ detail.testType || '-' }}</a-descriptions-item>
        <a-descriptions-item label="测试环境">{{ detail.testEnv || '-' }}</a-descriptions-item>
        <a-descriptions-item label="关联项目">{{ detail.relatedProject || '-' }}</a-descriptions-item>
        <a-descriptions-item label="备注">
          <div style="white-space: pre-wrap">{{ detail.remark || '-' }}</div>
        </a-descriptions-item>
        <a-descriptions-item label="创建人">{{ detail.createUserString }}</a-descriptions-item>
        <a-descriptions-item label="创建时间">{{ detail.createTime }}</a-descriptions-item>
        <a-descriptions-item label="更新人">{{ detail.updateUserString || '-' }}</a-descriptions-item>
        <a-descriptions-item label="更新时间">{{ detail.updateTime || '-' }}</a-descriptions-item>
      </a-descriptions>
    </a-spin>
  </a-drawer>
</template>

<script setup lang="ts">
import { useWindowSize } from '@vueuse/core'
import { Message } from '@arco-design/web-vue'
import { getTestPlan, type TestPlanDetailResp } from '@/apis/test/plan'

const { width } = useWindowSize()

const visible = ref(false)
const loading = ref(false)

const detail = ref<TestPlanDetailResp>({
  id: '',
  name: '',
  code: '',
  description: '',
  startTime: '',
  endTime: '',
  ownerId: null,
  ownerName: '',
  priority: 2,
  status: 1,
  testType: '',
  testEnv: '',
  relatedProject: '',
  remark: '',
  createUser: 0,
  createUserString: '',
  createTime: '',
  updateUser: null,
  updateUserString: '',
  updateTime: '',
})

// 重置
const reset = () => {
  detail.value = {
    id: '',
    name: '',
    code: '',
    description: '',
    startTime: '',
    endTime: '',
    ownerId: null,
    ownerName: '',
    priority: 2,
    status: 1,
    testType: '',
    testEnv: '',
    relatedProject: '',
    remark: '',
    createUser: 0,
    createUserString: '',
    createTime: '',
    updateUser: null,
    updateUserString: '',
    updateTime: '',
  }
}

// 加载数据
const loadData = async (id: string) => {
  try {
    loading.value = true
    const res = await getTestPlan(id)
    detail.value = res.data
  } catch (error) {
    Message.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 打开
const onOpen = async (id: string) => {
  reset()
  visible.value = true
  await loadData(id)
}

defineExpose({ onOpen })
</script>

<style scoped lang="scss">
:deep(.arco-descriptions-item-label) {
  width: 120px;
  font-weight: 500;
}
</style>

