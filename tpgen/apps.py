"""
Test Plan Generator App Configuration
测试计划生成器应用配置
"""
from django.apps import AppConfig


class TpgenConfig(AppConfig):
    """Test Plan Generator应用配置类"""
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'tpgen'
    verbose_name = 'Test Plan Generator'
    verbose_name_plural = 'Test Plan Generators'
    
    def ready(self):
        """应用就绪时的初始化"""
        # 可以在这里导入信号处理器等
        pass
