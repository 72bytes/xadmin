from django.apps import AppConfig


class XadminAuthConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'xauth'

    def ready(self):
        from xauth import signals  # 启用信号处理
        return True

