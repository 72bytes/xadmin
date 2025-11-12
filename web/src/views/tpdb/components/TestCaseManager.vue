<template>
  <div class="manager-container">
    <!-- 搜索和操作栏 -->
    <div class="toolbar">
      <a-space>
        <a-cascader
          v-model="selectedComponent"
          :options="componentOptions"
          placeholder="选择测试类型和组件"
          style="width: 300px"
          allow-clear
          @change="handleComponentChange"
        />
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
        新增测试用例
      </a-button>
    </div>

    <!-- 数据表格 -->
    <a-table
      :columns="columns"
      :data="dataList"
      :loading="loading"
      :pagination="pagination"
      row-key="id"
      @page-change="handlePageChange"
      @page-size-change="handlePageSizeChange"
    >
      <template #caseName="{ record }">
        <a-tag color="blue">{{ record.caseName }}</a-tag>
      </template>

      <template #caseConfig="{ record }">
        <a-button type="text" size="small" @click="handleViewConfig(record)">
          <template #icon>
            <icon-eye />
          </template>
          查看配置
        </a-button>
      </template>

      <template #operations="{ record }">
        <a-space>
          <a-button type="text" size="small" @click="handleEdit(record)">
            <template #icon>
              <icon-edit />
            </template>
            编辑
          </a-button>
          <a-popconfirm content="确定要删除此测试用例吗？" @ok="handleDelete(record.id)">
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
      :width="700"
      @cancel="handleModalCancel"
      @ok="handleModalOk"
    >
      <a-form :model="formData" :label-col-props="{ span: 6 }" :wrapper-col-props="{ span: 18 }">
        <a-form-item label="测试组件" field="testComponentId" required>
          <a-cascader
            v-model="formComponentPath"
            :options="componentOptions"
            placeholder="请选择测试类型和组件"
            @change="handleFormComponentChange"
          />
        </a-form-item>
        <a-form-item label="用例名称" field="caseName" required>
          <a-input v-model="formData.caseName" placeholder="请输入测试用例名称" />
        </a-form-item>
        <a-form-item label="用例配置" field="caseConfig">
          <a-textarea
            v-model="configJson"
            placeholder="请输入JSON格式配置，如: {&quot;timeout&quot;: 300}"
            :auto-size="{ minRows: 4, maxRows: 10 }"
          />
        </a-form-item>
      </a-form>
    </a-modal>

    <!-- 配置查看弹窗 -->
    <a-modal
      v-model:visible="configModalVisible"
      title="测试用例配置"
      :width="600"
      :footer="false"
    >
      <pre class="config-content">{{ configViewContent }}</pre>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { Message } from '@arco-design/web-vue'
import * as tpdbApi from '@/apis/tpdb'
import type { TestCase, TestCaseForm, TestCaseQuery, TestComponent, TestType } from '@/apis/tpdb'

defineOptions({ name: 'TestCaseManager' })

const loading = ref(false)
const dataList = ref<TestCase[]>([])
const testTypes = ref<TestType[]>([])
const testComponents = ref<TestComponent[]>([])

const queryForm = reactive<TestCaseQuery>({
  testComponentId: undefined,
  page: 1,
  size: 10,
})

const pagination = computed(() => ({
  current: queryForm.page || 1,
  pageSize: queryForm.size || 10,
  total: dataList.value.length,
  showTotal: true,
  showPageSize: true,
}))

const columns = [
  { title: 'ID', dataIndex: 'id', width: 80 },
  { title: '用例名称', slotName: 'caseName', width: 250 },
  { title: '用例配置', slotName: 'caseConfig', width: 120, align: 'center' as const },
  { title: '创建时间', dataIndex: 'createdAt', width: 160 },
  { title: '更新时间', dataIndex: 'updatedAt', width: 160 },
  { title: '操作', slotName: 'operations', width: 160, align: 'center' as const },
]

// 级联选择器
const selectedComponent = ref<(string | number)[]>([])
const formComponentPath = ref<(string | number)[]>([])

const componentOptions = computed(() => {
  return testTypes.value.map((type) => ({
    value: type.id,
    label: type.typeName,
    children: testComponents.value
      .filter((comp) => comp.testTypeId === type.id)
      .map((comp) => ({
        value: comp.id,
        label: comp.componentName,
      })),
  }))
})

const modalVisible = ref(false)
const modalMode = ref<'add' | 'edit'>('add')
const modalTitle = computed(() => (modalMode.value === 'add' ? '新增测试用例' : '编辑测试用例'))
const currentEditId = ref<number>()

const formData = reactive<TestCaseForm>({
  testComponentId: 0,
  caseName: '',
  caseConfig: {},
})

const configJson = ref('')

// 配置查看
const configModalVisible = ref(false)
const configViewContent = ref('')

const handleComponentChange = (value: any) => {
  if (value && value.length === 2) {
    queryForm.testComponentId = value[1]
  } else {
    queryForm.testComponentId = undefined
  }
}

const handleFormComponentChange = (value: any) => {
  if (value && value.length === 2) {
    formData.testComponentId = value[1]
  }
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

const loadTestComponents = async () => {
  try {
    const res = await tpdbApi.listTestComponents()
    if (res.success) {
      testComponents.value = res.data || []
    }
  } catch (error) {
    Message.error('加载测试组件失败')
  }
}

const loadData = async () => {
  loading.value = true
  try {
    const res = await tpdbApi.listTestCases(queryForm)
    if (res.success) {
      dataList.value = res.data?.list || []
    }
  } catch (error) {
    Message.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

const handleSearch = () => {
  queryForm.page = 1
  loadData()
}

const handleReset = () => {
  selectedComponent.value = []
  queryForm.testComponentId = undefined
  queryForm.page = 1
  loadData()
}

const handlePageChange = (page: number) => {
  queryForm.page = page
  loadData()
}

const handlePageSizeChange = (size: number) => {
  queryForm.size = size
  queryForm.page = 1
  loadData()
}

const handleAdd = () => {
  modalMode.value = 'add'
  modalVisible.value = true
  formComponentPath.value = []
  Object.assign(formData, {
    testComponentId: 0,
    caseName: '',
    caseConfig: {},
  })
  configJson.value = ''
}

const handleEdit = (record: TestCase) => {
  modalMode.value = 'edit'
  modalVisible.value = true
  currentEditId.value = record.id

  // 找到组件所属的测试类型
  const component = testComponents.value.find((c) => c.id === record.testComponentId)
  if (component) {
    formComponentPath.value = [component.testTypeId, component.id]
  }

  Object.assign(formData, {
    testComponentId: record.testComponentId,
    caseName: record.caseName,
    caseConfig: record.caseConfig || {},
  })
  configJson.value = JSON.stringify(record.caseConfig || {}, null, 2)
}

const handleDelete = async (id: number) => {
  try {
    await tpdbApi.deleteTestCase(id)
    Message.success('删除成功')
    loadData()
  } catch (error) {
    Message.error('删除失败')
  }
}

const handleViewConfig = (record: TestCase) => {
  configViewContent.value = JSON.stringify(record.caseConfig || {}, null, 2)
  configModalVisible.value = true
}

const handleModalOk = async () => {
  if (!formData.testComponentId || !formData.caseName) {
    Message.warning('请填写必填项')
    return
  }

  // 解析 JSON 配置
  if (configJson.value) {
    try {
      formData.caseConfig = JSON.parse(configJson.value)
    } catch (error) {
      Message.error('配置JSON格式错误')
      return
    }
  } else {
    formData.caseConfig = {}
  }

  try {
    if (modalMode.value === 'add') {
      await tpdbApi.createTestCase(formData)
      Message.success('新增成功')
    } else {
      await tpdbApi.updateTestCase(currentEditId.value!, formData)
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

onMounted(async () => {
  await loadTestTypes()
  await loadTestComponents()
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

.config-content {
  background: var(--color-fill-2);
  padding: 12px;
  border-radius: 4px;
  font-size: 13px;
  line-height: 1.6;
  max-height: 400px;
  overflow: auto;
}
</style>
