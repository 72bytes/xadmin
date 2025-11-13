"""
YAML Check 模块专用日志配置
"""

from loguru import logger
import sys
from pathlib import Path

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent

# 创建 logs 目录（如果不存在）
LOG_DIR = BASE_DIR / 'logs'
LOG_DIR.mkdir(exist_ok=True)

# 日志文件路径
LOG_FILE = LOG_DIR / 'yaml_check.log'

# 创建专用 logger
yaml_check_logger = logger.bind(module='yaml_check')

# 移除默认处理器
yaml_check_logger.remove()

# 添加控制台输出（开发环境）
yaml_check_logger.add(
    sys.stdout,
    format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>yaml_check</cyan> | <level>{message}</level>",
    level="DEBUG",
    colorize=True
)

# 添加文件输出
yaml_check_logger.add(
    str(LOG_FILE),
    format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} | {message}",
    level="INFO",
    rotation="10 MB",  # 文件达到10MB时轮转
    retention="30 days",  # 保留30天
    compression="zip",  # 压缩旧日志
    encoding="utf-8",
    backtrace=True,  # 显示完整的错误堆栈
    diagnose=True   # 显示变量值
)

# 导出 logger
__all__ = ['yaml_check_logger']

