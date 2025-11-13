from django.http import HttpRequest
from django.db.models import Q
from ninja_extra import Router
from xadmin_tpgen import models, schemas
from xutils import utils
from datetime import datetime


router = Router()


@router.get('/list')
def get_saved_plan_list(request: HttpRequest):
    """获取保存的测试计划列表"""
    name = request.GET.get('name', '')
    category = request.GET.get('category', '')
    create_user = request.GET.get('createUser', '')
    status = request.GET.get('status', '')
    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('size', 10))
    
    result = dict()
    _list = []
    
    # 构建查询条件
    filter_q = Q()
    if name:
        filter_q &= Q(name__icontains=name)
    if category:
        filter_q &= Q(category=category)
    if create_user:
        filter_q &= Q(create_user=int(create_user))
    if status:
        filter_q &= Q(status=int(status))
    
    # 查询总数
    total = models.TpgenSavedPlan.objects.filter(filter_q).count()
    
    # 分页查询
    saved_plans = models.TpgenSavedPlan.objects.filter(filter_q).order_by('-create_time')[(page-1)*size:page*size]
    
    for plan in saved_plans:
        # 获取更新人信息
        update_user_name = ''
        if plan.update_user:
            try:
                update_user_obj = models.SysUser.objects.get(id=plan.update_user)
                update_user_name = update_user_obj.username
            except models.SysUser.DoesNotExist:
                update_user_name = ''
        
        _list.append(dict(
            id=str(plan.id),
            name=plan.name,
            category=plan.category,
            description=plan.description or '',
            cpu=plan.cpu or '',
            gpu=plan.gpu or '',
            machineCount=plan.machine_count,
            osType=plan.os_type or '',
            kernelType=plan.kernel_type or '',
            testCaseCount=plan.test_case_count,
            status=plan.status,
            tags=plan.tags or '',
            useCount=plan.use_count,
            lastUsedTime=utils.dateformat(plan.last_used_time) if plan.last_used_time else '',
            createUser=plan.create_user,
            createUserString=plan.create_user_name or '',
            createTime=utils.dateformat(plan.create_time),
            updateUser=plan.update_user,
            updateUserString=update_user_name,
            updateTime=utils.dateformat(plan.update_time) if plan.update_time else '',
        ))
    
    result['total'] = total
    result['list'] = _list
    
    resp = utils.RespSuccessTempl()
    resp.data = result
    return resp.as_dict()


@router.get('/{plan_id}')
def get_saved_plan(request: HttpRequest, plan_id: int):
    """获取单个保存的测试计划详情"""
    try:
        plan = models.TpgenSavedPlan.objects.get(id=plan_id)
        
        # 获取更新人信息
        update_user_name = ''
        if plan.update_user:
            try:
                update_user_obj = models.SysUser.objects.get(id=plan.update_user)
                update_user_name = update_user_obj.username
            except models.SysUser.DoesNotExist:
                update_user_name = ''
        
        data = dict(
            id=str(plan.id),
            name=plan.name,
            category=plan.category,
            description=plan.description or '',
            configData=plan.config_data,
            yamlData=plan.yaml_data,
            cpu=plan.cpu or '',
            gpu=plan.gpu or '',
            machineCount=plan.machine_count,
            osType=plan.os_type or '',
            kernelType=plan.kernel_type or '',
            testCaseCount=plan.test_case_count,
            status=plan.status,
            tags=plan.tags or '',
            useCount=plan.use_count,
            lastUsedTime=utils.dateformat(plan.last_used_time) if plan.last_used_time else '',
            createUser=plan.create_user,
            createUserString=plan.create_user_name or '',
            createTime=utils.dateformat(plan.create_time),
            updateUser=plan.update_user,
            updateUserString=update_user_name,
            updateTime=utils.dateformat(plan.update_time) if plan.update_time else '',
        )
        
        resp = utils.RespSuccessTempl()
        resp.data = data
        return resp.as_dict()
    except models.TpgenSavedPlan.DoesNotExist:
        resp = utils.RespFailedTempl()
        resp.data = '测试计划配置不存在'
        return resp.as_dict()


@router.post('')
def add_saved_plan(request: HttpRequest, plan: schemas.TpgenSavedPlanIn):
    """新增保存的测试计划"""
    try:
        import json
        
        # 获取当前用户信息
        current_user = request.user
        user_name = current_user.username if hasattr(current_user, 'username') else ''
        
        # 将 yaml_data 转换为字符串（如果是对象）
        yaml_data_str = plan.yaml_data
        if isinstance(plan.yaml_data, dict):
            yaml_data_str = json.dumps(plan.yaml_data, ensure_ascii=False, indent=2)
        
        # 创建测试计划配置
        saved_plan = models.TpgenSavedPlan.objects.create(
            name=plan.name,
            category=plan.category,
            description=plan.description,
            config_data=plan.config_data,
            yaml_data=yaml_data_str,
            cpu=plan.cpu,
            gpu=plan.gpu,
            machine_count=plan.machine_count,
            os_type=plan.os_type,
            kernel_type=plan.kernel_type,
            test_case_count=plan.test_case_count,
            status=plan.status,
            tags=plan.tags,
            create_user=current_user.id,
            create_user_name=user_name,
        )
        
        resp = utils.RespSuccessTempl()
        resp.data = dict(id=saved_plan.id)
        return resp.as_dict()
    except Exception as e:
        resp = utils.RespFailedTempl()
        resp.data = f'创建失败: {str(e)}'
        return resp.as_dict()


@router.put('/{plan_id}')
def update_saved_plan(request: HttpRequest, plan_id: int, plan: schemas.TpgenSavedPlanUpdate):
    """修改保存的测试计划"""
    try:
        import json
        
        saved_plan = models.TpgenSavedPlan.objects.get(id=plan_id)
        
        # 获取当前用户信息
        current_user = request.user
        user_name = current_user.username if hasattr(current_user, 'username') else ''
        
        # 更新字段（只更新非 None 的字段）
        if plan.name is not None:
            saved_plan.name = plan.name
        if plan.category is not None:
            saved_plan.category = plan.category
        if plan.description is not None:
            saved_plan.description = plan.description
        if plan.config_data is not None:
            saved_plan.config_data = plan.config_data
        if plan.yaml_data is not None:
            # 将 yaml_data 转换为字符串（如果是对象）
            yaml_data_str = plan.yaml_data
            if isinstance(plan.yaml_data, dict):
                yaml_data_str = json.dumps(plan.yaml_data, ensure_ascii=False, indent=2)
            saved_plan.yaml_data = yaml_data_str
        if plan.cpu is not None:
            saved_plan.cpu = plan.cpu
        if plan.gpu is not None:
            saved_plan.gpu = plan.gpu
        if plan.machine_count is not None:
            saved_plan.machine_count = plan.machine_count
        if plan.os_type is not None:
            saved_plan.os_type = plan.os_type
        if plan.kernel_type is not None:
            saved_plan.kernel_type = plan.kernel_type
        if plan.test_case_count is not None:
            saved_plan.test_case_count = plan.test_case_count
        if plan.status is not None:
            saved_plan.status = plan.status
        if plan.tags is not None:
            saved_plan.tags = plan.tags
        
        saved_plan.update_user = current_user.id
        saved_plan.update_user_name = user_name
        saved_plan.save()
        
        resp = utils.RespSuccessTempl()
        resp.data = dict(id=saved_plan.id)
        return resp.as_dict()
    except models.TpgenSavedPlan.DoesNotExist:
        resp = utils.RespFailedTempl()
        resp.data = '测试计划配置不存在'
        return resp.as_dict()
    except Exception as e:
        resp = utils.RespFailedTempl()
        resp.data = f'更新失败: {str(e)}'
        return resp.as_dict()


@router.delete('/{plan_ids}')
def delete_saved_plan(request: HttpRequest, plan_ids: str):
    """删除保存的测试计划（支持批量）"""
    try:
        id_list = plan_ids.split(',')
        deleted_count = models.TpgenSavedPlan.objects.filter(id__in=id_list).delete()[0]
        
        resp = utils.RespSuccessTempl()
        resp.data = dict(deleted=deleted_count)
        return resp.as_dict()
    except Exception as e:
        resp = utils.RespFailedTempl()
        resp.data = f'删除失败: {str(e)}'
        return resp.as_dict()


@router.post('/{plan_id}/use')
def use_saved_plan(request: HttpRequest, plan_id: int):
    """使用保存的测试计划（增加使用计数）"""
    try:
        saved_plan = models.TpgenSavedPlan.objects.get(id=plan_id)
        
        # 更新使用统计
        saved_plan.use_count += 1
        saved_plan.last_used_time = datetime.now()
        saved_plan.save()
        
        resp = utils.RespSuccessTempl()
        resp.data = dict(
            id=saved_plan.id,
            useCount=saved_plan.use_count
        )
        return resp.as_dict()
    except models.TpgenSavedPlan.DoesNotExist:
        resp = utils.RespFailedTempl()
        resp.data = '测试计划配置不存在'
        return resp.as_dict()
    except Exception as e:
        resp = utils.RespFailedTempl()
        resp.data = f'操作失败: {str(e)}'
        return resp.as_dict()


@router.get('/categories/list')
def get_categories(request: HttpRequest):
    """获取所有类别列表"""
    try:
        # 从数据库中获取所有不重复的类别
        categories = models.TpgenSavedPlan.objects.values_list('category', flat=True).distinct().order_by('category')
        
        resp = utils.RespSuccessTempl()
        resp.data = list(categories)
        return resp.as_dict()
    except Exception as e:
        resp = utils.RespFailedTempl()
        resp.data = f'获取失败: {str(e)}'
        return resp.as_dict()

