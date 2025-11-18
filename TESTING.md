# XAdmin 项目测试配置

## ✅ 配置完成清单

已为项目配置以下测试文件：

- ✅ `pytest.ini` - Pytest 主配置文件
- ✅ `.coveragerc` - 代码覆盖率配置
- ✅ `conftest.py` - 全局 fixtures 和测试配置
- ✅ `tests/` - 主测试目录
- ✅ `tests/test_example_api.py` - 示例测试文件

## 📦 安装测试依赖

### 方式1：使用 uv（推荐）

```bash
uv pip install pytest pytest-django pytest-cov pytest-xdist pytest-timeout
```

### 方式2：使用 pip

```bash
source .venv/bin/activate
pip install pytest pytest-django pytest-cov pytest-xdist pytest-timeout
```

### 依赖说明

| 包 | 说明 |
|---|---|
| `pytest` | 核心测试框架 |
| `pytest-django` | Django 集成插件 |
| `pytest-cov` | 代码覆盖率插件 |
| `pytest-xdist` | 并行测试插件 |
| `pytest-timeout` | 超时控制插件 |

## 🚀 开始测试

### 1. 运行示例测试

```bash
# 确保虚拟环境已激活
source .venv/bin/activate

# 运行所有测试
pytest

# 运行示例测试
pytest tests/test_example_api.py -v
```

### 2. 查看测试覆盖率

```bash
# 生成覆盖率报告
pytest --cov=. --cov-report=html --cov-report=term

# 查看 HTML 报告（需要在 WSL 中安装浏览器或使用 Windows 浏览器打开）
# HTML 报告路径：htmlcov/index.html
```

### 3. 并行运行测试

```bash
# 自动检测 CPU 核心数并行运行
pytest -n auto
```

## 📝 创建新测试

### 1. 为特定模块创建测试

```bash
# 在模块目录下创建 tests 子目录
mkdir -p xadmin_auth/tests
touch xadmin_auth/tests/__init__.py
touch xadmin_auth/tests/test_auth_api.py
```

### 2. 编写测试用例

参考 `tests/test_example_api.py` 中的示例，编写测试：

```python
import pytest

@pytest.mark.django_db
class TestYourFeature:
    """测试你的功能"""
    
    def test_something(self, api_client):
        """测试某个功能"""
        response = api_client.get('/api/your-endpoint/')
        assert response.status_code == 200
```

## 📊 测试报告

### 覆盖率报告位置

- **终端报告**: 运行测试时直接显示
- **HTML 报告**: `htmlcov/index.html`
- **XML 报告**: `coverage.xml`（用于 CI/CD）

### 日志文件位置

- **Pytest 日志**: `logs/pytest.log`
- **覆盖率数据**: `.coverage`

## 🎯 测试目标

| 类型 | 目标覆盖率 |
|------|-----------|
| 核心业务逻辑 | >= 80% |
| API 端点 | >= 75% |
| 工具函数 | >= 70% |
| 总体目标 | >= 70% |

## 🔧 持续集成（CI）

如果配置了 CI/CD，可以在 `.github/workflows/` 或 `.gitlab-ci.yml` 中添加：

```yaml
test:
  script:
    - source .venv/bin/activate
    - pytest --cov=. --cov-report=xml --cov-report=term
  coverage: '/TOTAL.*\s+(\d+%)$/'
```

## 📖 更多信息

详细的测试文档请查看：`tests/README.md`

## 🆘 常见问题

### Q: 测试运行失败，提示数据库连接错误？
**A**: 确保 PostgreSQL 服务正在运行，并且配置正确。pytest 会自动创建测试数据库。

### Q: 如何跳过某些测试？
**A**: 使用标记：
```bash
# 跳过慢速测试
pytest -m "not slow"

# 只运行单元测试
pytest -m unit
```

### Q: 如何调试测试？
**A**: 使用 pdb 调试器：
```bash
# 失败时进入调试器
pytest --pdb

# 在测试开始时进入调试器
pytest --trace
```

### Q: 测试数据会影响开发数据库吗？
**A**: 不会。pytest-django 会自动创建独立的测试数据库（如 `test_xadmin`），测试完成后自动清理。

## 📞 获取帮助

- 查看 Pytest 文档：https://docs.pytest.org/
- 查看 pytest-django 文档：https://pytest-django.readthedocs.io/
- 查看项目测试示例：`tests/test_example_api.py`




