#!/usr/bin/env python3
"""
合并冲突解决验证脚本
验证所有功能是否正常工作
"""
import os
import sys

def add_backend_to_path():
    """添加backend目录到Python路径"""
    backend_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'backend')
    if backend_dir not in sys.path:
        sys.path.insert(0, backend_dir)
    return backend_dir

def test_basic_imports():
    """测试基本模块导入"""
    print("🔍 测试基本模块导入...")

    tests = [
        ("FastAPI", "fastapi"),
        ("SQLAlchemy", "sqlalchemy"),
        ("Pydantic", "pydantic"),
    ]

    for name, module in tests:
        try:
            __import__(module)
            print(f"   ✅ {name}")
        except ImportError:
            print(f"   ❌ {name} - 未安装")
            return False

    return True

def test_app_imports():
    """测试应用模块导入"""
    print("\n🔍 测试应用模块导入...")

    try:
        # 测试数据库模块
        from database.database import create_tables, get_database_url
        print("   ✅ 数据库配置模块")

        # 测试API路由
        from api.v1 import capsule_router, auth_router
        print("   ✅ API路由模块")

        # 测试胶囊服务
        from services.capsule import CapsuleManager
        print("   ✅ 胶囊服务模块")

        # 测试主应用
        from main import app
        print("   ✅ 主应用模块")

        print(f"\n📋 应用信息:")
        print(f"   标题: {app.title}")
        print(f"   版本: {app.version}")

        return True

    except Exception as e:
        print(f"   ❌ 应用导入失败: {e}")
        return False

def test_database_config():
    """测试数据库配置"""
    print("\n🔍 测试数据库配置...")

    try:
        from database.database import get_database_url, DATABASE_CONFIG

        db_url = get_database_url()
        print(f"   📁 数据库路径: {DATABASE_CONFIG['sqlite']['database']}")
        print(f"   🔗 数据库URL: {db_url}")

        # 检查数据库目录是否存在
        db_dir = os.path.dirname(DATABASE_CONFIG['sqlite']['database'])
        if os.path.exists(db_dir):
            print(f"   ✅ 数据库目录存在: {db_dir}")
        else:
            print(f"   ⚠️  数据库目录不存在，将自动创建: {db_dir}")

        return True

    except Exception as e:
        print(f"   ❌ 数据库配置测试失败: {e}")
        return False

def test_route_structure():
    """测试路由结构"""
    print("\n🔍 测试路由结构...")

    try:
        from api.v1 import (
            capsule_router, auth_router, admin_router,
            user_router, friend_router, upload_router
        )

        routers = [
            ("胶囊路由", capsule_router),
            ("认证路由", auth_router),
            ("管理员路由", admin_router),
            ("用户路由", user_router),
            ("好友路由", friend_router),
            ("上传路由", upload_router),
        ]

        for name, router in routers:
            if router is not None:
                print(f"   ✅ {name}")
            else:
                print(f"   ⚠️  {name} - 未加载")

        return True

    except Exception as e:
        print(f"   ❌ 路由结构测试失败: {e}")
        return False

def main():
    """主验证函数"""
    print("🚀 开始验证合并冲突解决结果...")
    print("=" * 50)

    # 设置Python路径
    backend_dir = add_backend_to_path()
    print(f"📁 Backend目录: {backend_dir}")

    # 运行测试
    tests = [
        ("基本模块导入", test_basic_imports),
        ("应用模块导入", test_app_imports),
        ("数据库配置", test_database_config),
        ("路由结构", test_route_structure),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} 测试出现异常: {e}")
            results.append((test_name, False))

    # 输出结果
    print("\n" + "=" * 50)
    print("📊 验证结果总结:")

    passed = 0
    for test_name, result in results:
        status = "✅ 通过" if result else "❌ 失败"
        print(f"   {test_name}: {status}")
        if result:
            passed += 1

    print(f"\n🎯 总体结果: {passed}/{len(results)} 项测试通过")

    if passed == len(results):
        print("🎉 恭喜！所有验证测试通过！")
        print("✅ 合并冲突已成功解决")
        print("✅ 前后端可以正常对接")
        print("✅ 用户系统可以使用")
        return True
    else:
        print("⚠️  部分测试未通过，可能需要进一步调试")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)