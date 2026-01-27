#!/usr/bin/env python3
"""
自动同步图集脚本
将新图集放到 gallery 目录后，运行此脚本自动更新后台数据
"""

import os
import sys
import django
import re

# 设置 Django 环境
sys.path.insert(0, '/home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')
django.setup()

from gallery.models import Gallery
from django.conf import settings
from django.db import models

def generate_gallery_id(folder_name, parent=None):
    """生成图集ID：根图集使用文件夹名，子图集使用父图集ID+子文件夹名"""
    if parent is None:
        # 根图集：直接使用文件夹名
        return folder_name
    else:
        # 子图集：父图集ID-子文件夹名
        return f"{parent.id}-{folder_name}"

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
        'skipped': 0,
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

            # 设置封面：如果没有cover.jpg，使用第一张图片作为封面
            if not os.path.exists(cover_path) and image_files:
                # 使用第一张图片作为封面
                first_image = image_files[0]
                cover_url = f'{folder_url}{first_image}'
            elif os.path.exists(cover_path):
                cover_url = f'{folder_url}cover.jpg'
            else:
                cover_url = ''

            # 生成图集ID
            gallery_id = generate_gallery_id(item, parent)

            # 检查图集是否已存在（通过 folder_path 查找）
            try:
                gallery = Gallery.objects.get(folder_path=folder_url)

                # 检查数据是否需要更新
                needs_update = (
                    gallery.title != item or
                    gallery.image_count != len(image_files) or
                    gallery.level != level or
                    gallery.parent != parent
                )

                # 如果封面已存在且当前计算出的封面与数据库一致，则不更新封面
                if gallery.cover_url and gallery.cover_url == cover_url:
                    # 封面一致，跳过封面更新
                    pass
                elif not gallery.cover_url and cover_url:
                    # 数据库没有封面但当前有封面，可以设置
                    needs_update = True

                if needs_update:
                    # 只更新需要更新的字段
                    gallery.title = item
                    gallery.description = f'{item}图集'
                    gallery.parent = parent
                    gallery.level = level
                    gallery.image_count = len(image_files)
                    gallery.folder_path = folder_url
                    gallery.is_active = True
                    gallery.save()

                    stats['updated'] += 1
                    print(f"  ✓ 更新: {gallery.title} ({gallery.image_count} 张图片) [ID: {gallery.id}]")
                else:
                    # 数据未变化，跳过
                    stats['skipped'] += 1
                    print(f"  ⊙ 跳过: {gallery.title} (数据未变化) [ID: {gallery.id}]")

            except Gallery.DoesNotExist:
                # 检查ID是否已被占用（可能是同名图集）
                if Gallery.objects.filter(id=gallery_id).exists():
                    # ID被占用，使用 folder_path 作为唯一标识
                    gallery_id = gallery_id + '-' + str(hash(folder_url))[:8]

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
                print(f"  + 创建: {gallery.title} ({gallery.image_count} 张图片) [ID: {gallery_id}]")

            # 从数据库集合中移除已处理的图集（通过 folder_path）
            try:
                db_gallery = Gallery.objects.get(folder_path=folder_url)
                if db_gallery.id in db_galleries:
                    db_galleries.remove(db_gallery.id)
            except Gallery.DoesNotExist:
                pass

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
                print(f"  - 删除: {gallery.title} [ID: {gallery.id}] [路径: {gallery.folder_path}]")
                gallery.delete()
                stats['deleted'] += 1
            except Gallery.DoesNotExist:
                pass

    # 递归刷新所有父图集的图片数量
    print("\n刷新父图集图片数量...")
    root_galleries = Gallery.objects.filter(parent__isnull=True)
    for root_gallery in root_galleries:
        root_gallery.refresh_image_count()

    # 自动设置封面：只为没有封面的图集设置封面
    print("\n自动设置封面（仅处理未设置封面的图集）...")
    auto_set_cover_stats = {'updated': 0}

    def find_first_child_cover(gallery):
        """递归查找第一个有封面的子图集"""
        children = gallery.children.all().order_by('sort_order', 'id')
        for child in children:
            if child.cover_url:
                return child
            # 递归查找
            found = find_first_child_cover(child)
            if found:
                return found
        return None

    # 只处理没有封面的图集
    galleries_without_cover = Gallery.objects.filter(cover_url='')
    print(f"  发现 {galleries_without_cover.count()} 个图集没有封面")

    for gallery in galleries_without_cover:
        # 获取第一张图片
        images = gallery.get_images()
        if images:
            # 有图片，使用第一张作为封面
            gallery.cover_url = images[0]['url']
            gallery.save()
            auto_set_cover_stats['updated'] += 1
            print(f"  ✓ 设置封面: {gallery.title} -> {images[0]['filename']}")
        else:
            # 没有图片，尝试使用第一个有封面的子图集
            first_child_with_cover = find_first_child_cover(gallery)
            if first_child_with_cover:
                gallery.cover_url = first_child_with_cover.cover_url
                gallery.save()
                auto_set_cover_stats['updated'] += 1
                print(f"  ✓ 设置封面(来自子图集): {gallery.title} -> {first_child_with_cover.title}")

    if auto_set_cover_stats['updated'] > 0:
        print(f"  共更新 {auto_set_cover_stats['updated']} 个图集的封面")
    else:
        print("  所有图集都有封面")

    # 打印统计信息
    print("\n" + "=" * 60)
    print("同步完成！")
    print("=" * 60)
    print(f"扫描目录: {stats['scanned']}")
    print(f"创建图集: {stats['created']}")
    print(f"更新图集: {stats['updated']}")
    print(f"跳过图集: {stats['skipped']}")
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