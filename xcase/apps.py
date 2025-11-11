"""
Django App 配置
"""
from django.apps import AppConfig


class XcaseConfig(AppConfig):
    """XCase App 配置"""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'xcase'
    verbose_name = '用例管理'
    
    def ready(self):
        """App 准备就绪时的初始化"""
        pass

