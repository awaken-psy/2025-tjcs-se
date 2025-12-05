"""
Capsule related Pydantic models
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from .base import Pagination


class Location(BaseModel):
    """位置模型"""
    latitude: float
    longitude: float
    address: str | None = None


class UnlockConditions(BaseModel):
    """解锁条件模型"""
    type: str  # "time", "location", "event"
    value: str | None = None  # datetime for time type
    radius: float | None = None  # meters for location type
    event_id: str | None = None
    is_unlocked: bool | None = None


class MediaFile(BaseModel):
    """媒体文件模型"""
    id: str
    type: str  # "image", "audio"
    url: str
    thumbnail: str | None = None
    duration: float | None = None  # seconds for audio


class Creator(BaseModel):
    """创建者信息模型"""
    user_id: int
    nickname: str
    avatar: str | None = None


class CapsuleStats(BaseModel):
    """胶囊统计模型"""
    view_count: int
    like_count: int
    comment_count: int
    unlock_count: int
    is_liked: bool | None = None
    is_collected: bool | None = None


class CapsuleBasic(BaseModel):
    """胶囊基础信息模型"""
    id: int
    title: str
    visibility: str  # "private", "friends", "public"
    status: str  # "draft", "pending", "published"
    created_at: datetime
    content_preview: str | None = None
    cover_image: str | None = None
    unlock_count: int | None = None
    like_count: int | None = None
    comment_count: int | None = None


class CapsuleDetail(BaseModel):
    """胶囊详情模型"""
    id: int
    title: str
    content: str
    visibility: str
    status: str
    created_at: datetime
    tags: List[str] | None = None
    location: Location | None = None
    unlock_conditions: UnlockConditions | None = None
    media_files: List[MediaFile] | None = None
    creator: Creator | None = None
    stats: CapsuleStats | None = None
    updated_at: datetime | None = None


class CapsuleCreateRequest(BaseModel):
    """创建胶囊请求模型"""
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)
    visibility: str  # "private", "friends", "public"
    tags: List[str] | None = None
    location: Location | None = None
    unlock_conditions: UnlockConditions | None = None
    media_files: List[str] | None = None  # file IDs




class CapsuleUpdateRequest(BaseModel):
    """更新胶囊请求模型"""
    title: str | None = Field(None, min_length=1, max_length=100)
    content: str | None = Field(None, min_length=1)
    visibility: str | None = None  # "private", "friends", "public"
    tags: List[str] | None = None


class CapsuleDraftRequest(BaseModel):
    """保存草稿请求模型"""
    title: str | None = Field(None, min_length=1, max_length=100)
    content: str | None = None
    visibility: str | None = None  # "private", "friends", "public"


class CapsuleCreateResponse(BaseModel):
    """创建胶囊响应模型"""
    capsule_id: int
    title: str
    status: str
    created_at: datetime


class CapsuleUpdateResponse(BaseModel):
    """更新胶囊响应模型"""
    capsule_id: int
    updated_at: datetime


class CapsuleDraftResponse(BaseModel):
    """保存草稿响应模型"""
    draft_id: str
    saved_at: datetime


class CapsuleListResponse(BaseModel):
    """胶囊列表响应模型"""
    capsules: List[CapsuleBasic]
    pagination: Pagination


class MyCapsulesQuery(BaseModel):
    """我的胶囊查询参数模型"""
    page: int = Field(1, ge=1)
    page_size: int = Field(20, ge=1, le=100)
    status: str = Field("all", pattern="^(all|draft|published)$")


class MultiModeBrowseResponse(BaseModel):
    """多模式浏览响应模型"""
    mode: str  # "map", "timeline", "tags"
    capsules: List[CapsuleBasic] | None = None
    timeline_groups: dict | None = None  # timeline模式使用 {"2024年1月": [...], "2023年12月": [...]}