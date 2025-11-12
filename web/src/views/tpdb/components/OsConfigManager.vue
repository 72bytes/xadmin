<template>
  <div class="manager-container">
    <!-- 搜索和操作栏 -->
    <div class="toolbar">
      <a-space>
        <a-input
          v-model="queryForm.osFamily"
          placeholder="搜索操作系统家族"
          style="width: 250px"
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
        新增配置
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
      <template #osFamily="{ record }">
        <a-tag color="green">{{ record.osFamily }}</a-tag>
      </template>

      <template #version="{ record }">
        <a-tag color="blue">{{ record.version }}</a-tag>
      </template>

      <template #downloadUrl="{ record }">
        <a v-if="record.downloadUrl" :href="record.downloadUrl" target="_blank" class="download-link">
          <icon-link /> 下载链接
        </a>
        <span v-else class="text-muted">-</span>
      </template>

      <template #operations="{ record }">
        <a-space>
          <a-button type="text" size="small" @click="handleEdit(record)">
            <template #icon>
              <icon-edit />
            </template>
            编辑
          </a-button>
          <a-popconfirm content="确定要删除此配置吗？" @ok="handleDelete(record.id)">
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
      <a-form :model="formData" :label-col-props="{ span: 7 }" :wrapper-col-props="{ span: 17 }">
        <a-form-item label="操作系统家族" field="osFamily" required>
          <a-input v-model="formData.osFamily" placeholder="如: Ubuntu, RHEL, CentOS" />
        </a-form-item>
        <a-form-item label="版本号" field="version" required>
          <a-input v-model="formData.version" placeholder="如: 22.04, 8.5" />
        </a-form-item>
        <a-form-item label="下载链接" field="downloadUrl">
          <a-input v-model="formData.downloadUrl" placeholder="请输入镜像下载链接" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { Message } from '@arco-design/web-vue'
import * as tpdbApi from '@/apis/tpdb'
import type { OsConfig, OsConfigForm, OsConfigQuery } from '@/apis/tpdb'

defineOptions({ name: 'OsConfigManager' })

const loading = ref(false)
const dataList = ref<OsConfig[]>([])

const queryForm = reactive<OsConfigQuery>({
  osFamily: '',
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
  { title: '操作系统家族', dataIndex: 'osFamily', slotName: 'osFamily', width: 150 },
  { title: '版本', dataIndex: 'version', slotName: 'version', width: 120 },
  { title: '下载链接', slotName: 'downloadUrl', width: 200 },
  { title: '创建时间', dataIndex: 'createdAt', width: 160 },
  { title: '更新时间', dataIndex: 'updatedAt', width: 160 },
  { title: '操作', slotName: 'operations', width: 160, align: 'center' as const },
]

const modalVisible = ref(false)
const modalMode = ref<'add' | 'edit'>('add')
const modalTitle = computed(() => (modalMode.value === 'add' ? '新增OS配置' : '编辑OS配置'))
const currentEditId = ref<number>()

const formData = reactive<OsConfigForm>({
  osFamily: '',
  version: '',
  downloadUrl: '',
})

const loadData = async () => {
  loading.value = true
  try {
    const res = await tpdbApi.listOsConfigs(queryForm)
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
  queryForm.osFamily = ''
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
  Object.assign(formData, {
    osFamily: '',
    version: '',
    downloadUrl: '',
  })
}

const handleEdit = (record: OsConfig) => {
  modalMode.value = 'edit'
  modalVisible.value = true
  currentEditId.value = record.id
  Object.assign(formData, {
    osFamily: record.osFamily,
    version: record.version,
    downloadUrl: record.downloadUrl || '',
  })
}

const handleDelete = async (id: number) => {
  try {
    await tpdbApi.deleteOsConfig(id)
    Message.success('删除成功')
    loadData()
  } catch (error) {
    Message.error('删除失败')
  }
}

const handleModalOk = async () => {
  if (!formData.osFamily || !formData.version) {
    Message.warning('请填写必填项')
    return
  }

  try {
    if (modalMode.value === 'add') {
      await tpdbApi.createOsConfig(formData)
      Message.success('新增成功')
    } else {
      await tpdbApi.updateOsConfig(currentEditId.value!, formData)
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
  display: flex;
  justify-content: space-between;
  align-items: center;
  padding: 16px;
  background: var(--color-bg-2);
  border-radius: 4px;
}

.download-link {
  color: var(--color-primary-light-4);
  display: flex;
  align-items: center;
  gap: 4px;

  &:hover {
    color: var(--color-primary-light-3);
  }
}

.text-muted {
  color: var(--color-text-4);
}
</style>
