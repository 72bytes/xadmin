from django.db.models import signals
from django.dispatch import receiver
from django.core.cache import cache
from django_currentuser.middleware import get_current_authenticated_user
from loguru import logger
from xauth import models


@receiver(signals.post_save, sender=models.SysDept)
def update_cache_after_dept_save(sender, instance, created, **kwargs):
    dept_tree = models.SysDept.build_dept_tree()
    cache.set('dept_tree', dept_tree)
    dept_enabled_tree = models.SysDept.build_dept_tree(status=1)
    cache.set('dept_enabled_tree', dept_enabled_tree)
    dept_disabled_tree = models.SysDept.build_dept_tree(status=2)
    cache.set('dept_disabled_tree', dept_disabled_tree)
    common_dept_tree = models.SysDept.build_dept_tree(choice=True, status=1)
    cache.set('common_dept_tree', common_dept_tree)

@receiver(signals.post_delete, sender=models.SysDept)
def update_cache_after_dept_delete(sender, instance, using, **kwargs):
    dept_tree = models.SysDept.build_dept_tree()
    cache.set('dept_tree', dept_tree)
    dept_enabled_tree = models.SysDept.build_dept_tree(status=1)
    cache.set('dept_enabled_tree', dept_enabled_tree)
    dept_disabled_tree = models.SysDept.build_dept_tree(status=2)
    cache.set('dept_disabled_tree', dept_disabled_tree)
    common_dept_tree = models.SysDept.build_dept_tree(choice=True, status=1)
    cache.set('common_dept_tree', common_dept_tree)

@receiver(signals.post_save, sender=models.SysMenu)
def update_cache_after_menu_save(sender, instance, created, **kwargs):
    menu_tree = models.SysMenu.build_menu_tree(all=True)
    cache.set('menu_tree', menu_tree)
    common_menu_tree = models.SysMenu.build_menu_tree(choice=True)
    cache.set('common_menu_tree', common_menu_tree)

@receiver(signals.post_delete, sender=models.SysMenu)
def update_cache_after_menu_delete(sender, instance, using, **kwargs):
    menu_tree = models.SysMenu.build_menu_tree(all=True)
    cache.set('menu_tree', menu_tree)
    common_menu_tree = models.SysMenu.build_menu_tree(choice=True)
    cache.set('common_menu_tree', common_menu_tree)

@receiver(signals.pre_save, sender=models.SysDept)
@receiver(signals.pre_save, sender=models.SysDict)
@receiver(signals.pre_save, sender=models.SysDictItem)
@receiver(signals.pre_save, sender=models.SysMenu)
@receiver(signals.pre_save, sender=models.SysOption)
@receiver(signals.pre_save, sender=models.SysRole)
@receiver(signals.pre_save, sender=models.SysUser)
def update_cu_user(sender, instance, raw, using, update_fields, **kwargs):
    cu = get_current_authenticated_user()
    if not bool(instance.id):
        instance.create_user = cu.id
        instance.update_user = cu.id
    else:
        instance.update_user = cu.id
