"""
Capsule unlocking related Pydantic models
"""
from datetime import datetime
from typing import List, Optional
from pydantic import BaseModel, Field

from app.database.orm import unlock_condition


class CurrentLocation(BaseModel):
    """当前位置模型"""
    latitude: float = Field(..., validation_alias="lat")
    longitude: float = Field(..., validation_alias="lng")

class UnlockCapsuleRequest(BaseModel):
    """解锁胶囊请求模型"""
    current_location: CurrentLocation
    password: str | None = Field(default=None, description="解锁密码（如果需要）")


class UnlockCapsuleResponse(BaseModel):
    """解锁胶囊响应模型"""
    capsule_id: str  # 修改为字符串类型以符合前端期望
    unlocked_at: datetime
    access_token: str


class NearbyCapsuleLocation(BaseModel):
    """附近胶囊位置信息"""
    latitude: float
    longitude: float
    distance: float  # meters


class NearbyCapsule(BaseModel):
    """附近胶囊项模型"""
    id: str
    title: str
    owner_id: int
    location: NearbyCapsuleLocation
    visibility: str  # "private", "friends", "public"
    unlock_condition_type: Optional[str] = "location"  # "password", "location"
    is_unlocked: bool
    can_unlock: bool
    creator_nickname: str
    created_at: datetime


class NearbyCapsulesResponse(BaseModel):
    """附近胶囊响应模型"""
    capsules: List[NearbyCapsule]


class NearbyCapsulesQuery(BaseModel):
    """附近胶囊查询参数模型"""
    lat: float
    lng: float
    radius: float | None = None  # meters
    page: int | None = None
    page_size: int | None = None