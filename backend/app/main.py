"""
时光胶囊·校园 - FastAPI 应用入口
"""
from fastapi import FastAPI, HTTPException, Query, Path, UploadFile, File, Request
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware # 导入 CORS 中间件
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY
import uvicorn
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

=======
from app.logger import get_logger, app_logger
from app.logger.config import config_manager
from app.database.database import create_tables
from app.api.v1 import *
>>>>>>> cf3e798be24f586905d9e7a260af2b9644249c44

app_logger.info("======================================================================")
app_logger.info(f"日志配置：{config_manager.get_config()}")
#=============================================================#
# 创建 FastAPI 应用实例
app_logger.info("创建应用程序实例")
app = FastAPI(
    title="时光胶囊·校园",
    description="基于地理位置与时间触发的校园记忆数字化平台",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)
<<<<<<< HEAD

# --- 关键：配置 CORS 中间件以允许前端访问 ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,                      # 允许的来源列表
    allow_credentials=True,                     # 允许携带 Cookies/Authorization Header
    allow_methods=["*"],                        # 允许所有 HTTP 方法
    allow_headers=["*"],                        # 允许所有 HTTP 请求头
)


# -----------------------------------------------------------
# 🔴 关键修改：注册 RequestValidationError 异常处理程序
# -----------------------------------------------------------


@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    捕获并格式化 Pydantic 验证错误 (422 Unprocessable Entity)，返回详细错误信息。
    """
    # 打印详细错误到后端日志，便于排查
    print(f"Pydantic 验证错误发生在: {request.url}")
    print("详细错误列表:", exc.errors()) 

    # 返回标准的 422 响应，包含详细的错误数组
    return JSONResponse(
        status_code=HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "success": False,
            "message": "请求体数据验证失败 (422 Unprocessable Entity)。请检查详细信息。",
            "detail": exc.errors(), # 将 Pydantic 的详细错误列表返回
        },
    )

# -----------------------------------------------------------

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
=======
app_logger.info("FastAPI 应用实例创建完成")
#=============================================================#
# 注册 API 路由
app_logger.info("开始注册 API 路由")
>>>>>>> cf3e798be24f586905d9e7a260af2b9644249c44
@app.get("/")
async def root():
    """根路径 - 返回应用信息"""
    app_logger.debug("访问根路径")
    return {
        "message": "欢迎使用时光胶囊·校园 API",
        "version": "1.0.0",
        "docs": "/docs",
    }
router_count = 0
routes = {
    "admin":       admin_router,       "auth": auth_router,    "capsule": capsule_router, 
    "interaction": interaction_router, "user": user_router,    "friend":  friend_router,  
    "report":      report_router,      "unlock": unlock_router,"upload": upload_router,
}
for name, router in routes.items():
    try:
        app.include_router(router, prefix=f"/api/v1")
        app_logger.info(f"已注册路由: {name}")
        router_count += 1
    except Exception as e:
        app_logger.error(f"注册路由失败: {name}", exc_info=True)
app_logger.info(f"API 路由注册完成，共注册 {router_count} 个路由模块")
#=============================================================#
app.add_middleware(
    CORSMiddleware,
    allow_origins=["127.0.0.1"],  # 允许的前端域名
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有方法
    allow_headers=["*"],  # 允许所有头（或明确写 ["Content-Type", "Authorization"]）
)

#=============================================================#
# 配置静态文件服务
UPLOAD_DIR = os.getenv('UPLOAD_DIR', './uploads')
app_logger.info(f"配置上传目录: {UPLOAD_DIR}")

if os.path.exists(UPLOAD_DIR):
    # 挂载上传目录作为静态文件服务
    app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
    app_logger.info(f"静态文件服务已挂载: {UPLOAD_DIR} -> /uploads")
else:
    # 如果上传目录不存在，创建它
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")
    app_logger.info(f"创建并挂载上传目录: {UPLOAD_DIR} -> /uploads")
#=============================================================#
# 创建数据库表
app_logger.info("开始初始化数据库表")
from app.database.orm import *
create_tables()
app_logger.info("数据库表初始化完成")
#=============================================================#
if __name__ == "__main__":
    app_logger.info("应用程序启动中...")
    try:
        # 启动服务器
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 8000))
        app_logger.info(f"启动服务器: {host}:{port}")
        uvicorn.run(
            "main:app",
            host=host,
            port=port,
            reload=True
        )
    except Exception as e:
        app_logger.error(f"应用程序启动失败: {str(e)}", exc_info=True)
        raise

<<<<<<< HEAD
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
=======
>>>>>>> cf3e798be24f586905d9e7a260af2b9644249c44
