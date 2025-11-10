<template>
  <div class="gi_page">
    <a-row wrap :gutter="16" align="stretch">
      <a-col :xs="24" :sm="24" :md="10" :lg="10" :xl="7" :xxl="7">
        <LeftBox />
      </a-col>
      <a-col :xs="24" :sm="24" :md="14" :lg="14" :xl="17" :xxl="17">
        <div>
          <PasswordPolicy />
        </div>
        <!-- 第三方账号功能已删除 -->
        <!-- <div style="margin-top: 16px">
          <RightBox />
        </div> -->
      </a-col>
    </a-row>
  </div>
</template>

<script setup lang="ts">
import LeftBox from './BasicInfo.vue'
// import RightBox from './Social.vue' // 第三方账号功能已删除
import PasswordPolicy from './Security.vue'

defineOptions({ name: 'SettingProfile' })
</script>

<style scoped lang="scss">
.gi_page {
  background-color: var(--color-bg-1);
}
</style>
