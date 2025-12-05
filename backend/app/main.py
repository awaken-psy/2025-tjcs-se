"""
时光胶囊·校园 - FastAPI 应用入口
"""
from fastapi import FastAPI, HTTPException, Query, Path, UploadFile, File
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware # 导入 CORS 中间件
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
import os
import sys
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# --- 路径修正与初始化 ---
# 确保项目根目录在 Python 路径中，以便进行绝对导入 (例如: from app.api...)
# 你的 Docker 容器工作目录是 /app
if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    # 这一段在 Docker 中可能不需要，因为 Dockerfile 或 compose 文件已经处理了 PYTHONPATH
    # 但是保留下来以防在本地直接运行
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 使用绝对导入方式修复数据库和 API 路由的导入
from app.database.database import create_tables
from app.api.v1 import (
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

# 允许跨域请求的来源列表
# 请根据你前端项目的实际运行地址进行修改！
# 默认假设前端在 localhost:8080
origins = [
    "http://localhost:8080",  # Vue CLI 默认地址
    "http://127.0.0.1:8080",
]


# 创建 FastAPI 应用实例
app = FastAPI(
    title="时光胶囊·校园",
    description="基于地理位置与时间触发的校园记忆数字化平台",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# --- 关键：配置 CORS 中间件以允许前端访问 ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,                      # 允许的来源列表
    allow_credentials=True,                     # 允许携带 Cookies/Authorization Header
    allow_methods=["*"],                        # 允许所有 HTTP 方法
    allow_headers=["*"],                        # 允许所有 HTTP 请求头
)


# 注册 API 路由
# 确保路由的导入是成功的，否则这里可能会报错
app.include_router(admin_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(capsule_router, prefix="/api")
app.include_router(unlock_router, prefix="/api") 
app.include_router(interaction_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(friend_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(report_router, prefix="/api")


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
            "POST /api/capsules/ - 创建胶囊",
            "GET /api/capsules/my - 获取我的胶囊",
            "GET /api/capsules/{id} - 获取胶囊详情",
            "PUT /api/capsules/{id} - 编辑胶囊",
            "DELETE /api/capsules/{id} - 删除胶囊",
            "POST /api/capsules/drafts - 保存草稿",
            "GET /api/capsules/browse - 多模式浏览胶囊",
            "POST /api/upload/ - 上传文件（图片/音频）",
            "DELETE /api/upload/file/{file_id} - 删除文件"
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

    # 仅在本地开发时运行，Docker 容器内由 docker compose up 负责启动，且数据库已初始化
    # 如果在本地直接运行，确保数据库已启动
    # create_tables()

    # 修正启动入口：使用 app.main:app
    uvicorn.run(
        "app.main:app", 
        host="0.0.0.0",
        port=8000,
        reload=True
    )