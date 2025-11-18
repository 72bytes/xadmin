"""
YAML Test Plan Upload and Validation API
"""
from ninja import Router, File
from ninja.files import UploadedFile
from django.http import HttpRequest
from xutils.utils import RespSuccessTempl, RespFailedTempl
from loguru import logger
from yaml_test_plan.validator import validate_yaml_full
from pathlib import Path
import yaml

router = Router()


@router.post('/upload')
def upload_yaml_test_plan(request: HttpRequest, file: UploadedFile = File(...)):
    """
    Upload and validate YAML test plan file using comprehensive validation
    Returns file content with detailed error information including line numbers
    """
    try:
        # Read file content
        content = file.read().decode('utf-8')
        
        # Split content into lines for frontend display
        lines = content.split('\n')
        
        # Use comprehensive YAML validation from yaml_test_plan.validator
        is_valid, errors = validate_yaml_full(content)
        
        # If validation failed
        if not is_valid:
            resp = RespFailedTempl()
            resp.code = 400
            resp.message = "YAML validation failed"
            resp.data = {
                "file_name": file.name,
                "file_size": file.size,
                "file_content": content,
                "lines": lines,
                "errors": errors,
                "error_count": len(errors)
            }
            return resp.as_dict()
        
        # Success - 解析 YAML 内容
        try:
            parsed_data = yaml.safe_load(content)
        except Exception as parse_error:
            logger.warning(f"YAML parsing warning: {parse_error}")
            parsed_data = None
        
        resp = RespSuccessTempl()
        resp.data = {
            "file_name": file.name,
            "file_size": file.size,
            "file_content": content,
            "lines": lines,
            "parsed_data": parsed_data,  # 添加解析后的数据
            "message": "File uploaded and validated successfully"
        }
        return resp.as_dict()
        
    except Exception as e:
        logger.error(f"Error uploading YAML file: {e}")
        resp = RespFailedTempl()
        resp.code = 500
        resp.message = f"Internal server error: {str(e)}"
        return resp.as_dict()


@router.get('/standard-template')
def get_standard_template(request: HttpRequest):
    """
    Get the standard YAML test plan template for comparison
    Returns the content of standard.yaml template
    """
    try:
        # Get the path to standard template
        template_path = Path(__file__).parent / 'templates' / 'standard.yaml'
        
        if not template_path.exists():
            resp = RespFailedTempl()
            resp.code = 404
            resp.message = "Standard template not found"
            return resp.as_dict()
        
        # Read template content
        with open(template_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        resp = RespSuccessTempl()
        resp.data = {
            "file_name": "standard.yaml",
            "file_content": content,
            "lines": lines,
            "message": "Standard template loaded successfully"
        }
        return resp.as_dict()
        
    except Exception as e:
        logger.error(f"Error loading standard template: {e}")
        resp = RespFailedTempl()
        resp.code = 500
        resp.message = f"Internal server error: {str(e)}"
        return resp.as_dict()

