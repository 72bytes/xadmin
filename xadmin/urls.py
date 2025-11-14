"""
URL configuration for xadmin project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
# from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # path('admin/', admin.site.urls),
    path('system/', include('xauth.urls')),  # 认证和系统管理 API
    # TODO: xadmin_tpgen 需要 TpgenSavedPlan 模型，暂时禁用
    # path('tpgen/', include('xadmin_tpgen.urls')),  # TPGEN 管理后台 API
    path('tp/', include('tpgen.urls')),  # TPGEN 核心 API
]
