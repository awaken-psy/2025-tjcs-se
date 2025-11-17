"""
Authentication API interface
"""
from fastapi import APIRouter

from app.model import (
    BaseResponse,
    UserRegisterRequest,
    UserLoginRequest,
    UserAuthResponse,
    UserRefreshTokenResponse
)

router = APIRouter(prefix='/auth', tags=['Authorization'])


@router.post("/register", response_model=BaseResponse[UserAuthResponse])
async def register(
    request: UserRegisterRequest
):
    """用户注册"""
    pass


@router.post("/login", response_model=BaseResponse[UserAuthResponse])
async def login(
    request: UserLoginRequest
):
    """用户登录"""
    pass


@router.post("/logout", response_model=BaseResponse[None])
async def logout():
    """用户登出"""
    pass


@router.post("/refresh", response_model=BaseResponse[UserRefreshTokenResponse])
async def refresh_token():
    """刷新令牌"""
    pass