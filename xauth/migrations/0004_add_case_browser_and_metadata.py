# Generated manually for Case Browser feature

from django.db import migrations, models
import django.db.models.deletion


def add_casebrowser_menu(apps, schema_editor):
    """Add Case Browser menu and permissions"""
    SysMenu = apps.get_model('xauth', 'SysMenu')
    SysRole = apps.get_model('xauth', 'SysRole')
    SysRoleMenu = apps.get_model('xauth', 'SysRoleMenu')
    
    # Get admin user ID (assuming ID 1)
    admin_user_id = 1
    
    # Find "用例管理" (Dev) directory menu
    try:
        dev_menu = SysMenu.objects.get(path='/dev')
    except SysMenu.DoesNotExist:
        print("Warning: Dev menu not found, creating it")
        dev_menu = SysMenu.objects.create(
            title='用例管理',
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
    
    # Create "用例浏览" menu
    casebrowser_menu = SysMenu.objects.create(
        title='用例浏览',
        parent_id=dev_menu.id,
        type=2,  # Menu
        path='/dev/casebrowser',
        name='DevCaseBrowser',
        component='system/casebrowser/index',
        icon='icon-apps',
        is_external=0,
        is_cache=1,
        is_hidden=0,
        permission='dev:casebrowser:view',
        sort=2,
        status=1,
        create_user=admin_user_id,
    )
    
    # Create button permissions
    permissions = [
        {
            'title': '查看用例',
            'permission': 'dev:casebrowser:view',
            'sort': 1,
        },
        {
            'title': '添加标签',
            'permission': 'dev:casebrowser:addtag',
            'sort': 2,
        },
        {
            'title': '删除标签',
            'permission': 'dev:casebrowser:deletetag',
            'sort': 3,
        },
        {
            'title': '添加选项',
            'permission': 'dev:casebrowser:addoption',
            'sort': 4,
        },
        {
            'title': '更新选项',
            'permission': 'dev:casebrowser:updateoption',
            'sort': 5,
        },
        {
            'title': '删除选项',
            'permission': 'dev:casebrowser:deleteoption',
            'sort': 6,
        },
    ]
    
    for perm in permissions:
        SysMenu.objects.create(
            title=perm['title'],
            parent_id=casebrowser_menu.id,
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
    
    # Assign menu to admin role
    try:
        admin_role = SysRole.objects.get(name='超级管理员')
        
        # Get all menu IDs (casebrowser + buttons)
        menu_ids = [casebrowser_menu.id]
        menu_ids.extend(SysMenu.objects.filter(parent_id=casebrowser_menu.id).values_list('id', flat=True))
        
        # Create role-menu associations
        for menu_id in menu_ids:
            SysRoleMenu.objects.get_or_create(
                role_id=admin_role.id,
                menu_id=menu_id
            )
    except SysRole.DoesNotExist:
        print("Warning: Admin role not found, skipping role-menu assignment")


def remove_casebrowser_menu(apps, schema_editor):
    """Remove Case Browser menu and permissions"""
    SysMenu = apps.get_model('xauth', 'SysMenu')
    SysRoleMenu = apps.get_model('xauth', 'SysRoleMenu')
    
    # Find Case Browser menu
    try:
        casebrowser_menu = SysMenu.objects.get(path='/dev/casebrowser')
        
        # Delete role-menu associations for all related menus
        menu_ids = [casebrowser_menu.id]
        menu_ids.extend(SysMenu.objects.filter(parent_id=casebrowser_menu.id).values_list('id', flat=True))
        SysRoleMenu.objects.filter(menu_id__in=menu_ids).delete()
        
        # Delete permission buttons
        SysMenu.objects.filter(parent_id=casebrowser_menu.id).delete()
        
        # Delete menu itself
        casebrowser_menu.delete()
    except SysMenu.DoesNotExist:
        print("Warning: Case Browser menu not found")


class Migration(migrations.Migration):

    dependencies = [
        ('xauth', '0003_add_caseeditor_menu'),
    ]

    operations = [
        # Create CaseMetadata table
        migrations.CreateModel(
            name='CaseMetadata',
            fields=[
                ('id', models.BigAutoField(db_comment='ID', primary_key=True, serialize=False)),
                ('casespace', models.CharField(db_comment='Casespace名称', max_length=255)),
                ('case_name', models.CharField(db_comment='Case名称', max_length=255)),
                ('create_time', models.DateTimeField(auto_now_add=True, db_comment='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, db_comment='更新时间')),
            ],
            options={
                'db_table': 'case_metadata',
                'db_table_comment': 'Case元数据表',
                'unique_together': {('casespace', 'case_name')},
            },
        ),
        # Create CaseTag table
        migrations.CreateModel(
            name='CaseTag',
            fields=[
                ('id', models.BigAutoField(db_comment='ID', primary_key=True, serialize=False)),
                ('tag', models.CharField(db_comment='标签名称', max_length=100)),
                ('create_time', models.DateTimeField(auto_now_add=True, db_comment='创建时间')),
                ('metadata', models.ForeignKey(
                    db_comment='关联的case元数据',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='tags',
                    to='xdb.casemetadata'
                )),
            ],
            options={
                'db_table': 'case_tag',
                'db_table_comment': 'Case标签表',
                'unique_together': {('metadata', 'tag')},
            },
        ),
        # Create CaseOption table
        migrations.CreateModel(
            name='CaseOption',
            fields=[
                ('id', models.BigAutoField(db_comment='ID', primary_key=True, serialize=False)),
                ('key', models.CharField(db_comment='选项键', max_length=100)),
                ('value', models.CharField(db_comment='选项值', max_length=500)),
                ('create_time', models.DateTimeField(auto_now_add=True, db_comment='创建时间')),
                ('update_time', models.DateTimeField(auto_now=True, db_comment='更新时间')),
                ('metadata', models.ForeignKey(
                    db_comment='关联的case元数据',
                    on_delete=django.db.models.deletion.CASCADE,
                    related_name='options',
                    to='xdb.casemetadata'
                )),
            ],
            options={
                'db_table': 'case_option',
                'db_table_comment': 'Case选项表',
                'unique_together': {('metadata', 'key')},
            },
        ),
        # Add Case Browser menu
        migrations.RunPython(add_casebrowser_menu, remove_casebrowser_menu),
    ]

