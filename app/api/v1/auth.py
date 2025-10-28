"""
认证和用户管理 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import Optional
from pydantic import BaseModel
from datetime import datetime
from auth.jwt_handler import JWTHandler, JWTConfig
from auth.dependencies import AuthenticationDependencies, PermissionChecker
from auth.permission_manager import PermissionManager
from models.core.user import Permission, UserRole, BaseUser
from services.user_service import UserService


# 请求和响应模型
class TokenRequest(BaseModel):
    """Token 请求模型"""
    username: str  # 用户名
    password: str  # 密码（演示用，实际应验证）


class TokenResponse(BaseModel):
    """Token 响应模型"""
    access_token: str
    refresh_token: str
    token_type: str = "bearer"
    expires_in: int  # 过期秒数


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str


class UserInfoResponse(BaseModel):
    """用户信息响应"""
    user_id: str
    username: str
    role: str
    permissions: list
    email: Optional[str] = None
    department: Optional[str] = None


# 创建路由器
router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post(
    "/login",
    response_model=TokenResponse,
    summary="用户登录",
    description="使用用户名和密码登录，获取 JWT Token"
)
async def login(request: TokenRequest):
    """
    用户登录接口
    
    示例:
    POST /api/v1/auth/login
    {
        "username": "张三",
        "password": "password123"
    }
    """
    # TODO: 实现实际的密码验证逻辑
    # 这里临时使用 UserService 中的测试用户
    
    user = UserService.get_user_by_username(request.username)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="用户名或密码错误"
        )
    
    # 生成 Token
    permissions = [p.value for p in user.permissions]
    access_token = JWTHandler.generate_access_token(
        user_id=user.user_id,
        username=user.username,
        role=user.role,
        permissions=permissions
    )
    
    refresh_token = JWTHandler.generate_refresh_token(
        user_id=user.user_id,
        username=user.username
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=JWTConfig.ACCESS_TOKEN_EXPIRE_HOURS * 3600
    )


@router.post(
    "/refresh",
    response_model=TokenResponse,
    summary="刷新访问令牌",
    description="使用刷新令牌获取新的访问令牌"
)
async def refresh_token(request: RefreshTokenRequest):
    """
    刷新 Token 接口
    
    示例:
    POST /api/v1/auth/refresh
    {
        "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGc..."
    }
    """
    success, new_token, error = JWTHandler.refresh_access_token(request.refresh_token)
    
    if not success:
        raise HTTPException(
            status_code=401,
            detail=error or "刷新失败"
        )
    
    # 解码新 token 获取用户信息
    payload = JWTHandler.decode_token(new_token)
    new_refresh_token = JWTHandler.generate_refresh_token(
        user_id=payload.get("sub"),
        username=payload.get("username")
    )
    
    return TokenResponse(
        access_token=new_token,
        refresh_token=new_refresh_token,
        expires_in=JWTConfig.ACCESS_TOKEN_EXPIRE_HOURS * 3600
    )


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


@router.post(
    "/demo-login/{username}",
    response_model=TokenResponse,
    summary="演示登录（无需密码）",
    description="用于演示的快速登录，只需提供用户名"
)
async def demo_login(username: str):
    """
    演示登录 - 快速生成 Token
    
    用于演示和开发测试，无需密码
    
    支持的用户名:
    - 张三 (user_001)
    - 李四 (user_002)  
    - 管理员 (admin_001)
    
    示例:
    POST /api/v1/auth/demo-login/张三
    """
    user = UserService.get_user_by_username(username)
    if not user:
        raise HTTPException(
            status_code=404,
            detail=f"测试用户 '{username}' 不存在"
        )
    
    # 生成 Token
    permissions = [p.value for p in user.permissions]
    access_token = JWTHandler.generate_access_token(
        user_id=user.user_id,
        username=user.username,
        role=user.role,
        permissions=permissions
    )
    
    refresh_token = JWTHandler.generate_refresh_token(
        user_id=user.user_id,
        username=user.username
    )
    
    return TokenResponse(
        access_token=access_token,
        refresh_token=refresh_token,
        expires_in=JWTConfig.ACCESS_TOKEN_EXPIRE_HOURS * 3600
    )
