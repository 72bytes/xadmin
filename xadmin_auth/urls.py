from http import HTTPStatus
from django.http import JsonResponse
from django.urls import path
from django.conf import urls as default_urls
from ninja_extra import NinjaExtraAPI
from ninja_jwt.exceptions import AuthenticationFailed
from xadmin_auth import auth
from xadmin_utils.utils import RespFailedTempl
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

from . import api_test_plan
from . import api_sut_device  # 新增这一行
from yaml_check import views as yaml_check_views  # 新增
from yaml_test_plan import api as yaml_test_plan_api  # YAML测试计划验证





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

api.add_router('test/plan', api_test_plan.router)
api.add_router('sut/device', api_sut_device.router)  # 新增这一行
api.add_router('yaml', yaml_check_views.router)  # 新增
api.add_router('yaml-test-plan', yaml_test_plan_api.router)  # YAML测试计划验证



# api.add_router('test/plan', api_test_plan.router)  # 暂时禁用


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