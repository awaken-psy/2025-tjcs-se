"""
用户注册管理服务
"""
import os
from typing import Tuple, Optional
from sqlalchemy.orm import Session

from app.database import UserRepository
from app.auth.password import PasswordManager
from app.auth.jwt_handler import JWTHandler
# 🔴 关键：从全局导入使用 Redis 初始化的管理器实例
from app.services.verifycode import verify_code_manager 
from app.domain.user import AuthorizedUser, RegisteredUser, AdminUser, UserRole
from app.services.user_service import UserService
from app.logger import get_logger


class RegisterManager:
    """用户注册管理器"""
    logger = get_logger("register_manager")

    admin_user_added = False
    init_admin_user:Optional[AdminUser] = None

    def __init__(self,db:Optional[Session]=None):
        # 这里可能会raise异常
        self.user_repository = UserRepository(db)

    def add_user(
        self,
        username: str,
        email: str,
        password: str,
        user_role: UserRole,
        campus_id: Optional[str] = None,
    ) -> Tuple[bool, str, Optional[AuthorizedUser]]:
        """
        添加新用户

        Args:
            username: 用户名
            email: 邮箱
            password: 密码
            user_role: 用户角色
            campus_id: 学号（可选）

        Returns:
            (success, message, user_data): 是否成功、消息和用户数据
        """
        # 1. 检查用户名是否已存在
        existing_user = self.user_repository.get_user_by_username(username)
        if existing_user:
            return False, "用户名已存在", None

        # 2. 检查邮箱是否已存在
        existing_user = self.user_repository.get_user_by_email(email)
        if existing_user:
            return False, "邮箱已存在", None
        
        # 3. 检查学号是否已存在（如果提供）
        if campus_id:
            existing_student = self.user_repository.get_user_by_student_id(campus_id)
            if existing_student:
                return False, "学号已存在", None
            
        # 4. 对密码进行哈希处理
        hash_success, hashed_password = PasswordManager.hash_password(password)

        if not hash_success:
            return False, "密码哈希失败", None

        # 5. 创建用户
        try:
            new_user = self.user_repository.create_user(
                username=username,
                nickname=username,
                email=email,
                password_hash=hashed_password,
                user_type="student",
                userrole=user_role,
                campus_id=campus_id,
            )

            return True, "用户创建成功", new_user
        except Exception as e:
            return False, "创建用户失败", None

    @classmethod        
    def add_init_admin_user(cls) -> Optional[AdminUser]:
        # 创建一个初始管理员账号（如果不存在）
        user_service = UserService()
        register_mannager = RegisterManager()

        admin_user = user_service.get_user_by_email(os.getenv("INIT_ADMIN_EMAIL", "admin@example.com"))
        if not admin_user:
            cls.logger.info("No admin user found, creating one...")
            success, message, admin_user = register_mannager.add_user(
                username = os.getenv("INIT_ADMIN_USERNAME", "admin_user"),
                user_role = UserRole.ADMIN,
                email = os.getenv("INIT_ADMIN_EMAIL", "admin@example.com"),
                password = os.getenv("INIT_ADMIN_PASSWORD", "123456"),
            )
            if success:
                cls.logger.info("Admin user created successfully.")
            else:
                cls.logger.error(f"Failed to create admin user: {message}")

        if admin_user:
            cls.logger.info(f"Initial admin user id:{admin_user.user_id}, email:{admin_user.email}")
            if not isinstance(admin_user, AdminUser):
                cls.logger.warning("Initial admin user is not an admin user.")
                return None
        return admin_user
        
    

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
            # 🔴 (已确认正确): 调用全局 Redis 实例进行验证，验证成功后 Redis 会自动删除验证码。
            verify_success, verify_message = verify_code_manager.verify_code(email, verify_code)
            if not verify_success:
                return False, verify_message, None

            # 2. 验证密码强度(可选)
            # password_valid, password_message = password_manager.validate_password_strength(password)
            # if not password_valid:
            #     return False, password_message, None

            success, message, new_user = self.add_user(
                username=email,
                email=email,
                password=password,
                user_role=UserRole.USER,
                campus_id=campus_id,
            )

            if not success or not new_user:
                return False, message, None

            # 8. 生成JWT令牌
            access_token = JWTHandler.generate_access_token_from_user(new_user)
            refresh_token = JWTHandler.generate_refresh_token_from_user(new_user)

            # 9. 返回用户数据和令牌
            user_response_data = {
                "user_id": new_user.user_id,
                "email": new_user.email,
                "nickname": nickname,
                "token": access_token,
                "refresh_token": refresh_token,
                "avatar": new_user.avatar_url if isinstance(new_user, RegisteredUser) else None,
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