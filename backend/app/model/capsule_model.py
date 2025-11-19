
# 请求模型
from typing import List, Optional, Dict, Any
from datetime import datetime
from domain.condition import Location, UnlockConditions
from domain.capsule import Visibility

from pydantic import BaseModel, Field

class UploadMediaFile(BaseModel):
    """上传的媒体文件模型"""
    file_type: str = Field(..., description="文件类型")
    file_name: str = Field(..., description="文件名")
    file_size: int = Field(..., ge=1, le=50*1024*1024, description="文件大小（字节）")


class CapsuleCreateRequest(BaseModel):
    """创建胶囊请求模型"""
    title: str = Field(..., min_length=1, max_length=1024, description="胶囊标题")
    text_content: Optional[str] = Field(None, description="文本内容")
    media_files: Optional[List[UploadMediaFile]] = Field(None, description="媒体文件列表")
    location: Location = Field(..., description="地理位置")
    unlock_conditions: UnlockConditions = Field(..., description="解锁条件")
    visibility: Visibility = Field(..., description="可见性")


class CapsuleUpdateRequest(BaseModel):
    """更新胶囊请求模型"""
    title: Optional[str] = Field(None, min_length=1, max_length=100, description="胶囊标题")
    text_content: Optional[str] = Field(None, description="文本内容")
    visibility: Optional[Visibility] = Field(None, description="可见性")
    media_files_to_remove: Optional[List[int]] = Field(None, description="要删除的媒体文件的id")
    media_files_to_add: Optional[List[UploadMediaFile]] = Field(None, description="要添加的媒体文件")


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


class UnlockVerifyRequest(BaseModel):
    """验证解锁条件请求模型"""
    current_location: Location = Field(..., description="当前纬度")
    # 可选的胶囊ID，如果不提供则验证所有可解锁的胶囊
    capsule_id: Optional[str] = Field(None, description="要验证的胶囊ID")
    # 可选的当前时间，如果不提供则使用服务器时间
    current_time: Optional[datetime] = Field(None, description="当前时间")


class UnlockVerifyData(BaseModel):
    """验证解锁条件响应数据"""
    access_token: str = Field(..., description="访问令牌(用于访问内容)")
    capsule_id: str = Field(..., description="胶囊ID")
    unlocked_at: datetime = Field(..., description="解锁时间")


class UnlockVerifyResponse(BaseModel):
    """验证解锁条件响应模型"""
    code: int = Field(..., description="状态码")
    data: Optional[UnlockVerifyData] = Field(None, description="响应数据")
    message: str = Field(..., description="操作结果描述")


class BaseResponse(BaseModel):
    """基础响应模型"""
    success: bool = Field(..., description="是否成功")
    message: Optional[str] = Field(None, description="响应消息")


class ErrorResponse(BaseResponse):
    """错误响应模型"""
    error: Dict[str, Any] = Field(..., description="错误详情")


class CapsuleCreatedResponse(BaseResponse):
    """创建胶囊成功响应模型"""
    capsule_id: str = Field(..., description="胶囊id")
    title:Optional[str] = Field(None, description="胶囊标题")


class CapsuleListResponse(BaseResponse):
    """胶囊列表响应模型"""
    capsule_list:List[Dict[str, Any]] = Field(..., description="胶囊列表")
    page:int = Field(..., ge=0, description="当前所在页数")
    pages:int = Field(..., ge=0, description="总页数")


class CapsuleDetailResponse(BaseResponse):
    """胶囊详情响应模型"""
    capsule_info: Dict[str, Any] = Field(..., description="胶囊详细信息")


class CapsuleUpdateResponse(BaseResponse):
    """更新胶囊响应模型"""
    capsule_id:str = Field(..., description="更新的胶囊id")
    updated_fields:List[str] = Field(..., description="更新的字段")
    updated_at:datetime = Field(..., description="更新时间")

class CapsuleDeleteResponse(BaseResponse):
    """删除胶囊响应模型"""
    pass

class DetailedCapsuleInfo(BaseModel):
    """详细胶囊信息模型"""
    capsule_id: str = Field(..., description="胶囊ID")
    # TODO 补充详细胶囊信息模型
    pass

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


# 附近胶囊相关模型
class NearbyCapsuleLocation(BaseModel):
    """附近胶囊位置信息"""
    distance: float = Field(..., description="距离(米)")
    latitude: float = Field(..., description="纬度")
    longitude: float = Field(..., description="经度")


class NearbyCapsule(BaseModel):
    """附近胶囊项模型"""
    can_unlock: bool = Field(..., description="是否符合解锁条件")
    created_at: datetime = Field(..., description="创建时间")
    creator_nickname: Optional[str] = Field(None, description="创建者昵称")
    id: str = Field(..., description="胶囊ID")
    is_unlocked: bool = Field(..., description="是否已解锁")
    location: NearbyCapsuleLocation = Field(..., description="位置信息")
    title: str = Field(..., description="胶囊标题")
    visibility: str = Field(..., description="可见性")


class NearbyCapsulesData(BaseModel):
    """附近胶囊响应数据"""
    capsules: List[NearbyCapsule] = Field(..., description="附近胶囊列表")


class NearbyCapsulesResponse(BaseModel):
    """获取附近胶囊响应模型"""
    code: int = Field(..., description="状态码")
    data: Optional[NearbyCapsulesData] = Field(None, description="响应数据")
    message: str = Field(..., description="操作结果描述")