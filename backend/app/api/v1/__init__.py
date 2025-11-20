from fastapi import APIRouter

# 导入所有路由模块
try:
    from .routes import *
except ImportError:
    pass

# Import interface routers
try:
    from .admin import router as admin_router
    from .authentication import router as auth_router
    from .capsules import router as capsule_router
    from .unlock import router as unlock_router
    from .interactions import router as interaction_router
    from .users import router as user_router
    from .friends import router as friend_router
    from .upload import router as upload_router
    from .reports import router as report_router
except ImportError as e:
    print(f"Import warning: {e}")
    admin_router = auth_router = capsule_router = unlock_router = None
    interaction_router = user_router = friend_router = upload_router = report_router = None

# 导入胶囊相关路由（保持向后兼容）
try:
    from .capsule.capsule import capsule_router as legacy_capsule_router
except ImportError:
    legacy_capsule_router = None

# unlock功能暂时禁用，等待其他团队成员实现
try:
    from .capsule.unlock import unlock_router as legacy_unlock_router
except ImportError:
    legacy_unlock_router = None

# 使用新的路由器，如果不存在则使用旧的
capsule_router = capsule_router or legacy_capsule_router
unlock_router = unlock_router or legacy_unlock_router

# Export all routers
__all__ = [
    'admin_router',
    'auth_router',
    'capsule_router',
    'unlock_router',
    'interaction_router',
    'user_router',
    'friend_router',
    'upload_router',
    'report_router'
]

