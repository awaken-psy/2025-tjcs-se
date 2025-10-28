"""
认证中间件 - FastAPI 依赖注入和中间件
"""
from typing import Optional
from fastapi import Depends, HTTPException, Header
from auth.jwt_handler import JWTHandler
from auth.permission_manager import PermissionManager, UnauthorizedException, PermissionDeniedException
from models.core.user import (
    BaseUser, AccessUser, AuthenticatedUser, AdminUser, 
    UserRole, Permission, UserFactory
)


class AuthenticationDependencies:
    """认证依赖注入类 - 为 FastAPI 路由提供依赖"""
    
    @staticmethod
    async def get_current_user(
        authorization: Optional[str] = Header(None)
    ) -> BaseUser:
        """
        获取当前用户
        
        从请求头中提取 JWT token 并验证，返回用户对象
        如果没有 token，返回访客用户
        
        Args:
            authorization: HTTP Authorization 请求头
        
        Returns:
            用户对象
        
        Raises:
            HTTPException: 如果 token 无效
        """
        if not authorization:
            # 没有 token，返回访客用户
            return UserFactory.create_guest_user()
        
        # 从 "Bearer <token>" 中提取 token
        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                return UserFactory.create_guest_user()
        except ValueError:
            return UserFactory.create_guest_user()
        
        # 验证 token
        valid, payload = JWTHandler.verify_access_token(token)
        if not valid:
            raise HTTPException(
                status_code=401,
                detail=payload.get("error", "Token验证失败")
            )
        
        # 根据角色创建对应的用户对象
        user_id = payload.get("sub")
        username = payload.get("username")
        role = UserRole(payload.get("role", "user"))
        permissions = [Permission(p) for p in payload.get("permissions", [])]
        
        if role == UserRole.ADMIN:
            return AdminUser(
                user_id=user_id,
                username=username,
                permissions=set(permissions)
            )
        else:
            return AuthenticatedUser(
                user_id=user_id,
                username=username,
                permissions=set(permissions)
            )
    
    @staticmethod
    async def get_authenticated_user(
        user: BaseUser = Depends(lambda: AuthenticationDependencies.get_current_user())
    ) -> AuthenticatedUser:
        """
        获取已认证的用户（必须已登录）
        
        如果用户是访客，抛出 401 异常
        
        Args:
            user: 当前用户
        
        Returns:
            认证用户对象
        
        Raises:
            HTTPException: 如果用户未登录
        """
        if user.role == UserRole.GUEST:
            raise HTTPException(
                status_code=401,
                detail="需要登录"
            )
        return user
    
    @staticmethod
    async def get_admin_user(
        user: BaseUser = Depends(lambda: AuthenticationDependencies.get_authenticated_user())
    ) -> AdminUser:
        """
        获取管理员用户（必须是管理员）
        
        Args:
            user: 当前用户
        
        Returns:
            管理员用户对象
        
        Raises:
            HTTPException: 如果用户不是管理员
        """
        if user.role != UserRole.ADMIN:
            raise HTTPException(
                status_code=403,
                detail="需要管理员权限"
            )
        return user


class PermissionChecker:
    """权限检查器 - 创建权限检查依赖"""
    
    @staticmethod
    def require_permission(permission: Permission):
        """
        创建需要特定权限的依赖
        
        Args:
            permission: 所需权限
        
        Returns:
            依赖函数
        """
        async def check_permission(
            user: BaseUser = Depends(AuthenticationDependencies.get_current_user)
        ) -> BaseUser:
            if not PermissionManager.check_permission(user, permission):
                raise HTTPException(
                    status_code=403,
                    detail=f"缺少权限: {permission.value}"
                )
            return user
        
        return check_permission
    
    @staticmethod
    def require_any_permission(*permissions: Permission):
        """
        创建需要任意一个权限的依赖
        
        Args:
            *permissions: 权限列表
        
        Returns:
            依赖函数
        """
        perms = set(permissions)
        
        async def check_permission(
            user: BaseUser = Depends(AuthenticationDependencies.get_current_user)
        ) -> BaseUser:
            if not PermissionManager.check_any_permission(user, perms):
                raise HTTPException(
                    status_code=403,
                    detail="缺少所需权限"
                )
            return user
        
        return check_permission
    
    @staticmethod
    def require_all_permissions(*permissions: Permission):
        """
        创建需要所有权限的依赖
        
        Args:
            *permissions: 权限列表
        
        Returns:
            依赖函数
        """
        perms = set(permissions)
        
        async def check_permission(
            user: BaseUser = Depends(AuthenticationDependencies.get_current_user)
        ) -> BaseUser:
            if not PermissionManager.check_all_permissions(user, perms):
                raise HTTPException(
                    status_code=403,
                    detail="缺少所需权限"
                )
            return user
        
        return check_permission


def create_bearer_auth_middleware():
    """
    创建 Bearer Token 认证中间件
    
    Returns:
        中间件函数
    """
    async def auth_middleware(request, call_next):
        """中间件实现"""
        # 在这里可以添加全局的认证逻辑
        response = await call_next(request)
        return response
    
    return auth_middleware
