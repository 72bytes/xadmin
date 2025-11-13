"""
路由基础测试模块

【简化版】只测试基本的路由注册和无需认证的路由功能
暂不包含复杂的权限认证测试

测试策略：
1. 测试每个模块的主要路由是否存在（不是404）
2. 测试公开路由（如登录）是否可以访问
3. 基本的路由响应检查
"""

import pytest
from django.test import Client
from django.urls import resolve, Resolver404
import json


# ==================== Fixtures ====================

@pytest.fixture
def client():
    """Django测试客户端"""
    return Client()


@pytest.fixture
def test_yaml_data():
    """测试用的YAML数据"""
    return {
        "metadata": {
            "generated": "2025-11-13T08:00:00.000Z",
            "version": "1.0"
        },
        "hardware": {
            "cpu": "Intel",
            "gpu": "NVIDIA",
            "machines": []
        },
        "environment": {
            "os": {
                "method": "same",
                "os": "Ubuntu"
            },
            "deployment": {
                "kernel": {
                    "method": "same",
                    "type": "Mainline",
                    "version": "5.15"
                }
            },
            "firmware": {
                "gpu_version": {
                    "comparison": True
                }
            }
        },
        "test_suites": []
    }


# ==================== 基础路由测试 ====================

class TestBasicRoutes:
    """基础路由检查"""
    
    def test_login_route_registered(self):
        """测试登录路由是否已注册"""
        try:
            match = resolve('/system/auth/login')
            assert match is not None
        except Resolver404:
            pytest.fail("❌ 登录路由未注册: /system/auth/login")
    
    def test_yaml_validate_route_registered(self):
        """测试YAML验证路由是否已注册"""
        try:
            match = resolve('/system/yaml/validate')
            assert match is not None
        except Resolver404:
            pytest.fail("❌ YAML验证路由未注册: /system/yaml/validate")
    
    def test_common_dict_option_route_registered(self):
        """测试通用字典选项路由是否已注册"""
        try:
            match = resolve('/system/common/dict/option')
            assert match is not None
        except Resolver404:
            pytest.fail("❌ 字典选项路由未注册: /system/common/dict/option")


class TestLoginRoute:
    """测试登录路由（无需认证）"""
    
    def test_login_route_accessible(self, client):
        """测试登录路由是否可访问"""
        # 发送空请求，只检查路由是否存在（不是404）
        response = client.post('/system/auth/login', 
                              content_type='application/json',
                              data='{}')
        
        # 登录应该返回400（参数错误）或其他业务错误，但不应该是404
        assert response.status_code != 404, \
            f"登录路由不应该返回404，实际返回了 {response.status_code}"
        
        print(f"✅ 登录路由可访问，返回状态码: {response.status_code}")


class TestDictOptionRoute:
    """测试字典选项路由（无需认证）"""
    
    def test_dict_option_route_accessible(self, client):
        """测试字典选项路由是否可访问"""
        response = client.get('/system/common/dict/option')
        
        # 应该返回200或业务错误，但不应该是404
        assert response.status_code != 404, \
            f"字典选项路由不应该返回404，实际返回了 {response.status_code}"
        
        print(f"✅ 字典选项路由可访问，返回状态码: {response.status_code}")


class TestYamlRoutes:
    """YAML相关路由测试（基础）"""
    
    def test_yaml_validate_route_registered(self):
        """测试YAML验证路由是否已注册"""
        try:
            match = resolve('/system/yaml/validate')
            assert match is not None
            print("✅ YAML验证路由已注册")
        except Resolver404:
            pytest.fail("❌ YAML验证路由未注册")
    
    def test_yaml_validate_accepts_post(self, client):
        """测试YAML验证路由接受POST请求"""
        # 发送空数据，只检查是否接受POST方法
        response = client.post('/system/yaml/validate',
                              content_type='application/json',
                              data='{}')
        
        # 不应该返回404（路由不存在）或405（方法不允许）
        assert response.status_code != 404, \
            f"YAML验证路由不应该返回404，实际返回了 {response.status_code}"
        
        # 如果返回405，说明方法不允许
        if response.status_code == 405:
            pytest.fail("YAML验证路由不接受POST方法")
        
        print(f"✅ YAML验证路由接受POST请求，返回状态码: {response.status_code}")


class TestRouteRegistration:
    """批量路由注册检查"""
    
    def test_critical_routes_registered(self):
        """测试关键路由是否已注册"""
        critical_routes = [
            '/system/auth/login',
            '/system/yaml/validate',
            '/system/common/dict/option',
        ]
        
        failed_routes = []
        for route in critical_routes:
            try:
                resolve(route)
            except Resolver404:
                failed_routes.append(route)
        
        if failed_routes:
            pytest.fail(f"❌ 以下关键路由未注册: {failed_routes}")
        
        print(f"✅ 所有 {len(critical_routes)} 个关键路由已注册")


class TestHTTPMethods:
    """HTTP方法测试"""
    
    def test_login_only_accepts_post(self, client):
        """测试登录路由只接受POST请求"""
        # 尝试GET请求
        response = client.get('/system/auth/login')
        
        # 应该返回405（Method Not Allowed）或400/401，但不应该是200
        assert response.status_code in [405, 400, 401], \
            f"登录路由不应该接受GET请求，但返回了 {response.status_code}"
        
        print(f"✅ 登录路由正确拒绝GET请求，返回状态码: {response.status_code}")


# ==================== 路由统计信息 ====================

class TestRouteStats:
    """路由统计信息"""
    
    def test_count_registered_routes(self):
        """统计已注册的路由数量"""
        from django.urls import get_resolver
        
        resolver = get_resolver()
        patterns = []
        
        def collect_patterns(url_patterns, prefix=''):
            for pattern in url_patterns:
                if hasattr(pattern, 'url_patterns'):
                    new_prefix = prefix + str(pattern.pattern)
                    collect_patterns(pattern.url_patterns, new_prefix)
                else:
                    full_pattern = prefix + str(pattern.pattern)
                    patterns.append(full_pattern)
        
        collect_patterns(resolver.url_patterns)
        
        # 统计各个模块的路由
        system_routes = [p for p in patterns if 'system/' in p]
        yaml_routes = [p for p in patterns if 'yaml' in p.lower()]
        auth_routes = [p for p in patterns if 'auth' in p.lower()]
        
        print(f"\n📊 路由统计:")
        print(f"  - 总路由数: {len(patterns)}")
        print(f"  - system/ 路由: {len(system_routes)}")
        print(f"  - yaml 相关路由: {len(yaml_routes)}")
        print(f"  - auth 相关路由: {len(auth_routes)}")
        
        # 确保至少有一些路由被注册
        assert len(patterns) > 0, "❌ 没有发现任何路由"
        assert len(system_routes) > 0, "❌ 没有发现任何 system/ 路由"


# ==================== TPGEN Saved Plans Tests ====================

class TestTpgenSavedPlans:
    """TPGEN 保存的测试计划路由测试"""
    
    def test_saved_plans_list_route_exists(self):
        """测试保存的测试计划列表路由存在"""
        try:
            resolve('/tpgen/saved-plans/list')
            assert True, "✅ /tpgen/saved-plans/list 路由已注册"
        except Resolver404:
            pytest.fail("❌ /tpgen/saved-plans/list 路由未注册")
    
    def test_saved_plans_create_route_exists(self):
        """测试创建保存的测试计划路由存在"""
        try:
            resolve('/tpgen/saved-plans')
            assert True, "✅ /tpgen/saved-plans 路由已注册"
        except Resolver404:
            pytest.fail("❌ /tpgen/saved-plans 路由未注册")
    
    def test_saved_plans_detail_route_exists(self):
        """测试保存的测试计划详情路由存在"""
        try:
            resolve('/tpgen/saved-plans/1')
            assert True, "✅ /tpgen/saved-plans/{id} 路由已注册"
        except Resolver404:
            pytest.fail("❌ /tpgen/saved-plans/{id} 路由未注册")
    
    def test_saved_plans_categories_route_exists(self):
        """测试测试计划类别列表路由存在"""
        try:
            resolve('/tpgen/saved-plans/categories/list')
            assert True, "✅ /tpgen/saved-plans/categories/list 路由已注册"
        except Resolver404:
            pytest.fail("❌ /tpgen/saved-plans/categories/list 路由未注册")
