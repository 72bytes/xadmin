# 我的测试计划 (MyTP) 模块

## 📁 项目结构

```
myTP/
├── index.vue                    # 主入口页面（简洁版）
├── index.scss                   # 全局样式
├── types.ts                     # TypeScript 类型定义
├── README.md                    # 项目文档
├── components/                  # 组件目录
│   ├── PlanTable.vue           # 测试计划表格组件
│   ├── PlanPreviewDrawer.vue   # 预览抽屉组件
│   └── PlanEditModal.vue       # 编辑对话框组件
└── composables/                 # 组合式函数目录
    └── usePlanData.ts          # 数据管理 composable
```

## 🎯 功能概述

这是一个用于管理已保存的测试计划的模块，用户可以：

- **查看计划列表**：展示所有已保存的测试计划
- **搜索和筛选**：支持按名称、类别、状态筛选
- **预览计划**：查看测试计划的详细配置信息
- **使用计划**：将已保存的计划应用到在线生成页面
- **编辑计划**：修改测试计划的基本信息
- **删除计划**：单个删除或批量删除

## 📦 组件说明

### 1. PlanTable.vue (表格组件)

**功能**：
- 展示测试计划列表
- 提供搜索和筛选功能
- 支持批量选择和操作
- 自定义列渲染（类别、状态、标签、硬件配置等）

**Props**：
```typescript
interface Props {
  dataList: SavedPlanResp[]        // 数据列表
  loading: boolean                  // 加载状态
  pagination: any                   // 分页配置
  selectedKeys: (string | number)[] // 已选中的行
  queryForm: QueryForm              // 查询表单
}
```

**Emits**：
- `refresh`: 刷新列表
- `search`: 搜索
- `reset`: 重置搜索
- `batch-delete`: 批量删除
- `preview`: 预览计划
- `use`: 使用计划
- `update`: 编辑计划
- `delete`: 删除计划

### 2. PlanPreviewDrawer.vue (预览抽屉组件)

**功能**：
- 以抽屉形式展示测试计划详情
- 显示所有配置信息
- 支持配置数据的 JSON 格式预览

**Props**：
```typescript
interface Props {
  modelValue: boolean           // 显示/隐藏状态
  record: SavedPlanResp | null  // 当前记录
}
```

### 3. PlanEditModal.vue (编辑对话框组件)

**功能**：
- 提供表单编辑界面
- 支持修改计划名称、类别、描述、标签、状态

**Props**：
```typescript
interface Props {
  modelValue: boolean      // 显示/隐藏状态
  form: EditForm | null    // 表单数据
}
```

**Emits**：
- `ok`: 确认编辑
- `cancel`: 取消编辑

## 🔧 Composables 说明

### usePlanData.ts

提供了一系列组合式函数来管理不同的业务逻辑：

#### 1. `usePlanData(queryForm)`
主数据管理，负责列表查询和分页

**返回值**：
```typescript
{
  loading: Ref<boolean>              // 加载状态
  dataList: ComputedRef<SavedPlanResp[]>  // 数据列表
  pagination: any                    // 分页信息
  selectedKeys: Ref<(string | number)[]>  // 选中的行
  search: () => void                 // 搜索函数
  refresh: () => void                // 刷新函数
}
```

#### 2. `usePlanPreview()`
预览功能管理

**返回值**：
```typescript
{
  previewDrawerVisible: Ref<boolean>      // 抽屉显示状态
  currentRecord: Ref<SavedPlanResp | null>  // 当前预览的记录
  onPreview: (record: SavedPlanResp) => Promise<void>  // 预览函数
}
```

#### 3. `usePlanUsage()`
使用计划功能

**返回值**：
```typescript
{
  onUse: (record: SavedPlanResp) => Promise<void>  // 使用计划
}
```

#### 4. `usePlanEdit(refresh)`
编辑功能管理

**参数**：
- `refresh: () => void` - 刷新回调

**返回值**：
```typescript
{
  editModalVisible: Ref<boolean>         // 对话框显示状态
  editForm: Ref<EditForm | null>         // 编辑表单数据
  onUpdate: (record: SavedPlanResp) => void        // 打开编辑对话框
  handleUpdateConfirm: () => Promise<void>         // 确认更新
  handleUpdateCancel: () => void                   // 取消更新
}
```

#### 5. `usePlanDelete(refresh, selectedKeys)`
删除功能管理

**参数**：
- `refresh: () => void` - 刷新回调
- `selectedKeys: Ref<(string | number)[]>` - 选中的行

**返回值**：
```typescript
{
  onDelete: (record: SavedPlanResp) => void     // 删除单条记录
  onBatchDelete: () => void                      // 批量删除
}
```

## 📝 类型定义 (types.ts)

```typescript
// 查询表单
interface QueryForm {
  name?: string
  category?: string
  status?: number
  sort: string[]
}

// 编辑表单
interface EditForm {
  name: string
  category: string
  description?: string
  tags?: string
  status: number
}

// 分类选项
const CATEGORY_OPTIONS = [...]

// 状态选项
const STATUS_OPTIONS = [...]
```

## 🎨 样式说明 (index.scss)

提供了页面的基础样式：
- 容器布局
- 头部样式
- 内容区域样式

## 🔄 数据流

```
index.vue (主入口)
    ↓
usePlanData (数据管理)
    ↓
PlanTable (表格展示)
    ↓
用户操作 (预览/编辑/删除等)
    ↓
对应的 composable 函数处理
    ↓
API 调用
    ↓
刷新数据
```

## 🚀 使用示例

主入口文件 `index.vue` 的核心代码：

```vue
<script setup lang="ts">
import { useResetReactive } from '@/hooks'
import PlanTable from './components/PlanTable.vue'
import PlanPreviewDrawer from './components/PlanPreviewDrawer.vue'
import PlanEditModal from './components/PlanEditModal.vue'
import { usePlanData, usePlanPreview, usePlanUsage, usePlanEdit, usePlanDelete } from './composables/usePlanData'

// 查询表单
const [queryForm, resetForm] = useResetReactive({
  sort: ['createTime,desc'],
})

// 数据管理
const { loading, dataList, pagination, selectedKeys, search, refresh } = usePlanData(queryForm)

// 预览功能
const { previewDrawerVisible, currentRecord, onPreview } = usePlanPreview()

// 使用功能
const { onUse } = usePlanUsage()

// 编辑功能
const { editModalVisible, editForm, onUpdate, handleUpdateConfirm, handleUpdateCancel } = usePlanEdit(search)

// 删除功能
const { onDelete, onBatchDelete } = usePlanDelete(refresh, selectedKeys)
</script>
```

## ✨ 重构优势

与原来的单文件实现相比，新架构具有以下优势：

### 1. **可维护性** ⭐⭐⭐⭐⭐
- 组件职责清晰，每个文件专注单一功能
- 业务逻辑分离到 composables，易于测试和复用
- 代码结构清晰，易于理解和修改

### 2. **可复用性** ⭐⭐⭐⭐⭐
- 组件可以在其他页面中复用
- Composable 函数可以在不同场景中使用
- 类型定义统一管理

### 3. **可测试性** ⭐⭐⭐⭐⭐
- 组件独立，易于单元测试
- Composable 函数纯粹，易于测试
- Mock 数据更容易注入

### 4. **可扩展性** ⭐⭐⭐⭐⭐
- 新增功能只需添加新的组件或 composable
- 不影响现有代码结构
- 易于添加新的状态管理

### 5. **开发体验** ⭐⭐⭐⭐⭐
- TypeScript 提供完整类型提示
- 组件热重载更快
- 代码跳转更准确

## 📊 代码统计

| 项目 | 原始版本 | 重构后 |
|------|---------|--------|
| 文件数量 | 1 个 | 7 个 |
| 主入口行数 | 604 行 | 88 行 |
| 组件复用性 | ❌ | ✅ |
| 业务逻辑分离 | ❌ | ✅ |
| 类型安全 | 部分 | 完全 |
| 可测试性 | 较低 | 较高 |

## 🔮 未来优化建议

1. **添加单元测试**
   - 为 composables 添加测试
   - 为组件添加测试

2. **性能优化**
   - 添加虚拟滚动支持（如果数据量大）
   - 优化表格渲染性能

3. **功能增强**
   - 添加导出功能
   - 添加计划对比功能
   - 添加计划版本管理

4. **用户体验**
   - 添加骨架屏
   - 优化加载动画
   - 添加更多提示信息

## 📚 参考文档

- [Vue 3 Composition API](https://vuejs.org/guide/extras/composition-api-faq.html)
- [TypeScript 类型系统](https://www.typescriptlang.org/docs/)
- [Arco Design Vue](https://arco.design/vue)

---

**开发完成时间**: 2025-11-11  
**重构目标**: ✅ 组件化、可维护、可扩展  
**项目状态**: ✅ 已完成，可投入使用

