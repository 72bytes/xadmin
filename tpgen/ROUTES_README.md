# TPGEN 路由配置说明

## ✅ 路由配置完成

tpgen app 的路由已经成功创建并配置完成！

## 📁 项目结构

```
tpgen/
├── api.py          # Django Ninja API 路由定义
├── urls.py         # URL 配置
├── views.py        # Django 视图函数
├── models.py       # 数据模型
└── schemas.py      # API 数据模式
```

## 🌐 可用路由

### 主路由配置

在 `/home/xadmin/xadmin/urls.py` 中：

```python
urlpatterns = [
    path('system/', include('xadmin_auth.urls')),        # 系统认证
    path('tpgen/', include('xadmin_tpgen.urls')),        # TPGEN 管理后台 API
    path('tp/', include('tpgen.urls')),                  # TPGEN 核心 API (新增)
]
```

### TPGEN 核心 API 端点

**基础路径**: `http://{host}:{port}/tp/`

#### 基本路由

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/tp/` | TPGEN 服务首页（返回 API 端点列表）|
| GET | `/tp/health` | 健康检查 |
| GET | `/tp/api/docs` | Swagger API 文档 |
| GET | `/tp/api/openapi.json` | OpenAPI Schema |

#### 测试设备 (SUT Device) API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/tp/api/sut-device/list` | 获取测试设备列表 |
| GET | `/tp/api/sut-device/{device_id}` | 获取单个设备详情 |
| POST | `/tp/api/sut-device/` | 创建测试设备 |
| PUT | `/tp/api/sut-device/{device_id}` | 更新测试设备 |
| DELETE | `/tp/api/sut-device/{device_ids}` | 删除测试设备（支持批量）|

#### 操作系统配置 (OS Config) API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/tp/api/os-config/list` | 获取操作系统配置列表 |
| POST | `/tp/api/os-config/` | 创建操作系统配置 |

#### 测试类型 (Test Type) API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/tp/api/test-type/list` | 获取所有测试类型 |
| POST | `/tp/api/test-type/` | 创建测试类型 |

#### 测试组件 (Test Component) API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/tp/api/test-component/list` | 获取测试组件列表 |
| POST | `/tp/api/test-component/` | 创建测试组件 |

#### 测试用例 (Test Case) API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/tp/api/test-case/list` | 获取测试用例列表 |
| POST | `/tp/api/test-case/` | 创建测试用例 |

#### 测试计划 (Test Plan) API

| 方法 | 路径 | 说明 |
|------|------|------|
| GET | `/tp/api/test-plan/list` | 获取测试计划列表 |
| GET | `/tp/api/test-plan/{plan_id}` | 获取测试计划详情 |
| POST | `/tp/api/test-plan/` | 创建测试计划 |
| DELETE | `/tp/api/test-plan/{plan_ids}` | 删除测试计划（支持批量）|

## 🚀 启动服务

### 1. 激活虚拟环境

```bash
cd /home/xadmin
source .venv/bin/activate
```

### 2. 运行数据库迁移（如果还没有）

```bash
python manage.py migrate --database=tpdb
```

### 3. 启动开发服务器

```bash
python manage.py runserver 0.0.0.0:8000
```

## 🧪 测试 API

### 使用 curl 测试

#### 1. 测试服务健康状态

```bash
curl http://localhost:8000/tp/health
```

**响应示例**:
```json
{
  "status": "healthy",
  "service": "tpgen"
}
```

#### 2. 获取 API 端点列表

```bash
curl http://localhost:8000/tp/
```

#### 3. 查看 API 文档

```bash
# 在浏览器中访问
http://localhost:8000/tp/api/docs
```

#### 4. 获取测试设备列表

```bash
curl "http://localhost:8000/tp/api/sut-device/list?page=1&size=10"
```

#### 5. 创建测试设备

```bash
curl -X POST http://localhost:8000/tp/api/sut-device/ \
  -H "Content-Type: application/json" \
  -d '{
    "hostname": "test-device-01",
    "asicName": "Navi 31 GFX1100",
    "ipAddress": "192.168.1.100",
    "gpuModel": "RX 7900 XTX"
  }'
```

#### 6. 获取测试类型列表

```bash
curl http://localhost:8000/tp/api/test-type/list
```

#### 7. 获取测试计划列表

```bash
curl "http://localhost:8000/tp/api/test-plan/list?page=1&size=10"
```

### 使用 Python requests 测试

```python
import requests

# 基础 URL
BASE_URL = "http://localhost:8000/tp"

# 1. 健康检查
response = requests.get(f"{BASE_URL}/health")
print(response.json())

# 2. 获取测试设备列表
response = requests.get(f"{BASE_URL}/api/sut-device/list", params={
    "page": 1,
    "size": 10
})
print(response.json())

# 3. 创建测试设备
device_data = {
    "hostname": "test-device-01",
    "asicName": "Navi 31 GFX1100",
    "ipAddress": "192.168.1.100",
    "gpuModel": "RX 7900 XTX"
}
response = requests.post(f"{BASE_URL}/api/sut-device/", json=device_data)
print(response.json())

# 4. 获取测试类型
response = requests.get(f"{BASE_URL}/api/test-type/list")
print(response.json())
```

## 🔐 认证配置

### 当前状态

目前 API **没有启用认证**，方便开发和测试。

### 启用认证

如果需要启用认证，编辑 `/home/xadmin/tpgen/urls.py`:

```python
# 取消注释以下行以启用认证
from xadmin_auth import auth

# 将 auth=None 改为 auth=auth.TitwBaseAuth()
ninja_api = NinjaExtraAPI(
    auth=auth.TitwBaseAuth(),  # 启用认证
    title='TPGEN API', 
    urls_namespace='tpgen-api'
)
```

启用认证后，所有 API 请求需要在请求头中携带 JWT token：

```bash
curl http://localhost:8000/tp/api/sut-device/list \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## 📊 数据库配置

TPGEN 使用独立的 `tpdb` 数据库，配置在 `/home/xadmin/xadmin/settings.py`:

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "xadmin",
        # ...
    },
    "tpdb": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "tpdb",
        "USER": "amd",
        "PASSWORD": "amdyes",
        "HOST": "10.67.167.53",
        "PORT": 5433,
        # ...
    },
}

# 数据库路由器
DATABASE_ROUTERS = ["xadmin.database_router.TpgenDatabaseRouter"]
```

## 📝 API 响应格式

所有 API 使用统一的响应格式：

### 成功响应

```json
{
  "code": 200,
  "data": {
    // 实际数据
  },
  "message": "success"
}
```

### 失败响应

```json
{
  "code": 400,
  "data": "错误描述信息",
  "message": "failed"
}
```

## 🔧 常见问题

### 1. 404 Not Found

- 确认 Django 服务器正在运行
- 检查 URL 路径是否正确（注意是 `/tp/` 而不是 `/tpgen/`）
- 查看 `INSTALLED_APPS` 中是否包含 `tpgen`

### 2. 数据库连接错误

```bash
# 测试数据库连接
python manage.py check --database=tpdb

# 运行迁移
python manage.py migrate --database=tpdb
```

### 3. 查看日志

在 `settings.py` 中设置 `DEBUG = True`，所有请求和错误都会输出到控制台。

## 📚 相关文档

- TPGEN 使用指南: `/home/xadmin/tpgen/TPGEN_USAGE_GUIDE.md`
- TPGEN 设置说明: `/home/xadmin/tpgen/SETUP_TPGEN.md`
- API 文档: `/home/xadmin/tpgen/TPGEN_API_DOCUMENT.md`

## 🎯 下一步

1. **测试 API**: 使用 curl 或浏览器访问 `http://localhost:8000/tp/api/docs`
2. **导入测试数据**: 使用 `/home/xadmin/tpgen/tp_data.sql` 导入测试数据
3. **开发前端**: 根据 API 文档开发前端界面
4. **启用认证**: 在生产环境中启用认证保护 API

---

**创建时间**: 2025-11-11  
**版本**: 1.0.0  
**状态**: ✅ 已完成并验证

