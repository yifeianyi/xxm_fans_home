#!/usr/bin/env python3
"""
将 db_backup.sqlite3 中的 fansDIY 相关表数据复制到 db.sqlite3
"""

import sqlite3
import shutil
from pathlib import Path

# 数据库路径
BACKUP_DB = Path("/home/yifeianyi/Desktop/xxm_fans_home/data/db_backup.sqlite3")
TARGET_DB = Path("/home/yifeianyi/Desktop/xxm_fans_home/data/db.sqlite3")

# fansDIY 相关的表
FANS_DIY_TABLES = [
    'fansDIY_collection',
    'fansDIY_work',
]

def copy_table_data(source_conn, target_conn, table_name):
    """复制表数据"""
    print(f"\n处理表: {table_name}")

    # 获取源表的所有数据
    cursor = source_conn.cursor()
    cursor.execute(f"SELECT * FROM {table_name}")
    rows = cursor.fetchall()

    # 获取列信息
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [col[1] for col in cursor.fetchall()]
    column_count = len(columns)

    print(f"  源表记录数: {len(rows)}")
    print(f"  列数: {column_count}")
    print(f"  列名: {', '.join(columns)}")

    if not rows:
        print(f"  ⚠️  源表为空，跳过")
        return

    # 清空目标表
    target_cursor = target_conn.cursor()
    target_cursor.execute(f"DELETE FROM {table_name}")
    print(f"  ✓ 已清空目标表")

    # 插入数据
    placeholders = ', '.join(['?' for _ in range(column_count)])
    insert_sql = f"INSERT INTO {table_name} VALUES ({placeholders})"

    try:
        target_cursor.executemany(insert_sql, rows)
        target_conn.commit()
        print(f"  ✓ 已复制 {len(rows)} 条记录")
    except Exception as e:
        target_conn.rollback()
        print(f"  ✗ 复制失败: {e}")
        raise

def main():
    print("=" * 60)
    print("复制 fansDIY 数据")
    print("=" * 60)

    # 检查数据库文件是否存在
    if not BACKUP_DB.exists():
        print(f"✗ 备份数据库不存在: {BACKUP_DB}")
        return 1

    if not TARGET_DB.exists():
        print(f"✗ 目标数据库不存在: {TARGET_DB}")
        return 1

    print(f"\n备份数据库: {BACKUP_DB}")
    print(f"目标数据库: {TARGET_DB}")

    # 备份目标数据库
    backup_target = TARGET_DB.with_suffix('.sqlite3.bak')
    shutil.copy2(TARGET_DB, backup_target)
    print(f"\n✓ 已备份目标数据库到: {backup_target}")

    try:
        # 连接数据库
        print("\n连接数据库...")
        source_conn = sqlite3.connect(BACKUP_DB)
        target_conn = sqlite3.connect(TARGET_DB)

        # 获取所有表
        print("\n检查源数据库表...")
        source_cursor = source_conn.cursor()
        source_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        source_tables = [row[0] for row in source_cursor.fetchall()]
        print(f"  源数据库表: {', '.join(source_tables)}")

        print("\n检查目标数据库表...")
        target_cursor = target_conn.cursor()
        target_cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        target_tables = [row[0] for row in target_cursor.fetchall()]
        print(f"  目标数据库表: {', '.join(target_tables)}")

        # 检查 fansDIY 表是否存在
        missing_in_source = [t for t in FANS_DIY_TABLES if t not in source_tables]
        missing_in_target = [t for t in FANS_DIY_TABLES if t not in target_tables]

        if missing_in_source:
            print(f"\n✗ 源数据库中缺少表: {', '.join(missing_in_source)}")
            return 1

        if missing_in_target:
            print(f"\n✗ 目标数据库中缺少表: {', '.join(missing_in_target)}")
            return 1

        # 复制数据
        print("\n开始复制数据...")
        for table_name in FANS_DIY_TABLES:
            copy_table_data(source_conn, target_conn, table_name)

        # 关闭连接
        source_conn.close()
        target_conn.close()

        print("\n" + "=" * 60)
        print("✓ 数据复制完成！")
        print("=" * 60)
        print(f"\n备份文件: {backup_target}")
        print("如果出现问题，可以使用备份文件恢复")

        return 0

    except Exception as e:
        print(f"\n✗ 发生错误: {e}")
        import traceback
        traceback.print_exc()
        return 1

if __name__ == "__main__":
    exit(main())
