<template>
  <div class="manager-container">
    <!-- 搜索和操作栏 -->
    <div class="toolbar">
      <a-space>
        <a-select
          v-model="queryForm.testTypeId"
          placeholder="选择测试类型"
          style="width: 200px"
          allow-clear
          @change="handleSearch"
        >
          <a-option v-for="type in testTypes" :key="type.id" :value="type.id">
            {{ type.typeName }}
          </a-option>
        </a-select>
        <a-input
          v-model="queryForm.componentCategory"
          placeholder="搜索组件分类"
          style="width: 200px"
          allow-clear
          @press-enter="handleSearch"
        >
          <template #prefix>
            <icon-search />
          </template>
        </a-input>
        <a-button type="primary" @click="handleSearch">
          <template #icon>
            <icon-search />
          </template>
          查询
        </a-button>
        <a-button @click="handleReset">
          <template #icon>
            <icon-refresh />
          </template>
          重置
        </a-button>
      </a-space>
      <a-button type="primary" @click="handleAdd">
        <template #icon>
          <icon-plus />
        </template>
        新增组件
      </a-button>
    </div>

    <!-- 数据表格 -->
    <a-table
      :columns="columns"
      :data="dataList"
      :loading="loading"
      row-key="id"
      :pagination="false"
    >
      <template #testType="{ record }">
        <a-tag color="purple">
          {{ getTestTypeName(record.testTypeId) }}
        </a-tag>
      </template>

      <template #componentCategory="{ record }">
        <a-tag v-if="record.componentCategory" color="blue">
          {{ record.componentCategory }}
        </a-tag>
        <span v-else class="text-muted">-</span>
      </template>

      <template #componentName="{ record }">
        <a-tag color="green">{{ record.componentName }}</a-tag>
      </template>

      <template #operations="{ record }">
        <a-space>
          <a-button type="text" size="small" @click="handleEdit(record)">
            <template #icon>
              <icon-edit />
            </template>
            编辑
          </a-button>
          <a-popconfirm content="确定要删除此组件吗？" @ok="handleDelete(record.id)">
            <a-button type="text" size="small" status="danger">
              <template #icon>
                <icon-delete />
              </template>
              删除
            </a-button>
          </a-popconfirm>
        </a-space>
      </template>
    </a-table>

    <!-- 添加/编辑弹窗 -->
    <a-modal
      v-model:visible="modalVisible"
      :title="modalTitle"
      :width="600"
      @cancel="handleModalCancel"
      @ok="handleModalOk"
    >
      <a-form :model="formData" :label-col-props="{ span: 6 }" :wrapper-col-props="{ span: 18 }">
        <a-form-item label="测试类型" field="testTypeId" required>
          <a-select v-model="formData.testTypeId" placeholder="请选择测试类型">
            <a-option v-for="type in testTypes" :key="type.id" :value="type.id">
              {{ type.typeName }}
            </a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="组件分类" field="componentCategory">
          <a-input v-model="formData.componentCategory" placeholder="如: Media, Compute" />
        </a-form-item>
        <a-form-item label="组件名称" field="componentName" required>
          <a-input v-model="formData.componentName" placeholder="如: ffmpeg, clpeak" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { Message } from '@arco-design/web-vue'
import * as tpdbApi from '@/apis/tpdb'
import type { TestComponent, TestComponentForm, TestComponentQuery, TestType } from '@/apis/tpdb'

defineOptions({ name: 'TestComponentManager' })

const loading = ref(false)
const dataList = ref<TestComponent[]>([])
const testTypes = ref<TestType[]>([])

const queryForm = reactive<TestComponentQuery>({
  testTypeId: undefined,
  componentCategory: '',
})

const columns = [
  { title: 'ID', dataIndex: 'id', width: 80 },
  { title: '测试类型', slotName: 'testType', width: 150 },
  { title: '组件分类', slotName: 'componentCategory', width: 150 },
  { title: '组件名称', slotName: 'componentName', width: 200 },
  { title: '操作', slotName: 'operations', width: 160, align: 'center' as const },
]

const modalVisible = ref(false)
const modalMode = ref<'add' | 'edit'>('add')
const modalTitle = computed(() => (modalMode.value === 'add' ? '新增测试组件' : '编辑测试组件'))
const currentEditId = ref<number>()

const formData = reactive<TestComponentForm>({
  testTypeId: 0,
  componentCategory: '',
  componentName: '',
})

const getTestTypeName = (id: number) => {
  const type = testTypes.value.find((t) => t.id === id)
  return type?.typeName || '-'
}

const loadTestTypes = async () => {
  try {
    const res = await tpdbApi.listTestTypes()
    if (res.success) {
      testTypes.value = res.data || []
    }
  } catch (error) {
    Message.error('加载测试类型失败')
  }
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await tpdbApi.listTestComponents(queryForm)
    if (res.success) {
      dataList.value = res.data || []
    }
  } catch (error) {
    Message.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  loadData()
}

const handleReset = () => {
  queryForm.testTypeId = undefined
  queryForm.componentCategory = ''
  loadData()
}

const handleAdd = () => {
  modalMode.value = 'add'
  modalVisible.value = true
  Object.assign(formData, {
    testTypeId: 0,
    componentCategory: '',
    componentName: '',
  })
}

const handleEdit = (record: TestComponent) => {
  modalMode.value = 'edit'
  modalVisible.value = true
  currentEditId.value = record.id
  Object.assign(formData, {
    testTypeId: record.testTypeId,
    componentCategory: record.componentCategory || '',
    componentName: record.componentName,
  })
}

const handleDelete = async (id: number) => {
  try {
    await tpdbApi.deleteTestComponent(id)
    Message.success('删除成功')
    loadData()
  } catch (error) {
    Message.error('删除失败')
  }
}

const handleModalOk = async () => {
  if (!formData.testTypeId || !formData.componentName) {
    Message.warning('请填写必填项')
    return
  }

  try {
    if (modalMode.value === 'add') {
      await tpdbApi.createTestComponent(formData)
      Message.success('新增成功')
    } else {
      await tpdbApi.updateTestComponent(currentEditId.value!, formData)
      Message.success('更新成功')
    }
    modalVisible.value = false
    loadData()
  } catch (error) {
    Message.error(modalMode.value === 'add' ? '新增失败' : '更新失败')
  }
}

const handleModalCancel = () => {
  modalVisible.value = false
}

onMounted(() => {
  loadTestTypes()
  loadData()
})
</script>

<style scoped lang="scss">
.manager-container {
  display: flex;
  flex-direction: column;
  gap: 16px;
  height: 100%;
}

.toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: var(--color-bg-2);
  border-radius: 4px;
}

.text-muted {
  color: var(--color-text-4);
}
</style>
