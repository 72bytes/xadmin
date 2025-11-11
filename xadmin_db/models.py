from typing import List
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.forms.models import model_to_dict
from xadmin_utils import utils


class ModelSaveMixin:
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

class SysDept(ModelSaveMixin, models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='ID')
    name = models.CharField(max_length=30, db_comment='名称')
    parent_id = models.BigIntegerField(db_index=True, db_comment='上级部门ID')
    ancestors = models.CharField(max_length=512, db_comment='祖级列表')
    description = models.CharField(max_length=200, blank=True, null=True, db_comment='描述')
    sort = models.IntegerField(db_comment='排序')
    status = models.PositiveIntegerField(db_comment='状态(1: 启用; 2: 禁用)')
    is_system = models.PositiveIntegerField(db_comment='是否为系统内置数据')  # This field type is a guess. Updated
    create_user = models.BigIntegerField(db_index=True, db_comment='创建人')
    create_time = models.DateTimeField(auto_now_add=True, db_comment='创建时间')
    update_user = models.BigIntegerField(db_index=True, blank=True, null=True, db_comment='修改人')
    update_time = models.DateTimeField(auto_now=True, blank=True, null=True, db_comment='修改时间')

    class Meta:
        db_table = 'sys_dept'
        unique_together = (('name', 'parent_id'),)
        db_table_comment = '部门表'

    def __str__(self):
        return f'<{self.id}, {self.name}>'

    @classmethod
    def build_dept_tree(cls, parent_id=0, choice=False, status=999):
        result = []
        filter = Q(parent_id=parent_id)
        dept_items = cls.objects.filter(filter)
        for item in dept_items:
            if (status != 999) and (status != item.status):
                continue
            if choice:
                dept = {
                    'key': item.id,
                    'parentId': item.parent_id,
                    'title': item.name,
                    'sort': item.sort,
                    'children': cls.build_dept_tree(parent_id=item.id, choice=choice, status=status)
                }
            else:
                dept = {
                    'id': item.id,
                    'parentId': item.parent_id,
                    'name': item.name or "",
                    'sort': item.sort,
                    'status': item.status,
                    'isSystem': bool(item.is_system),
                    'description': item.description,
                    'createUser': item.create_user,
                    'createUserString': 'fake',
                    'createTime': utils.dateformat(item.create_time),
                    'updateUser': item.update_user,
                    'updateUserString': 'fake',
                    'updateTime': item.update_time,
                    'children': cls.build_dept_tree(parent_id=item.id, choice=choice, status=status)
                }
            result.append(dept)
        return result

    @classmethod
    def delete_depts(cls, dept_id: int):
        dept_ids = cls.objects.filter(
            Q(id=dept_id) | Q(parent_id=dept_id)
        ).values_list('id', flat=True)
        if dept_ids:
            for did in list(dept_ids):
                cls.objects.filter(id=did).delete()
                SysRoleDept.objects.filter(dept_id=did).delete()
                cls.delete_depts(did)
                users = SysUser.objects.filter(dept_id=did)
                for user in users:
                    SysUserRole.objects.filter(user_id=user.id).delete()
                users.delete()


class SysDict(ModelSaveMixin, models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='ID')
    name = models.CharField(unique=True, max_length=30, db_comment='名称')
    code = models.CharField(unique=True, max_length=30, db_comment='编码')
    description = models.CharField(max_length=200, blank=True, null=True, db_comment='描述')
    is_system = models.PositiveIntegerField(db_comment='是否为系统内置数据')  # This field type is a guess. Updated
    create_user = models.BigIntegerField(db_comment='创建人')
    create_time = models.DateTimeField(auto_now_add=True, db_comment='创建时间')
    update_user = models.BigIntegerField(blank=True, null=True, db_comment='修改人')
    update_time = models.DateTimeField(auto_now=True, blank=True, null=True, db_comment='修改时间')

    class Meta:
        db_table = 'sys_dict'
        db_table_comment = '字典表'

    def __str__(self):
        return f'<{self.name}>'

class SysDictItem(ModelSaveMixin, models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='ID')
    label = models.CharField(max_length=30, db_comment='标签')
    value = models.CharField(max_length=30, db_comment='值')
    color = models.CharField(max_length=30, blank=True, null=True, db_comment='标签颜色')
    sort = models.IntegerField(db_comment='排序')
    description = models.CharField(max_length=200, blank=True, null=True, db_comment='描述')
    status = models.PositiveIntegerField(db_comment='状态(1: 启用; 2: 禁用)')
    dict_id = models.BigIntegerField(db_index=True, db_comment='字典ID')
    create_user = models.BigIntegerField(db_index=True, db_comment='创建人')
    create_time = models.DateTimeField(auto_now_add=True, db_comment='创建时间')
    update_user = models.BigIntegerField(db_index=True, blank=True, null=True, db_comment='修改人')
    update_time = models.DateTimeField(auto_now=True, blank=True, null=True, db_comment='修改时间')

    class Meta:
        db_table = 'sys_dict_item'
        unique_together = (('label', 'dict_id'),)
        db_table_comment = '字典项表'

    def __str__(self):
        return f'<{self.label}, {self.value}>'

class SysFile(ModelSaveMixin, models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='ID')
    name = models.CharField(max_length=255, db_comment='名称')
    size = models.BigIntegerField(db_comment='大小(字节)')
    url = models.CharField(max_length=512, db_index=True, db_comment='URL')
    extension = models.CharField(max_length=100, blank=True, null=True, db_comment='扩展名')
    thumbnail_size = models.BigIntegerField(blank=True, null=True, db_comment='缩略图大小(字节)')
    thumbnail_url = models.CharField(max_length=512, blank=True, null=True, db_comment='缩略图URL')
    type = models.PositiveIntegerField(db_index=True, db_comment='类型(1: 其他; 2: 图片; 3: 文档; 4: 视频; 5: 音频)')
    storage_id = models.BigIntegerField(db_comment='存储ID')
    create_user = models.BigIntegerField(db_index=True, db_comment='创建人')
    create_time = models.DateTimeField(auto_now_add=True, db_comment='创建时间')
    update_user = models.BigIntegerField(db_index=True, db_comment='修改人')
    update_time = models.DateTimeField(auto_now=True, db_comment='修改时间')

    class Meta:
        db_table = 'sys_file'
        db_table_comment = '文件表'

    def __str__(self):
        return f'<{self.name}>'

class SysLog(ModelSaveMixin, models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='ID')
    trace_id = models.CharField(max_length=255, blank=True, null=True, db_comment='链路ID')
    description = models.CharField(max_length=255, db_comment='日志描述')
    module = models.CharField(db_index=True, max_length=50, db_comment='所属模块')
    request_url = models.CharField(max_length=512, db_comment='请求URL')
    request_method = models.CharField(max_length=10, db_comment='请求方式')
    request_headers = models.TextField(blank=True, null=True, db_comment='请求头')
    request_body = models.TextField(blank=True, null=True, db_comment='请求体')
    status_code = models.IntegerField(db_comment='状态码')
    response_headers = models.TextField(blank=True, null=True, db_comment='响应头')
    response_body = models.TextField(blank=True, null=True, db_comment='响应体')
    time_taken = models.BigIntegerField(db_comment='耗时(ms)')
    ip = models.CharField(max_length=100, db_index=True, blank=True, null=True, db_comment='IP')
    address = models.CharField(max_length=255, blank=True, null=True, db_comment='IP归属地')
    browser = models.CharField(max_length=100, blank=True, null=True, db_comment='浏览器')
    os = models.CharField(max_length=100, blank=True, null=True, db_comment='操作系统')
    status = models.PositiveIntegerField(db_comment='状态(1: 成功; 2: 失败)')
    error_msg = models.TextField(blank=True, null=True, db_comment='错误信息')
    create_user = models.BigIntegerField(blank=True, null=True, db_comment='创建人')
    create_time = models.DateTimeField(auto_now_add=True, db_index=True, db_comment='创建时间')

    class Meta:
        db_table = 'sys_log'
        db_table_comment = '系统日志表'

    def __str__(self):
        return f'<{self.ip}>'

class SysMenu(ModelSaveMixin, models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='ID')
    title = models.CharField(max_length=30, db_comment='标题')
    parent_id = models.BigIntegerField(db_index=True, db_comment='上级菜单ID')
    type = models.PositiveIntegerField(db_comment='类型(1: 目录; 2: 菜单; 3: 按钮)')
    path = models.CharField(max_length=255, blank=True, null=True, db_comment='路由地址')
    name = models.CharField(max_length=50, blank=True, null=True, db_comment='组件名称')
    component = models.CharField(max_length=255, blank=True, null=True, db_comment='组件路径')
    redirect = models.CharField(max_length=255, blank=True, null=True, db_comment='重定向地址')
    icon = models.CharField(max_length=50, blank=True, null=True, db_comment='图标')
    is_external = models.PositiveIntegerField(blank=True, null=True, db_comment='是否外链')  # This field type is a guess. Updated
    is_cache = models.PositiveIntegerField(blank=True, null=True, db_comment='是否缓存')  # This field type is a guess. Updated
    is_hidden = models.PositiveIntegerField(blank=True, null=True, db_comment='是否隐藏')  # This field type is a guess. Updated
    permission = models.CharField(max_length=100, blank=True, null=True, db_comment='权限标识')
    sort = models.IntegerField(db_comment='排序')
    status = models.PositiveIntegerField(db_comment='状态(1: 启用; 2: 禁用)')
    create_user = models.BigIntegerField(db_index=True, db_comment='创建人')
    create_time = models.DateTimeField(auto_now_add=True, db_comment='创建时间')
    update_user = models.BigIntegerField(db_index=True, blank=True, null=True, db_comment='修改人')
    update_time = models.DateTimeField(auto_now=True, blank=True, null=True, db_comment='修改时间')

    class Meta:
        db_table = 'sys_menu'
        unique_together = (('title', 'parent_id'),)
        db_table_comment = '菜单表'
    
    @classmethod
    def build_menu_tree(cls, ids=None, parent_id=0, choice=False, all=False):
        menu_items = SysMenu.objects.filter(parent_id=parent_id)
        result = []
        for item in menu_items:
            if all:
                menu = {
                    'id': item.id,
                    'parentId': item.parent_id,
                    'title': item.title,
                    'type': item.type,
                    'path': item.path or "",
                    'name': item.name or "",
                    'component': item.component or "",
                    'redirect': item.redirect or "",
                    'icon': item.icon or "",
                    'isExternal': bool(item.is_external) if item.is_external else False,
                    'isCache': bool(item.is_cache) if item.is_cache else False,
                    'isHidden': bool(item.is_hidden) if item.is_hidden else False,
                    'permission': item.permission,
                    'sort': item.sort,
                    'status': item.status,
                    'createUser': item.create_user,
                    'createUserString': item.create_user,
                    'createTime': utils.dateformat(item.create_time),
                    'disabled': None,
                    'children': cls.build_menu_tree(ids=ids, parent_id=item.id, choice=choice, all=all)
                }
                result.append(menu)
            else:
                if (ids is None) or (item.id in ids):
                    if choice:
                        menu = {
                            'key': item.id,
                            'parentId': item.parent_id,
                            'title': item.title,
                            'sort': item.sort,
                            'children': cls.build_menu_tree(ids=ids, parent_id=item.id, choice=choice, all=all)
                        }
                        result.append(menu)
                    else:
                        if not item.type == 3:
                            menu = {
                                'id': item.id,
                                'parentId': item.parent_id,
                                'title': item.title,
                                'type': item.type,
                                'path': item.path or "",
                                'name': item.name or "",
                                'component': item.component or "",
                                'redirect': item.redirect or "",
                                'icon': item.icon or "",
                                'isExternal': bool(item.is_external) if item.is_external else False,
                                'isCache': bool(item.is_cache) if item.is_cache else False,
                                'isHidden': bool(item.is_hidden) if item.is_hidden else False,
                                'permission': item.permission,
                                'sort': item.sort,
                                'status': item.status,
                                'createUser': item.create_user,
                                'createUserString': item.create_user,
                                'createTime': utils.dateformat(item.create_time),
                                'disabled': None,
                                'children': cls.build_menu_tree(ids=ids, parent_id=item.id, choice=choice, all=all)
                            }
                            result.append(menu)
        return result

    @classmethod
    def delete_menus(cls, menu_id: int):
        menu_ids = cls.objects.filter(
            Q(id=menu_id) | Q(parent_id=menu_id)
        ).values_list('id', flat=True)
        if menu_ids:
            for mid in list(menu_ids):
                cls.objects.filter(id=mid).delete()
                cls.delete_menus(mid)


class SysMessage(ModelSaveMixin, models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='ID')
    title = models.CharField(max_length=50, db_comment='标题')
    content = models.CharField(max_length=255, blank=True, null=True, db_comment='内容')
    type = models.PositiveIntegerField(db_comment='类型(1: 系统消息)')
    create_user = models.BigIntegerField(blank=True, null=True, db_comment='创建人')
    create_time = models.DateTimeField(auto_now_add=True, db_comment='创建时间')

    class Meta:
        db_table = 'sys_message'
        db_table_comment = '消息表'
    
    def __str__(self):
        return f'<{self.title}>'

class SysMessageUser(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='ID')
    message_id = models.BigIntegerField(db_comment='消息ID')
    user_id = models.BigIntegerField(db_comment='用户ID')
    is_read = models.PositiveIntegerField(db_comment='是否已读')  # This field type is a guess. Updated
    read_time = models.DateTimeField(blank=True, null=True, db_comment='读取时间')

    class Meta:
        db_table = 'sys_message_user'
        unique_together = (('message_id', 'user_id'),)
        db_table_comment = '消息和用户关联表'
    
    def __str__(self):
        return f'<{self.user_id}, {self.message_id}>'

class SysNotice(ModelSaveMixin, models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='ID')
    title = models.CharField(max_length=150, db_comment='标题')
    content = models.TextField(db_comment='内容')
    type = models.CharField(max_length=30, db_comment='类型')
    effective_time = models.DateTimeField(blank=True, null=True, db_comment='生效时间')
    terminate_time = models.DateTimeField(blank=True, null=True, db_comment='终止时间')
    sort = models.IntegerField(db_comment='排序')
    create_user = models.BigIntegerField(db_index=True, db_comment='创建人')
    create_time = models.DateTimeField(auto_now_add=True, db_comment='创建时间')
    update_user = models.BigIntegerField(db_index=True, blank=True, null=True, db_comment='修改人')
    update_time = models.DateTimeField(auto_now=True, blank=True, null=True, db_comment='修改时间')

    class Meta:
        db_table = 'sys_notice'
        db_table_comment = '公告表'
    
    def __str__(self):
        return f'<{self.title}>'

class SysOption(ModelSaveMixin, models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='ID')
    category = models.CharField(max_length=50, db_comment='类别')
    name = models.CharField(max_length=50, db_comment='名称')
    code = models.CharField(max_length=100, db_comment='键')
    value = models.TextField(blank=True, null=True, db_comment='值')
    default_value = models.TextField(blank=True, null=True, db_comment='默认值')
    description = models.CharField(max_length=200, blank=True, null=True, db_comment='描述')
    update_user = models.BigIntegerField(blank=True, null=True, db_comment='修改人')
    update_time = models.DateTimeField(auto_now=True, blank=True, null=True, db_comment='修改时间')

    class Meta:
        db_table = 'sys_option'
        db_table_comment = '参数表'
        unique_together = (('category', 'code'),)
    
    def __str__(self):
        return f'<{self.name}, {self.code}>'

    @classmethod
    def get_options(cls, **kwargs):
        include = kwargs.get('include', ())
        exclude = kwargs.get('exclude', ())
        category = kwargs.get('category')
        codes = kwargs.get('codes', False)
        options = []
        if codes:
            _options = cls.objects.filter(code__in=codes, category=category)
        else:
            _options = cls.objects.filter(category=category)
        for opt in _options:
            options.append(model_to_dict(opt, fields=include, exclude=exclude))
        
        return options
        


class SysStorage(ModelSaveMixin, models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='ID')
    name = models.CharField(max_length=100, db_comment='名称')
    code = models.CharField(unique=True, max_length=30, db_comment='编码')
    type = models.PositiveIntegerField(db_comment='类型(1: 兼容S3协议存储; 2: 本地存储)')
    access_key = models.CharField(max_length=255, blank=True, null=True, db_comment='Access Key(访问密钥)')
    secret_key = models.CharField(max_length=255, blank=True, null=True, db_comment='Secret Key(私有密钥)')
    endpoint = models.CharField(max_length=255, blank=True, null=True, db_comment='Endpoint(终端节点)')
    bucket_name = models.CharField(max_length=255, blank=True, null=True, db_comment='桶名称')
    domain = models.CharField(max_length=255, db_comment='域名')
    description = models.CharField(max_length=200, blank=True, null=True, db_comment='描述')
    is_default = models.PositiveIntegerField(db_comment='是否为默认存储')  # This field type is a guess. Updated
    sort = models.IntegerField(db_comment='排序')
    status = models.PositiveIntegerField(db_comment='状态(1: 启用; 2: 禁用)')
    create_user = models.BigIntegerField(db_index=True, db_comment='创建人')
    create_time = models.DateTimeField(auto_now_add=True, db_comment='创建时间')
    update_user = models.BigIntegerField(blank=True, null=True, db_comment='修改人')
    update_time = models.DateTimeField(auto_now=True, blank=True, null=True, db_comment='修改时间')

    class Meta:
        db_table = 'sys_storage'
        db_table_comment = '存储表'

    def __str__(self):
        return f'<{self.name}>'

class SysRole(ModelSaveMixin, models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='ID')
    name = models.CharField(unique=True, max_length=30, db_comment='名称')
    code = models.CharField(unique=True, max_length=30, db_comment='编码')
    data_scope = models.IntegerField(db_comment='数据权限(1: 全部数据权限; 2: 本部门及以下数据权限; 3: 本部门数据权限; 4: 仅本人数据权限; 5: 自定义数据权限)')
    description = models.CharField(max_length=200, blank=True, null=True, db_comment='描述')
    sort = models.IntegerField(db_comment='排序')
    is_system = models.PositiveIntegerField(db_comment='是否为系统内置数据')  # This field type is a guess. Updated
    create_user = models.BigIntegerField(db_comment='创建人')
    create_time = models.DateTimeField(auto_now_add=True, db_comment='创建时间')
    update_user = models.BigIntegerField(blank=True, null=True, db_comment='修改人')
    update_time = models.DateTimeField(auto_now=True, blank=True, null=True, db_comment='修改时间')

    class Meta:
        db_table = 'sys_role'
        db_table_comment = '角色表'
    
    def __str__(self):
        return f'<f{self.name}, {self.code}>'

    @classmethod
    def get_role_info(cls, id: int):
        role = cls.objects.get(id=id)
        role_menus = SysRoleMenu.objects.filter(
            role_id=id
        ).values('menu_id')
        role_depts = SysRoleDept.objects.filter(
            role_id=id
        ).values('dept_id')
        data = dict(
            id = role.id,
            name = role.name,
            code = role.code,
            dataScope = role.data_scope,
            description = role.description,
            sort = 1,
            isSystem = bool(role.is_system),
            createUserString = role.create_user,
            createTime = role.create_time,
            updateUserString = role.update_user,
            updateTime = role.update_time,
        )
        data['menuIds'] = list(role_menus.values_list('menu_id', flat=True))
        data['deptIds'] = list(role_depts.values_list('dept_id', flat=True))

        return data


class SysRoleDept(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='ID')
    role_id = models.BigIntegerField(db_comment='角色ID')
    dept_id = models.BigIntegerField(db_comment='部门ID')

    class Meta:
        db_table = 'sys_role_dept'
        unique_together = (('role_id', 'dept_id'),)
        db_table_comment = '角色和部门关联表'
    
    def __str__(self):
        return f'<{self.role_id}, {self.dept_id}>'

    @classmethod
    def set_role_depts(cls, role_id: int, dept_ids: List[int]):
        cls.objects.filter(role_id=role_id).delete()
        for dept_id in dept_ids:
            cls.objects.create(role_id=role_id, dept_id=dept_id)


class SysRoleMenu(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='ID')
    role_id = models.BigIntegerField(db_comment='角色ID')
    menu_id = models.BigIntegerField(db_comment='菜单ID')

    class Meta:
        db_table = 'sys_role_menu'
        unique_together = (('role_id', 'menu_id'),)
        db_table_comment = '角色和菜单关联表'
    
    def __str__(self):
        return f'<{self.role_id}, {self.menu_id}>'
    
    @classmethod
    def set_role_menus(cls, role_id: int, menu_ids: List[int]):
        cls.objects.filter(role_id=role_id).delete()
        for menu_id in menu_ids:
            cls.objects.create(role_id=role_id, menu_id=menu_id)

# User Manager
class SysUserManager(BaseUserManager):
    def create_user(self, username, password, **extra_fields):
        user_id = extra_fields.get('id', None)
        if not username:
            raise ValueError('The UserName field must be set')
        if user_id is None:
            raise ValueError('The UserId field must be set')

        user = self.model(
            username=username,
            **extra_fields
        )
        user.set_password(password)
        user.save()
        return user
        
class SysUser(ModelSaveMixin, AbstractBaseUser):
    id = models.BigAutoField(primary_key=True, db_comment='ID')
    username = models.CharField(unique=True, max_length=64, db_comment='用户名')
    password = models.CharField(max_length=255, db_comment='密码')
    gender = models.PositiveIntegerField(db_comment='性别(0: 未知; 1: 男; 2: 女)')
    dept_id = models.BigIntegerField(db_comment='部门ID')
    status = models.PositiveIntegerField(db_comment='状态(1: 启用; 2: 禁用)')
    is_system = models.PositiveIntegerField(db_comment='是否为系统内置数据')  # This field type is a guess. Updated
    nickname = models.CharField(max_length=30, blank=True, null=True, db_comment='昵称')
    email = models.CharField(unique=True, max_length=255, blank=True, null=True, db_comment='邮箱')
    phone = models.CharField(unique=True, max_length=255, blank=True, null=True, db_comment='手机号码')
    avatar = models.TextField(blank=True, null=True, db_comment='头像地址')
    description = models.CharField(max_length=200, blank=True, null=True, db_comment='描述')
    pwd_reset_time = models.DateTimeField(blank=True, null=True, db_comment='最后一次修改密码时间')
    create_user = models.BigIntegerField(blank=True, null=True, db_comment='创建人')
    create_time = models.DateTimeField(auto_now_add=True, db_comment='创建时间')
    update_user = models.BigIntegerField(blank=True, null=True, db_comment='修改人')
    update_time = models.DateTimeField(auto_now=True, blank=True, null=True, db_comment='修改时间')

    objects = SysUserManager()
    USERNAME_FIELD = "id"
    REQUIRED_FIELDS = [id, username, password, gender, dept_id, status, is_system]
    class Meta:
        db_table = 'sys_user'
        db_table_comment = '用户表'
    
    def __str__(self):
        return self.username

    @classmethod
    def get_user_and_roles_by_id(cls, id: int):
        user = cls.objects.get(id=id)
        create_user = cls.objects.get(id=user.create_user)
        dept = SysDept.objects.get(id=user.dept_id)
        role_ids = SysUserRole.objects.filter(
            user_id = user.id
        ).values('role_id')
        role_names = SysRole.objects.filter(
            id__in=models.Subquery(role_ids)
        )
        _user = model_to_dict(user)
        _user['deptId'] = user.dept_id
        _user['createUser'] = create_user.username
        _user['isSystem'] = bool(user.is_system)
        _user['deptName'] = dept.name
        _user['roleIds'] = list(role_ids.values_list('role_id', flat=True))
        _user['roleNames'] = list(role_names.values_list('name', flat=True))
        for k in ('password', 'last_login', 'create_user', 'dept_id'):
            _user.pop(k)

        return _user

class SysUserPasswordHistory(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='ID')
    user_id = models.BigIntegerField(db_index=True, db_comment='用户ID')
    password = models.CharField(max_length=255, db_comment='密码')
    create_time = models.DateTimeField(db_comment='创建时间', auto_now_add=True)

    class Meta:
        db_table = 'sys_user_password_history'
        db_table_comment = '用户历史密码表'
    
    def __str__(self):
        return f"<{self.user_id}, {self.create_time}>"

class SysUserRole(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='ID')
    user_id = models.BigIntegerField(db_comment='用户ID')
    role_id = models.BigIntegerField(db_comment='角色ID')

    class Meta:
        db_table = 'sys_user_role'
        unique_together = (('user_id', 'role_id'),)
        db_table_comment = '用户和角色关联表'
    
    def __str__(self):
        return f"<{self.user_id}, {self.role_id}>"

    @classmethod
    def set_user_role(cls, user_id: int, role_id: int):
        cls.objects.create(user_id=user_id, role_id=role_id)

    @classmethod
    def set_user_roles(cls, user_id: int, role_ids: List[int]):
        cls.objects.filter(
            user_id=user_id
        ).delete()
        for role_id in role_ids:
            cls.set_user_role(user_id, role_id)


class SysUserSocial(models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='ID')
    source = models.CharField(max_length=255, db_comment='来源')
    open_id = models.CharField(max_length=255, db_comment='开放ID')
    user_id = models.BigIntegerField(db_comment='用户ID')
    meta_json = models.TextField(blank=True, null=True, db_comment='附加信息')
    last_login_time = models.DateTimeField(blank=True, null=True, db_comment='最后登录时间')
    create_time = models.DateTimeField(db_comment='创建时间', auto_now_add=True)

    class Meta:
        db_table = 'sys_user_social'
        unique_together = (('source', 'open_id'),)
        db_table_comment = '用户社会化关联表'
    
    def __str__(self):
        return f"<{self.user_id}, {self.open_id}>"
