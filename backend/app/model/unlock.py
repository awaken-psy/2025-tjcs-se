"""
Capsule unlocking related Pydantic models
"""
from datetime import datetime
from typing import List
from pydantic import BaseModel


class CurrentLocation(BaseModel):
    """当前位置模型"""
    latitude: float
    longitude: float


class UnlockCapsuleRequest(BaseModel):
    """解锁胶囊请求模型"""
    current_location: CurrentLocation


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
    location: NearbyCapsuleLocation
    visibility: str  # "private", "friends", "public"
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