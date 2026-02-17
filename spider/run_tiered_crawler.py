#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分层爬虫主控脚本
实现热数据（7天内）每小时爬取，冷数据（超过7天）每天3次爬取
支持多线程并发爬取热数据和冷数据，完成后统一导入

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
import threading
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from typing import Optional, Dict, Any, Tuple, List

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_PATH = os.path.join(PROJECT_ROOT, 'repo', 'xxm_fans_backend')

# 添加后端目录到路径（必须首先添加）
sys.path.insert(0, BACKEND_PATH)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')

import django
django.setup()

# Django 时区支持（必须在 django.setup() 之后导入）
from django.utils import timezone

# 导入分层导出模块
from tools.spider.export_tiered import TieredViewsExporter, WorkTier, DEFAULT_HOT_DAYS
from tools.spider.crawl_views import ViewsCrawler, VIEWS_FILE
from tools.spider.import_views import ViewsImporter
from tools.spider.utils.logger import setup_views_logger, get_project_root

logger = setup_views_logger("run_tiered_crawler")

# 冷数据爬取时段（24小时制）
COLD_CRAWL_HOURS = [0, 8, 16]  # 00:00, 08:00, 16:00

# 线程锁，用于日志同步
log_lock = threading.Lock()


def get_current_hour() -> int:
    """获取当前小时（使用 Django 本地时区）"""
    return timezone.localtime().hour


def should_crawl_cold_now() -> bool:
    """
    判断当前是否应该爬取冷数据
    冷数据每天只在指定时段爬取
    
    Returns:
        bool: 是否应该爬取冷数据
    """
    current_hour = get_current_hour()
    return current_hour in COLD_CRAWL_HOURS


def export_and_crawl_tier(
    tier: WorkTier,
    force: bool = False,
    request_delay_min: float = 1.0,
    request_delay_max: float = 3.0,
    max_retries: int = 2
) -> Tuple[bool, Dict[str, Any], Optional[str]]:
    """
    执行指定分层的导出和爬取流程（不包含导入）
    
    Args:
        tier: 分层类型 (HOT/COLD)
        force: 是否强制重新导入
        request_delay_min: 最小请求延迟
        request_delay_max: 最大请求延迟
        max_retries: 最大重试次数
        
    Returns:
        Tuple[bool, dict, Optional[str]]: (是否成功, 执行信息, 输出文件路径)
    """
    result_info = {
        "tier": tier.value,
        "start_time": datetime.now().isoformat(),
        "steps": {}
    }
    output_path = None
    
    with log_lock:
        logger.info("=" * 60)
        logger.info(f"开始执行{tier.value.upper()}数据爬取流程")
        logger.info("=" * 60)

    # 1. 导出数据
    with log_lock:
        logger.info(f"\n[1/2] 导出{tier.value.upper()}数据...")
    exporter = TieredViewsExporter()
    
    if tier == WorkTier.HOT:
        success, filepath, info = exporter.export_hot()
    elif tier == WorkTier.COLD:
        success, filepath, info = exporter.export_cold()
    else:
        success, filepath, info = exporter.export_all()
    
    if not success:
        error_msg = info.get('error', '导出失败')
        with log_lock:
            logger.error(f"导出失败: {error_msg}")
        result_info["steps"]["export"] = {"success": False, "error": error_msg}
        return False, result_info, None
    
    export_count = info.get('total_count', 0)
    with log_lock:
        logger.info(f"✓ 导出成功: {export_count} 条记录 -> {filepath}")
    result_info["steps"]["export"] = {"success": True, "count": export_count, "file": filepath}
    
    if export_count == 0:
        with log_lock:
            logger.info(f"没有{tier.value.upper()}数据需要爬取")
        result_info["status"] = "skipped"
        result_info["end_time"] = datetime.now().isoformat()
        return True, result_info, None

    # 2. 爬取数据
    with log_lock:
        logger.info(f"\n[2/2] 爬取B站{tier.value.upper()}数据...")
    
    # 备份原始文件路径
    original_views_file = VIEWS_FILE
    
    try:
        # 临时替换 views.json 为导出的文件
        import tools.spider.crawl_views as crawl_module
        crawl_module.VIEWS_FILE = filepath
        
        # 创建爬虫实例，传入 tier 参数以区分输出文件名
        crawler = ViewsCrawler(
            request_delay_min=request_delay_min,
            request_delay_max=request_delay_max,
            max_retries=max_retries,
            tier=tier.value  # 传入分层类型，用于生成不同的文件名
        )
        
        output_path = crawler.crawl()
        with log_lock:
            logger.info(f"✓ 爬取完成: {output_path}")
        result_info["steps"]["crawl"] = {"success": True, "output": output_path}
        
    except Exception as e:
        with log_lock:
            logger.error(f"爬取失败: {e}")
        result_info["steps"]["crawl"] = {"success": False, "error": str(e)}
        return False, result_info, None
    finally:
        # 恢复原始路径
        crawl_module.VIEWS_FILE = original_views_file

    result_info["status"] = "success"
    result_info["end_time"] = datetime.now().isoformat()
    
    with log_lock:
        logger.info("\n" + "=" * 60)
        logger.info(f"{tier.value.upper()}数据爬取流程执行成功!")
        logger.info("=" * 60)
    
    return True, result_info, output_path


def merge_crawl_results(
    output_files: Dict[WorkTier, Optional[str]],
    date_str: str,
    hour_str: str
) -> Optional[str]:
    """
    合并多个分层的爬取结果文件为一个文件
    
    Args:
        output_files: 各分层的输出文件路径字典
        date_str: 日期字符串
        hour_str: 小时字符串
        
    Returns:
        Optional[str]: 合并后的文件路径，如果无法合并则返回 None
    """
    import json
    
    merged_data = {
        "session_id": f"merged_{date_str.replace('-', '')}{hour_str}00",
        "crawl_time": datetime.now().isoformat(),
        "crawl_hour": hour_str,
        "total_count": 0,
        "success_count": 0,
        "fail_count": 0,
        "skip_count": 0,
        "duration_seconds": 0,
        "data": [],
        "source_tiers": []
    }
    
    valid_files = []
    for tier, output_path in output_files.items():
        if output_path and os.path.exists(output_path):
            try:
                with open(output_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                # 累加统计信息
                merged_data["total_count"] += data.get("total_count", 0)
                merged_data["success_count"] += data.get("success_count", 0)
                merged_data["fail_count"] += data.get("fail_count", 0)
                merged_data["skip_count"] += data.get("skip_count", 0)
                merged_data["duration_seconds"] += data.get("duration_seconds", 0)
                
                # 合并数据
                merged_data["data"].extend(data.get("data", []))
                merged_data["source_tiers"].append(tier.value)
                valid_files.append(output_path)
                
                logger.info(f"✓ 合并 {tier.value.upper()} 数据: {len(data.get('data', []))} 条")
                
            except Exception as e:
                logger.error(f"✗ 读取 {tier.value} 数据失败: {e}")
    
    if not valid_files:
        logger.warning("没有有效的数据文件可以合并")
        return None
    
    # 生成合并后的文件路径
    project_root = get_project_root()
    merged_dir = os.path.join(project_root, "data", "spider", "views", date_str[:4], date_str[5:7], date_str[8:10])
    os.makedirs(merged_dir, exist_ok=True)
    
    merged_filename = f"{date_str}-{hour_str}_views_data_merged.json"
    merged_path = os.path.join(merged_dir, merged_filename)
    
    # 写入合并后的文件
    with open(merged_path, 'w', encoding='utf-8') as f:
        json.dump(merged_data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"✓ 合并完成: 总计 {merged_data['total_count']} 条记录 -> {merged_path}")
    
    return merged_path


def import_crawl_result(
    output_path: str,
    date_str: str,
    hour_str: str,
    force: bool = False
) -> bool:
    """
    导入单个爬取结果文件到数据库
    
    Args:
        output_path: 爬取结果文件路径
        date_str: 日期字符串
        hour_str: 小时字符串
        force: 是否强制重新导入
        
    Returns:
        bool: 是否成功
    """
    if not output_path or not os.path.exists(output_path):
        logger.warning(f"文件不存在，跳过导入: {output_path}")
        return False
    
    importer = ViewsImporter()
    
    try:
        importer.connect()
        
        # 加载数据文件
        import json
        with open(output_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # 导入数据
        success = importer.import_data(data, force=force)
        importer.close()
        
        if success:
            logger.info(f"✓ 导入成功: {output_path}")
        else:
            logger.error(f"导入失败: {output_path}")
        
        return success
        
    except Exception as e:
        logger.error(f"导入失败: {e}")
        return False


def run_parallel_crawl(
    tiers: List[WorkTier],
    force: bool = False,
    request_delay_min: float = 1.0,
    request_delay_max: float = 3.0,
    max_retries: int = 2
) -> Tuple[bool, Dict[str, Any], Dict[WorkTier, Optional[str]]]:
    """
    并行执行多个分层的爬取流程
    
    Args:
        tiers: 要爬取的分层列表
        force: 是否强制重新导入
        request_delay_min: 最小请求延迟
        request_delay_max: 最大请求延迟
        max_retries: 最大重试次数
        
    Returns:
        Tuple[bool, dict, dict]: (整体是否成功, 执行信息, 各分层输出文件路径)
    """
    results = {
        "start_time": timezone.localtime().strftime('%Y-%m-%d %H:%M:%S'),
        "tiers": {},
    }
    output_files: Dict[WorkTier, Optional[str]] = {}
    
    logger.info("=" * 60)
    logger.info(f"开始并行爬取: {[t.value for t in tiers]}")
    logger.info("=" * 60)
    
    # 使用线程池并行执行爬取
    with ThreadPoolExecutor(max_workers=len(tiers)) as executor:
        # 提交所有任务
        future_to_tier = {}
        for tier in tiers:
            future = executor.submit(
                export_and_crawl_tier,
                tier,
                force,
                request_delay_min,
                request_delay_max,
                max_retries
            )
            future_to_tier[future] = tier
        
        # 收集结果
        for future in as_completed(future_to_tier):
            tier = future_to_tier[future]
            try:
                success, info, output_path = future.result()
                results["tiers"][tier.value] = info
                output_files[tier] = output_path
                
                if success:
                    logger.info(f"✓ {tier.value.upper()}数据爬取完成")
                else:
                    logger.error(f"✗ {tier.value.upper()}数据爬取失败")
                    
            except Exception as e:
                logger.error(f"✗ {tier.value.upper()}数据爬取异常: {e}")
                results["tiers"][tier.value] = {"error": str(e)}
                output_files[tier] = None
    
    # 合并并统一导入所有结果
    logger.info("\n" + "=" * 60)
    logger.info("开始合并并导入数据...")
    logger.info("=" * 60)
    
    crawl_time = datetime.now()
    date_str = crawl_time.strftime('%Y-%m-%d')
    hour_str = crawl_time.strftime('%H')
    
    # 合并所有分层的数据文件
    merged_path = merge_crawl_results(output_files, date_str, hour_str)
    
    # 统一导入合并后的文件
    all_import_success = True
    if merged_path:
        logger.info(f"\n导入合并后的数据...")
        success = import_crawl_result(merged_path, date_str, hour_str, force)
        # 为每个分层记录导入状态
        for tier in output_files.keys():
            if tier.value in results["tiers"]:
                results["tiers"][tier.value]["import_success"] = success
        if not success:
            all_import_success = False
    else:
        logger.warning("没有数据需要导入")
        all_import_success = False
    
    results["end_time"] = timezone.localtime().strftime('%Y-%m-%d %H:%M:%S')
    
    # 判断整体是否成功（至少有一个爬取成功，且导入成功）
    any_crawl_success = any(
        info.get("status") == "success" 
        for info in results["tiers"].values()
    )
    overall_success = any_crawl_success and all_import_success
    
    logger.info("\n" + "=" * 60)
    logger.info("并行爬取和导入执行完成")
    logger.info("=" * 60)
    
    return overall_success, results, output_files


def run_crawl_pipeline(
    tier: WorkTier, 
    views_file: str,
    force: bool = False,
    request_delay_min: float = 1.0,
    request_delay_max: float = 3.0,
    max_retries: int = 2
) -> Tuple[bool, Dict[str, Any]]:
    """
    执行指定分层的完整爬取流程（串行版本，用于单独执行）
    
    Args:
        tier: 分层类型 (HOT/COLD)
        views_file: views.json 文件路径（已废弃，保留参数兼容性）
        force: 是否强制重新导入
        request_delay_min: 最小请求延迟
        request_delay_max: 最大请求延迟
        max_retries: 最大重试次数
        
    Returns:
        Tuple[bool, dict]: (是否成功, 执行信息)
    """
    # 使用新的并行函数，但只执行一个 tier
    success, results, output_files = run_parallel_crawl(
        tiers=[tier],
        force=force,
        request_delay_min=request_delay_min,
        request_delay_max=request_delay_max,
        max_retries=max_retries
    )
    
    return success, results.get("tiers", {}).get(tier.value, {})


def run_scheduled_crawl(force: bool = False) -> Tuple[bool, Dict[str, Any]]:
    """
    根据当前时间执行调度爬取
    - 每小时都爬取热数据
    - 只在指定时段爬取冷数据
    - 热数据和冷数据并发执行，完成后统一导入
    
    Args:
        force: 是否强制重新导入
        
    Returns:
        Tuple[bool, dict]: (是否成功, 执行信息)
    """
    current_hour = get_current_hour()
    current_time = timezone.localtime().strftime('%Y-%m-%d %H:%M:%S')
    
    logger.info("=" * 60)
    logger.info(f"执行调度爬取 - 当前时间: {current_time}")
    logger.info(f"当前时段: {current_hour}:00")
    logger.info("=" * 60)
    
    # 确定要爬取的分层
    tiers_to_crawl = [WorkTier.HOT]  # 热数据始终爬取
    
    if current_hour in COLD_CRAWL_HOURS:
        tiers_to_crawl.append(WorkTier.COLD)
        logger.info(f"\n本时段将爬取: 热数据 + 冷数据（并发执行）")
    else:
        next_cold_hours = [h for h in COLD_CRAWL_HOURS if h > current_hour]
        next_cold = next_cold_hours[0] if next_cold_hours else COLD_CRAWL_HOURS[0]
        logger.info(f"\n本时段将爬取: 仅热数据")
        logger.info(f"下次冷数据爬取时间: {next_cold}:00")
    
    # 执行并行爬取和统一导入
    success, results, output_files = run_parallel_crawl(tiers=tiers_to_crawl, force=force)
    
    return success, results


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
  
  # 爬取全部数据（热+冷，并发执行）
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
            print(f"   冷数据: ✅ 本时段执行爬取（与热数据并发）")
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
            # 并行爬取热数据和冷数据
            success, results, output_files = run_parallel_crawl(
                tiers=[WorkTier.HOT, WorkTier.COLD],
                force=args.force,
                request_delay_min=args.delay_min,
                request_delay_max=args.delay_max,
                max_retries=args.retries
            )
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
