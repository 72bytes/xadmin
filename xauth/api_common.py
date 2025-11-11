from django.http import HttpRequest
from django.db.models import F, Q
from django.core.files.storage import FileSystemStorage
from django.core.cache import cache
from django.conf import settings
from ninja_extra import Router
from ninja import File
from ninja.files import UploadedFile
from xauth import models
from xutils import utils


router = Router()

@router.get('/dict/data_scope_enum')
def get_data_scope_enum(request):
    resp = utils.RespSuccessTempl()
    resp.data = settings.TITW_DATA_SCOPE
    return resp.as_dict()

@router.get('/dict/role')
def get_dict_role(request: HttpRequest):
    roles = models.SysRole.objects.annotate(
        label=F('name'), value=F('id')
    ).values('label', 'value')
    resp = utils.RespSuccessTempl()
    resp.data = list(roles)
    return resp.as_dict()

@router.get('/dict/option', auth=None)
def get_dict_option(request: HttpRequest):
    category = request.GET.get('category', False)
    filters= Q()
    if category:
        filters = Q(category=category)
    items = models.SysOption.objects.filter(
        filters
    ).values('code', 'value'
    ).annotate(label=F('code')
    ).values('label', 'value')
    resp = utils.RespSuccessTempl()
    resp.data = list(items)
    return resp.as_dict()

@router.get('/dict/{code}')
def get_dict(request, code: str):
    dict_id = models.SysDict.objects.get(code=code)
    dict_items = models.SysDictItem.objects.filter(
        dict_id=dict_id.id
    ).values('id', 'label', 'color'
    ).annotate(value=F('id')
    ).values('label', 'value', 'color')
    resp = utils.RespSuccessTempl()
    resp.data = list(dict_items)
    return resp.as_dict()

@router.post('/file')
def add_file(request, file: UploadedFile=File(...)):
    fs = FileSystemStorage(location=settings.TITW_WEB_ROOT, base_url='/')
    fs.delete(file.name)
    fs.save(file.name, file)
    resp = utils.RespSuccessTempl()
    resp.data = dict(url=fs.base_url+file.name)
    return resp.as_dict()

@router.get('/tree/dept')
def get_dept_tree(request: HttpRequest):
    data = cache.get('common_dept_tree')
    if not data:
        data = models.SysDept.build_dept_tree(choice=True, status=1)
        cache.set('common_dept_treee', data)
    resp = utils.RespSuccessTempl()
    resp.data = data
    return resp.as_dict()

@router.get('/tree/menu')
def get_menu_tree(request: HttpRequest):
    data = cache.get('common_menu_tree')
    if not data:
        data = models.SysMenu.build_menu_tree(choice=True)
        cache.set('common_menu_tree', data)
    resp = utils.RespSuccessTempl()
    resp.data = data
    return resp.as_dict()
