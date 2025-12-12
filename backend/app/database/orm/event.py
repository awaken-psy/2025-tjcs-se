from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.database.database import Base

# 避免循环导入
def get_user_model():
    from app.database.orm.user import User
    return User

class Event(Base):
    """活动模型"""
    __tablename__ = "events"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="活动ID")

    # 基本信息
    name = Column(String(100), nullable=False, comment="活动名称")
    description = Column(Text, nullable=False, comment="活动描述")
    date = Column(DateTime, nullable=False, comment="活动时间")
    location = Column(String(255), nullable=False, comment="活动地点")

    # 可选信息
    tags = Column(JSON, nullable=True, comment="活动标签(JSON格式)")
    cover_img = Column(String(500), nullable=True, comment="封面图片URL")

    # 创建者信息
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="创建者用户ID")

    # 时间信息
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    # 关系
    creator = relationship("User", back_populates="created_events")
    registrations = relationship("EventRegistration", back_populates="event", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Event(id={self.id}, name='{self.name}', location='{self.location}')>"

    def to_dict(self):
        """将活动模型转换为字典"""
        return {
            "id": str(self.id),
            "name": self.name,
            "description": self.description,
            "date": self.date.isoformat() if self.date else None,
            "location": self.location,
            "tags": self.tags or [],
            "cover_img": self.cover_img,
            "participant_count": len(self.registrations) if self.registrations else 0,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


class EventRegistration(Base):
    """活动报名记录模型"""
    __tablename__ = "event_registrations"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="报名记录ID")

    # 关联信息
    event_id = Column(Integer, ForeignKey("events.id"), nullable=False, index=True, comment="活动ID")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")

    # 报名时间
    registered_at = Column(DateTime, default=func.now(), nullable=False, comment="报名时间")

    # 唯一约束：一个用户只能报名一个活动一次
    __table_args__ = (
        {'mysql_charset': 'utf8mb4'},
    )

    # 关系
    event = relationship("Event", back_populates="registrations")
    user = relationship("User")

    def __repr__(self):
        return f"<EventRegistration(id={self.id}, event_id={self.event_id}, user_id={self.user_id})>"

    def to_dict(self):
        """将报名记录模型转换为字典"""
        return {
            "registration_id": str(self.id),
            "event_id": str(self.event_id),
            "user_id": str(self.user_id),
            "registered_at": self.registered_at.isoformat() if self.registered_at else None
        }