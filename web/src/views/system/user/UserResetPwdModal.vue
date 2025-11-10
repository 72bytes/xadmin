<template>
  <a-modal
    v-model:visible="visible"
    title="重置密码"
    :mask-closable="false"
    :esc-to-close="false"
    :modal-style="{ maxWidth: '520px' }"
    width="90%"
    draggable
    @before-ok="save"
    @close="reset"
  >
    <GiForm ref="formRef" v-model="form" :options="options" :columns="columns" />
  </a-modal>
</template>

<script setup lang="ts">
import { Message } from '@arco-design/web-vue'
import { resetUserPwd } from '@/apis/system'
import { type Columns, GiForm } from '@/components/GiForm'
import { useResetReactive } from '@/hooks'
import { encryptByRsa } from '@/utils/encrypt'

const emit = defineEmits<{
  (e: 'save-success'): void
}>()

const dataId = ref('')
const visible = ref(false)
const formRef = ref<InstanceType<typeof GiForm>>()

const options: Options = {
  form: { size: 'large' },
  btns: { hide: true },
}

const [form, resetForm] = useResetReactive({})

const columns: Columns = reactive([
  { label: '密码', field: 'newPassword', type: 'input-password', rules: [{ required: true, message: '请输入密码' }] },
])

// 重置
const reset = () => {
  formRef.value?.formRef?.resetFields()
  resetForm()
}

// 保存
const save = async () => {
  try {
    const isInvalid = await formRef.value?.formRef?.validate()
    if (isInvalid) return false
    await resetUserPwd({ newPassword: encryptByRsa(form.newPassword) || '' }, dataId.value)
    Message.success('重置成功')
    emit('save-success')
    return true
  } catch (error) {
    return false
  }
}

// 打开
const onOpen = (id: string) => {
  reset()
  dataId.value = id
  visible.value = true
}

defineExpose({ onOpen })
</script>

<style scoped lang="scss"></style>
