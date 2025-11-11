# tpgen API 接口文档

## 概述

**版本**: v2.0  
**基础URL**: `/tp/api/`  
**数据库**: tpdb (10.67.167.53:5433)  
**认证方式**: 当前未启用（开发环境），生产环境需要 JWT Token  
**API 文档**: `/tp/api/docs` (Swagger UI)  
**OpenAPI Schema**: `/tp/api/openapi.json`

---

## 快速开始

### 基础端点

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/tp/` | 服务首页（返回所有可用API端点） |
| GET | `/tp/health` | 健康检查 |
| GET | `/tp/api/docs` | Swagger API 交互式文档 |
| GET | `/tp/api/openapi.json` | OpenAPI 规范 |

---

## 目录

1. [基础端点](#基础端点)
2. [设备管理 (SUT Devices)](#1-设备管理-sut-devices)
3. [操作系统配置 (OS Configs)](#2-操作系统配置-os-configs)
4. [测试类型 (Test Types)](#3-测试类型-test-types)
5. [测试组件 (Test Components)](#4-测试组件-test-components)
6. [测试用例 (Test Cases)](#5-测试用例-test-cases)
7. [测试计划 (Test Plans)](#6-测试计划-test-plans)

---

## 1. 设备管理 (SUT Devices)

### 1.1 获取设备列表

**接口地址**: `GET /tp/api/sut-device/list`

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | int | 否 | 页码，默认1 |
| size | int | 否 | 每页数量，默认10 |
| gpu_model | string | 否 | 按GPU型号过滤（模糊匹配） |
| hostname | string | 否 | 按主机名过滤（模糊匹配） |

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "total": 10,
    "list": [
      {
        "id": 1,
        "hostname": "aerith-0",
        "asicName": "VGH 163F_REV_AE",
        "ipAddress": "10.67.78.176",
        "deviceId": "163f",
        "revId": "ae",
        "gpuSeries": "AMD APU",
        "gpuModel": "AMD Custom APU 0405",
        "createdAt": "2025-11-11 10:00:00",
        "updatedAt": "2025-11-11 10:00:00"
      }
    ]
  }
}
```

**cURL 示例**:
```bash
curl -X GET "http://localhost:8000/tp/api/sut-device/list?page=1&size=10"
```

---

### 1.2 获取设备详情

**接口地址**: `GET /tp/api/sut-device/{device_id}`

**路径参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| device_id | int | 是 | 设备ID |

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "hostname": "aerith-0",
    "asicName": "VGH 163F_REV_AE",
    "ipAddress": "10.67.78.176",
    "deviceId": "163f",
    "revId": "ae",
    "gpuSeries": "AMD APU",
    "gpuModel": "AMD Custom APU 0405",
    "createdAt": "2025-11-11 10:00:00",
    "updatedAt": "2025-11-11 10:00:00"
  }
}
```

**错误响应示例**:
```json
{
  "code": 500,
  "data": "设备不存在"
}
```

---

### 1.3 创建设备

**接口地址**: `POST /tp/api/sut-device/`

**请求体**:
```json
{
  "hostname": "navi31-test-01",
  "asicName": "Navi 31 GFX1100",
  "ipAddress": "10.67.80.101",
  "deviceId": "744c",
  "revId": "c8",
  "gpuSeries": "Radeon RX 7000",
  "gpuModel": "RX 7900 XTX"
}
```

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "id": 11
  }
}
```

**错误响应示例**:
```json
{
  "code": 500,
  "data": "创建失败: hostname already exists"
}
```

---

### 1.4 更新设备

**接口地址**: `PUT /tp/api/sut-device/{device_id}`

**路径参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| device_id | int | 是 | 设备ID |

**请求体**:
```json
{
  "hostname": "navi31-test-01-updated",
  "asicName": "Navi 31 GFX1100",
  "ipAddress": "10.67.80.101",
  "deviceId": "744c",
  "revId": "c8",
  "gpuSeries": "Radeon RX 7000",
  "gpuModel": "RX 7900 XT"
}
```

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "id": 11
  }
}
```

---

### 1.5 删除设备（支持批量）

**接口地址**: `DELETE /tp/api/sut-device/{device_ids}`

**路径参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| device_ids | string | 是 | 设备ID，多个ID用逗号分隔（如 "1,2,3"） |

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "deleted": 3
  }
}
```

---

## 2. 操作系统配置 (OS Configs)

### 2.1 获取OS配置列表

**接口地址**: `GET /tp/api/os-config/list`

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| os_family | string | 否 | 按OS家族过滤（模糊匹配） |
| page | int | 否 | 页码，默认1 |
| size | int | 否 | 每页数量，默认10 |

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "total": 8,
    "list": [
      {
        "id": 1,
        "osFamily": "Ubuntu",
        "version": "22.04",
        "downloadUrl": "https://releases.ubuntu.com/22.04/",
        "createdAt": "2025-11-11 10:00:00",
        "updatedAt": "2025-11-11 10:00:00"
      },
      {
        "id": 2,
        "osFamily": "Ubuntu",
        "version": "24.04",
        "downloadUrl": "https://releases.ubuntu.com/24.04/",
        "createdAt": "2025-11-11 10:00:00",
        "updatedAt": "2025-11-11 10:00:00"
      }
    ]
  }
}
```

---

### 2.2 创建OS配置

**接口地址**: `POST /tp/api/os-config/`

**请求体**:
```json
{
  "osFamily": "Fedora",
  "version": "39",
  "downloadUrl": "https://getfedora.org/en/workstation/download/"
}
```

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "id": 9
  }
}
```

---

## 3. 测试类型 (Test Types)

### 3.1 获取测试类型列表

**接口地址**: `GET /tp/api/test-type/list`

**响应示例**:
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "typeName": "Benchmark",
      "createdAt": "2025-11-11 10:00:00",
      "updatedAt": "2025-11-11 10:00:00"
    },
    {
      "id": 2,
      "typeName": "Functional",
      "createdAt": "2025-11-11 10:00:00",
      "updatedAt": "2025-11-11 10:00:00"
    },
    {
      "id": 3,
      "typeName": "Performance",
      "createdAt": "2025-11-11 10:00:00",
      "updatedAt": "2025-11-11 10:00:00"
    }
  ]
}
```

---

### 3.2 创建测试类型

**接口地址**: `POST /tp/api/test-type/`

**请求体**:
```json
{
  "typeName": "Stress"
}
```

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "id": 4
  }
}
```

---

## 4. 测试组件 (Test Components)

### 4.1 获取测试组件列表

**接口地址**: `GET /tp/api/test-component/list`

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| test_type_id | int | 否 | 按测试类型ID过滤 |
| component_category | string | 否 | 按组件分类过滤 |

**响应示例**:
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "testTypeId": 1,
      "componentCategory": "Media",
      "componentName": "ffmpeg"
    },
    {
      "id": 2,
      "testTypeId": 1,
      "componentCategory": "Compute",
      "componentName": "clpeak"
    }
  ]
}
```

---

### 4.2 创建测试组件

**接口地址**: `POST /tp/api/test-component/`

**请求体**:
```json
{
  "testTypeId": 1,
  "componentCategory": "Graphics",
  "componentName": "glmark2"
}
```

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "id": 10
  }
}
```

---

## 5. 测试用例 (Test Cases)

### 5.1 获取测试用例列表

**接口地址**: `GET /tp/api/test-case/list`

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| test_component_id | int | 否 | 按测试组件ID过滤 |
| page | int | 否 | 页码，默认1 |
| size | int | 否 | 每页数量，默认10 |

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "total": 30,
    "list": [
      {
        "id": 1,
        "testComponentId": 1,
        "caseName": "H.264 4K Encoding",
        "caseConfig": {
          "resolution": "3840x2160",
          "codec": "h264",
          "bitrate": "20M",
          "preset": "medium",
          "iterations": 100
        },
        "createdAt": "2025-11-11 10:00:00",
        "updatedAt": "2025-11-11 10:00:00"
      }
    ]
  }
}
```

---

### 5.2 创建测试用例

**接口地址**: `POST /tp/api/test-case/`

**请求体**:
```json
{
  "testComponentId": 1,
  "caseName": "H.265 8K Encoding",
  "caseConfig": {
    "resolution": "7680x4320",
    "codec": "hevc",
    "bitrate": "40M",
    "preset": "fast",
    "iterations": 50
  }
}
```

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "id": 31
  }
}
```

---

## 6. 测试计划 (Test Plans)

### 6.1 获取测试计划列表

**接口地址**: `GET /tp/api/test-plan/list`

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| plan_name | string | 否 | 按计划名称过滤（模糊匹配） |
| page | int | 否 | 页码，默认1 |
| size | int | 否 | 每页数量，默认10 |

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "total": 20,
    "list": [
      {
        "id": 1,
        "planName": "RX 7900 XTX Media Benchmark",
        "planDescription": "媒体编码性能测试",
        "sutDeviceId": 4,
        "osConfigId": 2,
        "createdBy": "qa_team",
        "createdAt": "2025-11-11 10:00:00",
        "updatedAt": "2025-11-11 10:00:00"
      }
    ]
  }
}
```

---

### 6.2 获取测试计划详情

**接口地址**: `GET /tp/api/test-plan/{plan_id}`

**路径参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| plan_id | int | 是 | 测试计划ID |

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "planName": "RX 7900 XTX Media Benchmark",
    "planDescription": "媒体编码性能测试",
    "sutDeviceId": 4,
    "osConfigId": 2,
    "createdBy": "qa_team",
    "createdAt": "2025-11-11 10:00:00",
    "updatedAt": "2025-11-11 10:00:00",
    "testCases": [
      {
        "id": 1,
        "caseName": "H.264 4K Encoding",
        "timeout": null
      },
      {
        "id": 2,
        "caseName": "H.265 4K Encoding",
        "timeout": 300
      }
    ]
  }
}
```

---

### 6.3 创建测试计划

**接口地址**: `POST /tp/api/test-plan/`

**请求体**:
```json
{
  "planName": "Navi 33 Graphics Performance Test",
  "planDescription": "测试 Navi 33 GPU 的图形性能",
  "sutDeviceId": 5,
  "osConfigId": 2,
  "createdBy": "admin"
}
```

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "id": 21
  }
}
```

---

### 6.4 删除测试计划（支持批量）

**接口地址**: `DELETE /tp/api/test-plan/{plan_ids}`

**路径参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| plan_ids | string | 是 | 测试计划ID，多个ID用逗号分隔（如 "1,2,3"） |

**响应示例**:
```json
{
  "code": 200,
  "data": {
    "deleted": 3
  }
}
```

---

## 7. 错误代码与响应格式

### 成功响应格式

所有成功的 API 响应使用统一格式：

```json
{
  "code": 200,
  "data": {
    // 实际返回的数据
  }
}
```

### 失败响应格式

所有失败的 API 响应格式：

```json
{
  "code": 500,
  "data": "错误描述信息"
}
```

### HTTP 状态码

| 状态码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 403 | 禁止访问（认证失败） |
| 404 | 资源不存在 |
| 500 | 服务器内部错误 |

---

## 8. 数据模型

### SutDevice (设备)
```typescript
interface SutDevice {
  id: number;
  hostname: string;           // 主机名（唯一）
  asicName?: string;          // ASIC名称
  ipAddress?: string;         // IP地址
  deviceId?: string;          // 设备ID
  revId?: string;             // 版本ID
  gpuSeries?: string;         // GPU系列
  gpuModel?: string;          // GPU型号
  createdAt: string;          // 创建时间
  updatedAt: string;          // 更新时间
}
```

### OsConfig (OS配置)
```typescript
interface OsConfig {
  id: number;
  osFamily: string;           // OS家族
  version: string;            // 版本号
  downloadUrl?: string;       // 下载链接
  createdAt: string;
  updatedAt: string;
}
```

### TestCase (测试用例)
```typescript
interface TestCase {
  id: number;
  testComponentId: number;    // 测试组件ID
  caseName: string;           // 用例名称
  caseConfig: object;         // JSON配置
  createdAt: string;
  updatedAt: string;
}
```

### TestPlan (测试计划)
```typescript
interface TestPlan {
  id: number;
  planName: string;           // 计划名称
  planDescription?: string;   // 计划描述
  sutDeviceId: number;        // 设备ID
  osConfigId: number;         // OS配置ID
  createdBy?: string;         // 创建者
  createdAt: string;
  updatedAt: string;
}
```

---

## 9. 认证说明

### 当前状态

**开发环境**：认证已禁用，无需 Token 即可访问所有 API。

### 启用认证（生产环境）

如需启用认证，需要修改 `/home/xadmin/tpgen/urls.py`：

```python
from xadmin_auth import auth

ninja_api = NinjaExtraAPI(
    auth=auth.TitwBaseAuth(),  # 启用认证
    title='TPGEN API',
    urls_namespace='tpgen-api'
)
```

启用后，所有API请求需要在请求头中添加：

```
Authorization: Bearer <your_jwt_token>
```

获取 Token 请参考系统认证接口：`POST /system/auth/token`

---

## 10. 示例代码

### Python (requests)

```python
import requests

# 基础URL
BASE_URL = "http://localhost:8000/tp/api"

# 获取设备列表
response = requests.get(f"{BASE_URL}/sut-device/list", params={
    "page": 1,
    "size": 10
})
result = response.json()
print(f"设备数量: {result['data']['total']}")
print(f"设备列表: {result['data']['list']}")

# 创建测试设备
device_data = {
    "hostname": "navi31-test-01",
    "asicName": "Navi 31 GFX1100",
    "ipAddress": "10.67.80.101",
    "gpuModel": "RX 7900 XTX"
}
response = requests.post(
    f"{BASE_URL}/sut-device/",
    json=device_data
)
new_device = response.json()
print(f"创建的设备ID: {new_device['data']['id']}")

# 创建测试计划
plan_data = {
    "planName": "New Test Plan",
    "planDescription": "Performance testing",
    "sutDeviceId": 1,
    "osConfigId": 2,
    "createdBy": "admin"
}
response = requests.post(
    f"{BASE_URL}/test-plan/",
    json=plan_data
)
new_plan = response.json()
print(f"创建的测试计划ID: {new_plan['data']['id']}")
```

---

### JavaScript (Fetch)

```javascript
const BASE_URL = 'http://localhost:8000/tp/api';

// 通用请求函数
async function apiRequest(endpoint, method = 'GET', data = null) {
  const options = {
    method,
    headers: {
      'Content-Type': 'application/json'
    }
  };
  
  if (data) {
    options.body = JSON.stringify(data);
  }
  
  const response = await fetch(`${BASE_URL}${endpoint}`, options);
  return response.json();
}

// 获取设备列表
const devices = await apiRequest('/sut-device/list?page=1&size=10');
console.log('设备总数:', devices.data.total);
console.log('设备列表:', devices.data.list);

// 获取测试类型
const testTypes = await apiRequest('/test-type/list');
console.log('测试类型:', testTypes.data);

// 创建测试计划
const planData = {
  planName: 'New Test Plan',
  planDescription: 'Description',
  sutDeviceId: 1,
  osConfigId: 2,
  createdBy: 'admin'
};
const newPlan = await apiRequest('/test-plan/', 'POST', planData);
console.log('新建测试计划ID:', newPlan.data.id);
```

---

### Vue 3 Composition API

```vue
<script setup>
import { ref, onMounted } from 'vue';

const BASE_URL = 'http://localhost:8000/tp/api';

const devices = ref([]);
const loading = ref(false);
const total = ref(0);

// 获取设备列表
async function fetchDevices(page = 1, size = 10) {
  loading.value = true;
  try {
    const response = await fetch(
      `${BASE_URL}/sut-device/list?page=${page}&size=${size}`
    );
    const result = await response.json();
    
    if (result.code === 200) {
      devices.value = result.data.list;
      total.value = result.data.total;
    }
  } catch (error) {
    console.error('获取设备列表失败:', error);
  } finally {
    loading.value = false;
  }
}

onMounted(() => {
  fetchDevices();
});
</script>

<template>
  <div v-if="loading">加载中...</div>
  <div v-else>
    <p>设备总数: {{ total }}</p>
    <div v-for="device in devices" :key="device.id">
      <h3>{{ device.hostname }}</h3>
      <p>GPU: {{ device.gpuModel }}</p>
    </div>
  </div>
</template>
```

---

## 11. 快速测试

### 使用 cURL

```bash
# 1. 健康检查
curl http://localhost:8000/tp/health

# 2. 获取API端点列表
curl http://localhost:8000/tp/

# 3. 获取设备列表
curl "http://localhost:8000/tp/api/sut-device/list?page=1&size=10"

# 4. 获取测试类型
curl http://localhost:8000/tp/api/test-type/list

# 5. 创建测试设备
curl -X POST http://localhost:8000/tp/api/sut-device/ \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "test-device-01",
    "asicName": "Navi 31",
    "ipAddress": "10.67.80.100",
    "gpuModel": "RX 7900 XTX"
  }'

# 6. 获取测试计划列表
curl "http://localhost:8000/tp/api/test-plan/list?page=1&size=10"
```

### 访问 Swagger 文档

在浏览器中访问：`http://localhost:8000/tp/api/docs`

这将打开交互式 API 文档，可以直接在浏览器中测试所有 API。

---

## 12. 最佳实践

### 1. 分页处理

```javascript
// 获取所有数据（处理分页）
async function getAllDevices() {
  let allDevices = [];
  let page = 1;
  let hasMore = true;
  
  while (hasMore) {
    const response = await fetch(
      `${BASE_URL}/sut-device/list?page=${page}&size=100`
    );
    const result = await response.json();
    
    if (result.code === 200) {
      allDevices = allDevices.concat(result.data.list);
      hasMore = page * 100 < result.data.total;
      page++;
    } else {
      break;
    }
  }
  
  return allDevices;
}
```

### 2. 错误处理

```javascript
async function safeApiRequest(endpoint, options) {
  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, options);
    const result = await response.json();
    
    if (result.code !== 200) {
      throw new Error(result.data || '请求失败');
    }
    
    return result;
  } catch (error) {
    console.error('API请求失败:', error);
    // 显示用户友好的错误消息
    alert(`操作失败: ${error.message}`);
    throw error;
  }
}
```

### 3. 数据缓存

```javascript
// 简单的内存缓存
const cache = new Map();
const CACHE_TTL = 5 * 60 * 1000; // 5分钟

async function getCachedDevices() {
  const cacheKey = 'devices';
  const cached = cache.get(cacheKey);
  
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data;
  }
  
  const result = await apiRequest('/sut-device/list?page=1&size=100');
  const devices = result.data;
  cache.set(cacheKey, {
    data: devices,
    timestamp: Date.now()
  });
  
  return devices;
}
```

---

## 13. 路由架构说明

### 主路由

```
/system/              → xadmin_auth (系统认证)
/tpgen/              → xadmin_tpgen (TPGEN 管理后台API)
/tp/                 → tpgen (TPGEN 核心API)
  ├── /              → 服务首页
  ├── /health        → 健康检查
  └── /api/          → Ninja API
      ├── /docs      → Swagger文档
      ├── /sut-device/
      ├── /os-config/
      ├── /test-type/
      ├── /test-component/
      ├── /test-case/
      └── /test-plan/
```

### 数据库

- **数据库名**: tpdb
- **主机**: 10.67.167.53:5433
- **路由**: 使用 `TpgenDatabaseRouter` 自动路由到 tpdb 数据库

---

## 14. 更新日志

### v2.0 (2025-11-11)
- 🎉 重构路由结构，采用 `/tp/api/` 作为基础路径
- ✨ 添加 Swagger UI 交互式文档
- ✨ 新增健康检查和服务首页端点
- 🔧 统一响应格式
- 📝 完善 API 文档
- 🚀 优化分页参数（page/size）
- 🗑️ 支持批量删除操作

### v1.0 (2025-11-11)
- 初始版本发布
- 完整的CRUD接口
- 支持设备、OS、测试用例、测试计划管理

---

## 15. 技术支持

**API 文档**: http://localhost:8000/tp/api/docs  
**API 版本**: v2.0  
**最后更新**: 2025-11-11  
**框架**: Django + Django Ninja Extra

---

**注意事项**:
- 所有接口默认返回 JSON 格式数据
- 请求时需要设置 `Content-Type: application/json`
- 开发环境无需认证，生产环境需要配置 JWT 认证
- 建议使用 Swagger UI (`/tp/api/docs`) 进行 API 测试

