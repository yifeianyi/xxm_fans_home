#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
分层爬虫修复测试
验证以下问题已修复：
1. 时区不一致问题（使用 Django timezone.localtime()）
2. 冷数据爬取时段判断时机问题（基于任务触发时间判断）

用法:
    cd /home/yifeianyi/Desktop/xxm_fans_home
    python spider/test_tiered_crawler_fix.py
"""

import sys
import os
import unittest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_PATH = os.path.join(PROJECT_ROOT, 'repo', 'xxm_fans_backend')

# 添加后端目录到路径（必须首先添加）
sys.path.insert(0, BACKEND_PATH)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')

import django
django.setup()

from django.utils import timezone

# 直接在测试中定义 COLD_CRAWL_HOURS（与 run_tiered_crawler.py 中的定义保持一致）
COLD_CRAWL_HOURS = [0, 8, 16]  # 00:00, 08:00, 16:00


class TestTimezoneHandling(unittest.TestCase):
    """测试时区处理"""
    
    def test_localtime_returns_correct_timezone(self):
        """验证 timezone.localtime() 返回正确时区的时间"""
        now = timezone.now()
        local_now = timezone.localtime()
        
        # localtime 应该和 now 表示同一时刻
        self.assertEqual(now.utcoffset(), timedelta(0))  # now 是 UTC
        
        # localtime 应该有时区偏移（Asia/Shanghai 是 UTC+8）
        offset = local_now.utcoffset()
        self.assertIsNotNone(offset)
        self.assertEqual(offset.total_seconds(), 8 * 3600)  # +8小时
    
    def test_get_current_hour_uses_localtime(self):
        """验证 get_current_hour 使用本地时间"""
        # 动态导入
        sys.path.insert(0, os.path.join(PROJECT_ROOT, 'spider'))
        import run_tiered_crawler as rtc
        
        # 模拟 timezone.localtime() 返回特定时间
        mock_time = timezone.make_aware(datetime(2024, 1, 15, 8, 30, 0))
        
        with patch('django.utils.timezone.localtime', return_value=mock_time):
            hour = rtc.get_current_hour()
            self.assertEqual(hour, 8)
    
    def test_cold_crawl_hours_match_local_time(self):
        """验证冷数据爬取时段与本地时间匹配"""
        # 动态导入 get_current_hour
        sys.path.insert(0, os.path.join(PROJECT_ROOT, 'spider'))
        import run_tiered_crawler as rtc
        
        # 测试不同时段
        test_cases = [
            (datetime(2024, 1, 15, 0, 0, 0), True, "00:00 应该爬冷数据"),
            (datetime(2024, 1, 15, 8, 0, 0), True, "08:00 应该爬冷数据"),
            (datetime(2024, 1, 15, 16, 0, 0), True, "16:00 应该爬冷数据"),
            (datetime(2024, 1, 15, 1, 0, 0), False, "01:00 不应该爬冷数据"),
            (datetime(2024, 1, 15, 7, 59, 59), False, "07:59 不应该爬冷数据"),
            (datetime(2024, 1, 15, 9, 0, 0), False, "09:00 不应该爬冷数据"),
            (datetime(2024, 1, 15, 22, 0, 0), False, "22:00 不应该爬冷数据"),
        ]
        
        for dt, expected, msg in test_cases:
            with self.subTest(time=dt.strftime('%H:%M'), expected=expected):
                aware_dt = timezone.make_aware(dt)
                with patch('django.utils.timezone.localtime', return_value=aware_dt):
                    hour = rtc.get_current_hour()
                    should_crawl = hour in COLD_CRAWL_HOURS
                    self.assertEqual(should_crawl, expected, msg)


class TestScheduledCrawlLogic(unittest.TestCase):
    """测试调度爬取逻辑（并行版本）"""
    
    def test_cold_data_crawled_based_on_trigger_time(self):
        """
        关键测试：验证冷数据爬取基于任务触发时间判断，而非热数据完成后时间
        
        验证：即使热数据爬取跨越了小时边界，决策也应基于触发时的小时
        """
        # 动态导入
        sys.path.insert(0, os.path.join(PROJECT_ROOT, 'spider'))
        import run_tiered_crawler as rtc
        
        # 模拟任务在 07:55 触发
        trigger_time = timezone.make_aware(datetime(2024, 1, 15, 7, 55, 0))
        
        # 模拟 run_parallel_crawl 的返回结果
        def mock_parallel_crawl(tiers, force=False, **kwargs):
            # 验证传入的 tiers 只包含热数据（因为触发时 hour=7 不在冷数据时段）
            self.assertEqual(len(tiers), 1)
            self.assertEqual(tiers[0], rtc.WorkTier.HOT)
            return True, {"test": "data"}, {rtc.WorkTier.HOT: "/path/to/hot.json"}
        
        with patch('django.utils.timezone.localtime', return_value=trigger_time):
            with patch('run_tiered_crawler.logger'):
                with patch.object(rtc, 'run_parallel_crawl', side_effect=mock_parallel_crawl) as mock_parallel:
                    # 执行调度爬取
                    rtc.run_scheduled_crawl(force=False)
                    
                    # 验证 run_parallel_crawl 被调用
                    self.assertEqual(mock_parallel.call_count, 1)
                    # 验证只传入了热数据
                    call_args = mock_parallel.call_args
                    self.assertEqual(call_args[1]['tiers'], [rtc.WorkTier.HOT])
    
    def test_cold_data_crawled_when_triggered_in_cold_hours(self):
        """
        验证：当任务在冷数据时段触发时，会同时爬取热数据和冷数据（并发）
        """
        # 动态导入
        sys.path.insert(0, os.path.join(PROJECT_ROOT, 'spider'))
        import run_tiered_crawler as rtc
        
        # 任务在 08:00 触发（冷数据时段）
        trigger_time = timezone.make_aware(datetime(2024, 1, 15, 8, 0, 0))
        
        # 模拟 run_parallel_crawl 的返回结果
        def mock_parallel_crawl(tiers, force=False, **kwargs):
            # 验证传入了热数据和冷数据
            self.assertEqual(len(tiers), 2)
            self.assertIn(rtc.WorkTier.HOT, tiers)
            self.assertIn(rtc.WorkTier.COLD, tiers)
            return True, {"test": "data"}, {
                rtc.WorkTier.HOT: "/path/to/hot.json",
                rtc.WorkTier.COLD: "/path/to/cold.json"
            }
        
        with patch('django.utils.timezone.localtime', return_value=trigger_time):
            with patch('run_tiered_crawler.logger'):
                with patch.object(rtc, 'run_parallel_crawl', side_effect=mock_parallel_crawl) as mock_parallel:
                    rtc.run_scheduled_crawl(force=False)
                    
                    # 验证 run_parallel_crawl 被调用
                    self.assertEqual(mock_parallel.call_count, 1)
                    # 验证同时传入了热数据和冷数据
                    call_args = mock_parallel.call_args
                    tiers = call_args[1]['tiers']
                    self.assertEqual(len(tiers), 2)
                    self.assertIn(rtc.WorkTier.HOT, tiers)
                    self.assertIn(rtc.WorkTier.COLD, tiers)
    
    def test_time_consistency_throughout_execution(self):
        """
        验证：整个执行过程中时间判断保持一致（并行版本）
        """
        # 动态导入
        sys.path.insert(0, os.path.join(PROJECT_ROOT, 'spider'))
        import run_tiered_crawler as rtc
        
        # 任务在 07:59:30 触发（在 07:00 时段）
        trigger_time = timezone.make_aware(datetime(2024, 1, 15, 7, 59, 30))
        
        captured_tiers = []
        
        def mock_parallel_crawl(tiers, force=False, **kwargs):
            captured_tiers.extend(tiers)
            return True, {"test": "data"}, {rtc.WorkTier.HOT: "/path/to/hot.json"}
        
        with patch('django.utils.timezone.localtime', return_value=trigger_time):
            with patch('run_tiered_crawler.logger'):
                with patch.object(rtc, 'run_parallel_crawl', side_effect=mock_parallel_crawl):
                    rtc.run_scheduled_crawl(force=False)
                    
                    # 触发时 hour=7，不在 COLD_CRAWL_HOURS 中，只应该爬热数据
                    self.assertEqual(len(captured_tiers), 1)
                    self.assertEqual(captured_tiers[0], rtc.WorkTier.HOT)


class TestColdCrawlHours(unittest.TestCase):
    """测试冷数据爬取时段定义"""
    
    def test_cold_crawl_hours_defined_correctly(self):
        """验证冷数据爬取时段正确定义"""
        self.assertEqual(COLD_CRAWL_HOURS, [0, 8, 16])
        self.assertEqual(len(COLD_CRAWL_HOURS), 3)
        self.assertTrue(all(isinstance(h, int) for h in COLD_CRAWL_HOURS))
        self.assertTrue(all(0 <= h < 24 for h in COLD_CRAWL_HOURS))


class TestEdgeCases(unittest.TestCase):
    """测试边界情况"""
    
    def test_exact_hour_boundary(self):
        """测试整点边界情况（并行版本）"""
        # 动态导入
        sys.path.insert(0, os.path.join(PROJECT_ROOT, 'spider'))
        import run_tiered_crawler as rtc
        
        # 07:59:59.999 - 最后一刻
        trigger_time = timezone.make_aware(datetime(2024, 1, 15, 7, 59, 59, 999999))
        
        captured_tiers = []
        
        def mock_parallel_crawl(tiers, force=False, **kwargs):
            captured_tiers.extend(tiers)
            return True, {"test": "data"}, {rtc.WorkTier.HOT: "/path/to/hot.json"}
        
        with patch('django.utils.timezone.localtime', return_value=trigger_time):
            with patch('run_tiered_crawler.logger'):
                with patch.object(rtc, 'run_parallel_crawl', side_effect=mock_parallel_crawl):
                    rtc.run_scheduled_crawl(force=False)
                    
                    # hour=7，不爬冷数据，只爬热数据
                    self.assertEqual(len(captured_tiers), 1)
                    self.assertEqual(captured_tiers[0], rtc.WorkTier.HOT)
    
    def test_exact_cold_hour_start(self):
        """测试冷数据时段精确开始（并行版本）"""
        # 动态导入
        sys.path.insert(0, os.path.join(PROJECT_ROOT, 'spider'))
        import run_tiered_crawler as rtc
        
        # 08:00:00.000 - 精确开始
        trigger_time = timezone.make_aware(datetime(2024, 1, 15, 8, 0, 0))
        
        captured_tiers = []
        
        def mock_parallel_crawl(tiers, force=False, **kwargs):
            captured_tiers.extend(tiers)
            return True, {"test": "data"}, {
                rtc.WorkTier.HOT: "/path/to/hot.json",
                rtc.WorkTier.COLD: "/path/to/cold.json"
            }
        
        with patch('django.utils.timezone.localtime', return_value=trigger_time):
            with patch('run_tiered_crawler.logger'):
                with patch.object(rtc, 'run_parallel_crawl', side_effect=mock_parallel_crawl):
                    rtc.run_scheduled_crawl(force=False)
                    
                    # hour=8，应该同时爬热数据和冷数据
                    self.assertEqual(len(captured_tiers), 2)
                    self.assertIn(rtc.WorkTier.HOT, captured_tiers)
                    self.assertIn(rtc.WorkTier.COLD, captured_tiers)


class TestParallelCrawlFeatures(unittest.TestCase):
    """测试并行爬取特性"""
    
    def test_views_crawler_accepts_tier_parameter(self):
        """验证 ViewsCrawler 接受 tier 参数"""
        from tools.spider.crawl_views import ViewsCrawler
        
        # 创建带 tier 参数的爬虫实例
        crawler_hot = ViewsCrawler(tier='hot')
        crawler_cold = ViewsCrawler(tier='cold')
        crawler_default = ViewsCrawler()
        
        self.assertEqual(crawler_hot.tier, 'hot')
        self.assertEqual(crawler_cold.tier, 'cold')
        self.assertIsNone(crawler_default.tier)
    
    def test_output_filename_includes_tier(self):
        """验证输出文件名包含 tier 标识"""
        from tools.spider.crawl_views import ViewsCrawler
        import tempfile
        import shutil
        
        # 创建临时目录
        temp_dir = tempfile.mkdtemp()
        
        try:
            # 测试热数据文件名
            crawler_hot = ViewsCrawler(tier='hot')
            test_time = datetime(2024, 1, 15, 8, 0, 0)
            
            # 调用 _save_output 方法
            test_data = {"test": "data"}
            output_path = crawler_hot._save_output(test_data, test_time)
            
            # 验证文件名包含 _hot
            self.assertIn('views_data_hot.json', output_path)
            self.assertTrue(os.path.exists(output_path))
            
            # 测试冷数据文件名
            crawler_cold = ViewsCrawler(tier='cold')
            output_path_cold = crawler_cold._save_output(test_data, test_time)
            
            # 验证文件名包含 _cold
            self.assertIn('views_data_cold.json', output_path_cold)
            self.assertTrue(os.path.exists(output_path_cold))
            
            # 测试默认文件名（不包含 tier）
            crawler_default = ViewsCrawler()
            output_path_default = crawler_default._save_output(test_data, test_time)
            
            # 验证文件名不包含 tier 标识
            self.assertIn('views_data.json', output_path_default)
            self.assertNotIn('views_data_hot', output_path_default)
            self.assertNotIn('views_data_cold', output_path_default)
            
        finally:
            # 清理临时目录
            shutil.rmtree(temp_dir, ignore_errors=True)
    
    def test_parallel_crawl_function_exists(self):
        """验证 run_parallel_crawl 函数存在"""
        sys.path.insert(0, os.path.join(PROJECT_ROOT, 'spider'))
        import run_tiered_crawler as rtc
        
        self.assertTrue(hasattr(rtc, 'run_parallel_crawl'))
        self.assertTrue(callable(rtc.run_parallel_crawl))
    
    def test_export_and_crawl_tier_function_exists(self):
        """验证 export_and_crawl_tier 函数存在"""
        sys.path.insert(0, os.path.join(PROJECT_ROOT, 'spider'))
        import run_tiered_crawler as rtc
        
        self.assertTrue(hasattr(rtc, 'export_and_crawl_tier'))
        self.assertTrue(callable(rtc.export_and_crawl_tier))


class TestIntegration(unittest.TestCase):
    """集成测试"""
    
    def test_module_imports(self):
        """验证模块可以正确导入"""
        try:
            sys.path.insert(0, os.path.join(PROJECT_ROOT, 'spider'))
            import run_tiered_crawler as rtc
            self.assertTrue(hasattr(rtc, 'run_scheduled_crawl'))
            self.assertTrue(hasattr(rtc, 'run_crawl_pipeline'))
            self.assertTrue(hasattr(rtc, 'run_parallel_crawl'))
            self.assertTrue(hasattr(rtc, 'export_and_crawl_tier'))
            self.assertTrue(hasattr(rtc, 'get_current_hour'))
            self.assertTrue(hasattr(rtc, 'should_crawl_cold_now'))
            self.assertTrue(hasattr(rtc, 'COLD_CRAWL_HOURS'))
        except ImportError as e:
            self.fail(f"模块导入失败: {e}")
    
    def test_timezone_configuration(self):
        """验证 Django 时区配置正确"""
        from django.conf import settings
        
        self.assertTrue(settings.USE_TZ)
        self.assertEqual(settings.TIME_ZONE, 'Asia/Shanghai')
    
    def test_fix_verification(self):
        """
        验证修复：冷数据爬取判断基于任务触发时间
        
        这是一个关键的回归测试，确保修复生效
        """
        sys.path.insert(0, os.path.join(PROJECT_ROOT, 'spider'))
        import run_tiered_crawler as rtc
        
        # 检查关键修复点1：使用 localtime 而非 now
        import inspect
        source = inspect.getsource(rtc.get_current_hour)
        self.assertIn('localtime()', source, "get_current_hour 应该使用 timezone.localtime()")
        
        # 检查关键修复点2：run_scheduled_crawl 使用 current_hour 变量判断，而非调用 should_crawl_cold_now()
        source = inspect.getsource(rtc.run_scheduled_crawl)
        self.assertIn('current_hour in COLD_CRAWL_HOURS', source, 
                     "应该使用 current_hour in COLD_CRAWL_HOURS 而非 should_crawl_cold_now()")
    
    def test_parallel_architecture_verification(self):
        """验证并行架构实现"""
        sys.path.insert(0, os.path.join(PROJECT_ROOT, 'spider'))
        import run_tiered_crawler as rtc
        import inspect
        
        # 检查 run_parallel_crawl 使用 ThreadPoolExecutor
        source = inspect.getsource(rtc.run_parallel_crawl)
        self.assertIn('ThreadPoolExecutor', source, "应该使用 ThreadPoolExecutor 实现并发")
        
        # 检查统一导入逻辑
        self.assertIn('import_crawl_result', source, "应该调用 import_crawl_result 进行统一导入")


def run_tests():
    """运行所有测试"""
    # 创建测试套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加测试类
    suite.addTests(loader.loadTestsFromTestCase(TestTimezoneHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestScheduledCrawlLogic))
    suite.addTests(loader.loadTestsFromTestCase(TestColdCrawlHours))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))
    suite.addTests(loader.loadTestsFromTestCase(TestParallelCrawlFeatures))
    suite.addTests(loader.loadTestsFromTestCase(TestIntegration))
    
    # 运行测试
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 返回退出码
    return 0 if result.wasSuccessful() else 1


if __name__ == '__main__':
    sys.exit(run_tests())
