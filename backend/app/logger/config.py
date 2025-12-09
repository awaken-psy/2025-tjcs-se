"""
日志系统配置管理模块
"""
import os
from enum import Enum
from typing import Optional, Dict, Any
from pydantic import BaseModel


class LogLevel(str, Enum):
    """日志级别枚举"""
    DEBUG = "DEBUG"
    INFO = "INFO"
    WARNING = "WARNING"
    ERROR = "ERROR"
    CRITICAL = "CRITICAL"


class LogFormat(str, Enum):
    """日志格式枚举"""
    SIMPLE = "simple"
    DETAILED = "detailed"
    JSON = "json"


class LoggerConfig(BaseModel):
    """日志配置模型"""
    # 基本配置
    name: str = "timecapsule"
    level: LogLevel = LogLevel.INFO
    format: LogFormat = LogFormat.DETAILED

    # 文件输出配置
    enable_file: bool = True
    log_dir: str = "logs"
    log_file: str = "app.log"
    max_file_size: int = 10 * 1024 * 1024  # 10MB
    backup_count: int = 5

    # 终端输出配置
    enable_console: bool = True

    # 其他配置
    enable_colors: bool = True
    date_format: str = "%Y-%m-%d %H:%M:%S"

    class Config:
        use_enum_values = True

    def __init__(self, **data):
        # 确保枚举类型正确转换
        if 'level' in data and isinstance(data['level'], str):
            data['level'] = LogLevel(data['level'].upper())
        if 'format' in data and isinstance(data['format'], str):
            data['format'] = LogFormat(data['format'].lower())
        super().__init__(**data)


class LogConfigManager:
    """日志配置管理器"""

    def __init__(self):
        self._config: Optional[LoggerConfig] = None

    def load_from_env(self) -> LoggerConfig:
        """从环境变量加载配置"""
        config = LoggerConfig()

        # 从环境变量读取配置
        if os.getenv("LOG_LEVEL"):
            config.level = LogLevel(os.getenv("LOG_LEVEL", "INFO").upper())

        if os.getenv("LOG_FORMAT"):
            config.format = LogFormat(os.getenv("LOG_FORMAT", "detailed").lower())

        if os.getenv("LOG_DIR"):
            config.log_dir = os.getenv("LOG_DIR", "./logs")

        if os.getenv("LOG_FILE"):
            config.log_file = os.getenv("LOG_FILE", "app.log")

        if os.getenv("ENABLE_CONSOLE") is not None:
            config.enable_console = os.getenv("ENABLE_CONSOLE", "true").lower() == "true"

        if os.getenv("ENABLE_FILE") is not None:
            config.enable_file = os.getenv("ENABLE_FILE", "true").lower() == "true"

        self._config = config
        return config

    def get_config(self) -> LoggerConfig:
        """获取当前配置"""
        if self._config is None:
            self._config = self.load_from_env()
        return self._config

    def set_config(self, config: LoggerConfig) -> None:
        """设置配置"""
        self._config = config

    def get_log_format_string(self, format_type: LogFormat) -> str:
        """获取日志格式字符串"""
        date_format = self.get_config().date_format

        formats = {
            LogFormat.SIMPLE: "%(levelname)s - %(message)s",
            LogFormat.DETAILED: f"%(asctime)s - %(name)s - %(levelname)s - %(module)s:%(lineno)d - %(message)s",
            LogFormat.JSON: '{"timestamp": "%(asctime)s", "logger": "%(name)s", "level": "%(levelname)s", "module": "%(module)s", "line": %(lineno)d, "message": "%(message)s"}'
        }

        return formats.get(format_type, formats[LogFormat.DETAILED])


# 全局配置管理器实例
config_manager = LogConfigManager()