"""
Pytest 配置文件
定义全局 fixtures 和测试配置
"""

import os
import pytest
import django
from django.conf import settings
from django.test import Client
from django.contrib.auth import get_user_model

# 设置 Django 环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xadmin.settings')
django.setup()

User = get_user_model()


# ==================== 数据库 Fixtures ====================

@pytest.fixture(scope='session')
def django_db_setup():
    """
    Django 数据库设置
    scope='session' 表示整个测试会话只执行一次
    """
    settings.DATABASES['default'] = {
        'ENGINE': 'django.db.backends.postgresql',
        'CONN_HEALTH_CHECKS': True,          # ✅ 添加这个
        'CONN_MAX_AGE': 0,                   # ✅ 添加这个
        'AUTOCOMMIT': True,                  # ✅ 添加这个
        'ATOMIC_REQUESTS': False,            # ✅ 添加这个
        'OPTIONS': {},                        # ✅ 添加这个
        'TIME_ZONE': None,                   # ✅ 添加这个
        'NAME': 'test_xadmin',  # 测试数据库名称
        'USER': settings.DATABASES['default']['USER'],
        'PASSWORD': settings.DATABASES['default']['PASSWORD'],
        'HOST': settings.DATABASES['default']['HOST'],
        'PORT': settings.DATABASES['default']['PORT'],
        'OPTIONS': settings.DATABASES['default'].get('OPTIONS', {}),
        'ATOMIC_REQUESTS': settings.DATABASES['default'].get('ATOMIC_REQUESTS', False),
        'TIME_ZONE': settings.DATABASES['default'].get('TIME_ZONE', None),  # 添加 TIME_ZONE 配置
        
        'CONN_MAX_AGE': settings.DATABASES['default'].get('CONN_MAX_AGE', 0),  # 添加 CONN_MAX_AGE 配置
    }


@pytest.fixture
def db_access(db):
    """
    提供数据库访问权限
    使用 @pytest.mark.django_db 或这个 fixture 来访问数据库
    """
    return db


# ==================== 用户 Fixtures ====================

@pytest.fixture
def test_user(db):
    """
    创建测试用户
    """
    user = User.objects.create_user(
        username='testuser',
        password='testpass123',
        email='test@example.com'
    )
    return user


@pytest.fixture
def admin_user(db):
    """
    创建管理员用户
    """
    user = User.objects.create_superuser(
        username='admin',
        password='admin123',
        email='admin@example.com'
    )
    return user


# ==================== 客户端 Fixtures ====================

@pytest.fixture
def api_client():
    """
    Django 测试客户端
    """
    return Client()


@pytest.fixture
def authenticated_client(api_client, test_user):
    """
    已认证的测试客户端 (使用 Session 认证 - 用于 Django 视图)
    """
    api_client.force_login(test_user)
    return api_client


@pytest.fixture
def authenticated_api_client(api_client, auth_token):
    """
    已认证的 API 测试客户端 (使用 JWT 认证 - 用于 Ninja API)
    返回一个客户端和 token 的元组
    """
    return api_client, auth_token


@pytest.fixture
def admin_client(api_client, admin_user):
    """
    管理员客户端 (使用 Session 认证 - 用于 Django 视图)
    """
    api_client.force_login(admin_user)
    return api_client


@pytest.fixture
def admin_api_client(api_client, admin_headers):
    """
    管理员 API 客户端 (使用 JWT 认证 - 用于 Ninja API)
    返回一个客户端和认证头的元组
    """
    return api_client, admin_headers


# ==================== Token Fixtures ====================

@pytest.fixture
def auth_token(test_user):
    """
    获取认证 token
    """
    from ninja_jwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(test_user)
    return str(refresh.access_token)


@pytest.fixture
def admin_token(admin_user):
    """
    获取管理员 token
    """
    from ninja_jwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(admin_user)
    return str(refresh.access_token)


@pytest.fixture
def auth_headers(auth_token):
    """
    认证请求头
    """
    return {
        'HTTP_AUTHORIZATION': f'Bearer {auth_token}',
        'CONTENT_TYPE': 'application/json'
    }


@pytest.fixture
def admin_headers(admin_token):
    """
    管理员认证请求头
    """
    return {
        'HTTP_AUTHORIZATION': f'Bearer {admin_token}',
        'CONTENT_TYPE': 'application/json'
    }


# ==================== YAML 测试 Fixtures ====================

@pytest.fixture
def sample_yaml_data():
    """
    示例 YAML 测试数据
    """
    return {
        'metadata': {
            'generated': '2025-01-01T00:00:00Z',
            'version': '1.0'
        },
        'hardware': {
            'cpu': 'Ryzen Threadripper',
            'gpu': 'Radeon RX 7900 XTX',
            'machines': [
                {
                    'id': 1,
                    'name': 'Test Machine 1',
                    'specs': {
                        'motherboard': 'ASUS',
                        'gpu': 'Radeon RX 7900 XTX',
                        'cpu': 'Ryzen Threadripper'
                    }
                }
            ]
        },
        'environment': {
            'os': {
                'method': 'same',
                'os': 'Ubuntu 22.04',
                'deployment': 'bare-metal'
            },
            'kernel': {
                'method': 'same',
                'type': 'mainline',
                'version': '6.5.0'
            }
        },
        'test_suites': [
            {
                'id': 1,
                'name': 'Benchmark Test',
                'description': 'Performance benchmark',
                'type': 'benchmark'
            }
        ]
    }


# ==================== 测试配置 Hooks ====================

def pytest_configure(config):
    """
    Pytest 配置钩子
    """
    # 设置测试环境变量
    os.environ['TESTING'] = 'True'
    os.environ['DJANGO_DEBUG'] = 'False'
    
    # 注册自定义标记
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )


def pytest_collection_modifyitems(config, items):
    """
    修改测试项集合
    自动为某些测试添加标记
    """
    for item in items:
        # 为 API 测试自动添加 api 标记
        if "api" in item.nodeid:
            item.add_marker(pytest.mark.api)
        
        # 为需要数据库的测试自动添加 db 标记
        if "db" in item.fixturenames:
            item.add_marker(pytest.mark.db)


@pytest.fixture(autouse=True)
def reset_database(db):
    """
    每次测试后重置数据库
    autouse=True 表示自动应用到所有测试
    """
    yield
    # 测试完成后的清理工作
    # Django 会自动回滚事务，这里可以添加额外的清理逻辑


# ==================== 临时文件 Fixtures ====================

@pytest.fixture
def tmp_yaml_file(tmp_path):
    """
    创建临时 YAML 文件
    """
    yaml_file = tmp_path / "test.yaml"
    return yaml_file


# ==================== 日志 Fixtures ====================

@pytest.fixture
def caplog_info(caplog):
    """
    捕获 INFO 级别以上的日志
    """
    import logging
    caplog.set_level(logging.INFO)
    return caplog

