from .config import (
    LoggerConfig,
    LogLevel,
    LogFormat,
    config_manager
)

__version__ = "1.0.0"
__author__ = "Time Capsule Team"

from .logger import (
    get_logger,
    configure_logging,
    log_debug,
    log_info,
    log_warning,
    log_error,
    log_critical,
    LoggerMixin,
    init_default_logging
)

# 首先初始化默认日志配置
try:
    init_default_logging()
except Exception as e:
    # 如果初始化失败，打印错误信息但不要中断程序
    import sys
    print(f"Warning: Failed to initialize default logging: {e}", file=sys.stderr)

# 在日志配置初始化之后创建预定义的日志记录器
app_logger = get_logger("timecapsule.app")
api_logger = get_logger("timecapsule.api")
db_logger = get_logger("timecapsule.database")
auth_logger = get_logger("timecapsule.auth")

__all__ = [
    'get_logger',
    'configure_logging',
    'log_debug',
    'log_info',
    'log_warning',
    'log_error',
    'log_critical',
    'LoggerMixin',
    'app_logger',
    'api_logger',
    'db_logger',
    'auth_logger',
    'init_default_logging',

    'LoggerConfig',
    'LogLevel',
    'LogFormat',
    'config_manager',
]