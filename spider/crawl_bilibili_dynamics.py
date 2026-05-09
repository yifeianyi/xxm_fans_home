#!/usr/bin/env python3
"""
B站动态全量爬虫
爬取咻咻满所有B站动态，写入数据库。支持分页遍历直到无更多数据。
两条动态间的爬取间隔：0.3 - 2 秒（随机）

用法:
    python spider/crawl_bilibili_dynamics.py              # 增量爬取（最多 5 页）
    python spider/crawl_bilibili_dynamics.py --full        # 全量爬取（不限页数）
    python spider/crawl_bilibili_dynamics.py --max-pages 3 # 指定最大页数
"""
import sys
import os
import json
import time
import random
from datetime import datetime

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


class BilibiliCrawler:

    API_URL = 'https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space'
    TIMEOUT = 15
    DEFAULT_MAX_PAGES = 5
    FULL_MAX_PAGES = 200

    def __init__(self):
        self.bilibili_uid = os.environ.get('BILIBILI_UID', '37754047')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': (
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) '
                'AppleWebKit/537.36 (KHTML, like Gecko) '
                'Chrome/120.0.0.0 Safari/537.36'
            ),
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://space.bilibili.com/',
            'Origin': 'https://space.bilibili.com',
        })

    def fetch_all(self, cookie_string=None, max_pages=None):
        """
        Returns (dynamics_list, api_code).
        api_code: 0=success, -101=cookie_expired.
        """
        if max_pages is None:
            max_pages = self.DEFAULT_MAX_PAGES

        if cookie_string:
            self._apply_cookie(cookie_string, '.bilibili.com')

        all_dynamics = []
        offset = ''
        page = 0
        code = 0

        while max_pages is None or page < max_pages:
            page += 1
            try:
                params = {
                    'host_mid': self.bilibili_uid,
                    'offset': offset,
                    'timezone_offset': '-480',
                }
                response = self.session.get(self.API_URL, params=params, timeout=self.TIMEOUT)
                response.raise_for_status()
                data = response.json()

                code = data.get('code')
                if code != 0:
                    print(f"  B站 API 返回错误: code={code}, message={data.get('message')}")
                    break

                items = data.get('data', {}).get('items', [])
                has_more = data.get('data', {}).get('has_more', False)
                next_offset = data.get('data', {}).get('offset', '')

                if not items:
                    print(f"  第 {page} 页无数据，停止翻页")
                    break

                parsed = self._parse_items(items)
                all_dynamics.extend(parsed)

                print(f"  第 {page} 页: 获取 {len(parsed)} 条 (累计 {len(all_dynamics)} 条)")

                if not has_more or not next_offset:
                    print(f"  已到最后一页")
                    break

                offset = next_offset

            except requests.RequestException as e:
                print(f"  第 {page} 页请求失败: {e}")
                break
            except json.JSONDecodeError as e:
                print(f"  第 {page} 页 JSON 解析失败: {e}")
                break

            delay = random.uniform(MIN_INTERVAL, MAX_INTERVAL)
            time.sleep(delay)

        return all_dynamics, code

    def _apply_cookie(self, cookie_string, domain):
        for part in cookie_string.split(';'):
            part = part.strip()
            if '=' not in part:
                continue
            key, _, value = part.partition('=')
            self.session.cookies.set(key.strip(), value, domain=domain)

    def _parse_items(self, items):
        dynamics = []
        for item in items:
            try:
                modules = item.get('modules', {})
                module_author = modules.get('module_author', {})
                dynamic_info = modules.get('module_dynamic', {})
                stat = modules.get('module_stat', {})

                dyn_id = item.get('id_str', '')
                if not dyn_id:
                    continue

                pub_ts = module_author.get('pub_ts')
                if pub_ts is not None:
                    ts = int(pub_ts)
                    if ts > 1e12:
                        ts = ts // 1000
                    pub_time = datetime.fromtimestamp(ts)
                else:
                    pub_time = datetime.now()

                desc = dynamic_info.get('desc')
                if isinstance(desc, dict):
                    text = desc.get('text', '') or ''
                elif desc is None:
                    text = ''
                else:
                    text = str(desc)

                major = dynamic_info.get('major')
                image_urls = self._extract_images(major)
                video_bvid = self._extract_bvid(major)

                if not text and major:
                    archive = major.get('archive')
                    if archive:
                        text = archive.get('title', '') or ''

                source_url = f'https://t.bilibili.com/{dyn_id}'

                dynamics.append({
                    'source_id': str(dyn_id),
                    'content': text,
                    'image_urls': image_urls,
                    'publish_time': pub_time,
                    'like_count': stat.get('like', {}).get('count', 0) or 0,
                    'comment_count': stat.get('comment', {}).get('count', 0) or 0,
                    'share_count': stat.get('forward', {}).get('count', 0) or 0,
                    'source_url': source_url,
                    'video_bvid': video_bvid,
                    'video_url': '',
                })
            except Exception as e:
                print(f"  解析B站动态项失败: {e}")
                continue

        return dynamics

    @staticmethod
    def _extract_bvid(major):
        if not major:
            return ''
        archive = major.get('archive')
        if not archive:
            return ''
        return archive.get('bvid', '')

    @staticmethod
    def _extract_images(major):
        urls = []
        if not major:
            return urls

        draw = major.get('draw')
        if draw:
            for img in draw.get('items', []):
                src = img.get('src', '')
                if src:
                    urls.append(src)

        archive = major.get('archive')
        if archive:
            cover = archive.get('cover', '')
            if cover and cover not in urls:
                urls.insert(0, cover)

        return urls


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
    parser = argparse.ArgumentParser(description='B站动态全量爬虫')
    parser.add_argument('--full', action='store_true', help='全量抓取（不限页数，最多 200 页）')
    parser.add_argument('--max-pages', type=int, default=None, help='指定最大翻页数')
    args = parser.parse_args()

    if args.full:
        max_pages = BilibiliCrawler.FULL_MAX_PAGES
        mode_label = '全量'
    elif args.max_pages is not None:
        max_pages = args.max_pages
        mode_label = f'指定 {max_pages} 页'
    else:
        max_pages = BilibiliCrawler.DEFAULT_MAX_PAGES
        mode_label = '增量'

    print("=" * 60)
    print(f"B站动态爬虫 - {mode_label}模式")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"间隔范围: {MIN_INTERVAL}s - {MAX_INTERVAL}s")
    print("=" * 60)

    cookie = CookieService.get_cookie('bilibili')
    if not cookie:
        print("❌ 未找到有效的 B站 Cookie，请在 Django Admin 中配置")
        return {'bilibili': {'saved': 0, 'skipped': 0, 'error': 'cookie_missing'}}

    crawler = BilibiliCrawler()
    dynamics, code = crawler.fetch_all(cookie, max_pages=max_pages)

    result = {'bilibili': {'saved': 0, 'skipped': 0, 'error': ''}}

    if code == -101:
        print("❌ Cookie 已过期")
        CookieService.mark_expired('bilibili')
        result['bilibili']['error'] = 'cookie_expired'
    elif dynamics is not None and code == 0:
        CookieService.mark_valid('bilibili')
        saved, skipped = MomentSaver.save_dynamics('bilibili', dynamics)
        result['bilibili']['saved'] = saved
        result['bilibili']['skipped'] = skipped
        print(f"\n✓ 完成: 新增 {saved}, 已存在 {skipped}")
    else:
        result['bilibili']['error'] = f'api_error_code_{code}'
        print(f"\n❌ 爬取失败 (code={code})")

    print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)
    return result


if __name__ == '__main__':
    main()
