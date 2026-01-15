#!/usr/bin/env python3
"""
验证 fansDIY 数据是否正确复制
"""

import sqlite3
from pathlib import Path

# 数据库路径
BACKUP_DB = Path("/home/yifeianyi/Desktop/xxm_fans_home/data/db_backup.sqlite3")
TARGET_DB = Path("/home/yifeianyi/Desktop/xxm_fans_home/data/db.sqlite3")

FANS_DIY_TABLES = [
    'fansDIY_collection',
    'fansDIY_work',
]

def verify_table_data(db_path, table_name):
    """验证表数据"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # 获取记录数
    cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
    count = cursor.fetchone()[0]

    # 获取前3条记录
    cursor.execute(f"SELECT * FROM {table_name} LIMIT 3")
    sample_data = cursor.fetchall()

    conn.close()

    return count, sample_data

def main():
    print("=" * 60)
    print("验证 fansDIY 数据复制")
    print("=" * 60)

    for table_name in FANS_DIY_TABLES:
        print(f"\n表: {table_name}")
        print("-" * 60)

        # 源数据库
        backup_count, backup_sample = verify_table_data(BACKUP_DB, table_name)
        print(f"源数据库记录数: {backup_count}")

        # 目标数据库
        target_count, target_sample = verify_table_data(TARGET_DB, table_name)
        print(f"目标数据库记录数: {target_count}")

        # 比较
        if backup_count == target_count:
            print(f"✓ 记录数匹配")
        else:
            print(f"✗ 记录数不匹配！差异: {target_count - backup_count}")

        # 显示样本数据
        if backup_sample:
            print(f"\n源数据库样本数据（前3条）:")
            for i, row in enumerate(backup_sample, 1):
                print(f"  {i}. {row}")

        if target_sample:
            print(f"\n目标数据库样本数据（前3条）:")
            for i, row in enumerate(target_sample, 1):
                print(f"  {i}. {row}")

        # 比较样本数据
        if backup_sample and target_sample:
            if backup_sample == target_sample:
                print(f"\n✓ 样本数据匹配")
            else:
                print(f"\n✗ 样本数据不匹配")

    print("\n" + "=" * 60)
    print("✓ 验证完成")
    print("=" * 60)

if __name__ == "__main__":
    main()