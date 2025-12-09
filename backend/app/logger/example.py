"""
日志系统使用示例
"""
import sys
import os
from pathlib import Path

# 添加项目根目录到 Python 路径
current_dir = Path(__file__).parent
project_root = current_dir.parent.parent
sys.path.insert(0, str(project_root))

from app.logger import (
    get_logger,
    configure_logging,
    log_debug,
    log_info,
    log_warning,
    log_error,
    log_critical,
    LoggerMixin,
    app_logger,
    LogLevel,
    LogFormat
)


def basic_usage_example():
    """基本使用示例"""
    print("=== 基本使用示例 ===")

    # 使用预定义的日志记录器
    app_logger.info("应用程序启动")
    app_logger.debug("调试信息")
    app_logger.warning("警告信息")
    app_logger.error("错误信息")
    app_logger.critical("严重错误")

    # 使用快捷函数
    log_info("使用快捷函数记录信息")
    log_debug("使用快捷函数记录调试信息", "custom_logger")
    log_warning("使用快捷函数记录警告")


def custom_configuration_example():
    """自定义配置示例"""
    print("\n=== 自定义配置示例 ===")

    # 配置自定义日志设置
    configure_logging(
        level=LogLevel.DEBUG,
        log_file="custom.log",
        enable_console=True,
        enable_file=True,
        enable_colors=True,
        format_type=LogFormat.SIMPLE
    )

    # 获取自定义日志记录器
    custom_logger = get_logger("custom.example")
    custom_logger.debug("自定义配置的调试信息")
    custom_logger.info("自定义配置的信息")
    custom_logger.warning("自定义配置的警告")


class ServiceExample(LoggerMixin):
    """在类中使用日志的示例"""

    def process_data(self, data):
        """处理数据的示例方法"""
        self.logger.info(f"开始处理数据: {data}")

        try:
            # 模拟处理过程
            if data is None:
                self.logger.warning("数据为空，跳过处理")
                return None

            # 模拟一个错误
            if data == "error":
                raise ValueError("模拟的处理错误")

            self.logger.debug(f"数据处理完成: {len(str(data))} 字符")
            return f"processed_{data}"

        except Exception as e:
            self.logger.error(f"数据处理失败: {str(e)}", exc_info=True)
            return None


def class_logging_example():
    """类中日志使用示例"""
    print("\n=== 类中日志使用示例 ===")

    service = ServiceExample()

    # 正常处理
    result1 = service.process_data("test_data")
    if result1:
        service.logger.info(f"处理成功: {result1}")

    # 空数据处理
    result2 = service.process_data(None)

    # 错误处理
    result3 = service.process_data("error")


def error_logging_example():
    """错误日志记录示例"""
    print("\n=== 错误日志记录示例 ===")

    try:
        # 模拟一个异常
        raise ValueError("这是一个示例异常")
    except Exception as e:
        # 使用快捷函数记录错误（包含异常信息）
        log_error("捕获到异常", exception=e)

        # 记录严重错误
        log_critical("应用程序发生严重错误", exception=e)


if __name__ == "__main__":
    """运行所有示例"""
    print("时光胶囊日志系统使用示例")
    print("=" * 50)

    # 运行各种示例
    basic_usage_example()
    custom_configuration_example()
    class_logging_example()
    error_logging_example()

    print("\n" + "=" * 50)
    print("示例完成！请查看控制台输出和日志文件。")