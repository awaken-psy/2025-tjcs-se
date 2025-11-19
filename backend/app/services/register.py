"""
用户注册管理服务
"""
from typing import Tuple, Optional
from sqlalchemy.orm import Session

from app.database import UserRepository
from app.auth.password import PasswordManager
from app.auth.jwt_handler import JWTHandler
from app.services.verifycode import verify_code_manager
from app.domain.user import AuthorizedUser, AdminUser


class RegisterManager:
    """用户注册管理器"""

    def __init__(self):
        # 这里可能会raise异常
        self.user_repository = UserRepository()

    def register_user(
        self,
        email: str,
        password: str,
        nickname: str,
        verify_code: str,
        campus_id: Optional[str] = None,
    ) -> Tuple[bool, str, Optional[dict]]:
        """
        注册新用户

        Args:
            email: 邮箱
            password: 密码
            nickname: 昵称
            campus_id: 学号（可选）
            verify_code: 验证码

        Returns:
            (success, message, user_data): 是否成功、消息和用户数据
        """

        try:
            # 1. 验证验证码
            verify_success, verify_message = verify_code_manager.verify_code(email, verify_code)
            if not verify_success:
                return False, verify_message, None

            # 2. 验证密码强度(可选)
            # password_valid, password_message = password_manager.validate_password_strength(password)
            # if not password_valid:
            #     return False, password_message, None

            # 3. 检查邮箱是否已存在
            existing_user = self.user_repository.get_user_by_email_or_username(email)
            if existing_user:
                return False, "该邮箱或用户名已被注册", None

            # 4. 检查学号是否已存在（如果提供）
            if campus_id:
                existing_student = self.user_repository.get_user_by_student_id(campus_id)
                if existing_student:
                    return False, "该id已被注册", None

            # 5. 对密码进行哈希处理
            hash_success, hashed_password = PasswordManager.hash_password(password)
            if not hash_success:
                return False, hashed_password, None

            # 6. 创建用户
            try:
                new_user = self.user_repository.create_user(
                    username=nickname,
                    email=email,
                    password_hash=hashed_password,
                    nickname=nickname,
                    campus_id=campus_id,
                    user_type="student",
                    userrole="user"
                )

                if isinstance(new_user, AdminUser):
                    raise ValueError("无法注册管理员用户")
            except Exception as e:
                return False, f"用户创建失败: {str(e)}", None

            # 8. 生成JWT令牌
            access_token = JWTHandler.generate_access_token_from_user(new_user)
            refresh_token = JWTHandler.generate_refresh_token_from_user(new_user)

            # 9. 返回用户数据和令牌
            user_response_data = {
                "user_id": new_user.user_id,
                "email": new_user.email,
                "nickname": new_user.nickname,
                "token": access_token,
                "refresh_token": refresh_token,
                "avatar": new_user.avatar_url
            }

            return True, "注册成功", user_response_data

        except Exception as e:
            return False, f"注册失败: {str(e)}", None

    def check_email_availability(self, email: str) -> Tuple[bool, str]:
        """
        检查邮箱是否可用

        Args:
            email: 邮箱地址

        Returns:
            (is_available, message): 是否可用和相关信息
        """
        try:
            existing_user = self.user_repository.get_user_by_email_or_username(email)

            if existing_user:
                return False, "该邮箱或用户名已被注册"
            else:
                return True, "邮箱可用"
        except Exception as e:
            return False, f"检查邮箱可用性失败: {str(e)}"

    def check_student_id_availability(self, student_id: str) -> Tuple[bool, str]:
        """
        检查学号是否可用

        Args:
            student_id: 学号

        Returns:
            (is_available, message): 是否可用和相关信息
        """
        try:
            existing_user = self.user_repository.get_user_by_student_id(student_id)

            if existing_user:
                return False, "该学号已被注册"
            else:
                return True, "学号可用"
        except Exception as e:
            return False, f"检查学号可用性失败: {str(e)}"