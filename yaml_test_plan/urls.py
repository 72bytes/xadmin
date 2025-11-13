from django.urls import path
from ninja_extra import NinjaExtraAPI
from xauth import auth
from .api import router

# 创建 NinjaExtraAPI 实例并添加路由
api = NinjaExtraAPI(
    auth=auth.XadminBaseAuth(),
    title='YAML Test Plan API',
    urls_namespace='yaml-test-plan'
)
api.add_router('', router)

urlpatterns = [
    path('api/', api.urls),
]

