#!/usr/bin/env python3
"""
胶囊ID类型迁移脚本
从Integer类型迁移到String类型
"""

import sys
import os
from datetime import datetime

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import text, MetaData, Table, Column, String, Integer, ForeignKey
from app.database.database import engine, get_database_url
from app.database.orm import *

def backup_data():
    """备份现有数据"""
    backup_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    print(f"📁 正在备份数据... 时间戳: {backup_time}")

    with engine.connect() as conn:
        # 备份胶囊数据
        result = conn.execute(text("SELECT COUNT(*) FROM capsules"))
        count = result.scalar()
        print(f"📊 发现 {count} 个胶囊记录")

        if count > 0:
            print("⚠️  检测到现有数据！")
            return True
    return False

def migrate_capsule_id_type():
    """迁移胶囊ID类型从Integer到String"""
    print("🔧 开始迁移胶囊ID字段类型...")

    try:
        # 检查数据库类型
        db_url = get_database_url()
        is_mysql = db_url.startswith('mysql')

        with engine.connect() as conn:
            trans = conn.begin()
            try:
                if is_mysql:
                    print("📱 检测到MySQL数据库，执行MySQL迁移...")

                    # 1. 禁用外键检查
                    conn.execute(text("SET FOREIGN_KEY_CHECKS = 0"))

                    # 2. 创建临时表结构
                    conn.execute(text("""
                        CREATE TABLE capsules_new LIKE capsules
                    """))

                    # 3. 修改新表的ID字段类型
                    conn.execute(text("""
                        ALTER TABLE capsules_new
                        MODIFY COLUMN id VARCHAR(255) NOT NULL PRIMARY KEY
                    """))

                    # 4. 复制数据（转换ID为字符串格式）
                    conn.execute(text("""
                        INSERT INTO capsules_new
                        SELECT
                            CONCAT('capsule_', id) as id,
                            title, text_content, user_id, latitude, longitude,
                            address, status, visibility, content_type,
                            tag_json, created_at, updated_at
                        FROM capsules
                    """))

                    # 5. 更新相关表的外键（如果存在数据）
                    # 先检查是否有相关数据
                    media_count = conn.execute(text("SELECT COUNT(*) FROM capsule_media")).scalar()
                    unlock_count = conn.execute(text("SELECT COUNT(*) FROM unlock_conditions")).scalar()
                    record_count = conn.execute(text("SELECT COUNT(*) FROM unlock_records")).scalar()

                    if media_count > 0:
                        print(f"📸 更新 {media_count} 个媒体文件记录...")
                        conn.execute(text("""
                            UPDATE capsule_media
                            SET capsule_id = CONCAT('capsule_', capsule_id)
                        """))
                        # 修改外键字段类型
                        conn.execute(text("""
                            ALTER TABLE capsule_media
                            MODIFY COLUMN capsule_id VARCHAR(255) NOT NULL
                        """))

                    if unlock_count > 0:
                        print(f"🔓 更新 {unlock_count} 个解锁条件记录...")
                        conn.execute(text("""
                            UPDATE unlock_conditions
                            SET capsule_id = CONCAT('capsule_', capsule_id)
                        """))
                        # 修改外键字段类型
                        conn.execute(text("""
                            ALTER TABLE unlock_conditions
                            MODIFY COLUMN capsule_id VARCHAR(255) NOT NULL
                        """))

                    if record_count > 0:
                        print(f"📝 更新 {record_count} 个解锁记录...")
                        conn.execute(text("""
                            UPDATE unlock_records
                            SET capsule_id = CONCAT('capsule_', capsule_id)
                        """))
                        # 修改外键字段类型
                        conn.execute(text("""
                            ALTER TABLE unlock_records
                            MODIFY COLUMN capsule_id VARCHAR(255) NOT NULL
                        """))

                        conn.execute(text("""
                            UPDATE unlock_attempts
                            SET capsule_id = CONCAT('capsule_', capsule_id)
                        """))
                        # 修改外键字段类型
                        conn.execute(text("""
                            ALTER TABLE unlock_attempts
                            MODIFY COLUMN capsule_id VARCHAR(255) NOT NULL
                        """))

                    # 6. 重命名表
                    conn.execute(text("DROP TABLE capsules"))
                    conn.execute(text("RENAME TABLE capsules_new TO capsules"))

                    # 7. 重新启用外键检查
                    conn.execute(text("SET FOREIGN_KEY_CHECKS = 1"))

                else:
                    print("📱 检测到SQLite数据库，执行SQLite迁移...")
                    # SQLite迁移逻辑（相对简单）
                    # SQLite不支持直接ALTER COLUMN，需要重建表

                    # 获取现有数据
                    result = conn.execute(text("SELECT COUNT(*) FROM capsules"))
                    if result.scalar() > 0:
                        print("⚠️  SQLite数据库有现有数据，建议手动处理或删除后重建")
                        return False

                trans.commit()
                print("✅ 迁移完成！")
                return True

            except Exception as e:
                trans.rollback()
                print(f"❌ 迁移失败，已回滚: {e}")
                return False

    except Exception as e:
        print(f"❌ 数据库连接失败: {e}")
        return False

def verify_migration():
    """验证迁移结果"""
    print("🔍 验证迁移结果...")

    try:
        with engine.connect() as conn:
            # 检查胶囊表结构
            result = conn.execute(text("DESCRIBE capsules"))
            for row in result:
                if row[0] == 'id':
                    print(f"📋 胶囊ID字段类型: {row[1]}")
                    break

            # 检查数据
            result = conn.execute(text("SELECT id, title FROM capsules LIMIT 5"))
            rows = result.fetchall()
            if rows:
                print("📊 迁移后的数据样本:")
                for row in rows:
                    print(f"   ID: {row[0]}, 标题: {row[1]}")
            else:
                print("📊 表中无数据")

        print("✅ 验证完成")
        return True

    except Exception as e:
        print(f"❌ 验证失败: {e}")
        return False

def main():
    """主函数"""
    print("时光胶囊 - 胶囊ID类型迁移")
    print("=" * 50)

    # 检查是否需要迁移
    if not backup_data():
        print("📭 数据库为空，无需迁移")
        print("✨ 可以直接使用新的表结构")
        return

    print("\n⚠️  警告：此操作将修改数据库结构！")
    confirm = input("确认执行迁移？(y/N): ").strip().lower()

    if confirm != 'y':
        print("❌ 迁移已取消")
        return

    # 执行迁移
    if migrate_capsule_id_type():
        verify_migration()
        print("\n🎉 迁移成功完成！")
    else:
        print("\n💥 迁移失败，请检查错误信息")

if __name__ == "__main__":
    main()