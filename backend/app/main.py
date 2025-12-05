import __init__
from dotenv import load_dotenv
load_dotenv()
import os
import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.logger import get_logger, app_logger
from app.logger.config import config_manager
from app.database.database import create_tables
from app.api.v1 import *

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
app_logger.info("FastAPI 应用实例创建完成")
#=============================================================#
# 注册 API 路由
app_logger.info("开始注册 API 路由")
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

