"""
下载 WorkStatic 中的B站封面到本地
将使用B站网络链接的封面下载到本地并更新数据库
"""
import os
import sys
import django
import time
import random

# 设置 Django 环境
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'repo', 'xxm_fans_backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')
django.setup()

from data_analytics.models import WorkStatic
from core.thumbnail_generator import ThumbnailGenerator
from tools.bilibili import BilibiliCoverDownloader
from datetime import datetime

# 下载配置
DOWNLOAD_DELAY_MIN = 1.0   # 最小延迟时间（秒）
DOWNLOAD_DELAY_MAX = 3.0   # 最大延迟时间（秒）
BATCH_SIZE = 5             # 每批次处理数量


def download_workstatic_covers(dry_run=False):
    """
    下载 WorkStatic 中的B站封面到本地

    Args:
        dry_run: 是否只显示将要下载的封面，不实际下载
    """
    print("=" * 80)
    print("WorkStatic 封面下载工具")
    print("=" * 80)

    # 统计信息
    stats = {
        'total': 0,
        'bilibili_covers': 0,
        'local_covers': 0,
        'downloaded': 0,
        'skipped': 0,
        'failed': 0,
        'errors': []
    }

    # 查询所有作品
    works = WorkStatic.objects.all()
    stats['total'] = works.count()

    print(f"\n总共找到 {stats['total']} 个作品")
    print("=" * 80)

    # 初始化封面下载器
    downloader = BilibiliCoverDownloader()

    # 遍历所有作品
    batch_count = 0
    for idx, work in enumerate(works, 1):
        print(f"\n处理作品 #{work.id}: {work.title}")
        print(f"  平台: {work.platform}")
        print(f"  作品ID: {work.work_id}")

        if not work.cover_url:
            print(f"  ⚠️  无封面URL，跳过")
            stats['local_covers'] += 1
            continue

        print(f"  当前封面: {work.cover_url}")

        # 检查是否为B站链接
        is_bilibili_url = work.cover_url.startswith('http') and (
            'bilibili.com' in work.cover_url or
            'hdslb.com' in work.cover_url or
            'i0.hdslb.com' in work.cover_url or
            'i1.hdslb.com' in work.cover_url or
            'i2.hdslb.com' in work.cover_url
        )

        if not is_bilibili_url:
            print(f"  ✅ 非B站链接或已是本地路径，跳过")
            stats['local_covers'] += 1
            continue

        stats['bilibili_covers'] += 1
        print(f"  🎯 检测到B站链接，准备下载")

        # 生成本地文件名
        # 使用 work_id 作为文件名，确保唯一性
        # 如果 work_id 是BV号，直接使用；否则使用 work_id
        if work.work_id.startswith('BV'):
            filename = f"{work.work_id}.jpg"
        else:
            # 如果不是BV号，添加平台前缀
            filename = f"{work.platform}_{work.work_id}.jpg"

        # 下载封面到 data_analytics/covers 目录
        sub_path = "data_analytics/covers"

        if dry_run:
            print(f"  [DRY RUN] 将下载到: {sub_path}/{filename}")
            stats['downloaded'] += 1
            # 预览模式下也添加延迟，避免输出过快
            time.sleep(0.1)
            continue

        try:
            # 下载封面
            local_path = downloader.download(work.cover_url, sub_path, filename, check_exists=True)

            if local_path:
                # 更新数据库中的封面URL
                old_cover_url = work.cover_url
                work.cover_url = f"/media/{local_path}"
                work.save()

                # 生成缩略图
                try:
                    thumbnail_path = ThumbnailGenerator.generate_thumbnail(local_path)
                    if thumbnail_path != local_path:
                        print(f"  ✅ 缩略图生成成功: {thumbnail_path}")
                except Exception as e:
                    print(f"  ⚠️  缩略图生成失败: {e}")

                print(f"  ✅ 封面下载成功")
                print(f"     旧URL: {old_cover_url}")
                print(f"     新URL: {work.cover_url}")
                stats['downloaded'] += 1
                batch_count += 1
            else:
                print(f"  ❌ 封面下载失败")
                stats['failed'] += 1

        except Exception as e:
            print(f"  ❌ 处理失败: {e}")
            stats['failed'] += 1
            stats['errors'].append(f"ID={work.id}, work_id={work.work_id}: {str(e)}")

        # 添加随机延迟，避免请求过快
        # 每下载一个封面后延迟 1-3 秒
        if local_path and not dry_run:
            delay = random.uniform(DOWNLOAD_DELAY_MIN, DOWNLOAD_DELAY_MAX)
            print(f"  ⏱️  等待 {delay:.1f} 秒后继续...")
            time.sleep(delay)

        # 每处理 BATCH_SIZE 个作品后，显示进度并休息更长时间
        if batch_count >= BATCH_SIZE and not dry_run:
            print(f"\n📊 已处理 {idx}/{stats['total']} 个作品，休息 {BATCH_SIZE * 2} 秒...")
            time.sleep(BATCH_SIZE * 2)
            batch_count = 0

    # 打印统计信息
    print("\n" + "=" * 80)
    print("处理完成")
    print("=" * 80)
    print(f"总作品数: {stats['total']}")
    print(f"B站封面: {stats['bilibili_covers']}")
    print(f"本地封面: {stats['local_covers']}")
    print(f"已下载: {stats['downloaded']}")
    print(f"跳过: {stats['skipped']}")
    print(f"失败: {stats['failed']}")

    if stats['errors']:
        print(f"\n错误列表:")
        for error in stats['errors']:
            print(f"  - {error}")

    print("\n" + "=" * 80)
    return stats


def main():
    """主函数"""
    import argparse

    parser = argparse.ArgumentParser(description='下载 WorkStatic 中的B站封面到本地')
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='只显示将要下载的封面，不实际下载'
    )
    parser.add_argument(
        '--force',
        action='store_true',
        help='强制重新下载已存在的封面'
    )

    args = parser.parse_args()

    print(f"\n执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"模式: {'DRY RUN (预览)' if args.dry_run else '实际执行'}")
    print(f"强制下载: {'是' if args.force else '否'}")

    # 执行下载
    stats = download_workstatic_covers(dry_run=args.dry_run)

    # 退出码
    if stats['failed'] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
