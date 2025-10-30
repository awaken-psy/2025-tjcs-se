"""
权限装饰器模块 - 提供声明式权限控制
"""
from functools import wraps
from typing import List, Callable, Optional
from app.models.core.user import Permission, BaseUser
from app.auth.permission_manager import PermissionManager, PermissionDeniedException


def require_permission(permission: Permission):
    """
    装饰器：要求用户拥有指定权限
    
    使用示例:
    @require_permission(Permission.CREATE_CAPSULE)
    def create_capsule_handler(user: BaseUser, ...):
        ...
    
    Args:
        permission: 所需权限
    
    Raises:
        PermissionDeniedException: 如果用户没有权限
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, user: BaseUser = None, **kwargs):
            if user is None:
                raise PermissionDeniedException("用户信息缺失")
            
            if not PermissionManager.check_permission(user, permission):
                raise PermissionDeniedException(
                    f"需要权限: {permission.value}"
                )
            
            return await func(*args, user=user, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, user: BaseUser = None, **kwargs):
            if user is None:
                raise PermissionDeniedException("用户信息缺失")
            
            if not PermissionManager.check_permission(user, permission):
                raise PermissionDeniedException(
                    f"需要权限: {permission.value}"
                )
            
            return func(*args, user=user, **kwargs)
        
        # 判断函数是否为异步
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def require_any_permission(*permissions: Permission):
    """
    装饰器：要求用户拥有任意一个指定权限
    
    使用示例:
    @require_any_permission(Permission.CREATE_CAPSULE, Permission.ADMIN)
    def create_capsule_handler(user: BaseUser, ...):
        ...
    
    Args:
        *permissions: 权限列表
    
    Raises:
        PermissionDeniedException: 如果用户没有任何权限
    """
    perms = set(permissions)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, user: BaseUser = None, **kwargs):
            if user is None:
                raise PermissionDeniedException("用户信息缺失")
            
            if not PermissionManager.check_any_permission(user, perms):
                raise PermissionDeniedException("缺少所需权限")
            
            return await func(*args, user=user, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, user: BaseUser = None, **kwargs):
            if user is None:
                raise PermissionDeniedException("用户信息缺失")
            
            if not PermissionManager.check_any_permission(user, perms):
                raise PermissionDeniedException("缺少所需权限")
            
            return func(*args, user=user, **kwargs)
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def require_all_permissions(*permissions: Permission):
    """
    装饰器：要求用户拥有所有指定权限
    
    使用示例:
    @require_all_permissions(Permission.UPDATE_USER, Permission.DELETE_USER)
    def admin_handler(user: BaseUser, ...):
        ...
    
    Args:
        *permissions: 权限列表
    
    Raises:
        PermissionDeniedException: 如果用户没有全部权限
    """
    perms = set(permissions)
    
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, user: BaseUser = None, **kwargs):
            if user is None:
                raise PermissionDeniedException("用户信息缺失")
            
            if not PermissionManager.check_all_permissions(user, perms):
                raise PermissionDeniedException("缺少所需权限")
            
            return await func(*args, user=user, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, user: BaseUser = None, **kwargs):
            if user is None:
                raise PermissionDeniedException("用户信息缺失")
            
            if not PermissionManager.check_all_permissions(user, perms):
                raise PermissionDeniedException("缺少所需权限")
            
            return func(*args, user=user, **kwargs)
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator


def require_admin():
    """
    装饰器：要求用户为管理员
    
    使用示例:
    @require_admin()
    def admin_handler(user: BaseUser, ...):
        ...
    
    Raises:
        PermissionDeniedException: 如果用户不是管理员
    """
    def decorator(func: Callable) -> Callable:
        @wraps(func)
        async def async_wrapper(*args, user: BaseUser = None, **kwargs):
            if user is None:
                raise PermissionDeniedException("用户信息缺失")
            
            if not PermissionManager.is_admin(user):
                raise PermissionDeniedException("需要管理员权限")
            
            return await func(*args, user=user, **kwargs)
        
        @wraps(func)
        def sync_wrapper(*args, user: BaseUser = None, **kwargs):
            if user is None:
                raise PermissionDeniedException("用户信息缺失")
            
            if not PermissionManager.is_admin(user):
                raise PermissionDeniedException("需要管理员权限")
            
            return func(*args, user=user, **kwargs)
        
        import asyncio
        if asyncio.iscoroutinefunction(func):
            return async_wrapper
        return sync_wrapper
    
    return decorator
