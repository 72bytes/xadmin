<template>
  <a-modal
    v-model:visible="visibleModel"
    :title="title"
    :ok-text="okText"
    :cancel-text="cancelText"
    @ok="handleOk"
    @cancel="handleCancel"
  >
    <div class="dialog-content">
      <a-input
        v-if="dialogType !== 'delete' && dialogType !== 'upload' && dialogType !== 'deleteCase' && dialogType !== 'uploadCase'"
        v-model="inputValue"
        :placeholder="placeholder"
        allow-clear
        @press-enter="handleOk"
      />

      <a-textarea
        v-if="dialogType === 'delete' || dialogType === 'deleteCase'"
        :model-value="message"
        :auto-size="{ minRows: 3, maxRows: 5 }"
        readonly
      />

      <div v-if="dialogType === 'upload'" class="upload-section">
        <a-upload
          :custom-request="handleUpload"
          :show-file-list="true"
          :file-list="uploadFileList"
          multiple
          @change="handleUploadChange"
        >
          <template #upload-button>
            <a-button type="primary">
              <icon-upload />
              选择文件
            </a-button>
          </template>
        </a-upload>
      </div>

      <div v-if="dialogType === 'uploadCase'" class="upload-case-section">
        <a-form :model="{ caseName: inputValue }">
          <a-form-item label="Case 名称" required>
            <a-input
              v-model="inputValue"
              placeholder="请输入 Case 名称"
              allow-clear
            />
          </a-form-item>
          <a-form-item label="压缩包文件" required>
            <a-upload
              :custom-request="handleUpload"
              :show-file-list="true"
              :file-list="uploadFileList"
              :limit="1"
              accept=".tar.gz,.tgz,.zip"
              @change="handleUploadChange"
            >
              <template #upload-button>
                <a-button>
                  <icon-upload />
                  选择压缩包 (.tar.gz, .tgz, .zip)
                </a-button>
              </template>
            </a-upload>
          </a-form-item>
        </a-form>
      </div>
    </div>
  </a-modal>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Message } from '@arco-design/web-vue'
import type { DialogType } from '@/apis/system/caseeditor-type'
import type { FileItem } from '@arco-design/web-vue'

interface Props {
  visible: boolean
  dialogType: DialogType
  title: string
  message?: string
  defaultValue?: string
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'confirm', value?: string | File[] | { caseName: string; file: File }): void
  (e: 'cancel'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const visibleModel = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value),
})

const inputValue = ref('')
const uploadFileList = ref<FileItem[]>([])

watch(
  () => props.visible,
  (newVisible) => {
    if (newVisible) {
      inputValue.value = props.defaultValue || ''
      uploadFileList.value = []
    }
  }
)

const okText = computed(() => {
  switch (props.dialogType) {
    case 'delete':
    case 'deleteCase':
      return '删除'
    case 'upload':
    case 'uploadCase':
      return '上传'
    default:
      return '确定'
  }
})

const cancelText = computed(() => '取消')

const placeholder = computed(() => {
  switch (props.dialogType) {
    case 'createFile':
      return '请输入文件名'
    case 'createFolder':
      return '请输入文件夹名'
    case 'rename':
      return '请输入新名称'
    case 'uploadCase':
      return '请输入 Case 名称'
    default:
      return ''
  }
})

const handleOk = () => {
  if (props.dialogType === 'upload') {
    const files = uploadFileList.value.map(item => item.file).filter(Boolean) as File[]
    if (files.length === 0) {
      Message.warning('请选择要上传的文件')
      return
    }
    emit('confirm', files)
  }
  else if (props.dialogType === 'uploadCase') {
    // 验证 case 名称和文件
    if (!inputValue.value.trim()) {
      Message.warning('请输入 Case 名称')
      return
    }
    if (uploadFileList.value.length === 0 || !uploadFileList.value[0].file) {
      Message.warning('请选择要上传的压缩包文件')
      return
    }
    emit('confirm', {
      caseName: inputValue.value.trim(),
      file: uploadFileList.value[0].file as File
    })
  }
  else if (props.dialogType !== 'delete' && props.dialogType !== 'deleteCase') {
    if (!inputValue.value.trim()) {
      Message.warning('请输入内容')
      return
    }
    emit('confirm', inputValue.value.trim())
  }
  else {
    emit('confirm')
  }
  visibleModel.value = false
}

const handleCancel = () => {
  emit('cancel')
  visibleModel.value = false
}

const handleUpload = (option: any) => {
  // 自定义上传逻辑，阻止默认行为
  return {
    abort() {
      // 取消上传
    },
  }
}

const handleUploadChange = (fileList: FileItem[], fileItem: FileItem) => {
  uploadFileList.value = fileList
}
</script>

<style scoped lang="less">
.dialog-content {
  padding: 8px 0;

  .upload-section {
    :deep(.arco-upload) {
      width: 100%;
    }
  }

  .upload-case-section {
    :deep(.arco-form) {
      margin-top: 8px;
    }

    :deep(.arco-upload) {
      width: 100%;
    }
  }
}
</style>

