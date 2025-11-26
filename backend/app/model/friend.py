"""
Friend related Pydantic models
"""
from datetime import datetime
from typing import List
from pydantic import BaseModel


class SearchedUser(BaseModel):
    """搜索用户结果模型"""
    user_id: int
    nickname: str
    is_friend: bool
    friend_status: str  # "none", "pending", "accepted"
    avatar: str | None = None


class FriendRequestUser(BaseModel):
    """好友请求用户信息"""
    user_id: int
    nickname: str
    avatar: str | None = None


class FriendRequestItem(BaseModel):
    """好友请求项模型"""
    request_id: str
    user: FriendRequestUser
    status: str  # "pending", "accepted", "rejected"
    created_at: datetime


class FriendItem(BaseModel):
    """好友项模型"""
    user_id: int
    nickname: str
    became_friends_at: datetime
    avatar: str | None = None


class UserSearchResponse(BaseModel):
    """用户搜索响应模型"""
    users: List[SearchedUser]


class FriendRequestsResponse(BaseModel):
    """好友请求响应模型"""
    requests: List[FriendRequestItem]


class FriendsListResponse(BaseModel):
    """好友列表响应模型"""
    friends: List[FriendItem]


class SendFriendRequest(BaseModel):
    """发送好友请求模型"""
    target_user_id: int


class HandleFriendRequest(BaseModel):
    """处理好友请求模型"""
    action: str  # "accept", "reject"


class UserSearchQuery(BaseModel):
    """用户搜索查询参数模型"""
    q: str
    page: int | None = None
    page_size: int | None = None


class FriendRequestsQuery(BaseModel):
    """好友请求查询参数模型"""
    type: str  # "received", "sent"
    page: int | None = None
    page_size: int | None = None
    status: str | None = None  # "pending", "accepted", "rejected"