"""
File upload related Pydantic models
"""
from pydantic import BaseModel, Field


class FileUploadResponse(BaseModel):
    """文件上传响应模型"""
    file_id: str = Field(..., pattern=r"^file_[a-zA-Z0-9]+$")
    url: str
    size: int
    format: str
    thumbnail_url: str | None = None
    duration: float | None = None  # seconds for audio


class ReportRequest(BaseModel):
    """举报请求模型"""
    target_type: str  # "capsule", "comment", "user"
    target_id: str
    reason: str  # "违规内容", "侵权", "不良信息", "其他"
    description: str | None = Field(None, max_length=500)