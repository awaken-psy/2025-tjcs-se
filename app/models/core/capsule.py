from enum import Enum
from typing import Set, Optional, List
from dataclasses import dataclass, field
from datetime import datetime


class CapsuleStatus(str, Enum):
    """胶囊状态枚举"""
    LOCKED = "locked"
    UNLOCKED = "unlocked"
    EXPIRED = "expired"


class Visibility(str, Enum):
    """可见性枚举"""
    PRIVATE = "private"  # 仅所有者可见
    FRIENDS = "friends"  # 好友可见
    CAMPUS = "campus"    # 校园公开


class ContentType(str, Enum):
    """内容类型枚举"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    MIXED = "mixed"


@dataclass
class Capsule:
    """胶囊主类 - 与用户关联"""
    capsule_id: str  # 胶囊唯一ID
    owner_id: str  # 所有者ID（用户ID）
    title: str  # 标题
    description: Optional[str] = None  # 描述
    content: Optional[str] = None  # 内容
    status: CapsuleStatus = CapsuleStatus.LOCKED  # 状态
    visibility: Visibility = Visibility.PRIVATE  # 可见性
    content_type: ContentType = ContentType.TEXT  # 内容类型
    created_at: datetime = field(default_factory=datetime.now)  # 创建时间
    updated_at: datetime = field(default_factory=datetime.now)  # 更新时间
    unlock_time: Optional[datetime] = None  # 解锁时间
    unlock_location: Optional[tuple] = None  # 解锁位置（lat, lng）
    unlock_radius: int = 100  # 解锁半径（米）
    like_count: int = 0  # 点赞数
    comment_count: int = 0  # 评论数
    unlocked_by: Set[str] = field(default_factory=set)  # 已解锁的用户ID集合
    
    def is_owner(self, user_id: str) -> bool:
        """检查用户是否为所有者"""
        return self.owner_id == user_id
    
    def can_view_by(self, user_id: str, is_admin: bool = False) -> bool:
        """
        检查用户是否可以查看胶囊
        
        Args:
            user_id: 用户ID
            is_admin: 是否为管理员
        
        Returns:
            是否可以查看
        """
        # 管理员可以查看所有胶囊
        if is_admin:
            return True
        
        # 所有者可以查看自己的胶囊
        if self.is_owner(user_id):
            return True
        
        # 根据可见性规则判断
        if self.visibility == Visibility.PRIVATE:
            return False
        elif self.visibility == Visibility.CAMPUS:
            return True
        elif self.visibility == Visibility.FRIENDS:
            # TODO: 检查是否为好友关系
            return True
        
        return False
    
    def can_edit_by(self, user_id: str, is_admin: bool = False) -> bool:
        """
        检查用户是否可以编辑胶囊
        
        Args:
            user_id: 用户ID
            is_admin: 是否为管理员
        
        Returns:
            是否可以编辑
        """
        # 管理员可以编辑所有胶囊
        if is_admin:
            return True
        
        # 只有所有者可以编辑
        return self.is_owner(user_id)
    
    def can_delete_by(self, user_id: str, is_admin: bool = False) -> bool:
        """
        检查用户是否可以删除胶囊
        
        Args:
            user_id: 用户ID
            is_admin: 是否为管理员
        
        Returns:
            是否可以删除
        """
        # 管理员可以删除所有胶囊
        if is_admin:
            return True
        
        # 只有所有者可以删除
        return self.is_owner(user_id)
    
    def is_unlocked_by(self, user_id: str) -> bool:
        """检查用户是否已解锁该胶囊"""
        return user_id in self.unlocked_by
    
    def mark_unlocked_by(self, user_id: str):
        """标记用户已解锁该胶囊"""
        self.unlocked_by.add(user_id)
        self.status = CapsuleStatus.UNLOCKED