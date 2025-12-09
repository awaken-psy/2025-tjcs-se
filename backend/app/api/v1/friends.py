"""
Friends API interface
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database.database import get_db
from app.auth.dependencies import login_required
from app.model import (
    BaseResponse,
    UserSearchResponse,
    FriendRequestsResponse,
    FriendsListResponse,
    SendFriendRequest,
    HandleFriendRequest,
    UserSearchQuery,
    FriendRequestsQuery
)
from app.services.friends import FriendService

router = APIRouter(prefix='/friends', tags=['Friends'])


@router.get("/search", response_model=BaseResponse[UserSearchResponse])
async def search_users(
    query: UserSearchQuery = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(login_required)
):
    """搜索用户"""
    try:
        friend_service = FriendService(db)
        page = query.page or 1
        page_size = query.page_size or 20

        result = friend_service.search_users(
            current_user_id=current_user.user_id,
            query=query.q,
            page=page,
            page_size=page_size
        )

        return BaseResponse.success("搜索成功", data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"搜索用户失败: {str(e)}"
        )


@router.post("/requests", response_model=BaseResponse[None])
async def send_friend_request(
    request: SendFriendRequest,
    db: Session = Depends(get_db),
    current_user = Depends(login_required)
):
    """发送好友请求"""
    try:
        friend_service = FriendService(db)
        friend_service.send_friend_request(
            requester_id=current_user.user_id,
            target_user_id=request.target_user_id
        )

        return BaseResponse.success("好友请求发送成功")
    except ValueError as e:
        return BaseResponse.fail(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"发送好友请求失败: {str(e)}"
        )


@router.get("/requests", response_model=BaseResponse[FriendRequestsResponse])
async def get_friend_requests(
    query: FriendRequestsQuery = Depends(),
    db: Session = Depends(get_db),
    current_user = Depends(login_required)
):
    """获取好友请求"""
    try:
        friend_service = FriendService(db)
        page = query.page or 1
        page_size = query.page_size or 20

        result = friend_service.get_friend_requests(
            current_user_id=current_user.user_id,
            request_type=query.type,
            page=page,
            page_size=page_size,
            status=query.status
        )

        return BaseResponse.success("获取好友请求成功", data=result)
    except ValueError as e:
        return BaseResponse.fail(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取好友请求失败: {str(e)}"
        )


@router.post("/requests/{request_id}", response_model=BaseResponse[None])
async def handle_friend_request(
    request_id: str,
    request: HandleFriendRequest,
    db: Session = Depends(get_db),
    current_user = Depends(login_required)
):
    """处理好友请求"""
    try:
        friend_service = FriendService(db)
        friend_service.handle_friend_request(
            current_user_id=current_user.user_id,
            request_id=int(request_id),
            action=request.action
        )

        message = "接受好友请求成功" if request.action == "accept" else "拒绝好友请求成功"

        return BaseResponse.success(message)
    except ValueError as e:
        return BaseResponse.fail(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"处理好友请求失败: {str(e)}"
        )


@router.get("/", response_model=BaseResponse[FriendsListResponse])
async def get_friends_list(
    page: int = 1,
    page_size: int = 20,
    db: Session = Depends(get_db),
    current_user = Depends(login_required)
):
    """获取好友列表"""
    try:
        friend_service = FriendService(db)
        result = friend_service.get_friends_list(
            current_user_id=current_user.user_id,
            page=page,
            page_size=page_size
        )

        return BaseResponse.success("获取好友列表成功", data=result)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"获取好友列表失败: {str(e)}"
        )


@router.delete("/{friend_id}", response_model=BaseResponse[None])
async def remove_friend(
    friend_id: int,
    db: Session = Depends(get_db),
    current_user = Depends(login_required)
):
    """删除好友"""
    try:
        friend_service = FriendService(db)
        friend_service.remove_friend(
            current_user_id=current_user.user_id,
            friend_id=friend_id
        )

        return BaseResponse.success("删除好友成功")
    except ValueError as e:
        return BaseResponse.fail(str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"删除好友失败: {str(e)}"
        )