"""
XCase 数据模型

定义用例管理相关的数据库模型：
- CaseMetadata: 用例元数据
- CaseTag: 用例标签
- CaseOption: 用例选项（键值对）
"""
from django.db import models


class ModelSaveMixin:
    """模型保存混入类"""
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)


class CaseMetadata(ModelSaveMixin, models.Model):
    """
    Case 元数据表
    
    存储每个 Case 的基本信息，作为其他相关数据的关联点。
    每个 Case 通过 casespace 和 case_name 的组合唯一标识。
    """
    id = models.BigAutoField(primary_key=True, db_comment='ID')
    casespace = models.CharField(max_length=255, db_comment='Casespace名称', db_index=True)
    case_name = models.CharField(max_length=255, db_comment='Case名称', db_index=True)
    create_time = models.DateTimeField(auto_now_add=True, db_comment='创建时间')
    update_time = models.DateTimeField(auto_now=True, db_comment='更新时间')
    
    class Meta:
        db_table = 'case_metadata'
        unique_together = (('casespace', 'case_name'),)
        db_table_comment = 'Case元数据表'
        indexes = [
            models.Index(fields=['casespace', 'case_name']),
            models.Index(fields=['create_time']),
            models.Index(fields=['update_time']),
        ]
        ordering = ['-update_time']
    
    def __str__(self):
        return f'<{self.casespace}/{self.case_name}>'
    
    def __repr__(self):
        return f'CaseMetadata(id={self.id}, casespace="{self.casespace}", case_name="{self.case_name}")'


class CaseTag(models.Model):
    """
    Case 标签表
    
    存储 Case 的标签信息，用于分类和检索。
    一个 Case 可以有多个标签，每个标签是一个简单的字符串。
    """
    id = models.BigAutoField(primary_key=True, db_comment='ID')
    metadata = models.ForeignKey(
        CaseMetadata,
        on_delete=models.CASCADE,
        related_name='tags',
        db_comment='关联的case元数据'
    )
    tag = models.CharField(max_length=100, db_comment='标签名称', db_index=True)
    create_time = models.DateTimeField(auto_now_add=True, db_comment='创建时间')
    
    class Meta:
        db_table = 'case_tag'
        unique_together = (('metadata', 'tag'),)
        db_table_comment = 'Case标签表'
        indexes = [
            models.Index(fields=['tag']),
            models.Index(fields=['metadata', 'tag']),
        ]
        ordering = ['tag']
    
    def __str__(self):
        return f'<{self.metadata.case_name}: {self.tag}>'
    
    def __repr__(self):
        return f'CaseTag(id={self.id}, case="{self.metadata.case_name}", tag="{self.tag}")'


class CaseOption(models.Model):
    """
    Case 选项表
    
    存储 Case 的键值对选项信息，用于存储自定义元数据。
    每个选项是一个键值对，键在同一 Case 中唯一。
    """
    id = models.BigAutoField(primary_key=True, db_comment='ID')
    metadata = models.ForeignKey(
        CaseMetadata,
        on_delete=models.CASCADE,
        related_name='options',
        db_comment='关联的case元数据'
    )
    key = models.CharField(max_length=100, db_comment='选项键', db_index=True)
    value = models.CharField(max_length=500, db_comment='选项值')
    create_time = models.DateTimeField(auto_now_add=True, db_comment='创建时间')
    update_time = models.DateTimeField(auto_now=True, db_comment='更新时间')
    
    class Meta:
        db_table = 'case_option'
        unique_together = (('metadata', 'key'),)
        db_table_comment = 'Case选项表'
        indexes = [
            models.Index(fields=['key']),
            models.Index(fields=['metadata', 'key']),
        ]
        ordering = ['key']
    
    def __str__(self):
        return f'<{self.metadata.case_name}: {self.key}={self.value}>'
    
    def __repr__(self):
        return f'CaseOption(id={self.id}, case="{self.metadata.case_name}", key="{self.key}", value="{self.value}")'

