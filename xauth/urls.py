from http import HTTPStatus
from django.http import JsonResponse
from django.urls import path
from django.conf import urls as default_urls
from ninja_extra import NinjaExtraAPI
from ninja_jwt.exceptions import AuthenticationFailed
from xauth import auth
from xutils.utils import RespFailedTempl
from loguru import logger
from . import api_auth
from . import api_menu
from . import api_role
from . import api_user
from . import api_dept
from . import api_dict
from . import api_dict_item
from . import api_option
from . import api_common


api = NinjaExtraAPI(auth=auth.TitwBaseAuth(), 
                    title='xadmin', 
                    urls_namespace='xadmin')

api.add_router('user', api_user.router)
api.add_router('auth', api_auth.router)
api.add_router('role', api_role.router)
api.add_router('menu', api_menu.router)
api.add_router('dept', api_dept.router)
api.add_router('dict/item', api_dict_item.router)
api.add_router('dict', api_dict.router)
api.add_router('option', api_option.router)
api.add_router('common', api_common.router)

@api.exception_handler(AuthenticationFailed)
def handl_auth_fail(request, exception):
    resp = RespFailedTempl()
    # 安全获取 code 属性，如果不存在则使用 403
    resp.code = getattr(exception, 'code', 403)
    # 获取错误消息
    resp.data = str(exception) if str(exception) else 'Authentication failed'
    return JsonResponse(resp.as_dict(), status=resp.code)

def create_exception_handler(code: int):
    def handler(request, exception=None):
        logger.warning("handling exceptions....")
        logger.warning(type(exception))
        resp = RespFailedTempl()
        resp.code = code
        if code == HTTPStatus.NOT_FOUND:
            resp.data = 'the requested resource is not found'
        if code == HTTPStatus.BAD_REQUEST:
            resp.data = 'bad request'
        if code == HTTPStatus.FORBIDDEN:
            resp.data = 'you may do not have permission to access this resource'
        if code == HTTPStatus.INTERNAL_SERVER_ERROR:
            resp.data = 'internal server error'
        return JsonResponse(resp.as_dict(), status=code)
    return handler


urlpatterns = [
    path('', api.urls, name='system'),
]

default_urls.handler400 = create_exception_handler(HTTPStatus.BAD_REQUEST)
default_urls.handler403 = create_exception_handler(HTTPStatus.FORBIDDEN)
default_urls.handler404 = create_exception_handler(HTTPStatus.NOT_FOUND)
default_urls.handler500 = create_exception_handler(HTTPStatus.INTERNAL_SERVER_ERROR)