# tpgen 数据库调用指南

## 核心原理

由于配置了 **数据库路由器** (`xadmin/database_router.py`)，所有 tpgen 的模型操作会**自动路由到 tpdb 数据库**，无需手动指定数据库。

---

## 1. 基础导入和查询

### 导入模型

```python
# 在任何 Python 文件中导入
from tpgen.models import (
    SutDevice,
    OsConfig,
    OsSupportedKernel,
    TestType,
    TestComponent,
    TestCase,
    TestPlan,
    TestPlanCase
)

# 或推荐方式（避免命名冲突）
from tpgen import models as tp_models
```

### 简单查询（自动使用 tpdb）

```python
# 查询所有设备 - 自动从 tpdb 读取
devices = SutDevice.objects.all()

# 查询单个对象
device = SutDevice.objects.get(id=1)

# 过滤查询
rx7900_devices = SutDevice.objects.filter(gpu_model__contains='7900')

# 统计数量
device_count = SutDevice.objects.count()

# 获取第一条
first_device = SutDevice.objects.first()
```

**重点**：不需要 `.using('tpdb')`，路由器会自动处理！

---

## 2. 在 Django Ninja API 中使用

### 示例：创建 tpgen 的 API

创建文件：`xadmin_auth/api_tpgen.py`

```python
from ninja import Router
from typing import List
from tpgen.models import SutDevice, TestPlan, OsConfig
from tpgen.schemas import (
    SutDeviceOut,
    TestPlanOut,
    TestPlanIn,
    OsConfigOut
)

router = Router()


# ============= 设备 API =============

@router.get("/devices", response=List[SutDeviceOut], summary="获取所有设备")
def list_devices(request):
    """获取所有测试设备列表"""
    devices = SutDevice.objects.all()
    return [
        SutDeviceOut(
            id=d.id,
            hostname=d.hostname,
            asicName=d.asic_name,
            ipAddress=d.ip_address,
            deviceId=d.device_id,
            revId=d.rev_id,
            gpuSeries=d.gpu_series,
            gpuModel=d.gpu_model,
            createdAt=str(d.created_at),
            updatedAt=str(d.updated_at)
        )
        for d in devices
    ]


@router.get("/devices/{device_id}", response=SutDeviceOut, summary="获取设备详情")
def get_device(request, device_id: int):
    """根据ID获取设备详情"""
    device = SutDevice.objects.get(id=device_id)
    return SutDeviceOut(
        id=device.id,
        hostname=device.hostname,
        asicName=device.asic_name,
        ipAddress=device.ip_address,
        deviceId=device.device_id,
        revId=device.rev_id,
        gpuSeries=device.gpu_series,
        gpuModel=device.gpu_model,
        createdAt=str(device.created_at),
        updatedAt=str(device.updated_at)
    )


# ============= 测试计划 API =============

@router.get("/test-plans", response=List[TestPlanOut], summary="获取所有测试计划")
def list_test_plans(request):
    """获取所有测试计划（包含关联数据）"""
    # 使用 select_related 优化查询
    plans = TestPlan.objects.select_related(
        'sut_device',
        'os_config'
    ).all()
    
    return [
        TestPlanOut(
            id=p.id,
            planName=p.plan_name,
            planDescription=p.plan_description,
            sutDeviceId=p.sut_device_id,
            osConfigId=p.os_config_id,
            createdBy=p.created_by,
            createdAt=str(p.created_at),
            updatedAt=str(p.updated_at)
        )
        for p in plans
    ]


@router.post("/test-plans", response=TestPlanOut, summary="创建测试计划")
def create_test_plan(request, data: TestPlanIn):
    """创建新的测试计划"""
    plan = TestPlan.objects.create(
        plan_name=data.planName,
        plan_description=data.planDescription,
        sut_device_id=data.sutDeviceId,
        os_config_id=data.osConfigId,
        created_by=data.createdBy or "unknown"
    )
    
    return TestPlanOut(
        id=plan.id,
        planName=plan.plan_name,
        planDescription=plan.plan_description,
        sutDeviceId=plan.sut_device_id,
        osConfigId=plan.os_config_id,
        createdBy=plan.created_by,
        createdAt=str(plan.created_at),
        updatedAt=str(plan.updated_at)
    )


@router.get("/test-plans/{plan_id}", response=dict, summary="获取测试计划详情")
def get_test_plan_detail(request, plan_id: int):
    """获取测试计划详情（包含关联的设备、OS、测试用例）"""
    plan = TestPlan.objects.select_related(
        'sut_device',
        'os_config'
    ).prefetch_related(
        'plan_cases__test_case__test_component__test_type'
    ).get(id=plan_id)
    
    # 获取关联的测试用例
    test_cases = []
    for pc in plan.plan_cases.all():
        test_cases.append({
            'id': pc.test_case.id,
            'case_name': pc.test_case.case_name,
            'component': pc.test_case.test_component.component_name,
            'test_type': pc.test_case.test_component.test_type.type_name,
            'timeout': pc.timeout,
            'config': pc.test_case.case_config
        })
    
    return {
        'id': plan.id,
        'plan_name': plan.plan_name,
        'plan_description': plan.plan_description,
        'device': {
            'id': plan.sut_device.id,
            'hostname': plan.sut_device.hostname,
            'gpu_model': plan.sut_device.gpu_model
        },
        'os_config': {
            'id': plan.os_config.id,
            'os_family': plan.os_config.os_family,
            'version': plan.os_config.version
        },
        'test_cases': test_cases,
        'created_by': plan.created_by,
        'created_at': str(plan.created_at)
    }


# ============= OS 配置 API =============

@router.get("/os-configs", response=List[OsConfigOut], summary="获取OS配置列表")
def list_os_configs(request):
    """获取所有操作系统配置"""
    configs = OsConfig.objects.all()
    return [
        OsConfigOut(
            id=c.id,
            osFamily=c.os_family,
            version=c.version,
            downloadUrl=c.download_url,
            createdAt=str(c.created_at),
            updatedAt=str(c.updated_at)
        )
        for c in configs
    ]
```

### 注册 API 路由

在 `xadmin_auth/urls.py` 中：

```python
from ninja import NinjaAPI
from xadmin_auth.api_tpgen import router as tpgen_router

api = NinjaAPI()

# 注册 tpgen 路由
api.add_router("/tpgen/", tpgen_router, tags=["Test Plan Generator"])
```

---

## 3. 在 Django 视图中使用

### 示例：传统 Django 视图

创建文件：`tpgen/views.py`

```python
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from tpgen.models import SutDevice, TestPlan


def device_list(request):
    """设备列表页面"""
    # 自动从 tpdb 读取
    devices = SutDevice.objects.all().order_by('-created_at')
    
    return render(request, 'tpgen/device_list.html', {
        'devices': devices
    })


def device_detail(request, device_id):
    """设备详情页面"""
    device = get_object_or_404(SutDevice, id=device_id)
    
    # 获取该设备的所有测试计划
    test_plans = device.test_plans.all()
    
    return render(request, 'tpgen/device_detail.html', {
        'device': device,
        'test_plans': test_plans
    })


def test_plan_json(request, plan_id):
    """返回测试计划的 JSON 数据"""
    plan = get_object_or_404(TestPlan, id=plan_id)
    
    data = {
        'id': plan.id,
        'name': plan.plan_name,
        'description': plan.plan_description,
        'device': {
            'hostname': plan.sut_device.hostname,
            'gpu_model': plan.sut_device.gpu_model
        },
        'os': {
            'family': plan.os_config.os_family,
            'version': plan.os_config.version
        }
    }
    
    return JsonResponse(data)
```

---

## 4. 复杂查询示例

### 关联查询

```python
# 查询特定 GPU 型号的所有测试计划
plans = TestPlan.objects.filter(
    sut_device__gpu_model__contains='7900'
).select_related('sut_device', 'os_config')

for plan in plans:
    print(f"{plan.plan_name}: {plan.sut_device.hostname}")
```

### 聚合查询

```python
from django.db.models import Count, Q

# 统计每个设备的测试计划数
device_stats = SutDevice.objects.annotate(
    plan_count=Count('test_plans')
).values('hostname', 'gpu_model', 'plan_count')

# 统计每个 OS 的测试计划数
os_stats = OsConfig.objects.annotate(
    plan_count=Count('test_plans')
).values('os_family', 'version', 'plan_count')
```

### 反向关系查询

```python
# 通过设备查询测试计划
device = SutDevice.objects.get(hostname='aerith-0')
plans = device.test_plans.all()  # 反向关系

# 通过测试用例查询测试计划
test_case = TestCase.objects.get(id=1)
plan_cases = test_case.plan_cases.all()  # 多对多反向关系
```

### 复杂过滤

```python
from django.db.models import Q

# 查询 Ubuntu 22.04 或 Ubuntu 24.04 的测试计划
plans = TestPlan.objects.filter(
    Q(os_config__os_family='Ubuntu', os_config__version='22.04') |
    Q(os_config__os_family='Ubuntu', os_config__version='24.04')
)

# 查询包含特定测试用例的测试计划
plans_with_case = TestPlan.objects.filter(
    plan_cases__test_case__case_name__contains='ffmpeg'
).distinct()
```

---

## 5. 在前端调用（JavaScript/Vue）

### JavaScript Fetch 示例

```javascript
// 获取所有设备
async function getDevices() {
    const response = await fetch('/api/tpgen/devices');
    const devices = await response.json();
    console.log('设备列表:', devices);
    return devices;
}

// 获取测试计划详情
async function getTestPlanDetail(planId) {
    const response = await fetch(`/api/tpgen/test-plans/${planId}`);
    const plan = await response.json();
    console.log('测试计划:', plan);
    return plan;
}

// 创建测试计划
async function createTestPlan(data) {
    const response = await fetch('/api/tpgen/test-plans', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            planName: data.name,
            planDescription: data.description,
            sutDeviceId: data.deviceId,
            osConfigId: data.osId,
            createdBy: 'admin'
        })
    });
    
    const result = await response.json();
    console.log('创建成功:', result);
    return result;
}
```

### Vue 3 组件示例

```vue
<template>
  <div class="device-list">
    <h2>测试设备列表</h2>
    
    <div v-if="loading">加载中...</div>
    
    <div v-else>
      <div v-for="device in devices" :key="device.id" class="device-card">
        <h3>{{ device.hostname }}</h3>
        <p>GPU型号: {{ device.gpuModel }}</p>
        <p>IP地址: {{ device.ipAddress }}</p>
        <button @click="viewDevice(device.id)">查看详情</button>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const devices = ref([]);
const loading = ref(true);

onMounted(async () => {
  await loadDevices();
});

async function loadDevices() {
  try {
    const response = await fetch('/api/tpgen/devices');
    devices.value = await response.json();
  } catch (error) {
    console.error('加载设备失败:', error);
  } finally {
    loading.value = false;
  }
}

function viewDevice(deviceId) {
  // 跳转到设备详情页
  window.location.href = `/tpgen/devices/${deviceId}`;
}
</script>
```

---

## 6. 性能优化技巧

### 使用 select_related（外键优化）

```python
# 不好的做法（N+1 查询问题）
plans = TestPlan.objects.all()
for plan in plans:
    print(plan.sut_device.hostname)  # 每次都查询数据库
    print(plan.os_config.os_family)  # 每次都查询数据库

# 好的做法（一次查询完成）
plans = TestPlan.objects.select_related('sut_device', 'os_config').all()
for plan in plans:
    print(plan.sut_device.hostname)  # 从缓存读取
    print(plan.os_config.os_family)  # 从缓存读取
```

### 使用 prefetch_related（多对多优化）

```python
# 优化多对多关系查询
plans = TestPlan.objects.prefetch_related(
    'plan_cases__test_case__test_component__test_type'
).all()

for plan in plans:
    for pc in plan.plan_cases.all():
        print(pc.test_case.case_name)  # 不会额外查询
```

### 只查询需要的字段

```python
# 只获取特定字段
devices = SutDevice.objects.only('hostname', 'gpu_model')

# 排除某些字段
devices = SutDevice.objects.defer('created_at', 'updated_at')
```

### 批量操作

```python
# 批量创建
devices = [
    SutDevice(hostname=f'gpu-{i}', gpu_model='RX 7900 XTX')
    for i in range(100)
]
SutDevice.objects.bulk_create(devices)

# 批量更新
SutDevice.objects.filter(gpu_model='old').update(gpu_model='new')
```

---

## 7. 常见错误和解决方案

### 错误1: DoesNotExist

```python
# 不好的做法
device = SutDevice.objects.get(id=999)  # 如果不存在会报错

# 好的做法1: 使用 try-except
try:
    device = SutDevice.objects.get(id=999)
except SutDevice.DoesNotExist:
    device = None

# 好的做法2: 使用 filter().first()
device = SutDevice.objects.filter(id=999).first()  # 返回 None 如果不存在

# 好的做法3: 在视图中使用 get_object_or_404
from django.shortcuts import get_object_or_404
device = get_object_or_404(SutDevice, id=999)  # 自动返回 404
```

### 错误2: 跨数据库外键

```python
# ❌ 错误：不能在 tpgen 模型中引用其他数据库的模型
from xadmin_db.models import SysUser

class TestPlan(models.Model):
    created_by_user = models.ForeignKey(SysUser, ...)  # 会失败！

# ✅ 正确：使用字符串字段
class TestPlan(models.Model):
    created_by = models.CharField(max_length=100)  # 存储用户名
```

---

## 8. 调试技巧

### 查看生成的 SQL

```python
import logging

# 开启 SQL 日志
logging.basicConfig()
logging.getLogger('django.db.backends').setLevel(logging.DEBUG)

# 执行查询
devices = SutDevice.objects.all()
# 会在终端打印 SQL 语句
```

### 检查数据库路由

```python
from django.db import router
from tpgen.models import SutDevice

# 检查读操作使用的数据库
print(router.db_for_read(SutDevice))  # 应该输出: tpdb

# 检查写操作使用的数据库
print(router.db_for_write(SutDevice))  # 应该输出: tpdb
```

---

## 9. 完整示例：创建一个测试计划页面

### API 端点（`xadmin_auth/api_tpgen.py`）

```python
from ninja import Router
from tpgen.models import SutDevice, OsConfig, TestPlan

router = Router()

@router.get("/create-form-data")
def get_create_form_data(request):
    """获取创建测试计划需要的下拉选项"""
    return {
        'devices': [
            {'id': d.id, 'label': f'{d.hostname} ({d.gpu_model})'}
            for d in SutDevice.objects.all()
        ],
        'os_configs': [
            {'id': c.id, 'label': f'{c.os_family} {c.version}'}
            for c in OsConfig.objects.all()
        ]
    }
```

### 前端表单（Vue 3）

```vue
<template>
  <div class="create-plan-form">
    <h2>创建测试计划</h2>
    
    <form @submit.prevent="submitForm">
      <div class="form-group">
        <label>计划名称:</label>
        <input v-model="form.planName" required />
      </div>
      
      <div class="form-group">
        <label>选择设备:</label>
        <select v-model="form.sutDeviceId" required>
          <option v-for="device in devices" :key="device.id" :value="device.id">
            {{ device.label }}
          </option>
        </select>
      </div>
      
      <div class="form-group">
        <label>选择操作系统:</label>
        <select v-model="form.osConfigId" required>
          <option v-for="os in osConfigs" :key="os.id" :value="os.id">
            {{ os.label }}
          </option>
        </select>
      </div>
      
      <button type="submit">创建</button>
    </form>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';

const form = ref({
  planName: '',
  sutDeviceId: null,
  osConfigId: null
});

const devices = ref([]);
const osConfigs = ref([]);

onMounted(async () => {
  // 加载表单数据
  const response = await fetch('/api/tpgen/create-form-data');
  const data = await response.json();
  devices.value = data.devices;
  osConfigs.value = data.os_configs;
});

async function submitForm() {
  const response = await fetch('/api/tpgen/test-plans', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      planName: form.value.planName,
      sutDeviceId: form.value.sutDeviceId,
      osConfigId: form.value.osConfigId,
      createdBy: 'current_user'
    })
  });
  
  if (response.ok) {
    alert('创建成功！');
    // 跳转到列表页
    window.location.href = '/tpgen/test-plans';
  }
}
</script>
```

---

## 总结

✅ **关键点**：
1. **无需手动指定数据库** - 路由器自动处理
2. **正常使用 Django ORM** - 就像操作普通模型一样
3. **优化查询** - 使用 `select_related` 和 `prefetch_related`
4. **避免跨数据库外键** - 使用字符串字段存储关联信息

✅ **最佳实践**：
- 导入时使用 `from tpgen.models import ...`
- API 使用 `tpgen.schemas` 进行数据验证
- 复杂查询使用 `select_related` 优化性能
- 前端通过 RESTful API 访问数据

---

**创建时间**: 2025-11-11  
**数据库**: tpdb (10.67.167.53:5433)  
**路由器**: xadmin.database_router.TpgenDatabaseRouter

