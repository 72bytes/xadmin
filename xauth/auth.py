from typing import Any
from django.db.models import Subquery 
from django.http import HttpRequest
from django.utils.translation import gettext_lazy as _
from django.conf import settings
from ninja_jwt.authentication import JWTAuth
from ninja_jwt.exceptions import AuthenticationFailed
from xauth import models
from loguru import logger


class TitwPermAuth(JWTAuth):
    def __init__(self, permission: str = ""):
        self.permission = permission
        super().__init__()

    def authenticate(self, request: HttpRequest, token: str) -> Any:
        user = self.jwt_authenticate(request, token)
        self.check_permission(request)
        return user

    def check_permission(self, request):
        if request.user.username == settings.TITW_SUPER_USER:
            return
        roles = models.SysUserRole.objects.filter(
            user_id=request.user.id
        ).values('role_id')
        menus = models.SysRoleMenu.objects.filter(
            role_id__in=Subquery(roles)
        ).values('menu_id')
        permissions = models.SysMenu.objects.filter(
            id__in=Subquery(menus)
        ).exclude(permission__isnull=True).exclude(permission='').values_list('permission', flat=True)
        if not bool(self.permission):
            return
        if self.permission not in tuple(permissions):
            logger.warning(f"user permissions: {tuple(permissions)}")
            logger.warning(f"user permission: {self.permission}")
            raise AuthenticationFailed(
                _("Forbidden: You don't have permission to access this API"),
                code=401
            )


class TitwBaseAuth(JWTAuth):
    def authenticate(self, request: HttpRequest, token: str) -> Any:
        logger.info(f"认证请求 - Token: {token[:50]}...")  # 只记录前50个字符
        try:
            user = self.jwt_authenticate(request, token)
            logger.info(f"认证成功 - 用户: {user.username}")
            if user.status == 2:
                raise AuthenticationFailed(
                    _("Forbidden: You don't have permission to access this API"),
                    code=401
                )
            return user
        except Exception as e:
            logger.error(f"认证失败: {str(e)}")
            raise
    
