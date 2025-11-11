"""
XCase API Schemas

定义用例管理相关的 API 请求和响应 Schema。
使用 Pydantic 的 ninja.Schema 进行数据验证。
"""
from typing import List, Optional
from ninja import Schema, Field


# ============================================================================
# Case Editor Schemas
# ============================================================================

class CasespaceItemSchema(Schema):
    """Casespace 列表项"""
    name: str
    path: str


class CaseItemSchema(Schema):
    """Case 列表项"""
    name: str
    path: str


class FileNodeSchema(Schema):
    """文件树节点"""
    path: str
    name: str
    type: str  # 'file' or 'folder'
    children: Optional[List['FileNodeSchema']] = None


class FileContentSchema(Schema):
    """文件内容"""
    path: str
    content: str
    language: Optional[str] = None


class SaveFileRequest(Schema):
    """保存文件请求"""
    path: str
    content: str


class CreateFileRequest(Schema):
    """创建文件请求"""
    parent_path: str = Field(..., alias='parentPath')
    name: str


class CreateFolderRequest(Schema):
    """创建目录请求"""
    parent_path: str = Field(..., alias='parentPath')
    name: str


class RenameRequest(Schema):
    """重命名文件/目录请求"""
    old_path: str = Field(..., alias='oldPath')
    new_name: str = Field(..., alias='newName')


class UploadFileItem(Schema):
    """单个上传文件项"""
    name: str
    content: str


class UploadFilesRequest(Schema):
    """批量上传文件请求"""
    parent_path: str = Field(..., alias='parentPath')
    files: List[UploadFileItem]


# ============================================================================
# Case Browser Schemas
# ============================================================================

class CaseOptionSchema(Schema):
    """Case 选项（键值对）"""
    key: str
    value: str


class CaseMetadataSchema(Schema):
    """Case 元数据（包含标签）"""
    casespace: str
    case_name: str = Field(..., alias='caseName')
    tags: List[str]


class CaseDetailSchema(Schema):
    """Case 详情（包含标签和选项）"""
    casespace: str
    case_name: str = Field(..., alias='caseName')
    tags: List[str]
    options: List[CaseOptionSchema]


# ============================================================================
# Case Tag Management Schemas
# ============================================================================

class AddTagRequest(Schema):
    """添加标签请求"""
    casespace: str
    case_name: str = Field(..., alias='caseName')
    tag: str


class DeleteTagRequest(Schema):
    """删除标签请求"""
    casespace: str
    case_name: str = Field(..., alias='caseName')
    tag: str


# ============================================================================
# Case Option Management Schemas
# ============================================================================

class AddOptionRequest(Schema):
    """添加选项请求"""
    casespace: str
    case_name: str = Field(..., alias='caseName')
    key: str
    value: str


class UpdateOptionRequest(Schema):
    """更新选项请求"""
    casespace: str
    case_name: str = Field(..., alias='caseName')
    key: str
    value: str


class DeleteOptionRequest(Schema):
    """删除选项请求"""
    casespace: str
    case_name: str = Field(..., alias='caseName')
    key: str


# ============================================================================
# Response Schemas
# ============================================================================

class SuccessResponse(Schema):
    """成功响应"""
    success: bool = True
    message: str


class ErrorResponse(Schema):
    """错误响应"""
    success: bool = False
    error: str


# 更新 FileNodeSchema 的 forward references
FileNodeSchema.model_rebuild()

