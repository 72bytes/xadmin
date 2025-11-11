"""
Test Plan Generator Views
测试计划生成器视图
"""
from django.shortcuts import render
from django.http import JsonResponse, HttpRequest


def index(request: HttpRequest):
    """TPGEN 首页视图"""
    return JsonResponse({
        'message': 'Welcome to Test Plan Generator (TPGEN)',
        'version': '1.0.0',
        'status': 'ok',
        'api_docs': '/tpgen/api/docs',
        'api_endpoints': {
            'sut_device': '/tpgen/api/sut-device',
            'os_config': '/tpgen/api/os-config',
            'test_type': '/tpgen/api/test-type',
            'test_component': '/tpgen/api/test-component',
            'test_case': '/tpgen/api/test-case',
            'test_plan': '/tpgen/api/test-plan',
        }
    })


def health_check(request: HttpRequest):
    """健康检查视图"""
    return JsonResponse({
        'status': 'healthy',
        'service': 'tpgen',
    })
