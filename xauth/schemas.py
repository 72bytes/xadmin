from ninja import Schema
from ninja import Field
from typing import List
from typing import Optional
from typing import Union




# Role
class SysRoleAdd(Schema):
    code: str
    data_scope: int = Field(..., alias='dataScope')
    menu_ids: List[int] = Field(..., alias='menuIds')
    dept_ids: List[int] = Field(..., alias='deptIds')
    name: str
    sort: int
    description: Optional[str] = ''
    is_system: int = 0

class SysRoleIn(Schema):
    id: int
    code: str
    create_user: int = Field(..., alias='createUserString')
    create_time: str = Field(..., alias='createTime')
    data_scope: int = Field(..., alias='dataScope')
    menu_ids: List[int] = Field(..., alias='menuIds')
    dept_ids: List[int] = Field(..., alias='deptIds')
    name: str
    sort: int
    description: Optional[str] = ''

# Menu
class SysMenuIn(Schema):
    type: int
    icon: str
    title: str
    sort: int
    permission: Optional[str] = ''
    path: str
    name: str
    component: Optional[str] = 'Layout'
    redirect: Optional[str] = ''
    is_external: bool = Field(..., alias='isExternal')
    is_cache: bool = Field(..., alias='isCache')
    is_hidden: bool = Field(..., alias='isHidden')
    parent_id: int = Field(0, alias='parentId')
    status: int 

# Department
class SysDeptAdd(Schema):
    parent_id: int = Field(..., alias='parentId')
    name: str
    sort: int
    description: Optional[str] = ''
    status: int
    is_system: Optional[int] = 0

# Option
class SysOption(Schema):
    id: int
    code: str
    value: str

SysOptionUpdate = List[SysOption]

class SysOptionResetIn(Schema):
    category: str

class SysOptionOut(Schema):
    id: int
    name: str
    code: str
    value: str
    description: str

# Dict
class SysDictIn(Schema):
    name: str
    code: str
    description: Optional[str] = ''
    is_system: Optional[int] = 0

class SysDictOut(Schema): # no used for now
    id: int
    name: str
    code: str
    description: str
    create_user: str = Field("", alias='createUser')
    create_time: str = Field("", alias='createTime')
    update_user: str = Field("", alias='updateUser')
    update_time: str = Field("", alias='updateTime')
    is_system: bool = Field(False, alias='isSystem')

# Dict Item
class SysDictItemIn(Schema):
    label: str
    value: str
    color: str
    sort: int
    description: Optional[str] = ''
    status: int
    dict_id: int = Field(..., alias='dictId')

# User
class SysUserOut(Schema): # not used for now
    id: int
    create_user: str = Field(..., alias='createUserString')
    createTime: str = Field(..., alias='createTime')
    disabled: bool = False
    update_user: str = Field(..., alias='updateUserString')
    update_time: str = Field(..., alias='updateTime')
    username: str
    nickname: str
    gender: int
    avatar: str
    email: Union[str, None]
    phone: Union[str, None]
    status: int
    is_system: bool = Field(..., alias='isSystem')
    description: str
    dept_id: str = Field(..., alias='deptId') 

class SysUserAdd(Schema):
    username: str
    nickname: str
    password: str
    email: Optional[str] = None
    phone: Optional[str] = None
    gender: int
    is_system: int = 0
    dept_id: int = Field(..., alias='deptId')
    role_ids: List[int] = Field(..., alias='roleIds')
    description: Optional[str] = ''
    status: int

class SysUserUpdate(Schema):
    username: str
    nickname: str
    email: Optional[str] = None
    phone: Optional[str] = None
    gender: int
    dept_id: int = Field(..., alias='deptId')
    role_ids: List[int] = Field(..., alias='roleIds')
    description: Optional[str] = ''
    status: int

class SetUserRoles(Schema):
    role_ids: str = Field(..., alias='roleIds')

class ResetUserPassword(Schema):
    new_password: str = Field(..., alias='newPassword')

class UpdateUserPassword(Schema):
    """用户修改自己的密码（需要验证旧密码）"""
    old_password: str = Field(..., alias='oldPassword')
    new_password: str = Field(..., alias='newPassword')

class SysUserLogin(Schema):
    # captcha: str  # 验证码功能已注释
    # uuid: str  # 验证码功能已注释
    username: str
    password: str

class SysUserProfile(Schema):
    gender: int
    nickname: str



# Case 相关 Schemas 已迁移到 xcase app
# from xcase.schemas import (
#     FileNodeSchema, FileContentSchema, CasespaceItemSchema, CaseItemSchema,
#     SaveFileRequest, CreateFileRequest, CreateFolderRequest, RenameRequest,
#     UploadFileItem, UploadFilesRequest, CaseOptionSchema, CaseMetadataSchema,
#     CaseDetailSchema, AddTagRequest, DeleteTagRequest, AddOptionRequest,
#     UpdateOptionRequest, DeleteOptionRequest
# )


# TPGEN Saved Plan Schemas
class TpgenSavedPlanIn(Schema):
    """保存的测试计划输入模式"""
    name: str
    category: str
    description: Optional[str] = None
    config_data: dict = Field(..., alias='configData')
    yaml_data: Optional[dict] = Field(None, alias='yamlData')
    cpu: Optional[str] = None
    gpu: Optional[str] = None
    machine_count: int = Field(0, alias='machineCount')
    os_type: Optional[str] = Field(None, alias='osType')
    kernel_type: Optional[str] = Field(None, alias='kernelType')
    test_case_count: int = Field(0, alias='testCaseCount')
    status: int = 1
    tags: Optional[str] = None


class TpgenSavedPlanUpdate(Schema):
    """保存的测试计划更新模式（所有字段可选）"""
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    config_data: Optional[dict] = Field(None, alias='configData')
    yaml_data: Optional[dict] = Field(None, alias='yamlData')
    cpu: Optional[str] = None
    gpu: Optional[str] = None
    machine_count: Optional[int] = Field(None, alias='machineCount')
    os_type: Optional[str] = Field(None, alias='osType')
    kernel_type: Optional[str] = Field(None, alias='kernelType')
    test_case_count: Optional[int] = Field(None, alias='testCaseCount')
    status: Optional[int] = None
    tags: Optional[str] = None


