"""
时光胶囊·校园 - FastAPI 应用入口

这个文件是整个后端服务的启动文件，负责所有的初始化工作，包括加载配置、
配置中间件、注册路由、初始化数据库连接和启动 uvicorn 服务器。
"""
import os
import sys
from fastapi import FastAPI, HTTPException, Query, Path, UploadFile, File, Request
from fastapi.staticfiles import StaticFiles # 用于挂载静态文件目录 (如上传的图片)
from fastapi.middleware.cors import CORSMiddleware # 导入 CORS 中间件，解决跨域问题
from fastapi.exceptions import RequestValidationError # 用于处理请求体数据验证失败的异常
import mimetypes

# 导入自定义的日志模块
from app.logger import get_logger, app_logger
from app.logger.config import config_manager
app_logger.info("\n================================重启分隔线=================================")
app_logger.info(f"日志配置：{config_manager.get_config_as_str()}")
from fastapi.responses import JSONResponse
from starlette.status import HTTP_422_UNPROCESSABLE_ENTITY # HTTP 422 状态码
import uvicorn # ASGI 服务器，用于运行 FastAPI 应用
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel # 用于类型提示和可能未使用的导入
from dotenv import load_dotenv # 用于加载 .env 文件中的环境变量
from app.services import create_admin

# 加载环境变量
load_dotenv()

# ------------------------------------------------------------------
# 1. 路径修正与内部模块导入
# ------------------------------------------------------------------
# 确保项目根目录在 Python 路径中，以便进行绝对导入 (例如: from app.api...)
# 你的 Docker 容器工作目录是 /app
if os.path.dirname(os.path.abspath(__file__)) not in sys.path:
    # 这一段在 Docker 中可能不需要，因为 Dockerfile 或 compose 文件已经处理了 PYTHONPATH
    # 但是保留下来以防在本地直接运行
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# 允许跨域请求的来源列表
# 请根据你前端项目的实际运行地址进行修改！
# 默认假设前端在 localhost:8080
origins = [
    "http://localhost:8080",  # Vue CLI 默认地址
    "http://127.0.0.1:8080",
]


# 导入数据库初始化函数
from app.database.database import create_tables
# 导入所有 v1 版本的 API 路由模块
from app.api.v1 import (
    admin_router,
    auth_router,
    capsule_router,
    hub_router,
    unlock_router,
    interaction_router,
    user_router,
    friend_router,
    upload_router,
    report_router,
    test_router,
    event_router
)


# ------------------------------------------------------------------
# 2. FastAPI 实例创建与配置
# ------------------------------------------------------------------
#=============================================================#
# 创建 FastAPI 应用实例
app_logger.info("创建应用程序实例")
app = FastAPI(
    title="时光胶囊·校园", # 应用名称，显示在 OpenAPI 文档 (Swagger UI) 顶部
    description="基于地理位置与时间触发的校园记忆数字化平台", # 应用描述
    version="1.0.0", # 应用版本
    docs_url="/docs", # Swagger UI 文档的路径
    redoc_url="/redoc", # ReDoc 文档的路径
    openapi_url="/openapi.json" # OpenAPI 规范文件的路径
)

# -----------------------------------------------------------
# 3. 中间件配置 (CORS)
# -----------------------------------------------------------
# --- 关键：配置 CORS 中间件以允许前端访问 ---
# 这一段配置允许来自指定来源 (origins) 的前端应用访问后端 API，解决跨域问题。
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,                      # 允许的来源列表（上面定义的）
    allow_credentials=True,                     # 允许携带 Cookies、HTTP 认证或 Authorization 头部
    allow_methods=["*"],                        # 允许所有 HTTP 方法 (GET, POST, PUT, DELETE...)
    allow_headers=["*"],                        # 允许所有 HTTP 请求头
)


# -----------------------------------------------------------
# 4. 异常处理：请求体数据验证错误 (422)
# -----------------------------------------------------------
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    """
    捕获并格式化 Pydantic 验证错误 (422 Unprocessable Entity)，返回详细错误信息。
    当请求体或查询参数不符合 Pydantic/FastAPI 的类型定义时触发。
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
            "detail": exc.errors(), # 将 Pydantic 的详细错误列表返回给客户端
        },
    )



# -----------------------------------------------------------
# 5. 注册 API 路由 (第一组注册)
# -----------------------------------------------------------
# 注册 API 路由，将各个模块的路由器挂载到主应用上
# prefix="/api" 会将所有路由（如 /v1/users）挂载为 /api/v1/users
app.include_router(admin_router, prefix="/api")
app.include_router(auth_router, prefix="/api")
app.include_router(capsule_router, prefix="/api")
app.include_router(hub_router, prefix="/api")
app.include_router(unlock_router, prefix="/api")
app.include_router(interaction_router, prefix="/api")
app.include_router(user_router, prefix="/api")
app.include_router(friend_router, prefix="/api")
app.include_router(upload_router, prefix="/api")
app.include_router(report_router, prefix="/api")
app.include_router(test_router, prefix="/api")
app.include_router(event_router, prefix="/api")


# -----------------------------------------------------------
# 6. 静态文件服务配置 (第一组配置)
# -----------------------------------------------------------

# 获取当前文件 (main.py) 所在的目录路径 (即 backend/app/)
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
# 获取项目根目录 (backend/)
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)

# 确保MIME类型正确设置 - 在全局范围内添加
mimetypes.add_type('video/mp4', '.mp4')
mimetypes.add_type('video/webm', '.webm')
mimetypes.add_type('video/quicktime', '.mov')
mimetypes.add_type('video/x-msvideo', '.avi')
mimetypes.add_type('audio/mpeg', '.mp3')
mimetypes.add_type('audio/wav', '.wav')
mimetypes.add_type('audio/aac', '.aac')
mimetypes.add_type('audio/flac', '.flac')

# 配置静态文件服务，用于访问用户上传的图片、视频等文件
UPLOAD_DIR = os.getenv('UPLOAD_DIR', os.path.join(PROJECT_ROOT, 'uploads'))

class CustomStaticFiles(StaticFiles):
    """自定义静态文件处理，为视频文件添加HTTP头支持"""

    async def __call__(self, scope, receive, send):
        # 检查请求路径是否为媒体文件
        if scope["type"] == "http" and any(scope["path"].endswith(ext) for ext in ['.mp4', '.webm', '.mov', '.avi', '.mp3', '.wav']):
            # 创建自定义的send方法来添加HTTP头
            original_send = send

            async def custom_send(message):
                if message["type"] == "http.response.start":
                    # 为媒体文件添加必要的HTTP头
                    headers = list(message.get("headers", []))
                    headers.extend([
                        (b"accept-ranges", b"bytes"),
                        (b"cache-control", b"public, max-age=3600"),
                        (b"access-control-allow-origin", b"*"),
                        (b"access-control-allow-methods", b"GET, HEAD, OPTIONS"),
                        (b"access-control-allow-headers", b"Range"),
                    ])

                    # 特殊处理：对于.mp4扩展名但实际是QuickTime格式的文件，使用兼容的MIME类型
                    scope_path = scope.get("path", "")
                    if scope_path.endswith('.mp4'):
                        # 检查文件是否实际是QuickTime格式
                        try:
                            import os
                            from pathlib import Path
                            # 确保路径是字符串类型
                            directory_str = str(self.directory) if hasattr(self, 'directory') else ""
                            relative_path = scope_path.lstrip('/uploads/')
                            full_path = os.path.join(directory_str, relative_path)
                            if os.path.exists(full_path):
                                with open(full_path, 'rb') as f:
                                    header = f.read(16)
                                    if len(header) >= 16 and header[4:8] == b'ftyp' and header[8:12] == b'qt  ':
                                        # 这是一个QuickTime文件，使用更兼容的MIME类型
                                        headers = [h for h in headers if not h[0].startswith(b'content-type')]
                                        # 使用 application/octet-stream 让浏览器自动检测
                                        headers.append((b"content-type", b"application/octet-stream"))
                        except Exception as e:
                            pass  # 如果检查失败，使用默认MIME类型

                    message["headers"] = headers
                await original_send(message)

            await super().__call__(scope, receive, custom_send)
        else:
            await super().__call__(scope, receive, send)

if os.path.exists(UPLOAD_DIR):
    # 挂载上传目录作为静态文件服务，通过 /uploads/filename 访问
    app.mount("/uploads", CustomStaticFiles(directory=UPLOAD_DIR), name="uploads")
    print(f"📁 静态文件服务已挂载: {UPLOAD_DIR} -> /uploads")
else:
    # 如果上传目录不存在，创建它
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    app.mount("/uploads", CustomStaticFiles(directory=UPLOAD_DIR), name="uploads")
    print(f"📁 创建并挂载上传目录: {UPLOAD_DIR} -> /uploads")

# -----------------------------------------------------------
# 7. 根路径和路由统计
# -----------------------------------------------------------
# 根路径 (Health Check / Info Endpoint)
@app.get("/")
async def root():
    """根路径 - 返回应用信息"""
    app_logger.debug("访问根路径")
    return {
        "message": "欢迎使用时光胶囊·校园 API",
        "version": "1.0.0",
        "docs": "/docs",
    }
#=============================================================#
# 创建数据库表
app_logger.info("开始初始化数据库表")
from app.database.orm import * 
create_tables() # 调用数据库模块中的函数，创建所有 ORM 定义的数据库表
app_logger.info("数据库表初始化完成")
create_admin() # 创建管理员用户


#=============================================================#
# -----------------------------------------------------------
# 9. 应用启动入口 (Uvicorn Server)
# -----------------------------------------------------------
if __name__ == "__main__":
    app_logger.info("应用程序启动中...")
    try:
        # 获取主机和端口，优先从环境变量获取，否则使用默认值
        host = os.getenv('HOST', '0.0.0.0')
        port = int(os.getenv('PORT', 8000))
        app_logger.info(f"启动服务器: {host}:{port}")
        
        # 第一次 Uvicorn 启动调用
        uvicorn.run(
            "main:app", # 格式为 "module:app_instance_name"
            host=host,
            port=port,
            reload=True # 开启热重载（仅用于开发环境）
        )
    except Exception as e:
        app_logger.error(f"应用程序启动失败: {str(e)}", exc_info=True)
        raise

    # 仅在本地开发时运行，Docker 容器内由 docker compose up 负责启动，且数据库已初始化
    # 如果在本地直接运行，确保数据库已启动
    # create_tables()
