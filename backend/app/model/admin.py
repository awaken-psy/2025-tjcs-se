"""
Admin related Pydantic models
"""
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field
from enum import Enum


class Action(str, Enum):
    """审核动作枚举"""
    APPROVE = "approve"
    REJECT = "reject"


class Sort(str, Enum):
    """排序方式枚举"""
    LATEST = "latest"
    OLDEST = "oldest"
    MOST_REPORTED = "most_reported"


class Status(str, Enum):
    """处理状态枚举"""
    PENDING = "pending"
    RESOLVED = "resolved"


class TargetType(str, Enum):
    """目标类型枚举"""
    CAPSULE = "capsule"
    COMMENT = "comment"
    USER = "user"


class Reason(str, Enum):
    """举报原因枚举"""
    VIOLATION = "违规内容"
    COPYRIGHT = "侵权"
    INAPPROPRIATE = "不良信息"
    OTHER = "其他"


class PendingCapsule(BaseModel):
    """待审核胶囊模型"""
    id: str
    title: str
    creator_nickname: str
    created_at: datetime
    report_count: int
    content_preview: str | None = None


class ReportItem(BaseModel):
    """举报项模型"""
    report_id: str
    target_type: str  # "capsule", "comment", "user"
    target_id: str
    reason: str  # "违规内容", "侵权", "不良信息", "其他"
    reporter_nickname: str
    reported_at: datetime
    status: str  # "pending", "resolved"


class ReviewCapsuleRequest(BaseModel):
    """审核胶囊请求模型"""
    action: str  # "approve", "reject"
    reason: str | None = Field(None, max_length=500)


class PendingCapsulesQuery(BaseModel):
    """待审核胶囊查询参数模型"""
    page: int | None = None
    page_size: int | None = None
    sort: str | None = None  # "latest", "oldest", "most_reported"


class ReportsQuery(BaseModel):
    """举报查询参数模型"""
    status: str | None = None  # "pending", "resolved"
    page: int | None = None
    page_size: int | None = None
    target_type: str | None = None  # "capsule", "comment", "user"
    reason: str | None = None  # "违规内容", "侵权", "不良信息", "其他"


class PendingCapsulesResponse(BaseModel):
    """待审核胶囊响应模型"""
    capsules: List[PendingCapsule]


class ReportsResponse(BaseModel):
    """举报响应模型"""
    reports: List[ReportItem]