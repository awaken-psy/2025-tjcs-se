#!/usr/bin/env python3
"""
服务器启动脚本
从项目根目录运行
"""
import os
import sys

# 添加backend目录到Python路径
backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

print("🔧 设置Python路径...")
print(f"📁 Backend目录: {backend_dir}")
print(f"🐍 Python路径: {sys.path[:3]}...")

print("\n🔍 测试导入...")
try:
    print("1. 导入FastAPI...")
    from fastapi import FastAPI
    print("   ✅ FastAPI导入成功")

    print("2. 导入应用模块...")
    from app.main import app
    print("   ✅ 应用导入成功!")

    print(f"\n📋 应用信息:")
    print(f"   标题: {app.title}")
    print(f"   版本: {app.version}")
    print(f"   文档: http://127.0.0.1:8000/docs")

    print("\n🚀 启动服务器...")
    import uvicorn
    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=True
    )

except ImportError as e:
    print(f"❌ 导入错误: {e}")
    print("\n🔍 详细诊断:")

    # 测试各个组件
    modules_to_test = [
        "fastapi",
        "uvicorn",
        "sqlalchemy",
        "pydantic"
    ]

    for module in modules_to_test:
        try:
            __import__(module)
            print(f"   ✅ {module}")
        except ImportError:
            print(f"   ❌ {module} - 未安装")

except Exception as e:
    print(f"❌ 启动错误: {e}")
    import traceback
    traceback.print_exc()

if __name__ == "__main__":
    print("服务器启动脚本结束")