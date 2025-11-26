"""
用户数据模型 - 定义用户角色、权限和用户实体
"""
from enum import Enum
from typing import Set, List, Optional, Union
# from pydantic import BaseModel, Field
from dataclasses import dataclass, field
from datetime import datetime


class UserRole(str, Enum):
    """用户角色枚举"""
    GUEST = "guest"  # 访客（未登录用户）
    USER = "user"  # 普通用户（已认证用户）
    ADMIN = "admin"  # 管理员

class UserType(str, Enum):
    """用户类型枚举"""
    STUDENT = "student"  # 学生
    TEACHER = "teacher"  # 教师
    OTHER = "other"  # 其他


class Permission(str, Enum):
    """权限枚举 - 系统权限定义"""
    # 胶囊操作权限
    CREATE_CAPSULE = "create:capsule"
    READ_CAPSULE = "read:capsule"
    UPDATE_CAPSULE = "update:capsule"
    DELETE_CAPSULE = "delete:capsule"
    
    # 解锁权限
    UNLOCK_CAPSULE = "unlock:capsule"
    
    # 用户管理权限
    CREATE_USER = "create:user"
    READ_USER = "read:user"
    UPDATE_USER = "update:user"
    DELETE_USER = "delete:user"
    
    # 内容审核权限
    MODERATE_CONTENT = "moderate:content"
    REVIEW_COMMENTS = "review:comments"
    
    # 系统管理权限
    MANAGE_PERMISSIONS = "manage:permissions"
    VIEW_ANALYTICS = "view:analytics"


class RolePermissionMap:
    """角色-权限映射表 - 定义各角色的权限"""
    
    # 访客权限：只能浏览公开内容
    GUEST_PERMISSIONS: Set[Permission] = {
        Permission.READ_CAPSULE,
    }
    
    # 普通用户权限：可以创建、编辑自己的胶囊，浏览可见内容
    USER_PERMISSIONS: Set[Permission] = {
        Permission.CREATE_CAPSULE,
        Permission.READ_CAPSULE,
        Permission.UPDATE_CAPSULE,  # 仅限自己的胶囊
        Permission.DELETE_CAPSULE,  # 仅限自己的胶囊
        Permission.UNLOCK_CAPSULE,
    }
    
    # 管理员权限：完全控制
    ADMIN_PERMISSIONS: Set[Permission] = {
        Permission.CREATE_CAPSULE,
        Permission.READ_CAPSULE,
        Permission.UPDATE_CAPSULE,
        Permission.DELETE_CAPSULE,
        Permission.UNLOCK_CAPSULE,
        Permission.CREATE_USER,
        Permission.READ_USER,
        Permission.UPDATE_USER,
        Permission.DELETE_USER,
        Permission.MODERATE_CONTENT,
        Permission.REVIEW_COMMENTS,
        Permission.MANAGE_PERMISSIONS,
        Permission.VIEW_ANALYTICS,
    }
    
    @staticmethod
    def get_role_permissions(role: UserRole) -> Set[Permission]:
        """获取角色对应的权限集合"""
        if role == UserRole.GUEST:
            return RolePermissionMap.GUEST_PERMISSIONS.copy()
        elif role == UserRole.USER:
            return RolePermissionMap.USER_PERMISSIONS.copy()
        elif role == UserRole.ADMIN:
            return RolePermissionMap.ADMIN_PERMISSIONS.copy()
        return set()

@dataclass
class BaseUser:
    """用户基类 - 定义所有用户共有的属性"""
    user_id: int  # 用户ID，唯一标识
    username: str  # 用户名
    role: UserRole  # 用户角色

    permissions: Set[Permission] = field(default_factory=set)  # 用户权限集合
    created_at: datetime = field(default_factory=datetime.now) # 创建时间
    
    def has_permission(self, permission: Permission) -> bool:
        """检查用户是否拥有指定权限"""
        return permission in self.permissions
    
    def has_any_permission(self, permissions: Set[Permission]) -> bool:
        """检查用户是否拥有任何一个指定权限"""
        return bool(self.permissions & permissions)
    
    def has_all_permissions(self, permissions: Set[Permission]) -> bool:
        """检查用户是否拥有全部指定权限"""
        return permissions.issubset(self.permissions)


@dataclass
class GuestUser(BaseUser):
    """访客用户 - 未登录用户，仅有只读权限"""
    
    def __post_init__(self):
        """初始化时自动设置权限"""
        if not self.permissions:
            self.permissions = RolePermissionMap.get_role_permissions(UserRole.GUEST)
        self.role = UserRole.GUEST


@dataclass
class RegisteredUser(BaseUser):
    """已注册用户，有创建和管理自己内容的权限"""
    is_active: bool = True  # 是否激活
    email: Optional[str] = None  # 邮箱
    nickname: Optional[str] = None  # 昵称
    password_hash: Optional[str] = None  # 密码哈希值

    user_type: Optional[UserType] = None  # 用户类型
    is_verified: bool = True  # 是否已验证邮箱
    is_active: bool = True  # 是否激活(当被封禁或注销时，该字段为False)
    
    avatar_url: Optional[str] = None  # 头像URL
    bio: Optional[str] = None  # 个人简介
    campus_id: Optional[str] = None  # 校园id或学号

    last_login: Optional[datetime] = None  # 最后登录时间
    
    def __post_init__(self):
        """初始化时自动设置权限"""
        if not self.permissions:
            self.permissions = RolePermissionMap.get_role_permissions(UserRole.USER)
        self.role = UserRole.USER
    
    def can_edit_capsule(self, capsule_owner_id: str) -> bool:
        """检查是否可以编辑指定的胶囊（仅限所有者）"""
        return (self.has_permission(Permission.UPDATE_CAPSULE) and 
                self.user_id == capsule_owner_id)
    
    def can_delete_capsule(self, capsule_owner_id: str) -> bool:
        """检查是否可以删除指定的胶囊（仅限所有者）"""
        return (self.has_permission(Permission.DELETE_CAPSULE) and 
                self.user_id == capsule_owner_id)


@dataclass
class AdminUser(BaseUser):
    """管理员用户 - 拥有完全权限"""
    email: Optional[str] = None  # 邮箱
    password_hash: Optional[str] = None  # 密码哈希值
    last_login: Optional[datetime] = None  # 最后登录时间
    admin_level: int = 1  # 管理员级别（1-普通管理员，0-超级管理员）
    is_active:bool = True # 是否激活
    
    def __post_init__(self):
        """初始化时自动设置权限"""
        if not self.permissions:
            self.permissions = RolePermissionMap.get_role_permissions(UserRole.ADMIN)
        self.role = UserRole.ADMIN
    
    def can_edit_user(self, target_user_id: str) -> bool:
        """检查是否可以编辑用户"""
        return self.has_permission(Permission.UPDATE_USER)
    
    def can_delete_user(self, target_user_id: str) -> bool:
        """检查是否可以删除用户"""
        return self.has_permission(Permission.DELETE_USER)
    
    def can_moderate_content(self) -> bool:
        """检查是否可以审核内容"""
        return self.has_permission(Permission.MODERATE_CONTENT)


AuthorizedUser = Union[RegisteredUser, AdminUser]  # 已认证用户类型别名

class UserFactory:
    """用户工厂类 - 创建不同类型的用户对象"""
    
    @staticmethod
    def create_guest_user(user_id: int = -1) -> GuestUser:
        """创建访客用户"""
        return GuestUser(
            user_id=user_id,
            username="访客",
            role=UserRole.GUEST
        )
    
    @staticmethod
    def create_registered_user(
        user_id: int,
        username: str,
        email: Optional[str] = None,
        nickname: Optional[str] = None,
        password_hash: Optional[str] = None,

        user_type: Optional[UserType] = None,
        is_active: bool = True,
        is_verified: bool = True,

        avatar_url: Optional[str] = None,
        campus_id: Optional[str] = None,
        bio: Optional[str] = None,
        last_login: Optional[datetime] = None
    ) -> RegisteredUser:
        """创建认证用户"""
        return RegisteredUser(
            user_id=user_id,
            username=username,
            email=email,
            nickname=nickname,
            password_hash=password_hash,

            user_type=user_type,
            is_active=is_active,
            is_verified=is_verified,

            avatar_url=avatar_url,
            campus_id=campus_id,
            bio=bio,

            role=UserRole.USER,
            last_login=last_login
        )
    
    @staticmethod
    def create_admin_user(
        user_id: int,
        username: str,
        email: Optional[str] = None,

        password_hash: Optional[str] = None,
        admin_level: int = 1,
        is_active: bool = True,
    ) -> AdminUser:
        """创建管理员用户"""
        return AdminUser(
            user_id=user_id,
            username=username,
            email=email,
            password_hash=password_hash,
            admin_level=admin_level,
            role=UserRole.ADMIN,
            is_active=is_active
        )
