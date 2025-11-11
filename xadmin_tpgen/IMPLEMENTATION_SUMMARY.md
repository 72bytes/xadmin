# TPGen 保存功能实施总结

## 完成时间

2025-11-11

## 实施内容

### 1. 数据库表设计

已在 `xadmin_db/models.py` 中创建 `TpgenSavedPlan` 模型：

- **表名**: `tpgen_saved_plan`
- **字段**: 20个字段，包括基本信息、配置数据、统计信息等
- **索引**: 3个复合索引优化查询性能
  - `idx_name_category`: 支持按名称和类别查询
  - `idx_user_category`: 支持按创建人和类别查询
  - `idx_create_time_desc`: 支持按时间降序排列

### 2. 数据库 Migration

- **文件**: `xadmin_db/migrations/0003_tpgensavedplan.py`
- **状态**: ✅ 已创建并应用
- **操作**: 创建 `tpgen_saved_plan` 表及相关索引

### 3. Schema 定义

已在 `xadmin_db/schemas.py` 中添加：

- `TpgenSavedPlanIn`: 用于创建新记录的输入 Schema
- `TpgenSavedPlanUpdate`: 用于更新记录的输入 Schema（所有字段可选）

### 4. 后端模块创建

创建了完整的 `xadmin_tpgen` 模块：

```
xadmin_tpgen/
├── __init__.py
├── admin.py
├── api_saved_plan.py      # 核心 API 接口
├── apps.py
├── migrations/
│   └── __init__.py
├── models.py
├── tests.py
├── urls.py                # URL 路由配置
└── views.py
```

### 5. API 接口实现

已在 `api_saved_plan.py` 中实现 7 个接口：

1. **GET /list** - 获取保存的测试计划列表（支持分页和多条件查询）
2. **GET /{plan_id}** - 获取单个测试计划详情
3. **POST /** - 新增测试计划
4. **PUT /{plan_id}** - 修改测试计划
5. **DELETE /{plan_ids}** - 删除测试计划（支持批量）
6. **POST /{plan_id}/use** - 记录使用计划（增加使用计数）
7. **GET /categories/list** - 获取所有类别列表

### 6. 路由注册

- 在 `xadmin_tpgen/urls.py` 中配置了 NinjaExtraAPI
- 在 `xadmin/urls.py` 中注册了 `/tpgen/` 路由
- 在 `xadmin/settings.py` 中添加了 `xadmin_tpgen` 到 INSTALLED_APPS

### 7. 功能特性

#### 查询功能

支持以下查询条件：
- ✅ 按名称模糊查询
- ✅ 按类别精确查询
- ✅ 按创建人查询
- ✅ 按状态查询
- ✅ 分页查询
- ✅ 组合查询

#### 数据管理

- ✅ 创建保存
- ✅ 修改更新（支持部分字段更新）
- ✅ 删除（支持批量删除）
- ✅ 详情查看

#### 统计功能

- ✅ 使用次数统计
- ✅ 最后使用时间记录
- ✅ 类别列表获取

## API 访问路径

- **Base URL**: `http://your-domain/tpgen/saved-plan`
- **API文档**: 参见 `API_DOCUMENTATION.md`

## 数据结构示例

### 保存的数据结构

```json
{
  "name": "RX 7900 系列基准测试计划",
  "category": "Benchmark",
  "description": "针对 RX 7900 系列 GPU 的全面基准测试",
  "configData": {
    "cpu": "Ryzen Threadripper",
    "gpu": "Radeon RX 7900 Series",
    "selectedMachines": [1, 2, 7],
    "osConfigMethod": "same",
    "os": "Ubuntu 22.04",
    "deployment": "Bare Metal",
    "kernelConfigMethod": "same",
    "kernelType": "DKMS",
    "kernelVersion": "6.1",
    "firmwareVersion": "2023.07",
    "versionComparison": false,
    "selectedTestCases": [...]
  },
  "yamlData": {...},
  "cpu": "Ryzen Threadripper",
  "gpu": "Radeon RX 7900 Series",
  "machineCount": 3,
  "osType": "Ubuntu 22.04",
  "kernelType": "DKMS",
  "testCaseCount": 6,
  "status": 1,
  "tags": "rx7900,benchmark,ubuntu"
}
```

## 下一步工作

### 前端集成

需要在前端完成以下工作：

1. **创建 API 调用函数**
   - 文件位置: `xadmin/web/src/apis/tpgen/saved-plan.ts`
   - 参考 `xadmin/web/src/apis/test/plan.ts` 的实现方式

2. **在 CustomPlan.vue 中添加保存按钮**
   - 位置: 第 50-60 行的操作按钮区域
   - 添加保存按钮和对应的处理函数
   - 处理保存逻辑（收集 formData 和 yamlData）

3. **创建保存计划管理页面（可选）**
   - 列表页面: 显示所有保存的计划
   - 详情页面: 查看和编辑保存的计划
   - 支持加载保存的计划到表单中

### 示例代码（前端）

#### 1. API 调用函数 (`apis/tpgen/saved-plan.ts`)

```typescript
import type { HttpResponse, PageRes } from '@/types/global'
import { http } from '@/utils/http'

export interface SavedPlan {
  id: string
  name: string
  category: string
  description: string
  configData: any
  yamlData?: any
  cpu?: string
  gpu?: string
  machineCount: number
  osType?: string
  kernelType?: string
  testCaseCount: number
  status: number
  tags?: string
  useCount: number
  lastUsedTime?: string
  createUser: number
  createUserString: string
  createTime: string
  updateUser?: number
  updateUserString?: string
  updateTime?: string
}

export interface SavedPlanParams {
  name?: string
  category?: string
  createUser?: number
  status?: number
  page?: number
  size?: number
}

// 获取列表
export function getSavedPlanList(params: SavedPlanParams) {
  return http.get<HttpResponse<PageRes<SavedPlan>>>('/tpgen/saved-plan/list', { params })
}

// 获取详情
export function getSavedPlan(id: string | number) {
  return http.get<HttpResponse<SavedPlan>>(`/tpgen/saved-plan/${id}`)
}

// 新增
export function addSavedPlan(data: Partial<SavedPlan>) {
  return http.post<HttpResponse<{ id: number }>>('/tpgen/saved-plan', data)
}

// 修改
export function updateSavedPlan(id: string | number, data: Partial<SavedPlan>) {
  return http.put<HttpResponse<{ id: number }>>(`/tpgen/saved-plan/${id}`, data)
}

// 删除
export function deleteSavedPlan(ids: string) {
  return http.delete<HttpResponse<{ deleted: number }>>(`/tpgen/saved-plan/${ids}`)
}

// 使用计划
export function useSavedPlan(id: string | number) {
  return http.post<HttpResponse<{ id: number; useCount: number }>>(`/tpgen/saved-plan/${id}/use`)
}

// 获取类别列表
export function getCategories() {
  return http.get<HttpResponse<string[]>>('/tpgen/saved-plan/categories/list')
}
```

#### 2. CustomPlan.vue 中添加保存按钮

```vue
<template>
  <div class="custom-plan">
    <!-- 现有内容 -->
    
    <!-- 操作按钮 -->
    <div class="actions">
      <a-button @click="handleReset">
        <template #icon><icon-refresh /></template>
        Reset Form
      </a-button>
      <!-- 新增：保存按钮 -->
      <a-button type="outline" @click="handleSave">
        <template #icon><icon-save /></template>
        Save Plan
      </a-button>
      <a-button type="primary" @click="handleGenerate">
        <template #icon><icon-settings /></template>
        Generate Test Plan
      </a-button>
    </div>
    
    <!-- 新增：保存对话框 -->
    <a-modal 
      v-model:visible="saveDialogVisible" 
      title="保存测试计划配置"
      @ok="handleSaveConfirm"
    >
      <a-form :model="saveForm" layout="vertical">
        <a-form-item label="计划名称" required>
          <a-input v-model="saveForm.name" placeholder="请输入计划名称" />
        </a-form-item>
        <a-form-item label="类别" required>
          <a-select v-model="saveForm.category" placeholder="请选择类别">
            <a-option value="Benchmark">Benchmark</a-option>
            <a-option value="Functional">Functional</a-option>
            <a-option value="Performance">Performance</a-option>
            <a-option value="Stress">Stress</a-option>
            <a-option value="Custom">Custom</a-option>
          </a-select>
        </a-form-item>
        <a-form-item label="描述">
          <a-textarea v-model="saveForm.description" placeholder="请输入描述" />
        </a-form-item>
        <a-form-item label="标签">
          <a-input v-model="saveForm.tags" placeholder="多个标签用逗号分隔" />
        </a-form-item>
      </a-form>
    </a-modal>
  </div>
</template>

<script setup lang="ts">
import { addSavedPlan } from '@/apis/tpgen/saved-plan'
import { Message } from '@arco-design/web-vue'

// 现有代码...

// 保存相关状态
const saveDialogVisible = ref(false)
const saveForm = reactive({
  name: '',
  category: 'Benchmark',
  description: '',
  tags: ''
})

// 处理保存按钮点击
const handleSave = () => {
  // 验证表单是否有数据
  if (formData.selectedMachines.length === 0) {
    Message.warning('请先选择机器')
    return
  }
  if (formData.selectedTestCases.length === 0) {
    Message.warning('请先选择测试用例')
    return
  }
  
  // 显示保存对话框
  saveDialogVisible.value = true
}

// 确认保存
const handleSaveConfirm = async () => {
  if (!saveForm.name) {
    Message.warning('请输入计划名称')
    return
  }
  if (!saveForm.category) {
    Message.warning('请选择类别')
    return
  }
  
  try {
    // 准备保存数据
    const saveData = {
      name: saveForm.name,
      category: saveForm.category,
      description: saveForm.description,
      tags: saveForm.tags,
      configData: { ...formData },
      yamlData: generatedYaml.value,
      cpu: formData.cpu,
      gpu: formData.gpu,
      machineCount: formData.selectedMachines.length,
      osType: formData.os || '',
      kernelType: formData.kernelType || '',
      testCaseCount: formData.selectedTestCases.length,
      status: 1 // 草稿状态
    }
    
    // 调用 API 保存
    const res = await addSavedPlan(saveData)
    if (res.code === 200) {
      Message.success('保存成功')
      saveDialogVisible.value = false
      // 重置表单
      saveForm.name = ''
      saveForm.description = ''
      saveForm.tags = ''
    } else {
      Message.error(res.data || '保存失败')
    }
  } catch (error) {
    Message.error('保存失败')
    console.error(error)
  }
}
</script>
```

## 测试建议

1. **单元测试**
   - 测试每个 API 接口的正常流程
   - 测试边界条件和错误处理

2. **集成测试**
   - 测试完整的创建-查询-修改-删除流程
   - 测试多条件查询的组合

3. **性能测试**
   - 测试大量数据下的查询性能
   - 验证索引的有效性

## 技术栈

- **后端框架**: Django 5.2.7
- **API框架**: Django Ninja Extra
- **数据库**: PostgreSQL/MySQL (支持 JSONField)
- **认证**: JWT Token

## 文件清单

### 后端文件

- ✅ `xadmin_db/models.py` - 数据模型定义
- ✅ `xadmin_db/schemas.py` - API Schema 定义
- ✅ `xadmin_db/migrations/0003_tpgensavedplan.py` - 数据库迁移
- ✅ `xadmin_tpgen/__init__.py`
- ✅ `xadmin_tpgen/apps.py`
- ✅ `xadmin_tpgen/admin.py`
- ✅ `xadmin_tpgen/models.py`
- ✅ `xadmin_tpgen/views.py`
- ✅ `xadmin_tpgen/tests.py`
- ✅ `xadmin_tpgen/api_saved_plan.py` - API 接口实现
- ✅ `xadmin_tpgen/urls.py` - URL 路由配置
- ✅ `xadmin_tpgen/migrations/__init__.py`
- ✅ `xadmin/settings.py` - 更新配置
- ✅ `xadmin/urls.py` - 注册路由

### 文档文件

- ✅ `xadmin_tpgen/API_DOCUMENTATION.md` - API 接口文档
- ✅ `xadmin_tpgen/IMPLEMENTATION_SUMMARY.md` - 实施总结（本文档）

## 验证清单

- [x] 数据库表已创建
- [x] Migration 已应用
- [x] 模块已注册到 INSTALLED_APPS
- [x] 路由已注册到主 urlpatterns
- [x] API 接口已实现
- [x] 无 linting 错误
- [ ] 前端 API 调用函数（待实现）
- [ ] 前端保存按钮（待实现）
- [ ] 前端管理页面（待实现）

## 总结

后端部分已全部完成，数据库表设计合理，API 接口完善，支持所有需要的查询和操作功能。下一步需要在前端实现相应的界面和调用逻辑。

