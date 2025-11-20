#!/usr/bin/env python3
"""
简单的启动脚本，用于测试应用是否能正常运行
"""
import os
import sys

# 设置工作目录
backend_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, backend_dir)

print("🔧 测试基本导入...")
try:
    import fastapi
    print("✅ FastAPI 导入成功")
except ImportError as e:
    print(f"❌ FastAPI 导入失败: {e}")
    sys.exit(1)

try:
    from app.main import app
    print("✅ 应用导入成功！")
    print(f"📋 应用标题: {app.title}")
    print(f"🌐 API文档: http://127.0.0.1:8000/docs")
except ImportError as e:
    print(f"❌ 应用导入失败: {e}")
    print("🔍 尝试详细诊断...")

    # 检查各个模块
    try:
        from app.api.v1 import capsule_router
        print("✅ capsule_router 导入成功")
    except Exception as e:
        print(f"❌ capsule_router 导入失败: {e}")

    try:
        from database.database import create_tables
        print("✅ create_tables 导入成功")
    except Exception as e:
        print(f"❌ create_tables 导入失败: {e}")

if __name__ == "__main__":
    print("🚀 启动测试完成")