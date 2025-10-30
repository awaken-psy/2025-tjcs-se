"""
权限管理模块 - 定义权限检查和验证逻辑
"""
from typing import Set, Callable, Optional
from app.models.core.user import Permission, BaseUser, UserRole


class PermissionManager:
    """权限管理器 - 处理权限相关的操作"""
    
    @staticmethod
    def check_permission(user: BaseUser, permission: Permission) -> bool:
        """
        检查用户是否拥有指定权限
        
        Args:
            user: 用户对象
            permission: 所需权限
        
        Returns:
            是否拥有权限
        """
        return user.has_permission(permission)
    
    @staticmethod
    def check_any_permission(user: BaseUser, permissions: Set[Permission]) -> bool:
        """
        检查用户是否拥有任何一个指定权限
        
        Args:
            user: 用户对象
            permissions: 权限集合
        
        Returns:
            是否拥有任何权限
        """
        return user.has_any_permission(permissions)
    
    @staticmethod
    def check_all_permissions(user: BaseUser, permissions: Set[Permission]) -> bool:
        """
        检查用户是否拥有全部指定权限
        
        Args:
            user: 用户对象
            permissions: 权限集合
        
        Returns:
            是否拥有全部权限
        """
        return user.has_all_permissions(permissions)
    
    @staticmethod
    def can_create_capsule(user: BaseUser) -> bool:
        """检查用户是否可以创建胶囊"""
        return user.has_permission(Permission.CREATE_CAPSULE)
    
    @staticmethod
    def can_read_capsule(user: BaseUser) -> bool:
        """检查用户是否可以读取胶囊"""
        return user.has_permission(Permission.READ_CAPSULE)
    
    @staticmethod
    def can_update_capsule(user: BaseUser, capsule_owner_id: str) -> bool:
        """
        检查用户是否可以更新胶囊
        
        Args:
            user: 用户对象
            capsule_owner_id: 胶囊所有者ID
        
        Returns:
            是否可以更新
        """
        # 管理员可以更新任何胶囊
        if user.role == UserRole.ADMIN:
            return user.has_permission(Permission.UPDATE_CAPSULE)
        
        # 普通用户只能更新自己的胶囊
        return (user.has_permission(Permission.UPDATE_CAPSULE) and 
                user.user_id == capsule_owner_id)
    
    @staticmethod
    def can_delete_capsule(user: BaseUser, capsule_owner_id: str) -> bool:
        """
        检查用户是否可以删除胶囊
        
        Args:
            user: 用户对象
            capsule_owner_id: 胶囊所有者ID
        
        Returns:
            是否可以删除
        """
        # 管理员可以删除任何胶囊
        if user.role == UserRole.ADMIN:
            return user.has_permission(Permission.DELETE_CAPSULE)
        
        # 普通用户只能删除自己的胶囊
        return (user.has_permission(Permission.DELETE_CAPSULE) and 
                user.user_id == capsule_owner_id)
    
    @staticmethod
    def can_unlock_capsule(user: BaseUser) -> bool:
        """检查用户是否可以解锁胶囊"""
        return user.has_permission(Permission.UNLOCK_CAPSULE)
    
    @staticmethod
    def can_moderate_content(user: BaseUser) -> bool:
        """检查用户是否可以审核内容"""
        return user.has_permission(Permission.MODERATE_CONTENT)
    
    @staticmethod
    def is_admin(user: BaseUser) -> bool:
        """检查用户是否为管理员"""
        return user.role == UserRole.ADMIN


class PermissionDeniedException(Exception):
    """权限被拒绝异常"""
    def __init__(self, message: str = "权限被拒绝", code: str = "PERMISSION_DENIED"):
        self.message = message
        self.code = code
        super().__init__(self.message)


class UnauthorizedException(Exception):
    """未授权异常"""
    def __init__(self, message: str = "未授权，请登录", code: str = "UNAUTHORIZED"):
        self.message = message
        self.code = code
        super().__init__(self.message)
