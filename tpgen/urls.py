"""
Test Plan Generator URL Configuration
测试计划生成器路由配置
"""
from http import HTTPStatus
from django.http import JsonResponse
from django.urls import path
from django.conf import urls as default_urls
from ninja_extra import NinjaExtraAPI
from ninja_jwt.exceptions import AuthenticationFailed
from xutils.utils import RespFailedTempl
from loguru import logger

# 导入视图
from . import views

# 导入 API 路由器
from .api import (
    sut_device_router,
    os_config_router,
    test_type_router,
    test_component_router,
    test_case_router,
    test_plan_router,
)


# 创建 API 实例（可选是否启用认证）
# 如果需要认证，使用: from xadmin_auth import auth
# ninja_api = NinjaExtraAPI(auth=auth.TitwBaseAuth(), title='TPGEN API', urls_namespace='tpgen-api')
# 暂时不启用认证，方便测试
ninja_api = NinjaExtraAPI(
    auth=None, 
    title='Test Plan Generator API',
    urls_namespace='tpgen'
)


# 注册所有路由
ninja_api.add_router('sut-device', sut_device_router)
ninja_api.add_router('os-config', os_config_router)
ninja_api.add_router('test-type', test_type_router)
ninja_api.add_router('test-component', test_component_router)
ninja_api.add_router('test-case', test_case_router)
ninja_api.add_router('test-plan', test_plan_router)


# 异常处理器
@ninja_api.exception_handler(AuthenticationFailed)
def handle_auth_fail(request, exception):
    """处理认证失败"""
    resp = RespFailedTempl()
    resp.code = getattr(exception, 'code', 403)
    resp.data = str(exception) if str(exception) else 'Authentication failed'
    return JsonResponse(resp.as_dict(), status=resp.code)


def create_exception_handler(code: int):
    """创建异常处理器工厂函数"""
    def handler(request, exception=None):
        logger.warning(f"Handling exception with code {code}")
        logger.warning(type(exception))
        resp = RespFailedTempl()
        resp.code = code
        if code == HTTPStatus.NOT_FOUND:
            resp.data = 'The requested resource is not found'
        elif code == HTTPStatus.BAD_REQUEST:
            resp.data = 'Bad request'
        elif code == HTTPStatus.FORBIDDEN:
            resp.data = 'You may not have permission to access this resource'
        elif code == HTTPStatus.INTERNAL_SERVER_ERROR:
            resp.data = 'Internal server error'
        return JsonResponse(resp.as_dict(), status=code)
    return handler


# URL 配置
# app_name = 'tpgen'  # 注释掉以避免与 ninja_api 的 urls_namespace 冲突

urlpatterns = [
    path('health', views.health_check, name='health_check'),
    path('api/', ninja_api.urls, name='tpgen'),
    path('', views.index, name='index'),
]

# 注册全局异常处理器
default_urls.handler400 = create_exception_handler(HTTPStatus.BAD_REQUEST)
default_urls.handler403 = create_exception_handler(HTTPStatus.FORBIDDEN)
default_urls.handler404 = create_exception_handler(HTTPStatus.NOT_FOUND)
default_urls.handler500 = create_exception_handler(HTTPStatus.INTERNAL_SERVER_ERROR)

