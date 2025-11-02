from typing import List, Optional, Dict, Any

from pydantic import BaseModel, Field
from datetime import datetime
from app.models.core.condition import Location

# 响应模型
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