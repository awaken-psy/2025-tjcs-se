from enum import Enum
from typing import Set, Optional, List
from dataclasses import dataclass, field
from datetime import datetime
import json
from app.model.capsule import CapsuleBasic, CapsuleDetail, Location, Creator, CapsuleStats

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
    PUBLIC = "public"    # 公开 (用于兼容)


class ContentType(str, Enum):
    """内容类型枚举"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    MIXED = "mixed"


@dataclass
class Capsule:
    """胶囊主类 - 与用户关联"""
    capsule_id: Optional[int] = None  # 胶囊唯一ID（数据库自动分配）
    owner_id: str = ""  # 所有者ID（用户ID）
    title: str = ""  # 标题
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
        elif self.visibility in [Visibility.CAMPUS, Visibility.PUBLIC]:
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

    def to_api_basic(self) -> 'CapsuleBasic':
       """Domain对象转CapsuleBasic响应模型"""
       from app.model.capsule import CapsuleBasic

       # 使用类型转换函数处理可见性和状态
       api_visibility = convert_visibility_for_frontend(self.visibility.value)
       api_status = convert_status_for_frontend(self.status.value)

       # 转换ID为字符串，确保不为None
       capsule_id_str = convert_capsule_id_to_string(self.capsule_id) or ""

       # 提取经纬度信息用于地图功能
       latitude = None
       longitude = None
       if self.unlock_location and len(self.unlock_location) >= 2:
           latitude = self.unlock_location[0]
           longitude = self.unlock_location[1]

       return CapsuleBasic(
            id=capsule_id_str,  # 转换为字符串ID
            title=self.title,
            visibility=api_visibility,
            status=api_status,
            created_at=self.created_at,
            content_preview=self.description,
            cover_image="",  # 确保不是None
            unlock_count=len(self.unlocked_by),
            like_count=self.like_count,
            comment_count=self.comment_count,
            latitude=latitude,  # 添加经纬度信息
            longitude=longitude
        )

    def to_api_detail(self, user) -> 'CapsuleDetail':
        """Domain对象转CapsuleDetail响应模型"""
        # 转换位置信息 - 标准3字段格式
        location = None
        if self.unlock_location and len(self.unlock_location) == 3:
            location = Location(
                latitude=self.unlock_location[0],   # latitude
                longitude=self.unlock_location[1],  # longitude
                address=self.unlock_location[2]     # address
            )
    
         # 转换创建者信息
        nickname = getattr(user, 'nickname', None) or getattr(user, 'username', None) or '匿名用户'
        avatar_url = getattr(user, 'avatar_url', None) or ""  # 确保avatar不为null
        creator = Creator(
            user_id=int(self.owner_id),
            nickname=nickname,
            avatar=avatar_url
        )
    
        # 转换统计信息
        stats = CapsuleStats(
            view_count=0,  # TODO: 实现访问统计
            like_count=self.like_count,
            comment_count=self.comment_count,
            unlock_count=len(self.unlocked_by),
            is_liked=False,  # TODO: 实现点赞状态
            is_collected=False  # TODO: 实现收藏状态
        )
    
    # 根据content_type推断标签
        tags = []
        if self.content_type == ContentType.IMAGE:
            tags = ["图片", "image"]
        elif self.content_type == ContentType.AUDIO:
            tags = ["音频", "audio"]
        elif self.content_type == ContentType.MIXED:
            tags = ["混合", "mixed"]
    
        # 使用类型转换函数处理可见性和状态
        api_visibility = convert_visibility_for_frontend(self.visibility.value)
        api_status = convert_status_for_frontend(self.status.value)

        # 转换ID为字符串，确保不为None
        capsule_id_str = convert_capsule_id_to_string(self.capsule_id) or ""

        # 创建默认的解锁条件对象
        from app.model.capsule import UnlockConditions
        unlock_conditions = UnlockConditions(
            type="time",
            value=self.unlock_time.isoformat() if self.unlock_time else None,
            radius=self.unlock_radius,
            event_id=None,
            is_unlocked=False  # 默认未解锁状态
        )

        return CapsuleDetail(
            id=capsule_id_str,  # 转换为字符串ID
            title=self.title,
            content=self.content or "",
            visibility=api_visibility,
            status=api_status,
            created_at=self.created_at,
            tags=tags,
            location=location,
            unlock_conditions=unlock_conditions,  # 使用真实的解锁条件
            media_files=[],  # TODO: 从媒体文件表获取
            creator=creator,
            stats=stats,
            updated_at=self.updated_at
        )


# ==================== 类型转换工具函数 ====================

def convert_capsule_id_to_string(capsule_id):
    """将胶囊ID转换为字符串类型（用于API响应）"""
    return str(capsule_id) if capsule_id is not None else None

def convert_capsule_id_from_string(capsule_id_str):
    """将字符串类型的胶囊ID转换为整数（用于数据库操作）"""
    if capsule_id_str is None:
        return None
    try:
        return int(capsule_id_str)
    except (ValueError, TypeError):
        return None

def convert_status_for_frontend(status: str) -> str:
    """
    将胶囊状态转换为前端期望的枚举值

    Args:
        status: 数据库状态值 (locked, unlocked, draft, expired)

    Returns:
        str: 前端期望的状态值 (draft, pending, published)
    """
    status_mapping = {
        "locked": "published",      # 已锁定状态对应前端已发布
        "unlocked": "published",    # 已解锁状态对应前端已发布
        "draft": "draft",           # 草稿状态保持不变
        "expired": "published",     # 已过期状态对应前端已发布
        "pending": "pending"        # 待审核状态保持不变
    }
    return status_mapping.get(status, "published")

def convert_status_from_frontend(status: str) -> str:
    """
    将前端状态值转换为数据库期望的状态值

    Args:
        status: 前端状态值 (draft, pending, published)

    Returns:
        str: 数据库期望的状态值 (locked, draft, expired, pending)
    """
    status_mapping = {
        "published": "locked",      # 前端已发布对应数据库锁定状态
        "draft": "draft",           # 草稿状态保持不变
        "pending": "pending"        # 待审核状态保持不变
    }
    return status_mapping.get(status, "locked")

def convert_visibility_for_frontend(visibility: str) -> str:
    """
    将可见性转换为前端期望的值

    Args:
        visibility: 数据库可见性值 (private, friends, campus, public)

    Returns:
        str: 前端期望的可见性值 (private, friends, public)
    """
    visibility_mapping = {
        "private": "private",       # 私有保持不变
        "friends": "friends",       # 好友可见保持不变
        "campus": "public",         # 校园公开转换为前端公开
        "public": "public"          # 🔥 修复：已经是public的保持不变
    }

    return visibility_mapping.get(visibility, "private")

def convert_visibility_from_frontend(visibility: str) -> str:
    """
    将前端可见性值转换为数据库期望的值

    Args:
        visibility: 前端可见性值 (private, friends, public)

    Returns:
        str: 数据库期望的可见性值 (private, friends, campus)
    """
    visibility_mapping = {
        "private": "private",       # 私有保持不变
        "friends": "friends",       # 好友可见保持不变
        "public": "campus"          # 前端公开转换为数据库校园公开
    }
    return visibility_mapping.get(visibility, "private")

def convert_capsule_basic_for_api(capsule_data):
    """
    将胶囊数据转换为API响应格式，处理类型转换

    Args:
        capsule_data: 胶囊数据字典或Pydantic模型对象

    Returns:
        dict: 转换后的胶囊数据
    """
    # 处理不同类型的数据源
    if hasattr(capsule_data, 'model_dump'):
        # Pydantic模型对象
        capsule_dict = capsule_data.model_dump()
    elif hasattr(capsule_data, '__dict__'):
        # 普通对象
        capsule_dict = vars(capsule_data)
    elif isinstance(capsule_data, dict):
        # 已经是字典
        capsule_dict = capsule_data
    else:
        # 其他类型，直接返回
        return capsule_data

    # 创建副本避免修改原数据
    result = capsule_dict.copy()

    # 转换ID为字符串
    if 'id' in result and result['id'] is not None:
        result['id'] = convert_capsule_id_to_string(result['id'])

    # 转换状态为前端格式（双重保险，因为domain可能已经转换过了）
    if 'status' in result and result['status'] is not None:
        result['status'] = convert_status_for_frontend(result['status'])

    # 转换可见性为前端格式（双重保险，因为domain可能已经转换过了）
    if 'visibility' in result and result['visibility'] is not None:
        result['visibility'] = convert_visibility_for_frontend(result['visibility'])

    # 确保cover_image不为null
    if 'cover_image' in result and result['cover_image'] is None:
        result['cover_image'] = ""

    return result

def convert_capsule_list_for_api(capsules_list):
    """
    批量转换胶囊列表为API响应格式

    Args:
        capsules_list: 胶囊数据列表

    Returns:
        list: 转换后的胶囊数据列表
    """
    return [convert_capsule_basic_for_api(capsule) for capsule in capsules_list]