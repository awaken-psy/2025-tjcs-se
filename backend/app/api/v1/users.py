"""
Users API interface
"""
from fastapi import APIRouter, Depends

from app.model import (
    BaseResponse,
    UserProfile,
    UserHistoryResponse,
    UpdateUserRequest,
    UserHistoryQuery
)

router = APIRouter(prefix='/users', tags=['Users'])


@router.get("/me", response_model=BaseResponse[UserProfile])
async def get_my_profile():
    """获取我的资料"""
    pass


@router.put("/me", response_model=BaseResponse[UserProfile])
async def update_my_profile(
    request: UpdateUserRequest
):
    """更新我的资料"""
    pass


@router.get("/me/history", response_model=BaseResponse[UserHistoryResponse])
async def get_my_history(
    query: UserHistoryQuery = Depends()
):
    """获取我的历史记录"""
    pass


@router.get("/{user_id}", response_model=BaseResponse[UserProfile])
async def get_user_profile(
    user_id: int
):
    """获取用户资料"""
    pass


@router.get("/{user_id}/capsules", response_model=BaseResponse[dict])
async def get_user_capsules(
    user_id: int
):
    """获取用户胶囊"""
    pass