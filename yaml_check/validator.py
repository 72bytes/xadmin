

from .logger import yaml_check_logger
from ipaddress import IPv4Address, AddressValueError

class YamlHelper:
    @staticmethod
    def is_empty(value):
        """检查值是否为空"""
        if value is None:
            return True
        if isinstance(value, str) and value.strip() == '':
            return True
        if isinstance(value, (list, dict)) and len(value) == 0:
            return True
        return False
    
    @staticmethod
    def get_nested_value(obj, path):
        """使用点号路径获取嵌套值"""
        keys = path.split('.')
        current = obj
        for key in keys:
            if isinstance(current, dict) and key in current:
                current = current[key]
            else:
                return None
        return current
    
    @staticmethod
    def has_key(obj, key):
        """检查对象中是否存在某个键（任意深度）"""
        if not isinstance(obj, dict):
            return False
        if key in obj:
            return True
        for k, v in obj.items():
            if isinstance(v, dict) and YamlHelper.has_key(v, key):
                return True
        return False
    
    @staticmethod
    def get_value_type(value):
        """获取值的类型"""
        if value is None:
            return 'null'
        if isinstance(value, bool):
            return 'boolean'
        if isinstance(value, int):
            return 'int'
        if isinstance(value, float):
            return 'number'
        if isinstance(value, str):
            return 'string'
        if isinstance(value, list):
            return 'array'
        if isinstance(value, dict):
            return 'object'
        return 'unknown'

"""
YAML 验证器主类

"""

from .config import (
    REQUIRED_ROOT_KEYS,
    VALUE_TYPE_CONFIG,
    VALUE_RANGE_CONFIG
)

class YamlValidator:
    
    def __init__(self):
        self.helper = YamlHelper()
        # 将扁平化数据作为类属性
        self.flattened_data = {}
        self.original_data = {}
    
    def _flatten_json(self, data, parent_key=''):
        """
        递归扁平化 JSON 数据
        
        示例:
        输入: {"hardware": {"cpu": "Intel", "machines": []}}
        输出: {"hardware.cpu": "Intel", "hardware.machines": []}
        """
        items = []
        
        if isinstance(data, dict):
            for k, v in data.items():
                new_key = f"{parent_key}.{k}" if parent_key else k
                if isinstance(v, dict):
                    items.extend(self._flatten_json(v, new_key).items())
                else:
                    items.append((new_key, v))
        else:
            items.append((parent_key, data))
        
        return dict(items)
    
    def validate_required_root_keys(self):
        """E001: 验证必需的根键"""
        yaml_check_logger.debug(f"开始 E001 验证：检查必需键 {REQUIRED_ROOT_KEYS}")
        
        for key in REQUIRED_ROOT_KEYS:
            exists = False
            if '.' in key:
                # 从扁平化数据中直接查找
                exists = key in self.flattened_data
                if not exists:
                    # 如果扁平化数据中没有，也检查原始数据
                    value = self.helper.get_nested_value(self.original_data, key)
                    exists = value is not None
            else:
                # 检查扁平化数据中是否有以该键开头的项
                exists = any(k == key or k.startswith(key + '.') for k in self.flattened_data.keys())
                if not exists:
                    # 如果扁平化数据中没有，也检查原始数据
                    exists = self.helper.has_key(self.original_data, key)
            
            if not exists:
                yaml_check_logger.warning(f"E001: 缺少必需键 [{key}]")
                return {
                    'valid': False,
                    'error_code': 'E001',
                    'error_message': f'E001 Unsupported: missing mandatory key [{key}]'
                }
        
        yaml_check_logger.info("✅ E001 验证通过：所有必需键存在")
        return {'valid': True, 'error_code': '0', 'error_message': 'OK'}
    
    def validate_mandatory_non_empty_keys(self):
        """
        E002: 验证不能为空的键
        直接从 self.flattened_data 检查所有字段是否为空
        """
        import json
        from datetime import datetime
        
        yaml_check_logger.debug("开始 E002 验证：检查空值")
        
        # 调试模式开关（生产环境设为 False）
        DEBUG_MODE = False
        
        # 调试模式：输出和保存数据
        if DEBUG_MODE:
            formatted_data = json.dumps(self.original_data, indent=2, ensure_ascii=False)
            yaml_check_logger.debug("=" * 60)
            yaml_check_logger.debug("开始验证 yaml_data")
            yaml_check_logger.debug(f"yaml_data:\n{formatted_data}")
            yaml_check_logger.debug("=" * 60)
            
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"/tmp/yaml_data_{timestamp}.json"
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(formatted_data)
            yaml_check_logger.debug(f"✅ yaml_data 已保存到: {filename}")
        
        yaml_check_logger.debug(f"扁平化后共 {len(self.flattened_data)} 个字段")
        
        if DEBUG_MODE:
            yaml_check_logger.debug("扁平化后的数据:")
            for key, value in self.flattened_data.items():
                yaml_check_logger.debug(f"  {key}: {value} (type: {type(value).__name__})")
        
        # 检查所有字段是否为空
        for key, value in self.flattened_data.items():
            # 字段不存在
            if value is None:
                yaml_check_logger.warning(f"E002: 字段 [{key}] 不存在")
                return {
                    'valid': False,
                    'error_code': 'E002',
                    'error_message': f'E002 Unsupported: empty value for [{key}]'
                }
            
            # 字段值为空（空字符串、空数组等）
            if self.helper.is_empty(value):
                yaml_check_logger.warning(f"E002: 字段 [{key}] 值为空: {value}")
                return {
                    'valid': False,
                    'error_code': 'E002',
                    'error_message': f'E002 Unsupported: empty value for [{key}]'
                }
        
        yaml_check_logger.info("✅ E002 验证通过：所有字段非空")
        return {'valid': True, 'error_code': '0', 'error_message': 'OK'}
    





    # # E101: 值类型配置
    # VALUE_TYPE_CONFIG = {
    #     'id': 'int',
    #     'order': 'int',
    #     'ipAddress': 'IPv4',
    # }
    # 其中VALUE_TYPE_CONFIG 中的key值是扁平化后的数据中的key值，如果不是扁平化后的数据中的key值的话，就是
    # 扁平化后的数据中的key值的最后1个点后面的值
    # int 值可以用python内建类型验证  但是IPv4类型需要借助标准库：# 使用标准库处理 IP from ipaddress import IPv4Address   验证IP地址是否为IPv4地址  
# 根据上述的介绍  请重新修改优化下validate_value_types(self): 函数

    def validate_value_types(self):
        """
        E101: 验证值类型 - 直接从 self.flattened_data 获取值
        
        支持两种 key 匹配方式：
        1. 完整匹配：VALUE_TYPE_CONFIG 中的 key 与 flattened_data 中的 key 完全匹配
        2. 后缀匹配：VALUE_TYPE_CONFIG 中的 key 与 flattened_data 中 key 的最后一个点后面的值匹配
        
        支持的类型：
        - Python 内建类型：int, number, string, boolean, array, object
        - IPv4：使用 ipaddress 库验证
        """

        
        yaml_check_logger.debug("开始 E101 验证：检查值类型")
        
        for config_key, expected_type in VALUE_TYPE_CONFIG.items():
            yaml_check_logger.debug(f"检查配置项：{config_key} -> {expected_type}")
            
            # 查找匹配的字段
            matched_items = []
            
            for flat_key, value in self.flattened_data.items():
                # 方式1：完整匹配
                if flat_key == config_key:
                    matched_items.append((flat_key, value))
                    yaml_check_logger.debug(f"  完整匹配: {flat_key}")
                # 方式2：后缀匹配（最后一个点后面的值）
                elif '.' in flat_key:
                    last_part = flat_key.rsplit('.', 1)[-1]
                    if last_part == config_key:
                        matched_items.append((flat_key, value))
                        yaml_check_logger.debug(f"  后缀匹配: {flat_key} (后缀: {last_part})")
            
            # 如果没有匹配项，跳过
            if not matched_items:
                yaml_check_logger.debug(f"  未找到匹配字段，跳过")
                continue
            
            # 验证所有匹配项
            for flat_key, value in matched_items:
                yaml_check_logger.debug(f"  验证字段: {flat_key} = {value} (期望类型: {expected_type})")
                
                # 跳过 None 值
                if value is None:
                    yaml_check_logger.debug(f"    值为 None，跳过")
                    continue
                
                # 特殊类型：IPv4
                if expected_type == 'IPv4':
                    try:
                        IPv4Address(value)
                        yaml_check_logger.debug(f"    ✅ IPv4 验证通过: {value}")
                    except (AddressValueError, ValueError, TypeError) as e:
                        yaml_check_logger.warning(f"E101: 字段 [{flat_key}] IPv4 验证失败: {value} - {str(e)}")
                        return {
                            'valid': False,
                            'error_code': 'E101',
                            'error_message': f'E101 Unsupported: value type error for [{flat_key}]. Expected IPv4, got invalid IP: {value}'
                        }
                    continue
                
                # 获取实际类型
                actual_type = self.helper.get_value_type(value)
                
                # 类型映射
                type_map = {
                    'string': ['string'],
                    'int': ['int'],
                    # 'number': ['int', 'number'],
                    'boolean': ['boolean'],
                    'array': ['array'],
                    'object': ['object']
                }
                
                valid_types = type_map.get(expected_type, [expected_type])
                
                if actual_type not in valid_types:
                    yaml_check_logger.warning(
                        f"E101: 字段 [{flat_key}] 类型错误，期望 {expected_type}，实际 {actual_type}，值: {value}"
                    )
                    return {
                        'valid': False,
                        'error_code': 'E101',
                        'error_message': f'E101 Unsupported: value type error for [{flat_key}]. Expected {expected_type}, got {actual_type}'
                    }
                
                yaml_check_logger.debug(f"    ✅ 类型验证通过: {actual_type} in {valid_types}")
        
        yaml_check_logger.info("✅ E101 验证通过：所有字段类型正确")
        return {'valid': True, 'error_code': '0', 'error_message': 'OK'}
    
    def validate_value_ranges(self):
        """E102: 验证值范围（白名单） - 直接从 self.flattened_data 获取值"""
        yaml_check_logger.debug("开始 E102 验证：检查值范围")
        
        for key, allowed_values in VALUE_RANGE_CONFIG.items():
            # 从扁平化数据中获取值
            value = self.flattened_data.get(key)
            
            if value is None:
                continue
            
            if value not in allowed_values:
                yaml_check_logger.warning(f"E102: 字段 [{key}] 值 '{value}' 不在白名单中")
                return {
                    'valid': False,
                    'error_code': 'E102',
                    'error_message': f'E102 Unsupported: invalid value range for [{key}]. Value "{value}" is not in whitelist [{", ".join(allowed_values)}]'
                }
        
        yaml_check_logger.info("✅ E102 验证通过：值范围合法")
        return {'valid': True, 'error_code': '0', 'error_message': 'OK'}
    
    def validate(self, yaml_data):
        """
        主验证函数
        对应 check_yaml.ts 的 compatibility_analysis
        """
        try:
            yaml_check_logger.info("========== 开始 YAML 验证流程 ==========")
            
            # 输入验证
            if not yaml_data or not isinstance(yaml_data, dict):
                yaml_check_logger.error("E000: 无效的 YAML 数据对象")
                return {
                    'success': False,
                    'error': {
                        'code': 'E000',
                        'message': 'Invalid YAML data object'
                    }
                }
            
            # 保存原始数据和扁平化数据
            self.original_data = yaml_data
            self.flattened_data = self._flatten_json(yaml_data)
            yaml_check_logger.debug(f"数据扁平化完成，共 {len(self.flattened_data)} 个字段")
            
            # E001: 验证必需的根键
            result = self.validate_required_root_keys()
            if not result['valid']:
                return {
                    'success': False,
                    'error': {
                        'code': result['error_code'],
                        'message': result['error_message']
                    }
                }
            
            # E002: 验证不能为空的键
            result = self.validate_mandatory_non_empty_keys()
            if not result['valid']:
                return {
                    'success': False,
                    'error': {
                        'code': result['error_code'],
                        'message': result['error_message']
                    }
                }
            
            # E101: 验证值类型
            result = self.validate_value_types()
            if not result['valid']:
                return {
                    'success': False,
                    'error': {
                        'code': result['error_code'],
                        'message': result['error_message']
                    }
                }
            
            # E102: 验证值范围
            result = self.validate_value_ranges()
            if not result['valid']:
                return {
                    'success': False,
                    'error': {
                        'code': result['error_code'],
                        'message': result['error_message']
                    }
                }
            
            # 所有验证通过
            yaml_check_logger.success("========== ✅ 所有验证通过 ==========")
            return {'success': True}
            
        except Exception as e:
            yaml_check_logger.exception(f"验证过程发生异常: {str(e)}")
            return {
                'success': False,
                'error': {
                    'code': 'E999',
                    'message': f'Validation exception: {str(e)}'
                }
            }