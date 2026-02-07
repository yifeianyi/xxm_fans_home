#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分层爬虫主控脚本
实现热数据（7天内）每小时爬取，冷数据（超过7天）每天3次爬取

路径: spider/run_tiered_crawler.py

用法:
    python spider/run_tiered_crawler.py --hot              # 只爬取热数据
    python spider/run_tiered_crawler.py --cold             # 只爬取冷数据
    python spider/run_tiered_crawler.py --all              # 爬取全部数据
    python spider/run_tiered_crawler.py --scheduled        # 根据当前时间自动选择
    python spider/run_tiered_crawler.py --stats            # 显示分层统计
"""

import argparse
import sys
import os
from datetime import datetime
from typing import Optional, Dict, Any, Tuple

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_PATH = os.path.join(PROJECT_ROOT, 'repo', 'xxm_fans_backend')

# 添加后端目录到路径（必须首先添加）
sys.path.insert(0, BACKEND_PATH)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')

import django
django.setup()

# 导入分层导出模块
from tools.spider.export_tiered import TieredViewsExporter, WorkTier, DEFAULT_HOT_DAYS
from tools.spider.crawl_views import ViewsCrawler, VIEWS_FILE
from tools.spider.import_views import ViewsImporter
from tools.spider.utils.logger import setup_views_logger, get_project_root

logger = setup_views_logger("run_tiered_crawler")

# 冷数据爬取时段（24小时制）
COLD_CRAWL_HOURS = [0, 8, 16]  # 00:00, 08:00, 16:00


def get_current_hour() -> int:
    """获取当前小时"""
    return datetime.now().hour


def should_crawl_cold_now() -> bool:
    """
    判断当前是否应该爬取冷数据
    冷数据每天只在指定时段爬取
    
    Returns:
        bool: 是否应该爬取冷数据
    """
    current_hour = get_current_hour()
    return current_hour in COLD_CRAWL_HOURS


def run_crawl_pipeline(
    tier: WorkTier, 
    views_file: str,
    force: bool = False,
    request_delay_min: float = 1.0,
    request_delay_max: float = 3.0,
    max_retries: int = 2
) -> Tuple[bool, Dict[str, Any]]:
    """
    执行指定分层的完整爬取流程
    
    Args:
        tier: 分层类型 (HOT/COLD)
        views_file: views.json 文件路径
        force: 是否强制重新导入
        request_delay_min: 最小请求延迟
        request_delay_max: 最大请求延迟
        max_retries: 最大重试次数
        
    Returns:
        Tuple[bool, dict]: (是否成功, 执行信息)
    """
    result_info = {
        "tier": tier.value,
        "start_time": datetime.now().isoformat(),
        "steps": {}
    }
    
    logger.info("=" * 60)
    logger.info(f"开始执行{tier.value.upper()}数据爬取流程")
    logger.info("=" * 60)

    # 1. 导出数据
    logger.info(f"\n[1/3] 导出{tier.value.upper()}数据...")
    exporter = TieredViewsExporter()
    
    if tier == WorkTier.HOT:
        success, filepath, info = exporter.export_hot()
    elif tier == WorkTier.COLD:
        success, filepath, info = exporter.export_cold()
    else:
        success, filepath, info = exporter.export_all()
    
    if not success:
        error_msg = info.get('error', '导出失败')
        logger.error(f"导出失败: {error_msg}")
        result_info["steps"]["export"] = {"success": False, "error": error_msg}
        return False, result_info
    
    export_count = info.get('total_count', 0)
    logger.info(f"✓ 导出成功: {export_count} 条记录 -> {filepath}")
    result_info["steps"]["export"] = {"success": True, "count": export_count, "file": filepath}
    
    if export_count == 0:
        logger.info(f"没有{tier.value.upper()}数据需要爬取，流程结束")
        result_info["status"] = "skipped"
        return True, result_info

    # 2. 爬取数据（临时修改 VIEWS_FILE 指向导出的文件）
    logger.info(f"\n[2/3] 爬取B站数据...")
    
    # 备份原始文件路径
    original_views_file = VIEWS_FILE
    
    try:
        # 临时替换 views.json 为导出的文件
        import tools.spider.crawl_views as crawl_module
        crawl_module.VIEWS_FILE = filepath
        
        crawler = ViewsCrawler(
            request_delay_min=request_delay_min,
            request_delay_max=request_delay_max,
            max_retries=max_retries
        )
        
        output_path = crawler.crawl()
        logger.info(f"✓ 爬取完成: {output_path}")
        result_info["steps"]["crawl"] = {"success": True, "output": output_path}
        
    except Exception as e:
        logger.error(f"爬取失败: {e}")
        result_info["steps"]["crawl"] = {"success": False, "error": str(e)}
        return False, result_info
    finally:
        # 恢复原始路径
        crawl_module.VIEWS_FILE = original_views_file

    # 3. 导入数据
    logger.info(f"\n[3/3] 导入数据到SQLite...")
    importer = ViewsImporter()
    
    try:
        importer.connect()
        
        # 从爬取结果文件中获取日期和小时
        crawl_time = datetime.now()
        date_str = crawl_time.strftime('%Y-%m-%d')
        hour_str = crawl_time.strftime('%H')
        
        success = importer.import_by_date(date_str, hour_str, auto_find=False, force=force)
        importer.close()
        
        if success:
            logger.info("✓ 导入成功")
            result_info["steps"]["import"] = {"success": True}
        else:
            logger.error("导入失败")
            result_info["steps"]["import"] = {"success": False, "error": "导入失败"}
            return False, result_info
            
    except Exception as e:
        logger.error(f"导入失败: {e}")
        result_info["steps"]["import"] = {"success": False, "error": str(e)}
        return False, result_info

    result_info["status"] = "success"
    result_info["end_time"] = datetime.now().isoformat()
    
    logger.info("\n" + "=" * 60)
    logger.info(f"{tier.value.upper()}数据爬取流程执行成功!")
    logger.info("=" * 60)
    
    return True, result_info


def run_scheduled_crawl(force: bool = False) -> Tuple[bool, Dict[str, Any]]:
    """
    根据当前时间执行调度爬取
    - 每小时都爬取热数据
    - 只在指定时段爬取冷数据
    
    Args:
        force: 是否强制重新导入
        
    Returns:
        Tuple[bool, dict]: (是否成功, 执行信息)
    """
    current_hour = get_current_hour()
    current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    
    logger.info("=" * 60)
    logger.info(f"执行调度爬取 - 当前时间: {current_time}")
    logger.info(f"当前时段: {current_hour}:00")
    logger.info("=" * 60)
    
    results = {
        "scheduled_time": current_time,
        "current_hour": current_hour,
        "hot": None,
        "cold": None,
    }
    
    # 1. 始终爬取热数据（每小时）
    logger.info("\n【阶段1】爬取热数据（每小时执行）")
    hot_success, hot_info = run_crawl_pipeline(
        tier=WorkTier.HOT,
        views_file="views_hot.json",
        force=force
    )
    results["hot"] = hot_info
    
    if not hot_success:
        logger.warning("热数据爬取失败，继续执行冷数据检查...")
    
    # 2. 只在指定时段爬取冷数据
    if should_crawl_cold_now():
        logger.info(f"\n【阶段2】爬取冷数据（{current_hour}:00 时段执行）")
        cold_success, cold_info = run_crawl_pipeline(
            tier=WorkTier.COLD,
            views_file="views_cold.json",
            force=force
        )
        results["cold"] = cold_info
        
        if not cold_success:
            logger.error("冷数据爬取失败")
    else:
        next_cold_hours = [h for h in COLD_CRAWL_HOURS if h > current_hour]
        if next_cold_hours:
            next_cold = next_cold_hours[0]
        else:
            next_cold = COLD_CRAWL_HOURS[0]
        logger.info(f"\n【阶段2】跳过冷数据爬取（不在爬取时段）")
        logger.info(f"        下次爬取时间: {next_cold}:00")
        results["cold"] = {"skipped": True, "next_scheduled": f"{next_cold}:00"}
    
    # 判断整体是否成功
    overall_success = results["hot"] and results["hot"].get("status") == "success"
    
    logger.info("\n" + "=" * 60)
    logger.info("调度爬取执行完成")
    logger.info("=" * 60)
    
    return overall_success, results


def main():
    parser = argparse.ArgumentParser(
        description='分层爬虫主控脚本 - 热数据每小时爬取，冷数据每天3次',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用示例:
  # 只爬取热数据（7天内发布的作品）- 每小时执行
  python run_tiered_crawler.py --hot
  
  # 只爬取冷数据（7天前发布的作品）- 每天0/8/16点执行
  python run_tiered_crawler.py --cold
  
  # 爬取全部数据（热+冷）
  python run_tiered_crawler.py --all
  
  # 根据当前时间自动选择（推荐用于定时任务）
  python run_tiered_crawler.py --scheduled
  
  # 显示分层统计信息
  python run_tiered_crawler.py --stats
  
  # 强制重新导入（即使数据已存在）
  python run_tiered_crawler.py --hot --force
  
  # 调整请求延迟（秒）
  python run_tiered_crawler.py --hot --delay-min 0.5 --delay-max 1.5
        """
    )
    
    # 执行模式
    mode_group = parser.add_mutually_exclusive_group()
    mode_group.add_argument('--hot', action='store_true', help='只爬取热数据（7天内）')
    mode_group.add_argument('--cold', action='store_true', help='只爬取冷数据（7天前）')
    mode_group.add_argument('--all', action='store_true', help='爬取全部数据')
    mode_group.add_argument('--scheduled', action='store_true', help='根据时间自动选择（推荐）')
    mode_group.add_argument('--stats', action='store_true', help='显示分层统计信息')
    
    # 可选参数
    parser.add_argument('--force', action='store_true', help='强制重新导入')
    parser.add_argument('--delay-min', type=float, default=1.0, help='最小请求延迟（秒）')
    parser.add_argument('--delay-max', type=float, default=3.0, help='最大请求延迟（秒）')
    parser.add_argument('--retries', type=int, default=2, help='最大重试次数')
    
    args = parser.parse_args()
    
    # 显示统计信息
    if args.stats:
        exporter = TieredViewsExporter()
        stats = exporter.get_tier_stats()
        
        print("\n" + "=" * 70)
        print("分层爬虫统计信息")
        print("=" * 70)
        print(f"\n📊 热数据阈值: {stats['hot_days_threshold']} 天")
        print(f"📅 分层截止时间: {stats['cutoff_date'][:10]}")
        print(f"📁 总作品数: {stats['total_works']}")
        
        print(f"\n🔥 热数据（最近{stats['hot_days_threshold']}天）: {stats['hot_works']['count']} 条")
        print(f"   爬取频率: 每小时")
        if stats['hot_works']['newest']:
            print(f"   最新: {stats['hot_works']['newest']['title'][:45]}...")
        if stats['hot_works']['oldest']:
            print(f"   最旧: {stats['hot_works']['oldest']['title'][:45]}...")
        
        print(f"\n❄️ 冷数据（{stats['hot_days_threshold']}天前）: {stats['cold_works']['count']} 条")
        print(f"   爬取频率: 每天3次 (00:00, 08:00, 16:00)")
        if stats['cold_works']['newest']:
            print(f"   最新: {stats['cold_works']['newest']['title'][:45]}...")
        if stats['cold_works']['oldest']:
            print(f"   最旧: {stats['cold_works']['oldest']['title'][:45]}...")
        
        print("\n" + "=" * 70)
        print("💡 当前时段爬取策略:")
        current_hour = get_current_hour()
        print(f"   当前时间: {current_hour}:00")
        print(f"   热数据: 始终爬取")
        if should_crawl_cold_now():
            print(f"   冷数据: ✅ 本时段执行爬取")
        else:
            next_cold = None
            for h in COLD_CRAWL_HOURS:
                if h > current_hour:
                    next_cold = h
                    break
            if next_cold is None:
                next_cold = COLD_CRAWL_HOURS[0]
            print(f"   冷数据: ⏸️ 跳过（下次: {next_cold}:00）")
        print("=" * 70 + "\n")
        
        sys.exit(0)
    
    # 执行爬取
    success = False
    
    try:
        if args.hot:
            success, info = run_crawl_pipeline(
                tier=WorkTier.HOT,
                views_file="views_hot.json",
                force=args.force,
                request_delay_min=args.delay_min,
                request_delay_max=args.delay_max,
                max_retries=args.retries
            )
        elif args.cold:
            success, info = run_crawl_pipeline(
                tier=WorkTier.COLD,
                views_file="views_cold.json",
                force=args.force,
                request_delay_min=args.delay_min,
                request_delay_max=args.delay_max,
                max_retries=args.retries
            )
        elif args.all:
            # 先爬热数据，再爬冷数据
            hot_success, hot_info = run_crawl_pipeline(
                tier=WorkTier.HOT,
                views_file="views_hot.json",
                force=args.force,
                request_delay_min=args.delay_min,
                request_delay_max=args.delay_max,
                max_retries=args.retries
            )
            cold_success, cold_info = run_crawl_pipeline(
                tier=WorkTier.COLD,
                views_file="views_cold.json",
                force=args.force,
                request_delay_min=args.delay_min,
                request_delay_max=args.delay_max,
                max_retries=args.retries
            )
            success = hot_success and cold_success
        elif args.scheduled:
            success, info = run_scheduled_crawl(force=args.force)
        else:
            # 默认执行调度模式
            print("使用默认模式：--scheduled（使用 --help 查看所有选项）")
            success, info = run_scheduled_crawl(force=args.force)
            
    except KeyboardInterrupt:
        logger.warning("用户中断爬取任务")
        sys.exit(130)
    except Exception as e:
        logger.error(f"执行失败: {e}")
        import traceback
        logger.error(traceback.format_exc())
        success = False
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
