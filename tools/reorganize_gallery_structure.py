#!/usr/bin/env python3
"""
重组微博图集目录结构
将 年/月/日 结构改为 年/月 结构
"""

import os
import shutil
from pathlib import Path

# 基础路径
BASE_PATH = Path("/home/yifeianyi/Desktop/xxm_fans_home/media/gallery/weibo_images")

def reorganize_gallery():
    """重组图集目录结构"""
    print(f"开始重组图集目录结构: {BASE_PATH}")
    print("=" * 60)

    # 统计信息
    stats = {
        'year_folders': 0,
        'month_folders_processed': 0,
        'day_moved': 0,
        'files_moved': 0,
        'errors': []
    }

    # 遍历所有年份目录
    for year_dir in sorted(BASE_PATH.iterdir()):
        if not year_dir.is_dir():
            continue

        print(f"\n处理年份: {year_dir.name}")
        stats['year_folders'] += 1

        # 遍历所有月份目录
        for month_dir in sorted(year_dir.iterdir()):
            if not month_dir.is_dir():
                continue

            print(f"  处理月份: {month_dir.name}")
            stats['month_folders_processed'] += 1

            # 检查该月份下是否有日期目录
            day_dirs = [d for d in month_dir.iterdir() if d.is_dir()]

            if not day_dirs:
                print(f"    无日期目录，跳过")
                continue

            # 遍历所有日期目录，将文件移动到月份目录
            for day_dir in sorted(day_dirs):
                print(f"    处理日期: {day_dir.name}")
                stats['day_moved'] += 1

                # 移动该日期目录下的所有文件到月份目录
                for file_path in day_dir.iterdir():
                    if file_path.is_file():
                        try:
                            # 目标路径
                            target_path = month_dir / file_path.name

                            # 如果目标文件已存在，添加序号
                            if target_path.exists():
                                counter = 1
                                stem = file_path.stem
                                suffix = file_path.suffix
                                while target_path.exists():
                                    target_path = month_dir / f"{stem}_{counter}{suffix}"
                                    counter += 1

                            # 移动文件
                            shutil.move(str(file_path), str(target_path))
                            stats['files_moved'] += 1
                            print(f"      移动: {file_path.name}")

                        except Exception as e:
                            error_msg = f"移动文件失败 {file_path}: {e}"
                            stats['errors'].append(error_msg)
                            print(f"      错误: {error_msg}")

                # 删除空的日期目录
                try:
                    day_dir.rmdir()
                    print(f"    删除空目录: {day_dir.name}")
                except Exception as e:
                    print(f"    警告: 无法删除目录 {day_dir.name}: {e}")

    # 打印统计信息
    print("\n" + "=" * 60)
    print("重组完成！统计信息:")
    print(f"  处理的年份目录: {stats['year_folders']}")
    print(f"  处理的月份目录: {stats['month_folders_processed']}")
    print(f"  移动的日期目录: {stats['day_moved']}")
    print(f"  移动的文件数: {stats['files_moved']}")

    if stats['errors']:
        print(f"\n错误数量: {len(stats['errors'])}")
        for error in stats['errors']:
            print(f"  - {error}")
    else:
        print("\n没有错误！")

    return stats

if __name__ == "__main__":
    # 确认操作
    print("警告: 此操作将重组图集目录结构！")
    print("当前结构: 年/月/日")
    print("目标结构: 年/月")
    print(f"\n目标路径: {BASE_PATH}")

    response = input("\n确认继续? (yes/no): ")
    if response.lower() == 'yes':
        reorganize_gallery()
    else:
        print("操作已取消")
