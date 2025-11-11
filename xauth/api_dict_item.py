from django.http import HttpRequest
from django.db.models import Q
from django.forms.models import model_to_dict
from ninja_extra import Router
from xauth import models
from xutils import utils
from xauth import schemas
from . import auth


router = Router()

@router.get('/list', auth=auth.TitwPermAuth('system:dict:item:list'))
def get_dict_item_list(request: HttpRequest):
    description = request.GET.get('description', False)
    status = request.GET.get('status', False)
    dict_id = request.GET.get('dictId', False)
    page = int(request.GET.get('page', 1))
    size = int(request.GET.get('size', 10))
    sort = request.GET.get('sort', False)
    desc = ''
    order_by = 'id'

    filters = Q()

    if sort:
        _sort = [_.strip() for _ in sort.split(',')]
        if 'desc' in _sort:
            desc = '-'
            _sort.remove('desc')
        if len(_sort) == 1:
            order_by = utils.camel_to_snake(_sort[0])
    if description:
        filters = Q(description__icontains=description)
    if status:
        filters = filters | Q(status=int(status))
    if dict_id:
        filters = filters | Q(dict_id=int(dict_id))
    
    if filters is not None:
        _items = models.SysDictItem.objects.filter(
            filters
        )
        total = models.SysDictItem.objects.filter(dict_id=int(dict_id)).count()
        items = _items.order_by(f'{desc}{order_by}')[(page-1)*size:page*size]
    else:
        _items = models.SysDictItem.objects.all(
        )
        total = _items.count()
        items = _items.order_by('dict_id')[(page-1)*size:page*size]
    data = dict()
    data['list'] = []
    data['total'] = total
    for item in items:
        data['list'].append(
            dict(
                id = item.id,
                createUserString = item.create_user,
                createTime = utils.dateformat(item.create_time),
                updateUserString = item.update_user,
                updateTime = utils.dateformat(item.update_time) if item.update_time else None,
                label = item.label,
                value = item.value,
                color = item.color,
                status = item.status,
                sort = item.sort,
                description = item.description,
                deptId = item.dict_id,
            )
        )
    resp = utils.RespSuccessTempl()
    resp.data = data
    return resp.as_dict()

@router.post('', auth=auth.TitwPermAuth('system:dict:item:add'))
def add_dict_item(request, dict_item: schemas.SysDictItemIn):
    models.SysDictItem.objects.create(**dict_item.dict())
    resp = utils.RespSuccessTempl()
    resp.data = 0
    return resp.as_dict()

@router.put('/{id}', auth=auth.TitwPermAuth('system:dict:item:update'))
def update_dict_item(request, id: int, dict_item: schemas.SysDictItemIn):
    _dict_item = models.SysDictItem.objects.get(id=id)
    for k,v in dict_item.dict().items():
        setattr(_dict_item, k, v)
    _dict_item.save()
    resp = utils.RespSuccessTempl()
    resp.data = dict()
    return resp.as_dict()

@router.delete('/{id}', auth=auth.TitwPermAuth('system:dict:item:delete'))
def delete_dict_items(request, id: int):
    models.SysDictItem.objects.filter(
        id=id
    ).delete()
    resp = utils.RespSuccessTempl()
    resp.data = dict()
    return resp.as_dict()

@router.get('/{id}', auth=auth.TitwPermAuth('system:dict:item:list'))
def get_dict_item(request, id: int):
    _item = models.SysDictItem.objects.get(id=id)
    resp = utils.RespSuccessTempl()
    resp.data = model_to_dict(_item)
    return resp.as_dict()