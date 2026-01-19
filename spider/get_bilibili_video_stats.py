#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站视频数据爬取脚本
定时爬取视频的播放量、弹幕、评论、点赞、投币、收藏数量
支持失败重试和异常处理
"""

import json
import time
import requests
import os
import sys
from datetime import datetime
from typing import Dict, List, Optional


class BilibiliVideoStatsCrawler:
    """B站视频数据爬虫类"""

    def __init__(self, json_file_path: str):
        """
        初始化爬虫

        Args:
            json_file_path: JSON数据文件路径
        """
        self.json_file_path = json_file_path
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
            'Referer': 'https://www.bilibili.com'
        }

    def load_json_data(self) -> Optional[List[Dict]]:
        """
        加载JSON数据文件

        Returns:
            数据列表，如果失败返回None
        """
        try:
            with open(self.json_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                if isinstance(data, list):
                    return data
                elif isinstance(data, dict) and 'data' in data:
                    return data['data']
                else:
                    print(f"错误: JSON文件格式不正确，期望列表或包含data字段的对象")
                    return None
        except FileNotFoundError:
            print(f"错误: 文件不存在 - {self.json_file_path}")
            return None
        except json.JSONDecodeError as e:
            print(f"错误: JSON解析失败 - {e}")
            return None
        except Exception as e:
            print(f"错误: 加载文件失败 - {e}")
            return None

    def save_json_data(self, data: List[Dict]) -> bool:
        """
        保存JSON数据文件

        Args:
            data: 要保存的数据列表

        Returns:
            是否保存成功
        """
        try:
            with open(self.json_file_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            return True
        except Exception as e:
            print(f"错误: 保存文件失败 - {e}")
            return False

    def get_video_stats(self, bvid: str) -> Optional[Dict]:
        """
        获取视频统计数据

        Args:
            bvid: B站视频BV号

        Returns:
            视频统计数据字典，失败返回None
        """
        url = f"https://api.bilibili.com/x/web-interface/view?bvid={bvid}"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            data = response.json()

            if data.get('code') == 0:
                stat = data['data']['stat']
                return {
                    'bvid': bvid,
                    'view': stat.get('view', 0),           # 播放量
                    'danmaku': stat.get('danmaku', 0),     # 弹幕数
                    'reply': stat.get('reply', 0),         # 评论数
                    'like': stat.get('like', 0),           # 点赞数
                    'coin': stat.get('coin', 0),           # 投币数
                    'favorite': stat.get('favorite', 0),   # 收藏数
                    'share': stat.get('share', 0),         # 分享数
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                print(f"警告: BV号 {bvid} 获取失败 - {data.get('message', 'Unknown error')}")
                return None

        except requests.RequestException as e:
            print(f"警告: BV号 {bvid} 请求失败 - {e}")
            return None
        except Exception as e:
            print(f"警告: BV号 {bvid} 处理失败 - {e}")
            return None

    def add_log(self, item: Dict, status: str, message: str = "") -> None:
        """
        为数据项添加日志

        Args:
            item: 数据项字典
            status: 状态（success/failed）
            message: 日志消息
        """
        if 'log' not in item:
            item['log'] = []

        log_entry = {
            'status': status,
            'message': message,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        item['log'].append(log_entry)

        # 只保留最近50条日志
        if len(item['log']) > 50:
            item['log'] = item['log'][-50:]

    def check_and_update_valid_status(self, item: Dict) -> None:
        """
        检查并更新is_valid状态

        规则：
        1. 连续3次失败 -> is_valid = False
        2. 连续2个小时爬取失败 -> is_valid = False

        Args:
            item: 数据项字典
        """
        if 'log' not in item or not item['log']:
            return

        # 获取最近的日志
        recent_logs = item['log'][-10:]  # 检查最近10条日志

        # 检查连续失败次数
        consecutive_failures = 0
        for log in reversed(recent_logs):
            if log['status'] == 'failed':
                consecutive_failures += 1
            else:
                break

        # 规则1: 连续3次失败
        if consecutive_failures >= 3:
            item['is_valid'] = False
            self.add_log(item, 'failed', f'连续{consecutive_failures}次失败，标记为无效')
            print(f"警告: BV号 {item.get('bvid', 'unknown')} 连续{consecutive_failures}次失败，标记为无效")
            return

        # 规则2: 连续2个小时爬取失败
        if consecutive_failures >= 2:
            # 检查时间间隔
            latest_failed = recent_logs[-1]['timestamp']
            second_latest_failed = recent_logs[-2]['timestamp']

            try:
                latest_time = datetime.strptime(latest_failed, '%Y-%m-%d %H:%M:%S')
                second_latest_time = datetime.strptime(second_latest_failed, '%Y-%m-%d %H:%M:%S')
                time_diff = latest_time - second_latest_time

                # 如果时间差小于等于2小时（7200秒）
                if time_diff.total_seconds() <= 7200:
                    item['is_valid'] = False
                    self.add_log(item, 'failed', f'连续2小时内爬取失败，标记为无效')
                    print(f"警告: BV号 {item.get('bvid', 'unknown')} 连续2小时内爬取失败，标记为无效")
                    return
            except Exception as e:
                print(f"警告: 解析时间失败 - {e}")

    def crawl_single_video(self, item: Dict) -> bool:
        """
        爬取单个视频数据

        Args:
            item: 数据项字典

        Returns:
            是否爬取成功
        """
        bvid = item.get('bvid')
        if not bvid:
            print(f"警告: 数据项缺少bvid字段")
            self.add_log(item, 'failed', '缺少bvid字段')
            return False

        # 检查is_valid状态
        if not item.get('is_valid', True):
            print(f"跳过: BV号 {bvid} 已标记为无效")
            return False

        print(f"正在爬取: BV号 {bvid}")

        # 获取视频数据
        stats = self.get_video_stats(bvid)

        if stats:
            # 更新视频数据
            item.update(stats)
            self.add_log(item, 'success', f'成功获取数据: 播放{stats["view"]}, 弹幕{stats["danmaku"]}, 评论{stats["reply"]}, 点赞{stats["like"]}, 投币{stats["coin"]}, 收藏{stats["favorite"]}')
            print(f"✓ BV号 {bvid}: 播放{stats['view']}, 弹幕{stats['danmaku']}, 评论{stats['reply']}, 点赞{stats['like']}, 投币{stats['coin']}, 收藏{stats['favorite']}")
            return True
        else:
            # 记录失败
            self.add_log(item, 'failed', '获取视频数据失败')
            print(f"✗ BV号 {bvid}: 获取失败")

            # 检查并更新is_valid状态
            self.check_and_update_valid_status(item)
            return False

    def crawl_all_videos(self, data: List[Dict]) -> Dict[str, int]:
        """
        爬取所有视频数据

        Args:
            data: 数据列表

        Returns:
            统计结果字典
        """
        success_count = 0
        failed_count = 0
        skipped_count = 0

        print(f"\n开始爬取 {len(data)} 个视频数据...")
        print("=" * 80)

        for i, item in enumerate(data, 1):
            print(f"\n[{i}/{len(data)}]", end=" ")

            # 检查is_valid状态
            if not item.get('is_valid', True):
                skipped_count += 1
                continue

            # 爬取数据
            if self.crawl_single_video(item):
                success_count += 1
            else:
                failed_count += 1

            # 避免请求过快
            time.sleep(0.5)

        print("\n" + "=" * 80)
        print(f"爬取完成: 成功 {success_count}, 失败 {failed_count}, 跳过 {skipped_count}")

        return {
            'success': success_count,
            'failed': failed_count,
            'skipped': skipped_count,
            'total': len(data)
        }

    def run_once(self) -> bool:
        """
        执行一次爬取任务

        Returns:
            是否执行成功
        """
        # 加载数据
        data = self.load_json_data()
        if data is None:
            return False

        if not data:
            print("警告: 数据文件为空")
            return False

        # 爬取数据
        self.crawl_all_videos(data)

        # 保存数据
        if self.save_json_data(data):
            print(f"\n数据已保存到: {self.json_file_path}")
            return True
        else:
            print(f"\n错误: 保存数据失败")
            return False

    def run_scheduled(self, interval_hours: int = 1) -> None:
        """
        定时执行爬取任务

        Args:
            interval_hours: 执行间隔（小时）
        """
        print(f"启动定时爬取任务，间隔: {interval_hours} 小时")
        print(f"数据文件: {self.json_file_path}")
        print("按 Ctrl+C 停止任务\n")

        try:
            while True:
                print(f"\n{'=' * 80}")
                print(f"任务开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"{'=' * 80}")

                self.run_once()

                # 计算下次执行时间
                next_run = datetime.now()
                next_run = next_run.replace(minute=0, second=0, microsecond=0)
                next_run = next_run.replace(hour=next_run.hour + interval_hours)

                print(f"\n下次执行时间: {next_run.strftime('%Y-%m-%d %H:%M:%S')}")
                print(f"等待 {interval_hours} 小时...")

                # 等待指定时间
                time.sleep(interval_hours * 3600)

        except KeyboardInterrupt:
            print("\n\n任务已停止")


def main():
    """主函数"""
    # 配置参数
    json_file_path = "bilibili_videos.json"  # JSON数据文件路径
    interval_hours = 1  # 爬取间隔（小时）

    # 检查命令行参数
    if len(sys.argv) > 1:
        json_file_path = sys.argv[1]
    if len(sys.argv) > 2:
        try:
            interval_hours = int(sys.argv[2])
        except ValueError:
            print("错误: 间隔时间必须是整数")
            sys.exit(1)

    # 检查文件是否存在
    if not os.path.exists(json_file_path):
        print(f"错误: 文件不存在 - {json_file_path}")
        print(f"\n请创建JSON文件，格式示例：")
        print(json.dumps([
            {
                "bvid": "BV1xx411c7mD",
                "is_valid": True,
                "log": []
            }
        ], indent=2, ensure_ascii=False))
        sys.exit(1)

    # 创建爬虫实例
    crawler = BilibiliVideoStatsCrawler(json_file_path)

    # 执行任务
    print("B站视频数据爬取脚本")
    print("=" * 80)

    # 选择运行模式
    print("\n请选择运行模式:")
    print("1. 执行一次")
    print("2. 定时执行（每小时一次）")

    try:
        choice = input("请输入选项 (1/2): ").strip()
        if choice == '1':
            crawler.run_once()
        elif choice == '2':
            crawler.run_scheduled(interval_hours)
        else:
            print("错误: 无效选项")
            sys.exit(1)
    except KeyboardInterrupt:
        print("\n\n任务已停止")
    except Exception as e:
        print(f"\n错误: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()