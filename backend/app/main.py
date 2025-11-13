"""
时光胶囊·校园 - FastAPI 应用入口
"""
import __init__
from fastapi import FastAPI

from api.v1 import (
    auth_router,
    capsule_router,
    unlock_router,
    event_router,
    hub_router,
    map_router,
    user_router
)

# 创建 FastAPI 应用实例
app = FastAPI(
    title="时光胶囊·校园",
    description="基于地理位置与时间触发的校园记忆数字化平台",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"  # OpenAPI JSON 的访问路径（默认就是 /openapi.json）
)


# 注册 API 路由
app.include_router(auth_router, prefix="/api/v1")
app.include_router(capsule_router, prefix="/api/v1")
app.include_router(unlock_router, prefix="/api/v1")
app.include_router(event_router, prefix="/api/v1")
app.include_router(hub_router, prefix="/api/v1")
app.include_router(map_router, prefix="/api/v1")
app.include_router(user_router, prefix="/api/v1")

# 根路径
@app.get("/")
async def root():
    """根路径 - 返回应用信息"""
    return {
        "message": "欢迎使用时光胶囊·校园 API",
        "version": "1.0.0",
        "docs": "/docs"
    }


# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": "2024-10-26T10:00:00Z"  # TODO: 使用实际时间
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
