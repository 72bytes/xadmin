# Generated manually for Case Editor menu

from django.db import migrations


def add_caseeditor_menu(apps, schema_editor):
    """Add Case Editor menu and permissions"""
    SysMenu = apps.get_model('xauth', 'SysMenu')
    SysRole = apps.get_model('xauth', 'SysRole')
    SysRoleMenu = apps.get_model('xauth', 'SysRoleMenu')
    
    # Get admin user ID (assuming ID 1)
    admin_user_id = 1
    
    # Create "开发工具" directory menu
    dev_menu = SysMenu.objects.create(
        title='开发工具',
        parent_id=0,
        type=1,  # Directory
        path='/dev',
        name='Dev',
        component='Layout',
        icon='icon-code',
        is_external=0,
        is_cache=0,
        is_hidden=0,
        permission='',
        sort=100,
        status=1,
        create_user=admin_user_id,
    )
    
    # Create "Case 编辑器" menu
    caseeditor_menu = SysMenu.objects.create(
        title='Case 编辑器',
        parent_id=dev_menu.id,
        type=2,  # Menu
        path='/dev/caseeditor',
        name='DevCaseEditor',
        component='system/caseeditor/index',
        icon='icon-file-text',
        is_external=0,
        is_cache=1,
        is_hidden=0,
        permission='dev:caseeditor:view',
        sort=1,
        status=1,
        create_user=admin_user_id,
    )
    
    # Create button permissions
    permissions = [
        {
            'title': '保存文件',
            'permission': 'dev:caseeditor:save',
            'sort': 1,
        },
        {
            'title': '创建文件',
            'permission': 'dev:caseeditor:create',
            'sort': 2,
        },
        {
            'title': '删除文件',
            'permission': 'dev:caseeditor:delete',
            'sort': 3,
        },
        {
            'title': '重命名',
            'permission': 'dev:caseeditor:rename',
            'sort': 4,
        },
        {
            'title': '上传文件',
            'permission': 'dev:caseeditor:upload',
            'sort': 5,
        },
    ]
    
    for perm in permissions:
        SysMenu.objects.create(
            title=perm['title'],
            parent_id=caseeditor_menu.id,
            type=3,  # Button
            path='',
            name='',
            component='',
            icon='',
            is_external=0,
            is_cache=0,
            is_hidden=0,
            permission=perm['permission'],
            sort=perm['sort'],
            status=1,
            create_user=admin_user_id,
        )
    
    # Assign menu to admin role (role_id=1)
    try:
        admin_role = SysRole.objects.get(id=1)
        
        # Add directory menu
        SysRoleMenu.objects.create(
            role_id=admin_role.id,
            menu_id=dev_menu.id,
        )
        
        # Add Case Editor menu
        SysRoleMenu.objects.create(
            role_id=admin_role.id,
            menu_id=caseeditor_menu.id,
        )
        
        # Add all permission buttons
        button_menus = SysMenu.objects.filter(parent_id=caseeditor_menu.id, type=3)
        for button_menu in button_menus:
            SysRoleMenu.objects.create(
                role_id=admin_role.id,
                menu_id=button_menu.id,
            )
    except SysRole.DoesNotExist:
        print("Warning: Admin role not found, skipping role-menu assignment")


def remove_caseeditor_menu(apps, schema_editor):
    """Remove Case Editor menu and permissions"""
    SysMenu = apps.get_model('xauth', 'SysMenu')
    SysRoleMenu = apps.get_model('xauth', 'SysRoleMenu')
    
    # Find Case Editor menu
    try:
        caseeditor_menu = SysMenu.objects.get(path='/dev/caseeditor')
        
        # Delete role-menu associations for all related menus
        menu_ids = [caseeditor_menu.id]
        menu_ids.extend(SysMenu.objects.filter(parent_id=caseeditor_menu.id).values_list('id', flat=True))
        SysRoleMenu.objects.filter(menu_id__in=menu_ids).delete()
        
        # Delete permission buttons
        SysMenu.objects.filter(parent_id=caseeditor_menu.id).delete()
        
        # Delete menu itself
        caseeditor_menu.delete()
        
        # Find and delete "开发工具" directory if it has no other children
        dev_menu = SysMenu.objects.get(path='/dev')
        if not SysMenu.objects.filter(parent_id=dev_menu.id).exists():
            SysRoleMenu.objects.filter(menu_id=dev_menu.id).delete()
            dev_menu.delete()
    except SysMenu.DoesNotExist:
        print("Warning: Case Editor menu not found")


class Migration(migrations.Migration):

    dependencies = [
        ('xauth', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_caseeditor_menu, remove_caseeditor_menu),
    ]

