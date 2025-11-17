"""
Authentication related Pydantic models
"""
from pydantic import BaseModel, EmailStr


class UserRegisterRequest(BaseModel):
    """用户注册请求模型"""
    email: EmailStr
    password: str
    nickname: str
    student_id: str | None = None


class UserLoginRequest(BaseModel):
    """用户登录请求模型"""
    email: EmailStr
    password: str


class UserAuthResponse(BaseModel):
    """用户认证响应模型"""
    user_id: int
    email: EmailStr
    nickname: str
    token: str
    refresh_token: str
    avatar: str | None = None

class UserRefreshTokenResponse(BaseModel):
    """用户刷新令牌请求响应"""
    token: str
    refresh_token: str