"""
密码哈希和验证工具
"""
import bcrypt
from typing import Tuple


class PasswordManager:
    """密码管理器"""

    @staticmethod
    def hash_password(password: str) -> Tuple[bool, str]:
        """
        对密码进行哈希处理

        Args:
            password: 原始密码

        Returns:
            (success, hashed_password): 是否成功和哈希后的密码
        """
        try:
            # 生成盐值并哈希密码
            salt = bcrypt.gensalt()
            hashed_password = bcrypt.hashpw(password.encode('utf-8'), salt)
            return True, hashed_password.decode('utf-8')
        except Exception as e:
            return False, f"密码哈希失败: {str(e)}"

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> Tuple[bool, str]:
        """
        验证密码是否正确

        Args:
            password: 原始密码
            hashed_password: 哈希后的密码

        Returns:
            (success, message): 是否验证成功和相关信息
        """
        try:
            # 验证密码
            is_valid = bcrypt.checkpw(
                password.encode('utf-8'),
                hashed_password.encode('utf-8')
            )

            if is_valid:
                return True, "密码验证成功"
            else:
                return False, "密码错误"
        except Exception as e:
            return False, f"密码验证失败: {str(e)}"

    @staticmethod
    def validate_password_strength(password: str) -> Tuple[bool, str]:
        """
        验证密码强度

        Args:
            password: 密码

        Returns:
            (is_valid, message): 是否有效和验证信息
        """
        if len(password) < 8:
            return False, "密码长度至少需要8位"

        if len(password) > 128:
            return False, "密码长度不能超过128位"

        # 检查是否包含数字
        if not any(char.isdigit() for char in password):
            return False, "密码必须包含至少一个数字"

        # 检查是否包含字母
        if not any(char.isalpha() for char in password):
            return False, "密码必须包含至少一个字母"

        return True, "密码强度符合要求"

