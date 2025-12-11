"""
Admin related Pydantic models
"""
from datetime import datetime
from typing import List
from pydantic import BaseModel, Field
from enum import Enum


# 审核动作枚举
class Action(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"


# 排序方式枚举
class Sort(str, Enum):
    LATEST = "latest"
    MOST_REPORTED = "most_reported"
    OLDEST = "oldest"


# 举报原因枚举
class Reason(str, Enum):
    VIOLATION = "违规内容"
    INFRINGEMENT = "侵权"
    INAPPROPRIATE = "不良信息"
    OTHER = "其他"


# 处理状态枚举
class Status(str, Enum):
    PENDING = "pending"
    RESOLVED = "resolved"


# 目标类型枚举
class TargetType(str, Enum):
    CAPSULE = "capsule"
    COMMENT = "comment"
    USER = "user"


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
    target_type: TargetType
    target_id: str
    reason: Reason
    reporter_nickname: str
    reported_at: datetime
    status: Status


class ReviewCapsuleRequest(BaseModel):
    """审核胶囊请求模型"""
    action: Action
    reason: str | None = Field(None, max_length=500)


class PendingCapsulesQuery(BaseModel):
    """待审核胶囊查询参数模型"""
    page: int | None = Field(1, ge=1)
    page_size: int | None = Field(20, ge=1, le=100)
    sort: Sort | None = Sort.LATEST


class ReportsQuery(BaseModel):
    """举报查询参数模型"""
    status: Status | None = None
    page: int | None = Field(1, ge=1)
    page_size: int | None = Field(20, ge=1, le=100)
    target_type: TargetType | None = None
    reason: Reason | None = None


class PendingCapsulesResponse(BaseModel):
    """待审核胶囊响应模型"""
    capsules: List[PendingCapsule]


class ReportsResponse(BaseModel):
    """举报响应模型"""
    reports: List[ReportItem]