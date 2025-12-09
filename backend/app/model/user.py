"""
User related Pydantic models
"""
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field, EmailStr


class UserStats(BaseModel):
    """用户统计信息模型"""
    created_capsules: int
    unlocked_capsules: int
    collected_capsules: int
    friends_count: int


class UserProfile(BaseModel):
    """用户资料模型"""
    user_id: int
    email: EmailStr
    nickname: str
    created_at: datetime
    avatar: str | None = None
    bio: str | None = None
    stats: UserStats | None = None


class UserHistoryItem(BaseModel):
    """历史记录项模型"""
    capsule_id: int
    title: str
    unlocked_at: datetime
    view_duration: int | None = None  # seconds


class UserHistoryResponse(BaseModel):
    """用户历史记录响应模型"""
    history: List[UserHistoryItem]


class UpdateUserRequest(BaseModel):
    """更新用户信息请求模型"""
    nickname: str | None = Field(None, min_length=1, max_length=20)
    avatar: str | None = None
    bio: str | None = Field(None, max_length=200)


class UserHistoryQuery(BaseModel):
    """用户历史记录查询参数模型"""
    page: int | None = None
    page_size: int | None = None
    sort: str | None = None  # "latest", "oldest"
    type: str | None = None  # "unlocked", "created", "collected"