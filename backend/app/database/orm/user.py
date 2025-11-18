from sqlalchemy import Column, String, Integer, DateTime, Boolean, Text
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime

from database.config import Base

class User(Base):
    """用户模型"""
    __tablename__ = "users"

    id =            Column(Integer,       primary_key=True, autoincrement=True, comment="用户ID")

    username =      Column(String(50),    unique=True,        nullable=False, index=True, comment="用户名")
    email =         Column(String(100),   unique=True,        nullable=False, index=True, comment="邮箱")
    password_hash = Column(String(255),                       nullable=False, comment="密码哈希")
    nickname =      Column(String(100),                       nullable=False, comment="昵称")

    user_type =     Column(String(20),    default="student",  nullable=False, comment="用户类型: student, teacher, alumni")
    userrole =      Column(String(20),    default="user",     nullable=False, comment="用户角色: user, admin")
    is_active =     Column(Boolean,       default=True,       nullable=False, comment="是否激活")
    is_verified =   Column(Boolean,       default=False,      nullable=False, comment="是否已验证")
    created_at =    Column(DateTime,      default=func.now(), nullable=False, comment="创建时间")
    updated_at =    Column(DateTime,      default=func.now(), nullable=False, onupdate=func.now(),  comment="更新时间")
    
    avatar_url =    Column(String(500),                       nullable=True, comment="头像URL")
    bio =           Column(Text,                              nullable=True, comment="个人简介")
    campus_id =     Column(String(20),                        nullable=True, index=True, comment="校园ID/学号")
    last_login_at = Column(DateTime,                          nullable=True, comment="最后登录时间")

    # 关系
    capsules =       relationship("Capsule", back_populates="user", cascade="all, delete-orphan")
    unlock_records = relationship("UnlockRecord", back_populates="user", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<User(id={self.id}, username='{self.username}', email='{self.email}')>"
    
    # def to_dict(self):
    #     """将用户模型转换为字典"""
    #     return {
    #         "id": self.id,
    #         "username": self.username,
    #         "userrole": self.userrole,
    #         "email": self.email,
    #         "nickname": self.nickname,
    #         "avatar_url": self.avatar_url,
    #         "bio": self.bio,
    #         "campus_id": self.campus_id,
    #         "user_type": self.user_type,
    #         "is_active": self.is_active,
    #         "is_verified": self.is_verified,
    #         "created_at": self.created_at,
    #         "updated_at": self.updated_at,
    #         "last_login_at": self.last_login_at
    #     }

    def update_last_login(self):
        """更新最后登录时间"""
        self.last_login_at = datetime.now()


class UserFriend(Base):
    """用户好友关系模型"""
    __tablename__ = "user_friends"

    id = Column(Integer, primary_key=True, autoincrement=True, comment="关系ID")
    user_id = Column(Integer, nullable=False, index=True, comment="用户ID")
    friend_id = Column(Integer, nullable=False, index=True, comment="好友ID")
    status = Column(String(20), nullable=False, default="pending", comment="关系状态: pending, accepted, blocked")
    created_at = Column(DateTime, default=func.now(), nullable=False, comment="创建时间")
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now(), nullable=False, comment="更新时间")

    def __repr__(self):
        return f"<UserFriend(user_id={self.user_id}, friend_id={self.friend_id}, status='{self.status}')>"
    

    # def to_dict(self):
    #     """将用户好友关系模型转换为字典"""
    #     return {
    #         "id": self.id,
    #         "user_id": self.user_id,
    #         "friend_id": self.friend_id,
    #         "status": self.status,
    #         "created_at": self.created_at,
    #         "updated_at": self.updated_at
    #     }