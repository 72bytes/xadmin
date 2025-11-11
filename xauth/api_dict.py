from django.http import HttpRequest
from django.db.models import Q
from django.forms.models import model_to_dict
from ninja_extra import Router
from xauth import models
from xutils import utils
from xauth import schemas
from . import auth


router = Router()

@router.get('/list', auth=auth.TitwPermAuth('system:dict:list'))
def get_dict_list(request: HttpRequest):
    keyword = request.GET.get('description', False)
    if not keyword:
        _dict = models.SysDict.objects.all()
    else:
        _dict = models.SysDict.objects.filter(
            Q(description__icontains=keyword) | 
            Q(name__icontains=keyword) |
            Q(value__icontains=keyword)
        )
    data = []
    for _d in _dict:
        record = model_to_dict(_d)
        data.append(record)
    resp = utils.RespSuccessTempl()
    resp.data = data
    return resp.as_dict()

@router.post('', auth=auth.TitwPermAuth('system:dict:add'))
def add_dict(request, dict_schema: schemas.SysDictIn):
    models.SysDict.objects.create(**dict_schema.dict())
    resp = utils.RespSuccessTempl()
    resp.data = 0
    return resp.as_dict()

@router.put('/{id}', auth=auth.TitwPermAuth('system:dict:update'))
def update_dict(request, id: int, dict_schema: schemas.SysDictIn):
    _dict = models.SysDict.objects.get(id=id)
    for k,v in dict_schema.dict().items():
        setattr(_dict, k, v)
    _dict.save()
    resp = utils.RespSuccessTempl()
    resp.data = dict()
    return resp.as_dict()

@router.delete('/{id}', auth=auth.TitwPermAuth('system:dict:delete'))
def delete_dict(request, id: int):
    models.SysDict.objects.filter(
        id=id
    ).delete()
    resp = utils.RespSuccessTempl()
    resp.data = dict()
    return resp.as_dict()

@router.get('/{id}', auth=auth.TitwPermAuth('system:dict:list'))
def get_dict(request, id: int):
    _dict = models.SysDict.objects.get(id=id)
    resp = utils.RespSuccessTempl()
    resp.data = model_to_dict(_dict)
    return resp.as_dict()