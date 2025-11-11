# XCase - 用例管理模块

XCase 是一个独立的 Django 应用，用于管理测试用例、用例文件和用例元数据。

## 功能特性

### 1. 用例编辑器 (Case Editor)
- **Casespace 和 Case 管理**：组织和管理测试用例的层级结构
- **文件树浏览**：可视化展示用例目录结构
- **在线编辑**：支持多种文件格式的在线编辑（JSON、YAML、Shell、Python 等）
- **文件操作**：创建、删除、重命名文件和目录
- **批量上传**：支持批量上传文件到指定目录
- **Case 上传/下载**：支持压缩包格式（.tar.gz、.zip）上传和下载整个 Case

### 2. 用例浏览器 (Case Browser)
- **用例卡片展示**：以卡片形式展示所有用例
- **标签管理**：为用例添加、删除标签，方便分类和检索
- **选项管理**：为用例添加键值对形式的选项（metadata）
- **可视化过滤**：根据标签和选项快速筛选用例

### 3. 文件管理 (File Manager)
- **安全路径检查**：防止路径遍历攻击
- **多格式支持**：自动识别文件类型并提供语法高亮
- **编码支持**：自动处理 UTF-8 和 Latin-1 编码
- **压缩包处理**：支持 tar.gz 和 zip 格式的解压和打包

## 目录结构

```
xcase/
├── __init__.py           # 模块初始化
├── apps.py               # Django App 配置
├── models.py             # 数据模型（CaseMetadata、CaseTag、CaseOption）
├── schemas.py            # API 请求/响应 Schema 定义
├── file_manager.py       # 文件系统管理器
├── api_caseeditor.py     # Case Editor API 端点
├── api_casebrowser.py    # Case Browser API 端点
├── urls.py               # URL 路由配置
├── constants.py          # 常量定义
├── exceptions.py         # 自定义异常类
├── migrations/           # 数据库迁移文件
├── tests/                # 单元测试
└── README.md             # 本文件
```

## 数据模型

### CaseMetadata
存储用例的基本元数据信息。

字段：
- `id`: 主键
- `casespace`: Casespace 名称
- `case_name`: Case 名称
- `create_time`: 创建时间
- `update_time`: 更新时间

### CaseTag
存储用例的标签信息。

字段：
- `id`: 主键
- `metadata`: 关联的 CaseMetadata（外键）
- `tag`: 标签名称
- `create_time`: 创建时间

### CaseOption
存储用例的键值对选项信息。

字段：
- `id`: 主键
- `metadata`: 关联的 CaseMetadata（外键）
- `key`: 选项键
- `value`: 选项值
- `create_time`: 创建时间
- `update_time`: 更新时间

## API 端点

### Case Editor API (`/case/caseeditor`)

#### Casespace 管理
- `GET /casespaces` - 获取所有 Casespace 列表
- `GET /casespaces/{casespace}/cases` - 获取指定 Casespace 的 Case 列表

#### 文件和目录管理
- `GET /files` - 获取文件树结构
- `GET /files/content` - 获取文件内容
- `POST /files` - 保存文件内容
- `POST /files/create` - 创建新文件
- `POST /files/folder` - 创建新目录
- `PUT /files/rename` - 重命名文件或目录
- `DELETE /files` - 删除文件或目录
- `POST /files/upload` - 批量上传文件

#### Case 管理
- `DELETE /casespaces/{casespace}/cases/{case}` - 删除 Case
- `POST /casespaces/{casespace}/upload-case` - 上传 Case 压缩包
- `GET /casespaces/{casespace}/cases/{case}/download` - 下载 Case 为压缩包

### Case Browser API (`/case/casebrowser`)

#### Case 元数据
- `GET /casespaces/{casespace}/cases` - 获取指定 Casespace 下所有 Case 的元数据
- `GET /casespaces/{casespace}/cases/{case_name}` - 获取单个 Case 的详细信息

#### 标签管理
- `POST /cases/tags` - 添加标签
- `DELETE /cases/tags` - 删除标签

#### 选项管理
- `POST /cases/options` - 添加选项
- `PUT /cases/options` - 更新选项
- `DELETE /cases/options` - 删除选项

## 配置说明

### Django Settings

在 `settings.py` 中添加：

```python
INSTALLED_APPS = [
    # ...
    'xcase',
]

# XCase 配置（可选）
XCASE_SETTINGS = {
    'STORAGE_ROOT_NAME': 'caseeditor',  # 存储根目录名称
    'MAX_FILE_SIZE': 100 * 1024 * 1024,  # 最大文件大小（100MB）
    'MAX_ARCHIVE_SIZE': 500 * 1024 * 1024,  # 最大压缩包大小（500MB）
}
```

### URL 配置

在主 `urls.py` 中添加：

```python
urlpatterns = [
    # ...
    path('case/', include('xcase.urls')),
]
```

## 安全特性

1. **路径遍历防护**：所有文件路径都会进行安全检查，防止访问存储根目录之外的文件
2. **文件类型白名单**：只允许上传指定类型的文件
3. **文件大小限制**：限制单个文件和压缩包的最大大小
4. **压缩包安全检查**：解压前检查压缩包内容，防止恶意文件

## 开发指南

### 添加新的 API 端点

1. 在 `api_caseeditor.py` 或 `api_casebrowser.py` 中定义新的路由
2. 在 `schemas.py` 中定义请求/响应 Schema（如需要）
3. 更新前端 API 服务（`web/src/apis/system/caseeditor.ts` 或 `casebrowser.ts`）

### 扩展文件类型支持

在 `constants.py` 的 `LANGUAGE_EXTENSION_MAP` 中添加新的文件扩展名映射：

```python
LANGUAGE_EXTENSION_MAP = {
    # ...
    '.new_ext': 'new_language',
}
```

### 添加自定义异常

在 `exceptions.py` 中继承 `XCaseException` 创建新的异常类：

```python
class CustomException(XCaseException):
    def __init__(self, message: str):
        super().__init__(message, code=400)
```

## 测试

运行测试：

```bash
python manage.py test xcase
```

## 依赖

- Django >= 4.2
- django-ninja-extra
- loguru
- psycopg2 (PostgreSQL)

## 许可证

[项目许可证信息]

## 维护者

[维护者信息]

