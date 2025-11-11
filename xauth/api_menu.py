from django.core.cache import cache
from ninja_extra import Router
from xauth import models
from xutils import utils
from xauth import schemas
from . import auth


router = Router()

@router.get('/tree', auth=auth.TitwPermAuth('system:menu:list'))
def get_menu_tree(request):
    data = cache.get('menu_tree')
    if not data:
        data = models.SysMenu.build_menu_tree(all=True)
        cache.set('menu_tree', data)
    resp = utils.RespSuccessTempl()
    resp.data = data
    return resp.as_dict()

@router.post('', auth=auth.TitwPermAuth('system:menu:add'))
def add_menu(request, menu: schemas.SysMenuIn):
    models.SysMenu.objects.create(**menu.dict())
    resp = utils.RespSuccessTempl()
    resp.data = dict()
    return resp.as_dict()

@router.get('/{id}', auth=auth.TitwPermAuth('system:menu:list'))
def get_menu(request, id: int):
    menu = models.SysMenu.objects.get(id=id)
    create_user = models.SysUser.objects.get(id=menu.create_user)
    resp = utils.RespSuccessTempl()
    resp.data = {
        "id": menu.id,
        "createUserString": create_user.nickname,
        "createTime": utils.dateformat(menu.create_time),
        "title": menu.title,
        "parentId": menu.parent_id,
        "type": menu.type,
        "path": menu.path,
        "name": menu.name,
        "component": menu.component,
        "redirect": menu.redirect,
        "icon": menu.icon,
        "isExternal": menu.is_external,
        "isCache": menu.is_cache,
        "isHidden": menu.is_hidden,
        "permission": menu.permission,
        "sort": menu.sort,
        "status": menu.status
    }
    return resp.as_dict()

@router.put('/{id}', auth=auth.TitwPermAuth('system:menu:update'))
def update_menu(request, id: int, menu: schemas.SysMenuIn):
    _menu = models.SysMenu.objects.get(id=id)
    for k,v in menu.dict().items():
        setattr(_menu, k, v)
    _menu.save()
    resp = utils.RespSuccessTempl()
    resp.data = dict()
    return resp.as_dict()

@router.delete('/{id}', auth=auth.TitwPermAuth('system:menu:delete'))
def delete_menus(request, id: int):
    models.SysMenu.delete_menus(id)
    resp = utils.RespSuccessTempl()
    resp.data = dict()
    return resp.as_dict()
