from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text, Float, ForeignKey, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from datetime import datetime

from app.models.database.config import Base

class Capsule(Base):
    """胶囊主模型"""
    __tablename__ = "capsules"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="胶囊ID")
    title = Column(String(255), nullable=False, comment="胶囊标题")
    text_content = Column(Text, nullable=True, comment="文本内容")
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="创建者用户ID")

    # 位置信息
    latitude = Column(Float, nullable=False, comment="纬度")
    longitude = Column(Float, nullable=False, comment="经度")
    address = Column(String(500), nullable=True, comment="详细地址")

    # 状态和可见性
    status = Column(String(20), nullable=False, default="locked", comment="状态: locked, unlocked, expired")
    visibility = Column(String(20), nullable=False, default="private", comment="可见性: private, friends, campus")
    content_type = Column(String(20), nullable=False, default="text", comment="内容类型: text, image, audio, mixed")

    # 时间信息
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    # 关系
    user = relationship("User", back_populates="capsules")
    media_files = relationship("CapsuleMedia", back_populates="capsule", cascade="all, delete-orphan")
    unlock_conditions = relationship("UnlockCondition", back_populates="capsule", uselist=False, cascade="all, delete-orphan")
    unlock_records = relationship("UnlockRecord", back_populates="capsule", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Capsule(id={self.id}, title='{self.title}', status='{self.status}')>"


class CapsuleMedia(Base):
    """胶囊媒体文件模型"""
    __tablename__ = "capsule_media"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="媒体文件ID")
    capsule_id = Column(Integer, ForeignKey("capsules.id"), nullable=False, index=True, comment="胶囊ID")
    file_type = Column(String(50), nullable=False, comment="文件类型")
    file_name = Column(String(255), nullable=False, comment="文件名")
    file_path = Column(String(500), nullable=False, comment="文件存储路径")
    file_size = Column(Integer, nullable=False, comment="文件大小（字节）")
    mime_type = Column(String(100), nullable=True, comment="MIME类型")
    upload_order = Column(Integer, nullable=False, default=0, comment="上传顺序")
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")

    # 关系
    capsule = relationship("Capsule", back_populates="media_files")

    def __repr__(self):
        return f"<CapsuleMedia(id={self.id}, capsule_id={self.capsule_id}, file_name='{self.file_name}')>"


# class CapsuleAccess(Base):
#     """胶囊访问权限模型"""
#     __tablename__ = "capsule_access"

#     id = Column(Integer, primary_key=True, autoincrement=True, comment="访问权限ID")
#     capsule_id = Column(Integer, ForeignKey("capsules.id"), nullable=False, index=True, comment="胶囊ID")
#     user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True, comment="用户ID")
#     access_type = Column(String(20), nullable=False, default="view", comment="访问类型: view, edit, admin")
#     granted_by = Column(Integer, ForeignKey("users.id"), nullable=False, comment="授权者用户ID")
#     granted_at = Column(DateTime, default=func.now(), nullable=False, comment="授权时间")
#     expires_at = Column(DateTime, nullable=True, comment="权限过期时间")

#     def __repr__(self):
#         return f"<CapsuleAccess(capsule_id={self.capsule_id}, user_id={self.user_id}, access_type='{self.access_type}')>"