"""
Test Plan Generator Schemas
测试计划生成器API模式定义
"""
from ninja import Schema, Field
from typing import Optional


# ============================================================================
# Test Management System Schemas
# 测试管理系统API模式
# ============================================================================

# SutDevice (测试设备)
class SutDeviceIn(Schema):
    """测试设备输入模式"""
    hostname: str
    asic_name: Optional[str] = Field(None, alias='asicName')
    ip_address: Optional[str] = Field(None, alias='ipAddress')
    device_id: Optional[str] = Field(None, alias='deviceId')
    rev_id: Optional[str] = Field(None, alias='revId')
    gpu_series: Optional[str] = Field(None, alias='gpuSeries')
    gpu_model: Optional[str] = Field(None, alias='gpuModel')


class SutDeviceOut(Schema):
    """测试设备输出模式"""
    id: int
    hostname: str
    asic_name: Optional[str] = Field(None, alias='asicName')
    ip_address: Optional[str] = Field(None, alias='ipAddress')
    device_id: Optional[str] = Field(None, alias='deviceId')
    rev_id: Optional[str] = Field(None, alias='revId')
    gpu_series: Optional[str] = Field(None, alias='gpuSeries')
    gpu_model: Optional[str] = Field(None, alias='gpuModel')
    created_at: str = Field(..., alias='createdAt')
    updated_at: str = Field(..., alias='updatedAt')


# OsConfig (操作系统配置)
class OsConfigIn(Schema):
    """操作系统配置输入模式"""
    os_family: str = Field(..., alias='osFamily')
    version: str
    download_url: Optional[str] = Field(None, alias='downloadUrl')


class OsConfigOut(Schema):
    """操作系统配置输出模式"""
    id: int
    os_family: str = Field(..., alias='osFamily')
    version: str
    download_url: Optional[str] = Field(None, alias='downloadUrl')
    created_at: str = Field(..., alias='createdAt')
    updated_at: str = Field(..., alias='updatedAt')


# OsSupportedKernel (操作系统支持的内核)
class OsSupportedKernelIn(Schema):
    """内核版本输入模式"""
    os_config_id: int = Field(..., alias='osConfigId')
    kernel_version: str = Field(..., alias='kernelVersion')


class OsSupportedKernelOut(Schema):
    """内核版本输出模式"""
    id: int
    os_config_id: int = Field(..., alias='osConfigId')
    kernel_version: str = Field(..., alias='kernelVersion')


# TestType (测试类型)
class TestTypeIn(Schema):
    """测试类型输入模式"""
    type_name: str = Field(..., alias='typeName')


class TestTypeOut(Schema):
    """测试类型输出模式"""
    id: int
    type_name: str = Field(..., alias='typeName')
    created_at: str = Field(..., alias='createdAt')
    updated_at: str = Field(..., alias='updatedAt')


# TestComponent (测试组件)
class TestComponentIn(Schema):
    """测试组件输入模式"""
    test_type_id: int = Field(..., alias='testTypeId')
    component_category: Optional[str] = Field(None, alias='componentCategory')
    component_name: str = Field(..., alias='componentName')


class TestComponentOut(Schema):
    """测试组件输出模式"""
    id: int
    test_type_id: int = Field(..., alias='testTypeId')
    component_category: Optional[str] = Field(None, alias='componentCategory')
    component_name: str = Field(..., alias='componentName')


# TestCase (测试用例)
class TestCaseIn(Schema):
    """测试用例输入模式"""
    test_component_id: int = Field(..., alias='testComponentId')
    case_name: str = Field(..., alias='caseName')
    case_config: Optional[dict] = Field(default_factory=dict, alias='caseConfig')


class TestCaseOut(Schema):
    """测试用例输出模式"""
    id: int
    test_component_id: int = Field(..., alias='testComponentId')
    case_name: str = Field(..., alias='caseName')
    case_config: dict = Field(default_factory=dict, alias='caseConfig')
    created_at: str = Field(..., alias='createdAt')
    updated_at: str = Field(..., alias='updatedAt')


# TestPlan (测试计划)
class TestPlanIn(Schema):
    """测试计划输入模式"""
    plan_name: str = Field(..., alias='planName')
    plan_description: Optional[str] = Field(None, alias='planDescription')
    sut_device_id: int = Field(..., alias='sutDeviceId')
    os_config_id: int = Field(..., alias='osConfigId')
    created_by: Optional[str] = Field(None, alias='createdBy')


class TestPlanOut(Schema):
    """测试计划输出模式"""
    id: int
    plan_name: str = Field(..., alias='planName')
    plan_description: Optional[str] = Field(None, alias='planDescription')
    sut_device_id: int = Field(..., alias='sutDeviceId')
    os_config_id: int = Field(..., alias='osConfigId')
    created_by: Optional[str] = Field(None, alias='createdBy')
    created_at: str = Field(..., alias='createdAt')
    updated_at: str = Field(..., alias='updatedAt')


# TestPlanCase (测试计划与用例关联)
class TestPlanCaseIn(Schema):
    """测试计划用例关联输入模式"""
    test_plan_id: int = Field(..., alias='testPlanId')
    test_case_id: int = Field(..., alias='testCaseId')
    timeout: Optional[int] = None


class TestPlanCaseOut(Schema):
    """测试计划用例关联输出模式"""
    id: int
    test_plan_id: int = Field(..., alias='testPlanId')
    test_case_id: int = Field(..., alias='testCaseId')
    timeout: Optional[int] = None

