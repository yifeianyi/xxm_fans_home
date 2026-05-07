#!/usr/bin/env python3
"""
满の动态爬虫单元测试
覆盖：B站API解析、微博API解析、去重逻辑、Cookie过期检测
"""
import sys
import os
import unittest
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_PATH = os.path.join(PROJECT_ROOT, 'repo', 'xxm_fans_backend')

sys.path.insert(0, BACKEND_PATH)
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')

import django
django.setup()

sys.path.insert(0, os.path.join(PROJECT_ROOT, 'spider'))
from crawl_moments import BilibiliDynamicCrawler, WeiboDynamicCrawler, MomentSaver


class TestBilibiliDynamicCrawler(unittest.TestCase):
    """B站动态爬取器测试"""

    def setUp(self):
        self.crawler = BilibiliDynamicCrawler()

    def test_parse_dynamic_items_basic(self):
        """测试基本动态解析"""
        items = [{
            'id_str': '123456789',
            'modules': {
                'module_author': {
                    'id': '123456789',
                    'pub_ts': 1730000000,
                },
                'module_dynamic': {
                    'desc': {'text': '这是一条B站动态测试'},
                    'major': None,
                },
                'module_stat': {
                    'like': {'count': 42},
                    'comment': {'count': 5},
                    'forward': {'count': 3},
                },
            },
        }]
        dynamics = self.crawler._parse_items(items)
        self.assertEqual(len(dynamics), 1)
        self.assertEqual(dynamics[0]['source_id'], '123456789')
        self.assertEqual(dynamics[0]['content'], '这是一条B站动态测试')
        self.assertEqual(dynamics[0]['like_count'], 42)
        self.assertEqual(dynamics[0]['comment_count'], 5)
        self.assertEqual(dynamics[0]['share_count'], 3)

    def test_parse_dynamic_items_with_images(self):
        """测试带图片的动态解析"""
        items = [{
            'id_str': 'img001',
            'modules': {
                'module_author': {
                    'id': 'img001',
                    'pub_ts': 1730000000,
                },
                'module_dynamic': {
                    'desc': {'text': '图片动态'},
                    'major': {
                        'draw': {
                            'items': [
                                {'src': 'https://example.com/img1.jpg'},
                                {'src': 'https://example.com/img2.png'},
                            ]
                        }
                    },
                },
                'module_stat': {
                    'like': {'count': 10},
                    'comment': {'count': 2},
                    'forward': {'count': 0},
                },
            },
        }]
        dynamics = self.crawler._parse_items(items)
        self.assertEqual(len(dynamics), 1)
        self.assertEqual(len(dynamics[0]['image_urls']), 2)
        self.assertEqual(dynamics[0]['image_urls'][0], 'https://example.com/img1.jpg')

    def test_parse_dynamic_items_no_images(self):
        """测试无图片动态"""
        items = [{
            'id_str': 'notext001',
            'modules': {
                'module_author': {
                    'id': 'notext001',
                    'pub_ts': 1730000000,
                },
                'module_dynamic': {
                    'desc': {'text': ''},
                    'major': {'draw': {'items': []}},
                },
                'module_stat': {
                    'like': {'count': 0},
                    'comment': {'count': 0},
                    'forward': {'count': 0},
                },
            },
        }]
        dynamics = self.crawler._parse_items(items)
        self.assertEqual(len(dynamics), 1)
        self.assertEqual(dynamics[0]['image_urls'], [])

    def test_parse_dynamic_items_missing_stat(self):
        """测试缺失互动数据"""
        items = [{
            'id_str': 'nostat001',
            'modules': {
                'module_author': {
                    'id': 'nostat001',
                    'pub_ts': 1730000000,
                },
                'module_dynamic': {
                    'desc': {'text': '无互动数据'},
                    'major': None,
                },
                'module_stat': {},
            },
        }]
        dynamics = self.crawler._parse_items(items)
        self.assertEqual(len(dynamics), 1)
        self.assertEqual(dynamics[0]['like_count'], 0)
        self.assertEqual(dynamics[0]['comment_count'], 0)
        self.assertEqual(dynamics[0]['share_count'], 0)

    def test_parse_dynamic_items_missing_id(self):
        """测试缺失ID的项被跳过"""
        items = [{
            'modules': {
                'module_author': {},
                'module_dynamic': {'desc': {'text': '无ID'}},
                'module_stat': {},
            },
        }]
        dynamics = self.crawler._parse_items(items)
        self.assertEqual(len(dynamics), 0)

    def test_parse_dynamic_items_empty(self):
        """测试空列表"""
        dynamics = self.crawler._parse_items([])
        self.assertEqual(dynamics, [])

    def test_extract_images_empty(self):
        """测试无图片时提取"""
        urls = BilibiliDynamicCrawler._extract_images(None)
        self.assertEqual(urls, [])

    def test_extract_images_normal(self):
        """测试正常提取图片"""
        major = {
            'draw': {
                'items': [
                    {'src': 'http://a.jpg'},
                    {'src': 'http://b.png'},
                ]
            }
        }
        urls = BilibiliDynamicCrawler._extract_images(major)
        self.assertEqual(len(urls), 2)

    def test_extract_images_skip_empty_src(self):
        """测试跳过空src"""
        major = {
            'draw': {
                'items': [
                    {'src': ''},
                    {'src': 'http://valid.jpg'},
                ]
            }
        }
        urls = BilibiliDynamicCrawler._extract_images(major)
        self.assertEqual(len(urls), 1)

    def test_extract_images_archive_cover(self):
        """测试提取 MAJOR_TYPE_ARCHIVE 封面图"""
        major = {
            'type': 'MAJOR_TYPE_ARCHIVE',
            'draw': None,
            'archive': {
                'bvid': 'BV1xx1234',
                'cover': 'http://i0.hdslb.com/cover.jpg',
            },
        }
        urls = BilibiliDynamicCrawler._extract_images(major)
        self.assertEqual(len(urls), 1)
        self.assertEqual(urls[0], 'http://i0.hdslb.com/cover.jpg')

    def test_extract_images_archive_with_draw(self):
        """测试同时有 draw 图片和 archive 封面"""
        major = {
            'type': 'MAJOR_TYPE_DRAW',
            'draw': {
                'items': [
                    {'src': 'http://draw1.jpg'},
                ]
            },
            'archive': {
                'cover': 'http://cover.jpg',
            },
        }
        urls = BilibiliDynamicCrawler._extract_images(major)
        self.assertEqual(len(urls), 2)

    def test_extract_bvid_archive(self):
        """测试从 ARCHIVE major 提取 BV 号"""
        major = {
            'type': 'MAJOR_TYPE_ARCHIVE',
            'archive': {'bvid': 'BV1bUR3BDEjh'},
        }
        bvid = BilibiliDynamicCrawler._extract_bvid(major)
        self.assertEqual(bvid, 'BV1bUR3BDEjh')

    def test_extract_bvid_none(self):
        """测试无 major 时返回空"""
        bvid = BilibiliDynamicCrawler._extract_bvid(None)
        self.assertEqual(bvid, '')

    def test_extract_bvid_no_archive(self):
        """测试无 archive 时返回空"""
        major = {'type': 'MAJOR_TYPE_DRAW'}
        bvid = BilibiliDynamicCrawler._extract_bvid(major)
        self.assertEqual(bvid, '')


class TestWeiboDynamicCrawler(unittest.TestCase):
    """微博动态爬取器测试"""

    def setUp(self):
        self.crawler = WeiboDynamicCrawler()

    def test_parse_cards_basic(self):
        """测试基本微博卡片解析"""
        cards = [{
            'card_type': 9,
            'mblog': {
                'id': 'wb001',
                'created_at': 'Sat Jun 15 14:30:00 +0800 2024',
                'text_raw': '这是一条微博测试内容',
                'pics': [],
                'attitudes_count': 100,
                'comments_count': 20,
                'reposts_count': 5,
            },
        }]
        posts = self.crawler._parse_cards(cards)
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]['source_id'], 'wb001')
        self.assertEqual(posts[0]['content'], '这是一条微博测试内容')
        self.assertEqual(posts[0]['like_count'], 100)
        self.assertEqual(posts[0]['comment_count'], 20)
        self.assertEqual(posts[0]['share_count'], 5)

    def test_parse_cards_with_images(self):
        """测试带图片的微博解析"""
        cards = [{
            'card_type': 9,
            'mblog': {
                'id': 'wb_img001',
                'created_at': 'Sun Jun 16 10:00:00 +0800 2024',
                'text': '带图微博',
                'pics': [
                    {'large': {'url': 'https://wx1.sinaimg.cn/large/img1.jpg'},
                     'url': 'https://wx1.sinaimg.cn/small/img1.jpg'},
                    {'large': {'url': 'https://wx2.sinaimg.cn/large/img2.jpg'},
                     'url': 'https://wx2.sinaimg.cn/small/img2.jpg'},
                ],
                'attitudes_count': 50,
                'comments_count': 10,
                'reposts_count': 2,
            },
        }]
        posts = self.crawler._parse_cards(cards)
        self.assertEqual(len(posts), 1)
        self.assertEqual(len(posts[0]['image_urls']), 2)
        self.assertEqual(posts[0]['image_urls'][0], 'https://wx1.sinaimg.cn/large/img1.jpg')

    def test_parse_cards_skip_non_card_type_9(self):
        """测试跳过非微博卡片"""
        cards = [
            {'card_type': 8, 'mblog': {}},
            {'card_type': 9, 'mblog': {
                'id': 'wb_keep', 'created_at': 'Sat Jun 15 14:30:00 +0800 2024',
                'text': '保留', 'pics': [],
                'attitudes_count': 0, 'comments_count': 0, 'reposts_count': 0,
            }},
        ]
        posts = self.crawler._parse_cards(cards)
        self.assertEqual(len(posts), 1)
        self.assertEqual(posts[0]['content'], '保留')

    def test_parse_cards_empty_mblog(self):
        """测试空 mblog"""
        cards = [{'card_type': 9, 'mblog': {}}]
        posts = self.crawler._parse_cards(cards)
        self.assertEqual(len(posts), 0)

    def test_parse_cards_missing_id(self):
        """测试缺失微博ID"""
        cards = [{
            'card_type': 9,
            'mblog': {'created_at': 'Sat Jun 15 14:30:00 +0800 2024', 'pics': []},
        }]
        posts = self.crawler._parse_cards(cards)
        self.assertEqual(len(posts), 0)

    def test_parse_cards_empty_list(self):
        """测试空卡片列表"""
        posts = self.crawler._parse_cards([])
        self.assertEqual(posts, [])

    def test_clean_html_basic(self):
        """测试HTML标签清除"""
        result = self.crawler._clean_html('<br/>换行<br>测试<a href="link">链接</a>')
        self.assertEqual(result, '换行\n测试链接')

    def test_clean_html_plain_text(self):
        """测试纯文本"""
        result = self.crawler._clean_html('纯文本无标签')
        self.assertEqual(result, '纯文本无标签')


class TestMomentSaver(unittest.TestCase):
    """动态保存器测试"""

    @patch('crawl_moments.ImageService')
    @patch('crawl_moments.Moment')
    def test_skip_existing_moment(self, MockMoment, MockImageService):
        """测试已存在动态跳过"""
        MockMoment.objects.filter.return_value.exists.return_value = True

        dynamics = [{
            'source_id': 'exist001',
            'content': '已存在',
            'image_urls': [],
            'publish_time': datetime(2024, 6, 15),
            'like_count': 0,
            'comment_count': 0,
            'share_count': 0,
            'source_url': 'http://example.com',
        }]

        saved, skipped = MomentSaver.save_dynamics('weibo', dynamics)
        self.assertEqual(saved, 0)
        self.assertEqual(skipped, 1)

    @patch('crawl_moments.Moment')
    @patch('crawl_moments.ImageService')
    def test_save_new_moment(self, MockImageService, MockMoment):
        """测试保存新动态"""
        MockMoment.objects.filter.return_value.exists.return_value = False
        MockImageService.download_and_generate_thumbnails.return_value = []

        dynamics = [{
            'source_id': 'new001',
            'content': '新动态',
            'image_urls': ['http://img.jpg'],
            'publish_time': datetime(2024, 6, 15),
            'like_count': 10,
            'comment_count': 2,
            'share_count': 1,
            'source_url': 'http://example.com/new',
        }]

        saved, skipped = MomentSaver.save_dynamics('bilibili', dynamics)
        self.assertEqual(saved, 1)
        self.assertEqual(skipped, 0)
        self.assertTrue(MockMoment.objects.create.called)

    @patch('crawl_moments.Moment')
    @patch('crawl_moments.ImageService')
    def test_save_empty_dynamics(self, MockImageService, MockMoment):
        """测试保存空列表"""
        saved, skipped = MomentSaver.save_dynamics('weibo', [])
        self.assertEqual(saved, 0)
        self.assertEqual(skipped, 0)
        MockMoment.objects.create.assert_not_called()


if __name__ == '__main__':
    unittest.main(verbosity=2)
