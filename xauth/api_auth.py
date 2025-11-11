from base64 import b64decode

# from uuid import uuid4
# from captcha.image import ImageCaptcha  # 验证码功能已注释
from django.conf import settings
from django.db.models import Q
from django.http import HttpRequest


# from django.utils import timezone
from loguru import logger
from ninja.responses import Response
from ninja_extra import Router
from ninja_jwt.tokens import RefreshToken

from xauth import models, schemas
from xutils import utils

# Create your views here.
router = Router()
# image = ImageCaptcha(width=111, height=36, font_sizes=[16])  # 验证码功能已注释


# 验证码接口已注释
# @router.get("/captcha/image", auth=None)
# def captcha(request):
#     code = "1289"
#     img = image.generate(code)
#     img = img.read()
#     img = b64encode(img).decode()
#     img = f"data:image/png;base64,{img}"
#     resp = utils.RespSuccessTempl()
#     resp.data = dict(
#         uuid=uuid4(),
#         img=img,
#         expireTime=int(
#             (timezone.now() + timezone.timedelta(days=1)).timestamp() * 1000
#         ),
#     )
#
#     return resp.as_dict()


@router.post("/login", auth=None)
def login(request: HttpRequest, data: schemas.SysUserLogin):
    try:
        user = models.SysUser.objects.get(username=data.username)
        if user.status == 2:
            resp = utils.RespFailedTempl()
            resp.data = {"error": "user has been disabled."}
            resp.code = 401
            resp.msg = "用户已被禁用！"
            return resp.as_dict()
        password = b64decode(data.password)
        # logger.info(f"user password: {password.decode()}")
        if user.check_password(password):
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)
            logger.info(
                f"登录成功 - 用户: {user.username}, Token: {access_token[:50]}..."
            )
            resp = utils.RespSuccessTempl()
            resp.data = dict(token=access_token)
            return resp.as_dict()
        else:
            resp = utils.RespFailedTempl()
            resp.data = {"error": "Invalid username or password"}
            resp.code = 401
            return Response(resp.as_dict(), status=401)
    except models.SysUser.DoesNotExist:
        resp = utils.RespFailedTempl()
        resp.data = {"error": "Invalid username or password"}
        resp.code = 401
        return Response(resp.as_dict(), status=401)


@router.post("/logout")
def logout(request):
    resp = utils.RespSuccessTempl()
    resp.data = dict()
    return resp.as_dict()


# User
@router.get("/route")
def get_user_route(request):
    user: models.SysUser = request.user
    if user.username == settings.TITW_SUPER_USER:
        routes = models.SysMenu.build_menu_tree(ids=None)
        resp = utils.RespSuccessTempl()
        resp.data = routes
        return resp.as_dict()
    else:
        roles = models.SysUserRole.objects.filter(user_id=user.id).values_list(
            "role_id", flat=True
        )
        menu_ids = models.SysRoleMenu.objects.filter(role_id__in=roles).values_list(
            "menu_id", flat=True
        )
        logger.info(f"menu_ids: {list(menu_ids)}")
        routes = models.SysMenu.build_menu_tree(ids=list(menu_ids))
        resp = utils.RespSuccessTempl()
        resp.data = routes
        return resp.as_dict()


@router.get("/user/info")
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
        ).values_list("permission", flat=True)
    data = dict(
        id=user.id,
        username=user.username,
        nickname=user.nickname,
        gender=user.gender,
        email=user.email or "",
        phone=user.phone or "",
        avatar=user.avatar or "",
        description=user.description or "",
        registrationDate=utils.dateformat(user.create_time),
        deptId=user.dept_id,
        deptName=dept.name,
        permissions=list(permissions),
        roles=list(role_names),
    )
    resp = utils.RespSuccessTempl()
    resp.data = data
    return resp.as_dict()
