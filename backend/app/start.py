import __init__
from app.logger import app_logger
import os
import uvicorn

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