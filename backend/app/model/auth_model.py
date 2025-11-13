from pydantic import BaseModel, Field
from datetime import datetime
from typing import Optional

class TokenRequest(BaseModel):
    """Token 请求模型"""
    username: str = Field(..., description="用户名") # 用户名
    password: str = Field(..., description="密码（演示用，实际应验证）") # 密码


class TokenResponse(BaseModel):
    """Token 响应模型"""
    access_token: str = Field(..., description="访问令牌")
    refresh_token: str = Field(..., description="刷新令牌")
    token_type: str = "bearer"
    expires_in: int  # 过期秒数


class RefreshTokenRequest(BaseModel):
    """刷新令牌请求"""
    refresh_token: str = Field(..., description="刷新令牌")


class UserInfoResponse(BaseModel):
    """用户信息响应"""
    # 通用信息
    user_id: str = Field(..., description="用户 ID")
    username: str = Field(..., description="用户名")
    role: str = Field(..., description="用户角色")

    # 认证用户信息
    last_login: Optional[datetime] = Field(None, description="上次登录时间")
    email: Optional[str] = Field(None, description="邮箱")
    department: Optional[str] = Field(None, description="部门")

    # 管理员信息
    admin_level: Optional[int] = Field(None, description="管理员级别")

    # @staticmethod
    # def from_user(user: BaseUser):
    #     """从 BaseUser 对象构造 UserInfoResponse 对象"""
    #     return UserInfoResponse(
    #         user_id=user.user_id,
    #         username=user.username,
    #         role=user.role,
    #         email=getattr(user, 'email', None),
    #         department=getattr(user, 'department', None),
    #         last_login=getattr(user, 'last_login', None),
    #         admin_level=getattr(user, 'admin_level', None)
    #     )

