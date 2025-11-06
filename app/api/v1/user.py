"""
认证和用户管理 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional, List
from pydantic import BaseModel, Field
from datetime import datetime
from auth.jwt_handler import JWTHandler, JWTConfig
from auth.dependencies import AuthenticationDependencies, PermissionChecker
from auth.permission_manager import PermissionManager
from models.core.user import Permission, UserRole, BaseUser
from services.user_service import UserService

class TokenResponse(BaseModel):
    """Token 响应模型"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = "bearer"
    expires_in: int  # 过期秒数

class UserInfoResponse(BaseModel):
    """用户信息响应"""
    # 通用信息
    user_id: str = Field(..., description="用户 ID")
    username: str = Field(..., description="用户名")
    role: UserRole = Field(..., description="用户角色")

    # 认证用户信息
    last_login: Optional[datetime] = Field(None, description="上次登录时间")
    email: Optional[str] = Field(None, description="邮箱")
    department: Optional[str] = Field(None, description="部门")

    # 管理员信息
    admin_level: Optional[int] = Field(None, description="管理员级别")

    @staticmethod
    def from_user(user: BaseUser):
        """从 BaseUser 对象构造 UserInfoResponse 对象"""
        return UserInfoResponse(
            user_id=user.user_id,
            username=user.username,
            role=user.role,
            email=getattr(user, 'email', None),
            department=getattr(user, 'department', None),
            last_login=getattr(user, 'last_login', None),
            admin_level=getattr(user, 'admin_level', None)
        )

# 创建路由器
router = APIRouter(prefix="/user", tags=["user"])

@router.get(
    "/me",
    response_model=UserInfoResponse,
    summary="获取当前用户信息",
    description="获取已登录用户的详细信息"
)
async def get_current_user_info(
    user: BaseUser = Depends(AuthenticationDependencies.get_current_user)
):
    """
    获取当前用户信息
    
    需要提供有效的 Bearer Token
    
    示例:
    GET /api/v1/auth/me
    Headers:
        Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGc...
    """
    permissions = [p.value for p in user.permissions]
    
    response_data = {
        "user_id": user.user_id,
        "username": user.username,
        "role": user.role.value,
        "permissions": permissions,
    }
    
    # 如果是认证用户，添加额外信息
    if hasattr(user, 'email'):
        response_data["email"] = user.email
    if hasattr(user, 'department'):
        response_data["department"] = user.department
    
    return UserInfoResponse(**response_data)


@router.get(
    "/permissions",
    summary="获取当前用户权限列表",
    description="获取已登录用户拥有的所有权限"
)
async def get_user_permissions(
    user: BaseUser = Depends(AuthenticationDependencies.get_current_user)
):
    """
    获取用户权限列表
    
    返回用户拥有的所有权限
    """
    permissions = [p.value for p in user.permissions]
    
    return {
        "user_id": user.user_id,
        "role": user.role.value,
        "permissions": permissions,
        "permission_count": len(permissions)
    }


@router.post(
    "/check-permission",
    summary="检查用户权限",
    description="检查当前用户是否拥有指定权限"
)
async def check_permission(
    required_permission: str,
    user: BaseUser = Depends(AuthenticationDependencies.get_current_user)
):
    """
    检查权限
    
    Args:
        required_permission: 要检查的权限字符串，如 "create:capsule"
    
    返回权限检查结果
    """
    try:
        permission = Permission(required_permission)
        has_perm = PermissionManager.check_permission(user, permission)
        
        return {
            "user_id": user.user_id,
            "permission": required_permission,
            "has_permission": has_perm
        }
    except ValueError:
        raise HTTPException(
            status_code=400,
            detail=f"无效的权限: {required_permission}"
        )


@router.get(
    "/users",
    summary="获取用户列表（仅管理员）",
    description="获取系统中的所有用户列表"
)
async def list_users(
    user: BaseUser = Depends(
        PermissionChecker.require_permission(Permission.READ_USER)
    )
):
    """
    获取用户列表
    
    需要 READ_USER 权限
    """
    users = UserService.list_all_users()
    
    result = []
    for u in users:
        result.append({
            "user_id": u.user_id,
            "username": u.username,
            "role": u.role.value,
            "permissions": [p.value for p in u.permissions]
        })
    
    return {
        "total": len(result),
        "users": result
    }


@router.get(
    "/test-users",
    summary="获取测试用户信息",
    description="获取系统中预配置的测试用户列表"
)
async def get_test_users():
    """
    获取测试用户
    
    用于开发测试的测试用户列表
    """
    test_users = [
        {
            "user_id": "user_001",
            "username": "张三",
            "role": "user",
            "email": "zhangsan@university.edu",
            "department": "计算机学院",
            "student_id": "2021010001",
            "description": "普通认证用户示例"
        },
        {
            "user_id": "user_002",
            "username": "李四",
            "role": "user",
            "email": "lisi@university.edu",
            "department": "数学学院",
            "student_id": "2021010002",
            "description": "普通认证用户示例"
        },
        {
            "user_id": "admin_001",
            "username": "管理员",
            "role": "admin",
            "admin_level": 1,
            "description": "系统管理员示例"
        }
    ]
    
    return {
        "total": len(test_users),
        "test_users": test_users,
        "note": "这些是预配置的测试用户，可直接用于演示和开发"
    }

