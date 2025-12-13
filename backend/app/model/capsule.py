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
    type: str = Field(default="private", description="解锁条件类型: private, password, public")
    password: str | None = Field(default=None, description="解锁密码")
    radius: float | None = Field(default=None, description="地点触发半径(米)")
    is_unlocked: bool | None = Field(default=None, description="当前用户是否已解锁")
    unlockable_time: datetime | None = Field(default=None, description="可解锁的最早时间")


class MediaFile(BaseModel):
    """媒体文件模型"""
    id: int  # 修改为整数类型，与数据库ID一致
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
    id: str  # 修改为字符串类型以符合前端期望
    title: str
    visibility: str  # "private", "friends", "public"
    status: str  # "draft", "pending", "published"
    created_at: datetime
    content_preview: str | None = None
    cover_image: str | None = None
    unlock_count: int | None = None
    like_count: int | None = None
    comment_count: int | None = None
    latitude: float | None = None  # 为地图功能添加经纬度字段
    longitude: float | None = None


class CapsuleDetail(BaseModel):
    """胶囊详情模型"""
    id: str  # 修改为字符串类型以符合前端期望
    title: str
    content: str
    visibility: str
    status: str  # "draft", "published", "all"
    created_at: datetime
    tags: List[str] | None = None
    location: Location | None = None
    unlock_conditions: UnlockConditions | None = None
    media_files: List[MediaFile] | None = None
    creator: Creator | None = None
    stats: CapsuleStats | None = None


class CapsuleCreateRequest(BaseModel):
    """创建胶囊请求模型"""
    title: str = Field(..., min_length=1, max_length=100)
    content: str = Field(..., min_length=1)
    visibility: str  # "private", "friends", "public"
    tags: List[str] | None = None
    location: Location | None = None
    unlock_conditions: UnlockConditions | None = None
    media_files: List[str] | None = None  # file IDs 改回字符串类型以兼容前端




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
    capsule_id: str  # 前端期望string类型
    title: str
    status: str
    created_at: datetime


class CapsuleUpdateResponse(BaseModel):
    """更新胶囊响应模型"""
    capsule_id: str  # 修改为字符串类型以符合前端期望
    updated_at: datetime


class CapsuleDraftResponse(BaseModel):
    """保存草稿响应模型"""
    draft_id: int  # 修改为整数类型，与数据库ID一致
    saved_at: datetime


class CapsuleListResponse(BaseModel):
    """胶囊列表响应模型"""
    capsules: List[CapsuleDetail]
    pagination: Pagination


class MyCapsulesQuery(BaseModel):
    """我的胶囊查询参数模型"""
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)  # 改为size，与frontend保持一致
    status: str = Field("all", pattern="^(all|draft|published)$")


class MultiModeBrowseResponse(BaseModel):
    """多模式浏览响应模型"""
    mode: str  # "map", "timeline", "tags"
    capsules: List[CapsuleDetail] | None = None
    timeline_groups: dict | None = None  # timeline模式使用 {"2024年1月": [...], "2023年12月": [...]}