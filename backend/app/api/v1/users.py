"""
Users API interface
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.dependencies import login_required
from app.model import (
    BaseResponse,
    UserProfile,
    UserHistoryResponse,
    UpdateUserRequest,
    UserHistoryQuery
)
from app.services.users import UserService

router = APIRouter(prefix='/users', tags=['Users'])


@router.get("/me", response_model=BaseResponse[UserProfile])
async def get_my_profile(
    db: Session = Depends(get_db),
    current_user = Depends(login_required)
):
    """获取我的资料"""
    try:
        user_service = UserService(db)
        result = user_service.get_my_profile(current_user.user_id)

        return BaseResponse.success("获取资料成功", data=result)
    except ValueError as e:
        return BaseResponse.fail(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取资料失败: {str(e)}"
        )


@router.put("/me", response_model=BaseResponse[UserProfile])
async def update_my_profile(
    request: UpdateUserRequest,
    db: Session = Depends(get_db),
    current_user = Depends(login_required)
):
    """更新我的资料"""
    try:
        user_service = UserService(db)
        result = user_service.update_my_profile(
            user_id=current_user.user_id,
            nickname=request.nickname,
            avatar=request.avatar,
            bio=request.bio
        )

        return BaseResponse.success("更新资料成功", data=result)
    except ValueError as e:
        return BaseResponse.fail(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"更新资料失败: {str(e)}"
        )


@router.get("/me/history", response_model=BaseResponse[UserHistoryResponse])
async def get_my_history(
    query: UserHistoryQuery = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(login_required)
):
    """获取我的历史记录"""
    try:
        user_service = UserService(db)
        page = query.page or 1
        page_size = query.page_size or 20
        sort = query.sort or "latest"
        type = query.type or "unlocked"

        result = user_service.get_my_history(
            user_id=current_user.user_id,
            page=page,
            page_size=page_size,
            sort=sort,
            type=type
        )

        return BaseResponse.success("获取历史记录成功", data=result)
    except ValueError as e:
        return BaseResponse.fail(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取历史记录失败: {str(e)}"
        )


@router.get("/{user_id}", response_model=BaseResponse[UserProfile])
async def get_user_profile(
    user_id: int,
    db: Session = Depends(get_db)
):
    """获取用户资料"""
    try:
        user_service = UserService(db)
        result = user_service.get_user_profile(user_id)

        return BaseResponse.success("获取用户资料成功", data=result)
    except ValueError as e:
        return BaseResponse.fail(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户资料失败: {str(e)}"
        )


@router.get("/{user_id}/capsules", response_model=BaseResponse[dict])
async def get_user_capsules(
    user_id: int,
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db)
):
    """获取用户胶囊"""
    try:
        user_service = UserService(db)
        result = user_service.get_user_capsules(
            user_id=user_id,
            page=page,
            page_size=page_size
        )

        return BaseResponse.success("获取用户胶囊成功", data=result)
    except ValueError as e:
        return BaseResponse.fail(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取用户胶囊失败: {str(e)}"
        )