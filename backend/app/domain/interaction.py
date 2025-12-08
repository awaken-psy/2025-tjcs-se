from datetime import datetime
from typing import Optional, List
from enum import Enum
from pydantic import BaseModel

from app.model.interaction import (
    CommentUser, CommentItem, LikeCapsuleResponse,
    AddCommentResponse, CollectCapsuleResponse
)


class InteractionType(str, Enum):
    """交互类型枚举"""
    VIEW = "view"
    LIKE = "like"
    COMMENT = "comment"
    SHARE = "share"
    COLLECT = "collect"


class CommentSortType(str, Enum):
    """评论排序类型枚举"""
    LATEST = "latest"    # 最新
    HOTTEST = "hottest"  # 最热


class User(BaseModel):
    """用户领域对象"""
    user_id: int
    username: str
    nickname: str
    avatar_url: Optional[str] = None


class Interaction(BaseModel):
    """交互领域对象"""
    id: Optional[int] = None
    unlock_record_id: int
    user_id: int  # 添加user_id字段
    capsule_id: int  # 添加capsule_id字段
    interaction_type: InteractionType
    comment_content: Optional[str] = None
    comment_rating: Optional[int] = None
    share_platform: Optional[str] = None
    share_url: Optional[str] = None
    interaction_latitude: Optional[float] = None
    interaction_longitude: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None

    def to_api_comment_item(self, user: User,
                           like_count: int = 0,
                           is_liked: bool = False,
                           replies: Optional[List['CommentItem']] = None) -> CommentItem:
        """转换为API评论项模型"""
        comment_user = CommentUser(
            user_id=user.user_id,
            nickname=user.nickname,
            avatar=user.avatar_url
        )

        return CommentItem(
            id=str(self.id) if self.id else "",
            content=self.comment_content or "",
            user=comment_user,
            created_at=self.created_at or datetime.now(),
            like_count=like_count,
            is_liked=is_liked,
            replies=replies
        )


class CapsuleCollect(BaseModel):
    """胶囊收藏领域对象"""
    id: Optional[int] = None
    user_id: int
    capsule_id: int
    is_collected: bool = True
    created_at: Optional[datetime] = None

    def to_api_collect_response(self) -> CollectCapsuleResponse:
        """转换为API收藏响应模型"""
        return CollectCapsuleResponse(
            is_collected=self.is_collected
        )


class CapsuleLike(BaseModel):
    """胶囊点赞领域对象"""
    user_id: int
    capsule_id: int
    is_liked: bool = True
    like_count: int = 0

    def to_api_like_response(self) -> LikeCapsuleResponse:
        """转换为API点赞响应模型"""
        return LikeCapsuleResponse(
            like_count=self.like_count,
            is_liked=self.is_liked
        )


class Comment(BaseModel):
    """评论领域对象"""
    id: Optional[int] = None
    capsule_id: int
    user_id: int
    content: str
    parent_id: Optional[int] = None
    like_count: int = 0
    is_liked: bool = False
    created_at: Optional[datetime] = None

    def to_api_add_comment_response(self, user: User) -> AddCommentResponse:
        """转换为API添加评论响应模型"""
        return AddCommentResponse(
            comment_id=str(self.id) if self.id else "",
            content=self.content,
            user_nickname=user.nickname,
            created_at=self.created_at or datetime.now(),
            user_avatar=user.avatar_url
        )