from sqlalchemy import Column, String, Integer, DateTime, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from sqlalchemy.sql.sqltypes import Boolean

from database.config import Base

class UnlockCondition(Base):
    """解锁条件主模型"""
    __tablename__ = "unlock_conditions"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="解锁条件ID")
    capsule_id = Column(Integer, ForeignKey("capsules.id"), nullable=False, unique=True, comment="胶囊ID")
    condition_type = Column(String(20), nullable=False, comment="条件类型: time, location, combined")

    # 时间条件
    unlock_time = Column(DateTime, nullable=True, comment="解锁时间")
    end_time = Column(DateTime, nullable=True, comment="结束时间")

    # 周期解锁条件
    period_type = Column(String(20), nullable=True, comment="周期类型: daily, weekly, monthly, yearly")
    base_time = Column(DateTime, nullable=True, comment="周期基准时间")
    time_of_duration = Column(Integer, nullable=True, comment="每次持续时间（分钟）")
    period_count = Column(Integer, nullable=True, comment="循环次数")

    # 位置条件
    trigger_latitude = Column(Float, nullable=True, comment="触发纬度")
    trigger_longitude = Column(Float, nullable=True, comment="触发经度")
    radius_meters = Column(Integer, nullable=True, default=100, comment="触发半径（米）")

    # 其他条件
    # require_all_conditions = Column(Boolean, default=True, nullable=False, comment="是否需要满足所有条件")
    # max_unlock_count = Column(Integer, nullable=True, comment="最大解锁次数")

    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    # 关系
    capsule = relationship("Capsule", back_populates="unlock_conditions")

    def __repr__(self):
        return f"<UnlockCondition(id={self.id}, capsule_id={self.capsule_id}, condition_type='{self.condition_type}')>"
    
    # def to_dict(self):
    #     return {
    #         "id": self.id,
    #         "capsule_id": self.capsule_id,
    #         "condition_type": self.condition_type,
    #         "unlock_time": self.unlock_time,
    #         "end_time": self.end_time,
    #         "period_type": self.period_type,
    #         "base_time": self.base_time,
    #         "time_of_duration": self.time_of_duration,
    #         "period_count": self.period_count,
    #         "trigger_latitude": self.trigger_latitude,
    #         "trigger_longitude": self.trigger_longitude,
    #         "radius_meters": self.radius_meters,
    #         "created_at": self.created_at,
    #         "updated_at": self.updated_at,
    #     }


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