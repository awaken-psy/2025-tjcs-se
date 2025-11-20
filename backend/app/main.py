"""
时光胶囊·校园 - FastAPI 应用入口
"""
from fastapi import FastAPI, HTTPException, Query, Path, UploadFile, File
from fastapi.staticfiles import StaticFiles
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
import os
import sys

# 添加当前目录到Python路径，确保可以找到app模块
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
if parent_dir not in sys.path:
    sys.path.insert(0, parent_dir)

# 修复数据库导入路径
from database.database import create_tables


# 修复API路由导入路径 - 使用相对导入
try:
    from api.v1 import (
        admin_router,
        auth_router,
        capsule_router,
        unlock_router,
        interaction_router,
        user_router,
        friend_router,
        upload_router,
        report_router
    )
except ImportError as e:
    print(f"Warning: Could not import from api.v1: {e}")
    admin_router = auth_router = capsule_router = None
    unlock_router = interaction_router = user_router = None
    friend_router = upload_router = report_router = None

# 尝试导入旧的路由结构以保持兼容性
try:
    from api.v1.routes import (
        auth_router as legacy_auth_router,
        event_router,
        hub_router,
        map_router,
        user_router as legacy_user_router
    )
    # 使用新的路由器，如果不存在则使用旧的
    auth_router = auth_router or legacy_auth_router
    user_router = user_router or legacy_user_router
except ImportError as e:
    print(f"Warning: Could not import legacy routes: {e}")
    event_router = hub_router = map_router = None

# 创建 FastAPI 应用实例
app = FastAPI(
    title="时光胶囊·校园",
    description="基于地理位置与时间触发的校园记忆数字化平台",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# 注册 API 路由
if admin_router:
    app.include_router(admin_router, prefix="/api/v1")
if auth_router:
    app.include_router(auth_router, prefix="/api/v1")
if capsule_router:
    app.include_router(capsule_router, prefix="/api/v1")
if unlock_router:  # 只有在unlock_router存在时才注册
    app.include_router(unlock_router, prefix="/api/v1")
if interaction_router:
    app.include_router(interaction_router, prefix="/api/v1")
if user_router:
    app.include_router(user_router, prefix="/api/v1")
if friend_router:
    app.include_router(friend_router, prefix="/api/v1")
if upload_router:
    app.include_router(upload_router, prefix="/api/v1")
if report_router:
    app.include_router(report_router, prefix="/api/v1")

# 注册旧的路由以保持兼容性
if event_router:
    app.include_router(event_router, prefix="/api/v1")
if hub_router:
    app.include_router(hub_router, prefix="/api/v1")
if map_router:
    app.include_router(map_router, prefix="/api/v1")


# 配置静态文件服务
UPLOAD_DIR = os.getenv('UPLOAD_DIR', './uploads')
if os.path.exists(UPLOAD_DIR):
    # 挂载上传目录作为静态文件服务
    app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
    print(f"📁 静态文件服务已挂载: {UPLOAD_DIR} -> /uploads")
else:
    # 如果上传目录不存在，创建它
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
    print(f"📁 创建并挂载上传目录: {UPLOAD_DIR} -> /uploads")

# 根路径
@app.get("/")
async def root():
    """根路径 - 返回应用信息"""
    return {
        "message": "欢迎使用时光胶囊·校园 API",
        "version": "1.0.0",
        "docs": "/docs",
        "available_endpoints": [
            "POST /api/v1/capsule/create - 创建胶囊",
            "GET /api/v1/capsule/my - 获取我的胶囊",
            "GET /api/v1/capsule/detail/{id} - 获取胶囊详情",
            "POST /api/v1/capsule/edit/{id} - 编辑胶囊",
            "POST /api/v1/capsule/delete/{id} - 删除胶囊",
            "POST /api/v1/capsule/upload-img - 上传图片"
        ]
    }

# 健康检查端点
@app.get("/health")
async def health_check():
    """健康检查"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "api_version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    print("🚀 启动时光胶囊API服务...")
    print("📖 API文档地址: http://127.0.0.1:8000/docs")
    print("❤️ 健康检查地址: http://127.0.0.1:8000/health")
    print("=" * 50)

    # 创建数据库表
    create_tables()

    uvicorn.run(
        "main:app",
        host="127.0.0.1",
        port=8000,
        reload=True
    )
