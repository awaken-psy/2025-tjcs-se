"""
Event related Pydantic models
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from .base import Pagination


class EventCreateRequest(BaseModel):
    """创建活动请求模型"""
    name: str = Field(..., min_length=1, max_length=100, description="活动名称")
    description: str = Field(..., min_length=1, description="活动描述")
    date: datetime = Field(..., description="活动时间")
    location: str = Field(..., min_length=1, description="活动地点")
    tags: List[str] = Field(default=[], description="活动标签")
    cover_img: Optional[str] = Field(None, description="封面图片URL")


class EventUpdateRequest(BaseModel):
    """更新活动请求模型"""
    name: Optional[str] = Field(None, min_length=1, max_length=100, description="活动名称")
    description: Optional[str] = Field(None, min_length=1, description="活动描述")
    date: Optional[datetime] = Field(None, description="活动时间")
    location: Optional[str] = Field(None, min_length=1, description="活动地点")
    tags: Optional[List[str]] = Field(None, description="活动标签")
    cover_img: Optional[str] = Field(None, description="封面图片URL")


class EventDeleteRequest(BaseModel):
    """删除活动请求模型"""
    event_id: str = Field(..., description="活动ID")


class EventResponse(BaseModel):
    """活动响应模型"""
    id: str = Field(..., description="活动ID")
    name: str = Field(..., description="活动名称")
    description: str = Field(..., description="活动描述")
    date: datetime = Field(..., description="活动时间")
    location: str = Field(..., description="活动地点")
    tags: List[str] = Field(default=[], description="活动标签")
    cover_img: Optional[str] = Field(None, description="封面图片URL")
    participant_count: int = Field(default=0, description="参与人数")
    is_registered: bool = Field(default=False, description="当前用户是否已报名")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: datetime = Field(..., description="更新时间")


class EventCreateResponse(BaseModel):
    """创建活动响应模型"""
    id: str = Field(..., description="创建的活动ID")
    name: str = Field(..., description="活动名称")
    created_at: datetime = Field(..., description="创建时间")


class EventUpdateResponse(BaseModel):
    """更新活动响应模型"""
    updated: bool = Field(..., description="是否更新成功")
    event_id: str = Field(..., description="活动ID")


class EventDeleteResponse(BaseModel):
    """删除活动响应模型"""
    deleted: bool = Field(..., description="是否删除成功")
    event_id: str = Field(..., description="活动ID")


class EventRegistrationRequest(BaseModel):
    """活动报名请求模型"""
    event_id: str = Field(..., description="活动ID")


class EventRegistrationResponse(BaseModel):
    """活动报名响应模型"""
    registration_id: str = Field(..., description="报名记录ID")
    event_id: str = Field(..., description="活动ID")
    user_id: str = Field(..., description="用户ID")
    registered_at: datetime = Field(..., description="报名时间")


class EventCancelResponse(BaseModel):
    """取消报名响应模型"""
    cancelled: bool = Field(..., description="是否取消成功")
    event_id: str = Field(..., description="活动ID")


class EventListResponse(BaseModel):
    """活动列表响应模型"""
    list: List[EventResponse] = Field(..., description="活动列表")
    total: int = Field(..., description="总数量")
    page: Optional[int] = Field(None, description="当前页码")
    page_size: Optional[int] = Field(None, description="每页数量")


class EventBasic(BaseModel):
    """活动基本信息模型（用于列表展示）"""
    id: str
    name: str
    description: str
    date: datetime
    location: str
    tags: List[str] = []
    cover_img: Optional[str] = None
    participant_count: int = 0
    is_registered: bool = False
    created_at: datetime
    updated_at: datetime