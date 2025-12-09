"""
日志处理器模块
"""
import logging
import logging.handlers
import os
import sys
from pathlib import Path
from typing import Optional

from .config import LoggerConfig, LogLevel, LogFormat, config_manager


class ColoredConsoleHandler(logging.StreamHandler):
    """支持彩色输出的终端处理器"""

    # ANSI 颜色代码
    COLORS = {
        'DEBUG': '\033[36m',      # 青色
        'INFO': '\033[32m',       # 绿色
        'WARNING': '\033[33m',    # 黄色
        'ERROR': '\033[31m',      # 红色
        'CRITICAL': '\033[35m',   # 紫色
        'RESET': '\033[0m'        # 重置
    }

    def __init__(self, stream=None, enable_colors: bool = True):
        super().__init__(stream)
        self.enable_colors = enable_colors and hasattr(stream, 'isatty') and stream.isatty()

    def format(self, record):
        """格式化日志记录并添加颜色"""
        message = super().format(record)

        if self.enable_colors and record.levelname in self.COLORS:
            color = self.COLORS[record.levelname]
            reset = self.COLORS['RESET']
            return f"{color}{message}{reset}"

        return message


class RotatingFileHandler(logging.handlers.RotatingFileHandler):
    """自动轮转的文件处理器"""

    def __init__(self,
                 log_dir: str,
                 log_file: str,
                 max_bytes: int = 10*1024*1024,
                 backup_count: int = 5,
                 encoding: str = 'utf-8'):

        # 确保日志目录存在
        log_path = Path(log_dir)
        log_path.mkdir(parents=True, exist_ok=True)

        full_path = log_path / log_file
        super().__init__(
            filename=str(full_path),
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding=encoding
        )


class HandlerFactory:
    """日志处理器工厂类"""

    @staticmethod
    def create_console_handler(config: LoggerConfig) -> Optional[logging.Handler]:
        """创建终端处理器"""
        if not config.enable_console:
            return None

        handler = ColoredConsoleHandler(
            stream=sys.stdout,
            enable_colors=config.enable_colors
        )

        # 设置日志级别
        if isinstance(config.level, str):
            handler.setLevel(getattr(logging, config.level.upper()))
        else:
            handler.setLevel(getattr(logging, config.level.value))

        # 设置格式化器
        formatter = HandlerFactory._create_formatter(config)
        handler.setFormatter(formatter)

        return handler

    @staticmethod
    def create_file_handler(config: LoggerConfig) -> Optional[logging.Handler]:
        """创建文件处理器"""
        if not config.enable_file:
            return None

        handler = RotatingFileHandler(
            log_dir=config.log_dir,
            log_file=config.log_file,
            max_bytes=config.max_file_size,
            backup_count=config.backup_count
        )

        # 设置日志级别
        if isinstance(config.level, str):
            handler.setLevel(getattr(logging, config.level.upper()))
        else:
            handler.setLevel(getattr(logging, config.level.value))

        # 设置格式化器
        formatter = HandlerFactory._create_formatter(config)
        handler.setFormatter(formatter)

        return handler

    @staticmethod
    def _create_formatter(config: LoggerConfig) -> logging.Formatter:
        """创建日志格式化器"""
        format_string = config_manager.get_log_format_string(config.format)
        date_format = config.date_format

        return logging.Formatter(
            fmt=format_string,
            datefmt=date_format
        )


class LoggerManager:
    """日志记录器管理器"""

    def __init__(self):
        self._loggers: dict[str, logging.Logger] = {}

    def get_logger(self, name: Optional[str] = None, config: Optional[LoggerConfig] = None) -> logging.Logger:
        """获取或创建日志记录器"""
        if config is None:
            config = config_manager.get_config()

        if name is None:
            name = config.name

        # 如果已存在该名称的日志记录器，直接返回
        if name in self._loggers:
            return self._loggers[name]

        # 创建新的日志记录器
        logger = logging.getLogger(name)

        # 避免重复添加处理器
        if logger.handlers:
            self._loggers[name] = logger
            return logger

        # 设置日志级别
        if isinstance(config.level, str):
            logger.setLevel(getattr(logging, config.level.upper()))
        else:
            logger.setLevel(getattr(logging, config.level.value))

        # 创建并添加处理器
        console_handler = HandlerFactory.create_console_handler(config)
        if console_handler:
            logger.addHandler(console_handler)

        file_handler = HandlerFactory.create_file_handler(config)
        if file_handler:
            logger.addHandler(file_handler)

        # 防止日志传播到根记录器
        logger.propagate = False

        # 缓存日志记录器
        self._loggers[name] = logger

        return logger

    def clear_handlers(self, logger_name: Optional[str] = None):
        """清除指定日志记录器的所有处理器"""
        if logger_name is None:
            # 清除所有缓存的日志记录器的处理器
            for logger in self._loggers.values():
                logger.handlers.clear()
        else:
            logger = logging.getLogger(logger_name)
            logger.handlers.clear()

    def reload_config(self, config: LoggerConfig):
        """重新加载配置并更新所有日志记录器"""
        config_manager.set_config(config)

        # 清除所有现有处理器
        for name in list(self._loggers.keys()):
            logger = self._loggers[name]
            logger.handlers.clear()

        # 重新创建日志记录器
        self._loggers.clear()


# 全局日志管理器实例
logger_manager = LoggerManager()