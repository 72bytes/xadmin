# loguru_config.py

from loguru import logger
import sys
import logging

logger.remove()
logger.add(sys.stdout, format="{time} {level} {message}", level="DEBUG")
logger.add("/home/zx/xadmin_zx/logs/xadmin.log", rotation="50MB", retention=10, 
           compression="zip", level="DEBUG")

class InterceptHandler(logging.Handler):
    def emit(self, record):
        level = logger.level(record.levelname).name
        logger.log(level, record.getMessage())

logging.basicConfig(handlers=[InterceptHandler()], level=0)
logging.getLogger("django").handlers = [InterceptHandler()]
