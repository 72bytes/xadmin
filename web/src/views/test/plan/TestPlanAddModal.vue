<template>
  <a-modal
    v-model:visible="visible"
    title="新增测试计划"
    :mask-closable="false"
    :esc-to-close="true"
    draggable
    :width="width >= 600 ? 600 : '100%'"
    @close="reset"
  >
    <a-steps :current="current" class="mb-15" @change="onChangeCurrent">
      <a-step>基本信息</a-step>
      <a-step>时间规划</a-step>
      <a-step>人员配置</a-step>
      <a-step>测试范围</a-step>
      <a-step>确认提交</a-step>
    </a-steps>
    <a-form ref="formRef" :model="form" :rules="rules" size="large" auto-label-width>
      <!-- 步骤1: 基本信息 -->
      <fieldset v-show="current === 1">
        <a-form-item label="名称" field="name">
          <a-input v-model.trim="form.name" placeholder="请输入测试计划名称" />
        </a-form-item>
        <a-form-item label="编号" field="code">
          <a-input v-model.trim="form.code" placeholder="请输入测试计划编号" />
        </a-form-item>
        <a-form-item label="描述" field="description">
          <a-textarea
            v-model.trim="form.description"
            placeholder="请输入描述"
            show-word-limit
            :max-length="500"
            :auto-size="{ minRows: 3, maxRows: 5 }"
          />
        </a-form-item>
      </fieldset>

      <!-- 步骤2: 时间规划 -->
      <fieldset v-show="current === 2">
        <a-form-item label="开始时间" field="startTime">
          <a-date-picker
            v-model="form.startTime"
            show-time
            format="YYYY-MM-DD HH:mm:ss"
            placeholder="请选择开始时间"
            style="width: 100%"
          />
        </a-form-item>
        <a-form-item label="结束时间" field="endTime">
          <a-date-picker
            v-model="form.endTime"
            show-time
            format="YYYY-MM-DD HH:mm:ss"
            placeholder="请选择结束时间"
            style="width: 100%"
          />
        </a-form-item>
        <a-form-item label="优先级" field="priority">
          <a-select v-model="form.priority" placeholder="请选择优先级">
            <a-option :value="1">高</a-option>
            <a-option :value="2">中</a-option>
            <a-option :value="3">低</a-option>
          </a-select>
        </a-form-item>
      </fieldset>

      <!-- 步骤3: 人员配置 -->
      <fieldset v-show="current === 3">
        <a-form-item label="负责人" field="ownerName">
          <a-input v-model.trim="form.ownerName" placeholder="请输入负责人姓名" />
        </a-form-item>
        <a-form-item label="状态" field="status">
          <a-select v-model="form.status" placeholder="请选择状态">
            <a-option :value="1">未开始</a-option>
            <a-option :value="2">进行中</a-option>
            <a-option :value="3">已完成</a-option>
            <a-option :value="4">已取消</a-option>
          </a-select>
        </a-form-item>
      </fieldset>

      <!-- 步骤4: 测试范围 -->
      <fieldset v-show="current === 4">
        <a-form-item label="测试类型" field="testType">
          <a-select v-model="form.testType" placeholder="请选择测试类型" allow-clear>
            <a-option value="功能测试">功能测试</a-option>
            <a-option value="性能测试">性能测试</a-option>
            <a-option value="安全测试">安全测试</a-option>
            <a-option value="兼容性测试">兼容性测试</a-option>
            <a-option value="接口测试">接口测试</a-option>
            <a-option value="自动化测试">自动化测试</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="测试环境" field="testEnv">
          <a-select v-model="form.testEnv" placeholder="请选择测试环境" allow-clear>
            <a-option value="开发环境">开发环境</a-option>
            <a-option value="测试环境">测试环境</a-option>
            <a-option value="预生产环境">预生产环境</a-option>
            <a-option value="生产环境">生产环境</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="关联项目" field="relatedProject">
          <a-input v-model.trim="form.relatedProject" placeholder="请输入关联项目" />
        </a-form-item>
        <a-form-item label="备注" field="remark">
          <a-textarea
            v-model.trim="form.remark"
            placeholder="请输入备注"
            show-word-limit
            :max-length="500"
            :auto-size="{ minRows: 3, maxRows: 5 }"
          />
        </a-form-item>
      </fieldset>

      <!-- 步骤5: 确认提交 -->
      <fieldset v-show="current === 5" class="confirm-step">
        <a-descriptions :column="1" bordered size="large">
          <a-descriptions-item label="名称">{{ form.name }}</a-descriptions-item>
          <a-descriptions-item label="编号">{{ form.code }}</a-descriptions-item>
          <a-descriptions-item label="描述">{{ form.description || '-' }}</a-descriptions-item>
          <a-descriptions-item label="开始时间">{{ form.startTime || '-' }}</a-descriptions-item>
          <a-descriptions-item label="结束时间">{{ form.endTime || '-' }}</a-descriptions-item>
          <a-descriptions-item label="优先级">
            <a-tag v-if="form.priority === 1" color="red">高</a-tag>
            <a-tag v-else-if="form.priority === 2" color="orange">中</a-tag>
            <a-tag v-else color="blue">低</a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="负责人">{{ form.ownerName || '-' }}</a-descriptions-item>
          <a-descriptions-item label="状态">
            <a-tag v-if="form.status === 1" color="gray">未开始</a-tag>
            <a-tag v-else-if="form.status === 2" color="blue">进行中</a-tag>
            <a-tag v-else-if="form.status === 3" color="green">已完成</a-tag>
            <a-tag v-else color="red">已取消</a-tag>
          </a-descriptions-item>
          <a-descriptions-item label="测试类型">{{ form.testType || '-' }}</a-descriptions-item>
          <a-descriptions-item label="测试环境">{{ form.testEnv || '-' }}</a-descriptions-item>
          <a-descriptions-item label="关联项目">{{ form.relatedProject || '-' }}</a-descriptions-item>
          <a-descriptions-item label="备注">{{ form.remark || '-' }}</a-descriptions-item>
        </a-descriptions>
      </fieldset>
    </a-form>
    <template #footer>
      <a-space size="large">
        <a-button :disabled="current === 1" type="secondary" @click="onPrev">
          <IconLeft />
          上一步
        </a-button>
        <a-button v-if="current !== 5" :disabled="current === 5" type="primary" @click="onNext">
          下一步
          <IconRight />
        </a-button>
        <a-button v-if="current === 5" type="primary" :loading="saveLoading" @click="onClickOk">确定</a-button>
      </a-space>
    </template>
  </a-modal>
</template>

<script setup lang="ts">
import { type FormInstance, Message } from '@arco-design/web-vue'
import { useWindowSize } from '@vueuse/core'
import { addTestPlan } from '@/apis/test/plan'
import { useResetReactive } from '@/hooks'

const emit = defineEmits<{
  (e: 'save-success'): void
}>()

const { width } = useWindowSize()

const visible = ref(false)
const formRef = ref<FormInstance>()
const saveLoading = ref(false)

const rules: FormInstance['rules'] = {
  name: [{ required: true, message: '请输入测试计划名称' }],
  code: [{ required: true, message: '请输入测试计划编号' }],
  priority: [{ required: true, message: '请选择优先级' }],
  status: [{ required: true, message: '请选择状态' }],
}

const [form, resetForm] = useResetReactive({
  name: '',
  code: '',
  description: '',
  startTime: '',
  endTime: '',
  ownerId: undefined,
  ownerName: '',
  priority: 2,
  status: 1,
  testType: '',
  testEnv: '',
  relatedProject: '',
  remark: '',
})

const current = ref<number>(1)

// 重置
const reset = () => {
  current.value = 1
  formRef.value?.resetFields()
  resetForm()
}

// 上一步
const onPrev = () => {
  current.value = Math.max(1, current.value - 1)
}

// 下一步
const onNext = async () => {
  try {
    // 根据当前步骤验证对应字段
    if (current.value === 1) {
      const isInvalid = await formRef.value?.validateField(['name', 'code'])
      if (isInvalid) return
    } else if (current.value === 2) {
      const isInvalid = await formRef.value?.validateField(['priority'])
      if (isInvalid) return
    } else if (current.value === 3) {
      const isInvalid = await formRef.value?.validateField(['status'])
      if (isInvalid) return
    }
    current.value = Math.min(5, current.value + 1)
  } catch (error) {
    console.error(error)
  }
}

// 当前页
const onChangeCurrent = (page: number) => {
  current.value = page
}

// 保存
const save = async () => {
  try {
    const isInvalid = await formRef.value?.validate()
    if (isInvalid) return false
    
    saveLoading.value = true
    await addTestPlan(form)
    Message.success('新增成功')
    emit('save-success')
    return true
  } catch (error) {
    return false
  } finally {
    saveLoading.value = false
  }
}

// 确认
const onClickOk = async () => {
  if (unref(current) === 5) {
    const success = await save()
    if (success) {
      visible.value = false
    }
  }
}

// 打开
const onOpen = async () => {
  reset()
  visible.value = true
}

defineExpose({ onOpen })
</script>

<style scoped lang="scss">
fieldset {
  padding: 15px 15px 0 15px;
  margin-bottom: 10px;
  border: 1px solid var(--color-neutral-3);
  border-radius: 3px;
  min-height: 380px;
  max-height: 440px;
  overflow-y: auto;
}

.confirm-step {
  padding: 15px;
}

fieldset legend {
  color: rgb(var(--gray-10));
  padding: 2px 5px 2px 5px;
  border: 1px solid var(--color-neutral-3);
  border-radius: 3px;
}

.mb-15 {
  margin-bottom: 15px;
}

:deep(.arco-modal-footer) {
  margin-top: -20px;
}
</style>

