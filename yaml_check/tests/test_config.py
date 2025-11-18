"""
测试 yaml_check.config 模块
验证配置常量的正确性
"""

import pytest
from yaml_check import config


class TestConfig:
    """配置常量测试类"""
    
    def test_required_root_keys_exists(self):
        """测试必需根键配置存在"""
        assert hasattr(config, 'REQUIRED_ROOT_KEYS')
        assert isinstance(config.REQUIRED_ROOT_KEYS, list)
    
    def test_required_root_keys_not_empty(self):
        """测试必需根键配置非空"""
        assert len(config.REQUIRED_ROOT_KEYS) > 0
    
    def test_required_root_keys_format(self):
        """测试必需根键格式正确"""
        for key in config.REQUIRED_ROOT_KEYS:
            assert isinstance(key, str)
            assert '.' in key  # 应该是点分隔的路径
            assert key.strip() == key  # 不应有前后空格
    
    # def test_required_root_keys_content(self):
    #     """测试必需根键内容"""
    #     assert 'hardware.cpu' in config.REQUIRED_ROOT_KEYS
    #     assert 'hardware.gpu' in config.REQUIRED_ROOT_KEYS
    
    def test_value_type_config_exists(self):
        """测试值类型配置存在"""
        assert hasattr(config, 'VALUE_TYPE_CONFIG')
        assert isinstance(config.VALUE_TYPE_CONFIG, dict)
    
    def test_value_type_config_format(self):
        """测试值类型配置格式"""
        valid_types = ['int', 'float', 'str', 'bool', 'IPv4']
        
        for key, value_type in config.VALUE_TYPE_CONFIG.items():
            assert isinstance(key, str)
            assert isinstance(value_type, str)
            assert value_type in valid_types, f"Invalid type: {value_type}"
    
    def test_value_type_config_content(self):
        """测试值类型配置内容"""
        assert 'id' in config.VALUE_TYPE_CONFIG
        assert config.VALUE_TYPE_CONFIG['id'] == 'int'
        assert 'order' in config.VALUE_TYPE_CONFIG
        assert config.VALUE_TYPE_CONFIG['order'] == 'int'
        assert 'ipAddress' in config.VALUE_TYPE_CONFIG
        assert config.VALUE_TYPE_CONFIG['ipAddress'] == 'IPv4'
    
    def test_value_range_config_exists(self):
        """测试值范围配置存在"""
        assert hasattr(config, 'VALUE_RANGE_CONFIG')
        assert isinstance(config.VALUE_RANGE_CONFIG, dict)
    
    def test_value_range_config_format(self):
        """测试值范围配置格式"""
        for key, values in config.VALUE_RANGE_CONFIG.items():
            assert isinstance(key, str)
            assert isinstance(values, list)
            assert len(values) > 0  # 白名单不应为空
            for value in values:
                assert isinstance(value, str)
    
    # def test_value_range_config_content(self):
    #     """测试值范围配置内容"""
    #     assert 'hardware.cpu' in config.VALUE_RANGE_CONFIG
    #     cpu_values = config.VALUE_RANGE_CONFIG['hardware.cpu']
    #     assert 'Ryzen Threadripper' in cpu_values
    #     assert 'Ryzen 7' in cpu_values
    #     assert 'Ryzen 9' in cpu_values
    #     assert 'EPYC' in cpu_values


# @pytest.mark.parametrize("key", [
#     'hardware.cpu',
#     'hardware.gpu',
# ])
# def test_required_keys_individual(key):
#     """参数化测试：验证每个必需键"""
#     assert key in config.REQUIRED_ROOT_KEYS


@pytest.mark.parametrize("key,expected_type", [
    ('id', 'int'),
    ('order', 'int'),
    ('ipAddress', 'IPv4'),
])
def test_value_types_individual(key, expected_type):
    """参数化测试：验证每个类型配置"""
    assert key in config.VALUE_TYPE_CONFIG
    assert config.VALUE_TYPE_CONFIG[key] == expected_type

