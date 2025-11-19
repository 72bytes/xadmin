from http import HTTPStatus
from django.http import JsonResponse
from django.urls import path
from django.conf import urls as default_urls
from ninja_extra import NinjaExtraAPI
from ninja_jwt.exceptions import AuthenticationFailed
from xauth import auth
from xutils.utils import RespFailedTempl
from loguru import logger
from . import api_saved_plan


api = NinjaExtraAPI(auth=auth.XadminBaseAuth(), 
                    title='xadmin_tpgen', 
                    urls_namespace='xadmin_tpgen')

# 添加保存的计划管理路由
api.add_router('saved-plans', api_saved_plan.router)


@api.exception_handler(AuthenticationFailed)
def handl_auth_fail(request, exception):
    resp = RespFailedTempl()
    resp.code = getattr(exception, 'code', 403)
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
    path('', api.urls, name='tpgen'),
]

default_urls.handler400 = create_exception_handler(HTTPStatus.BAD_REQUEST)
default_urls.handler403 = create_exception_handler(HTTPStatus.FORBIDDEN)
default_urls.handler404 = create_exception_handler(HTTPStatus.NOT_FOUND)
default_urls.handler500 = create_exception_handler(HTTPStatus.INTERNAL_SERVER_ERROR)

