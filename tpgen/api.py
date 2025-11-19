"""
Test Plan Generator API Routers
测试计划生成器 API 路由定义
"""
from django.http import HttpRequest
from ninja_extra import Router
from typing import List
from . import models, schemas
from xutils import utils


# ============================================================================
# SutDevice (测试设备) API
# ============================================================================

sut_device_router = Router(tags=['SUT Device'])


@sut_device_router.get('/product-names')
def get_product_names(request: HttpRequest):
    """获取所有产品系列名称（去重）"""
    from django.db.models import Count
    
    # 获取所有不为空的 product_name，并计数
    product_names = (
        models.SutDevice.objects
        .filter(product_name__isnull=False)
        .values('product_name')
        .annotate(count=Count('id'))
        .order_by('product_name')
    )
    
    data = [
        {
            'label': pn['product_name'].capitalize() if pn['product_name'] else '',
            'value': pn['product_name'],
            'count': pn['count']
        }
        for pn in product_names if pn['product_name']
    ]
    
    resp = utils.RespSuccessTempl()
    resp.data = data
    return resp.as_dict()


@sut_device_router.get('/asic-names')
def get_asic_names(request: HttpRequest, productName: str = None):
    """获取 ASIC 名称列表（可根据 productName 过滤）"""
    queryset = models.SutDevice.objects.filter(asic_name__isnull=False)
    
    # 如果提供了 productName，则过滤
    if productName:
        queryset = queryset.filter(product_name=productName)
    
    # 获取唯一的 ASIC 名称
    asic_names = (
        queryset
        .values('asic_name')
        .distinct()
        .order_by('asic_name')
    )
    
    data = [
        {
            'label': asic['asic_name'],
            'value': asic['asic_name']
        }
        for asic in asic_names
    ]
    
    resp = utils.RespSuccessTempl()
    resp.data = data
    return resp.as_dict()


@sut_device_router.get('/machines')
def get_machines_by_selection(request: HttpRequest, 
                               productName: str = None, 
                               asicName: str = None):
    """
    根据 product_name 和 asic_name 筛选获取机器列表
    用于 Available Test Machines 展示
    """
    try:
        queryset = models.SutDevice.objects.all()
        
        # 根据 productName 过滤
        if productName:
            queryset = queryset.filter(product_name=productName)
        
        # 根据 asicName 过滤
        if asicName:
            queryset = queryset.filter(asic_name=asicName)
        
        # 构造返回数据，hostname作为主标题
        machines = queryset.order_by('hostname')
        result = [
            {
                'id': m.id,
                'hostname': m.hostname,
                'asicName': m.asic_name,
                'productName': m.product_name,
                'ipAddress': m.ip_address,
                'deviceId': m.device_id,
                'revId': m.rev_id,
                'gpuSeries': m.gpu_series,
                'gpuModel': m.gpu_model,
                'createdAt': utils.dateformat(m.created_at),
                'updatedAt': utils.dateformat(m.updated_at),
            }
            for m in machines
        ]
        
        resp = utils.RespSuccessTempl()
        resp.data = result
        return resp.as_dict()
    
    except Exception as e:
        print(f'[get_machines_by_selection] Error: {str(e)}')
        resp = utils.RespFailedTempl()
        resp.message = f'获取机器列表失败: {str(e)}'
        return resp.as_dict()


@sut_device_router.get('/list')
def list_sut_devices(request: HttpRequest, 
                     hostname: str = None,
                     gpu_model: str = None,
                     page: int = 1,
                     size: int = 10):
    """获取测试设备列表"""
    from django.db import connection
    
    # 构建 SQL 查询（使用原始 SQL 绕过 ORM 缓存问题）
    where_clauses = []
    params = []
    
    if hostname:
        where_clauses.append("hostname ILIKE %s")
        params.append(f'%{hostname}%')
    if gpu_model:
        where_clauses.append("gpu_model ILIKE %s")
        params.append(f'%{gpu_model}%')
    
    where_sql = "WHERE " + " AND ".join(where_clauses) if where_clauses else ""
    
    # 获取总数
    count_sql = f"SELECT COUNT(*) FROM sut_devices {where_sql}"
    with connection.cursor() as cursor:
        cursor.execute(count_sql, params)
        total = cursor.fetchone()[0]
    
    # 获取数据列表
    offset = (page - 1) * size
    list_sql = f"""
        SELECT id, hostname, asic_name, product_name, ip_address, 
               device_id, rev_id, gpu_series, gpu_model, created_at, updated_at
        FROM sut_devices 
        {where_sql}
        ORDER BY created_at DESC
        LIMIT %s OFFSET %s
    """
    
    with connection.cursor() as cursor:
        cursor.execute(list_sql, params + [size, offset])
        columns = [col[0] for col in cursor.description]
        devices = [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    data = {
        'total': total,
        'list': [
            {
                'id': d['id'],
                'hostname': d['hostname'],
                'asicName': d['asic_name'],
                'productName': d['product_name'],
                'ipAddress': str(d['ip_address']) if d['ip_address'] else None,
                'deviceId': d['device_id'],
                'revId': d['rev_id'],
                'gpuSeries': d['gpu_series'],
                'gpuModel': d['gpu_model'],
                'createdAt': utils.dateformat(d['created_at']),
                'updatedAt': utils.dateformat(d['updated_at']),
            }
            for d in devices
        ]
    }
    
    resp = utils.RespSuccessTempl()
    resp.data = data
    return resp.as_dict()


@sut_device_router.get('/{device_id}')
def get_sut_device(request: HttpRequest, device_id: int):
    """获取单个测试设备详情"""
    try:
        device = models.SutDevice.objects.get(id=device_id)
        data = {
            'id': device.id,
            'hostname': device.hostname,
            'asicName': device.asic_name,
            'productName': device.product_name,
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


@sut_device_router.post('')
def create_sut_device(request: HttpRequest, payload: schemas.SutDeviceIn):
    """创建测试设备"""
    try:
        device = models.SutDevice.objects.create(
            hostname=payload.hostname,
            asic_name=payload.asic_name,
            product_name=payload.product_name,
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


@sut_device_router.put('/{device_id}')
def update_sut_device(request: HttpRequest, device_id: int, payload: schemas.SutDeviceIn):
    """更新测试设备"""
    try:
        device = models.SutDevice.objects.get(id=device_id)
        device.hostname = payload.hostname
        device.asic_name = payload.asic_name
        device.product_name = payload.product_name
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


@sut_device_router.delete('/{device_ids}')
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


@os_config_router.get('/list')
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


@os_config_router.get('/options')
def get_os_options(request: HttpRequest):
    """获取所有 OS 选项（用于下拉框）"""
    configs = models.OsConfig.objects.all().order_by('os_family', 'version')
    
    data = [
        {
            'id': c.id,
            'label': f"{c.os_family} {c.version}",
            'value': str(c.id),
            'osFamily': c.os_family,
            'version': c.version
        }
        for c in configs
    ]
    
    resp = utils.RespSuccessTempl()
    resp.data = data
    return resp.as_dict()


@os_config_router.get('/{config_id}/kernels')
def get_os_kernels(request: HttpRequest, config_id: int):
    """获取指定 OS 配置支持的内核版本"""
    try:
        config = models.OsConfig.objects.get(id=config_id)
        kernels = models.OsSupportedKernel.objects.filter(os_config=config).order_by('kernel_version')
        
        data = [
            {
                'id': k.id,
                'label': k.kernel_version,
                'value': k.kernel_version
            }
            for k in kernels
        ]
        
        resp = utils.RespSuccessTempl()
        resp.data = data
        return resp.as_dict()
    except models.OsConfig.DoesNotExist:
        resp = utils.RespFailedTempl()
        resp.data = 'OS配置不存在'
        return resp.as_dict()


@os_config_router.get('/kernels/all')
def get_all_kernel_types(request: HttpRequest):
    """获取所有内核类型（去重）"""
    kernels = models.OsSupportedKernel.objects.values('kernel_version').distinct().order_by('kernel_version')
    
    data = [
        {
            'label': k['kernel_version'],
            'value': k['kernel_version']
        }
        for k in kernels
    ]
    
    resp = utils.RespSuccessTempl()
    resp.data = data
    return resp.as_dict()


@os_config_router.post('')
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


@test_type_router.get('/list')
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


@test_type_router.get('/options')
def get_test_type_options(request: HttpRequest):
    """获取测试类型选项（用于下拉框）"""
    types = models.TestType.objects.all().order_by('type_name')
    
    data = [
        {
            'id': t.id,
            'label': t.type_name,
            'value': str(t.id)
        }
        for t in types
    ]
    
    resp = utils.RespSuccessTempl()
    resp.data = data
    return resp.as_dict()


@test_type_router.post('')
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


@test_component_router.get('/list')
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


@test_component_router.post('')
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


@test_case_router.get('/search')
def search_test_cases(request: HttpRequest, keyword: str = ''):
    """搜索所有测试用例（用于搜索框自动完成）"""
    queryset = models.TestCase.objects.select_related(
        'test_component',
        'test_component__test_type'
    ).all()
    
    if keyword:
        queryset = queryset.filter(case_name__icontains=keyword)
    
    # 限制返回数量，避免数据过多
    cases = queryset.order_by('case_name')[:50]
    
    data = [
        {
            'id': c.id,
            'caseName': c.case_name,
            'componentId': c.test_component_id,
            'componentName': c.test_component.component_name if c.test_component else '',
            'category': c.test_component.component_category if c.test_component else '',
            'testTypeId': c.test_component.test_type_id if c.test_component else None,
            'testTypeName': c.test_component.test_type.type_name if c.test_component and c.test_component.test_type else '',
        }
        for c in cases
    ]
    
    resp = utils.RespSuccessTempl()
    resp.data = data
    return resp.as_dict()


@test_case_router.get('/list')
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


@test_case_router.post('')
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


@test_plan_router.get('/list')
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


@test_plan_router.get('/{plan_id}')
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


@test_plan_router.post('')
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


@test_plan_router.delete('/{plan_ids}')
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

