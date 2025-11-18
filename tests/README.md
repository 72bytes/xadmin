# XAdmin 测试文档

## 📋 目录结构

```
xadmin_zx/
├── pytest.ini              # Pytest 配置文件
├── .coveragerc             # 代码覆盖率配置
├── conftest.py             # 全局 fixtures 和配置
├── tests/                  # 主测试目录
│   ├── __init__.py
│   ├── test_example_api.py # API 测试示例
│   └── README.md           # 本文件
├── xadmin_auth/tests/      # 认证模块测试
├── yaml_check/tests/       # YAML 验证测试
└── ...
```

## 🚀 快速开始

### 1. 安装测试依赖

```bash
# 使用 uv 安装
uv pip install pytest pytest-django pytest-cov pytest-xdist pytest-timeout

# 或使用 pip
pip install pytest pytest-django pytest-cov pytest-xdist pytest-timeout
```

### 2. 运行测试

```bash
# 运行所有测试
pytest

# 运行指定文件的测试
pytest tests/test_example_api.py

# 运行指定类的测试
pytest tests/test_example_api.py::TestAuthAPI

# 运行指定函数的测试
pytest tests/test_example_api.py::test_simple_assertion

# 详细输出
pytest -v

# 显示打印输出
pytest -s

# 并行运行测试（需要 pytest-xdist）
pytest -n auto
```

### 3. 按标记运行测试

```bash
# 只运行单元测试
pytest -m unit

# 只运行 API 测试
pytest -m api

# 只运行慢速测试
pytest -m slow

# 跳过慢速测试
pytest -m "not slow"

# 运行多个标记
pytest -m "api or unit"
```

### 4. 代码覆盖率

```bash
# 生成覆盖率报告
pytest --cov=. --cov-report=html

# 只显示未覆盖的行
pytest --cov=. --cov-report=term-missing

# 查看 HTML 报告
open htmlcov/index.html
```

### 5. 失败重试

```bash
# 只运行上次失败的测试
pytest --lf

# 先运行失败的，再运行其他的
pytest --ff

# 失败时立即停止
pytest -x

# 最多失败2次后停止
pytest --maxfail=2
```

## 📝 编写测试

### 基本测试结构

```python
import pytest

def test_example():
    """测试函数名必须以 test_ 开头"""
    assert 1 + 1 == 2

class TestExample:
    """测试类名必须以 Test 开头"""
    
    def test_method(self):
        """测试方法名必须以 test_ 开头"""
        assert "hello".upper() == "HELLO"
```

### 使用 Fixtures

```python
@pytest.fixture
def sample_data():
    """创建测试数据"""
    return {"key": "value"}

def test_with_fixture(sample_data):
    """使用 fixture"""
    assert sample_data["key"] == "value"
```

### Django 测试

```python
import pytest

@pytest.mark.django_db
def test_user_creation():
    """需要数据库访问的测试"""
    from django.contrib.auth import get_user_model
    User = get_user_model()
    user = User.objects.create_user(username='test', password='pass')
    assert user.username == 'test'
```

### API 测试

```python
import pytest
import json

@pytest.mark.api
@pytest.mark.django_db
def test_api_endpoint(api_client):
    """测试 API 端点"""
    response = api_client.get('/api/endpoint/')
    assert response.status_code == 200
    data = response.json()
    assert data['success'] is True
```

### 参数化测试

```python
@pytest.mark.parametrize("input,expected", [
    ("hello", "HELLO"),
    ("world", "WORLD"),
])
def test_upper(input, expected):
    """参数化测试"""
    assert input.upper() == expected
```

## 🏷️ 测试标记

| 标记 | 说明 | 用法 |
|------|------|------|
| `@pytest.mark.unit` | 单元测试 | `pytest -m unit` |
| `@pytest.mark.integration` | 集成测试 | `pytest -m integration` |
| `@pytest.mark.api` | API 测试 | `pytest -m api` |
| `@pytest.mark.slow` | 慢速测试 | `pytest -m "not slow"` |
| `@pytest.mark.django_db` | 需要数据库 | 自动应用 |
| `@pytest.mark.skip` | 跳过测试 | - |
| `@pytest.mark.skipif` | 条件跳过 | - |

## 📊 覆盖率目标

- **总体覆盖率**: >= 70%
- **核心模块**: >= 80%
- **工具模块**: >= 60%

## 🔍 调试技巧

### 1. 使用 pdb 调试

```bash
# 失败时进入调试器
pytest --pdb

# 开始时就进入调试器
pytest --trace
```

### 2. 查看详细输出

```bash
# 显示所有打印输出
pytest -s

# 显示局部变量
pytest --showlocals
```

### 3. 只运行失败的测试

```bash
# 上次失败的测试
pytest --lf

# 失败优先运行
pytest --ff
```

## 📚 常用命令速查

```bash
# 运行所有测试
pytest

# 详细输出
pytest -v

# 显示打印
pytest -s

# 并行运行
pytest -n auto

# 覆盖率报告
pytest --cov=.

# 只运行标记的测试
pytest -m unit

# 跳过慢速测试
pytest -m "not slow"

# 失败时停止
pytest -x

# 重新运行失败的测试
pytest --lf

# 调试模式
pytest --pdb
```

## 📖 参考资料

- [Pytest 官方文档](https://docs.pytest.org/)
- [pytest-django 文档](https://pytest-django.readthedocs.io/)
- [Django 测试文档](https://docs.djangoproject.com/en/stable/topics/testing/)

## 💡 最佳实践

1. **测试命名**: 使用描述性的测试名称
2. **独立性**: 每个测试应该独立运行
3. **清晰性**: 使用 AAA 模式（Arrange, Act, Assert）
4. **覆盖率**: 关注核心业务逻辑的覆盖
5. **速度**: 保持测试快速运行
6. **标记**: 合理使用标记组织测试
7. **Fixtures**: 复用测试数据和配置
8. **文档**: 为测试添加清晰的文档字符串

## 🐛 常见问题

### Q: 测试数据库连接失败？
A: 确保 PostgreSQL 服务正在运行，并且配置正确。

### Q: 某些测试很慢？
A: 使用 `@pytest.mark.slow` 标记，运行时跳过：`pytest -m "not slow"`

### Q: 如何并行运行测试？
A: 安装 `pytest-xdist`，然后运行：`pytest -n auto`

### Q: 如何查看覆盖率详情？
A: 运行 `pytest --cov=. --cov-report=html`，然后打开 `htmlcov/index.html`


