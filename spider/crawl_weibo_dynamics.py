#!/usr/bin/env python3
"""
微博动态全量爬虫（桌面版 API）
爬取咻咻满所有微博动态，写入数据库。支持分页遍历直到无更多数据。
两条动态间的爬取间隔：0.3 - 2 秒（随机）

用法:
    python spider/crawl_weibo_dynamics.py              # 增量爬取（最多 3 页）
    python spider/crawl_weibo_dynamics.py --full        # 全量爬取（不限页数）
    python spider/crawl_weibo_dynamics.py --max-pages 5 # 指定最大页数
"""
import sys
import os
import json
import time
import random
import re
from datetime import datetime
from urllib.parse import quote

import requests
import django

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_PATH = os.path.join(PROJECT_ROOT, 'repo', 'xxm_fans_backend')

sys.path.insert(0, BACKEND_PATH)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')
django.setup()

from django.utils import timezone
from django.db.utils import IntegrityError
from moments.models import Moment, PlatformCookie
from moments.services.cookie_service import CookieService
from moments.services.image_service import ImageService

MIN_INTERVAL = 0.3
MAX_INTERVAL = 2.0


class WeiboCrawler:

    API_URL = 'https://weibo.com/ajax/statuses/mymblog'
    TIMEOUT = 15
    DEFAULT_MAX_PAGES = 3
    FULL_MAX_PAGES = 500

    def __init__(self):
        self.weibo_uid = os.environ.get('WEIBO_UID', '5704967686')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
            'Accept': 'application/json, text/plain, */*',
            'X-Requested-With': 'XMLHttpRequest',
            'Referer': 'https://weibo.com/',
        })

    def fetch_all(self, cookie_string=None, max_pages=None):
        """
        Returns (posts_list, api_code).
        api_code: 1=success, None=failure.
        """
        if max_pages is None:
            max_pages = self.DEFAULT_MAX_PAGES

        if cookie_string:
            self._apply_cookie(cookie_string, '.weibo.com')

        all_posts = []
        since_id = ''
        code = 1

        try:
            for page in range(1, max_pages + 1):
                url = f'{self.API_URL}?uid={self.weibo_uid}&page={page}&feature=0'
                if since_id:
                    url += f'&since_id={quote(since_id)}'

                response = self.session.get(url, timeout=self.TIMEOUT)
                response.raise_for_status()
                data = response.json()

                ok = data.get('ok')
                if ok != 1:
                    print(f"  微博 API 返回异常: ok={ok}")
                    code = 0
                    break

                posts_data = data.get('data', {})
                posts_list = posts_data.get('list', [])
                if not posts_list:
                    print(f"  第 {page} 页无数据，停止翻页")
                    break

                parsed = self._parse_posts(posts_list)
                all_posts.extend(parsed)

                print(f"  第 {page} 页: 获取 {len(parsed)} 条 (累计 {len(all_posts)} 条)")

                next_since_id = posts_data.get('since_id', '')
                if not next_since_id:
                    total = posts_data.get('total', 0)
                    if len(all_posts) >= total:
                        print(f"  已到最后一页（共 {total} 条）")
                    break

                since_id = next_since_id
                delay = random.uniform(MIN_INTERVAL, MAX_INTERVAL)
                time.sleep(delay)

            return all_posts, code

        except requests.RequestException as e:
            print(f"  微博请求失败: {e}")
            return None, None
        except json.JSONDecodeError as e:
            print(f"  微博 JSON 解析失败: {e}")
            return None, None

    def _apply_cookie(self, cookie_string, domain):
        for part in cookie_string.split(';'):
            part = part.strip()
            if '=' not in part:
                continue
            key, _, value = part.partition('=')
            self.session.cookies.set(key.strip(), value, domain=domain)

    def _parse_posts(self, posts_list):
        posts = []
        for post in posts_list:
            try:
                post_id = post.get('idstr') or post.get('mid') or str(post.get('id', ''))
                if not post_id:
                    continue

                created_at = post.get('created_at', '')
                try:
                    pub_time = datetime.strptime(created_at, '%a %b %d %H:%M:%S %z %Y')
                except (ValueError, TypeError):
                    pub_time = datetime.now()

                text = post.get('text_raw', '') or post.get('text', '')
                text = self._clean_html(text)

                image_urls = self._extract_images(post)

                source_url = (
                    f'https://weibo.com/{self.weibo_uid}/{post.get("mblogid", "")}'
                    if post.get('mblogid')
                    else f'https://weibo.com/u/{self.weibo_uid}'
                )

                page_info = post.get('page_info', {}) or {}
                video_url = ''
                if page_info.get('type') == 'video':
                    video_url = page_info.get('page_url', '') or page_info.get('media_info', {}).get('stream_url', '')

                posts.append({
                    'source_id': str(post_id),
                    'content': text,
                    'image_urls': image_urls,
                    'publish_time': pub_time,
                    'like_count': int(post.get('attitudes_count', 0) or 0),
                    'comment_count': int(post.get('comments_count', 0) or 0),
                    'share_count': int(post.get('reposts_count', 0) or 0),
                    'source_url': source_url,
                    'video_bvid': '',
                    'video_url': video_url,
                })
            except Exception as e:
                print(f"  解析微博帖子失败: {e}")
                continue

        return posts

    @staticmethod
    def _extract_images(post):
        urls = []
        pic_ids = post.get('pic_ids', []) or []
        pic_infos = post.get('pic_infos', {}) or {}

        for pid in pic_ids:
            info = pic_infos.get(pid, {})
            largest = info.get('largest', {}) or info.get('large', {}) or info.get('original', {})
            url = largest.get('url', '')
            if url:
                urls.append(url)

        return urls

    @staticmethod
    def _clean_html(text):
        text = re.sub(r'<br\s*/?>', '\n', text)
        text = re.sub(r'<[^>]+>', '', text)
        return text.strip()


class MomentSaver:

    @classmethod
    def save_dynamics(cls, source, dynamics):
        saved = 0
        skipped = 0

        for dyn in dynamics:
            exists = Moment.objects.filter(
                source=source,
                source_id=dyn['source_id'],
            ).exists()
            if exists:
                skipped += 1
                continue

            images = []
            if dyn.get('image_urls'):
                images = ImageService.download_and_generate_thumbnails(
                    source, dyn['source_id'], dyn['image_urls'][:4]
                )

            try:
                if isinstance(dyn['publish_time'], datetime):
                    pub_time = dyn['publish_time']
                else:
                    pub_time = datetime.fromisoformat(str(dyn['publish_time']))
                if timezone.is_naive(pub_time):
                    pub_time = timezone.make_aware(pub_time)

                Moment.objects.create(
                    source=source,
                    source_id=dyn['source_id'],
                    content=dyn.get('content', ''),
                    images=images,
                    publish_time=pub_time,
                    like_count=dyn.get('like_count', 0),
                    comment_count=dyn.get('comment_count', 0),
                    share_count=dyn.get('share_count', 0),
                    source_url=dyn.get('source_url', ''),
                    video_bvid=dyn.get('video_bvid', ''),
                    video_url=dyn.get('video_url', ''),
                )
                saved += 1
            except IntegrityError:
                skipped += 1
            except Exception as e:
                print(f"  保存动态失败 [{source}]: {e}")

        return saved, skipped


def main():
    import argparse
    parser = argparse.ArgumentParser(description='微博动态全量爬虫')
    parser.add_argument('--full', action='store_true', help='全量抓取（不限页数，最多 500 页）')
    parser.add_argument('--max-pages', type=int, default=None, help='指定最大翻页数')
    args = parser.parse_args()

    if args.full:
        max_pages = WeiboCrawler.FULL_MAX_PAGES
        mode_label = '全量'
    elif args.max_pages is not None:
        max_pages = args.max_pages
        mode_label = f'指定 {max_pages} 页'
    else:
        max_pages = WeiboCrawler.DEFAULT_MAX_PAGES
        mode_label = '增量'

    print("=" * 60)
    print(f"微博动态爬虫 - {mode_label}模式")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"间隔范围: {MIN_INTERVAL}s - {MAX_INTERVAL}s")
    print("=" * 60)

    cookie = CookieService.get_cookie('weibo')
    if not cookie:
        print("❌ 未找到有效的 微博 Cookie，请在 Django Admin 中配置")
        return {'weibo': {'saved': 0, 'skipped': 0, 'error': 'cookie_missing'}}

    crawler = WeiboCrawler()
    dynamics, code = crawler.fetch_all(cookie, max_pages=max_pages)

    result = {'weibo': {'saved': 0, 'skipped': 0, 'error': ''}}

    if code is None:
        print("❌ 爬取失败")
        CookieService.mark_expired('weibo')
        result['weibo']['error'] = 'api_error'
    elif code == 1 and dynamics is not None:
        CookieService.mark_valid('weibo')
        saved, skipped = MomentSaver.save_dynamics('weibo', dynamics)
        result['weibo']['saved'] = saved
        result['weibo']['skipped'] = skipped
        print(f"\n✓ 完成: 新增 {saved}, 已存在 {skipped}")
    else:
        print("❌ Cookie 可能已过期")
        CookieService.mark_expired('weibo')
        result['weibo']['error'] = 'cookie_expired'

    print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    return result


if __name__ == '__main__':
    main()
