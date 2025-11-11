"""
Case Editor API 端点

提供用例编辑器的所有 API 接口，包括：
- Casespace 和 Case 管理
- 文件树浏览
- 文件内容读写
- 文件和目录的增删改查
- Case 的上传下载
"""
from typing import Optional
from django.http import HttpRequest, HttpResponse
from ninja_extra import Router
from loguru import logger

from xutils import utils
from . import schemas
from .file_manager import file_manager
from .exceptions import (
    CaseNotFoundException,
    CasespaceNotFoundException,
    PathTraversalException,
    InvalidCaseNameException,
    FileOperationException,
)


router = Router(tags=["Case Editor"])


@router.get("/casespaces", url_name="get_casespaces")
def get_casespaces(request: HttpRequest):
    """
    获取所有 Casespace 列表
    
    Returns:
        Casespace 列表，每个包含 name 和 path
    """
    try:
        casespaces = file_manager.get_casespaces()
        resp = utils.RespSuccessTempl()
        resp.data = casespaces
        return resp.as_dict()
    except Exception as e:
        logger.error(f"Error getting casespaces: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()


@router.get("/casespaces/{casespace}/cases", url_name="get_cases")
def get_cases(request: HttpRequest, casespace: str):
    """
    获取指定 Casespace 的 Case 列表
    
    Path Parameters:
        casespace: Casespace 名称
        
    Returns:
        Case 列表，每个包含 name 和 path
    """
    try:
        cases = file_manager.get_cases(casespace)
        resp = utils.RespSuccessTempl()
        resp.data = cases
        return resp.as_dict()
    except CasespaceNotFoundException as e:
        logger.warning(f"Casespace not found: {casespace}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()
    except Exception as e:
        logger.error(f"Error getting cases for {casespace}: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()


@router.get("/files", url_name="get_file_tree")
def get_file_tree(
    request: HttpRequest,
    casespace: Optional[str] = None,
    case: Optional[str] = None,
    path: str = "/"
):
    """
    获取文件树结构
    
    Query Parameters:
        casespace: Casespace 名称（可选）
        case: Case 名称（可选）
        path: 路径（默认为根目录）
        
    Returns:
        文件树节点列表
    """
    try:
        # 必须同时提供 casespace 和 case
        if not casespace or not case:
            resp = utils.RespSuccessTempl()
            resp.data = []  # 返回空数组而不是所有 casespace
            return resp.as_dict()
        
        file_tree = file_manager.get_file_tree(path, casespace, case)
        resp = utils.RespSuccessTempl()
        resp.data = file_tree
        return resp.as_dict()
    except PathTraversalException as e:
        logger.warning(f"Path traversal attempt: {e}")
        resp = utils.RespFailedTempl()
        resp.code = 403
        resp.data = str(e)
        return resp.as_dict()
    except Exception as e:
        logger.error(f"Error getting file tree: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()


@router.get("/files/content", url_name="get_file_content")
def get_file_content(request: HttpRequest, path: str):
    """
    获取文件内容
    
    Query Parameters:
        path: 文件路径
        
    Returns:
        文件内容，包含 path, content, language
    """
    try:
        content = file_manager.get_file_content(path)
        resp = utils.RespSuccessTempl()
        resp.data = content
        return resp.as_dict()
    except FileNotFoundError as e:
        logger.warning(f"File not found: {path}")
        resp = utils.RespFailedTempl()
        resp.code = 404
        resp.data = f"文件未找到: {str(e)}"
        return resp.as_dict()
    except PathTraversalException as e:
        logger.warning(f"Path traversal attempt: {e}")
        resp = utils.RespFailedTempl()
        resp.code = 403
        resp.data = str(e)
        return resp.as_dict()
    except Exception as e:
        logger.error(f"Error getting file content: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()


@router.post("/files/save", url_name="save_file")
def save_file(request: HttpRequest, data: schemas.SaveFileRequest):
    """
    保存文件内容
    
    Body:
        path: 文件路径
        content: 文件内容
        
    Returns:
        成功消息
    """
    try:
        file_manager.save_file(data.path, data.content)
        resp = utils.RespSuccessTempl()
        resp.data = {"success": True, "message": "文件保存成功"}
        return resp.as_dict()
    except FileNotFoundError as e:
        logger.warning(f"File not found: {data.path}")
        resp = utils.RespFailedTempl()
        resp.code = 404
        resp.data = f"文件未找到: {str(e)}"
        return resp.as_dict()
    except FileOperationException as e:
        logger.error(f"File operation failed: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()
    except Exception as e:
        logger.error(f"Error saving file: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()


@router.post("/files/create", url_name="create_file")
def create_file(request: HttpRequest, data: schemas.CreateFileRequest):
    """
    创建新文件
    
    Body:
        parentPath: 父目录路径
        name: 文件名
        
    Returns:
        新创建的文件节点信息
    """
    try:
        new_file = file_manager.create_file(data.parent_path, data.name)
        resp = utils.RespSuccessTempl()
        resp.data = new_file
        return resp.as_dict()
    except (ValueError, FileExistsError) as e:
        logger.warning(f"Error creating file: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()
    except FileOperationException as e:
        logger.error(f"File operation failed: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()
    except Exception as e:
        logger.error(f"Unexpected error creating file: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()


@router.post("/folders/create", url_name="create_folder")
def create_folder(request: HttpRequest, data: schemas.CreateFolderRequest):
    """
    创建新目录
    
    Body:
        parentPath: 父目录路径
        name: 目录名
        
    Returns:
        新创建的目录节点信息
    """
    try:
        new_folder = file_manager.create_folder(data.parent_path, data.name)
        resp = utils.RespSuccessTempl()
        resp.data = new_folder
        return resp.as_dict()
    except (ValueError, FileExistsError) as e:
        logger.warning(f"Error creating folder: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()
    except FileOperationException as e:
        logger.error(f"File operation failed: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()
    except Exception as e:
        logger.error(f"Unexpected error creating folder: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()


@router.put("/files/rename", url_name="rename_item")
def rename_item(request: HttpRequest, data: schemas.RenameRequest):
    """
    重命名文件或目录
    
    Body:
        oldPath: 当前路径
        newName: 新名称
        
    Returns:
        重命名后的节点信息
    """
    try:
        renamed_item = file_manager.rename_item(data.old_path, data.new_name)
        resp = utils.RespSuccessTempl()
        resp.data = renamed_item
        return resp.as_dict()
    except (FileNotFoundError, FileExistsError) as e:
        logger.warning(f"Error renaming item: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()
    except FileOperationException as e:
        logger.error(f"File operation failed: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()
    except Exception as e:
        logger.error(f"Unexpected error renaming item: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()


@router.delete("/files", url_name="delete_item")
def delete_item(request: HttpRequest, path: str):
    """
    删除文件或目录
    
    Query Parameters:
        path: 要删除的路径
        
    Returns:
        成功消息
    """
    try:
        file_manager.delete_item(path)
        resp = utils.RespSuccessTempl()
        resp.data = {"success": True, "message": "删除成功"}
        return resp.as_dict()
    except FileNotFoundError as e:
        logger.warning(f"File not found: {path}")
        resp = utils.RespFailedTempl()
        resp.code = 404
        resp.data = f"文件未找到: {str(e)}"
        return resp.as_dict()
    except FileOperationException as e:
        logger.error(f"File operation failed: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()
    except Exception as e:
        logger.error(f"Error deleting item: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()


@router.post("/files/upload", url_name="upload_files")
def upload_files(request: HttpRequest, data: schemas.UploadFilesRequest):
    """
    批量上传文件
    
    Body:
        parentPath: 父目录路径
        files: 文件列表 [{name: string, content: string}, ...]
        
    Returns:
        上传结果，包含成功文件数量
    """
    try:
        uploaded_count = file_manager.upload_files(
            data.parent_path,
            [{'name': f.name, 'content': f.content} for f in data.files]
        )
        resp = utils.RespSuccessTempl()
        resp.data = {
            "success": True,
            "message": f"成功上传 {uploaded_count} 个文件",
            "count": uploaded_count
        }
        return resp.as_dict()
    except ValueError as e:
        logger.warning(f"Invalid upload request: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()
    except FileOperationException as e:
        logger.error(f"File operation failed: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()
    except Exception as e:
        logger.error(f"Unexpected error uploading files: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()


@router.delete("/casespaces/{casespace}/cases/{case}", url_name="delete_case")
def delete_case(request: HttpRequest, casespace: str, case: str):
    """
    删除指定的 Case
    
    Path Parameters:
        casespace: Casespace 名称
        case: Case 名称
        
    Returns:
        成功消息
    """
    try:
        file_manager.delete_case(casespace, case)
        resp = utils.RespSuccessTempl()
        resp.data = {"success": True, "message": f"成功删除 case: {case}"}
        return resp.as_dict()
    except CaseNotFoundException as e:
        logger.warning(f"Case not found: {casespace}/{case}")
        resp = utils.RespFailedTempl()
        resp.code = 404
        resp.data = str(e)
        return resp.as_dict()
    except FileOperationException as e:
        logger.error(f"File operation failed: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()
    except Exception as e:
        logger.error(f"Error deleting case: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()


@router.get("/casespaces/{casespace}/cases/{case}/download", url_name="download_case")
def download_case(request: HttpRequest, casespace: str, case: str):
    """
    下载指定的 Case 为 zip 文件
    
    Path Parameters:
        casespace: Casespace 名称
        case: Case 名称
        
    Returns:
        zip 文件下载响应
    """
    try:
        # Get zip data from file manager
        zip_data = file_manager.download_case(casespace, case)
        
        # Create HTTP response with zip file
        response = HttpResponse(zip_data, content_type='application/zip')
        response['Content-Disposition'] = f'attachment; filename="{case}.zip"'
        return response
    except CaseNotFoundException as e:
        logger.warning(f"Case not found: {casespace}/{case}")
        resp = utils.RespFailedTempl()
        resp.code = 404
        resp.data = str(e)
        return resp.as_dict()
    except FileOperationException as e:
        logger.error(f"File operation failed: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()
    except Exception as e:
        logger.error(f"Error downloading case: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()


@router.post("/casespaces/{casespace}/upload-case", url_name="upload_case")
def upload_case(request: HttpRequest, casespace: str):
    """
    上传并解压 Case 压缩包
    
    Path Parameters:
        casespace: Casespace 名称
    
    Form Data:
        case_name: 新 Case 的名称
        file: 压缩包文件 (.tar.gz, .tgz, 或 .zip)
        
    Returns:
        上传结果，包含新 Case 名称
    """
    try:
        logger.info(f"Upload case request received: casespace={casespace}")
        
        # Get form data from request
        case_name = request.POST.get('case_name')
        if not case_name:
            raise ValueError("case_name is required")
        
        # Get uploaded file
        if 'file' not in request.FILES:
            raise ValueError("file is required")
        
        uploaded_file = request.FILES['file']
        file_data = uploaded_file.read()
        filename = uploaded_file.name
        
        logger.info(f"Processing upload: case_name={case_name}, filename={filename}, size={len(file_data)} bytes")
        
        # Upload and extract
        file_manager.upload_case(casespace, case_name, file_data, filename)
        
        resp = utils.RespSuccessTempl()
        resp.data = {
            "success": True,
            "message": f"成功上传并解压 case: {case_name}",
            "caseName": case_name
        }
        return resp.as_dict()
    except InvalidCaseNameException as e:
        logger.warning(f"Invalid case name: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()
    except ValueError as e:
        logger.warning(f"Invalid upload request: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()
    except PathTraversalException as e:
        logger.warning(f"Path traversal attempt in archive: {e}")
        resp = utils.RespFailedTempl()
        resp.code = 403
        resp.data = str(e)
        return resp.as_dict()
    except Exception as e:
        logger.error(f"Error uploading case: {e}")
        resp = utils.RespFailedTempl()
        resp.data = str(e)
        return resp.as_dict()

