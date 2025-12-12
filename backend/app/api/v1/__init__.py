from fastapi import APIRouter

# 导入所有路由模块

from .admin import router as admin_router
from .authentication import router as auth_router
from .capsules import router as capsule_router
from .hub import router as hub_router
from .unlock import router as unlock_router
from .interactions import router as interaction_router
from .users import router as user_router
from .friends import router as friend_router
from .upload import router as upload_router
from .reports import router as report_router
from .events import router as event_router

# 导出路由器
capsule_router = capsule_router
unlock_router = unlock_router

# Export all routers
__all__ = [
    'admin_router',
    'auth_router',
    'capsule_router',
    'hub_router',
    'unlock_router',
    'interaction_router',
    'user_router',
    'friend_router',
    'upload_router',
    'report_router',
    'event_router'
]

