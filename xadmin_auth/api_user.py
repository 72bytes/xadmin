from base64 import b64decode, b64encode

from django.conf import settings
from django.db.models import OuterRef, Q, Subquery
from django.http import HttpRequest
from loguru import logger
from ninja import File
from ninja.files import UploadedFile
from ninja_extra import Router

from xadmin_db import models, schemas
from xadmin_utils import utils

from . import auth

router = Router()


@router.post("/avatar")
def upload_avatar(request, file: UploadedFile = File(..., alias="avatarFile")):
    avatar = b64encode(file.read()).decode()
    avatar = f"data:image/png;base64,{avatar}"
    request.user.avatar = avatar
    request.user.save()
    resp = utils.RespSuccessTempl()
    resp.data = dict(avatar=avatar)
    return resp.as_dict()


@router.get("/avatar")
def get_avatar(request):
    resp = utils.RespSuccessTempl()
    resp.data = dict(avatar=request.user.avatar)
    return resp.as_dict()


@router.get("/info")
def get_user_info(request: HttpRequest):
    user: models.SysUser = request.user
    dept = models.SysDept.objects.get(id=user.dept_id)
    role_ids = models.SysUserRole.objects.filter(user_id=user.id).values_list(
        "role_id", flat=True
    )
    role_names = models.SysRole.objects.filter(id__in=role_ids).values_list(
        "code", flat=True
    )
    menu_ids = models.SysRoleMenu.objects.filter(
        role_id__in=list(role_ids)
    ).values_list("menu_id", flat=True)
    if user.username == settings.TITW_SUPER_USER:
        permissions = ("*:*:*",)
    else:
        permissions = models.SysMenu.objects.filter(
            Q(id__in=menu_ids) & Q(type=3)
        ).exclude(permission__isnull=True).exclude(permission='').values_list("permission", flat=True)
    data = dict(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        gender=user.gender,
        email=user.email or "",
        phone=user.phone or "",
        avatar=user.avatar or "",
        description=user.description or "",
        deptId=user.dept_id,
        deptName=dept.name,
        permissions=list(permissions),
        roles=list(role_names),
    )
    resp = utils.RespSuccessTempl()
    resp.data = data
    return resp.as_dict()


@router.get("/list", auth=auth.TitwPermAuth("system:user:list"))
def user_list(request: HttpRequest):
    description = request.GET.get("description", False)
    status = request.GET.get("status", False)
    page = int(request.GET.get("page", 1))
    size = int(request.GET.get("size", 10))

    result = dict()
    _list = []
    dept_id = int(request.GET.get("deptId"))
    dept_ids = models.SysDept.objects.filter(ancestors__contains=str(dept_id)).values(
        "id"
    )
    dept_name_subquery = models.SysDept.objects.filter(id=OuterRef("dept_id")).values(
        "name"
    )[:1]

    filter = Q(dept_id__in=dept_ids) | Q(dept_id=dept_id)
    if description:
        filter = Q(description__icontains=description) & filter
    if status:
        filter = Q(status=int(status)) & filter
    users = models.SysUser.objects.filter(filter).annotate(
        dept_name=Subquery(dept_name_subquery)
    )[(page - 1) * size : page * size]
    for user in users:
        roles = models.SysUserRole.objects.filter(user_id=user.id).values_list(
            "role_id", flat=True
        )
        role_names = models.SysRole.objects.filter(id__in=roles).values_list(
            "name", flat=True
        )
        create_user = models.SysUser.objects.get(id=user.create_user)
        _list.append(
            dict(
                id=str(user.id),
                createUserString=create_user.username,
                createTime=utils.dateformat(user.create_time),
                disabled=False,
                updateUserString=user.update_user,
                updateTime=user.update_time,
                username=user.username,
                nickname=user.nickname,
                gender=user.gender,
                avatar=user.avatar or "",
                email=user.email,
                phone=user.phone,
                status=user.status,
                isSystem=user.is_system,
                description=user.description,
                deptId=user.dept_id,
                deptName=user.dept_name,
                roleIds=list(roles),
                roleNames=list(role_names),
            )
        )

    result["total"] = models.SysUser.objects.all().count()
    result["list"] = _list
    resp = utils.RespSuccessTempl()
    resp.data = result
    return resp.as_dict()


@router.post("", auth=auth.TitwPermAuth("system:user:add"))
def add_user(request, user_in: schemas.SysUserAdd):
    data = user_in.dict()
    role_ids = data.pop("role_ids")
    user = models.SysUser.objects.create(**data)
    user.create_user = request.user.id
    password = b64decode(user_in.password)
    logger.info(f"User created with password: {password.decode()}")
    user.set_password(password)
    user.save()
    models.SysUserRole.set_user_roles(user.id, role_ids)
    resp = utils.RespSuccessTempl()
    resp.data = dict()
    return resp.as_dict()


@router.get("/{id}", auth=auth.TitwPermAuth("system:user:list"))
def get_user(request, id: int):
    _user = models.SysUser.get_user_and_roles_by_id(id)
    resp = utils.RespSuccessTempl()
    resp.data = _user
    return resp.as_dict()


@router.delete("/{id}", auth=auth.TitwPermAuth("system:user:delete"))
def delete_user(request, id: int):
    user = models.SysUser.objects.get(id=id)
    user.delete()
    resp = utils.RespSuccessTempl()
    resp.data = dict()
    return resp.as_dict()


@router.put("/{id}", auth=auth.TitwPermAuth("system:user:update"))
def update_user(request, id: int, user_in: schemas.SysUserUpdate):
    exclude_fields = [
        "role_ids",
    ]
    _user = models.SysUser.objects.get(id=id)
    for k, v in user_in.dict().items():
        if k not in exclude_fields:
            setattr(_user, k, v)
    _user.save()
    models.SysUserRole.set_user_roles(id, user_in.role_ids)
    resp = utils.RespSuccessTempl()
    resp.data = dict()
    return resp.as_dict()


@router.patch("/{id}/password", auth=auth.TitwPermAuth("system:user:resetPwd"))
def reset_user_password(request, id: int, password: schemas.ResetUserPassword):
    user = models.SysUser.objects.get(id=id)
    user.set_password(b64decode(password.new_password))
    user.save()
    resp = utils.RespSuccessTempl()
    resp.data = dict()
    return resp.as_dict()


@router.patch("/{id}/role")
def reset_user_roles(request, id: int, role_ids: schemas.SetUserRoles):
    models.SysUserRole.set_user_roles(id, role_ids.role_ids)
    resp = utils.RespSuccessTempl()
    resp.data = dict()
    return resp.as_dict()


@router.patch("/basic/info")
def update_user_profile(request, profile: schemas.SysUserProfile):
    user = models.SysUser.objects.get(id=request.user.id)
    for k, v in profile.dict().items():
        setattr(user, k, v)
    user.save()
    resp = utils.RespSuccessTempl()
    resp.data = dict()
    return resp.as_dict()
