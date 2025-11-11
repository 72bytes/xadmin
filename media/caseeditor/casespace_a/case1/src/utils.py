"""
工具函数模块
"""

import json
import logging
from pathlib import Path


def setup_logging(level=logging.INFO):
    """配置日志"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    return logging.getLogger(__name__)


def load_config(config_path: str) -> dict:
    """加载配置文件"""
    path = Path(config_path)
    if not path.exists():
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    with open(path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_config(config_path: str, config: dict):
    """保存配置文件"""
    path = Path(config_path)
    with open(path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=2, ensure_ascii=False)

