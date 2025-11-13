"""
TPGEN Schema 定义
用于 API 请求和响应的数据模型
"""
from typing import Optional, Any
from pydantic import BaseModel, Field, ConfigDict


class TpgenSavedPlanIn(BaseModel):
    """创建保存的测试计划请求"""
    model_config = ConfigDict(populate_by_name=True)  # 允许使用别名
    
    name: str
    category: str
    description: Optional[str] = None
    config_data: dict = Field(..., alias='configData')  # 支持驼峰命名
    yaml_data: Any = Field(..., alias='yamlData')  # 支持对象或字符串
    cpu: Optional[str] = None
    gpu: Optional[str] = None
    machine_count: int = Field(1, alias='machineCount')
    os_type: Optional[str] = Field(None, alias='osType')
    kernel_type: Optional[str] = Field(None, alias='kernelType')
    test_case_count: int = Field(0, alias='testCaseCount')
    status: int = 1  # 0=草稿, 1=已发布, 2=已归档
    tags: Optional[str] = None


class TpgenSavedPlanUpdate(BaseModel):
    """更新保存的测试计划请求（所有字段可选）"""
    model_config = ConfigDict(populate_by_name=True)  # 允许使用别名
    
    name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    config_data: Optional[dict] = Field(None, alias='configData')
    yaml_data: Optional[Any] = Field(None, alias='yamlData')
    cpu: Optional[str] = None
    gpu: Optional[str] = None
    machine_count: Optional[int] = Field(None, alias='machineCount')
    os_type: Optional[str] = Field(None, alias='osType')
    kernel_type: Optional[str] = Field(None, alias='kernelType')
    test_case_count: Optional[int] = Field(None, alias='testCaseCount')
    status: Optional[int] = None
    tags: Optional[str] = None

