"""
Test Plan Generator API Routers
测试计划生成器 API 路由定义
"""
from django.http import HttpRequest
from ninja_extra import Router
from typing import List
from . import models, schemas
from xadmin_utils import utils


# ============================================================================
# SutDevice (测试设备) API
# ============================================================================

sut_device_router = Router(tags=['SUT Device'])


@sut_device_router.get('/list', response=dict)
def list_sut_devices(request: HttpRequest, 
                     hostname: str = None,
                     gpu_model: str = None,
                     page: int = 1,
                     size: int = 10):
    """获取测试设备列表"""
    queryset = models.SutDevice.objects.all()
    
    if hostname:
        queryset = queryset.filter(hostname__icontains=hostname)
    if gpu_model:
        queryset = queryset.filter(gpu_model__icontains=gpu_model)
    
    total = queryset.count()
    devices = queryset.order_by('-created_at')[(page-1)*size:page*size]
    
    data = {
        'total': total,
        'list': [
            {
                'id': d.id,
                'hostname': d.hostname,
                'asicName': d.asic_name,
                'ipAddress': d.ip_address,
                'deviceId': d.device_id,
                'revId': d.rev_id,
                'gpuSeries': d.gpu_series,
                'gpuModel': d.gpu_model,
                'createdAt': utils.dateformat(d.created_at),
                'updatedAt': utils.dateformat(d.updated_at),
            }
            for d in devices
        ]
    }
    
    resp = utils.RespSuccessTempl()
    resp.data = data
    return resp.as_dict()


@sut_device_router.get('/{device_id}', response=dict)
def get_sut_device(request: HttpRequest, device_id: int):
    """获取单个测试设备详情"""
    try:
        device = models.SutDevice.objects.get(id=device_id)
        data = {
            'id': device.id,
            'hostname': device.hostname,
            'asicName': device.asic_name,
            'ipAddress': device.ip_address,
            'deviceId': device.device_id,
            'revId': device.rev_id,
            'gpuSeries': device.gpu_series,
            'gpuModel': device.gpu_model,
            'createdAt': utils.dateformat(device.created_at),
            'updatedAt': utils.dateformat(device.updated_at),
        }
        resp = utils.RespSuccessTempl()
        resp.data = data
        return resp.as_dict()
    except models.SutDevice.DoesNotExist:
        resp = utils.RespFailedTempl()
        resp.data = '设备不存在'
        return resp.as_dict()


@sut_device_router.post('', response=dict)
def create_sut_device(request: HttpRequest, payload: schemas.SutDeviceIn):
    """创建测试设备"""
    try:
        device = models.SutDevice.objects.create(
            hostname=payload.hostname,
            asic_name=payload.asic_name,
            ip_address=payload.ip_address,
            device_id=payload.device_id,
            rev_id=payload.rev_id,
            gpu_series=payload.gpu_series,
            gpu_model=payload.gpu_model,
        )
        resp = utils.RespSuccessTempl()
        resp.data = {'id': device.id}
        return resp.as_dict()
    except Exception as e:
        resp = utils.RespFailedTempl()
        resp.data = f'创建失败: {str(e)}'
        return resp.as_dict()


@sut_device_router.put('/{device_id}', response=dict)
def update_sut_device(request: HttpRequest, device_id: int, payload: schemas.SutDeviceIn):
    """更新测试设备"""
    try:
        device = models.SutDevice.objects.get(id=device_id)
        device.hostname = payload.hostname
        device.asic_name = payload.asic_name
        device.ip_address = payload.ip_address
        device.device_id = payload.device_id
        device.rev_id = payload.rev_id
        device.gpu_series = payload.gpu_series
        device.gpu_model = payload.gpu_model
        device.save()
        
        resp = utils.RespSuccessTempl()
        resp.data = {'id': device.id}
        return resp.as_dict()
    except models.SutDevice.DoesNotExist:
        resp = utils.RespFailedTempl()
        resp.data = '设备不存在'
        return resp.as_dict()
    except Exception as e:
        resp = utils.RespFailedTempl()
        resp.data = f'更新失败: {str(e)}'
        return resp.as_dict()


@sut_device_router.delete('/{device_ids}', response=dict)
def delete_sut_devices(request: HttpRequest, device_ids: str):
    """删除测试设备（支持批量）"""
    try:
        id_list = device_ids.split(',')
        deleted_count = models.SutDevice.objects.filter(id__in=id_list).delete()[0]
        
        resp = utils.RespSuccessTempl()
        resp.data = {'deleted': deleted_count}
        return resp.as_dict()
    except Exception as e:
        resp = utils.RespFailedTempl()
        resp.data = f'删除失败: {str(e)}'
        return resp.as_dict()


# ============================================================================
# OsConfig (操作系统配置) API
# ============================================================================

os_config_router = Router(tags=['OS Config'])


@os_config_router.get('/list', response=dict)
def list_os_configs(request: HttpRequest,
                   os_family: str = None,
                   page: int = 1,
                   size: int = 10):
    """获取操作系统配置列表"""
    queryset = models.OsConfig.objects.all()
    
    if os_family:
        queryset = queryset.filter(os_family__icontains=os_family)
    
    total = queryset.count()
    configs = queryset.order_by('-created_at')[(page-1)*size:page*size]
    
    data = {
        'total': total,
        'list': [
            {
                'id': c.id,
                'osFamily': c.os_family,
                'version': c.version,
                'downloadUrl': c.download_url,
                'createdAt': utils.dateformat(c.created_at),
                'updatedAt': utils.dateformat(c.updated_at),
            }
            for c in configs
        ]
    }
    
    resp = utils.RespSuccessTempl()
    resp.data = data
    return resp.as_dict()


@os_config_router.post('', response=dict)
def create_os_config(request: HttpRequest, payload: schemas.OsConfigIn):
    """创建操作系统配置"""
    try:
        config = models.OsConfig.objects.create(
            os_family=payload.os_family,
            version=payload.version,
            download_url=payload.download_url,
        )
        resp = utils.RespSuccessTempl()
        resp.data = {'id': config.id}
        return resp.as_dict()
    except Exception as e:
        resp = utils.RespFailedTempl()
        resp.data = f'创建失败: {str(e)}'
        return resp.as_dict()


# ============================================================================
# TestType (测试类型) API
# ============================================================================

test_type_router = Router(tags=['Test Type'])


@test_type_router.get('/list', response=dict)
def list_test_types(request: HttpRequest):
    """获取所有测试类型"""
    types = models.TestType.objects.all().order_by('type_name')
    
    data = [
        {
            'id': t.id,
            'typeName': t.type_name,
            'createdAt': utils.dateformat(t.created_at),
            'updatedAt': utils.dateformat(t.updated_at),
        }
        for t in types
    ]
    
    resp = utils.RespSuccessTempl()
    resp.data = data
    return resp.as_dict()


@test_type_router.post('', response=dict)
def create_test_type(request: HttpRequest, payload: schemas.TestTypeIn):
    """创建测试类型"""
    try:
        test_type = models.TestType.objects.create(
            type_name=payload.type_name
        )
        resp = utils.RespSuccessTempl()
        resp.data = {'id': test_type.id}
        return resp.as_dict()
    except Exception as e:
        resp = utils.RespFailedTempl()
        resp.data = f'创建失败: {str(e)}'
        return resp.as_dict()


# ============================================================================
# TestComponent (测试组件) API
# ============================================================================

test_component_router = Router(tags=['Test Component'])


@test_component_router.get('/list', response=dict)
def list_test_components(request: HttpRequest,
                        test_type_id: int = None,
                        component_category: str = None):
    """获取测试组件列表"""
    queryset = models.TestComponent.objects.all()
    
    if test_type_id:
        queryset = queryset.filter(test_type_id=test_type_id)
    if component_category:
        queryset = queryset.filter(component_category=component_category)
    
    components = queryset.order_by('component_name')
    
    data = [
        {
            'id': c.id,
            'testTypeId': c.test_type_id,
            'componentCategory': c.component_category,
            'componentName': c.component_name,
        }
        for c in components
    ]
    
    resp = utils.RespSuccessTempl()
    resp.data = data
    return resp.as_dict()


@test_component_router.post('', response=dict)
def create_test_component(request: HttpRequest, payload: schemas.TestComponentIn):
    """创建测试组件"""
    try:
        component = models.TestComponent.objects.create(
            test_type_id=payload.test_type_id,
            component_category=payload.component_category,
            component_name=payload.component_name,
        )
        resp = utils.RespSuccessTempl()
        resp.data = {'id': component.id}
        return resp.as_dict()
    except Exception as e:
        resp = utils.RespFailedTempl()
        resp.data = f'创建失败: {str(e)}'
        return resp.as_dict()


# ============================================================================
# TestCase (测试用例) API
# ============================================================================

test_case_router = Router(tags=['Test Case'])


@test_case_router.get('/list', response=dict)
def list_test_cases(request: HttpRequest,
                   test_component_id: int = None,
                   page: int = 1,
                   size: int = 10):
    """获取测试用例列表"""
    queryset = models.TestCase.objects.all()
    
    if test_component_id:
        queryset = queryset.filter(test_component_id=test_component_id)
    
    total = queryset.count()
    cases = queryset.order_by('-created_at')[(page-1)*size:page*size]
    
    data = {
        'total': total,
        'list': [
            {
                'id': c.id,
                'testComponentId': c.test_component_id,
                'caseName': c.case_name,
                'caseConfig': c.case_config,
                'createdAt': utils.dateformat(c.created_at),
                'updatedAt': utils.dateformat(c.updated_at),
            }
            for c in cases
        ]
    }
    
    resp = utils.RespSuccessTempl()
    resp.data = data
    return resp.as_dict()


@test_case_router.post('', response=dict)
def create_test_case(request: HttpRequest, payload: schemas.TestCaseIn):
    """创建测试用例"""
    try:
        test_case = models.TestCase.objects.create(
            test_component_id=payload.test_component_id,
            case_name=payload.case_name,
            case_config=payload.case_config,
        )
        resp = utils.RespSuccessTempl()
        resp.data = {'id': test_case.id}
        return resp.as_dict()
    except Exception as e:
        resp = utils.RespFailedTempl()
        resp.data = f'创建失败: {str(e)}'
        return resp.as_dict()


# ============================================================================
# TestPlan (测试计划) API
# ============================================================================

test_plan_router = Router(tags=['Test Plan'])


@test_plan_router.get('/list', response=dict)
def list_test_plans(request: HttpRequest,
                   plan_name: str = None,
                   page: int = 1,
                   size: int = 10):
    """获取测试计划列表"""
    queryset = models.TestPlan.objects.all()
    
    if plan_name:
        queryset = queryset.filter(plan_name__icontains=plan_name)
    
    total = queryset.count()
    plans = queryset.order_by('-created_at')[(page-1)*size:page*size]
    
    data = {
        'total': total,
        'list': [
            {
                'id': p.id,
                'planName': p.plan_name,
                'planDescription': p.plan_description,
                'sutDeviceId': p.sut_device_id,
                'osConfigId': p.os_config_id,
                'createdBy': p.created_by,
                'createdAt': utils.dateformat(p.created_at),
                'updatedAt': utils.dateformat(p.updated_at),
            }
            for p in plans
        ]
    }
    
    resp = utils.RespSuccessTempl()
    resp.data = data
    return resp.as_dict()


@test_plan_router.get('/{plan_id}', response=dict)
def get_test_plan(request: HttpRequest, plan_id: int):
    """获取测试计划详情（包含关联的测试用例）"""
    try:
        plan = models.TestPlan.objects.get(id=plan_id)
        
        # 获取关联的测试用例
        plan_cases = models.TestPlanCase.objects.filter(test_plan=plan).select_related('test_case')
        cases = [
            {
                'id': pc.test_case.id,
                'caseName': pc.test_case.case_name,
                'timeout': pc.timeout,
            }
            for pc in plan_cases
        ]
        
        data = {
            'id': plan.id,
            'planName': plan.plan_name,
            'planDescription': plan.plan_description,
            'sutDeviceId': plan.sut_device_id,
            'osConfigId': plan.os_config_id,
            'createdBy': plan.created_by,
            'createdAt': utils.dateformat(plan.created_at),
            'updatedAt': utils.dateformat(plan.updated_at),
            'testCases': cases,
        }
        
        resp = utils.RespSuccessTempl()
        resp.data = data
        return resp.as_dict()
    except models.TestPlan.DoesNotExist:
        resp = utils.RespFailedTempl()
        resp.data = '测试计划不存在'
        return resp.as_dict()


@test_plan_router.post('', response=dict)
def create_test_plan(request: HttpRequest, payload: schemas.TestPlanIn):
    """创建测试计划"""
    try:
        plan = models.TestPlan.objects.create(
            plan_name=payload.plan_name,
            plan_description=payload.plan_description,
            sut_device_id=payload.sut_device_id,
            os_config_id=payload.os_config_id,
            created_by=payload.created_by,
        )
        resp = utils.RespSuccessTempl()
        resp.data = {'id': plan.id}
        return resp.as_dict()
    except Exception as e:
        resp = utils.RespFailedTempl()
        resp.data = f'创建失败: {str(e)}'
        return resp.as_dict()


@test_plan_router.delete('/{plan_ids}', response=dict)
def delete_test_plans(request: HttpRequest, plan_ids: str):
    """删除测试计划（支持批量）"""
    try:
        id_list = plan_ids.split(',')
        deleted_count = models.TestPlan.objects.filter(id__in=id_list).delete()[0]
        
        resp = utils.RespSuccessTempl()
        resp.data = {'deleted': deleted_count}
        return resp.as_dict()
    except Exception as e:
        resp = utils.RespFailedTempl()
        resp.data = f'删除失败: {str(e)}'
        return resp.as_dict()

