<template>
  <div class="case-browser">
    <!-- Toolbar Header -->
    <div class="browser-toolbar">
      <div class="toolbar-left">
        <h3 class="title">用例浏览</h3>
      </div>

      <div class="toolbar-center">
        <!-- 可以在这里添加状态消息 -->
      </div>

      <div class="toolbar-right">
        <a-select
          v-model="selectedCasespace"
          :style="{ width: '200px' }"
          placeholder="选择 Casespace"
          allow-search
          allow-clear
          @change="handleCasespaceChange"
        >
          <a-option
            v-for="cs in casespaces"
            :key="cs.name"
            :value="cs.name"
          >
            {{ cs.name }}
          </a-option>
        </a-select>
      </div>
    </div>

    <!-- Content Area -->
    <div class="browser-content">

    <div v-if="loading" class="loading-state">
      <a-spin />
      <p>加载中...</p>
    </div>

    <div v-else-if="!selectedCasespace" class="empty-state">
      <icon-apps :size="64" />
      <p>请选择一个 Casespace 来查看用例</p>
    </div>

    <div v-else-if="cases.length === 0" class="empty-state">
      <icon-empty :size="64" />
      <p>该 Casespace 下暂无用例</p>
    </div>

    <div v-else class="cases-grid">
      <a-row :gutter="[20, 20]">
        <a-col
          v-for="caseItem in cases"
          :key="caseItem.caseName"
          :xs="24"
          :sm="12"
          :md="8"
          :lg="6"
          :xl="4"
        >
          <a-card
            class="case-card"
            hoverable
            :bordered="false"
          >
            <div class="case-content">
              <div class="case-header">
                <div class="case-icon">
                  <icon-folder :size="20" />
                </div>
                <div class="case-title">
                  <h4 class="case-name">{{ caseItem.caseName }}</h4>
                  <span class="case-meta">{{ caseItem.tags.length }} 个标签</span>
                </div>
              </div>
              
              <div class="content-divider"></div>
              
              <div v-if="caseItem.tags.length === 0" class="no-tags">
                <icon-tag :size="16" class="empty-icon" />
                <span>暂无标签</span>
              </div>
              <div v-else class="tags-container">
                <a-tag
                  v-for="(tag, index) in caseItem.tags.slice(0, 5)"
                  :key="index"
                  :color="getTagColor(tag)"
                  size="small"
                  class="case-tag"
                >
                  {{ tag }}
                </a-tag>
                <a-tag
                  v-if="caseItem.tags.length > 5"
                  size="small"
                  class="more-tag"
                >
                  +{{ caseItem.tags.length - 5 }}
                </a-tag>
              </div>
            </div>

            <template #actions>
              <div class="card-actions">
                <a-button
                  type="text"
                  size="small"
                  class="action-btn"
                  @click="handleOpenTagsDrawer(caseItem)"
                >
                  <icon-tag />
                  <span>标签</span>
                </a-button>
                <a-button
                  type="text"
                  size="small"
                  class="action-btn"
                  @click="handleOpenOptionsDrawer(caseItem)"
                >
                  <icon-settings />
                  <span>选项</span>
                </a-button>
              </div>
            </template>
          </a-card>
        </a-col>
      </a-row>
    </div>
    </div>

    <!-- Tags Drawer -->
    <TagsDrawer
      v-model:visible="tagsDrawerVisible"
      :casespace="selectedCasespace || ''"
      :case-name="currentCase?.caseName || ''"
      :tags="currentCase?.tags || []"
      @refresh="loadCases"
    />

    <!-- Options Drawer -->
    <OptionsDrawer
      v-model:visible="optionsDrawerVisible"
      :casespace="selectedCasespace || ''"
      :case-name="currentCase?.caseName || ''"
      @refresh="loadCaseDetail"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { Message } from '@arco-design/web-vue'
import * as caseBrowserAPI from '@/apis/system/casebrowser'
import * as caseEditorAPI from '@/apis/system/caseeditor'
import type { CaseMetadata } from '@/apis/system/casebrowser-type'
import type { CasespaceItem } from '@/apis/system/caseeditor-type'
import TagsDrawer from './components/TagsDrawer.vue'
import OptionsDrawer from './components/OptionsDrawer.vue'

// State
const selectedCasespace = ref<string>()
const casespaces = ref<CasespaceItem[]>([])
const cases = ref<CaseMetadata[]>([])
const loading = ref(false)

// Drawer state
const tagsDrawerVisible = ref(false)
const optionsDrawerVisible = ref(false)
const currentCase = ref<CaseMetadata>()

// Load casespaces on mount
onMounted(async () => {
  await loadCasespaces()
})

// Load casespaces
const loadCasespaces = async () => {
  try {
    const { data } = await caseEditorAPI.getCasespaces()
    casespaces.value = data
    
    // 默认选中第一个 casespace
    if (data.length > 0 && !selectedCasespace.value) {
      selectedCasespace.value = data[0].name
      await loadCases()
    }
  }
  catch (error) {
    console.error('Failed to load casespaces:', error)
    Message.error('加载 Casespace 列表失败')
  }
}

// Load cases for selected casespace
const loadCases = async () => {
  if (!selectedCasespace.value)
    return

  loading.value = true
  try {
    const { data } = await caseBrowserAPI.getCasesMetadata(selectedCasespace.value)
    cases.value = data
  }
  catch (error) {
    console.error('Failed to load cases:', error)
    Message.error('加载用例列表失败')
  }
  finally {
    loading.value = false
  }
}

// Load case detail (for options)
const loadCaseDetail = async () => {
  if (!selectedCasespace.value || !currentCase.value)
    return

  try {
    const { data } = await caseBrowserAPI.getCaseDetail(
      selectedCasespace.value,
      currentCase.value.caseName
    )
    
    // Update current case in the list
    const index = cases.value.findIndex(
      c => c.caseName === currentCase.value?.caseName
    )
    if (index !== -1) {
      cases.value[index] = data
    }
    currentCase.value = data
  }
  catch (error) {
    console.error('Failed to load case detail:', error)
  }
}

// Handle casespace change
const handleCasespaceChange = () => {
  cases.value = []
  loadCases()
}

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

// Handle open tags drawer
const handleOpenTagsDrawer = (caseItem: CaseMetadata) => {
  currentCase.value = caseItem
  tagsDrawerVisible.value = true
}

// Handle open options drawer
const handleOpenOptionsDrawer = async (caseItem: CaseMetadata) => {
  currentCase.value = caseItem
  
  // Load full case detail with options
  if (selectedCasespace.value) {
    try {
      const { data } = await caseBrowserAPI.getCaseDetail(
        selectedCasespace.value,
        caseItem.caseName
      )
      currentCase.value = data
    }
    catch (error) {
      console.error('Failed to load case detail:', error)
    }
  }
  
  optionsDrawerVisible.value = true
}
</script>

<style scoped lang="scss">
.case-browser {
  height: 100%;
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.browser-toolbar {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 56px;
  padding: 0 16px;
  background-color: var(--color-bg-2);
  border-bottom: 1px solid var(--color-border-2);
  gap: 16px;
  flex-shrink: 0;

  .toolbar-left {
    flex-shrink: 0;

    .title {
      margin: 0;
      font-size: 16px;
      font-weight: 600;
      color: var(--color-text-1);
    }
  }

  .toolbar-center {
    flex: 1;
    display: flex;
    justify-content: center;
    align-items: center;
    min-width: 0;
  }

  .toolbar-right {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-shrink: 0;
  }
}

.browser-content {
  flex: 1;
  overflow: auto;
  padding: 20px;
}

.loading-state,
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: 60px 20px;
  color: var(--color-text-3);

  p {
    margin-top: 16px;
    font-size: 14px;
  }
}

.cases-grid {
  .case-card {
    height: 100%;
    border-radius: 8px;
    border: 1px solid var(--color-border-2);
    overflow: hidden;
    transition: all 0.3s cubic-bezier(0.4, 0, 0.2, 1);
    background: var(--color-bg-1);

    &:hover {
      border-color: rgb(var(--primary-6));
      box-shadow: 0 4px 16px rgba(var(--primary-6), 0.15);
      transform: translateY(-2px);

      .case-icon {
        background: linear-gradient(135deg, rgb(var(--primary-6)), rgb(var(--primary-5)));
        color: #fff;
        transform: rotate(-5deg);
      }
    }

    :deep(.arco-card-body) {
      padding: 20px;
    }

    :deep(.arco-card-actions) {
      background-color: transparent;
      border-top: 1px solid var(--color-border-2);
      padding: 0;
    }
  }

  .case-content {
    .case-header {
      display: flex;
      align-items: flex-start;
      gap: 12px;
      margin-bottom: 16px;

      .case-icon {
        flex-shrink: 0;
        width: 40px;
        height: 40px;
        display: flex;
        align-items: center;
        justify-content: center;
        background: var(--color-fill-2);
        border-radius: 8px;
        color: rgb(var(--primary-6));
        transition: all 0.3s ease;
      }

      .case-title {
        flex: 1;
        min-width: 0;

        .case-name {
          margin: 0;
          font-size: 15px;
          font-weight: 600;
          color: var(--color-text-1);
          line-height: 1.4;
          white-space: nowrap;
          overflow: hidden;
          text-overflow: ellipsis;
          margin-bottom: 4px;
        }

        .case-meta {
          font-size: 12px;
          color: var(--color-text-3);
        }
      }
    }

    .content-divider {
      height: 1px;
      background: var(--color-border-1);
      margin-bottom: 16px;
    }

    .no-tags {
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      padding: 24px 0;
      color: var(--color-text-3);
      font-size: 13px;
      gap: 8px;

      .empty-icon {
        opacity: 0.5;
      }
    }

    .tags-container {
      display: flex;
      flex-wrap: wrap;
      gap: 6px;
      align-items: center;
      min-height: 60px;
      padding: 8px 0;

      .case-tag {
        font-size: 12px;
        border-radius: 4px;
        transition: all 0.2s;

        &:hover {
          transform: translateY(-2px);
          box-shadow: 0 2px 8px rgba(var(--primary-6), 0.25);
        }
      }

      .more-tag {
        background: var(--color-fill-2);
        color: var(--color-text-2);
        border: 1px dashed var(--color-border-2);
        font-weight: 500;
      }
    }
  }

  .card-actions {
    display: flex;
    width: 100%;

    .action-btn {
      flex: 1;
      height: 40px;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 6px;
      color: var(--color-text-2);
      font-size: 13px;
      border-radius: 0;
      transition: all 0.2s;

      &:hover {
        background-color: rgb(var(--primary-1));
        color: rgb(var(--primary-6));

        svg {
          transform: scale(1.15);
        }
      }

      &:not(:last-child) {
        border-right: 1px solid var(--color-border-1);
      }

      svg {
        transition: transform 0.2s;
      }

      span {
        font-weight: 500;
      }
    }
  }
}
</style>

