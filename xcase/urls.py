"""
XCase URL 配置

配置用例管理模块的所有 URL 路由。
"""
from http import HTTPStatus
from django.http import JsonResponse
from django.urls import path
from django.conf import urls as default_urls
from ninja_extra import NinjaExtraAPI
from ninja_jwt.exceptions import AuthenticationFailed
from loguru import logger

from xauth import auth
from xutils.utils import RespFailedTempl
from . import api_caseeditor
from . import api_casebrowser


# 创建独立的 API 实例
api = NinjaExtraAPI(
    auth=auth.TitwBaseAuth(),
    title='XCase API',
    version='1.0.0',
    description='用例管理模块 API',
    urls_namespace='xcase'
)

# 注册路由
api.add_router('caseeditor', api_caseeditor.router)
api.add_router('casebrowser', api_casebrowser.router)


# 异常处理器
@api.exception_handler(AuthenticationFailed)
def handle_auth_fail(request, exception):
    """处理认证失败异常"""
    resp = RespFailedTempl()
    resp.code = getattr(exception, 'code', 403)
    resp.data = str(exception) if str(exception) else 'Authentication failed'
    return JsonResponse(resp.as_dict(), status=resp.code)


def create_exception_handler(code: int):
    """创建通用异常处理器"""
    def handler(request, exception=None):
        logger.warning(f"HTTP {code} error in XCase: {exception}")
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
        else:
            resp.data = f'HTTP {code} error'
        
        return JsonResponse(resp.as_dict(), status=code)
    
    return handler


# URL 模式
urlpatterns = [
    path('', api.urls, name='xcase'),
]

# 配置异常处理（如果需要自定义）
# default_urls.handler400 = create_exception_handler(HTTPStatus.BAD_REQUEST)
# default_urls.handler403 = create_exception_handler(HTTPStatus.FORBIDDEN)
# default_urls.handler404 = create_exception_handler(HTTPStatus.NOT_FOUND)
# default_urls.handler500 = create_exception_handler(HTTPStatus.INTERNAL_SERVER_ERROR)

