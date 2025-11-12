<template>
  <div class="manager-container">
    <!-- 搜索和操作栏 -->
    <div class="toolbar">
      <a-space>
        <a-input
          v-model="queryForm.hostname"
          placeholder="搜索主机名"
          style="width: 200px"
          allow-clear
          @press-enter="handleSearch"
        >
          <template #prefix>
            <icon-search />
          </template>
        </a-input>
        <a-input
          v-model="queryForm.gpuModel"
          placeholder="搜索GPU型号"
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
      <a-space>
        <a-button type="primary" @click="handleAdd">
          <template #icon>
            <icon-plus />
          </template>
          新增设备
        </a-button>
        <a-button
          type="primary"
          status="danger"
          :disabled="selectedKeys.length === 0"
          @click="handleBatchDelete"
        >
          <template #icon>
            <icon-delete />
          </template>
          批量删除
        </a-button>
      </a-space>
    </div>

    <!-- 数据表格 -->
    <a-table
      v-model:selected-keys="selectedKeys"
      :columns="columns"
      :data="dataList"
      :loading="loading"
      :pagination="pagination"
      :row-selection="{ type: 'checkbox', showCheckedAll: true }"
      row-key="id"
      @page-change="handlePageChange"
      @page-size-change="handlePageSizeChange"
    >
      <template #hostname="{ record }">
        <a-tag color="arcoblue">{{ record.hostname }}</a-tag>
      </template>

      <template #gpuInfo="{ record }">
        <div class="gpu-info">
          <div v-if="record.gpuModel" class="gpu-model">{{ record.gpuModel }}</div>
          <div v-if="record.gpuSeries" class="gpu-series">{{ record.gpuSeries }}</div>
        </div>
      </template>

      <template #asicInfo="{ record }">
        <div class="asic-info">
          <div v-if="record.asicName" class="asic-name">{{ record.asicName }}</div>
          <div v-if="record.deviceId || record.revId" class="device-ids">
            <span v-if="record.deviceId">ID: {{ record.deviceId }}</span>
            <span v-if="record.revId">Rev: {{ record.revId }}</span>
          </div>
        </div>
      </template>

      <template #operations="{ record }">
        <a-space>
          <a-button type="text" size="small" @click="handleEdit(record)">
            <template #icon>
              <icon-edit />
            </template>
            编辑
          </a-button>
          <a-popconfirm content="确定要删除此设备吗？" @ok="handleDelete(record.id)">
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
        <a-form-item label="主机名" field="hostname" required>
          <a-input v-model="formData.hostname" placeholder="请输入主机名" />
        </a-form-item>
        <a-form-item label="IP地址" field="ipAddress">
          <a-input v-model="formData.ipAddress" placeholder="请输入IP地址" />
        </a-form-item>
        <a-form-item label="ASIC名称" field="asicName">
          <a-input v-model="formData.asicName" placeholder="请输入ASIC名称" />
        </a-form-item>
        <a-form-item label="设备ID" field="deviceId">
          <a-input v-model="formData.deviceId" placeholder="请输入设备ID" />
        </a-form-item>
        <a-form-item label="版本ID" field="revId">
          <a-input v-model="formData.revId" placeholder="请输入版本ID" />
        </a-form-item>
        <a-form-item label="GPU系列" field="gpuSeries">
          <a-input v-model="formData.gpuSeries" placeholder="请输入GPU系列" />
        </a-form-item>
        <a-form-item label="GPU型号" field="gpuModel">
          <a-input v-model="formData.gpuModel" placeholder="请输入GPU型号" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { Message } from '@arco-design/web-vue'
import * as tpdbApi from '@/apis/tpdb'
import type { SutDevice, SutDeviceForm, SutDeviceQuery } from '@/apis/tpdb'

defineOptions({ name: 'SutDeviceManager' })

// 数据状态
const loading = ref(false)
const dataList = ref<SutDevice[]>([])
const selectedKeys = ref<number[]>([])

// 查询表单
const queryForm = reactive<SutDeviceQuery>({
  hostname: '',
  gpuModel: '',
  page: 1,
  size: 10,
})

// 分页配置
const pagination = computed(() => ({
  current: queryForm.page || 1,
  pageSize: queryForm.size || 10,
  total: dataList.value.length,
  showTotal: true,
  showPageSize: true,
}))

// 表格列配置
const columns = [
  { title: '主机名', dataIndex: 'hostname', slotName: 'hostname', width: 150 },
  { title: 'IP地址', dataIndex: 'ipAddress', width: 140 },
  { title: 'GPU信息', slotName: 'gpuInfo', width: 180 },
  { title: 'ASIC信息', slotName: 'asicInfo', width: 200 },
  { title: '创建时间', dataIndex: 'createdAt', width: 160 },
  { title: '操作', slotName: 'operations', width: 160, align: 'center' as const },
]

// 弹窗状态
const modalVisible = ref(false)
const modalMode = ref<'add' | 'edit'>('add')
const modalTitle = computed(() => (modalMode.value === 'add' ? '新增设备' : '编辑设备'))
const currentEditId = ref<number>()

// 表单数据
const formData = reactive<SutDeviceForm>({
  hostname: '',
  ipAddress: '',
  asicName: '',
  deviceId: '',
  revId: '',
  gpuSeries: '',
  gpuModel: '',
})

// 加载数据
const loadData = async () => {
  loading.value = true
  try {
    const res = await tpdbApi.listSutDevices(queryForm)
    if (res.success) {
      dataList.value = res.data?.list || []
    }
  } catch (error) {
    Message.error('加载数据失败')
  } finally {
    loading.value = false
  }
}

// 搜索
const handleSearch = () => {
  queryForm.page = 1
  loadData()
}

// 重置
const handleReset = () => {
  queryForm.hostname = ''
  queryForm.gpuModel = ''
  queryForm.page = 1
  loadData()
}

// 分页变化
const handlePageChange = (page: number) => {
  queryForm.page = page
  loadData()
}

const handlePageSizeChange = (size: number) => {
  queryForm.size = size
  queryForm.page = 1
  loadData()
}

// 新增
const handleAdd = () => {
  modalMode.value = 'add'
  modalVisible.value = true
  Object.assign(formData, {
    hostname: '',
    ipAddress: '',
    asicName: '',
    deviceId: '',
    revId: '',
    gpuSeries: '',
    gpuModel: '',
  })
}

// 编辑
const handleEdit = (record: SutDevice) => {
  modalMode.value = 'edit'
  modalVisible.value = true
  currentEditId.value = record.id
  Object.assign(formData, {
    hostname: record.hostname,
    ipAddress: record.ipAddress || '',
    asicName: record.asicName || '',
    deviceId: record.deviceId || '',
    revId: record.revId || '',
    gpuSeries: record.gpuSeries || '',
    gpuModel: record.gpuModel || '',
  })
}

// 删除单个
const handleDelete = async (id: number) => {
  try {
    await tpdbApi.deleteSutDevice(id)
    Message.success('删除成功')
    loadData()
  } catch (error) {
    Message.error('删除失败')
  }
}

// 批量删除
const handleBatchDelete = () => {
  if (selectedKeys.value.length === 0) {
    Message.warning('请选择要删除的设备')
    return
  }

  tpdbApi.deleteSutDevice(selectedKeys.value)
    .then(() => {
      Message.success('批量删除成功')
      selectedKeys.value = []
      loadData()
    })
    .catch(() => {
      Message.error('批量删除失败')
    })
}

// 弹窗确认
const handleModalOk = async () => {
  if (!formData.hostname) {
    Message.warning('请输入主机名')
    return
  }

  try {
    if (modalMode.value === 'add') {
      await tpdbApi.createSutDevice(formData)
      Message.success('新增成功')
    } else {
      await tpdbApi.updateSutDevice(currentEditId.value!, formData)
      Message.success('更新成功')
    }
    modalVisible.value = false
    loadData()
  } catch (error) {
    Message.error(modalMode.value === 'add' ? '新增失败' : '更新失败')
  }
}

// 弹窗取消
const handleModalCancel = () => {
  modalVisible.value = false
}

// 初始化
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

.gpu-info,
.asic-info {
  .gpu-model,
  .asic-name {
    font-weight: 500;
    margin-bottom: 4px;
  }

  .gpu-series,
  .device-ids {
    font-size: 12px;
    color: var(--color-text-3);

    span + span {
      margin-left: 8px;
    }
  }
}
</style>
