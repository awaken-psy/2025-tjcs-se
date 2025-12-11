from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from ..database import Base
import enum


class ReportStatus(enum.Enum):
    """举报状态枚举"""
    PENDING = "pending"  # 待处理
    RESOLVED = "resolved"  # 已处理


class TargetType(enum.Enum):
    """举报目标类型枚举"""
    CAPSULE = "capsule"  # 胶囊
    COMMENT = "comment"  # 评论
    USER = "user"  # 用户


class Reason(enum.Enum):
    """举报原因枚举"""
    VIOLATION = "违规内容"  # 违规内容
    COPYRIGHT = "侵权"  # 侵权
    INAPPROPRIATE = "不良信息"  # 不良信息
    OTHER = "其他"  # 其他


class Report(Base):
    """举报记录"""
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="举报ID")

    # 举报目标
    target_type = Column(Enum(TargetType), nullable=False, comment="举报目标类型")
    target_id = Column(String(50), nullable=False, comment="举报目标ID")

    # 举报信息
    reason = Column(Enum(Reason), nullable=False, comment="举报原因")
    reason_detail = Column(Text, nullable=True, comment="举报详细说明")

    # 举报者
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False, comment="举报者ID")

    # 处理状态
    status = Column(Enum(ReportStatus), default=ReportStatus.PENDING, nullable=False, comment="处理状态")
    processor_id = Column(Integer, ForeignKey("users.id"), nullable=True, comment="处理者ID")
    process_result = Column(Text, nullable=True, comment="处理结果说明")

    # 时间戳
    reported_at = Column(DateTime, default=func.now(), nullable=False, comment="举报时间")
    processed_at = Column(DateTime, nullable=True, comment="处理时间")
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    # 关系
    reporter = relationship("User", foreign_keys=[reporter_id], back_populates="reports_made")
    processor = relationship("User", foreign_keys=[processor_id], back_populates="reports_processed")

    def __repr__(self):
        return f"<Report(id={self.id}, target_type='{self.target_type}', target_id='{self.target_id}', status='{self.status}')>"