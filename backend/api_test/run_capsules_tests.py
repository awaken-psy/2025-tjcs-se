#!/usr/bin/env python3
"""
胶囊API测试运行器
用于运行所有胶囊相关的API测试
"""

import pytest
import sys
import os

def run_capsule_tests():
    """运行所有胶囊相关测试"""

    # 获取当前脚本所在目录
    current_dir = os.path.dirname(os.path.abspath(__file__))

    # 定义测试文件列表（按数字顺序执行）
    test_files = [
        "test_5_capsules_basic.py",      # 基础CRUD操作
        "test_6_capsules_unlock.py",     # 解锁功能
        "test_7_capsules_interactions.py", # 互动功能（点赞、收藏、评论）
        "test_8_capsules_media.py",      # 媒体文件
        "test_9_capsules_browse.py",     # 浏览和搜索
        "test_10_capsules_hub.py"        # Hub功能
    ]

    # 构建完整的测试文件路径
    test_paths = [os.path.join(current_dir, test_file) for test_file in test_files]

    print("🚀 开始运行胶囊API测试...")
    print(f"📁 测试目录: {current_dir}")
    print(f"📋 测试文件: {len(test_files)} 个")
    print("\n" + "="*60)

    # 运行测试
    exit_code = pytest.main([
        "-v",                    # 详细输出
        "-s",                    # 显示print语句
        "--tb=short",           # 简短的错误回溯
        "-x",                   # 遇到第一个失败就停止
        "--disable-warnings",   # 禁用警告
        *test_paths             # 测试文件列表
    ])

    print("\n" + "="*60)

    if exit_code == 0:
        print("✅ 所有胶囊API测试通过！")
    else:
        print("❌ 部分胶囊API测试失败！")

    return exit_code

def run_specific_test(test_name):
    """运行特定的测试文件"""

    current_dir = os.path.dirname(os.path.abspath(__file__))
    test_path = os.path.join(current_dir, test_name)

    if not os.path.exists(test_path):
        print(f"❌ 测试文件不存在: {test_path}")
        return 1

    print(f"🚀 运行特定测试: {test_name}")
    print(f"📁 测试路径: {test_path}")
    print("\n" + "="*60)

    exit_code = pytest.main([
        "-v",
        "-s",
        "--tb=short",
        "--disable-warnings",
        test_path
    ])

    print("\n" + "="*60)

    if exit_code == 0:
        print(f"✅ 测试 {test_name} 通过！")
    else:
        print(f"❌ 测试 {test_name} 失败！")

    return exit_code

def main():
    """主函数"""
    if len(sys.argv) > 1:
        # 如果指定了特定的测试文件
        test_name = sys.argv[1]
        return run_specific_test(test_name)
    else:
        # 运行所有胶囊测试
        return run_capsule_tests()

if __name__ == "__main__":
    sys.exit(main())