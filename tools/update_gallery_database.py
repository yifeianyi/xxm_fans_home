#!/usr/bin/env python3
"""
更新微博图集数据库
删除日层级的图集记录，并更新月层级图集的图片数量
"""

import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, '/home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')
django.setup()

from gallery.models import Gallery

def update_database():
    """更新数据库中的图集路径"""
    print("=" * 60)
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

if __name__ == "__main__":
    print("=" * 60)
    print("微博图集数据库更新工具")
    print("=" * 60)

    response = input("\n确认继续? (yes/no): ")
    if response.lower() != 'yes':
        print("操作已取消")
        sys.exit(0)

    stats = update_database()

    print("\n" + "=" * 60)
    print("数据库更新完成！统计信息:")
    print("=" * 60)
    print(f"  检查的图集数: {stats['total_checked']}")
    print(f"  删除的日层级图集: {stats['day_level_deleted']}")
    print(f"  更新的月层级图集: {stats['month_level_updated']}")

    if stats['errors']:
        print(f"\n错误数量: {len(stats['errors'])}")
        for error in stats['errors']:
            print(f"  - {error}")
    else:
        print("\n没有错误！")