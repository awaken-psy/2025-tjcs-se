#!/usr/bin/env python3
"""
测试 MySQL 数据库连接和数据持久化的脚本
"""

import mysql.connector
from mysql.connector import Error

def test_mysql_connection():
    """测试 MySQL 数据库连接"""
    try:
        # 连接参数
        config = {
            'host': 'localhost',
            'port': 3307,  # Docker 映射的端口
            'database': 'timecapsule',
            'user': 'timecapsule_admin',
            'password': 'Markov@2025',
            'charset': 'utf8mb4'
        }

        print("🔗 尝试连接 MySQL 数据库...")
        connection = mysql.connector.connect(**config)

        if connection.is_connected():
            print("✅ 数据库连接成功!")

            cursor = connection.cursor()

            # 检查数据库和表
            cursor.execute("SHOW DATABASES;")
            databases = cursor.fetchall()
            print(f"📊 可用数据库: {[db[0] for db in databases]}")

            cursor.execute("SHOW TABLES;")
            tables = cursor.fetchall()
            print(f"📋 当前表: {[table[0] for table in tables]}")

            # 检查胶囊数据
            cursor.execute("SELECT COUNT(*) FROM capsules;")
            count = cursor.fetchone()[0]
            print(f"💊 胶囊总数: {count}")

            if count > 0:
                cursor.execute("SELECT id, title, latitude, longitude, created_at FROM capsules ORDER BY id DESC LIMIT 3;")
                capsules = cursor.fetchall()
                print("📦 最近的胶囊:")
                for capsule in capsules:
                    print(f"  - ID: {capsule[0]}, 标题: {capsule[1]}, 位置: ({capsule[2]}, {capsule[3]}), 创建时间: {capsule[4]}")

            cursor.close()

    except Error as e:
        print(f"❌ 数据库连接错误: {e}")
    finally:
        if 'connection' in locals() and connection.is_connected():
            connection.close()
            print("🔌 数据库连接已关闭")

if __name__ == "__main__":
    test_mysql_connection()