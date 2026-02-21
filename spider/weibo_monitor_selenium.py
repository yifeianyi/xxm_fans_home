#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
微博动态监测测试 Demo - Selenium版本
使用Selenium模拟真实浏览器访问，绕过反爬限制
"""

import json
import time
import os
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException


class WeiboMonitorSelenium:
    """微博监测类 - Selenium版本"""

    def __init__(self, headless=False):
        """
        初始化微博监测器

        Args:
            headless (bool): 是否使用无头模式
        """
        self.headless = headless
        self.driver = None

    def init_driver(self):
        """初始化浏览器驱动"""
        chrome_options = Options()

        if self.headless:
            chrome_options.add_argument('--headless=new')  # 新版无头模式

        # 添加反检测选项
        chrome_options.add_argument('--disable-blink-features=AutomationControlled')
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)

        # 无头模式必需参数
        chrome_options.add_argument('--disable-gpu')
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--disable-software-rasterizer')
        chrome_options.add_argument('--disable-extensions')

        # 模拟真实浏览器
        chrome_options.add_argument('--user-agent=Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1')

        # 禁用不必要的功能以提高性能
        chrome_options.add_argument('--disable-background-networking')
        chrome_options.add_argument('--disable-default-apps')
        chrome_options.add_argument('--disable-sync')
        chrome_options.add_argument('--disable-translate')
        chrome_options.add_argument('--metrics-recording-only')
        chrome_options.add_argument('--mute-audio')
        chrome_options.add_argument('--no-first-run')
        chrome_options.add_argument('--safebrowsing-disable-auto-update')

        # 设置日志级别
        chrome_options.add_argument('--log-level=3')  # 只显示致命错误

        try:
            print("  正在启动Chromium浏览器...")
            # 使用Chromium浏览器
            self.driver = webdriver.Chrome(options=chrome_options)
            self.driver.set_page_load_timeout(30)
            self.driver.set_script_timeout(10)
            print("  ✓ Chromium浏览器启动成功")

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
            import traceback
            traceback.print_exc()
            print("\n排查建议:")
            print("1. 安装Chromium: sudo apt install chromium-browser chromium-chromedriver")
            print("2. 验证安装: chromium-browser --version && chromedriver --version")
            return False

    def get_user_posts(self, user_id, max_posts=10):
        """
        获取用户的微博列表

        Args:
            user_id (str): 用户ID
            max_posts (int): 最大获取数量

        Returns:
            list: 微博列表
        """
        url = f'https://m.weibo.cn/u/{user_id}'

        try:
            print(f"  访问URL: {url}")
            self.driver.get(url)

            # 等待页面加载
            wait = WebDriverWait(self.driver, 10)

            # 等待微博卡片出现
            try:
                wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, '.card-wrap, .card')))

                # 模拟滚动加载更多
                for _ in range(3):
                    self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                    time.sleep(1)

                # 获取微博数据
                # 尝试多种方式获取微博内容
                posts = []

                # 方式1: 通过API直接获取
                try:
                    # 查找页面中的脚本数据
                    scripts = self.driver.find_elements(By.TAG_NAME, 'script')
                    for script in scripts:
                        script_content = script.get_attribute('innerHTML')
                        if 'render_data' in script_content or '$render_data' in script_content:
                            print("  找到渲染数据")
                            # 这里可以解析JSON数据
                            break
                except:
                    pass

                # 方式2: 通过DOM解析
                try:
                    # 查找微博卡片
                    card_wraps = self.driver.find_elements(By.CSS_SELECTOR, '.card-wrap, .card')

                    print(f"  找到 {len(card_wraps)} 个微博卡片")

                    for card in card_wraps[:max_posts]:
                        try:
                            # 提取微博ID
                            mid = card.get_attribute('mid') or ''
                            if not mid:
                                try:
                                    # 从URL中提取mid
                                    detail_link = card.find_element(By.CSS_SELECTOR, 'a[href*="/detail/"]')
                                    href = detail_link.get_attribute('href')
                                    if '/detail/' in href:
                                        mid = href.split('/detail/')[-1].split('?')[0]
                                except:
                                    pass

                            # 提取文本内容
                            try:
                                text_elem = card.find_element(By.CSS_SELECTOR, '.weibo-text, .card-text, [node-type="feed_list_content"]')
                                text = text_elem.text.strip()
                            except:
                                text = ''

                            # 提取发布时间
                            try:
                                time_elem = card.find_element(By.CSS_SELECTOR, '.time, .from, [node-type="feed_list_date"]')
                                created_at = time_elem.text.strip()
                            except:
                                created_at = ''

                            # 提取互动数据
                            try:
                                action_elem = card.find_element(By.CSS_SELECTOR, '.card-act, .card-comment')
                                actions = action_elem.text
                                # 解析转发、评论、点赞数
                                reposts = comments = attitudes = 0
                                if '转发' in actions:
                                    parts = actions.split()
                                    for part in parts:
                                        if '转发' in part:
                                            reposts = self._extract_number(part)
                                        elif '评论' in part:
                                            comments = self._extract_number(part)
                                        elif '赞' in part:
                                            attitudes = self._extract_number(part)
                            except:
                                reposts = comments = attitudes = 0

                            # 提取图片
                            pics = []
                            try:
                                pic_elems = card.find_elements(By.CSS_SELECTOR, 'img.img-pic, img.media-pic')
                                for pic in pic_elems[:9]:
                                    src = pic.get_attribute('src')
                                    if src:
                                        pics.append(src)
                            except:
                                pass

                            if text or mid:  # 至少有文本或ID
                                post = {
                                    'id': mid,
                                    'text': text,
                                    'created_at': created_at,
                                    'source': '微博客户端',
                                    'reposts_count': reposts,
                                    'comments_count': comments,
                                    'attitudes_count': attitudes,
                                    'is_top': 0,
                                    'pics': pics,
                                    'url': f"https://m.weibo.cn/detail/{mid}" if mid else ''
                                }
                                posts.append(post)

                        except Exception as e:
                            print(f"  解析微博卡片失败: {e}")
                            continue

                except Exception as e:
                    print(f"  DOM解析失败: {e}")

                print(f"  成功提取 {len(posts)} 条微博")
                return posts

            except TimeoutException:
                print("  ✗ 页面加载超时")
                return []

        except Exception as e:
            print(f"  ✗ 获取微博失败: {e}")
            return []

    def _extract_number(self, text):
        """从文本中提取数字"""
        import re
        match = re.search(r'\d+', text.replace('万', '0000').replace('k', '000'))
        return int(match.group()) if match else 0

    def monitor(self, user_id, screen_name=None, max_posts=10):
        """
        监测指定用户的微博动态

        Args:
            user_id (str): 微博用户ID
            screen_name (str): 用户名
            max_posts (int): 最大获取数量

        Returns:
            dict: 监测结果
        """
        display_name = screen_name or user_id
        print(f"\n{'='*60}")
        print(f"开始监测微博用户: {display_name} (ID: {user_id})")
        print(f"{'='*60}\n")

        if not self.init_driver():
            return {
                'status': 'error',
                'message': '浏览器初始化失败',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

        try:
            print("[步骤1] 获取最新微博...")
            posts = self.get_user_posts(user_id, max_posts=max_posts)

            if not posts:
                result = {
                    'status': 'success',
                    'user_id': user_id,
                    'screen_name': display_name,
                    'posts': [],
                    'message': '未获取到微博',
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }
            else:
                print(f"\n[步骤2] 解析微博内容...")
                print(f"✓ 成功获取 {len(posts)} 条微博\n")

                for i, post in enumerate(posts[:max_posts], 1):
                    print(f"\n微博 #{i}")
                    print(f"  微博ID: {post['id']}")
                    print(f"  发布时间: {post['created_at']}")
                    print(f"  转发: {post['reposts_count']} | 评论: {post['comments_count']} | 点赞: {post['attitudes_count']}")

                    if post['text']:
                        text_preview = post['text'][:100] + '...' if len(post['text']) > 100 else post['text']
                        print(f"  内容: {text_preview}")

                    if post['pics']:
                        print(f"  图片: {len(post['pics'])} 张")

                result = {
                    'status': 'success',
                    'user_id': user_id,
                    'screen_name': display_name,
                    'posts': posts[:max_posts],
                    'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                }

            return result

        finally:
            if self.driver:
                self.driver.quit()

    def save_result(self, result, output_dir='data/spider/weibo'):
        """保存监测结果"""
        if result['status'] != 'success':
            return

        now = datetime.now()
        year = now.strftime('%Y')
        month = now.strftime('%m')
        day = now.strftime('%d')
        timestamp = now.strftime('%Y%m%d_%H%M%S')

        output_path = os.path.join(output_dir, year, month, day)
        os.makedirs(output_path, exist_ok=True)

        filename = f"weibo_{result['screen_name']}_{timestamp}.json"
        output_file = os.path.join(output_path, filename)

        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)

        print(f"\n{'='*60}")
        print(f"✓ 结果已保存到: {output_file}")
        print(f"{'='*60}")


def main():
    """主函数"""
    print("\n" + "="*60)
    print("微博动态监测测试 Demo - Selenium版本")
    print("="*60)
    print("\n说明：使用Selenium模拟真实浏览器，绕过反爬限制")
    print("要求：已安装Chrome浏览器和chromedriver\n")

    # 配置要监测的微博账号
    accounts = [
        {'user_id': '5704967686', 'screen_name': '咻咻满'},
    ]

    monitor = WeiboMonitorSelenium(headless=True)

    for account in accounts:
        user_id = account['user_id']
        screen_name = account.get('screen_name')

        try:
            result = monitor.monitor(user_id, screen_name=screen_name, max_posts=5)
            monitor.save_result(result)

        except KeyboardInterrupt:
            print("\n\n监测已中断")
            break
        except Exception as e:
            print(f"\n✗ 监测用户 {user_id} 时出错: {e}")
            continue

    print("\n监测完成！\n")


if __name__ == '__main__':
    main()
