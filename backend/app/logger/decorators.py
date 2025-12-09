"""
API日志装饰器
用于记录FastAPI接口的调用情况
"""
import time
import json
from typing import Any, Callable
from functools import wraps
import inspect
from datetime import datetime
from .logger import get_logger


class CustomJSONEncoder(json.JSONEncoder):
    """自定义JSON编码器，处理特殊类型"""

    def default(self, obj):
        # 处理datetime类型
        if isinstance(obj, datetime):
            return obj.isoformat()

        # 处理其他特殊类型
        if hasattr(obj, '__dict__'):
            return str(obj)

        # 调用父类默认处理
        return super().default(obj)


def api_logging(logger):
    """
    API日志装饰器

    Args:
        logger: 日志记录器对象

    Usage:
        from app.logger import api_logger
        from app.logger.decorators import api_logging

        @api_logging(api_logger)
        async def my_api_endpoint(request, pydantic_model, ...):
            pass
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def wrapper(*args, **kwargs) -> Any:
            # 记录开始时间
            start_time = time.time()

            # 获取接口信息
            endpoint_name = f"{func.__module__}.{func.__name__}"

            # 获取函数参数名
            sig = inspect.signature(func)
            param_names = list(sig.parameters.keys())

            # 构建参数字典
            params = {}
            for i, arg in enumerate(args):
                if i < len(param_names):
                    param_name = param_names[i]
                    params[param_name] = _serialize_value(arg)

            # 添加关键字参数
            for key, value in kwargs.items():
                params[key] = _serialize_value(value)

            # 记录请求开始
            log_data = {
                "接口名称": endpoint_name,
                "参数": params
            }

            logger.info(f"API请求开始: {json.dumps(log_data, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)}")

            try:
                # 执行原函数
                result = await func(*args, **kwargs)

                # 计算处理时间
                end_time = time.time()
                processing_time = round((end_time - start_time) * 1000, 2)  # 毫秒

                # 记录响应信息
                response_log = {
                    "接口名称": endpoint_name,
                    "处理状态": "成功",
                    "处理总用时(毫秒)": processing_time,
                    "响应内容": _serialize_value(result)
                }

                logger.info(f"API请求完成: {json.dumps(response_log, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)}")

                return result

            except Exception as e:
                # 计算处理时间
                end_time = time.time()
                processing_time = round((end_time - start_time) * 1000, 2)

                # 记录错误信息
                error_log = {
                    "接口名称": endpoint_name,
                    "处理状态": "失败",
                    "错误信息": str(e),
                    "处理总用时(毫秒)": processing_time
                }

                logger.error(f"API请求异常: {json.dumps(error_log, ensure_ascii=False, indent=2, cls=CustomJSONEncoder)}", exc_info=True)

                # 重新抛出异常
                raise

        return wrapper
    return decorator


def _serialize_value(value: Any) -> Any:
    """序列化值为JSON可表示的格式"""
    try:
        # 处理None值
        if value is None:
            return None

        # 处理基本类型
        if isinstance(value, (str, int, float, bool)):
            return value

        # 处理datetime类型
        if isinstance(value, datetime):
            return value.isoformat()

        # 处理Pydantic模型
        if hasattr(value, 'dict'):
            return value.dict()

        # 处理有__dict__的对象
        if hasattr(value, '__dict__'):
            return str(value)

        # 处理字典
        if isinstance(value, dict):
            return {k: _serialize_value(v) for k, v in value.items()}

        # 处理列表和元组
        if isinstance(value, (list, tuple)):
            return [_serialize_value(item) for item in value]

        # 其他类型转为字符串
        return str(value)

    except Exception:
        return f"<无法序列化的对象: {type(value).__name__}>"