# YAML Check 模块测试文档

## 📋 测试文件说明

| 文件 | 测试内容 | 测试数量 |
|------|----------|----------|
| `test_config.py` | 配置常量验证 | 15+ 测试 |
| `test_line_finder.py` | 行号查找功能 | 25+ 测试 |
| `test_logger.py` | 日志配置 | 15+ 测试 |
| `test_validator.py` | YAML 验证器核心功能 | 40+ 测试 |
| `test_views.py` | API 端点测试 | 20+ 测试 |

## 🚀 运行测试

### 1. 运行所有 yaml_check 测试

```bash
# 激活虚拟环境
source .venv/bin/activate

# 运行所有测试
pytest yaml_check/tests/ -v

# 带覆盖率运行
pytest yaml_check/tests/ --cov=yaml_check --cov-report=term-missing
```

### 2. 运行特定测试文件

```bash
# 只测试配置
pytest yaml_check/tests/test_config.py -v

# 只测试验证器
pytest yaml_check/tests/test_validator.py -v

# 只测试 API
pytest yaml_check/tests/test_views.py -v
```

### 3. 运行特定测试类

```bash
# 测试 ValidationHelper
pytest yaml_check/tests/test_validator.py::TestValidationHelper -v

# 测试 YamlValidator
pytest yaml_check/tests/test_validator.py::TestYamlValidator -v
```

### 4. 运行特定测试函数

```bash
# 测试单个函数
pytest yaml_check/tests/test_config.py::test_required_keys_individual -v
```

## 📊 测试覆盖率目标

| 模块 | 目标覆盖率 | 说明 |
|------|-----------|------|
| `config.py` | 100% | 配置文件应该完全覆盖 |
| `line_finder.py` | >= 90% | 工具函数高覆盖率 |
| `logger.py` | >= 80% | 日志配置核心部分 |
| `validator.py` | >= 85% | 核心验证逻辑 |
| `views.py` | >= 75% | API 端点主要流程 |

## 🏷️ 测试标记

### 使用标记过滤测试

```bash
# 跳过慢速测试
pytest yaml_check/tests/ -m "not slow"

# 只运行单元测试
pytest yaml_check/tests/ -m unit

# 只运行 API 测试
pytest yaml_check/tests/ -m api
```

### 测试标记说明

- `@pytest.mark.unit` - 单元测试
- `@pytest.mark.integration` - 集成测试
- `@pytest.mark.slow` - 慢速测试（> 1秒）
- `@pytest.mark.django_db` - 需要数据库

## 🎯 测试重点

### 1. test_config.py
- ✅ 验证所有配置常量存在
- ✅ 验证配置格式正确
- ✅ 验证配置内容符合预期

### 2. test_line_finder.py
- ✅ 测试简单键查找
- ✅ 测试嵌套键查找
- ✅ 测试数组键查找
- ✅ 测试错误键提取
- ✅ 测试边界情况

### 3. test_logger.py
- ✅ 验证 logger 实例正确配置
- ✅ 测试各级别日志记录
- ✅ 测试日志文件创建
- ✅ 测试异常日志
- ✅ 测试性能

### 4. test_validator.py（核心）
- ✅ 测试 E001：必需键验证
- ✅ 测试 E002：空值验证
- ✅ 测试 E101：类型验证
- ✅ 测试 E102：范围验证
- ✅ 测试 JSON 扁平化
- ✅ 测试 IPv4 地址验证
- ✅ 测试完整验证流程

### 5. test_views.py
- ✅ 测试 API 端点存在
- ✅ 测试有效数据验证
- ✅ 测试无效数据验证
- ✅ 测试认证和授权
- ✅ 测试错误处理
- ✅ 测试边界情况
- ✅ 测试性能

## 🐛 调试测试

### 显示详细输出

```bash
# 显示 print 输出
pytest yaml_check/tests/ -s

# 显示局部变量
pytest yaml_check/tests/ --showlocals

# 失败时进入调试器
pytest yaml_check/tests/ --pdb
```

### 只运行失败的测试

```bash
# 重新运行上次失败的测试
pytest yaml_check/tests/ --lf

# 失败优先运行
pytest yaml_check/tests/ --ff
```

## 📈 生成测试报告

### HTML 覆盖率报告

```bash
# 生成 HTML 报告
pytest yaml_check/tests/ --cov=yaml_check --cov-report=html

# 查看报告（WSL 中）
# 报告位置：htmlcov/index.html
```

### 终端覆盖率报告

```bash
# 详细终端报告
pytest yaml_check/tests/ --cov=yaml_check --cov-report=term-missing

# 简洁报告
pytest yaml_check/tests/ --cov=yaml_check --cov-report=term
```

## 💡 最佳实践

### 1. 编写新测试

```python
import pytest

def test_new_feature():
    """测试新功能"""
    # Arrange - 准备测试数据
    data = {'key': 'value'}
    
    # Act - 执行测试
    result = some_function(data)
    
    # Assert - 验证结果
    assert result == expected_value
```

### 2. 使用 Fixtures

```python
@pytest.fixture
def sample_data():
    """共享测试数据"""
    return {'test': 'data'}

def test_with_fixture(sample_data):
    """使用 fixture"""
    assert sample_data['test'] == 'data'
```

### 3. 参数化测试

```python
@pytest.mark.parametrize("input,expected", [
    (1, 2),
    (2, 4),
    (3, 6),
])
def test_multiply_by_two(input, expected):
    """参数化测试"""
    assert input * 2 == expected
```

## 🔍 常见问题

### Q: 测试失败，提示数据库错误？
**A**: 确保使用 `@pytest.mark.django_db` 装饰器：
```python
@pytest.mark.django_db
def test_my_function():
    # 测试代码
```

### Q: 如何跳过某个测试？
**A**: 使用 `skip` 装饰器：
```python
@pytest.mark.skip(reason="功能未实现")
def test_future_feature():
    pass
```

### Q: 如何测试异常？
**A**: 使用 `pytest.raises`：
```python
def test_exception():
    with pytest.raises(ValueError):
        raise ValueError("Test")
```

### Q: 测试运行很慢？
**A**: 使用并行运行：
```bash
pytest yaml_check/tests/ -n auto
```

## 📚 参考资料

- [Pytest 官方文档](https://docs.pytest.org/)
- [pytest-django 文档](https://pytest-django.readthedocs.io/)
- [项目测试指南](../../tests/README.md)

## 🎓 下一步

1. ✅ 运行所有测试确保通过
2. ✅ 查看覆盖率报告
3. ✅ 为新功能添加测试
4. ✅ 定期运行测试确保代码质量

