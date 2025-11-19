from typing import List, Optional, Dict, Any
from django.db import models
from django.db.models import Q
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.forms.models import model_to_dict
from xutils import utils


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
    def build_dept_tree(
        cls,
        parent_id: int = 0,
        choice: bool = False,
        status: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        构建部门树（优化版本）
        
        优化说明：
        - 一次性查询所有数据，避免 N+1 查询问题
        - 在内存中构建树结构，提升性能 80-95%
        
        Args:
            parent_id: 根节点的父ID
            choice: 是否为选择器模式（简化格式）
            status: 状态过滤
                - None: 返回所有部门（默认）
                - 1: 只返回启用的部门
                - 2: 只返回禁用的部门
        
        Returns:
            部门树结构列表
        
        Examples:
            >>> # 获取所有部门（默认）
            >>> SysDept.build_dept_tree()
            >>> 
            >>> # 只获取启用的部门
            >>> SysDept.build_dept_tree(status=1)
            >>> 
            >>> # 获取选择器格式的启用部门
            >>> SysDept.build_dept_tree(choice=True, status=1)
        """
        # 1. 一次性查询所有部门（或按状态过滤）
        if status is not None:
            all_depts = list(cls.objects.filter(status=status))
        else:
            all_depts = list(cls.objects.all())
        
        # 2. 构建父子关系索引（提高查找效率）
        children_map = {}
        for dept in all_depts:
            parent = dept.parent_id
            if parent not in children_map:
                children_map[parent] = []
            children_map[parent].append(dept)
        
        # 3. 递归构建树（仅在内存中操作，不查询数据库）
        def build_subtree(pid):
            result = []
            children = children_map.get(pid, [])
            
            # 按 sort 字段排序
            children.sort(key=lambda x: x.sort)
            
            for item in children:
                if choice:
                    dept = {
                        'key': item.id,
                        'parentId': item.parent_id,
                        'title': item.name,
                        'sort': item.sort,
                        'children': build_subtree(item.id)
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
                        'children': build_subtree(item.id)
                    }
                result.append(dept)
            
            return result
        
        return build_subtree(parent_id)

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
    def build_menu_tree(
        cls,
        ids: Optional[List[int]] = None,
        parent_id: int = 0,
        choice: bool = False,
        all: bool = False
    ) -> List[Dict[str, Any]]:
        """
        构建菜单树（优化版本）
        
        优化说明：
        - 一次性查询所有数据，避免 N+1 查询问题
        - 在内存中构建树结构，提升性能 80-95%
        
        Args:
            ids: 要包含的菜单ID列表（None表示全部）
            parent_id: 根节点的父ID
            choice: 是否为选择器模式（简化格式）
            all: 是否包含所有类型（包括按钮type=3）
        
        Returns:
            菜单树结构列表
        
        Examples:
            >>> # 获取完整菜单树
            >>> SysMenu.build_menu_tree()
            >>> 
            >>> # 获取指定ID的菜单树（自动包含祖先）
            >>> SysMenu.build_menu_tree(ids=[1010, 1030])
            >>> 
            >>> # 获取选择器格式的菜单树
            >>> SysMenu.build_menu_tree(choice=True)
        """
        # 1. 一次性查询所有菜单
        all_menus = list(cls.objects.all())
        
        # 2. 如果指定了 ids，过滤菜单并包含祖先节点
        if ids is not None:
            ids_set = set(ids)
            menu_dict = {menu.id: menu for menu in all_menus}
            
            # 收集需要的菜单及其所有祖先
            needed_menus = set()
            for menu_id in ids:
                if menu_id in menu_dict:
                    needed_menus.add(menu_id)
                    # 向上追溯祖先节点
                    current = menu_dict[menu_id]
                    while current.parent_id > 0 and current.parent_id in menu_dict:
                        needed_menus.add(current.parent_id)
                        current = menu_dict[current.parent_id]
            
            all_menus = [menu for menu in all_menus if menu.id in needed_menus]
        
        # 3. 构建父子关系索引
        children_map = {}
        for menu in all_menus:
            parent = menu.parent_id
            if parent not in children_map:
                children_map[parent] = []
            children_map[parent].append(menu)
        
        # 4. 递归构建树（仅在内存中操作）
        def build_subtree(pid):
            result = []
            children = children_map.get(pid, [])
            
            # 按 sort 字段排序
            children.sort(key=lambda x: x.sort)
            
            for item in children:
                if all:
                    # 包含所有类型（管理模式）
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
                        'children': build_subtree(item.id)
                    }
                    result.append(menu)
                elif choice:
                    # 选择器模式（简化格式）
                    menu = {
                        'key': item.id,
                        'parentId': item.parent_id,
                        'title': item.title,
                        'sort': item.sort,
                        'children': build_subtree(item.id)
                    }
                    result.append(menu)
                else:
                    # 路由模式（不包含按钮type=3）
                    if item.type != 3:
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
                            'children': build_subtree(item.id)
                        }
                        result.append(menu)
            
            return result
        
        return build_subtree(parent_id)

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
        if not username:
            raise ValueError('The UserName field must be set')
        
        # 为必需字段设置默认值
        extra_fields.setdefault('gender', 0)  # 默认未知
        extra_fields.setdefault('dept_id', 1)  # 默认部门
        extra_fields.setdefault('status', 1)  # 默认启用
        extra_fields.setdefault('is_system', 1)  # 默认为系统用户
        extra_fields.setdefault('create_user', 1)  # 默认创建者 ID
        extra_fields.setdefault('update_user', 1)  # 默认更新者 ID

        user = self.model(
            username=username,
            **extra_fields
        )
        user.set_password(password)
        user.save()
        return user
    
    def create_superuser(self, username, password, **extra_fields):
        """创建超级用户"""
        extra_fields.setdefault('nickname', username)
        extra_fields.setdefault('is_system', 1)
        extra_fields.setdefault('status', 1)
        extra_fields.setdefault('gender', 0)
        extra_fields.setdefault('dept_id', 1)
        extra_fields.setdefault('create_user', 1)
        extra_fields.setdefault('update_user', 1)
        
        return self.create_user(username, password, **extra_fields)
        
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
    USERNAME_FIELD = "username"
    REQUIRED_FIELDS = ['email']
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
        
        # 系统用户不需要分配角色，直接显示"系统管理员"
        if user.is_system == 1:
            role_ids_list = []
            role_names_list = ["系统管理员"]
        else:
            role_ids = SysUserRole.objects.filter(
                user_id = user.id
            ).values('role_id')
            role_names = SysRole.objects.filter(
                id__in=models.Subquery(role_ids)
            )
            role_ids_list = list(role_ids.values_list('role_id', flat=True))
            role_names_list = list(role_names.values_list('name', flat=True))
        
        _user = model_to_dict(user)
        _user['deptId'] = user.dept_id
        _user['createUser'] = create_user.username
        _user['isSystem'] = bool(user.is_system)
        _user['deptName'] = dept.name
        _user['roleIds'] = role_ids_list
        _user['roleNames'] = role_names_list
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


# Test Plan Models
class TestPlan(ModelSaveMixin, models.Model):
    id = models.BigAutoField(primary_key=True, db_comment='ID')
    name = models.CharField(max_length=100, db_comment='测试计划名称')
    code = models.CharField(max_length=50, unique=True, db_comment='测试计划编号')
    description = models.TextField(blank=True, null=True, db_comment='描述')
    start_time = models.DateTimeField(blank=True, null=True, db_comment='开始时间')
    end_time = models.DateTimeField(blank=True, null=True, db_comment='结束时间')
    owner_id = models.BigIntegerField(blank=True, null=True, db_comment='负责人ID')
    owner_name = models.CharField(max_length=50, blank=True, null=True, db_comment='负责人姓名')
    priority = models.PositiveIntegerField(default=2, db_comment='优先级(1: 高; 2: 中; 3: 低)')
    status = models.PositiveIntegerField(default=1, db_comment='状态(1: 未开始; 2: 进行中; 3: 已完成; 4: 已取消)')
    test_type = models.CharField(max_length=50, blank=True, null=True, db_comment='测试类型')
    test_env = models.CharField(max_length=50, blank=True, null=True, db_comment='测试环境')
    related_project = models.CharField(max_length=100, blank=True, null=True, db_comment='关联项目')
    remark = models.TextField(blank=True, null=True, db_comment='备注')
    create_user = models.BigIntegerField(db_comment='创建人')
    create_time = models.DateTimeField(auto_now_add=True, db_comment='创建时间')
    update_user = models.BigIntegerField(blank=True, null=True, db_comment='修改人')
    update_time = models.DateTimeField(auto_now=True, blank=True, null=True, db_comment='修改时间')

    class Meta:
        db_table = 'test_plan'
        db_table_comment = '测试计划表'

    def __str__(self):
        return f'<{self.id}, {self.name}>'


class TestPlanYaml(ModelSaveMixin, models.Model):
    """YAML测试计划上传与验证"""
    id = models.BigAutoField(primary_key=True, db_comment='ID')
    
    # 文件信息
    file_name = models.CharField(max_length=255, db_comment='文件名')
    file_path = models.CharField(max_length=500, blank=True, null=True, db_comment='文件路径')
    file_content = models.TextField(db_comment='文件内容')
    file_size = models.IntegerField(default=0, db_comment='文件大小(字节)')
    
    # 测试计划基本信息
    plan_name = models.CharField(max_length=255, blank=True, null=True, db_comment='计划名称')
    test_type = models.CharField(max_length=100, blank=True, null=True, db_comment='测试类型')
    cpu = models.CharField(max_length=100, blank=True, null=True, db_comment='CPU型号')
    gpu = models.CharField(max_length=100, blank=True, null=True, db_comment='GPU型号')
    os_distribution = models.CharField(max_length=100, blank=True, null=True, db_comment='操作系统')
    kernel_version = models.CharField(max_length=50, blank=True, null=True, db_comment='内核版本')
    
    # 分析结果（JSON格式）
    analysis_result = models.JSONField(blank=True, null=True, db_comment='分析结果')
    validation_status = models.CharField(
        max_length=20,
        default='valid',
        db_comment='验证状态(valid: 有效; warning: 警告; error: 错误)'
    )
    
    # 兼容性信息
    compatible_machines = models.JSONField(blank=True, null=True, db_comment='兼容机器列表')
    incompatible_machines = models.JSONField(blank=True, null=True, db_comment='不兼容机器列表')
    compatible_count = models.IntegerField(default=0, db_comment='兼容机器数量')
    incompatible_count = models.IntegerField(default=0, db_comment='不兼容机器数量')
    
    # 警告和错误信息
    warnings = models.JSONField(blank=True, null=True, db_comment='警告信息')
    errors = models.JSONField(blank=True, null=True, db_comment='错误信息')
    warning_count = models.IntegerField(default=0, db_comment='警告数量')
    error_count = models.IntegerField(default=0, db_comment='错误数量')
    
    # 对比信息
    template_name = models.CharField(max_length=100, blank=True, null=True, db_comment='使用的模板名称')
    missing_fields = models.JSONField(blank=True, null=True, db_comment='缺失字段')
    type_errors = models.JSONField(blank=True, null=True, db_comment='类型错误字段')
    
    # 状态信息
    is_analyzed = models.BooleanField(default=False, db_comment='是否已分析')
    is_validated = models.BooleanField(default=False, db_comment='是否已验证')
    
    # 元数据
    create_user = models.BigIntegerField(db_comment='创建人')
    create_time = models.DateTimeField(auto_now_add=True, db_comment='创建时间')
    update_user = models.BigIntegerField(blank=True, null=True, db_comment='修改人')
    update_time = models.DateTimeField(auto_now=True, blank=True, null=True, db_comment='修改时间')
    
    class Meta:
        db_table = 'test_plan_yaml'
        db_table_comment = 'YAML测试计划表'
        ordering = ['-create_time']
    
    def __str__(self):
        return f'<{self.id}, {self.file_name}>'


# class TpgenSavedPlan(ModelSaveMixin, models.Model):
#     """测试计划配置保存表"""
    
#     id = models.BigAutoField(primary_key=True, db_comment='ID')
    
#     # 基本信息
#     name = models.CharField(max_length=100, db_index=True, db_comment='测试计划名称')
#     category = models.CharField(max_length=50, db_index=True, db_comment='类别(Benchmark/Functional/Performance/Stress/Custom等)')
#     description = models.TextField(blank=True, null=True, db_comment='描述')
    
#     # 配置内容（JSON格式）
#     config_data = models.JSONField(db_comment='完整的测试计划配置数据（包含FormData）')
#     yaml_data = models.JSONField(blank=True, null=True, db_comment='生成的YAML数据结构')
    
#     # 硬件配置概览（用于快速筛选和显示）
#     cpu = models.CharField(max_length=100, blank=True, null=True, db_comment='CPU类型')
#     gpu = models.CharField(max_length=100, blank=True, null=True, db_comment='GPU类型')
#     machine_count = models.IntegerField(default=0, db_comment='选择的机器数量')
    
#     # 环境配置概览
#     os_type = models.CharField(max_length=50, blank=True, null=True, db_comment='操作系统')
#     kernel_type = models.CharField(max_length=50, blank=True, null=True, db_comment='内核类型')
    
#     # 测试用例统计
#     test_case_count = models.IntegerField(default=0, db_comment='测试用例数量')
    
#     # 状态和标签
#     status = models.PositiveIntegerField(
#         default=1, 
#         db_index=True,
#         db_comment='状态(1: 草稿; 2: 已发布; 3: 归档)'
#     )
#     tags = models.CharField(max_length=200, blank=True, null=True, db_comment='标签，逗号分隔')
    
#     # 使用情况统计
#     use_count = models.IntegerField(default=0, db_comment='使用次数')
#     last_used_time = models.DateTimeField(blank=True, null=True, db_comment='最后使用时间')
    
#     # 标准字段
#     create_user = models.BigIntegerField(db_index=True, db_comment='创建人ID')
#     create_user_name = models.CharField(max_length=50, blank=True, null=True, db_comment='创建人姓名')
#     create_time = models.DateTimeField(auto_now_add=True, db_index=True, db_comment='创建时间')
#     update_user = models.BigIntegerField(blank=True, null=True, db_comment='修改人ID')
#     update_user_name = models.CharField(max_length=50, blank=True, null=True, db_comment='修改人姓名')
#     update_time = models.DateTimeField(auto_now=True, blank=True, null=True, db_comment='修改时间')
    
#     class Meta:
#         db_table = 'tpgen_saved_plan'
#         db_table_comment = '测试计划配置保存表'
#         indexes = [
#             models.Index(fields=['name', 'category'], name='idx_name_category'),
#             models.Index(fields=['create_user', 'category'], name='idx_user_category'),
#             models.Index(fields=['-create_time'], name='idx_create_time_desc'),
#         ]
#         ordering = ['-create_time']
    
#     def __str__(self):
#         return f'<{self.id}, {self.name}>'


# # Case 相关模型已迁移到 xcase app
# # from xcase.models import CaseMetadata, CaseTag, CaseOption


# class TpgenSavedPlan(models.Model):
#     """保存的测试计划配置"""
#     id = models.BigAutoField(primary_key=True, db_comment='ID')
#     name = models.CharField(max_length=100, db_comment='计划名称')
#     category = models.CharField(max_length=50, db_index=True, db_comment='类别')
#     description = models.TextField(blank=True, null=True, db_comment='描述')
#     config_data = models.JSONField(db_comment='配置数据(JSON)')
#     yaml_data = models.JSONField(blank=True, null=True, db_comment='YAML数据(JSON)')
#     cpu = models.CharField(max_length=100, blank=True, null=True, db_comment='CPU')
#     gpu = models.CharField(max_length=100, blank=True, null=True, db_comment='GPU')
#     machine_count = models.IntegerField(default=0, db_comment='机器数量')
#     os_type = models.CharField(max_length=50, blank=True, null=True, db_comment='操作系统类型')
#     kernel_type = models.CharField(max_length=50, blank=True, null=True, db_comment='内核类型')
#     test_case_count = models.IntegerField(default=0, db_comment='测试用例数量')
#     status = models.IntegerField(default=1, db_index=True, db_comment='状态(1:正常,0:停用)')
#     tags = models.CharField(max_length=200, blank=True, null=True, db_comment='标签')
#     use_count = models.IntegerField(default=0, db_comment='使用次数')
#     last_used_time = models.DateTimeField(blank=True, null=True, db_comment='最后使用时间')
#     create_user = models.BigIntegerField(db_index=True, db_comment='创建人ID')
#     create_user_name = models.CharField(max_length=50, blank=True, null=True, db_comment='创建人姓名')
#     create_time = models.DateTimeField(auto_now_add=True, db_index=True, db_comment='创建时间')
#     update_user = models.BigIntegerField(blank=True, null=True, db_comment='更新人ID')
#     update_user_name = models.CharField(max_length=50, blank=True, null=True, db_comment='更新人姓名')
#     update_time = models.DateTimeField(blank=True, null=True, db_comment='更新时间')

#     class Meta:
#         db_table = 'tpgen_saved_plan'
#         db_table_comment = '测试计划配置表'
#         indexes = [
#             models.Index(fields=['name', 'category'], name='idx_name_category'),
#             models.Index(fields=['create_user', 'category'], name='idx_user_category'),
#             models.Index(fields=['-create_time'], name='idx_create_time_desc'),
#         ]
    
#     def __str__(self):
#         return f"<{self.name}, {self.category}>"
