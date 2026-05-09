#!/usr/bin/env python3
"""
满の动态爬虫脚本
每5分钟爬取咻咻满的微博和B站动态增量内容，写入数据库
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


class BilibiliDynamicCrawler:
    """B站动态爬取器"""

    API_URL = 'https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space'
    TIMEOUT = 15

    def __init__(self):
        self.bilibili_uid = os.environ.get('BILIBILI_UID', '37754047')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 '
                          '(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Referer': 'https://space.bilibili.com/',
            'Origin': 'https://space.bilibili.com',
        })

    def fetch_dynamics(self, cookie_string=None):
        """获取用户动态列表"""
        if cookie_string:
            self.session.cookies.set('Cookie', cookie_string, domain='.bilibili.com')

        try:
            params = {
                'host_mid': self.bilibili_uid,
                'offset': '',
                'timezone_offset': '-480',
            }
            response = self.session.get(
                self.API_URL, params=params, timeout=self.TIMEOUT
            )
            response.raise_for_status()
            data = response.json()

            code = data.get('code')
            if code != 0:
                print(f"  B站API返回错误: code={code}, message={data.get('message')}")
                return None, code

            items = data.get('data', {}).get('items', [])
            parsed = self._parse_items(items)
            return parsed, code

        except requests.RequestException as e:
            print(f"  B站请求失败: {e}")
            return None, None
        except json.JSONDecodeError as e:
            print(f"  B站JSON解析失败: {e}")
            return None, None

    def _parse_items(self, items):
        """解析动态项"""
        dynamics = []
        for item in items:
            try:
                module_author = item.get('modules', {}).get('module_author', {})
                dynamic_info = item.get('modules', {}).get('module_dynamic', {})
                stat = item.get('modules', {}).get('module_stat', {})

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
        """从 major 字段提取视频 BV 号"""
        if not major:
            return ''
        archive = major.get('archive')
        if not archive:
            return ''
        return archive.get('bvid', '')

    @staticmethod
    def _extract_images(major):
        """从 major 字段提取图片 URL（draw 图片 + archive 封面）"""
        urls = []
        if not major:
            return urls

        draw = major.get('draw')
        if draw:
            items = draw.get('items', [])
            for img in items:
                src = img.get('src', '')
                if src:
                    urls.append(src)

        archive = major.get('archive')
        if archive:
            cover = archive.get('cover', '')
            if cover and cover not in urls:
                urls.insert(0, cover)

        return urls


class WeiboDynamicCrawler:
    """微博动态爬取器（requests API方式）"""

    API_URL = 'https://m.weibo.cn/api/container/getIndex'
    TIMEOUT = 15

    def __init__(self):
        self.weibo_uid = os.environ.get('WEIBO_UID', '5704967686')
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) '
                          'AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
            'Accept': 'application/json, text/plain, */*',
            'Referer': f'https://m.weibo.cn/u/{self.weibo_uid}',
        })

    def fetch_dynamics(self, cookie_string=None, max_pages=3):
        """获取微博动态"""
        if cookie_string:
            self.session.cookies.set('Cookie', cookie_string, domain='.weibo.cn')

        try:
            params = {
                'type': 'uid',
                'value': self.weibo_uid,
                'containerid': f'107603{self.weibo_uid}',
            }

            all_posts = []
            for page in range(max_pages):
                response = self.session.get(
                    self.API_URL, params=params, timeout=self.TIMEOUT
                )
                response.raise_for_status()
                data = response.json()

                ok = data.get('ok')
                if ok != 1:
                    print(f"  微博API返回异常: ok={ok}")
                    break

                cards = data.get('data', {}).get('cards', [])
                parsed = self._parse_cards(cards)
                all_posts.extend(parsed)

                since_id = data.get('data', {}).get('cardlistInfo', {}).get('since_id')
                if not since_id or len(cards) == 0:
                    break

                params['since_id'] = since_id
                time.sleep(random.uniform(1, 2))

            return all_posts, 1

        except requests.RequestException as e:
            print(f"  微博请求失败: {e}")
            return None, None
        except json.JSONDecodeError as e:
            print(f"  微博JSON解析失败: {e}")
            return None, None

    def _parse_cards(self, cards):
        """解析微博卡片"""
        posts = []
        for card in cards:
            if card.get('card_type') != 9:
                continue
            try:
                mblog = card.get('mblog', {})
                if not mblog:
                    continue

                weibo_id = mblog.get('id', '')
                if not weibo_id:
                    continue

                created_at = mblog.get('created_at', '')
                try:
                    pub_time = datetime.strptime(created_at, '%a %b %d %H:%M:%S %z %Y')
                except (ValueError, TypeError):
                    pub_time = datetime.now()

                text = mblog.get('text_raw', '') or mblog.get('text', '')
                text = self._clean_html(text)

                pics = mblog.get('pics', [])
                image_urls = [
                    p.get('large', {}).get('url') or p.get('url', '')
                    for p in pics
                    if p.get('large', {}).get('url') or p.get('url')
                ]

                source_url = f'https://m.weibo.cn/detail/{weibo_id}'

                page_info = mblog.get('page_info', {})
                video_url = ''
                if page_info:
                    ptype = page_info.get('type', '')
                    if ptype == 'video':
                        video_url = page_info.get('page_url', '')
                    elif 'media_stream_url' in page_info:
                        video_url = page_info.get('media_stream_url', '')

                posts.append({
                    'source_id': str(weibo_id),
                    'content': text,
                    'image_urls': image_urls,
                    'publish_time': pub_time,
                    'like_count': int(mblog.get('attitudes_count', 0) or 0),
                    'comment_count': int(mblog.get('comments_count', 0) or 0),
                    'share_count': int(mblog.get('reposts_count', 0) or 0),
                    'source_url': source_url,
                    'video_bvid': '',
                    'video_url': video_url,
                })
            except Exception as e:
                print(f"  解析微博卡片失败: {e}")
                continue

        return posts

    @staticmethod
    def _clean_html(text):
        """去除 HTML 标签"""
        import re
        text = re.sub(r'<br\s*/?>', '\n', text)
        text = re.sub(r'<[^>]+>', '', text)
        return text.strip()


class MomentSaver:
    """动态保存器 - 去重 + 写入 DB + 下载图片"""

    @classmethod
    def save_dynamics(cls, source, dynamics):
        """保存动态列表，去重并下载图片（每篇最多下载4张）"""
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
    parser = argparse.ArgumentParser(description='满の动态爬虫')
    parser.add_argument('--full', action='store_true', help='全量抓取（首次使用）')
    args = parser.parse_args()

    weibo_pages = 10 if args.full else 1

    print("=" * 60)
    print("满の动态爬虫")
    print(f"开始时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    results = {'bilibili': {'saved': 0, 'skipped': 0, 'error': ''},
               'weibo': {'saved': 0, 'skipped': 0, 'error': ''}}

    # --- B站 ---
    print("\n[B站动态]")
    bili_cookie = CookieService.get_cookie('bilibili')
    if not bili_cookie:
        print("  未找到有效 Cookie，跳过")
        results['bilibili']['error'] = 'cookie_missing'
    else:
        crawler = BilibiliDynamicCrawler()
        dynamics, code = crawler.fetch_dynamics(bili_cookie)

        if code == -101:
            print("  Cookie 已过期")
            CookieService.mark_expired('bilibili')
            results['bilibili']['error'] = 'cookie_expired'
        elif dynamics is not None and code == 0:
            CookieService.mark_valid('bilibili')
            saved, skipped = MomentSaver.save_dynamics('bilibili', dynamics)
            results['bilibili']['saved'] = saved
            results['bilibili']['skipped'] = skipped
            print(f"  新增: {saved}, 已存在: {skipped}")
        else:
            results['bilibili']['error'] = f'api_error_code_{code}'
            print(f"  爬取失败 (code={code})")

    time.sleep(random.uniform(1, 3))

    # --- 微博 ---
    print("\n[微博动态]")
    weibo_cookie = CookieService.get_cookie('weibo')
    if not weibo_cookie:
        print("  未找到有效 Cookie，跳过")
        results['weibo']['error'] = 'cookie_missing'
    else:
        crawler = WeiboDynamicCrawler()
        dynamics, code = crawler.fetch_dynamics(weibo_cookie, max_pages=weibo_pages)

        if code != 1 and code is not None:
            print("  Cookie 可能已过期")
            CookieService.mark_expired('weibo')
            results['weibo']['error'] = 'cookie_expired'
        elif dynamics is not None:
            CookieService.mark_valid('weibo')
            saved, skipped = MomentSaver.save_dynamics('weibo', dynamics)
            results['weibo']['saved'] = saved
            results['weibo']['skipped'] = skipped
            print(f"  新增: {saved}, 已存在: {skipped}")
        else:
            results['weibo']['error'] = 'api_error'
            print(f"  爬取失败")

    print(f"\n结束时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    return results


if __name__ == '__main__':
    main()
