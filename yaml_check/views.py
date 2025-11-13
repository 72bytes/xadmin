from django.http import JsonResponse, HttpRequest
from ninja_extra import Router, api_controller
from xutils import utils
from .validator import YamlValidator
from .line_finder import YamlLineFinder
from .logger import yaml_check_logger
import json

router = Router()


@router.post('/validate')
def validate_yaml(request: HttpRequest):
    """
    YAML 兼容性验证 API
    
    请求体：
    {
        "yamlData": {
            "metadata": {...},
            "hardware": {...},
            ...
        }
    }
    
    响应：
    {
        "code": 200,
        "msg": "success",
        "data": {
            "success": true/false,
            "error": {
                "code": "E001",
                "message": "...",
                "key": "hardware.cpu",
                "lineNumber": 5
            }
        }
    }
    """
    try:
        yaml_check_logger.info("收到 YAML 验证请求")
        
        # 解析请求体
        body = json.loads(request.body)
        yaml_data = body.get('yamlData')
        
        if not yaml_data:
            yaml_check_logger.warning("请求体中缺少 yamlData")
            resp = utils.RespFailedTempl()
            resp.data = 'Missing yamlData in request body'
            return resp.as_dict()
        
        yaml_check_logger.debug(f"开始验证 YAML 数据，数据键: {list(yaml_data.keys())}")
        
        # 创建验证器并验证
        validator = YamlValidator()
        result = validator.validate(yaml_data)
        
        yaml_check_logger.info(f"验证完成，结果: {'成功' if result.get('success') else '失败'}")
        
        # 如果验证失败，计算行号
        if not result['success'] and result.get('error'):
            error = result['error']
            error_code = error.get('code', '')
            error_message = error.get('message', '')
            
            yaml_check_logger.warning(f"验证失败: [{error_code}] {error_message}")
            
            # 只对 E002, E101, E102 计算行号
            if error_code in ['E002', 'E101', 'E102']:
                # 提取 key 路径
                key_path = YamlLineFinder.extract_key_from_error(error_message)
                
                if key_path:
                    yaml_check_logger.debug(f"提取到错误 key 路径: {key_path}")
                    
                    # 将 YAML 数据转换为文本格式
                    yaml_text = YamlLineFinder.js_to_yaml(yaml_data).rstrip()
                    
                    # 查找行号
                    line_number = YamlLineFinder.find_key_line_number(yaml_text, key_path)
                    
                    if line_number != -1:
                        error['key'] = key_path
                        error['lineNumber'] = line_number
                        yaml_check_logger.info(f"找到错误行号: {line_number}, key: {key_path}")
                    else:
                        yaml_check_logger.warning(f"未能找到 key 的行号: {key_path}")
        
        # 返回结果
        resp = utils.RespSuccessTempl()
        resp.data = result
        yaml_check_logger.info("返回验证结果")
        return resp.as_dict()
        
    except json.JSONDecodeError as e:
        yaml_check_logger.error(f"JSON 解析失败: {str(e)}")
        resp = utils.RespFailedTempl()
        resp.data = 'Invalid JSON in request body'
        return resp.as_dict()
    except Exception as e:
        yaml_check_logger.exception(f"验证过程发生异常: {str(e)}")
        resp = utils.RespFailedTempl()
        resp.data = f'Validation error: {str(e)}'
        return resp.as_dict()