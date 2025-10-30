from sqlalchemy import Column, Integer, String, Text, DateTime, Float, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.models.database.config import Base

class CapsuleInteraction(Base):
    """胶囊交互记录"""
    __tablename__ = "capsule_interactions"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="交互记录ID")
    unlock_record_id = Column(Integer, ForeignKey("unlock_records.id"), nullable=False, index=True, comment="解锁记录ID")
    interaction_type = Column(String(50), nullable=False, comment="交互类型: view, like, comment, share")

    # 评论相关
    comment_content = Column(Text, nullable=True, comment="评论内容")
    comment_rating = Column(Integer, nullable=True, comment="评分（1-5星）")

    # 分享相关
    share_platform = Column(String(50), nullable=True, comment="分享平台")
    share_url = Column(String(500), nullable=True, comment="分享URL")

    # # 位置信息
    # interaction_latitude = Column(Float, nullable=True, comment="交互时的纬度")
    # interaction_longitude = Column(Float, nullable=True, comment="交互时的经度")

    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    # 关系
    unlock_record = relationship("UnlockRecord", back_populates="interactions")

    def __repr__(self):
        return f"<CapsuleInteraction(id={self.id}, unlock_record_id={self.unlock_record_id}, type='{self.interaction_type}')>"