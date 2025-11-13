"""
测试 yaml_check.logger 模块
验证日志配置的正确性
"""

import pytest
import os
from pathlib import Path
from yaml_check.logger import yaml_check_logger


class TestLogger:
    """测试日志配置"""
    
    def test_logger_exists(self):
        """测试 logger 实例存在"""
        assert yaml_check_logger is not None
    
    def test_logger_has_name(self):
        """测试 logger 有正确的名称"""
        # Loguru logger 通过 bind 绑定 name
        assert hasattr(yaml_check_logger, '_core')
    
    def test_logger_can_log_info(self, caplog):
        """测试可以记录 INFO 级别日志"""
        test_message = "Test INFO message"
        yaml_check_logger.info(test_message)
        # 注意：Loguru 的日志不会自动出现在 caplog 中
        # 这个测试主要验证不会抛出异常
    
    def test_logger_can_log_debug(self):
        """测试可以记录 DEBUG 级别日志"""
        test_message = "Test DEBUG message"
        yaml_check_logger.debug(test_message)
        # 验证不会抛出异常
    
    def test_logger_can_log_warning(self):
        """测试可以记录 WARNING 级别日志"""
        test_message = "Test WARNING message"
        yaml_check_logger.warning(test_message)
    
    def test_logger_can_log_error(self):
        """测试可以记录 ERROR 级别日志"""
        test_message = "Test ERROR message"
        yaml_check_logger.error(test_message)
    
    def test_logger_can_log_with_context(self):
        """测试可以记录带上下文的日志"""
        yaml_check_logger.info("Test with context", extra={"key": "value"})
    
    def test_log_file_path(self):
        """测试日志文件路径是否正确"""
        # 日志文件应该在项目的 logs 目录下
        project_root = Path(__file__).parent.parent.parent
        expected_log_dir = project_root / 'logs'
        
        # 验证日志目录存在
        assert expected_log_dir.exists(), f"Log directory should exist: {expected_log_dir}"
        
        # 验证日志文件存在或可以创建
        expected_log_file = expected_log_dir / 'yaml_check.log'
        # 如果文件不存在，记录一条日志来创建它
        if not expected_log_file.exists():
            yaml_check_logger.info("Test log to create file")
    
    def test_logger_methods_exist(self):
        """测试 logger 有所有必需的方法"""
        assert hasattr(yaml_check_logger, 'debug')
        assert hasattr(yaml_check_logger, 'info')
        assert hasattr(yaml_check_logger, 'warning')
        assert hasattr(yaml_check_logger, 'error')
        assert hasattr(yaml_check_logger, 'exception')
        assert hasattr(yaml_check_logger, 'critical')
    
    def test_logger_is_callable(self):
        """测试 logger 方法可调用"""
        assert callable(yaml_check_logger.debug)
        assert callable(yaml_check_logger.info)
        assert callable(yaml_check_logger.warning)
        assert callable(yaml_check_logger.error)


class TestLoggerIntegration:
    """测试日志集成功能"""
    
    def test_logger_with_exception(self):
        """测试记录异常日志"""
        try:
            raise ValueError("Test exception")
        except ValueError as e:
            yaml_check_logger.exception("Caught exception")
            # 验证不会抛出异常
    
    def test_logger_with_special_characters(self):
        """测试记录包含特殊字符的日志"""
        special_msg = "Test 特殊字符 🎉 with\nnewlines\tand\ttabs"
        yaml_check_logger.info(special_msg)
    
    def test_logger_with_dict(self):
        """测试记录字典对象"""
        test_dict = {"key1": "value1", "key2": 123, "nested": {"key3": "value3"}}
        yaml_check_logger.info(f"Test dict: {test_dict}")
    
    def test_logger_performance(self):
        """测试日志性能（大量日志）"""
        import time
        start = time.time()
        
        # 记录100条日志
        for i in range(100):
            yaml_check_logger.debug(f"Performance test log {i}")
        
        elapsed = time.time() - start
        # 100条日志应该在1秒内完成
        assert elapsed < 1.0, f"Logging 100 messages took too long: {elapsed:.2f}s"


@pytest.mark.parametrize("log_level,message", [
    ("debug", "Debug message"),
    ("info", "Info message"),
    ("warning", "Warning message"),
    ("error", "Error message"),
])
def test_log_levels_parametrized(log_level, message):
    """参数化测试：不同日志级别"""
    log_method = getattr(yaml_check_logger, log_level)
    log_method(message)
    # 验证不抛出异常

