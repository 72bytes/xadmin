# XAdmin

一个基于 Django + Django Ninja 构建的现代化后台管理系统，提供完整的用户、角色、权限、菜单管理功能。

## ✨ 功能特性

- 🔐 **用户管理** - 完整的用户 CRUD 操作，支持头像上传
- 👥 **角色权限管理** - 灵活的角色权限体系，支持数据权限控制
- 📋 **菜单管理** - 动态菜单配置，支持多级菜单和路由管理
- 🏢 **部门管理** - 树形部门结构，支持部门数据隔离
- 📚 **数据字典** - 系统配置数据统一管理
- 🔑 **JWT 认证** - 基于 JWT 的安全认证机制
- ⚡ **Redis 缓存** - 高性能数据缓存支持
- 📖 **API 文档** - 自动生成的交互式 API 文档 (Swagger/ReDoc)

## 🛠 技术栈

- **Python** 3.14+
- **Django** 5.2.7 - Web 框架
- **Django Ninja** 1.4.5 - 高性能 API 框架
- **Django Ninja Extra** 0.30.2 - 增强功能
- **Django Ninja JWT** 5.4.0 - JWT 认证
- **PostgreSQL** - 主数据库
- **Redis** 7.0.1 - 缓存和会话存储
- **Gunicorn** 23.0.0 - WSGI HTTP 服务器
- **Loguru** 0.7.3 - 日志管理

## 📁 项目结构

```
xadmin/
├── xadmin/                 # 核心配置模块
│   ├── settings.py        # Django 配置文件
│   ├── urls.py            # 主路由配置
│   ├── wsgi.py            # WSGI 配置
│   ├── asgi.py            # ASGI 配置
│   └── logru_config.py    # 日志配置
├── xauth/                 # 认证和权限模块
│   ├── api_auth.py        # 认证 API
│   ├── api_user.py        # 用户管理 API
│   ├── api_role.py        # 角色管理 API
│   ├── api_menu.py        # 菜单管理 API
│   ├── api_dept.py        # 部门管理 API
│   ├── api_dict.py        # 字典管理 API
│   ├── api_dict_item.py   # 字典项管理 API
│   ├── api_option.py      # 选项 API
│   ├── api_common.py      # 通用 API
│   ├── auth.py            # 认证逻辑
│   └── urls.py            # 认证模块路由
├── xdb/                   # 数据库模型模块
│   ├── models.py          # 数据模型定义
│   ├── schemas.py         # Pydantic 模式
│   ├── signals.py         # 数据库信号处理
│   └── migrations/        # 数据库迁移文件
├── xutils/                # 工具模块
│   └── utils.py           # 通用工具函数
├── manage.py              # Django 管理脚本
├── gunicorn.conf.py       # Gunicorn 配置
├── startserver.sh         # 启动脚本
├── pyproject.toml         # 项目依赖配置
└── requirements.txt       # Python 依赖列表
```

## 🚀 快速开始

### 环境要求

- Python 3.14 或更高版本
- PostgreSQL 数据库
- Redis 服务器

### 1. 克隆项目

```bash
git clone <repository-url>
cd xadmin
```

### 2. 安装依赖

```bash
uv sync
```

### 3. 配置数据库

编辑 `xadmin/settings.py`，配置 PostgreSQL 连接信息：

```python
DATABASES = {
    "default": {
        "ENGINE": "django.db.backends.postgresql",
        "NAME": "xadmin",        # 数据库名称
        "USER": "username",           # 数据库用户名
        "PASSWORD": "password",    # 数据库密码
        "HOST": "127.0.0.1",     # 数据库主机
        "PORT": 5432,            # 数据库端口
        "OPTIONS": {
            "options": "-c TimeZone=Asia/Shanghai",
        },
    }
}
```

### 4. 配置 Redis

确保 Redis 服务正在运行，并根据需要修改配置：

```python
CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": "redis://127.0.0.1:6379/1",
        "OPTIONS": {
            "PASSWORD": "yourpass",
        },
    }
}
```

### 5. 运行数据库迁移

```bash
python manage.py migrate
```

### 6. 创建超级用户（可选）

```bash
python manage.py createsuperuser
```

### 7. 启动开发服务器

开发环境：

```bash
python manage.py runserver
```

生产环境（使用 Gunicorn）：

```bash
./startserver.sh
# 或
gunicorn xadmin.wsgi:application -c gunicorn.conf.py
```

服务将在 `http://0.0.0.0:9527` 启动（生产模式）或 `http://127.0.0.1:8000`（开发模式）。

## 📖 API 文档

启动服务后，可以访问以下地址查看 API 文档：

- **Swagger UI** (交互式文档): http://127.0.0.1:8000/system/docs
- **ReDoc** (美观的只读文档): http://127.0.0.1:8000/system/redoc
- **OpenAPI Schema** (JSON): http://127.0.0.1:8000/system/openapi.json

### API 认证

大部分 API 需要 JWT 认证。使用流程：

1. 调用登录 API 获取 access_token
2. 在后续请求的 Header 中添加：`Authorization: Bearer <access_token>`

Token 有效期：30 天（可在 `settings.py` 中配置）

## ⚙️ 配置说明

### 数据库配置

项目使用 PostgreSQL 作为主数据库，支持以下时区配置：

```python
TIME_ZONE = "Asia/Shanghai"
USE_TZ = True
```

### Redis 配置

Redis 用于：
- 缓存数据（部门树、菜单树等）
- 会话存储
- 其他临时数据

配置位置：`xadmin/settings.py`

```python
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_PASSWORD = "yourpass"
REDIS_DB = 0
```

### JWT 配置

JWT Token 配置：

```python
NINJA_JWT = {
    "ACCESS_TOKEN_LIFETIME": timedelta(days=30),
}
```

### 数据权限范围

系统支持以下数据权限范围：

1. 全部数据权限
2. 本部门及以下数据权限
3. 本部门数据权限
4. 仅本人数据权限
5. 自定义数据权限

### 日志配置

日志文件位置：`/var/log/xadmin.log`

- 日志轮转：50MB
- 保留数量：10 个文件
- 压缩格式：zip

## 🚢 部署说明

### Gunicorn 配置

生产环境推荐使用 Gunicorn 部署，配置文件 `gunicorn.conf.py`：

```python
bind = '0.0.0.0:9527'      # 监听地址和端口
workers = 3                 # 工作进程数
timeout = 120               # 请求超时时间（秒）
reload = False              # 生产环境不要启用自动重载
```

### 生产环境检查清单

- [ ] 修改 `SECRET_KEY` 为随机生成的安全密钥
- [ ] 设置 `DEBUG = False`
- [ ] 配置 `ALLOWED_HOSTS` 为实际域名
- [ ] 使用强密码配置数据库和 Redis
- [ ] 配置 HTTPS（推荐使用 Nginx 反向代理）
- [ ] 配置防火墙规则
- [ ] 设置日志轮转和监控
- [ ] 配置数据库备份策略

### Nginx 反向代理示例

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://127.0.0.1:9527;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static/ {
        alias /path/to/your/static/files/;
    }

    location /media/ {
        alias /path/to/your/media/files/;
    }
}
```

## 📝 主要模块说明

### 用户模块 (api_user.py)

- 用户列表查询（支持分页、搜索）
- 用户信息 CRUD
- 用户头像上传和获取
- 用户密码修改

### 角色模块 (api_role.py)

- 角色管理 CRUD
- 角色权限分配
- 数据权限范围设置

### 菜单模块 (api_menu.py)

- 菜单树形结构管理
- 路由配置
- 权限关联

### 部门模块 (api_dept.py)

- 部门树形结构管理
- 部门人员管理
- 支持缓存优化

### 字典模块 (api_dict.py / api_dict_item.py)

- 系统字典类型管理
- 字典数据项管理
- 支持字典数据导出

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！
