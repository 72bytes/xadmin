from django.http import HttpRequest
from django.db.models import Q
from ninja_extra import Router
from tpgen import models as tp_models
from tpgen import schemas as tp_schemas
from xadmin_db import models  # For SysUser
from xadmin_utils import utils
from datetime import datetime


router = Router()


@router.get('/list')
def get_test_plan_list(request: HttpRequest):
    """获取测试计划列表"""
    name = request.GET.get('name', '')
    code = request.GET.get('code', '')
    status = request.GET.get('status', '')
    priority = request.GET.get('priority', '')
    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('size', 10))
    
    result = dict()
    _list = []
    
    # 构建查询条件
    filter_q = Q()
    if name:
        filter_q &= Q(name__icontains=name)
    if code:
        filter_q &= Q(code__icontains=code)
    if status:
        filter_q &= Q(status=int(status))
    if priority:
        filter_q &= Q(priority=int(priority))
    
    # 查询总数
    total = tp_models.TestPlan.objects.filter(filter_q).count()
    
    # 分页查询
    test_plans = tp_models.TestPlan.objects.filter(filter_q).order_by('-created_at')[(page-1)*size:page*size]
    
    for plan in test_plans:
        # 获取创建人和更新人信息
        create_user = models.SysUser.objects.get(id=plan.create_user)
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
            code=plan.code,
            description=plan.description or '',
            startTime=utils.dateformat(plan.start_time) if plan.start_time else '',
            endTime=utils.dateformat(plan.end_time) if plan.end_time else '',
            ownerId=plan.owner_id,
            ownerName=plan.owner_name or '',
            priority=plan.priority,
            status=plan.status,
            testType=plan.test_type or '',
            testEnv=plan.test_env or '',
            relatedProject=plan.related_project or '',
            remark=plan.remark or '',
            createUser=plan.create_user,
            createUserString=create_user.username,
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
def get_test_plan(request: HttpRequest, plan_id: int):
    """获取单个测试计划详情"""
    try:
        plan = tp_models.TestPlan.objects.get(id=plan_id)
        
        # 获取创建人和更新人信息
        create_user = models.SysUser.objects.get(id=plan.create_user)
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
            code=plan.code,
            description=plan.description or '',
            startTime=utils.dateformat(plan.start_time) if plan.start_time else '',
            endTime=utils.dateformat(plan.end_time) if plan.end_time else '',
            ownerId=plan.owner_id,
            ownerName=plan.owner_name or '',
            priority=plan.priority,
            status=plan.status,
            testType=plan.test_type or '',
            testEnv=plan.test_env or '',
            relatedProject=plan.related_project or '',
            remark=plan.remark or '',
            createUser=plan.create_user,
            createUserString=create_user.username,
            createTime=utils.dateformat(plan.create_time),
            updateUser=plan.update_user,
            updateUserString=update_user_name,
            updateTime=utils.dateformat(plan.update_time) if plan.update_time else '',
        )
        
        resp = utils.RespSuccessTempl()
        resp.data = data
        return resp.as_dict()
    except models.TestPlan.DoesNotExist:
        resp = utils.RespFailedTempl()
        resp.data = '测试计划不存在'
        return resp.as_dict()


@router.post('')
def add_test_plan(request: HttpRequest, plan: tp_schemas.TestPlanIn):
    """新增测试计划"""
    try:
        # 检查编号是否已存在
        if tp_models.TestPlan.objects.filter(code=plan.code).exists():
            resp = utils.RespFailedTempl()
            resp.data = '测试计划编号已存在'
            return resp.as_dict()
        
        # 处理时间字段
        start_time = None
        end_time = None
        if plan.start_time:
            try:
                start_time = datetime.fromisoformat(plan.start_time.replace('Z', '+00:00'))
            except:
                pass
        if plan.end_time:
            try:
                end_time = datetime.fromisoformat(plan.end_time.replace('Z', '+00:00'))
            except:
                pass
        
        # 创建测试计划
        test_plan = tp_models.TestPlan.objects.create(
            name=plan.name,
            code=plan.code,
            description=plan.description,
            start_time=start_time,
            end_time=end_time,
            owner_id=plan.owner_id,
            owner_name=plan.owner_name,
            priority=plan.priority,
            status=plan.status,
            test_type=plan.test_type,
            test_env=plan.test_env,
            related_project=plan.related_project,
            remark=plan.remark,
            create_user=request.user.id,
        )
        
        resp = utils.RespSuccessTempl()
        resp.data = dict(id=test_plan.id)
        return resp.as_dict()
    except Exception as e:
        resp = utils.RespFailedTempl()
        resp.data = f'创建失败: {str(e)}'
        return resp.as_dict()


@router.put('/{plan_id}')
def update_test_plan(request: HttpRequest, plan_id: int, plan: tp_schemas.TestPlanIn):
    """修改测试计划"""
    try:
        test_plan = tp_models.TestPlan.objects.get(id=plan_id)
        
        # 检查编号是否被其他记录占用
        if tp_models.TestPlan.objects.filter(code=plan.code).exclude(id=plan_id).exists():
            resp = utils.RespFailedTempl()
            resp.data = '测试计划编号已存在'
            return resp.as_dict()
        
        # 处理时间字段
        start_time = None
        end_time = None
        if plan.start_time:
            try:
                start_time = datetime.fromisoformat(plan.start_time.replace('Z', '+00:00'))
            except:
                pass
        if plan.end_time:
            try:
                end_time = datetime.fromisoformat(plan.end_time.replace('Z', '+00:00'))
            except:
                pass
        
        # 更新测试计划
        test_plan.name = plan.name
        test_plan.code = plan.code
        test_plan.description = plan.description
        test_plan.start_time = start_time
        test_plan.end_time = end_time
        test_plan.owner_id = plan.owner_id
        test_plan.owner_name = plan.owner_name
        test_plan.priority = plan.priority
        test_plan.status = plan.status
        test_plan.test_type = plan.test_type
        test_plan.test_env = plan.test_env
        test_plan.related_project = plan.related_project
        test_plan.remark = plan.remark
        test_plan.update_user = request.user.id
        test_plan.save()
        
        resp = utils.RespSuccessTempl()
        resp.data = dict(id=test_plan.id)
        return resp.as_dict()
    except models.TestPlan.DoesNotExist:
        resp = utils.RespFailedTempl()
        resp.data = '测试计划不存在'
        return resp.as_dict()
    except Exception as e:
        resp = utils.RespFailedTempl()
        resp.data = f'更新失败: {str(e)}'
        return resp.as_dict()


@router.delete('/{plan_ids}')
def delete_test_plan(request: HttpRequest, plan_ids: str):
    """删除测试计划（支持批量）"""
    try:
        id_list = plan_ids.split(',')
        deleted_count = tp_models.TestPlan.objects.filter(id__in=id_list).delete()[0]
        
        resp = utils.RespSuccessTempl()
        resp.data = dict(deleted=deleted_count)
        return resp.as_dict()
    except Exception as e:
        resp = utils.RespFailedTempl()
        resp.data = f'删除失败: {str(e)}'
        return resp.as_dict()


