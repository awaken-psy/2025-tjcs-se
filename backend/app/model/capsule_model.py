
# 请求模型
from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from pydantic import BaseModel, Field
from enum import Enum


class CapsuleVisibility(str, Enum):
    """胶囊可见性枚举"""
    PRIVATE = "private"
    FRIENDS = "friends"
    PUBLIC = "public"


class CapsuleStatus(str, Enum):
    """胶囊状态枚举"""
    DRAFT = "draft"
    PENDING = "pending"
    PUBLISHED = "published"


class Location(BaseModel):
    """位置信息模型"""
    latitude: float = Field(..., description="纬度")
    longitude: float = Field(..., description="经度")
    address: Optional[str] = Field(None, description="地址描述")


class UnlockCondition(BaseModel):
    """解锁条件模型"""
    type: str = Field(..., description="解锁条件类型")  # time, location, event
    value: Optional[str] = Field(None, description="条件值")
    radius: Optional[float] = Field(None, description="地点触发半径(米)")
    event_id: Optional[str] = Field(None, description="事件ID")
    is_unlocked: Optional[bool] = Field(None, description="当前用户是否已解锁")


class UnlockConditions(BaseModel):
    """解锁条件列表模型"""
    conditions: List[UnlockCondition] = Field(default_factory=list, description="解锁条件列表")


class MediaFile(BaseModel):
    """媒体文件模型"""
    id: str = Field(..., description="文件ID")
    type: str = Field(..., description="文件类型")  # image, audio
    url: str = Field(..., description="文件URL")
    thumbnail: Optional[str] = Field(None, description="缩略图URL")
    duration: Optional[float] = Field(None, description="音频时长(秒)")


class UserInfo(BaseModel):
    """用户信息模型"""
    user_id: int = Field(..., description="用户ID")
    nickname: str = Field(..., description="用户昵称")
    avatar: Optional[str] = Field(None, description="用户头像URL")


class CapsuleStats(BaseModel):
    """胶囊统计模型"""
    view_count: int = Field(..., description="查看次数")
    like_count: int = Field(..., description="点赞数")
    comment_count: int = Field(..., description="评论数")
    unlock_count: int = Field(..., description="解锁次数")
    is_liked: Optional[bool] = Field(None, description="当前用户是否点赞")
    is_collected: Optional[bool] = Field(None, description="当前用户是否收藏")


class CapsuleCreateRequest(BaseModel):
    """创建胶囊请求模型"""
    title: str = Field(..., min_length=1, max_length=100, description="胶囊标题")
    content: str = Field(..., min_length=1, description="胶囊内容")
    visibility: CapsuleVisibility = Field(..., description="可见性")
    tags: Optional[List[str]] = Field(default_factory=list, description="标签列表")
    location: Optional[Location] = Field(None, description="位置信息")
    unlock_conditions: Optional[UnlockConditions] = Field(None, description="解锁条件")
    media_files: Optional[List[str]] = Field(default_factory=list, description="媒体文件ID列表")


class CapsuleCreateRequestLegacy(BaseModel):
    """创建胶囊请求模型（兼容前端扁平化数据格式）"""
    title: str = Field(..., min_length=1, max_length=100, description="胶囊标题")
    content: str = Field(..., min_length=1, description="胶囊内容")
    visibility: str = Field(..., description="可见性")
    tags: Optional[List[str]] = Field(default_factory=list, description="标签列表")
    location: Optional[str] = Field("", description="位置信息")
    lat: Optional[float] = Field(0.0, description="纬度")
    lng: Optional[float] = Field(0.0, description="经度")
    createTime: Optional[str] = Field(None, description="创建时间")
    updateTime: Optional[str] = Field(None, description="更新时间")
    imageUrl: Optional[str] = Field("", description="图片URL")
    likes: Optional[int] = Field(0, description="点赞数")
    views: Optional[int] = Field(0, description="浏览数")


class CapsuleUpdateRequest(BaseModel):
    """更新胶囊请求模型"""
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="新标题")
    content: Optional[str] = Field(None, min_length=1, description="新内容")
    visibility: Optional[CapsuleVisibility] = Field(None, description="新可见性")
    tags: Optional[List[str]] = Field(None, description="新标签列表")


class DraftSaveRequest(BaseModel):
    """保存草稿请求模型"""
    title: str = Field(..., min_length=1, max_length=100, description="草稿标题")
    content: Optional[str] = Field(None, description="部分内容")
    visibility: Optional[CapsuleVisibility] = Field(CapsuleVisibility.PRIVATE, description="可见性")


class UnlockCheckRequest(BaseModel):
    """解锁检查请求模型"""
    user_location: Location = Field(..., description="用户当前位置")
    current_time: Optional[str] = Field(None, description="当前时间（ISO格式），如不提供则使用服务器时间")
    max_distance_meters: int = Field(1000, ge=10, le=10000, description="最大查询距离（米）")


class UnlockCapsuleRequest(BaseModel):
    """解锁胶囊请求模型"""
    capsule_id: str = Field(..., description="胶囊ID")
    user_location: Optional[Dict[str, float]] = Field(None, description="用户当前位置")
    current_time: Optional[str] = Field(None, description="当前时间")


class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = Field(..., description="是否成功")
    message: Optional[str] = Field(None, description="响应消息")


class ErrorResponse(BaseResponse):
    """错误响应模型"""
    error: Dict[str, Any] = Field(..., description="错误详情")


class CapsuleCreatedResponse(BaseResponse):
    """创建胶囊成功响应模型"""
    capsule_id: str = Field(..., description="胶囊ID")
    title: str = Field(..., description="胶囊标题")
    status: CapsuleStatus = Field(..., description="状态")
    created_at: datetime = Field(..., description="创建时间")


class CapsuleUpdateResponse(BaseResponse):
    """更新胶囊响应模型"""
    capsule_id: str = Field(..., description="胶囊ID")
    updated_at: datetime = Field(..., description="更新时间")


class DraftSaveResponse(BaseResponse):
    """保存草稿响应模型"""
    draft_id: str = Field(..., description="草稿ID")
    saved_at: datetime = Field(..., description="保存时间")


class CapsuleListItem(BaseModel):
    """胶囊列表项模型"""
    capsule_id: str = Field(..., description="胶囊ID")
    title: str = Field(..., description="胶囊标题")
    content: str = Field(..., description="胶囊内容")
    visibility: CapsuleVisibility = Field(..., description="可见性")
    status: CapsuleStatus = Field(..., description="状态")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")
    location: Optional[Location] = Field(None, description="位置信息")
    media_count: int = Field(default=0, description="媒体文件数量")


class PaginationInfo(BaseModel):
    """分页信息模型"""
    page: int = Field(..., ge=1, description="当前页码")
    page_size: int = Field(..., ge=1, le=100, description="每页数量")
    total: int = Field(..., ge=0, description="总记录数")
    total_pages: int = Field(..., ge=0, description="总页数")


class CapsuleListResponse(BaseModel):
    """胶囊列表响应模型"""
    capsules: List[CapsuleListItem] = Field(..., description="胶囊列表")
    pagination: PaginationInfo = Field(..., description="分页信息")


class CapsuleListResponseLegacy(BaseModel):
    """胶囊列表响应模型（兼容前端格式）"""
    code: int = Field(200, description="响应状态码")
    message: str = Field("success", description="响应消息")
    data: Union[List[Dict[str, Any]], Dict[str, Any]] = Field(..., description="胶囊数据")
    total: Optional[int] = Field(None, description="总数量")


class CapsuleDetailInfo(BaseModel):
    """胶囊详情信息模型"""
    id: str = Field(..., description="胶囊ID")
    title: str = Field(..., description="胶囊标题")
    content: str = Field(..., description="胶囊内容")
    visibility: CapsuleVisibility = Field(..., description="可见性")
    status: CapsuleStatus = Field(..., description="状态")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    location: Optional[Location] = Field(None, description="位置信息")
    unlock_conditions: Optional[UnlockConditions] = Field(None, description="解锁条件")
    media_files: List[MediaFile] = Field(default_factory=list, description="媒体文件列表")
    creator: UserInfo = Field(..., description="创建者信息")
    stats: CapsuleStats = Field(..., description="统计信息")
    created_at: datetime = Field(..., description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")


class CapsuleDetailResponse(BaseModel):
    """胶囊详情响应模型"""
    capsule: CapsuleDetailInfo = Field(..., description="胶囊详细信息")


class CapsuleDeleteResponse(BaseResponse):
    """删除胶囊响应模型"""
    pass

class DetailedCapsuleInfo(BaseModel):
    """详细胶囊信息模型"""
    capsule_id: str = Field(..., description="胶囊ID")
    title: Optional[str] = Field(None, description="胶囊标题")
    content: Optional[str] = Field(None, description="胶囊内容")
    location: Optional[Location] = Field(None, description="胶囊位置")
    visibility: Optional[str] = Field(None, description="可见性")
    created_at: Optional[datetime] = Field(None, description="创建时间")
    updated_at: Optional[datetime] = Field(None, description="更新时间")

class SimpleCapsuleInfo(BaseModel):
    """简化胶囊信息模型"""
    capsule_id: str = Field(..., description="胶囊ID")
    title: str = Field(..., description="胶囊标题")
    created_at: datetime = Field(..., description="创建时间")
    position: Location = Field(..., description="胶囊位置信息")
    # owner_id: str = Field(..., description="胶囊所有者ID")

class UnlockCheckResponse(BaseResponse):
    """解锁检查响应模型"""
    unlockable_capsules: List[SimpleCapsuleInfo] = Field(default_factory=list, description="可解锁胶囊列表")
    total_capsules_found: int = Field(..., description="找到的胶囊总数")
    unlockable_count: int = Field(..., description="可解锁的胶囊数量")
    user_location: Location = Field(..., description="用户位置信息")
    check_time: str = Field(..., description="检查时间")


class UnlockCapsuleResponse(BaseResponse):
    """解锁胶囊响应模型"""
    capsule_id: str = Field(..., description="胶囊ID")
    unlocked_at: str = Field(..., description="解锁时间")
    capsule_context: DetailedCapsuleInfo = Field(..., description="胶囊详细信息")
    unlock_method: str = Field(..., description="解锁方式")
    unlock_conditions_met: List[str] = Field(..., description="满足的解锁条件")