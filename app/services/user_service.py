"""
用户服务模块 - 处理用户相关的业务逻辑（临时 mock 实现）
"""
from typing import Optional, Dict
from models.core.user import (
    BaseUser, AuthenticatedUser, AdminUser, AccessUser,
    UserRole, UserFactory, Permission
)


class UserService:
    """用户服务 - 管理用户数据"""
    
    # 临时用户存储（实际应该从数据库查询）
    _users: Dict[str, BaseUser] = {}
    
    # 初始化默认用户
    @staticmethod
    def init_default_users():
        """初始化默认用户供测试使用"""
        # 创建测试用户
        user1 = UserFactory.create_authenticated_user(
            user_id="user_001",
            username="张三",
            email="zhangsan@university.edu",
            department="计算机学院",
            student_id="2021010001"
        )
        
        user2 = UserFactory.create_authenticated_user(
            user_id="user_002",
            username="李四",
            email="lisi@university.edu",
            department="数学学院",
            student_id="2021010002"
        )
        
        # 创建管理员用户
        admin = UserFactory.create_admin_user(
            user_id="admin_001",
            username="管理员",
            admin_level=1
        )
        
        UserService._users = {
            "user_001": user1,
            "user_002": user2,
            "admin_001": admin,
        }
    
    @staticmethod
    def get_user_by_id(user_id: str) -> Optional[BaseUser]:
        """
        通过ID获取用户
        
        Args:
            user_id: 用户ID
        
        Returns:
            用户对象，或 None 如果不存在
        """
        return UserService._users.get(user_id)
    
    @staticmethod
    def get_user_by_username(username: str) -> Optional[BaseUser]:
        """
        通过用户名获取用户
        
        Args:
            username: 用户名
        
        Returns:
            用户对象，或 None 如果不存在
        """
        for user in UserService._users.values():
            if user.username == username:
                return user
        return None
    
    @staticmethod
    def create_user(
        user_id: str,
        username: str,
        role: UserRole = UserRole.USER,
        **kwargs
    ) -> BaseUser:
        """
        创建新用户
        
        Args:
            user_id: 用户ID
            username: 用户名
            role: 用户角色
            **kwargs: 其他用户属性
        
        Returns:
            创建的用户对象
        """
        if role == UserRole.ADMIN:
            user = UserFactory.create_admin_user(user_id, username)
        else:
            user = UserFactory.create_authenticated_user(user_id, username, **kwargs)
        
        UserService._users[user_id] = user
        return user
    
    @staticmethod
    def get_guest_user() -> AccessUser:
        """获取访客用户"""
        return UserFactory.create_guest_user()
    
    @staticmethod
    def list_all_users() -> list:
        """获取所有用户列表"""
        return list(UserService._users.values())
    
    @staticmethod
    def delete_user(user_id: str) -> bool:
        """
        删除用户
        
        Args:
            user_id: 用户ID
        
        Returns:
            是否删除成功
        """
        if user_id in UserService._users:
            del UserService._users[user_id]
            return True
        return False


# 初始化默认用户
UserService.init_default_users()
