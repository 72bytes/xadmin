from django.db import models
from xauth.models import SysUser


class TpgenSavedPlan(models.Model):
    """保存的测试计划配置表"""
    
    name = models.CharField(max_length=255, verbose_name='测试计划名称')
    category = models.CharField(max_length=100, verbose_name='类别')
    description = models.TextField(null=True, blank=True, verbose_name='描述')
    
    # 配置数据（JSON格式存储）
    config_data = models.JSONField(verbose_name='配置数据', help_text='前端配置表单数据')
    yaml_data = models.TextField(verbose_name='YAML数据', help_text='生成的YAML测试计划内容')
    
    # 测试计划关键信息（冗余存储，便于查询和展示）
    cpu = models.CharField(max_length=100, null=True, blank=True, verbose_name='CPU类型')
    gpu = models.CharField(max_length=100, null=True, blank=True, verbose_name='GPU类型')
    machine_count = models.IntegerField(default=1, verbose_name='机器数量')
    os_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='操作系统类型')
    kernel_type = models.CharField(max_length=50, null=True, blank=True, verbose_name='内核类型')
    test_case_count = models.IntegerField(default=0, verbose_name='测试用例数量')
    
    # 状态和标签
    status = models.IntegerField(default=1, verbose_name='状态', help_text='0=草稿, 1=已发布, 2=已归档')
    tags = models.CharField(max_length=255, null=True, blank=True, verbose_name='标签', help_text='多个标签用逗号分隔')
    
    # 使用统计
    use_count = models.IntegerField(default=0, verbose_name='使用次数')
    last_used_time = models.DateTimeField(null=True, blank=True, verbose_name='最后使用时间')
    
    # 审计字段
    create_user = models.IntegerField(verbose_name='创建人ID')
    create_user_name = models.CharField(max_length=100, verbose_name='创建人名称')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    update_user = models.IntegerField(null=True, blank=True, verbose_name='更新人ID')
    update_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        db_table = 'tpgen_saved_plan'
        verbose_name = '保存的测试计划'
        verbose_name_plural = verbose_name
        ordering = ['-create_time']
        indexes = [
            models.Index(fields=['category']),
            models.Index(fields=['status']),
            models.Index(fields=['-create_time']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.category})"
