from sqlalchemy import Column, String, Integer, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from sqlalchemy.sql.sqltypes import Boolean

from ..database import Base

class UnlockCondition(Base):
    """解锁条件主模型"""
    __tablename__ = "unlock_conditions"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="解锁条件ID")
    capsule_id = Column(Integer, ForeignKey("capsules.id", ondelete="CASCADE"), nullable=False, unique=True, comment="胶囊ID")

    # 解锁条件类型: private, password, public
    condition_type = Column(String(20), nullable=False, default="private", comment="解锁条件类型: private, password, public")

    # 密码解锁
    password = Column(String(255), nullable=True, comment="解锁密码")

    # 位置条件
    trigger_latitude = Column(Float, nullable=True, comment="触发纬度")
    trigger_longitude = Column(Float, nullable=True, comment="触发经度")
    radius_meters = Column(Integer, nullable=True, default=100, comment="触发半径（米）")

    # 时间条件
    unlockable_time = Column(DateTime, nullable=True, comment="可解锁的最早时间")

    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    # 关系
    capsule = relationship("Capsule", back_populates="unlock_conditions")

    def __repr__(self):
        return f"<UnlockCondition(id={self.id}, capsule_id={self.capsule_id}, condition_type='{self.condition_type}')>"

    def to_dict(self):
        return {
            "id": self.id,
            "type": self.condition_type,
            "password": self.password,
            "radius": self.radius_meters,
            "unlockable_time": self.unlockable_time.isoformat() if self.unlockable_time is not None else None,
            "location": {
                "latitude": self.trigger_latitude,
                "longitude": self.trigger_longitude,
                "address": None
            } if self.trigger_latitude is not None and self.trigger_longitude is not None else None,
            "is_unlocked": False  # 需要从解锁记录中查询
        }


# class LocationHistory(Base):
#     """用户位置历史记录"""
#     __tablename__ = "location_history"
#
#     id = Column(Integer, primary_key=True, autoincrement=True, comment="位置记录ID")
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
#     latitude = Column(Float, nullable=False, comment="纬度")
#     longitude = Column(Float, nullable=False, comment="经度")
#     accuracy = Column(Float, nullable=True, comment="定位精度（米）")
#     altitude = Column(Float, nullable=True, comment="海拔高度")
#     address = Column(String(500), nullable=True, comment="详细地址")
#     recorded_at = Column(DateTime, default=func.now(), nullable=False, comment="记录时间")
#
#     def __repr__(self):
#         return f"<LocationHistory(user_id={self.user_id}, lat={self.latitude}, lon={self.longitude})>"
#
#
# class TimeConditionLog(Base):
#     """时间条件检查日志"""
#     __tablename__ = "time_condition_logs"
#
#     id = Column(Integer, primary_key=True, autoincrement=True, comment="日志ID")
#     capsule_id = Column(Integer, ForeignKey("capsules.id"), nullable=False, index=True, comment="胶囊ID")
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
#     check_time = Column(DateTime, nullable=False, comment="检查时间")
#     unlock_time = Column(DateTime, nullable=True, comment="解锁时间")
#     end_time = Column(DateTime, nullable=True, comment="结束时间")
#     is_met = Column(Boolean, nullable=False, comment="是否满足条件")
#     remaining_time = Column(String(100), nullable=True, comment="剩余时间")
#     created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
#
#     def __repr__(self):
#         return f"<TimeConditionLog(capsule_id={self.capsule_id}, user_id={self.user_id}, is_met={self.is_met})>"
#
#
# class LocationConditionLog(Base):
#     """位置条件检查日志"""
#     __tablename__ = "location_condition_logs"
#
#     id = Column(Integer, primary_key=True, autoincrement=True, comment="日志ID")
#     capsule_id = Column(Integer, ForeignKey("capsules.id"), nullable=False, index=True, comment="胶囊ID")
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
#     user_latitude = Column(Float, nullable=False, comment="用户纬度")
#     user_longitude = Column(Float, nullable=False, comment="用户经度")
#     trigger_latitude = Column(Float, nullable=False, comment="触发纬度")
#     trigger_longitude = Column(Float, nullable=False, comment="触发经度")
#     distance_meters = Column(Float, nullable=False, comment="距离（米）")
#     radius_meters = Column(Integer, nullable=False, comment="触发半径（米）")
#     is_met = Column(Boolean, nullable=False, comment="是否满足条件")
#     created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
#
#     def __repr__(self):
#         return f"<LocationConditionLog(capsule_id={self.capsule_id}, user_id={self.user_id}, distance={self.distance_meters}m)>"
#
#
# class CombinedConditionLog(Base):
#     """组合条件检查日志"""
#     __tablename__ = "combined_condition_logs"
#
#     id = Column(Integer, primary_key=True, autoincrement=True, comment="日志ID")
#     capsule_id = Column(Integer, ForeignKey("capsules.id"), nullable=False, index=True, comment="胶囊ID")
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
#     time_condition_met = Column(Boolean, nullable=False, comment="时间条件是否满足")
#     location_condition_met = Column(Boolean, nullable=False, comment="位置条件是否满足")
#     all_conditions_met = Column(Boolean, nullable=False, comment="所有条件是否满足")
#     met_conditions = Column(JSON, nullable=True, comment="满足的条件列表")
#     unmet_conditions = Column(JSON, nullable=True, comment="未满足的条件列表")
#     created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
#
#     def __repr__(self):
#         return f"<CombinedConditionLog(capsule_id={self.capsule_id}, user_id={self.user_id}, all_met={self.all_conditions_met})>"