from sqlalchemy import Column, String, Integer, DateTime, Float, ForeignKey, JSON, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from sqlalchemy.sql.sqltypes import Boolean

from ..database import Base

class UnlockRecord(Base):
    """解锁记录主模型"""
    __tablename__ = "unlock_records"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="解锁记录ID")
    capsule_id = Column(Integer, ForeignKey("capsules.id"), nullable=False, index=True, comment="胶囊ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")

    # 解锁相关信息
    unlock_method = Column(String(50), nullable=False, comment="解锁方式: time, location, combined")
    # unlock_conditions_met = Column(JSON, nullable=False, comment="满足的解锁条件列表")
    unlock_location_latitude = Column(Float, nullable=True, comment="解锁时的纬度")
    unlock_location_longitude = Column(Float, nullable=True, comment="解锁时的经度")
    unlock_address = Column(String(500), nullable=True, comment="解锁时的地址")

    # 时间信息
    unlocked_at = Column(DateTime, default=func.now(), nullable=False, comment="解锁时间")
    # session_expires_at = Column(DateTime, nullable=True, comment="会话过期时间")

    # 统计信息
    view_count = Column(Integer, default=0, nullable=False, comment="查看次数")
    last_viewed_at = Column(DateTime, nullable=True, comment="最后查看时间")

    # 关系
    capsule = relationship("Capsule", back_populates="unlock_records")
    user = relationship("User")
    interactions = relationship("CapsuleInteraction", back_populates="unlock_record", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<UnlockRecord(id={self.id}, capsule_id={self.capsule_id}, user_id={self.user_id})>"
    
    # def to_dict(self):
    #     return {
    #         "id": self.id,
    #         "capsule_id": self.capsule_id,
    #         "user_id": self.user_id,
    #         "unlock_method": self.unlock_method,
    #         "unlock_location_latitude": self.unlock_location_latitude,
    #         "unlock_location_longitude": self.unlock_location_longitude,
    #         "unlock_address": self.unlock_address,
    #         "unlocked_at": self.unlocked_at,
    #         "view_count": self.view_count,
    #         "last_viewed_at": self.last_viewed_at,
    #     }





# class CapsuleViewAnalytics(Base):
#     """胶囊查看分析数据"""
#     __tablename__ = "capsule_view_analytics"
#
#     id = Column(Integer, primary_key=True, autoincrement=True, comment="分析记录ID")
#     capsule_id = Column(Integer, ForeignKey("capsules.id"), nullable=False, index=True, comment="胶囊ID")
#     date = Column(DateTime, nullable=False, index=True, comment="统计日期")
#
#     # 统计指标
#     total_views = Column(Integer, default=0, nullable=False, comment="总查看次数")
#     unique_viewers = Column(Integer, default=0, nullable=False, comment="独立查看用户数")
#     avg_view_duration = Column(Float, default=0, nullable=False, comment="平均查看时长（秒）")
#     completion_rate = Column(Float, default=0, nullable=False, comment="完成率（0-1）")
#
#     # 地理位置分布
#     view_by_location = Column(JSON, nullable=True, comment="按地理位置分布的查看次数")
#
#     created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
#     updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")
#
#     def __repr__(self):
#         return f"<CapsuleViewAnalytics(capsule_id={self.capsule_id}, date={self.date}, views={self.total_views})>"


class UnlockAttempt(Base):
    """解锁尝试记录"""
    __tablename__ = "unlock_attempts"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="尝试记录ID")
    capsule_id = Column(Integer, ForeignKey("capsules.id"), nullable=False, index=True, comment="胶囊ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")

    # 尝试信息
    attempt_location_latitude = Column(Float, nullable=True, comment="尝试时的纬度")
    attempt_location_longitude = Column(Float, nullable=True, comment="尝试时的经度")
    attempt_time = Column(DateTime, nullable=False, comment="尝试时间")

    # 条件检查结果
    time_condition_met = Column(Boolean, nullable=False, comment="时间条件是否满足")
    location_condition_met = Column(Boolean, nullable=False, comment="位置条件是否满足")
    all_conditions_met = Column(Boolean, nullable=False, comment="所有条件是否满足")

    # 距离信息
    distance_to_trigger = Column(Float, nullable=True, comment="到触发点的距离（米）")

    # 失败原因
    failure_reason = Column(String(200), nullable=True, comment="失败原因")

    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")

    def __repr__(self):
        return f"<UnlockAttempt(capsule_id={self.capsule_id}, user_id={self.user_id}, success={self.all_conditions_met})>"
    
    # def to_dict(self):
    #     return {
    #         "id": self.id,
    #         "capsule_id": self.capsule_id,
    #         "user_id": self.user_id,
    #         "attempt_location_latitude": self.attempt_location_latitude,
    #         "attempt_location_longitude": self.attempt_location_longitude,
    #         "attempt_time": self.attempt_time.strftime,
    #         "time_condition_met": self.time_condition_met,
    #         "location_condition_met": self.location_condition_met,
    #         "all_conditions_met": self.all_conditions_met,
    #         "distance_to_trigger": self.distance_to_trigger,
    #         "failure_reason": self.failure_reason,
    #         "created_at": self.created_at.strftime,
    #     }


# class CapsuleNotification(Base):
#     """胶囊相关通知"""
#     __tablename__ = "capsule_notifications"
#
#     id = Column(Integer, primary_key=True, autoincrement=True, comment="通知ID")
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
#     capsule_id = Column(Integer, ForeignKey("capsules.id"), nullable=True, index=True, comment="胶囊ID")
#
#     # 通知内容
#     notification_type = Column(String(50), nullable=False, comment="通知类型: unlock_available, friend_unlocked, capsule_expired, new_comment")
#     title = Column(String(200), nullable=False, comment="通知标题")
#     message = Column(Text, nullable=False, comment="通知内容")
#
#     # 状态
#     is_read = Column(Boolean, default=False, nullable=False, comment="是否已读")
#     is_sent = Column(Boolean, default=False, nullable=False, comment="是否已发送")
#
#     # 时间信息
#     scheduled_at = Column(DateTime, nullable=True, comment="计划发送时间")
#     sent_at = Column(DateTime, nullable=True, comment="实际发送时间")
#     read_at = Column(DateTime, nullable=True, comment="阅读时间")
#     expires_at = Column(DateTime, nullable=True, comment="过期时间")
#
#     created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
#
#     def __repr__(self):
#         return f"<CapsuleNotification(user_id={self.user_id}, type='{self.notification_type}', is_read={self.is_read})>"