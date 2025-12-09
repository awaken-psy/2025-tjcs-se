"""
Hub related Pydantic models
"""
from datetime import datetime
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field

from .unlock import NearbyCapsule


class UserInfoResponse(BaseModel):
    """用户基础信息响应模型"""
    user_id: int
    nickname: str | None = None
    avatar: str | None = None
    email: str
    created_at: datetime
    stats: Dict[str, Any]  # 统计信息


class RecentActivity(BaseModel):
    """最近用户动态模型"""
    id: int  # 动态ID
    type: str  # "capsule_created", "capsule_unlocked", "friend_added"
    user_id: int
    user_nickname: str
    target_id: Optional[int] = None  # 目标对象ID（胶囊ID、好友ID等）
    content: str  # 动态内容描述
    created_at: datetime
    metadata: Dict[str, Any] = {}  # 额外信息


class RecentActivitiesResponse(BaseModel):
    """最近用户动态响应模型"""
    activities: List[RecentActivity]
    total: int


class NearbyCapsulesQuery(BaseModel):
    """附近胶囊查询参数模型"""
    lat: float = Field(..., description="当前纬度")
    lng: float = Field(..., description="当前经度")
    radius_meters: int = Field(100, ge=10, le=10000, description="搜索半径（米）")
    page: int = Field(1, ge=1, description="页码")
    limit: int = Field(20, ge=1, le=100, description="每页数量")


class HubNearbyCapsulesResponse(BaseModel):
    """中枢页附近胶囊响应模型"""
    capsules: List[NearbyCapsule]


class UserLocationRequest(BaseModel):
    """用户位置上报请求模型"""
    latitude: float = Field(..., description="纬度")
    longitude: float = Field(..., description="经度")
    address: Optional[str] = Field(None, description="地址描述")


class UserLocationResponse(BaseModel):
    """用户位置响应模型"""
    user_id: int
    latitude: float
    longitude: float
    address: Optional[str] = None
    updated_at: datetime