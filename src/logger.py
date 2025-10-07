"""
日志模块
配置loguru日志系统
"""

import sys
from pathlib import Path
from loguru import logger
from .config import config


def setup_logger() -> None:
    """设置日志配置"""
    # 移除默认的日志处理器
    logger.remove()
    
    # 创建日志目录
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # 控制台日志
    logger.add(
        sys.stdout,
        level=config.LOG_LEVEL,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
               "<level>{message}</level>",
        colorize=True
    )
    
    # 文件日志 - 普通日志
    logger.add(
        log_dir / "app.log",
        level="INFO",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="1 day",
        retention="7 days",
        compression="zip"
    )
    
    # 文件日志 - 错误日志
    logger.add(
        log_dir / "error.log",
        level="ERROR",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
        rotation="1 day",
        retention="30 days",
        compression="zip"
    )


def get_logger(name: str = __name__):
    """获取日志记录器"""
    return logger.bind(name=name)


# 初始化日志
setup_logger()

# 导出默认日志记录器
__all__ = ["logger", "get_logger", "setup_logger"]