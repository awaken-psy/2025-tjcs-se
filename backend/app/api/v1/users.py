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
from app.auth.dependencies import login_required
from app.domain.user import AuthorizedUser
from app.services.user_service import UserService

router = APIRouter(prefix='/users', tags=['Users'])


@router.get("/me", response_model=BaseResponse[UserProfile])
async def get_my_profile(
    current_user: AuthorizedUser = Depends(login_required)
):
    """获取我的资料"""
    try:
        # 创建用户服务
        user_service = UserService()

        # 获取用户资料
        success, user_profile, message = user_service.get_user_profile(current_user.user_id)

        if success:
            return BaseResponse.success(data=user_profile, message=message)
        else:
            return BaseResponse.fail(message=message)

    except Exception as e:
        return BaseResponse.fail(message=f"获取用户资料失败: {str(e)}")


@router.put("/me", response_model=BaseResponse[None])
async def update_my_profile(
    request: UpdateUserRequest,
    current_user: AuthorizedUser = Depends(login_required)
):
    """更新我的资料"""
    try:
        # 创建用户服务
        user_service = UserService()

        # 更新用户资料
        success, user_profile, message = user_service.update_user_profile(
            user_id=current_user.user_id,
            update_request=request
        )

        if success:
            return BaseResponse.success(message=message)
        else:
            return BaseResponse.fail(message=message)

    except Exception as e:
        return BaseResponse.fail(message=f"更新用户资料失败: {str(e)}")


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