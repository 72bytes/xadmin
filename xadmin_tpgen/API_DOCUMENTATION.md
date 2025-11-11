# TPGen Saved Plan API 文档

## 概述

这是测试计划配置保存功能的后端 API 接口文档。用户可以通过这些接口保存、查询、修改和删除自定义的测试计划配置。

## 基础信息

- **Base URL**: `/tpgen/saved-plan`
- **认证方式**: TitwBaseAuth (JWT Token)
- **数据格式**: JSON

## 数据库表结构

### tpgen_saved_plan 表

| 字段名 | 类型 | 说明 |
|--------|------|------|
| id | BigAutoField | 主键ID |
| name | CharField(100) | 测试计划名称 |
| category | CharField(50) | 类别（Benchmark/Functional/Performance/Stress/Custom等） |
| description | TextField | 描述 |
| config_data | JSONField | 完整的测试计划配置数据（包含FormData） |
| yaml_data | JSONField | 生成的YAML数据结构 |
| cpu | CharField(100) | CPU类型 |
| gpu | CharField(100) | GPU类型 |
| machine_count | IntegerField | 选择的机器数量 |
| os_type | CharField(50) | 操作系统 |
| kernel_type | CharField(50) | 内核类型 |
| test_case_count | IntegerField | 测试用例数量 |
| status | PositiveIntegerField | 状态(1: 草稿; 2: 已发布; 3: 归档) |
| tags | CharField(200) | 标签，逗号分隔 |
| use_count | IntegerField | 使用次数 |
| last_used_time | DateTimeField | 最后使用时间 |
| create_user | BigIntegerField | 创建人ID |
| create_user_name | CharField(50) | 创建人姓名 |
| create_time | DateTimeField | 创建时间 |
| update_user | BigIntegerField | 修改人ID |
| update_user_name | CharField(50) | 修改人姓名 |
| update_time | DateTimeField | 修改时间 |

### 索引

- `idx_name_category`: (name, category)
- `idx_user_category`: (create_user, category)
- `idx_create_time_desc`: (-create_time)

## API 接口

### 1. 获取保存的测试计划列表

**GET** `/tpgen/saved-plan/list`

#### 请求参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| name | string | 否 | 测试计划名称（模糊查询） |
| category | string | 否 | 类别 |
| createUser | integer | 否 | 创建人ID |
| status | integer | 否 | 状态 |
| page | integer | 否 | 页码，默认1 |
| size | integer | 否 | 每页数量，默认10 |

#### 响应示例

```json
{
  "code": 200,
  "data": {
    "total": 100,
    "list": [
      {
        "id": "1",
        "name": "RX 7900 系列基准测试计划",
        "category": "Benchmark",
        "description": "针对 RX 7900 系列 GPU 的全面基准测试",
        "cpu": "Ryzen Threadripper",
        "gpu": "Radeon RX 7900 Series",
        "machineCount": 3,
        "osType": "Ubuntu 22.04",
        "kernelType": "DKMS",
        "testCaseCount": 6,
        "status": 2,
        "tags": "rx7900,benchmark,ubuntu",
        "useCount": 5,
        "lastUsedTime": "2025-11-11 10:30:00",
        "createUser": 1001,
        "createUserString": "张三",
        "createTime": "2025-11-10 14:20:00",
        "updateUser": 1001,
        "updateUserString": "张三",
        "updateTime": "2025-11-11 09:15:00"
      }
    ]
  }
}
```

### 2. 获取单个保存的测试计划详情

**GET** `/tpgen/saved-plan/{plan_id}`

#### 路径参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| plan_id | integer | 是 | 测试计划ID |

#### 响应示例

```json
{
  "code": 200,
  "data": {
    "id": "1",
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
    "yamlData": {
      "metadata": {...},
      "hardware": {...},
      "environment": {...},
      "firmware": {...},
      "test_suites": [...]
    },
    "cpu": "Ryzen Threadripper",
    "gpu": "Radeon RX 7900 Series",
    "machineCount": 3,
    "osType": "Ubuntu 22.04",
    "kernelType": "DKMS",
    "testCaseCount": 6,
    "status": 2,
    "tags": "rx7900,benchmark,ubuntu",
    "useCount": 5,
    "lastUsedTime": "2025-11-11 10:30:00",
    "createUser": 1001,
    "createUserString": "张三",
    "createTime": "2025-11-10 14:20:00",
    "updateUser": 1001,
    "updateUserString": "张三",
    "updateTime": "2025-11-11 09:15:00"
  }
}
```

### 3. 新增保存的测试计划

**POST** `/tpgen/saved-plan`

#### 请求体

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
  "yamlData": {
    "metadata": {...},
    "hardware": {...},
    "environment": {...},
    "firmware": {...},
    "test_suites": [...]
  },
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

#### 响应示例

```json
{
  "code": 200,
  "data": {
    "id": 1
  }
}
```

### 4. 修改保存的测试计划

**PUT** `/tpgen/saved-plan/{plan_id}`

#### 路径参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| plan_id | integer | 是 | 测试计划ID |

#### 请求体

所有字段都是可选的，只需要传递需要更新的字段。

```json
{
  "name": "更新后的测试计划名称",
  "description": "更新后的描述",
  "status": 2,
  "tags": "new,tags"
}
```

#### 响应示例

```json
{
  "code": 200,
  "data": {
    "id": 1
  }
}
```

### 5. 删除保存的测试计划

**DELETE** `/tpgen/saved-plan/{plan_ids}`

支持批量删除，多个ID用逗号分隔。

#### 路径参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| plan_ids | string | 是 | 测试计划ID，多个用逗号分隔，如 "1,2,3" |

#### 响应示例

```json
{
  "code": 200,
  "data": {
    "deleted": 3
  }
}
```

### 6. 使用保存的测试计划

**POST** `/tpgen/saved-plan/{plan_id}/use`

记录测试计划的使用，增加使用计数并更新最后使用时间。

#### 路径参数

| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| plan_id | integer | 是 | 测试计划ID |

#### 响应示例

```json
{
  "code": 200,
  "data": {
    "id": 1,
    "useCount": 6
  }
}
```

### 7. 获取所有类别列表

**GET** `/tpgen/saved-plan/categories/list`

获取数据库中所有不重复的类别列表。

#### 响应示例

```json
{
  "code": 200,
  "data": [
    "Benchmark",
    "Custom",
    "Functional",
    "Performance",
    "Stress"
  ]
}
```

## 错误响应

所有 API 在发生错误时都会返回以下格式：

```json
{
  "code": 400/403/404/500,
  "data": "错误信息描述"
}
```

## 查询示例

### 按名称查询

```
GET /tpgen/saved-plan/list?name=GPU&page=1&size=10
```

### 按类别查询

```
GET /tpgen/saved-plan/list?category=Benchmark&page=1&size=10
```

### 按创建人查询

```
GET /tpgen/saved-plan/list?createUser=1001&page=1&size=10
```

### 组合查询

```
GET /tpgen/saved-plan/list?name=GPU&category=Benchmark&createUser=1001&status=2&page=1&size=10
```

## 前端调用示例

```typescript
import { http } from '@/utils/http'

// 获取列表
export function getSavedPlanList(params: any) {
  return http.get('/tpgen/saved-plan/list', { params })
}

// 获取详情
export function getSavedPlan(id: number) {
  return http.get(`/tpgen/saved-plan/${id}`)
}

// 新增
export function addSavedPlan(data: any) {
  return http.post('/tpgen/saved-plan', data)
}

// 修改
export function updateSavedPlan(id: number, data: any) {
  return http.put(`/tpgen/saved-plan/${id}`, data)
}

// 删除
export function deleteSavedPlan(ids: string) {
  return http.delete(`/tpgen/saved-plan/${ids}`)
}

// 使用计划
export function useSavedPlan(id: number) {
  return http.post(`/tpgen/saved-plan/${id}/use`)
}

// 获取类别列表
export function getCategories() {
  return http.get('/tpgen/saved-plan/categories/list')
}
```

## 注意事项

1. 所有接口都需要认证，请在请求头中携带有效的 JWT Token
2. `configData` 字段存储完整的表单数据，建议前端在保存前进行验证
3. `yamlData` 字段可选，如果不生成 YAML 可以不传
4. 索引已优化，支持按名称、类别、创建人的快速查询
5. 默认按创建时间降序排列，最新的记录在前面

