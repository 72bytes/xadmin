<template>
  <div
    ref="notificationEl"
    class="notification"
    style="display: none; white-space: pre-line;"
  >
    {{ displayMessage }}
  </div>
</template>

<script setup>
/**
 * Notification 组件
 * 右上角通知消息（成功、错误、警告等）
 * 完全模仿 fronted/tp_gen.js 的实现逻辑
 */

import { ref } from 'vue'

// DOM 引用
const notificationEl = ref(null)
const displayMessage = ref('')
let hideTimer = null

/**
 * 显示通知
 * 完全模仿 fronted 的 showNotification 函数
 */
function show(message, type = 'success', duration = 3000) {
  console.log('[Notification] show called:', { message, type, duration })

  if (!notificationEl.value) {
    console.error('[Notification] notificationEl is null!')
    return
  }

  // 检查 message 是否有效
  if (!message || typeof message !== 'string') {
    console.error('[Notification] Invalid message:', message)
    return
  }

  // 清除之前的定时器
  if (hideTimer) {
    clearTimeout(hideTimer)
  }

  // 设置消息内容
  displayMessage.value = message
  console.log('[Notification] displayMessage set to:', displayMessage.value)
  console.log('[Notification] message length:', message.length)

  // 设置 className（重置为基础类）
  notificationEl.value.className = 'notification'

  // 添加类型类
  if (type === 'error') {
    notificationEl.value.classList.add('error')
  } else if (type === 'warning') {
    notificationEl.value.classList.add('warning')
  } else if (type === 'info') {
    notificationEl.value.classList.add('info')
  }

  // 显示通知
  notificationEl.value.style.display = 'block'

  console.log('[Notification] 通知已显示')
  console.log('[Notification] Element text content:', notificationEl.value.textContent)
  console.log('[Notification] Element style:', {
    display: notificationEl.value.style.display,
    color: window.getComputedStyle(notificationEl.value).color,
    fontSize: window.getComputedStyle(notificationEl.value).fontSize,
  })

  // 自动隐藏
  hideTimer = setTimeout(() => {
    hide()
  }, duration)
}

/**
 * 隐藏通知
 */
function hide() {
  if (notificationEl.value) {
    notificationEl.value.style.display = 'none'
  }
  if (hideTimer) {
    clearTimeout(hideTimer)
    hideTimer = null
  }
}

// 暴露方法供父组件调用
defineExpose({
  show,
  hide,
})
</script>

  <style scoped>
  .notification {
    position: fixed;
    top: 30px;
    right: 30px;
    padding: 18px 24px;
    background: linear-gradient(135deg, #4caf50, #8bc34a);
    color: white;
    border-radius: 10px;
    box-shadow: 0 10px 25px rgba(0, 0, 0, 0.15);
    z-index: 10000;
    min-width: 280px;
    max-width: 400px;
    font-size: 15px;
    font-weight: 500;
    line-height: 1.6;
  }

  .notification-content {
    display: flex;
    align-items: flex-start;
    gap: 12px;
  }

  .notification-content i {
    font-size: 20px;
    flex-shrink: 0;
    margin-top: 2px;
  }

  .notification-message {
    flex: 1;
    word-break: break-word;
  }

  /* 成功通知 - 绿色渐变 */
  .notification.success {
    background: linear-gradient(135deg, #4caf50, #8bc34a);
  }

  /* 错误通知 - 红色渐变 */
  .notification.error {
    background: linear-gradient(135deg, #e74c3c, #c0392b);
  }

  /* 警告通知 - 橙色渐变 */
  .notification.warning {
    background: linear-gradient(135deg, #ff9800, #f57c00);
  }

  /* 信息通知 - 蓝色渐变 */
  .notification.info {
    background: linear-gradient(135deg, #2196f3, #1976d2);
  }

  /* 滑入滑出动画 */
  .slide-fade-enter-active {
    transition: all 0.4s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  }

  .slide-fade-leave-active {
    transition: all 0.3s ease-out;
  }

  .slide-fade-enter-from {
    transform: translateX(100%);
    opacity: 0;
  }

  .slide-fade-leave-to {
    transform: translateY(-20px);
    opacity: 0;
  }
  </style>
