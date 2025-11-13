"""
测试 yaml_check.line_finder 模块
验证行号查找功能
"""

import pytest
from yaml_check.line_finder import YamlLineFinder


class TestFindKeyLineNumber:
    """测试 YamlLineFinder.find_key_line_number 方法"""
    
    def test_find_simple_key(self):
        """测试查找简单键"""
        yaml_text = """
metadata:
  version: 1.0
hardware:
  cpu: Test CPU
  gpu: Test GPU
"""
        # 查找 hardware.cpu
        line_num = YamlLineFinder.find_key_line_number(yaml_text, 'hardware.cpu')
        assert line_num == 5  # cpu 在第5行
        
        # 查找 hardware.gpu
        line_num = YamlLineFinder.find_key_line_number(yaml_text, 'hardware.gpu')
        assert line_num == 6  # gpu 在第6行
    
    def test_find_nested_key(self):
        """测试查找嵌套键"""
        yaml_text = """
hardware:
  machines:
    - id: 1
      name: Machine1
      specs:
        motherboard: ASUS
        cpu: Intel
"""
        line_num = YamlLineFinder.find_key_line_number(yaml_text, 'hardware.machines')
        assert line_num == 3  # machines 在第3行
    
    def test_find_top_level_key(self):
        """测试查找顶层键"""
        yaml_text = """
metadata:
  version: 1.0
hardware:
  cpu: Test
"""
        line_num = YamlLineFinder.find_key_line_number(yaml_text, 'metadata')
        assert line_num == 2  # metadata 在第2行
        
        line_num = YamlLineFinder.find_key_line_number(yaml_text, 'hardware')
        assert line_num == 4  # hardware 在第4行
    
    def test_key_not_found(self):
        """测试键不存在的情况"""
        yaml_text = """
hardware:
  cpu: Test
"""
        line_num = YamlLineFinder.find_key_line_number(yaml_text, 'nonexistent.key')
        assert line_num == -1  # 未找到返回 -1
    
    def test_empty_yaml(self):
        """测试空 YAML 文本"""
        line_num = YamlLineFinder.find_key_line_number('', 'any.key')
        assert line_num == -1
    
    def test_key_with_special_characters(self):
        """测试包含特殊字符的键"""
        yaml_text = """
environment:
  os-config: Ubuntu
  kernel_version: 6.5.0
"""
        # 注意：YAML 中的 - 和 _ 在键名中是有效的
        line_num = YamlLineFinder.find_key_line_number(yaml_text, 'environment.os-config')
        assert line_num > 0
    
    def test_multiple_occurrences(self):
        """测试键多次出现的情况（返回第一次出现）"""
        yaml_text = """
section1:
  cpu: Intel
section2:
  cpu: AMD
"""
        line_num = YamlLineFinder.find_key_line_number(yaml_text, 'section1.cpu')
        assert line_num == 3  # 第一个 cpu
        
        line_num = YamlLineFinder.find_key_line_number(yaml_text, 'section2.cpu')
        assert line_num == 5  # 第二个 cpu
    
    def test_array_notation(self):
        """测试数组表示法"""
        yaml_text = """
hardware:
  machines:
    - id: 1
      name: Machine1
    - id: 2
      name: Machine2
"""
        line_num = YamlLineFinder.find_key_line_number(yaml_text, 'hardware.machines')
        assert line_num == 3


class TestExtractKeyFromError:
    """测试 extract_key_from_error 函数"""
    
    def test_extract_from_e001_error(self):
        """测试从 E001 错误中提取键"""
        error_msg = "E001 Missing required key: [hardware.cpu]"
        key = YamlLineFinder.extract_key_from_error(error_msg)
        assert key == 'hardware.cpu'
    
    def test_extract_from_e002_error(self):
        """测试从 E002 错误中提取键"""
        error_msg = "E002 Unsupported: empty value for [hardware.machines]"
        key = YamlLineFinder.extract_key_from_error(error_msg)
        assert key == 'hardware.machines'
    
    def test_extract_from_e101_error(self):
        """测试从 E101 错误中提取键"""
        error_msg = "E101 Type error: [id] expected int but got str"
        key = YamlLineFinder.extract_key_from_error(error_msg)
        assert key == 'id'
    
    def test_extract_from_e102_error(self):
        """测试从 E102 错误中提取键"""
        error_msg = "E102 Value not in whitelist: [hardware.cpu] = 'Unknown CPU'"
        key = YamlLineFinder.extract_key_from_error(error_msg)
        assert key == 'hardware.cpu'
    
    def test_no_brackets_returns_none(self):
        """测试没有方括号的错误消息"""
        error_msg = "Some error without brackets"
        key = YamlLineFinder.extract_key_from_error(error_msg)
        assert key is None
    
    def test_empty_brackets_returns_none(self):
        """测试空方括号"""
        error_msg = "Error with empty brackets: []"
        key = YamlLineFinder.extract_key_from_error(error_msg)
        assert key is None or key == ''
    
    def test_multiple_brackets_returns_first(self):
        """测试多个方括号（返回第一个）"""
        error_msg = "Error [key1] and [key2]"
        key = YamlLineFinder.extract_key_from_error(error_msg)
        assert key == 'key1'
    
    def test_nested_path_extraction(self):
        """测试提取嵌套路径"""
        error_msg = "E001 Missing: [environment.os.deployment]"
        key = YamlLineFinder.extract_key_from_error(error_msg)
        assert key == 'environment.os.deployment'


@pytest.mark.parametrize("yaml_text,key_path,expected_found", [
    # 正常情况
    ("hardware:\n  cpu: Test", "hardware.cpu", True),
    ("metadata:\n  version: 1.0", "metadata.version", True),
    # 键不存在
    ("hardware:\n  cpu: Test", "hardware.gpu", False),
    # 空文本
    ("", "any.key", False),
])
def test_find_key_parametrized(yaml_text, key_path, expected_found):
    """参数化测试：查找键"""
    line_num = YamlLineFinder.find_key_line_number(yaml_text, key_path)
    if expected_found:
        assert line_num > 0
    else:
        assert line_num == -1


@pytest.mark.parametrize("error_msg,expected_key", [
    ("E001 Missing: [hardware.cpu]", "hardware.cpu"),
    ("E002 Empty: [machines]", "machines"),
    ("E101 Type: [id] wrong", "id"),
    ("E102 Range: [os.type] invalid", "os.type"),
    ("No brackets here", None),
])
def test_extract_key_parametrized(error_msg, expected_key):
    """参数化测试：提取错误键"""
    key = YamlLineFinder.extract_key_from_error(error_msg)
    assert key == expected_key

