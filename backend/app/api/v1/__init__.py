# 导入所有路由模块
from .routes import *

# 导入胶囊相关路由
from .capsule.capsule import capsule_router

# unlock功能暂时禁用，等待其他团队成员实现
try:
    from .capsule.unlock import unlock_router
except ImportError:
    unlock_router = None

