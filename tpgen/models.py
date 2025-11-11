"""
Test Plan Generator Models
测试计划生成器模型
"""
from django.db import models


class ModelSaveMixin:
    """模型保存Mixin"""
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


# ============================================================================
# Test Management System Models
# 测试管理系统模型
# ============================================================================

class SutDevice(ModelSaveMixin, models.Model):
    """测试设备表 - 存储所有SUT (System Under Test) 测试设备信息"""
    id = models.BigAutoField(primary_key=True, db_comment='主键')
    hostname = models.CharField(max_length=255, unique=True, db_comment='设备主机名（唯一）')
    asic_name = models.CharField(max_length=255, blank=True, null=True, db_comment='ASIC名称（如 Navi 31 GFX1100）')
    ip_address = models.GenericIPAddressField(blank=True, null=True, db_index=True, db_comment='IP地址')
    device_id = models.CharField(max_length=50, blank=True, null=True, db_comment='设备ID')
    rev_id = models.CharField(max_length=50, blank=True, null=True, db_comment='版本ID')
    gpu_series = models.CharField(max_length=100, blank=True, null=True, db_comment='GPU系列（如 Radeon RX 7000）')
    gpu_model = models.CharField(max_length=100, blank=True, null=True, db_index=True, db_comment='GPU型号（如 RX 7900 XTX）')
    created_at = models.DateTimeField(auto_now_add=True, db_comment='创建时间')
    updated_at = models.DateTimeField(auto_now=True, db_comment='更新时间')

    class Meta:
        db_table = 'sut_devices'
        db_table_comment = '测试设备表'
        indexes = [
            models.Index(fields=['hostname'], name='idx_sut_devices_hostname'),
            models.Index(fields=['asic_name'], name='idx_sut_devices_asic_name'),
            models.Index(fields=['gpu_model'], name='idx_sut_devices_gpu_model'),
        ]

    def __str__(self):
        return f'<{self.id}, {self.hostname}>'


class OsConfig(ModelSaveMixin, models.Model):
    """操作系统配置表 - 存储支持的操作系统配置"""
    id = models.BigAutoField(primary_key=True, db_comment='主键')
    os_family = models.CharField(max_length=100, db_index=True, db_comment='操作系统家族（如 Ubuntu, RHEL）')
    version = models.CharField(max_length=50, db_index=True, db_comment='操作系统版本')
    download_url = models.CharField(max_length=500, blank=True, null=True, db_comment='镜像下载链接')
    created_at = models.DateTimeField(auto_now_add=True, db_comment='创建时间')
    updated_at = models.DateTimeField(auto_now=True, db_comment='更新时间')

    class Meta:
        db_table = 'os_configs'
        db_table_comment = '操作系统配置表'
        unique_together = (('os_family', 'version'),)
        indexes = [
            models.Index(fields=['os_family'], name='idx_os_configs_os_family'),
            models.Index(fields=['version'], name='idx_os_configs_version'),
        ]

    def __str__(self):
        return f'<{self.os_family} {self.version}>'


class OsSupportedKernel(models.Model):
    """操作系统支持的内核版本表 - 存储每个操作系统配置支持的内核版本"""
    id = models.BigAutoField(primary_key=True, db_comment='主键')
    os_config = models.ForeignKey(
        OsConfig, 
        on_delete=models.CASCADE, 
        related_name='supported_kernels',
        db_comment='关联的操作系统配置ID'
    )
    kernel_version = models.CharField(max_length=100, db_index=True, db_comment='内核版本号')

    class Meta:
        db_table = 'os_supported_kernels'
        db_table_comment = '操作系统支持的内核版本表'
        unique_together = (('os_config', 'kernel_version'),)
        indexes = [
            models.Index(fields=['os_config'], name='idx_os_kernels_os_config'),
            models.Index(fields=['kernel_version'], name='idx_os_kernels_version'),
        ]

    def __str__(self):
        return f'<{self.os_config.os_family} - {self.kernel_version}>'


class TestType(ModelSaveMixin, models.Model):
    """测试类型表 - 存储测试类型（如 Benchmark, Functional, Performance）"""
    id = models.BigAutoField(primary_key=True, db_comment='主键')
    type_name = models.CharField(max_length=100, unique=True, db_index=True, db_comment='测试类型名称')
    created_at = models.DateTimeField(auto_now_add=True, db_comment='创建时间')
    updated_at = models.DateTimeField(auto_now=True, db_comment='更新时间')

    class Meta:
        db_table = 'test_types'
        db_table_comment = '测试类型表'
        indexes = [
            models.Index(fields=['type_name'], name='idx_test_types_type_name'),
        ]

    def __str__(self):
        return f'<{self.type_name}>'


class TestComponent(models.Model):
    """测试组件表 - 存储测试类型下的具体测试组件"""
    id = models.BigAutoField(primary_key=True, db_comment='主键')
    test_type = models.ForeignKey(
        TestType,
        on_delete=models.CASCADE,
        related_name='components',
        db_comment='关联的测试类型ID'
    )
    component_category = models.CharField(
        max_length=100, 
        blank=True, 
        null=True, 
        db_index=True,
        db_comment='组件分类（如 Media, Compute）'
    )
    component_name = models.CharField(max_length=255, db_index=True, db_comment='组件名称（如 ffmpeg, clpeak）')

    class Meta:
        db_table = 'test_components'
        db_table_comment = '测试组件表'
        unique_together = (('test_type', 'component_category', 'component_name'),)
        indexes = [
            models.Index(fields=['test_type'], name='idx_test_components_test_type'),
            models.Index(fields=['component_category'], name='idx_test_components_category'),
            models.Index(fields=['component_name'], name='idx_test_components_name'),
        ]

    def __str__(self):
        return f'<{self.component_name}>'


class TestCase(ModelSaveMixin, models.Model):
    """测试用例表 - 存储具体的测试用例"""
    id = models.BigAutoField(primary_key=True, db_comment='主键')
    test_component = models.ForeignKey(
        TestComponent,
        on_delete=models.CASCADE,
        related_name='test_cases',
        db_comment='关联的测试组件ID'
    )
    case_name = models.CharField(max_length=255, db_index=True, db_comment='测试用例名称')
    case_config = models.JSONField(default=dict, blank=True, db_comment='测试用例配置（JSON格式）')
    created_at = models.DateTimeField(auto_now_add=True, db_comment='创建时间')
    updated_at = models.DateTimeField(auto_now=True, db_comment='更新时间')

    class Meta:
        db_table = 'test_cases'
        db_table_comment = '测试用例表'
        unique_together = (('test_component', 'case_name'),)
        indexes = [
            models.Index(fields=['test_component'], name='idx_test_cases_component'),
            models.Index(fields=['case_name'], name='idx_test_cases_case_name'),
        ]

    def __str__(self):
        return f'<{self.case_name}>'


class TestPlan(ModelSaveMixin, models.Model):
    """测试计划表 - 存储测试计划（关联设备和操作系统配置）"""
    id = models.BigAutoField(primary_key=True, db_comment='主键')
    plan_name = models.CharField(max_length=255, db_comment='测试计划名称')
    plan_description = models.TextField(blank=True, null=True, db_comment='测试计划描述')
    sut_device = models.ForeignKey(
        SutDevice,
        on_delete=models.CASCADE,
        related_name='test_plans',
        db_comment='关联的测试设备ID'
    )
    os_config = models.ForeignKey(
        OsConfig,
        on_delete=models.RESTRICT,
        related_name='test_plans',
        db_comment='关联的操作系统配置ID'
    )
    created_by = models.CharField(max_length=100, blank=True, null=True, db_comment='创建者')
    created_at = models.DateTimeField(auto_now_add=True, db_comment='创建时间')
    updated_at = models.DateTimeField(auto_now=True, db_comment='更新时间')

    class Meta:
        db_table = 'test_plans'
        db_table_comment = '测试计划表'
        indexes = [
            models.Index(fields=['sut_device'], name='idx_test_plans_sut_device'),
            models.Index(fields=['os_config'], name='idx_test_plans_os_config'),
        ]

    def __str__(self):
        return f'<{self.id}, {self.plan_name}>'


class TestPlanCase(models.Model):
    """测试计划与用例关联表 - 多对多关系表，关联测试计划和测试用例"""
    id = models.BigAutoField(primary_key=True, db_comment='主键')
    test_plan = models.ForeignKey(
        TestPlan,
        on_delete=models.CASCADE,
        related_name='plan_cases',
        db_comment='关联的测试计划ID'
    )
    test_case = models.ForeignKey(
        TestCase,
        on_delete=models.CASCADE,
        related_name='plan_cases',
        db_comment='关联的测试用例ID'
    )
    timeout = models.IntegerField(blank=True, null=True, db_comment='超时时长（秒）')

    class Meta:
        db_table = 'test_plan_cases'
        db_table_comment = '测试计划与用例关联表'
        unique_together = (('test_plan', 'test_case'),)
        indexes = [
            models.Index(fields=['test_plan'], name='idx_test_plan_cases_test_plan'),
            models.Index(fields=['test_case'], name='idx_test_plan_cases_test_case'),
        ]

    def __str__(self):
        return f'<Plan: {self.test_plan.plan_name}, Case: {self.test_case.case_name}>'
