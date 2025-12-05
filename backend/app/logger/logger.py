"""
日志系统主模块
提供简单易用的日志接口
"""
import logging
from typing import Optional
from .config import LoggerConfig, LogLevel, LogFormat, config_manager
from .handlers import logger_manager


def get_logger(name: Optional[str] = None, config: Optional[LoggerConfig] = None) -> logging.Logger:
    """
    获取日志记录器

    Args:
        name: 日志记录器名称，默认使用配置中的名称
        config: 日志配置，默认使用全局配置

    Returns:
        日志记录器实例
    """
    return logger_manager.get_logger(name, config)


def configure_logging(
    level: LogLevel = LogLevel.INFO,
    log_file: str = "app.log",
    log_dir: str = "logs",
    enable_console: bool = True,
    enable_file: bool = True,
    enable_colors: bool = True,
    format_type: LogFormat = LogFormat.DETAILED,
    max_file_size: int = 10 * 1024 * 1024,
    backup_count: int = 5
) -> None:
    """
    配置日志系统

    Args:
        level: 日志级别
        log_file: 日志文件名
        log_dir: 日志目录
        enable_console: 是否启用终端输出
        enable_file: 是否启用文件输出
        enable_colors: 是否启用彩色终端输出
        format_type: 日志格式类型
        max_file_size: 最大文件大小（字节）
        backup_count: 备份文件数量
    """
    config = LoggerConfig(
        level=level,
        log_file=log_file,
        log_dir=log_dir,
        enable_console=enable_console,
        enable_file=enable_file,
        enable_colors=enable_colors,
        format=format_type,
        max_file_size=max_file_size,
        backup_count=backup_count
    )

    # 重新加载配置
    logger_manager.reload_config(config)


def log_debug(message: str, name: Optional[str] = None):
    """记录调试信息"""
    logger = get_logger(name)
    logger.debug(message)


def log_info(message: str, name: Optional[str] = None):
    """记录信息"""
    logger = get_logger(name)
    logger.info(message)


def log_warning(message: str, name: Optional[str] = None):
    """记录警告"""
    logger = get_logger(name)
    logger.warning(message)


def log_error(message: str, name: Optional[str] = None, exception: Optional[Exception] = None):
    """记录错误"""
    logger = get_logger(name)
    if exception:
        logger.error(f"{message}: {str(exception)}", exc_info=True)
    else:
        logger.error(message)


def log_critical(message: str, name: Optional[str] = None, exception: Optional[Exception] = None):
    """记录严重错误"""
    logger = get_logger(name)
    if exception:
        logger.critical(f"{message}: {str(exception)}", exc_info=True)
    else:
        logger.critical(message)


class LoggerMixin:
    """日志记录器混入类，为其他类提供日志功能"""

    @property
    def logger(self) -> logging.Logger:
        """获取当前类的日志记录器"""
        if not hasattr(self, '_logger'):
            class_name = self.__class__.__module__ + '.' + self.__class__.__name__
            self._logger = get_logger(class_name)
        return self._logger




def init_default_logging():
    """初始化默认日志配置"""
    configure_logging(
        level=LogLevel.INFO,
        enable_console=True,
        enable_file=True,
        enable_colors=True,
        format_type=LogFormat.DETAILED
    )