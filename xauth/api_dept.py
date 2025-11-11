from django.core.cache import cache
from ninja_extra import Router
from xauth import models
from xutils import utils
from xauth import schemas
from . import auth


router = Router()

@router.get('/export', auth=auth.TitwPermAuth('system:dept:list'))
def export_department(request):
    pass

@router.get('/tree', auth=auth.TitwPermAuth('system:dept:list'))
def get_department_tree(request):
    resp = utils.RespSuccessTempl()
    data = []
    status = request.GET.get('status')
    if status not in (None, ''):
        if int(status) == 1:
            data = cache.get('dept_enabled_tree')
            if not data:
                data = models.SysDept.build_dept_tree(status=int(status))
                cache.set('dept_enabled_tree', data)
        else:
            data = cache.get('dept_disabled_tree')
            if not data:
                data = []
                depts = models.SysDept.objects.filter(
                    status=int(status)
                )
                for dept in depts:
                    dept = {
                        'id': dept.id,
                        'parentId': dept.parent_id,
                        'name': dept.name or "",
                        'sort': dept.sort,
                        'status': dept.status,
                        'isSystem': bool(dept.is_system),
                        'description': dept.description,
                        'createUser': dept.create_user,
                        'createUserString': 'fake',
                        'createTime': utils.dateformat(dept.create_time),
                        'updateUser': dept.update_user,
                        'updateUserString': 'fake',
                        'updateTime': dept.update_time,
                    }
                    data.append(dept)
                cache.set('dept_disabled_tree', data)
    else:
        data = cache.get('dept_tree')
        if not data:
            data = models.SysDept.build_dept_tree()
            cache.set('dept_tree', data)

    resp.data = data
    return resp.as_dict()

@router.post('', auth=auth.TitwPermAuth('system:dept:add'))
def add_department(request, dept: schemas.SysDeptAdd):
    parent = models.SysDept.objects.get(id=dept.parent_id)
    _data = dept.dict()
    _data['ancestors'] = f'{parent.ancestors},{parent.id}'
    models.SysDept.objects.create(**_data)
    resp = utils.RespSuccessTempl()
    resp.data = dict()
    return resp.as_dict()

@router.get('/{id}', auth=auth.TitwPermAuth('system:dept:list'))
def get_department(request, id: int):
    dept = models.SysDept.objects.get(id=id)
    data = {
        'id': dept.id,
        'parentId': dept.parent_id,
        'name': dept.name or "",
        'sort': dept.sort,
        'status': dept.status,
        'isSystem': bool(dept.is_system),
        'description': dept.description,
        'createUser': dept.create_user,
        'createUserString': 'fake',
        'createTime': utils.dateformat(dept.create_time),
        'updateUser': dept.update_user,
        'updateUserString': 'fake',
        'updateTime': dept.update_time,
    }
    resp = utils.RespSuccessTempl()
    resp.data = data
    return resp.as_dict()

@router.put('/{id}', auth=auth.TitwPermAuth('system:dept:update'))
def update_department(request, id: int, dept: schemas.SysDeptAdd):
    parent = models.SysDept.objects.get(id=dept.parent_id)
    _dept = models.SysDept.objects.get(id=id)
    for k,v in dept.dict().items():
        setattr(_dept, k, v)
    _dept.ancestors = f'{parent.ancestors},{parent.id}'
    _dept.save()
    resp = utils.RespSuccessTempl()
    resp.data = dict()
    return resp.as_dict()

@router.delete('/{id}', auth=auth.TitwPermAuth('system:dept:delete'))
def delete_departments(request, id: int):
    models.SysDept.delete_depts(id)
    resp = utils.RespSuccessTempl()
    resp.data = dict()
    return resp.as_dict()

