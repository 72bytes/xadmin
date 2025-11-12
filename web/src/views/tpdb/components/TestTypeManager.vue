<template>
  <div class="manager-container">
    <!-- 操作栏 -->
    <div class="toolbar">
      <a-button type="primary" @click="handleAdd">
        <template #icon>
          <icon-plus />
        </template>
        新增测试类型
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
      <template #typeName="{ record }">
        <a-tag color="purple">{{ record.typeName }}</a-tag>
      </template>

      <template #operations="{ record }">
        <a-space>
          <a-button type="text" size="small" @click="handleEdit(record)">
            <template #icon>
              <icon-edit />
            </template>
            编辑
          </a-button>
          <a-popconfirm content="确定要删除此测试类型吗？" @ok="handleDelete(record.id)">
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
      :width="500"
      @cancel="handleModalCancel"
      @ok="handleModalOk"
    >
      <a-form :model="formData" :label-col-props="{ span: 6 }" :wrapper-col-props="{ span: 18 }">
        <a-form-item label="类型名称" field="typeName" required>
          <a-input v-model="formData.typeName" placeholder="如: Benchmark, Functional, Performance" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { Message } from '@arco-design/web-vue'
import * as tpdbApi from '@/apis/tpdb'
import type { TestType, TestTypeForm } from '@/apis/tpdb'

defineOptions({ name: 'TestTypeManager' })

const loading = ref(false)
const dataList = ref<TestType[]>([])

const columns = [
  { title: 'ID', dataIndex: 'id', width: 80 },
  { title: '类型名称', dataIndex: 'typeName', slotName: 'typeName', width: 200 },
  { title: '创建时间', dataIndex: 'createdAt', width: 180 },
  { title: '更新时间', dataIndex: 'updatedAt', width: 180 },
  { title: '操作', slotName: 'operations', width: 160, align: 'center' as const },
]

const modalVisible = ref(false)
const modalMode = ref<'add' | 'edit'>('add')
const modalTitle = computed(() => (modalMode.value === 'add' ? '新增测试类型' : '编辑测试类型'))
const currentEditId = ref<number>()

const formData = reactive<TestTypeForm>({
  typeName: '',
})

const loadData = async () => {
  loading.value = true
  try {
    const res = await tpdbApi.listTestTypes()
    if (res.success) {
      dataList.value = res.data || []
    }
  } catch (error) {
    Message.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const handleAdd = () => {
  modalMode.value = 'add'
  modalVisible.value = true
  formData.typeName = ''
}

const handleEdit = (record: TestType) => {
  modalMode.value = 'edit'
  modalVisible.value = true
  currentEditId.value = record.id
  formData.typeName = record.typeName
}

const handleDelete = async (id: number) => {
  try {
    await tpdbApi.deleteTestType(id)
    Message.success('删除成功')
    loadData()
  } catch (error) {
    Message.error('删除失败')
  }
}

const handleModalOk = async () => {
  if (!formData.typeName) {
    Message.warning('请输入类型名称')
    return
  }

  try {
    if (modalMode.value === 'add') {
      await tpdbApi.createTestType(formData)
      Message.success('新增成功')
    } else {
      await tpdbApi.updateTestType(currentEditId.value!, formData)
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
  padding: 16px;
  background: var(--color-bg-2);
  border-radius: 4px;
}
</style>
