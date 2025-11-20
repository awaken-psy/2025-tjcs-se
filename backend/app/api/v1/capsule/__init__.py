# 胶囊相关API模块
from .capsule import capsule_router

# unlock功能暂时禁用，等待其他团队成员实现
try:
    from .unlock import unlock_router
except ImportError:
    unlock_router = None

__all__ = ['capsule_router', 'unlock_router']