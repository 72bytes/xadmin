from django.http import HttpRequest
from django.db.models import F
from ninja_extra import Router
from xauth import models
from xutils import utils
from xauth import schemas
from . import auth


router = Router()

@router.get('', auth=auth.TitwPermAuth('system:option:list'))
def get_option(request: HttpRequest):
    resp = utils.RespSuccessTempl()
    resp.data = list()
    category = request.GET.get('category', False)
    if not category:
        return resp.as_dict()
    options = models.SysOption.objects.filter(
        category=category
    ).values('id', 'name', 'code', 'value', 'description')
    resp.data = list(options)
    return resp.as_dict()

@router.put('', auth=auth.TitwPermAuth('system:option:update'))
def update_option(request, options: schemas.SysOptionUpdate):
    for item in options:
        _item = models.SysOption.objects.get(id=item.id)
        for k, v in item.dict().items():
            setattr(_item, k, v)
        _item.save()
    resp = utils.RespSuccessTempl()
    resp.data = dict()
    return resp.as_dict()

@router.patch('', auth=auth.TitwPermAuth('system:option:update'))
def reset_option(request, category: schemas.SysOptionResetIn):
    models.SysOption.objects.filter(
        category=category.category
    ).update(value=F('default_value'))
    resp = utils.RespSuccessTempl()
    resp.data = dict()
    return resp.as_dict()
