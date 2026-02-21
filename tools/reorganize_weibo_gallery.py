#!/usr/bin/env python3
"""
重组微博图集目录结构并同步更新数据库
将 年/月/日 结构改为 年/月 结构
"""

import os
import sys
import django
from pathlib import Path

# 设置 Django 环境
sys.path.insert(0, '/home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')
django.setup()

from gallery.models import Gallery

# 基础路径
BASE_PATH = Path("/home/yifeianyi/Desktop/xxm_fans_home/media/gallery/weibo_images")

def reorganize_directories():
    """重组目录结构"""
    print(f"开始重组图集目录结构: {BASE_PATH}")
    print("=" * 60)

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
                            import shutil
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

    return stats

def update_database():
    """更新数据库中的图集路径"""
    print("\n" + "=" * 60)
    print("开始更新数据库...")
    print("=" * 60)

    stats = {
        'total_checked': 0,
        'day_level_deleted': 0,
        'month_level_updated': 0,
        'errors': []
    }

    # 查找所有包含 weibo_images 的图集
    galleries = Gallery.objects.filter(folder_path__contains='weibo_images')
    stats['total_checked'] = galleries.count()

    print(f"找到 {stats['total_checked']} 个微博图集")

    for gallery in galleries:
        path_parts = gallery.folder_path.strip('/').split('/')

        # 检查是否是日层级（路径长度为 4: gallery/weibo_images/年/月/日）
        if len(path_parts) == 4:
            print(f"\n处理日层级图集: {gallery.id}")
            print(f"  原路径: {gallery.folder_path}")

            # 删除日层级的图集记录
            try:
                gallery.delete()
                stats['day_level_deleted'] += 1
                print(f"  ✓ 已删除")
            except Exception as e:
                error_msg = f"删除图集失败 {gallery.id}: {e}"
                stats['errors'].append(error_msg)
                print(f"  ✗ 错误: {error_msg}")

        # 检查是否是月层级（路径长度为 3: gallery/weibo_images/年/月）
        elif len(path_parts) == 3:
            print(f"\n处理月层级图集: {gallery.id}")
            print(f"  原路径: {gallery.folder_path}")

            # 更新图片数量（因为文件已经移动到这里）
            try:
                gallery.refresh_image_count()
                stats['month_level_updated'] += 1
                print(f"  ✓ 已更新图片数量: {gallery.image_count}")
            except Exception as e:
                error_msg = f"更新图集失败 {gallery.id}: {e}"
                stats['errors'].append(error_msg)
                print(f"  ✗ 错误: {error_msg}")

    return stats

def main():
    """主函数"""
    print("=" * 60)
    print("微博图集目录重组工具")
    print("=" * 60)
    print("\n当前结构: 年/月/日")
    print("目标结构: 年/月")
    print(f"\n目标路径: {BASE_PATH}")

    response = input("\n确认继续? (yes/no): ")
    if response.lower() != 'yes':
        print("操作已取消")
        return

    # 第一步：重组目录
    print("\n\n第一步：重组目录结构")
    print("=" * 60)
    dir_stats = reorganize_directories()

    print("\n" + "=" * 60)
    print("目录重组完成！统计信息:")
    print(f"  处理的年份目录: {dir_stats['year_folders']}")
    print(f"  处理的月份目录: {dir_stats['month_folders_processed']}")
    print(f"  移动的日期目录: {dir_stats['day_moved']}")
    print(f"  移动的文件数: {dir_stats['files_moved']}")

    if dir_stats['errors']:
        print(f"\n错误数量: {len(dir_stats['errors'])}")
        for error in dir_stats['errors']:
            print(f"  - {error}")

    # 第二步：更新数据库
    print("\n\n第二步：更新数据库")
    print("=" * 60)

    response = input("\n目录重组已完成，是否继续更新数据库? (yes/no): ")
    if response.lower() != 'yes':
        print("数据库更新已跳过")
        return

    db_stats = update_database()

    print("\n" + "=" * 60)
    print("数据库更新完成！统计信息:")
    print(f"  检查的图集数: {db_stats['total_checked']}")
    print(f"  删除的日层级图集: {db_stats['day_level_deleted']}")
    print(f"  更新的月层级图集: {db_stats['month_level_updated']}")

    if db_stats['errors']:
        print(f"\n错误数量: {len(db_stats['errors'])}")
        for error in db_stats['errors']:
            print(f"  - {error}")
    else:
        print("\n没有错误！")

    # 最终统计
    print("\n" + "=" * 60)
    print("全部完成！")
    print("=" * 60)
    print(f"目录重组: 移动了 {dir_stats['files_moved']} 个文件")
    print(f"数据库更新: 删除了 {db_stats['day_level_deleted']} 个日层级图集")
    print(f"数据库更新: 更新了 {db_stats['month_level_updated']} 个月层级图集")

if __name__ == "__main__":
    main()