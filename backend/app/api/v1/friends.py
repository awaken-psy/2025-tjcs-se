"""
Friends API interface
"""
from fastapi import APIRouter, Depends

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

router = APIRouter(prefix='/friends', tags=['Friends'])


@router.get("/search", response_model=BaseResponse[UserSearchResponse])
async def search_users(
    query: UserSearchQuery = Depends()
):
    """搜索用户"""
    pass


@router.post("/requests", response_model=BaseResponse[None])
async def send_friend_request(
    request: SendFriendRequest
):
    """发送好友请求"""
    pass


@router.get("/requests", response_model=BaseResponse[FriendRequestsResponse])
async def get_friend_requests(
    query: FriendRequestsQuery = Depends()
):
    """获取好友请求"""
    pass


@router.post("/requests/{request_id}", response_model=BaseResponse[None])
async def handle_friend_request(
    request_id: str,
    request: HandleFriendRequest
):
    """处理好友请求"""
    pass


@router.get("/", response_model=BaseResponse[FriendsListResponse])
async def get_friends_list():
    """获取好友列表"""
    pass


@router.delete("/{friend_id}", response_model=BaseResponse[None])
async def remove_friend(
    friend_id: int
):
    """删除好友"""
    pass