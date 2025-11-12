<template>
  <a-form
    ref="formRef"
    :model="form"
    :rules="rules"
    :label-col-style="{ display: 'none' }"
    :wrapper-col-style="{ flex: 1 }"
    size="large"
    @submit="handleLogin"
  >
    <a-form-item field="username" hide-label>
      <a-input v-model="form.username" placeholder="请输入用户名" allow-clear />
    </a-form-item>
    <a-form-item field="password" hide-label>
      <a-input-password v-model="form.password" placeholder="请输入密码" />
    </a-form-item>
    <!-- 验证码功能已注释 -->
    <!-- <a-form-item field="captcha" hide-label>
      <a-input v-model="form.captcha" placeholder="请输入验证码" :max-length="4" allow-clear style="flex: 1 1" />
      <div class="captcha-container" @click="getCaptcha">
        <img :src="captchaImgBase64" alt="验证码" class="captcha" />
        <div v-if="form.expired" class="overlay">
          <p>已过期，请刷新</p>
        </div>
      </div>
    </a-form-item> -->
    <a-form-item>
      <a-space direction="vertical" fill class="w-full">
        <a-button class="btn" type="primary" :loading="loading" html-type="submit" size="large" long>立即登录</a-button>
      </a-space>
    </a-form-item>
  </a-form>
</template>

<script setup lang="ts">
import { type FormInstance, Message } from '@arco-design/web-vue'
// import { getImageCaptcha } from '@/apis/common' // 验证码功能已注释
import { useTabsStore, useUserStore } from '@/stores'
import { encodeByBase64, encryptByRsa } from '@/utils/encrypt'

// 验证码图片 - 已注释
// const captchaImgBase64 = ref()

const formRef = ref<FormInstance>()
const form = reactive({
  username: 'admin', // 演示默认值
  password: 'admin123', // 演示默认值
  // captcha: '', // 验证码功能已注释
  // uuid: '', // 验证码功能已注释
  // expired: false, // 验证码功能已注释
})
const rules: FormInstance['rules'] = {
  username: [{ required: true, message: '请输入用户名' }],
  password: [{ required: true, message: '请输入密码' }],
  // captcha: [{ required: true, message: '请输入验证码' }], // 验证码功能已注释
}

// 验证码过期定时器 - 已注释
// let timer: ReturnType<typeof setTimeout>
// const startTimer = (expireTime: number) => {
//   if (timer) {
//     clearTimeout(timer)
//   }
//   const remainingTime = expireTime - Date.now()
//   if (remainingTime <= 0) {
//     form.expired = true
//     return
//   }
//   timer = setTimeout(() => {
//     form.expired = true
//   }, remainingTime)
// }

// 组件销毁时清理定时器 - 已注释
// onBeforeUnmount(() => {
//   if (timer) {
//     clearTimeout(timer)
//   }
// })

// 获取验证码 - 已注释
// const getCaptcha = () => {
//   getImageCaptcha().then((res) => {
//     const { uuid, img, expireTime } = res.data
//     captchaImgBase64.value = img
//     form.uuid = uuid
//     form.expired = false
//     startTimer(expireTime)
//   })
// }

const userStore = useUserStore()
const tabsStore = useTabsStore()
const router = useRouter()
const loading = ref(false)
// 登录
const handleLogin = async () => {
  try {
    const isInvalid = await formRef.value?.validate()
    if (isInvalid) return
    loading.value = true
    await userStore.accountLogin({
      username: form.username,
      password: encodeByBase64(form.password) || '',
      // captcha: form.captcha, // 验证码功能已注释
      // uuid: form.uuid, // 验证码功能已注释
    })
    tabsStore.reset()
    const { redirect, ...othersQuery } = router.currentRoute.value.query
    await router.push({
      path: (redirect as string) || '/',
      query: {
        ...othersQuery,
      },
    })
    Message.success('欢迎使用')
  } catch (error) {
    // getCaptcha() // 验证码功能已注释
    // form.captcha = '' // 验证码功能已注释
  } finally {
    loading.value = false
  }
}

// 验证码初始化 - 已注释
// onMounted(() => {
//   getCaptcha()
// })
</script>

<style scoped lang="scss">
.arco-input-wrapper,
:deep(.arco-select-view-single) {
  height: 40px;
  border-radius: 4px;
  font-size: 13px;
}

.arco-input-wrapper.arco-input-error {
  background-color: rgb(var(--danger-1));
  border-color: rgb(var(--danger-3));
}

.arco-input-wrapper.arco-input-error:hover {
  background-color: rgb(var(--danger-1));
  border-color: rgb(var(--danger-6));
}

.arco-input-wrapper :deep(.arco-input) {
  font-size: 13px;
  color: var(--color-text-1);
}

.arco-input-wrapper:hover {
  border-color: rgb(var(--arcoblue-6));
}

/* 验证码样式 - 已注释 */
/* .captcha {
  width: 111px;
  height: 36px;
  margin: 0 0 0 5px;
} */

.btn {
  height: 40px;
}

/* .captcha-container {
  position: relative;
  display: inline-block;
  cursor: pointer;
}

.overlay {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background-color: rgba(51, 51, 51, 0.8);
  display: flex;
  justify-content: center;
  align-items: center;
}

.overlay p {
  font-size: 12px;
  color: white;
} */
</style>
