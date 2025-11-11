"""
Case Browser API 端点

提供用例浏览器的所有 API 接口，包括：
- Case 元数据管理
- 标签管理
- 选项管理
"""
from django.http import HttpRequest
from ninja_extra import Router
from loguru import logger

from xutils import utils
from . import schemas
from .models import CaseMetadata, CaseTag, CaseOption
from .file_manager import file_manager


router = Router(tags=["Case Browser"])


@router.get("/casespaces/{casespace}/cases", url_name="get_cases_metadata")
def get_cases_metadata(request: HttpRequest, casespace: str):
    """
    获取指定 Casespace 下所有 Case 的元数据（包含 tags）
    
    Path Parameters:
        casespace: Casespace 名称
        
    Returns:
        Case 元数据列表，包含 casespace, caseName, tags
    """
    try:
        # Get all cases from file system
        cases = file_manager.get_cases(casespace)
        
        result = []
        for case_info in cases:
            case_name = case_info['name']
            
            # Get or create metadata
            metadata, created = CaseMetadata.objects.get_or_create(
                casespace=casespace,
                case_name=case_name
            )
            
            # Get tags
            tags = list(metadata.tags.values_list('tag', flat=True))
            
            result.append({
                'casespace': casespace,
                'caseName': case_name,
                'tags': tags
            })
        
        resp = utils.RespSuccessTempl()
        resp.data = result
        return resp.as_dict()
    except Exception as e:
        logger.error(f"Error getting cases metadata: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()


@router.get("/casespaces/{casespace}/cases/{case_name}", url_name="get_case_detail")
def get_case_detail(request: HttpRequest, casespace: str, case_name: str):
    """
    获取单个 Case 的详细信息，包含 tags 和 options
    
    Path Parameters:
        casespace: Casespace 名称
        case_name: Case 名称
        
    Returns:
        Case 详情，包含 casespace, caseName, tags, options
    """
    try:
        # Get or create metadata
        metadata, created = CaseMetadata.objects.get_or_create(
            casespace=casespace,
            case_name=case_name
        )
        
        # Get tags
        tags = list(metadata.tags.values_list('tag', flat=True))
        
        # Get options
        options = [
            {'key': opt.key, 'value': opt.value}
            for opt in metadata.options.all()
        ]
        
        result = {
            'casespace': casespace,
            'caseName': case_name,
            'tags': tags,
            'options': options
        }
        
        resp = utils.RespSuccessTempl()
        resp.data = result
        return resp.as_dict()
    except Exception as e:
        logger.error(f"Error getting case detail: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()


@router.post("/cases/tags", url_name="add_tag")
def add_tag(request: HttpRequest, data: schemas.AddTagRequest):
    """
    添加 tag 到 case
    
    Body:
        casespace: Casespace 名称
        caseName: Case 名称
        tag: 标签名称
        
    Returns:
        成功消息
    """
    try:
        # Get or create metadata
        metadata, created = CaseMetadata.objects.get_or_create(
            casespace=data.casespace,
            case_name=data.case_name
        )
        
        # Add tag (unique constraint will prevent duplicates)
        tag_obj, created = CaseTag.objects.get_or_create(
            metadata=metadata,
            tag=data.tag
        )
        
        if created:
            message = f"成功添加标签: {data.tag}"
            logger.info(f"Tag added: {data.casespace}/{data.case_name} - {data.tag}")
        else:
            message = f"标签已存在: {data.tag}"
            logger.debug(f"Tag already exists: {data.casespace}/{data.case_name} - {data.tag}")
        
        resp = utils.RespSuccessTempl()
        resp.data = {"success": True, "message": message}
        return resp.as_dict()
    except Exception as e:
        logger.error(f"Error adding tag: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()


@router.delete("/cases/tags", url_name="delete_tag")
def delete_tag(request: HttpRequest, casespace: str, case_name: str, tag: str):
    """
    删除 case 的 tag
    
    Query Parameters:
        casespace: Casespace 名称
        case_name: Case 名称 (caseName)
        tag: 标签名称
        
    Returns:
        成功消息
    """
    try:
        # Get metadata
        metadata = CaseMetadata.objects.get(
            casespace=casespace,
            case_name=case_name
        )
        
        # Delete tag
        deleted_count, _ = CaseTag.objects.filter(
            metadata=metadata,
            tag=tag
        ).delete()
        
        if deleted_count > 0:
            message = f"成功删除标签: {tag}"
            logger.info(f"Tag deleted: {casespace}/{case_name} - {tag}")
        else:
            message = f"标签不存在: {tag}"
            logger.debug(f"Tag not found: {casespace}/{case_name} - {tag}")
        
        resp = utils.RespSuccessTempl()
        resp.data = {"success": True, "message": message}
        return resp.as_dict()
    except CaseMetadata.DoesNotExist:
        logger.warning(f"Case not found: {casespace}/{case_name}")
        resp = utils.RespFailedTempl()
        resp.code = 404
        resp.data = f"Case 不存在: {casespace}/{case_name}"
        return resp.as_dict()
    except Exception as e:
        logger.error(f"Error deleting tag: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()


@router.post("/cases/options", url_name="add_option")
def add_option(request: HttpRequest, data: schemas.AddOptionRequest):
    """
    添加 option 到 case
    
    Body:
        casespace: Casespace 名称
        caseName: Case 名称
        key: 选项键
        value: 选项值
        
    Returns:
        成功消息
    """
    try:
        # Get or create metadata
        metadata, created = CaseMetadata.objects.get_or_create(
            casespace=data.casespace,
            case_name=data.case_name
        )
        
        # Add or update option
        option, created = CaseOption.objects.update_or_create(
            metadata=metadata,
            key=data.key,
            defaults={'value': data.value}
        )
        
        if created:
            message = f"成功添加选项: {data.key}={data.value}"
            logger.info(f"Option added: {data.casespace}/{data.case_name} - {data.key}={data.value}")
        else:
            message = f"成功更新选项: {data.key}={data.value}"
            logger.info(f"Option updated: {data.casespace}/{data.case_name} - {data.key}={data.value}")
        
        resp = utils.RespSuccessTempl()
        resp.data = {"success": True, "message": message}
        return resp.as_dict()
    except Exception as e:
        logger.error(f"Error adding option: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()


@router.put("/cases/options", url_name="update_option")
def update_option(request: HttpRequest, data: schemas.UpdateOptionRequest):
    """
    更新 case 的 option
    
    Body:
        casespace: Casespace 名称
        caseName: Case 名称
        key: 选项键
        value: 选项值
        
    Returns:
        成功消息
    """
    try:
        # Get metadata
        metadata = CaseMetadata.objects.get(
            casespace=data.casespace,
            case_name=data.case_name
        )
        
        # Update option
        option = CaseOption.objects.get(
            metadata=metadata,
            key=data.key
        )
        option.value = data.value
        option.save()
        
        logger.info(f"Option updated: {data.casespace}/{data.case_name} - {data.key}={data.value}")
        
        resp = utils.RespSuccessTempl()
        resp.data = {"success": True, "message": f"成功更新选项: {data.key}={data.value}"}
        return resp.as_dict()
    except CaseMetadata.DoesNotExist:
        logger.warning(f"Case not found: {data.casespace}/{data.case_name}")
        resp = utils.RespFailedTempl()
        resp.code = 404
        resp.data = f"Case 不存在: {data.casespace}/{data.case_name}"
        return resp.as_dict()
    except CaseOption.DoesNotExist:
        logger.warning(f"Option not found: {data.casespace}/{data.case_name} - {data.key}")
        resp = utils.RespFailedTempl()
        resp.code = 404
        resp.data = f"选项不存在: {data.key}"
        return resp.as_dict()
    except Exception as e:
        logger.error(f"Error updating option: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()


@router.delete("/cases/options", url_name="delete_option")
def delete_option(request: HttpRequest, casespace: str, case_name: str, key: str):
    """
    删除 case 的 option
    
    Query Parameters:
        casespace: Casespace 名称
        case_name: Case 名称 (caseName)
        key: 选项键
        
    Returns:
        成功消息
    """
    try:
        # Get metadata
        metadata = CaseMetadata.objects.get(
            casespace=casespace,
            case_name=case_name
        )
        
        # Delete option
        deleted_count, _ = CaseOption.objects.filter(
            metadata=metadata,
            key=key
        ).delete()
        
        if deleted_count > 0:
            message = f"成功删除选项: {key}"
            logger.info(f"Option deleted: {casespace}/{case_name} - {key}")
        else:
            message = f"选项不存在: {key}"
            logger.debug(f"Option not found: {casespace}/{case_name} - {key}")
        
        resp = utils.RespSuccessTempl()
        resp.data = {"success": True, "message": message}
        return resp.as_dict()
    except CaseMetadata.DoesNotExist:
        logger.warning(f"Case not found: {casespace}/{case_name}")
        resp = utils.RespFailedTempl()
        resp.code = 404
        resp.data = f"Case 不存在: {casespace}/{case_name}"
        return resp.as_dict()
    except Exception as e:
        logger.error(f"Error deleting option: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()

