#!/usr/bin/env python3
"""
自动同步图集脚本
将新图集放到 gallery 目录后，运行此脚本自动更新后台数据
"""

import os
import sys
import django

# 设置 Django 环境
sys.path.insert(0, '/home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')
django.setup()

from gallery.models import Gallery
from django.conf import settings
from django.db import models

def sync_gallery():
    """同步图集数据"""
    print("=" * 60)
    print("自动同步图集数据")
    print("=" * 60)

    gallery_root = os.path.join(settings.MEDIA_ROOT, 'gallery')

    if not os.path.exists(gallery_root):
        print(f"错误: 图集目录不存在: {gallery_root}")
        return

    print(f"\n扫描目录: {gallery_root}")

    # 统计信息
    stats = {
        'scanned': 0,
        'created': 0,
        'updated': 0,
        'deleted': 0,
        'errors': []
    }

    # 获取数据库中所有图集ID
    db_galleries = set(Gallery.objects.values_list('id', flat=True))

    # 递归扫描文件夹
    def scan_folder(folder_path, parent=None, level=0):
        nonlocal stats

        try:
            items = sorted(os.listdir(folder_path))
        except PermissionError as e:
            error_msg = f"无法访问目录 {folder_path}: {e}"
            stats['errors'].append(error_msg)
            print(f"  ✗ {error_msg}")
            return

        for item in items:
            item_path = os.path.join(folder_path, item)

            if not os.path.isdir(item_path):
                continue

            stats['scanned'] += 1

            # 计算相对路径
            rel_path = os.path.relpath(item_path, settings.MEDIA_ROOT)
            folder_url = '/' + rel_path.replace('\\', '/') + '/'

            # 检查是否有封面
            cover_path = os.path.join(item_path, 'cover.jpg')
            cover_url = f'{folder_url}cover.jpg' if os.path.exists(cover_path) else ''

            # 计算图片数量
            try:
                image_files = [f for f in os.listdir(item_path)
                             if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif', '.mp4'))
                             and f != 'cover.jpg']
            except PermissionError:
                image_files = []

            # 生成图集ID
            gallery_id = rel_path.replace('\\', '-').replace('/', '-')

            # 检查图集是否已存在
            try:
                gallery = Gallery.objects.get(id=gallery_id)

                # 更新现有图集
                gallery.title = item
                gallery.description = f'{item}图集'
                gallery.cover_url = cover_url
                gallery.parent = parent
                gallery.level = level
                gallery.image_count = len(image_files)
                gallery.folder_path = folder_url
                gallery.is_active = True
                gallery.save()

                stats['updated'] += 1
                print(f"  ✓ 更新: {gallery.title} ({gallery.image_count} 张图片)")

            except Gallery.DoesNotExist:
                # 创建新图集
                gallery = Gallery.objects.create(
                    id=gallery_id,
                    title=item,
                    description=f'{item}图集',
                    cover_url=cover_url,
                    parent=parent,
                    level=level,
                    image_count=len(image_files),
                    folder_path=folder_url,
                    tags=[],
                    is_active=True
                )

                stats['created'] += 1
                print(f"  + 创建: {gallery.title} ({gallery.image_count} 张图片)")

            # 从数据库集合中移除已处理的图集
            if gallery_id in db_galleries:
                db_galleries.remove(gallery_id)

            # 递归处理子文件夹
            scan_folder(item_path, gallery, level + 1)

    # 开始扫描
    scan_folder(gallery_root)

    # 删除数据库中不存在的图集
    if db_galleries:
        print("\n删除不存在的图集:")
        for gallery_id in db_galleries:
            try:
                gallery = Gallery.objects.get(id=gallery_id)
                gallery.delete()
                stats['deleted'] += 1
                print(f"  - 删除: {gallery.title}")
            except Gallery.DoesNotExist:
                pass

    # 递归刷新所有父图集的图片数量
    print("\n刷新父图集图片数量...")
    root_galleries = Gallery.objects.filter(parent__isnull=True)
    for root_gallery in root_galleries:
        root_gallery.refresh_image_count()

    # 打印统计信息
    print("\n" + "=" * 60)
    print("同步完成！")
    print("=" * 60)
    print(f"扫描目录: {stats['scanned']}")
    print(f"创建图集: {stats['created']}")
    print(f"更新图集: {stats['updated']}")
    print(f"删除图集: {stats['deleted']}")

    if stats['errors']:
        print(f"\n错误数量: {len(stats['errors'])}")
        for error in stats['errors']:
            print(f"  - {error}")
    else:
        print("\n没有错误！")

    # 显示图集统计
    print("\n图集统计:")
    total_galleries = Gallery.objects.count()
    total_images = Gallery.objects.aggregate(total=models.Sum('image_count'))['total'] or 0
    print(f"  总图集数: {total_galleries}")
    print(f"  总图片数: {total_images}")

if __name__ == "__main__":
    sync_gallery()