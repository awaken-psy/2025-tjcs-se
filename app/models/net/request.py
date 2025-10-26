
# 请求模型
from typing import List, Optional, Dict
from models.core.condition import Location, UnlockConditions
from models.core.capsule import Visibility

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
