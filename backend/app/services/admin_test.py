"""
管理员服务层 (admin.py)

该文件定义了管理员专用的业务逻辑服务，包括：
1. 获取用户验证码信息
2. 系统状态监控
3. 其他管理员专用的测试功能

所有管理员权限验证在API层完成，该层专注于业务逻辑处理。
"""
import logging
from typing import Dict, Tuple, Optional, Any
from datetime import datetime

from app.services.verifycode import verify_code_manager

logger = logging.getLogger(__name__)

class AdminTestService:
    """管理员测试服务主类"""

    def __init__(self):
        self.verify_manager = verify_code_manager

    def get_user_verification_code(self, email: str) -> Tuple[bool, str, Optional[Dict]]:
        """
        获取指定用户邮箱的当前注册验证码

        Args:
            email: 用户邮箱地址

        Returns:
            tuple: (success, message, data)
                - success: 操作是否成功
                - message: 响应消息
                - data: 包含验证码信息的字典（操作成功时）
        """
        try:
            # 基本邮箱格式验证
            if "@" not in email or "." not in email:
                return False, "邮箱格式无效", None

            # 检查Redis连接
            if not self.verify_manager.redis_client:
                return False, "系统错误：Redis客户端未连接", None

            # 获取Redis key和验证码
            redis_key = self.verify_manager._get_redis_key(email)
            stored_code = self.verify_manager.redis_client.get(redis_key)
            ttl = self.verify_manager.redis_client.ttl(redis_key)

            if not stored_code:
                # 没有验证码的情况
                data = {
                    "email": email,
                    "has_code": False,
                    "message": "该邮箱当前没有有效的验证码"
                }
                return True, f"邮箱 {email} 没有有效的验证码", data

            # 有验证码的情况
            code_str = stored_code if isinstance(stored_code, str) else stored_code.decode('utf-8')

            data = {
                "email": email,
                "has_code": True,
                "verification_code": code_str,
                "ttl_seconds": ttl if ttl > 0 else 0,
                "expire_minutes": self.verify_manager.expire_minutes,
                "retrieved_at": datetime.now().isoformat()
            }

            return True, f"成功获取邮箱 {email} 的验证码", data

        except Exception as e:
            logger.error(f"获取用户验证码失败: {str(e)}")
            return False, f"获取验证码失败: {str(e)}", None

    def get_system_status(self) -> Tuple[bool, str, Optional[Dict]]:
        """
        获取系统状态信息

        Returns:
            tuple: (success, message, data)
                - success: 操作是否成功
                - message: 响应消息
                - data: 系统状态信息字典
        """
        try:
            status_info = {
                "redis_connected": self.verify_manager.redis_client is not None,
                "verification_expire_minutes": self.verify_manager.expire_minutes,
                "thread_pool_active": self.verify_manager.executor._threads is not None,
                "checked_at": datetime.now().isoformat()
            }

            # 测试Redis连接并获取详细信息
            if self.verify_manager.redis_client:
                try:
                    redis_info = self.verify_manager.redis_client.info()
                    status_info["redis_info"] = {
                        "connected_clients": redis_info.get("connected_clients", 0),
                        "used_memory": redis_info.get("used_memory_human", "unknown"),
                        "uptime_in_seconds": redis_info.get("uptime_in_seconds", 0),
                        "redis_version": redis_info.get("redis_version", "unknown"),
                        "used_memory_peak_human": redis_info.get("used_memory_peak_human", "unknown")
                    }

                    # 测试Redis基本操作
                    test_key = "admin:test:connection"
                    self.verify_manager.redis_client.setex(test_key, 1, "test")
                    test_result = self.verify_manager.redis_client.get(test_key)
                    status_info["redis_test"] = {
                        "read_write": test_result == b"test" if isinstance(test_result, bytes) else test_result == "test"
                    }
                    self.verify_manager.redis_client.delete(test_key)

                except Exception as redis_error:
                    status_info["redis_error"] = str(redis_error)
                    status_info["redis_test"] = {
                        "read_write": False,
                        "error": str(redis_error)
                    }

            return True, "系统状态获取成功", status_info

        except Exception as e:
            logger.error(f"获取系统状态失败: {str(e)}")
            return False, f"获取系统状态失败: {str(e)}", None


# 创建全局管理员测试服务实例
admin_test_service:AdminTestService = AdminTestService()