# TPGen Online - 数据库集成迁移文档

## 📋 更新概述

已将 TPGen Online（在线测试计划生成器）从使用 Mock 数据迁移到使用数据库真实数据。

**更新日期**: 2025-11-12  
**版本**: v2.0

---

## 🎯 主要变更

### 1. API 扩展

**文件**: `web/src/apis/tpdb/index.ts`

新增 TPGEN Online 专用 API 接口：

```typescript
// 获取可用测试设备（带筛选）
export function getAvailableDevices(query?: {
  gpuModel?: string
  gpuSeries?: string
  asicName?: string
})

// 获取测试用例树形结构
export function getTestCaseTree()

// 获取 OS 配置选项列表
export function getOsOptions()

// 获取内核版本选项
export function getKernelOptions(osConfigId?: number)
```

### 2. 类型定义更新

**文件**: `web/src/views/tpgen/online/types.ts`

#### Machine 接口更新

```typescript
// 旧版本（Mock 数据）
interface Machine {
  id: number
  name: string
  motherboard: string
  gpu: string
  cpu: string
  status: 'Available' | 'Unavailable'
}

// 新版本（数据库字段）
interface Machine {
  id: number
  hostname: string           // 对应 sut_devices.hostname
  asicName?: string          // 对应 sut_devices.asic_name
  ipAddress?: string         // 对应 sut_devices.ip_address
  deviceId?: string          // 对应 sut_devices.device_id
  revId?: string             // 对应 sut_devices.rev_id
  gpuSeries?: string         // 对应 sut_devices.gpu_series
  gpuModel?: string          // 对应 sut_devices.gpu_model
  // 兼容旧代码的字段
  name?: string              // 映射到 hostname
  gpu?: string               // 映射到 gpuModel
  status?: 'Available' | 'Unavailable'
}
```

#### TestCase 接口更新

```typescript
// 旧版本
interface TestCase {
  id: number
  name: string
  description: string
  testType?: string
  subgroup?: string
}

// 新版本（数据库字段）
interface TestCase {
  id: number
  caseName: string           // 对应 test_cases.case_name
  caseConfig?: Record<string, any>  // 对应 test_cases.case_config
  testComponentId?: number   // 对应 test_cases.test_component_id
  testTypeName?: string      // 从关联表获取
  componentName?: string     // 从关联表获取
  componentCategory?: string // 从关联表获取
  // 兼容旧代码的字段
  name?: string              // 映射到 caseName
  description?: string       // 从 caseConfig 提取
  testType?: string          // 测试类型名称
  subgroup?: string          // 映射到 componentName
}
```

### 3. Composables 创建

#### useMachines.ts

**文件**: `web/src/views/tpgen/online/composables/useMachines.ts`

统一管理机器数据获取：

```typescript
export function useMachines() {
  return {
    machines,              // 所有机器列表
    loading,               // 加载状态
    loaded,                // 是否已加载
    loadMachines,          // 加载机器数据
    getMachineById,        // 根据 ID 获取机器
    getMachinesByGpu,      // 根据 GPU 过滤机器
    getMachineName,        // 获取机器名称
    getMachinesByIds,      // 批量获取机器
  }
}
```

#### useTestCases.ts

**文件**: `web/src/views/tpgen/online/composables/useTestCases.ts`

统一管理测试用例数据获取：

```typescript
export function useTestCases() {
  return {
    testCaseGroups,        // 测试用例组（树形结构）
    loading,               // 加载状态
    loaded,                // 是否已加载
    loadTestCases,         // 加载测试用例
    getAllTestCases,       // 获取所有测试用例（扁平化）
    getTestCasesByType,    // 按类型获取用例
    getTestCasesByComponent, // 按组件获取用例
    searchTestCases,       // 搜索测试用例
  }
}
```

### 4. 组件更新

#### HardwareConfig.vue

**变更**:
- ✅ 使用 `useMachines` composable
- ✅ 从 `listSutDevices` API 获取真实设备数据
- ✅ 使用 `getGpuSeriesOptions` API 获取 GPU 系列选项
- ✅ 添加加载状态显示
- ✅ 更新机器卡片展示字段（ASIC、GPU Model、GPU Series、IP）

**关键代码**:
```typescript
import { useMachines } from '../composables/useMachines'
const { machines, getMachineById, loadMachines } = useMachines()

onMounted(async () => {
  await Promise.all([
    loadGpuOptions(),
    loadMachines()
  ])
})
```

#### TestCaseManager.vue

**变更**:
- ✅ 使用 `useTestCases` composable
- ✅ 从数据库动态加载测试用例数据
- ✅ 支持测试类型、测试组件、测试用例三层结构
- ✅ 添加加载状态显示

**关键代码**:
```typescript
import { useTestCases } from '../composables/useTestCases'
const { testCaseGroups, loadTestCases, getAllTestCases: getAllTestCasesFromDb } = useTestCases()

onMounted(async () => {
  await loadTestCases()
})
```

#### OSConfig.vue

**变更**:
- ✅ 使用 `useMachines` composable 获取机器名称
- ✅ 移除对 `mockMachines` 的直接引用

#### KernelConfig.vue

**变更**:
- ✅ 使用 `useMachines` composable 获取机器名称
- ✅ 移除对 `mockMachines` 的直接引用

#### CustomPlan.vue

**变更**:
- ✅ 使用 `useMachines` composable
- ✅ 在生成 YAML 时使用真实机器数据
- ✅ 更新机器信息字段（hostname、asicName、gpuModel、gpuSeries、ipAddress）

**关键代码**:
```typescript
import { useMachines } from '../composables/useMachines'
const { machines, getMachineById, loadMachines } = useMachines()

onMounted(async () => {
  await loadMachines()
  updateProgress()
})
```

---

## 📊 数据流程图

### 旧版本（Mock 数据）

```
Component → mockData.ts → 静态 Mock 数据
```

### 新版本（数据库数据）

```
Component
  ↓
useMachines / useTestCases Composable
  ↓
tpdb API (/tp/api/)
  ↓
Django Ninja API
  ↓
tpdb PostgreSQL Database
```

---

## 🎯 数据映射关系

### SUT 设备数据映射

| 数据库字段 (tpdb.sut_devices) | 前端字段 (Machine) | 说明 |
|-------------------------------|-------------------|------|
| hostname | hostname | 设备主机名 |
| asic_name | asicName | ASIC 名称 |
| ip_address | ipAddress | IP 地址 |
| device_id | deviceId | 设备 ID |
| rev_id | revId | 版本 ID |
| gpu_series | gpuSeries | GPU 系列 |
| gpu_model | gpuModel | GPU 型号 |

### 测试用例数据映射

| 数据库表 | 数据库字段 | 前端字段 | 说明 |
|---------|-----------|---------|------|
| test_types | type_name | testTypeName | 测试类型名称 |
| test_components | component_name | componentName | 测试组件名称 |
| test_components | component_category | componentCategory | 组件分类 |
| test_cases | case_name | caseName | 测试用例名称 |
| test_cases | case_config | caseConfig | 用例配置(JSON) |

---

## ✅ 兼容性保证

为确保平滑迁移，新版本保留了对旧字段的兼容：

1. **Machine 接口**: 保留 `name`, `gpu`, `status` 字段，映射到新字段
2. **TestCase 接口**: 保留 `name`, `description`, `testType`, `subgroup` 字段
3. **数据转换**: Composables 自动完成数据格式转换

---

## 🚀 使用指南

### 1. 确保数据库有数据

在使用前，确保 tpdb 数据库中有测试数据：

```sql
-- 检查设备数据
SELECT COUNT(*) FROM sut_devices;

-- 检查测试类型
SELECT COUNT(*) FROM test_types;

-- 检查测试组件
SELECT COUNT(*) FROM test_components;

-- 检查测试用例
SELECT COUNT(*) FROM test_cases;
```

### 2. 初始化示例数据

如果数据库为空，可以使用示例数据：

```bash
cd /home/xadmin
psql -h 10.67.167.53 -p 5433 -U amd -d tpdb -f tpgen/tp_data.sql
```

### 3. 访问页面

```
http://localhost:5173/tpgen/online
```

页面会自动加载数据库中的真实数据。

---

## 🔍 故障排查

### 问题 1: 没有设备显示

**原因**: 数据库中没有设备数据

**解决**:
1. 进入 TPDB 管理页面添加设备
2. 或导入示例数据
3. 检查 API 是否正常：`GET /tp/api/sut-device/list`

### 问题 2: 没有测试用例显示

**原因**: 数据库中没有测试类型、组件和用例数据

**解决**:
1. 进入 TPDB 管理页面依次添加：
   - 测试类型（如 Benchmark, Functional）
   - 测试组件（如 ffmpeg, clpeak）
   - 测试用例
2. 或导入示例数据
3. 检查 API 是否正常：`GET /tp/api/test-type/list`

### 问题 3: 加载很慢

**原因**: 数据量大或网络慢

**解决**:
1. 检查数据库查询性能
2. 添加适当的索引
3. 考虑添加缓存机制
4. 减少单次加载的数据量

### 问题 4: 数据格式错误

**原因**: API 返回的数据格式不匹配

**解决**:
1. 检查 Composables 中的数据转换逻辑
2. 查看浏览器控制台的错误信息
3. 验证 API 响应格式

---

## 📝 开发注意事项

### 1. Mock 数据保留

`mockData.ts` 文件仍然保留，用于：
- OS 选项（osOptions）
- 部署方式选项（deploymentOptions）
- 内核类型选项（kernelTypeOptions）
- 内核版本选项（kernelVersionOptions）
- 固件版本选项（firmwareVersionOptions）

这些选项数据可以考虑后续也迁移到数据库。

### 2. 缓存机制

Composables 使用内存缓存，避免重复请求：
- 首次加载后数据缓存在内存
- 可以通过 `force` 参数强制刷新
- 页面刷新会清除缓存

### 3. 数据加载时机

- `HardwareConfig`: 组件挂载时加载设备和 GPU 选项
- `TestCaseManager`: 组件挂载时加载测试用例
- `CustomPlan`: 组件挂载时加载设备数据

### 4. 错误处理

所有 API 调用都有错误处理，失败时：
- 显示错误消息（Arco Message）
- 返回空数据
- 记录错误日志到控制台

---

## 🎉 迁移完成检查清单

- [x] API 接口扩展完成
- [x] 类型定义更新完成
- [x] useMachines Composable 创建完成
- [x] useTestCases Composable 创建完成
- [x] HardwareConfig.vue 更新完成
- [x] TestCaseManager.vue 更新完成
- [x] OSConfig.vue 更新完成
- [x] KernelConfig.vue 更新完成
- [x] CustomPlan.vue 更新完成
- [x] 数据兼容性保证
- [x] 错误处理完善
- [x] 文档编写完成

---

## 📚 相关文档

- [TPDB README](../../tpdb/README.md) - TPDB 管理页面文档
- [TPDB Installation](../../tpdb/INSTALLATION.md) - TPDB 安装指南
- [TPGEN API Document](../../../tpgen/TPGEN_API_DOCUMENT.md) - API 文档
- [TPGen Models](../../../tpgen/models.py) - 数据模型定义

---

**维护者**: XAdmin Team  
**最后更新**: 2025-11-12  
**状态**: ✅ 迁移完成

