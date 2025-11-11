# tpgen API 接口文档

## 概述

**版本**: v1.0  
**基础URL**: `/api/tpgen`  
**数据库**: tpdb (10.67.167.53:5433)  
**认证方式**: JWT Token（需要在请求头中添加 `Authorization: Bearer <token>`）

---

## 目录

1. [设备管理 (SUT Devices)](#1-设备管理-sut-devices)
2. [操作系统配置 (OS Configs)](#2-操作系统配置-os-configs)
3. [操作系统内核 (OS Kernels)](#3-操作系统内核-os-kernels)
4. [测试类型 (Test Types)](#4-测试类型-test-types)
5. [测试组件 (Test Components)](#5-测试组件-test-components)
6. [测试用例 (Test Cases)](#6-测试用例-test-cases)
7. [测试计划 (Test Plans)](#7-测试计划-test-plans)
8. [测试计划用例关联 (Test Plan Cases)](#8-测试计划用例关联-test-plan-cases)

---

## 1. 设备管理 (SUT Devices)

### 1.1 获取设备列表

**接口地址**: `GET /api/tpgen/devices`

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| page | int | 否 | 页码，默认1 |
| page_size | int | 否 | 每页数量，默认20 |
| gpu_model | string | 否 | 按GPU型号过滤 |
| hostname | string | 否 | 按主机名过滤 |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 10,
    "page": 1,
    "page_size": 20,
    "items": [
      {
        "id": 1,
        "hostname": "aerith-0",
        "asicName": "VGH 163F_REV_AE",
        "ipAddress": "10.67.78.176",
        "deviceId": "163f",
        "revId": "ae",
        "gpuSeries": "AMD APU",
        "gpuModel": "AMD Custom APU 0405",
        "createdAt": "2025-11-11T10:00:00",
        "updatedAt": "2025-11-11T10:00:00"
      }
    ]
  }
}
```

**cURL 示例**:
```bash
curl -X GET "http://localhost:8000/api/tpgen/devices?page=1&page_size=20" \
  -H "Authorization: Bearer <your_token>"
```

---

### 1.2 获取设备详情

**接口地址**: `GET /api/tpgen/devices/{device_id}`

**路径参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| device_id | int | 是 | 设备ID |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "hostname": "aerith-0",
    "asicName": "VGH 163F_REV_AE",
    "ipAddress": "10.67.78.176",
    "deviceId": "163f",
    "revId": "ae",
    "gpuSeries": "AMD APU",
    "gpuModel": "AMD Custom APU 0405",
    "testPlans": [
      {
        "id": 1,
        "planName": "Aerith Media Benchmark"
      }
    ],
    "createdAt": "2025-11-11T10:00:00",
    "updatedAt": "2025-11-11T10:00:00"
  }
}
```

---

### 1.3 创建设备

**接口地址**: `POST /api/tpgen/devices`

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
  "message": "设备创建成功",
  "data": {
    "id": 11,
    "hostname": "navi31-test-01",
    "asicName": "Navi 31 GFX1100",
    "ipAddress": "10.67.80.101",
    "deviceId": "744c",
    "revId": "c8",
    "gpuSeries": "Radeon RX 7000",
    "gpuModel": "RX 7900 XTX",
    "createdAt": "2025-11-11T14:00:00",
    "updatedAt": "2025-11-11T14:00:00"
  }
}
```

---

### 1.4 更新设备

**接口地址**: `PUT /api/tpgen/devices/{device_id}`

**请求体**:
```json
{
  "hostname": "navi31-test-01-updated",
  "gpuModel": "RX 7900 XT"
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "设备更新成功",
  "data": {
    "id": 11,
    "hostname": "navi31-test-01-updated",
    "gpuModel": "RX 7900 XT",
    "updatedAt": "2025-11-11T15:00:00"
  }
}
```

---

### 1.5 删除设备

**接口地址**: `DELETE /api/tpgen/devices/{device_id}`

**响应示例**:
```json
{
  "code": 200,
  "message": "设备删除成功"
}
```

---

## 2. 操作系统配置 (OS Configs)

### 2.1 获取OS配置列表

**接口地址**: `GET /api/tpgen/os-configs`

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| os_family | string | 否 | 按OS家族过滤（Ubuntu/RHEL/Fedora等） |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "osFamily": "Ubuntu",
      "version": "22.04",
      "downloadUrl": "https://releases.ubuntu.com/22.04/",
      "createdAt": "2025-11-11T10:00:00",
      "updatedAt": "2025-11-11T10:00:00"
    },
    {
      "id": 2,
      "osFamily": "Ubuntu",
      "version": "24.04",
      "downloadUrl": "https://releases.ubuntu.com/24.04/",
      "createdAt": "2025-11-11T10:00:00",
      "updatedAt": "2025-11-11T10:00:00"
    }
  ]
}
```

---

### 2.2 获取OS配置详情

**接口地址**: `GET /api/tpgen/os-configs/{config_id}`

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "osFamily": "Ubuntu",
    "version": "22.04",
    "downloadUrl": "https://releases.ubuntu.com/22.04/",
    "supportedKernels": [
      {
        "id": 1,
        "kernelVersion": "6.2.0-39-generic"
      },
      {
        "id": 2,
        "kernelVersion": "6.5.0-14-generic"
      }
    ],
    "testPlans": [
      {
        "id": 1,
        "planName": "Ubuntu 22.04 Media Test"
      }
    ],
    "createdAt": "2025-11-11T10:00:00",
    "updatedAt": "2025-11-11T10:00:00"
  }
}
```

---

### 2.3 创建OS配置

**接口地址**: `POST /api/tpgen/os-configs`

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
  "message": "OS配置创建成功",
  "data": {
    "id": 9,
    "osFamily": "Fedora",
    "version": "39",
    "downloadUrl": "https://getfedora.org/en/workstation/download/",
    "createdAt": "2025-11-11T14:00:00",
    "updatedAt": "2025-11-11T14:00:00"
  }
}
```

---

## 3. 操作系统内核 (OS Kernels)

### 3.1 获取内核列表

**接口地址**: `GET /api/tpgen/os-kernels`

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| os_config_id | int | 否 | 按OS配置ID过滤 |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "osConfigId": 1,
      "kernelVersion": "6.2.0-39-generic",
      "osConfig": {
        "osFamily": "Ubuntu",
        "version": "22.04"
      }
    }
  ]
}
```

---

### 3.2 创建内核版本

**接口地址**: `POST /api/tpgen/os-kernels`

**请求体**:
```json
{
  "osConfigId": 1,
  "kernelVersion": "6.8.0-45-generic"
}
```

---

## 4. 测试类型 (Test Types)

### 4.1 获取测试类型列表

**接口地址**: `GET /api/tpgen/test-types`

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "typeName": "Benchmark",
      "createdAt": "2025-11-11T10:00:00",
      "updatedAt": "2025-11-11T10:00:00"
    },
    {
      "id": 2,
      "typeName": "Functional",
      "createdAt": "2025-11-11T10:00:00",
      "updatedAt": "2025-11-11T10:00:00"
    },
    {
      "id": 3,
      "typeName": "Performance",
      "createdAt": "2025-11-11T10:00:00",
      "updatedAt": "2025-11-11T10:00:00"
    }
  ]
}
```

---

### 4.2 创建测试类型

**接口地址**: `POST /api/tpgen/test-types`

**请求体**:
```json
{
  "typeName": "Stress"
}
```

---

## 5. 测试组件 (Test Components)

### 5.1 获取测试组件列表

**接口地址**: `GET /api/tpgen/test-components`

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| test_type_id | int | 否 | 按测试类型过滤 |
| category | string | 否 | 按组件分类过滤（Media/Compute/Graphics） |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "testTypeId": 1,
      "componentCategory": "Media",
      "componentName": "ffmpeg",
      "testType": {
        "id": 1,
        "typeName": "Benchmark"
      }
    },
    {
      "id": 2,
      "testTypeId": 1,
      "componentCategory": "Compute",
      "componentName": "clpeak",
      "testType": {
        "id": 1,
        "typeName": "Benchmark"
      }
    }
  ]
}
```

---

### 5.2 创建测试组件

**接口地址**: `POST /api/tpgen/test-components`

**请求体**:
```json
{
  "testTypeId": 1,
  "componentCategory": "Graphics",
  "componentName": "glmark2"
}
```

---

## 6. 测试用例 (Test Cases)

### 6.1 获取测试用例列表

**接口地址**: `GET /api/tpgen/test-cases`

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| component_id | int | 否 | 按测试组件过滤 |
| case_name | string | 否 | 按用例名称搜索 |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
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
      "testComponent": {
        "componentName": "ffmpeg",
        "componentCategory": "Media"
      },
      "createdAt": "2025-11-11T10:00:00",
      "updatedAt": "2025-11-11T10:00:00"
    }
  ]
}
```

---

### 6.2 获取测试用例详情

**接口地址**: `GET /api/tpgen/test-cases/{case_id}`

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
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
    "testComponent": {
      "id": 1,
      "componentName": "ffmpeg",
      "componentCategory": "Media",
      "testType": {
        "id": 1,
        "typeName": "Benchmark"
      }
    },
    "usedInPlans": [
      {
        "planId": 1,
        "planName": "RX 7900 XTX Media Benchmark"
      }
    ],
    "createdAt": "2025-11-11T10:00:00",
    "updatedAt": "2025-11-11T10:00:00"
  }
}
```

---

### 6.3 创建测试用例

**接口地址**: `POST /api/tpgen/test-cases`

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
  "message": "测试用例创建成功",
  "data": {
    "id": 31,
    "testComponentId": 1,
    "caseName": "H.265 8K Encoding",
    "caseConfig": {
      "resolution": "7680x4320",
      "codec": "hevc",
      "bitrate": "40M",
      "preset": "fast",
      "iterations": 50
    },
    "createdAt": "2025-11-11T14:00:00",
    "updatedAt": "2025-11-11T14:00:00"
  }
}
```

---

### 6.4 更新测试用例

**接口地址**: `PUT /api/tpgen/test-cases/{case_id}`

**请求体**:
```json
{
  "caseName": "H.265 8K Encoding (Updated)",
  "caseConfig": {
    "resolution": "7680x4320",
    "codec": "hevc",
    "bitrate": "50M",
    "preset": "medium",
    "iterations": 100
  }
}
```

---

## 7. 测试计划 (Test Plans)

### 7.1 获取测试计划列表

**接口地址**: `GET /api/tpgen/test-plans`

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| device_id | int | 否 | 按设备过滤 |
| os_config_id | int | 否 | 按OS配置过滤 |
| created_by | string | 否 | 按创建者过滤 |
| page | int | 否 | 页码 |
| page_size | int | 否 | 每页数量 |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 20,
    "page": 1,
    "page_size": 10,
    "items": [
      {
        "id": 1,
        "planName": "RX 7900 XTX Media Benchmark",
        "planDescription": "媒体编码性能测试",
        "sutDeviceId": 4,
        "osConfigId": 2,
        "device": {
          "hostname": "navi31-test-01",
          "gpuModel": "RX 7900 XTX"
        },
        "osConfig": {
          "osFamily": "Ubuntu",
          "version": "22.04"
        },
        "createdBy": "qa_team",
        "testCaseCount": 5,
        "createdAt": "2025-11-11T10:00:00",
        "updatedAt": "2025-11-11T10:00:00"
      }
    ]
  }
}
```

---

### 7.2 获取测试计划详情

**接口地址**: `GET /api/tpgen/test-plans/{plan_id}`

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "planName": "RX 7900 XTX Media Benchmark",
    "planDescription": "媒体编码性能测试",
    "sutDeviceId": 4,
    "osConfigId": 2,
    "device": {
      "id": 4,
      "hostname": "navi31-test-01",
      "gpuModel": "RX 7900 XTX",
      "ipAddress": "10.67.80.101"
    },
    "osConfig": {
      "id": 2,
      "osFamily": "Ubuntu",
      "version": "22.04",
      "downloadUrl": "https://releases.ubuntu.com/22.04/"
    },
    "testCases": [
      {
        "id": 1,
        "caseName": "H.264 4K Encoding",
        "componentName": "ffmpeg",
        "testType": "Benchmark",
        "timeout": 300,
        "config": {
          "resolution": "3840x2160",
          "codec": "h264",
          "bitrate": "20M"
        }
      },
      {
        "id": 2,
        "caseName": "H.265 4K Encoding",
        "componentName": "ffmpeg",
        "testType": "Benchmark",
        "timeout": 300,
        "config": {
          "resolution": "3840x2160",
          "codec": "hevc",
          "bitrate": "25M"
        }
      }
    ],
    "createdBy": "qa_team",
    "createdAt": "2025-11-11T10:00:00",
    "updatedAt": "2025-11-11T10:00:00"
  }
}
```

---

### 7.3 创建测试计划

**接口地址**: `POST /api/tpgen/test-plans`

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
  "message": "测试计划创建成功",
  "data": {
    "id": 21,
    "planName": "Navi 33 Graphics Performance Test",
    "planDescription": "测试 Navi 33 GPU 的图形性能",
    "sutDeviceId": 5,
    "osConfigId": 2,
    "createdBy": "admin",
    "createdAt": "2025-11-11T14:00:00",
    "updatedAt": "2025-11-11T14:00:00"
  }
}
```

---

### 7.4 更新测试计划

**接口地址**: `PUT /api/tpgen/test-plans/{plan_id}`

**请求体**:
```json
{
  "planName": "Navi 33 Complete Test Suite",
  "planDescription": "完整的性能和功能测试"
}
```

---

### 7.5 删除测试计划

**接口地址**: `DELETE /api/tpgen/test-plans/{plan_id}`

**响应示例**:
```json
{
  "code": 200,
  "message": "测试计划删除成功"
}
```

---

## 8. 测试计划用例关联 (Test Plan Cases)

### 8.1 为测试计划添加测试用例

**接口地址**: `POST /api/tpgen/test-plans/{plan_id}/cases`

**请求体**:
```json
{
  "testCaseId": 10,
  "timeout": 600
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "测试用例添加成功",
  "data": {
    "id": 45,
    "testPlanId": 1,
    "testCaseId": 10,
    "timeout": 600
  }
}
```

---

### 8.2 批量添加测试用例

**接口地址**: `POST /api/tpgen/test-plans/{plan_id}/cases/batch`

**请求体**:
```json
{
  "testCases": [
    {
      "testCaseId": 1,
      "timeout": 300
    },
    {
      "testCaseId": 2,
      "timeout": 300
    },
    {
      "testCaseId": 5,
      "timeout": 600
    }
  ]
}
```

**响应示例**:
```json
{
  "code": 200,
  "message": "批量添加成功",
  "data": {
    "added": 3,
    "skipped": 0
  }
}
```

---

### 8.3 从测试计划中移除测试用例

**接口地址**: `DELETE /api/tpgen/test-plans/{plan_id}/cases/{case_id}`

**响应示例**:
```json
{
  "code": 200,
  "message": "测试用例移除成功"
}
```

---

### 8.4 更新测试用例配置

**接口地址**: `PUT /api/tpgen/test-plan-cases/{plan_case_id}`

**请求体**:
```json
{
  "timeout": 900
}
```

---

## 9. 高级查询接口

### 9.1 获取测试计划统计

**接口地址**: `GET /api/tpgen/statistics/test-plans`

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "totalPlans": 20,
    "plansByDevice": [
      {
        "deviceName": "navi31-test-01",
        "planCount": 5
      }
    ],
    "plansByOS": [
      {
        "osFamily": "Ubuntu",
        "version": "22.04",
        "planCount": 8
      }
    ],
    "recentPlans": [
      {
        "id": 20,
        "planName": "Latest Test Plan",
        "createdAt": "2025-11-11T14:00:00"
      }
    ]
  }
}
```

---

### 9.2 搜索测试计划

**接口地址**: `GET /api/tpgen/search/test-plans`

**请求参数**:
| 参数名 | 类型 | 必填 | 说明 |
|--------|------|------|------|
| q | string | 是 | 搜索关键词 |
| fields | string | 否 | 搜索字段（name,description,device,os） |

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "planName": "RX 7900 XTX Media Benchmark",
      "device": "navi31-test-01",
      "matchField": "planName"
    }
  ]
}
```

---

### 9.3 获取设备可用性

**接口地址**: `GET /api/tpgen/devices/availability`

**响应示例**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "deviceId": 1,
      "hostname": "aerith-0",
      "isAvailable": true,
      "runningPlans": 0
    },
    {
      "deviceId": 4,
      "hostname": "navi31-test-01",
      "isAvailable": false,
      "runningPlans": 2
    }
  ]
}
```

---

## 10. 错误代码

| 错误码 | 说明 |
|--------|------|
| 200 | 成功 |
| 400 | 请求参数错误 |
| 401 | 未授权（Token无效或过期） |
| 403 | 禁止访问（权限不足） |
| 404 | 资源不存在 |
| 409 | 资源冲突（如唯一约束冲突） |
| 422 | 数据验证失败 |
| 500 | 服务器内部错误 |

**错误响应格式**:
```json
{
  "code": 400,
  "message": "参数错误",
  "errors": {
    "hostname": ["该字段为必填项"],
    "gpuModel": ["最大长度为100字符"]
  }
}
```

---

## 11. 数据模型

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

## 12. 认证说明

### 获取Token

**接口地址**: `POST /api/auth/token`

**请求体**:
```json
{
  "username": "admin",
  "password": "password123"
}
```

**响应示例**:
```json
{
  "access": "eyJ0eXAiOiJKV1QiLCJhbGc...",
  "refresh": "eyJ0eXAiOiJKV1QiLCJhbGc..."
}
```

### 使用Token

在所有需要认证的请求中，添加以下请求头：

```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
```

---

## 13. 示例代码

### Python (requests)

```python
import requests

# 基础URL
BASE_URL = "http://localhost:8000/api/tpgen"
TOKEN = "your_jwt_token"

# 设置请求头
headers = {
    "Authorization": f"Bearer {TOKEN}",
    "Content-Type": "application/json"
}

# 获取设备列表
response = requests.get(f"{BASE_URL}/devices", headers=headers)
devices = response.json()
print(f"设备数量: {len(devices['data'])}")

# 创建测试计划
plan_data = {
    "planName": "New Test Plan",
    "sutDeviceId": 1,
    "osConfigId": 2,
    "createdBy": "admin"
}
response = requests.post(
    f"{BASE_URL}/test-plans",
    json=plan_data,
    headers=headers
)
new_plan = response.json()
print(f"创建的测试计划ID: {new_plan['data']['id']}")
```

---

### JavaScript (Fetch)

```javascript
const BASE_URL = 'http://localhost:8000/api/tpgen';
const TOKEN = 'your_jwt_token';

// 通用请求函数
async function apiRequest(endpoint, method = 'GET', data = null) {
  const options = {
    method,
    headers: {
      'Authorization': `Bearer ${TOKEN}`,
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
const devices = await apiRequest('/devices');
console.log('设备列表:', devices);

// 创建测试计划
const planData = {
  planName: 'New Test Plan',
  sutDeviceId: 1,
  osConfigId: 2,
  createdBy: 'admin'
};
const newPlan = await apiRequest('/test-plans', 'POST', planData);
console.log('新建测试计划:', newPlan);
```

---

### Vue 3 Composition API

```vue
<script setup>
import { ref, onMounted } from 'vue';

const BASE_URL = 'http://localhost:8000/api/tpgen';
const token = localStorage.getItem('token');

const devices = ref([]);
const loading = ref(false);

// 获取设备列表
async function fetchDevices() {
  loading.value = true;
  try {
    const response = await fetch(`${BASE_URL}/devices`, {
      headers: {
        'Authorization': `Bearer ${token}`
      }
    });
    const result = await response.json();
    devices.value = result.data;
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
```

---

## 14. 最佳实践

### 1. 分页处理

```javascript
// 获取所有数据（处理分页）
async function getAllDevices() {
  let allDevices = [];
  let page = 1;
  let hasMore = true;
  
  while (hasMore) {
    const response = await fetch(
      `${BASE_URL}/devices?page=${page}&page_size=100`
    );
    const result = await response.json();
    
    allDevices = allDevices.concat(result.data.items);
    hasMore = result.data.page * result.data.page_size < result.data.total;
    page++;
  }
  
  return allDevices;
}
```

### 2. 错误处理

```javascript
async function safeApiRequest(endpoint, options) {
  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, options);
    
    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.message);
    }
    
    return response.json();
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
  
  const devices = await apiRequest('/devices');
  cache.set(cacheKey, {
    data: devices,
    timestamp: Date.now()
  });
  
  return devices;
}
```

---

## 15. 更新日志

### v1.0 (2025-11-11)
- 初始版本发布
- 完整的CRUD接口
- 支持设备、OS、测试用例、测试计划管理
- JWT认证支持

---

## 16. 联系方式

**技术支持**: qa_team@example.com  
**API版本**: v1.0  
**最后更新**: 2025-11-11

---

**注意**: 所有接口默认返回JSON格式数据，请求时需要设置 `Content-Type: application/json`

