from enum import Enum

class CapsuleStatus(str, Enum):
    """胶囊状态枚举"""
    LOCKED = "locked"
    UNLOCKED = "unlocked"
    EXPIRED = "expired"

class Visibility(str, Enum):
    """可见性枚举"""
    PRIVATE = "private"
    FRIENDS = "friends"
    CAMPUS = "campus"

class ContentType(str, Enum):
    """内容类型枚举"""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    MIXED = "mixed"


class Capsule:
    """胶囊主类"""
    pass