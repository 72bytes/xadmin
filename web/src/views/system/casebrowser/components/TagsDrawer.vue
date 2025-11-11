<template>
  <a-drawer
    v-model:visible="visibleModel"
    :title="`管理标签 - ${caseName}`"
    width="400px"
    @cancel="handleClose"
  >
    <div class="tags-drawer">
      <!-- Tags Display -->
      <div class="tags-section">
        <div class="section-title">当前标签</div>
        
        <div v-if="localTags.length === 0" class="empty-tags">
          <icon-tag :size="32" />
          <p>暂无标签</p>
        </div>

        <a-space v-else wrap :size="8">
          <a-tag
            v-for="tag in localTags"
            :key="tag"
            :color="getTagColor(tag)"
            closable
            @close="handleDeleteTag(tag)"
          >
            {{ tag }}
          </a-tag>
        </a-space>
      </div>

      <!-- Add Tag Form -->
      <div class="add-section">
        <div class="section-title">添加标签</div>
        
        <a-space direction="vertical" :style="{ width: '100%' }">
          <a-input
            v-model="newTag"
            placeholder="输入标签名称"
            allow-clear
            @press-enter="handleAddTag"
          >
            <template #prefix>
              <icon-tag />
            </template>
          </a-input>
          
          <a-button
            type="primary"
            long
            :disabled="!newTag.trim()"
            :loading="adding"
            @click="handleAddTag"
          >
            <template #icon>
              <icon-plus />
            </template>
            添加标签
          </a-button>
        </a-space>
      </div>
    </div>
  </a-drawer>
</template>

<script setup lang="ts">
import { ref, computed, watch } from 'vue'
import { Message } from '@arco-design/web-vue'
import * as caseBrowserAPI from '@/apis/system/casebrowser'

interface Props {
  visible: boolean
  casespace: string
  caseName: string
  tags: string[]
}

interface Emits {
  (e: 'update:visible', value: boolean): void
  (e: 'refresh'): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// State
const localTags = ref<string[]>([])
const newTag = ref('')
const adding = ref(false)

// Computed
const visibleModel = computed({
  get: () => props.visible,
  set: (value) => emit('update:visible', value),
})

// Watch tags prop
watch(
  () => props.tags,
  (newTags) => {
    localTags.value = [...newTags]
  },
  { immediate: true }
)

// 丰富的标签颜色调色板
const tagColorPalette = [
  'red',
  'orangered',
  'orange',
  'gold',
  'lime',
  'green',
  'cyan',
  'blue',
  'arcoblue',
  'purple',
  'pinkpurple',
  'magenta',
]

// 根据标签名称获取一致的颜色
const getTagColor = (tag: string): string => {
  // 简单的字符串哈希函数
  let hash = 0
  for (let i = 0; i < tag.length; i++) {
    hash = tag.charCodeAt(i) + ((hash << 5) - hash)
    hash = hash & hash // Convert to 32bit integer
  }
  
  // 使用哈希值选择颜色
  const index = Math.abs(hash) % tagColorPalette.length
  return tagColorPalette[index]
}

// Handle add tag
const handleAddTag = async () => {
  const tag = newTag.value.trim()
  if (!tag) {
    Message.warning('请输入标签名称')
    return
  }

  // Check if tag already exists
  if (localTags.value.includes(tag)) {
    Message.warning('标签已存在')
    return
  }

  adding.value = true
  try {
    await caseBrowserAPI.addTag({
      casespace: props.casespace,
      caseName: props.caseName,
      tag,
    })
    
    localTags.value.push(tag)
    newTag.value = ''
    Message.success(`已添加标签: ${tag}`)
    emit('refresh')
  }
  catch (error: any) {
    console.error('Failed to add tag:', error)
    Message.error(error.message || '添加标签失败')
  }
  finally {
    adding.value = false
  }
}

// Handle delete tag
const handleDeleteTag = async (tag: string) => {
  try {
    await caseBrowserAPI.deleteTag(props.casespace, props.caseName, tag)
    
    const index = localTags.value.indexOf(tag)
    if (index > -1) {
      localTags.value.splice(index, 1)
    }
    
    Message.success(`已删除标签: ${tag}`)
    emit('refresh')
  }
  catch (error: any) {
    console.error('Failed to delete tag:', error)
    Message.error(error.message || '删除标签失败')
  }
}

// Handle close
const handleClose = () => {
  newTag.value = ''
  visibleModel.value = false
}
</script>

<style scoped lang="scss">
.tags-drawer {
  display: flex;
  flex-direction: column;
  gap: 24px;

  .section-title {
    font-size: 14px;
    font-weight: 600;
    color: var(--color-text-1);
    margin-bottom: 12px;
  }

  .tags-section {
    .empty-tags {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 40px 20px;
      color: var(--color-text-3);

      p {
        margin-top: 12px;
        font-size: 14px;
      }
    }
  }

  .add-section {
    padding-top: 24px;
    border-top: 1px solid var(--color-border-2);
  }
}
</style>

