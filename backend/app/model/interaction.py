"""
Capsule interaction related Pydantic models
"""
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field


class CommentUser(BaseModel):
    """评论用户信息模型"""
    user_id: int
    nickname: str
    avatar: str | None = None


class CommentItem(BaseModel):
    """评论项模型"""
    id: str
    content: str
    user: CommentUser
    created_at: datetime
    like_count: int | None = None
    is_liked: bool | None = None
    replies: List['CommentItem'] | None = None


class LikeCapsuleResponse(BaseModel):
    """点赞胶囊响应模型"""
    like_count: int
    is_liked: bool


class AddCommentRequest(BaseModel):
    """添加评论请求模型"""
    content: str = Field(..., min_length=1, max_length=500)
    parent_id: str | None = None


class AddCommentResponse(BaseModel):
    """添加评论响应模型"""
    comment_id: str
    content: str
    user_nickname: str
    created_at: datetime
    user_avatar: str | None = None


class CommentsListResponse(BaseModel):
    """评论列表响应模型"""
    comments: List[CommentItem]


class CollectCapsuleResponse(BaseModel):
    """收藏胶囊响应模型"""
    is_collected: bool


class CommentsQuery(BaseModel):
    """评论查询参数模型"""
    page: int | None = None
    page_size: int | None = None
    sort: str | None = None  # "latest", "hottest"