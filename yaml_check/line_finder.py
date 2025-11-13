"""
YAML 行号查找工具
对应 CustomPlan.vue 第 137-189 行的 findKeyLineNumber
"""

import re
from .logger import yaml_check_logger

class YamlLineFinder:
    
    @staticmethod
    def extract_key_from_error(error_message):
        """
        从错误信息中提取 key 路径
        对应 CustomPlan.vue 第 196-200 行
        """
        match = re.search(r'\[([^\]]+)\]', error_message)
        return match.group(1) if match else None
    
    @staticmethod
    def find_key_line_number(yaml_text, key_path):
        """
        在 YAML 文本中查找指定 key 路径所在的行号
        对应 CustomPlan.vue 第 137-189 行
        
        参数：
        - yaml_text: YAML 格式的文本字符串
        - key_path: key 路径，如 "hardware.machines"
        
        返回：
        - 行号（从1开始），未找到返回 -1
        """
        yaml_check_logger.debug(f"查找 key 行号: {key_path}")
        
        if not yaml_text or not key_path:
            yaml_check_logger.warning("yaml_text 或 key_path 为空")
            return -1
        
        lines = yaml_text.split('\n')
        keys = key_path.split('.')
        
        yaml_check_logger.debug(f"YAML 文本共 {len(lines)} 行，key 路径层级: {keys}")
        
        current_key_index = 0
        expected_indent = 0
        
        for i, line in enumerate(lines):
            trimmed_line = line.strip()
            
            # 跳过空行和注释
            if not trimmed_line or trimmed_line.startswith('#'):
                continue
            
            # 计算缩进级别（空格数除以2）
            match = re.search(r'\S', line)
            if match:
                indent = match.start() // 2
            else:
                continue
            
            # 获取当前需要匹配的 key
            target_key = keys[current_key_index]
            
            # 匹配 key（支持 "key:" 格式）
            key_pattern = re.compile(f'^{re.escape(target_key)}\\s*:')
            
            if key_pattern.match(trimmed_line) and indent == expected_indent:
                current_key_index += 1
                yaml_check_logger.debug(f"匹配到 key '{target_key}' 在第 {i+1} 行")
                
                # 如果已经找到完整路径，返回行号（从1开始）
                if current_key_index == len(keys):
                    yaml_check_logger.info(f"找到完整 key 路径 '{key_path}' 在第 {i+1} 行")
                    return i + 1
                
                # 更新下一层的期望缩进
                expected_indent = indent + 1
        
        # 未找到
        yaml_check_logger.warning(f"未找到 key 路径: {key_path}")
        return -1
    
    @staticmethod
    def js_to_yaml(obj, indent=0):
        """
        将 JavaScript/Python 对象转换为 YAML 格式文本
        对应 CustomPlan.vue 第 206-241 行
        
        这个函数确保后端生成的 YAML 格式与前端一致
        """
        yaml = ''
        spaces = '  ' * indent
        
        if not isinstance(obj, dict):
            return str(obj)
        
        for key, value in obj.items():
            if isinstance(value, list):
                yaml += f'{spaces}{key}:\n'
                for item in value:
                    if isinstance(item, dict):
                        item_yaml = YamlLineFinder.js_to_yaml(item, indent + 2)
                        lines = item_yaml.strip().split('\n')
                        yaml += f'{spaces}  -'
                        for idx, line in enumerate(lines):
                            if idx == 0:
                                yaml += f' {line.strip()}\n'
                            else:
                                yaml += f'{spaces}    {line.strip()}\n'
                    else:
                        yaml += f'{spaces}  - {item}\n'
            elif isinstance(value, dict):
                yaml += f'{spaces}{key}:\n'
                yaml += YamlLineFinder.js_to_yaml(value, indent + 1)
            else:
                yaml += f'{spaces}{key}: {value}\n'
        
        return yaml