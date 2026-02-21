#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站动态监测测试 Demo
使用Selenium模拟真实浏览器获取B站用户动态
"""

import json
import time
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class BilibiliDynamicMonitor:
    """B站动态监控类"""

    def __init__(self, headless=True):
        """
        初始化监控器

        Args:
            headless (bool): 是否使用无头模式
        """
        self.headless = headless
        self.driver = None

    def init_driver(self):
        """初始化浏览器驱动"""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument('--headless=new')

        # 添加反检测选项
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # 无头模式必需参数
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')

        # 模拟真实浏览器
        chrome_options.add_argument(
            '--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )

        # 禁用不必要的功能
        chrome_options.add_argument('--disable-extensions')
        chrome_options.add_argument('--disable-background-networking')
        chrome_options.add_argument('--disable-sync')
        chrome_options.add_argument('--log-level=3')

        try:
            print("  正在启动浏览器...")
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
            print("  ✓ 浏览器启动成功")

            # 隐藏webdriver特征
            self.driver.execute_cdp_cmd('Page.addScriptToEvaluateOnNewDocument', {
                'source': '''
                    Object.defineProperty(navigator, 'webdriver', {
                        get: () => undefined
                    })
                '''
            })
            return True
        except Exception as e:
            print(f"✗ 初始化浏览器失败: {e}")
            return False

    def get_user_dynamics(self, uid, max_count=10):
        """
        获取用户动态

        Args:
            uid (str): B站用户UID
            max_count (int): 获取最大动态数量

        Returns:
            list: 动态列表
        """
        if not self.driver:
            return []

        try:
            # 访问用户动态页面
            url = f"https://space.bilibili.com/{uid}/dynamic"
            print(f"  访问动态页面: {url}")

            self.driver.get(url)
            time.sleep(5)  # 等待页面加载

            # 滚动页面以加载更多动态
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)

            # 尝试多种CSS选择器
            selectors = [
                '.bili-dyn-list__item',
                '.bili-dyn-item',
                '[class*="bili-dyn"]',
                '.card',
                '.dyn-item'
            ]

            dynamic_items = []
            for selector in selectors:
                try:
                    items = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    if items and len(items) > 0:
                        print(f"  使用选择器 '{selector}' 找到 {len(items)} 个元素")
                        dynamic_items = items
                        break
                except:
                    continue

            if not dynamic_items:
                print("  ✗ 未找到动态元素，尝试保存页面HTML用于调试")
                self.save_page_html(uid)
                return []

            dynamics = []

            # 获取所有动态卡片
            for i, item in enumerate(dynamic_items[:max_count]):
                try:
                    dynamic = self.parse_dynamic_item(item)
                    if dynamic and dynamic.get('content'):  # 只保留有内容的动态
                        dynamics.append(dynamic)
                except Exception as e:
                    print(f"  解析动态 {i+1} 失败: {e}")
                    continue

            print(f"  成功获取 {len(dynamics)} 条动态")
            return dynamics

        except TimeoutException:
            print("  ✗ 页面加载超时")
            return []
        except Exception as e:
            print(f"  ✗ 获取动态失败: {e}")
            import traceback
            traceback.print_exc()
            return []

    def save_page_html(self, uid):
        """保存页面HTML用于调试"""
        try:
            import os
            now = datetime.now()
            debug_dir = 'data/spider/bilibili_dynamic/debug'
            os.makedirs(debug_dir, exist_ok=True)
            
            timestamp = now.strftime('%Y%m%d_%H%M%S')
            html_file = f'{debug_dir}/page_{uid}_{timestamp}.html'
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(self.driver.page_source)
            
            print(f"  页面HTML已保存到: {html_file}")
        except Exception as e:
            print(f"  保存HTML失败: {e}")

    def parse_dynamic_item(self, item):
        """
        解析单个动态项

        Args:
            item: 动态卡片元素

        Returns:
            dict: 动态信息
        """
        dynamic = {}

        try:
            # 获取动态ID
            try:
                dynamic['id'] = item.get_attribute('data-dyn-id') or str(hash(str(item)))
            except:
                dynamic['id'] = str(hash(str(item)))

            # 获取发布时间 - 尝试多种选择器
            time_selectors = [
                '.bili-dyn-item__time',
                '.pub-time',
                '[class*="time"]',
                'span[title*="发布"]'
            ]
            for selector in time_selectors:
                try:
                    time_element = item.find_element(By.CSS_SELECTOR, selector)
                    if time_element and time_element.text.strip():
                        dynamic['publish_time'] = time_element.text.strip()
                        break
                except:
                    continue
            if 'publish_time' not in dynamic:
                dynamic['publish_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # 获取动态内容 - 尝试多种选择器
            content_selectors = [
                '.bili-dyn-content__text',
                '.text',
                '[class*="content"]',
                '.content',
                'p'
            ]
            content = ''
            for selector in content_selectors:
                try:
                    content_elements = item.find_elements(By.CSS_SELECTOR, selector)
                    for elem in content_elements:
                        text = elem.text.strip()
                        if text and len(text) > 5:  # 只取有意义的内容
                            content = text
                            break
                    if content:
                        break
                except:
                    continue
            dynamic['content'] = content

            # 获取点赞数
            like_selectors = [
                '.bili-dyn-item__like--num',
                '.like-num',
                '[class*="like"] span',
                '.like'
            ]
            for selector in like_selectors:
                try:
                    like_element = item.find_element(By.CSS_SELECTOR, selector)
                    like_text = like_element.text.strip()
                    if like_text:
                        dynamic['likes'] = like_text
                        break
                except:
                    continue
            if 'likes' not in dynamic:
                dynamic['likes'] = '0'

            # 获取评论数
            comment_selectors = [
                '.bili-dyn-item__reply--num',
                '.reply-num',
                '[class*="reply"] span',
                '.comment'
            ]
            for selector in comment_selectors:
                try:
                    comment_element = item.find_element(By.CSS_SELECTOR, selector)
                    comment_text = comment_element.text.strip()
                    if comment_text:
                        dynamic['comments'] = comment_text
                        break
                except:
                    continue
            if 'comments' not in dynamic:
                dynamic['comments'] = '0'

            # 获取转发数
            share_selectors = [
                '.bili-dyn-item__share--num',
                '.share-num',
                '[class*="share"] span'
            ]
            for selector in share_selectors:
                try:
                    share_element = item.find_element(By.CSS_SELECTOR, selector)
                    share_text = share_element.text.strip()
                    if share_text:
                        dynamic['shares'] = share_text
                        break
                except:
                    continue
            if 'shares' not in dynamic:
                dynamic['shares'] = '0'

            # 检查是否有图片
            try:
                image_selectors = [
                    '.bili-dyn-content__gallery img',
                    '.gallery img',
                    '.image img',
                    'img[src*="pic"]'
                ]
                for selector in image_selectors:
                    images = item.find_elements(By.CSS_SELECTOR, selector)
                    if images and len(images) > 0:
                        dynamic['has_images'] = True
                        dynamic['image_count'] = len(images)
                        dynamic['first_image'] = images[0].get_attribute('src')
                        break
                if 'has_images' not in dynamic:
                    dynamic['has_images'] = False
                    dynamic['image_count'] = 0
            except:
                dynamic['has_images'] = False
                dynamic['image_count'] = 0

            # 检查是否有视频
            try:
                video_selectors = [
                    '.bili-dyn-content__video',
                    '.video',
                    'iframe[src*="player"]'
                ]
                for selector in video_selectors:
                    video = item.find_element(By.CSS_SELECTOR, selector)
                    dynamic['has_video'] = True
                    break
                if 'has_video' not in dynamic:
                    dynamic['has_video'] = False
            except:
                dynamic['has_video'] = False

            return dynamic

        except Exception as e:
            print(f"  解析动态项失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def close(self):
        """关闭浏览器"""
        if self.driver:
            self.driver.quit()
            print("  ✓ 浏览器已关闭")


def save_result(user_info, dynamics, output_file):
    """
    保存结果到JSON文件

    Args:
        user_info (dict): 用户信息
        dynamics (list): 动态列表
        output_file (str): 输出文件路径
    """
    now = datetime.now()

    result = {
        'update_time': now.strftime('%Y-%m-%d %H:%M:%S'),
        'user': user_info,
        'dynamic_count': len(dynamics),
        'dynamics': dynamics
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"✓ 结果已保存到: {output_file}")


def main():
    """主函数"""
    print("=" * 60)
    print("B站动态监测测试 Demo - Selenium版本")
    print("=" * 60)
    print()
    print("说明：使用Selenium模拟真实浏览器获取B站用户动态")
    print("要求：已安装Chrome浏览器和chromedriver")
    print()

    # 定义要监控的B站用户
    accounts = [
        {'uid': '37754047', 'name': '咻咻满'},
        {'uid': '480116537', 'name': '咻小满'}
    ]

    # 初始化监控器
    monitor = BilibiliDynamicMonitor(headless=True)

    if not monitor.init_driver():
        print("\n监测完成！")
        return

    print()
    print("=" * 60)

    for account in accounts:
        print(f"\n开始监测B站用户: {account['name']} (UID: {account['uid']})")
        print("=" * 60)

        # 获取用户动态
        dynamics = monitor.get_user_dynamics(account['uid'], max_count=5)

        # 保存结果
        if dynamics:
            now = datetime.now()
            year = now.strftime('%Y')
            month = now.strftime('%m')
            output_dir = f'data/spider/bilibili_dynamic/{year}/{month}'
            import os
            os.makedirs(output_dir, exist_ok=True)

            timestamp = now.strftime('%Y%m%d_%H%M%S')
            output_file = f'{output_dir}/bilibili_dynamic_{account["name"]}_{timestamp}.json'

            save_result(account, dynamics, output_file)

            # 显示简要信息
            print(f"\n  最新动态预览:")
            for i, dyn in enumerate(dynamics[:3], 1):
                print(f"    [{i}] {dyn['publish_time']}")
                content_preview = dyn['content'][:50] + '...' if len(dyn['content']) > 50 else dyn['content']
                print(f"        {content_preview}")
                print(f"        点赞: {dyn['likes']} 评论: {dyn['comments']}")
        else:
            print("  未获取到动态，可能是页面未加载完成或账号设置问题")

        # 避免请求过快
        time.sleep(2)

    # 关闭浏览器
    monitor.close()

    print()
    print("=" * 60)
    print("监测完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()