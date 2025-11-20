#!/usr/bin/env python3
"""
数据库初始化脚本
用于创建数据库表结构
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.database.orm.config import create_tables, drop_tables


def main():
    """主函数"""
    print("时光胶囊·校园 - 数据库初始化")
    print("=" * 50)

    while True:
        print("\n请选择操作:")
        print("1. 创建所有表")
        print("2. 删除所有表（危险操作）")
        print("3. 退出")

        choice = input("\n请输入选择 (1-3): ").strip()

        if choice == "1":
            print("\n正在创建数据库表...")
            try:
                create_tables()
                print("✅ 数据库表创建成功！")
            except Exception as e:
                print(f"❌ 创建数据库表失败: {e}")

        elif choice == "2":
            confirm = input("\n⚠️  警告：这将删除所有数据！确认删除？(y/N): ").strip().lower()
            if confirm == "y":
                print("正在删除所有表...")
                try:
                    drop_tables()
                    print("✅ 所有表已删除")
                except Exception as e:
                    print(f"❌ 删除表失败: {e}")
            else:
                print("操作已取消")

        elif choice == "3":
            print("退出程序")
            break

        else:
            print("无效选择，请重新输入")


if __name__ == "__main__":
    main()