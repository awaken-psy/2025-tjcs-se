"""
用户登录管理服务
"""
from typing import Tuple, Optional
from sqlalchemy.orm import Session

from app.database import UserRepository
from app.auth.password import PasswordManager
from app.auth.jwt_handler import JWTHandler
from app.domain.user import UserRole, GuestUser, RegisteredUser, AdminUser, BaseUser


class LoginManager:
    """用户登录管理器"""

    def __init__(self):
        #这里可能会raise异常
        self.user_repository = UserRepository()

    def login_user(
        self,
        email_or_username: str,
        password: str
    ) -> Tuple[bool, str, Optional[dict]]:
        """
        用户登录

        Args:
            email_or_username: 邮箱或用户名
            password: 密码 (来自前端的SHA-256哈希值)

        Returns:
            (success, message, user_data): 是否成功、消息和用户数据
        """
        try:
            # 1. 根据邮箱或用户名查找用户
            user_domain = self.user_repository.get_user_by_email_or_username(email_or_username)
            if not user_domain:
                return False, "用户不存在或密码错误", None

            # 2. 检查用户是否激活
            if not user_domain.is_active:
                return False, "用户账户已被禁用或未激活", None

            # 3. 验证密码 (前端发送的是SHA-256哈希，需要用bcrypt验证)
            password_valid, password_message = PasswordManager.verify_password(password, user_domain.password_hash)
            if not password_valid:
                return False, "用户不存在或密码错误", None

            # 4. 更新最后登录时间
            self.user_repository.update_user_last_login(user_domain.user_id)

            # 5. 生成JWT令牌

            access_token = JWTHandler.generate_access_token_from_user(user_domain)
            refresh_token = JWTHandler.generate_refresh_token_from_user(user_domain)

            nickname = user_domain.nickname if isinstance(user_domain, RegisteredUser) else user_domain.username
            avatar_url = user_domain.avatar_url if isinstance(user_domain, RegisteredUser) else None
            # 6. 返回用户数据和令牌
            user_response_data = {
                "user_id": user_domain.user_id,
                "email": user_domain.email,
                "nickname": nickname,
                "token": access_token,
                "refresh_token": refresh_token,
                "avatar": avatar_url
            }

            return True, "登录成功", user_response_data

        except Exception as e:
            return False, f"登录失败: {str(e)}", None