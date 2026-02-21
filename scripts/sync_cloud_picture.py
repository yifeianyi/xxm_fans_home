#!/usr/bin/env python3
"""
直播云图批量入库脚本
将 media/cloud_picture 目录下的直播云图导入到图集系统
按年份分组，自动识别日期并创建图集
"""

import os
import sys
import django
import re
from datetime import datetime

# 设置 Django 环境
sys.path.insert(0, '/home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')
django.setup()

from gallery.models import Gallery
from django.conf import settings
from django.db import models


def parse_date_from_filename(filename):
    """
    从文件名中解析日期
    支持格式: 20190425.jpg, 2019-04-25.jpg, 2019_04_25.jpg
    """
    # 移除文件扩展名
    name_without_ext = os.path.splitext(filename)[0]

    # 匹配日期格式: YYYYMMDD
    pattern1 = r'(\d{4})(\d{2})(\d{2})'
    # 匹配日期格式: YYYY-MM-DD
    pattern2 = r'(\d{4})-(\d{2})-(\d{2})'
    # 匹配日期格式: YYYY_MM_DD
    pattern3 = r'(\d{4})_(\d{2})_(\d{2})'

    for pattern in [pattern1, pattern2, pattern3]:
        match = re.match(pattern, name_without_ext)
        if match:
            year, month, day = match.groups()
            try:
                date_obj = datetime(int(year), int(month), int(day))
                # 格式化为中文日期: 2019年4月25日
                formatted_date = date_obj.strftime('%Y年%-m月%-d日')
                return {
                    'year': year,
                    'month': month,
                    'day': day,
                    'date_obj': date_obj,
                    'formatted': formatted_date,
                    'sort_key': int(f"{year}{month}{day}")
                }
            except ValueError:
                continue

    return None


def sync_cloud_picture():
    """同步直播云图到图集系统"""
    print("=" * 60)
    print("直播云图批量入库")
    print("=" * 60)

    cloud_picture_root = os.path.join(settings.MEDIA_ROOT, 'cloud_picture')

    if not os.path.exists(cloud_picture_root):
        print(f"错误: 云图目录不存在: {cloud_picture_root}")
        return

    print(f"\n扫描目录: {cloud_picture_root}")

    # 统计信息
    stats = {
        'scanned_years': 0,
        'scanned_images': 0,
        'created_years': 0,
        'updated_years': 0,
        'created_galleries': 0,
        'updated_galleries': 0,
        'errors': []
    }

    # 创建根图集 "直播云图"（如果不存在）
    root_gallery_id = 'livestream-cloud-picture'
    root_folder_url = '/media/cloud_picture/'

    try:
        root_gallery = Gallery.objects.get(id=root_gallery_id)
        stats['scanned_years'] += 1
        print(f"  ⊙ 根图集已存在: {root_gallery.title}")
    except Gallery.DoesNotExist:
        root_gallery = Gallery.objects.create(
            id=root_gallery_id,
            title='直播云图',
            description='直播云图集，按日期分类',
            cover_url='',
            parent=None,
            level=0,
            image_count=0,
            folder_path=root_folder_url,
            tags=['直播', '云图'],
            is_active=True
        )
        stats['created_years'] += 1
        print(f"  + 创建根图集: {root_gallery.title}")

    # 扫描年份目录
    year_folders = sorted([f for f in os.listdir(cloud_picture_root)
                          if os.path.isdir(os.path.join(cloud_picture_root, f))
                          and f != 'thumbnails'
                          and re.match(r'^\d{4}$', f)])

    print(f"\n发现 {len(year_folders)} 个年份目录")

    for year_folder in year_folders:
        year_path = os.path.join(cloud_picture_root, year_folder)
        year_folder_url = f'/media/cloud_picture/{year_folder}/'

        # 检查或创建年份图集
        year_gallery_id = f'{root_gallery_id}-{year_folder}'

        year_gallery = Gallery.objects.filter(folder_path=year_folder_url).first()
        if year_gallery:
            # 更新年份图集信息
            year_gallery.parent = root_gallery
            year_gallery.level = 1
            year_gallery.save()
            stats['updated_years'] += 1
            print(f"\n  ✓ 更新年份图集: {year_folder}年")
        else:
            year_gallery = Gallery.objects.create(
                id=year_gallery_id,
                title=f'{year_folder}年',
                description=f'{year_folder}年直播云图',
                cover_url='',
                parent=root_gallery,
                level=1,
                image_count=0,
                folder_path=year_folder_url,
                tags=[year_folder],
                is_active=True
            )
            stats['created_years'] += 1
            print(f"\n  + 创建年份图集: {year_folder}年")

        # 扫描年份目录下的图片文件
        try:
            image_files = sorted([f for f in os.listdir(year_path)
                                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
                                and f != 'cover.jpg'])
        except PermissionError as e:
            error_msg = f"无法访问目录 {year_path}: {e}"
            stats['errors'].append(error_msg)
            print(f"  ✗ {error_msg}")
            continue

        print(f"    发现 {len(image_files)} 张图片")

        # 统计该年份的图片数量
        year_gallery.image_count = len(image_files)

        # 为每个图片创建独立的日期图集（可选）
        # 这里我们选择将图片作为日期图集，每个日期一张图片
        for image_file in image_files:
            date_info = parse_date_from_filename(image_file)

            if date_info:
                # 创建日期图集
                date_gallery_id = f'{year_gallery_id}-{date_info["sort_key"]}'
                date_folder_url = year_folder_url

                # 检查是否已存在该日期的图集
                date_gallery = Gallery.objects.filter(id=date_gallery_id).first()
                if date_gallery:
                    # 更新图片信息
                    date_gallery.cover_url = f'{date_folder_url}{image_file}'
                    date_gallery.image_count = 1
                    date_gallery.save()
                    stats['updated_galleries'] += 1
                else:
                    date_gallery = Gallery.objects.create(
                        id=date_gallery_id,
                        title=date_info['formatted'],
                        description=f'{date_info["formatted"]}直播云图',
                        cover_url=f'{date_folder_url}{image_file}',
                        parent=year_gallery,
                        level=2,
                        image_count=1,
                        folder_path=date_folder_url,
                        tags=[year_folder, date_info['formatted']],
                        is_active=True
                    )
                    stats['created_galleries'] += 1
                    print(f"      + {date_info['formatted']}: {image_file}")
            else:
                print(f"      ⊙ 跳过无法识别日期的图片: {image_file}")

        # 设置年份图集封面（使用第一张图片）
        if image_files:
            first_image = image_files[0]
            year_gallery.cover_url = f'{year_folder_url}{first_image}'
            year_gallery.save()

        year_gallery.save()
        stats['scanned_images'] += len(image_files)

    # 刷新根图集的图片数量
    root_gallery.refresh_image_count()

    # 打印统计信息
    print("\n" + "=" * 60)
    print("入库完成！")
    print("=" * 60)
    print(f"扫描年份: {stats['scanned_years']}")
    print(f"扫描图片: {stats['scanned_images']}")
    print(f"创建年份图集: {stats['created_years']}")
    print(f"更新年份图集: {stats['updated_years']}")
    print(f"创建日期图集: {stats['created_galleries']}")
    print(f"更新日期图集: {stats['updated_galleries']}")

    if stats['errors']:
        print(f"\n错误数量: {len(stats['errors'])}")
        for error in stats['errors']:
            print(f"  - {error}")
    else:
        print("\n没有错误！")

    # 显示图集统计
    print("\n图集统计:")
    total_galleries = Gallery.objects.count()
    cloud_galleries = Gallery.objects.filter(folder_path__startswith='/media/cloud_picture/').count()
    cloud_images = Gallery.objects.filter(folder_path__startswith='/media/cloud_picture/').aggregate(total=models.Sum('image_count'))['total'] or 0
    print(f"  系统总图集数: {total_galleries}")
    print(f"  云图图集数: {cloud_galleries}")
    print(f"  云图图片数: {cloud_images}")


if __name__ == "__main__":
    sync_cloud_picture()