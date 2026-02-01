#!/usr/bin/env python3
"""
直播云图导入到直播日历脚本
将 media/cloud_picture 目录下的直播云图导入到 Livestream 表的 danmaku_cloud_url 字段
根据文件名中的日期自动匹配对应的直播记录
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

from livestream.models import Livestream
from django.conf import settings


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
                return date_obj.date()
            except ValueError:
                continue

    return None


def import_cloud_picture():
    """将云图导入到直播日历"""
    print("=" * 60)
    print("直播云图导入到直播日历")
    print("=" * 60)

    cloud_picture_root = os.path.join(settings.MEDIA_ROOT, 'cloud_picture')

    if not os.path.exists(cloud_picture_root):
        print(f"错误: 云图目录不存在: {cloud_picture_root}")
        return

    print(f"\n扫描目录: {cloud_picture_root}")

    # 统计信息
    stats = {
        'scanned_files': 0,
        'matched_livestreams': 0,
        'unmatched_files': 0,
        'skipped_existing': 0,
        'errors': []
    }

    # 获取所有年份目录
    year_folders = sorted([f for f in os.listdir(cloud_picture_root)
                          if os.path.isdir(os.path.join(cloud_picture_root, f))
                          and f != 'thumbnails'
                          and re.match(r'^\d{4}$', f)])

    print(f"\n发现 {len(year_folders)} 个年份目录")

    # 遍历所有云图文件
    for year_folder in year_folders:
        year_path = os.path.join(cloud_picture_root, year_folder)

        print(f"\n处理 {year_folder} 年:")

        # 获取该年份下的所有图片文件
        try:
            image_files = sorted([f for f in os.listdir(year_path)
                                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp'))
                                and f != 'cover.jpg'])
        except PermissionError as e:
            error_msg = f"无法访问目录 {year_path}: {e}"
            stats['errors'].append(error_msg)
            print(f"  ✗ {error_msg}")
            continue

        print(f"  发现 {len(image_files)} 张云图文件")

        for image_file in image_files:
            stats['scanned_files'] += 1

            # 解析日期
            date_obj = parse_date_from_filename(image_file)
            if not date_obj:
                stats['unmatched_files'] += 1
                print(f"    ⊙ 跳过无法识别日期的文件: {image_file}")
                continue

            # 生成云图URL
            cloud_picture_url = f'/media/cloud_picture/{year_folder}/{image_file}'

            # 查找对应的直播记录
            try:
                livestream = Livestream.objects.get(date=date_obj)

                # 检查是否已有云图
                if livestream.danmaku_cloud_url:
                    stats['skipped_existing'] += 1
                    print(f"    ⊙ 跳过 (已有云图): {date_obj} - {image_file}")
                    continue

                # 更新云图URL
                livestream.danmaku_cloud_url = cloud_picture_url
                livestream.save(update_fields=['danmaku_cloud_url', 'updated_at'])

                stats['matched_livestreams'] += 1
                print(f"    ✓ 已导入: {date_obj} - {image_file}")

            except Livestream.DoesNotExist:
                stats['unmatched_files'] += 1
                print(f"    ⊙ 未找到对应直播记录: {date_obj} - {image_file}")
            except Exception as e:
                error_msg = f"处理文件 {image_file} 时出错: {e}"
                stats['errors'].append(error_msg)
                print(f"    ✗ {error_msg}")

    # 打印统计信息
    print("\n" + "=" * 60)
    print("导入完成！")
    print("=" * 60)
    print(f"扫描文件: {stats['scanned_files']}")
    print(f"成功导入: {stats['matched_livestreams']}")
    print(f"跳过已有: {stats['skipped_existing']}")
    print(f"未匹配: {stats['unmatched_files']}")

    if stats['errors']:
        print(f"\n错误数量: {len(stats['errors'])}")
        for error in stats['errors']:
            print(f"  - {error}")
    else:
        print("\n没有错误！")

    # 显示数据库统计
    print("\n数据库统计:")
    total_livestreams = Livestream.objects.count()
    livestreams_with_cloud = Livestream.objects.filter(danmaku_cloud_url__icontains='cloud_picture').count()
    print(f"  总直播记录数: {total_livestreams}")
    print(f"  已有云图记录: {livestreams_with_cloud}")


if __name__ == "__main__":
    import_cloud_picture()