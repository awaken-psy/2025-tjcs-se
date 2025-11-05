"""
数据库模型包
"""

# 导入所有模型
from app.models.database.user import User, UserFriend
from app.models.database.capsule import Capsule, CapsuleMedia
from app.models.database.unlock_condition import UnlockCondition
from app.models.database.unlock_record import (
    UnlockRecord, UnlockAttempt
)
from app.models.database.capsule_interaction import CapsuleInteraction

# 导出所有模型
__all__ = [
    # 用户相关
    "User", "UserFriend",

    # 胶囊相关
    "Capsule", "CapsuleMedia",

    # 解锁条件相关
    "UnlockCondition",

    # 解锁记录相关
    "UnlockRecord",  "UnlockAttempt", 

    # 交互记录相关
    "CapsuleInteraction",
]