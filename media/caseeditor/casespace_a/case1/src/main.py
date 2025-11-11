#!/usr/bin/env python3
"""
主应用入口
"""

import sys
from utils import setup_logging, load_config


def main():
    """主函数"""
    # 设置日志
    logger = setup_logging()
    logger.info("应用启动中...")
    
    # 加载配置
    config = load_config("config/settings.json")
    
    # 启动应用
    app = create_app(config)
    app.run(
        host=config['server']['host'],
        port=config['server']['port']
    )


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"错误: {e}", file=sys.stderr)
        sys.exit(1)

