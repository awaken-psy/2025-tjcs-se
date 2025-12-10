from datetime import datetime
from typing import Optional
from enum import Enum
from pydantic import BaseModel

from app.model.friend import (
    SearchedUser,
    FriendRequestUser,
    FriendRequestItem,
    FriendItem,
    SendFriendRequest,
    HandleFriendRequest
)


class FriendStatus(str, Enum):
    """好友关系状态枚举"""
    NONE = "none"          # 无关系
    PENDING = "pending"    # 待处理（好友请求）
    ACCEPTED = "accepted"  # 已是好友
    BLOCKED = "blocked"    # 已拉黑
    REJECTED = "rejected"  # 已拒绝


class FriendRequestAction(str, Enum):
    """好友请求操作枚举"""
    ACCEPT = "accept"      # 接受
    REJECT = "reject"      # 拒绝


class FriendRequestType(str, Enum):
    """好友请求类型枚举"""
    RECEIVED = "received"  # 收到的请求
    SENT = "sent"         # 发送的请求


class User(BaseModel):
    """用户领域对象"""
    user_id: int
    username: str
    nickname: str
    avatar_url: Optional[str] = None
    email: Optional[str] = None
    user_type: Optional[str] = None
    is_active: bool = True
    created_at: Optional[datetime] = None


class FriendRelation(BaseModel):
    """好友关系领域对象"""
    id: Optional[int] = None
    user_id: int
    friend_id: int
    status: FriendStatus
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_api_friend_item(self, friend_user: User) -> FriendItem:
        """转换为API好友项模型"""
        return FriendItem(
            user_id=friend_user.user_id,
            nickname=friend_user.nickname,
            became_friends_at=self.created_at or datetime.now(),
            avatar=friend_user.avatar_url
        )

    def to_api_searched_user(self, user: User) -> SearchedUser:
        """转换为API搜索用户模型"""
        return SearchedUser(
            user_id=user.user_id,
            nickname=user.nickname,
            is_friend=(self.status == FriendStatus.ACCEPTED),
            friend_status=self.status.value,
            avatar=user.avatar_url
        )


class FriendRequest(BaseModel):
    """好友请求领域对象"""
    id: Optional[int] = None
    requester_id: int
    addressee_id: int
    status: FriendStatus
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_api_friend_request_item(self, user: User, is_received: bool = True) -> FriendRequestItem:
        """转换为API好友请求项模型"""
        request_user = FriendRequestUser(
            user_id=user.user_id,
            nickname=user.nickname,
            avatar=user.avatar_url
        )

        return FriendRequestItem(
            request_id=str(self.id) if self.id else "",
            user=request_user,
            status=self.status.value,
            created_at=self.created_at or datetime.now()
        )