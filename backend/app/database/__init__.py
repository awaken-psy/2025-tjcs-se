"""
数据库模型包
"""

# 导入所有模型
from database.orm.user import User, UserFriend
from database.orm.capsule import Capsule, CapsuleMedia
from database.orm.unlock_condition import UnlockCondition
from database.orm.unlock_record import (
    UnlockRecord, UnlockAttempt
)
from database.orm.capsule_interaction import CapsuleInteraction
from database.orm.config import get_db, create_tables, drop_tables


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

    # 数据库配置
    "get_db", "create_tables", "drop_tables"
]