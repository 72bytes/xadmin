from ninja import Router, File
from ninja.files import UploadedFile
from xauth.auth import XadminBaseAuth
from .validator import validate_yaml_full
from .models import TestPlanYaml
from django.db import transaction

router = Router(tags=["YAML测试计划验证"])


@router.post("/upload", auth=XadminBaseAuth(), summary="上传YAML测试计划")
def upload_yaml(request, file: UploadedFile = File(...)):
    """上传并验证 YAML 测试计划文件"""
    try:
        # 文件类型检查
        if not file.name.endswith(('.yaml', '.yml')):
            return {
                'code': 400,
                'message': 'Only YAML files (.yaml, .yml) are allowed',
                'data': None
            }
        
        # 文件大小检查 (最大 5MB)
        if file.size > 5 * 1024 * 1024:
            return {
                'code': 400,
                'message': 'File size exceeds 5MB limit',
                'data': None
            }
        
        # 读取内容
        content = file.read().decode('utf-8')
        
        # 严格验证
        validation_result = validate_yaml_full(content)
        
        if not validation_result['valid']:
            error_message = validation_result['error_message']
            line_number = validation_result.get('line_number')
            
            if line_number:
                display_message = f"Line {line_number} [ERROR]\n{error_message}"
            else:
                display_message = f"[ERROR]\n{error_message}"
            
            return {
                'code': 400,
                'message': 'YAML Validation Failed',
                'data': {
                    'error_code': validation_result.get('error_code'),
                    'error_message': display_message,
                    'line_number': line_number
                }
            }
        
        # 验证通过，保存到数据库
        with transaction.atomic():
            yaml_record = TestPlanYaml.objects.create(
                file_name=file.name,
                file_content=content,
                file_size=file.size,
                validation_status='valid',
                create_user=request.user.id
            )
        
        return {
            'code': 200,
            'message': 'File uploaded and validated successfully',
            'data': {
                'id': yaml_record.id,
                'file_name': yaml_record.file_name,
                'file_size': yaml_record.file_size
            }
        }
    
    except Exception as e:
        return {
            'code': 500,
            'message': f'Server error: {str(e)}',
            'data': None
        }


@router.get("/list", auth=XadminBaseAuth(), summary="获取YAML列表")
def list_yaml(request, page: int = 1, page_size: int = 10):
    """获取 YAML 测试计划列表"""
    try:
        offset = (page - 1) * page_size
        queryset = TestPlanYaml.objects.all()
        total = queryset.count()
        records = queryset[offset:offset + page_size]
        
        data_list = []
        for record in records:
            data_list.append({
                'id': record.id,
                'file_name': record.file_name,
                'file_size': record.file_size,
                'validation_status': record.validation_status,
                'create_time': record.create_time.isoformat(),
            })
        
        return {
            'code': 200,
            'message': 'Success',
            'data': {
                'list': data_list,
                'total': total,
                'page': page,
                'page_size': page_size
            }
        }
    except Exception as e:
        return {
            'code': 500,
            'message': f'Server error: {str(e)}',
            'data': None
        }


@router.delete("/{id}", auth=XadminBaseAuth(), summary="删除YAML记录")
def delete_yaml(request, id: int):
    """删除指定的 YAML 记录"""
    try:
        yaml_record = TestPlanYaml.objects.get(id=id)
        yaml_record.delete()
        
        return {
            'code': 200,
            'message': 'YAML record deleted successfully',
            'data': None
        }
    except TestPlanYaml.DoesNotExist:
        return {
            'code': 404,
            'message': 'YAML record not found',
            'data': None
        }
    except Exception as e:
        return {
            'code': 500,
            'message': f'Server error: {str(e)}',
            'data': None
        }

