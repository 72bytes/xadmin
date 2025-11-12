<template>
  <a-card class="card" :bordered="false">
    <div class="content">
      <a-space size="medium">
        <Avatar :src="userStore.avatar" :name="userStore.nickname" :size="68" />
        <div class="welcome">
          <p class="hello">{{ goodTimeText() }}！{{ userStore.nickname }}</p>
          <p>北海虽赊，扶摇可接；东隅已逝，桑榆非晚。</p>
        </div>
      </a-space>
    </div>
  </a-card>
</template>

<script setup lang="ts">
import { useUserStore } from '@/stores'
import { goodTimeText } from '@/utils'

const userStore = useUserStore()
</script>

<style scoped lang="scss">
:deep(.arco-statistic-title) {
  margin-bottom: 0;
}

.card {
  width: 100%;

  :deep(.arco-card-body) {
    width: 100%;
    padding: 0;
  }

  .content {
    width: 100%;
    padding: 8px 20px;
    display: flex;
    align-items: center;
    box-sizing: border-box;

    .welcome {
      margin: 8px 0;
      color: $color-text-3;
      .hello {
        font-size: 1.25rem;
        color: $color-text-1;
        margin-bottom: 10px;
      }
    }
  }
}
</style>
