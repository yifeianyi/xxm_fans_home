#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主控脚本
整合导出、爬取、导入流程

路径: spider/run_views_crawler.py

用法:
    python spider/run_views_crawler.py --full        # 完整流程
    python spider/run_views_crawler.py --export-only # 仅导出
    python spider/run_views_crawler.py --crawl-only  # 仅爬取
    python spider/run_views_crawler.py --import-only # 仅导入
"""

import argparse
import sys
import os

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_PATH = os.path.join(PROJECT_ROOT, 'repo', 'xxm_fans_backend')

# 添加后端目录到路径（必须首先添加）
sys.path.insert(0, BACKEND_PATH)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')

import django
django.setup()

# 通过 tools 包导入 spider 模块
from tools.spider.export_views import ViewsExporter, OUTPUT_FILE
from tools.spider.crawl_views import ViewsCrawler, VIEWS_FILE
from tools.spider.import_views import ViewsImporter
from tools.spider.utils.logger import setup_views_logger

logger = setup_views_logger("run_views_crawler")


def run_full_pipeline(force: bool = False):
    """执行完整流程
    
    Args:
        force: 是否强制重新导入（即使数据已存在）
    """
    logger.info("=" * 60)
    logger.info("开始执行完整流程: 导出 -> 爬取 -> 导入")
    logger.info("=" * 60)

    # 1. 导出数据
    logger.info("\n[1/3] 导出作品数据...")
    exporter = ViewsExporter()
    if not exporter.export():
        logger.error("导出失败，终止流程")
        return False

    # 2. 爬取数据
    logger.info("\n[2/3] 爬取B站数据...")
    crawler = ViewsCrawler(request_delay_min=1.0, request_delay_max=3.0, max_retries=2)
    try:
        output_path = crawler.crawl()
        logger.info(f"爬取完成: {output_path}")
    except Exception as e:
        logger.error(f"爬取失败: {e}")
        return False

    # 3. 导入数据
    logger.info("\n[3/3] 导入数据到SQLite...")
    importer = ViewsImporter()
    try:
        importer.connect()
        # 自动查找并导入最新数据文件
        success = importer.import_latest(force=force)
        importer.close()
        if not success:
            logger.error("导入失败")
            return False
    except Exception as e:
        logger.error(f"导入失败: {e}")
        return False

    logger.info("\n" + "=" * 60)
    logger.info("完整流程执行成功!")
    logger.info("=" * 60)
    return True


def main():
    parser = argparse.ArgumentParser(
        description='B站投稿数据爬虫',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 执行完整流程（导出 -> 爬取 -> 导入）
  python run_views_crawler.py
  
  # 仅导入最新数据文件（自动查找）
  python run_views_crawler.py --import-only
  
  # 导入指定日期的数据
  python run_views_crawler.py --import-only --date 2026-02-06 --hour 14
  
  # 强制重新导入（即使数据已存在）
  python run_views_crawler.py --import-only --force
        """
    )
    parser.add_argument('--full', action='store_true', help='执行完整流程（默认）')
    parser.add_argument('--export-only', action='store_true', help='仅导出 views.json')
    parser.add_argument('--crawl-only', action='store_true', help='仅爬取数据')
    parser.add_argument('--import-only', action='store_true', help='仅导入数据（自动查找最新文件）')
    parser.add_argument('--date', type=str, help='指定日期 (YYYY-MM-DD)，用于导入')
    parser.add_argument('--hour', type=str, help='指定小时 (HH)，用于导入')
    parser.add_argument('--force', action='store_true', help='强制重新导入（即使数据已存在）')

    args = parser.parse_args()

    if not any([args.full, args.export_only, args.crawl_only, args.import_only]):
        args.full = True

    success = False

    try:
        if args.full:
            success = run_full_pipeline(force=args.force)
        elif args.export_only:
            exporter = ViewsExporter()
            success = exporter.export()
        elif args.crawl_only:
            crawler = ViewsCrawler(request_delay_min=1.0, request_delay_max=3.0, max_retries=2)
            output_path = crawler.crawl()
            success = True
            print(f"爬取完成: {output_path}")
        elif args.import_only:
            importer = ViewsImporter()
            importer.connect()
            if args.date or args.hour:
                # 指定了日期/小时，按指定导入
                success = importer.import_by_date(args.date, args.hour, auto_find=False, force=args.force)
            else:
                # 未指定，自动查找最新文件
                logger.info("未指定日期/小时，自动查找最新数据文件...")
                success = importer.import_latest(force=args.force)
            importer.close()
    except Exception as e:
        logger.error(f"执行失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        success = False

    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
