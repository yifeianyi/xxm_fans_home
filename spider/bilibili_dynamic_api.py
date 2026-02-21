#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站动态监测测试 Demo - API版本
使用requests直接调用B站API获取用户动态
"""

import json
import time
import random
from datetime import datetime
import requests


class BilibiliDynamicMonitorAPI:
    """B站动态监控类 - API版本"""

    def __init__(self):
        """初始化监控器"""
        self.session = requests.Session()
        # 设置完整的请求头模拟真实浏览器
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Referer': 'https://www.bilibili.com',
            'Origin': 'https://www.bilibili.com',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-site',
            'Sec-Ch-Ua': '"Not_A Brand";v="8", "Chromium";v="120", "Google Chrome";v="120"',
            'Sec-Ch-Ua-Mobile': '?0',
            'Sec-Ch-Ua-Platform': '"Windows"',
        })
        
        # 初始化时访问B站主页获取基础Cookie
        self._init_session()
    
    def _init_session(self):
        """初始化会话，获取基础Cookie"""
        try:
            print("  初始化会话，访问B站主页...")
            response = self.session.get('https://www.bilibili.com', timeout=10)
            if response.status_code == 200:
                cookies = self.session.cookies.get_dict()
                print(f"  ✓ 成功获取Cookie: {list(cookies.keys())}")
        except Exception as e:
            print(f"  警告：初始化会话失败: {e}")

    def get_user_dynamics(self, uid, max_count=10):
        """
        获取用户动态

        Args:
            uid (str): B站用户UID
            max_count (int): 获取最大动态数量

        Returns:
            list: 动态列表
        """
        # 尝试多种API接口
        apis = [
            # 方法1: 动态列表API
            {
                'url': f'https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/space',
                'params': {'host_mid': str(uid), 'offset': '', 'timezone_offset': '-480'}
            },
            # 方法2: 用户动态API（新版）
            {
                'url': f'https://api.bilibili.com/x/polymer/web-dynamic/v1/feed/author/dynamics',
                'params': {'mid': str(uid), 'features': 'itemOpusStyle'}
            },
            # 方法3: 旧版动态API
            {
                'url': f'https://api.vc.bilibili.com/dynamic_svr/v1/dynamic_svr/space_history',
                'params': {'visitor_uid': '0', 'host_mid': str(uid), 'offset_dynamic_id': '0'}
            }
        ]

        for i, api_config in enumerate(apis):
            try:
                print(f"  尝试API方法 {i+1}: {api_config['url'].split('/')[-1]}")
                dynamics = self._fetch_from_api(api_config, max_count)
                if dynamics:
                    print(f"  ✓ 使用方法 {i+1} 成功获取 {len(dynamics)} 条动态")
                    return dynamics
            except Exception as e:
                print(f"  方法 {i+1} 失败: {e}")
                continue

        print("  ✗ 所有API方法均失败")
        return []

    def _fetch_from_api(self, api_config, max_count):
        """
        从API获取数据

        Args:
            api_config (dict): API配置
            max_count (int): 最大数量

        Returns:
            list: 动态列表
        """
        try:
            # 可选：添加Cookie以绕过某些限制
            # 获取Cookie方法：
            # 1. 登录B站网页版
            # 2. 打开浏览器开发者工具 (F12)
            # 3. Network标签 -> 找到请求 -> 复制Cookie
            # 4. 取消下面注释并替换为真实Cookie
            # self.session.headers.update({
            #     'Cookie': 'buvid3=xxx; SESSDATA=xxx; bili_jct=xxx'
            # })

            response = self.session.get(
                api_config['url'],
                params=api_config['params'],
                timeout=10
            )

            # 输出调试信息
            print(f"  响应状态码: {response.status_code}")
            print(f"  响应长度: {len(response.content)}")

            response.raise_for_status()

            data = response.json()

            # 检查API响应
            if data.get('code') != 0:
                print(f"  API返回错误: code={data.get('code')}, message={data.get('message', 'Unknown error')}")
                return []

            # 解析不同API格式的响应
            items = []
            
            # 尝试从不同路径获取动态列表
            data_value = data.get('data', {})
            if isinstance(data_value, dict):
                # 尝试各种可能的字段名
                for key in ['items', 'list', 'dynamics', 'cards', 'archives', 'content']:
                    if key in data_value and isinstance(data_value[key], list):
                        items = data_value[key]
                        print(f"  从路径 'data.{key}' 找到 {len(items)} 个动态")
                        break
                
                # 如果还没找到，尝试获取data下的所有list类型值
                if not items:
                    for key, value in data_value.items():
                        if isinstance(value, list) and len(value) > 0:
                            items = value
                            print(f"  从路径 'data.{key}' 找到 {len(items)} 个动态")
                            break
            elif isinstance(data_value, list):
                items = data_value
                print(f"  从路径 'data' 找到 {len(items)} 个动态")

            if not items:
                print(f"  API响应数据结构: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}...")
                return []

            # 解析动态项
            dynamics = []
            for item in items[:max_count]:
                try:
                    dynamic = self.parse_dynamic_item(item)
                    if dynamic and dynamic.get('content'):
                        dynamics.append(dynamic)
                except Exception as e:
                    print(f"  解析动态项失败: {e}")
                    continue

            return dynamics

        except requests.RequestException as e:
            print(f"  请求失败: {e}")
            return []
        except json.JSONDecodeError as e:
            print(f"  JSON解析失败: {e}")
            if 'response' in locals():
                print(f"  Content-Type: {response.headers.get('Content-Type', 'unknown')}")
                print(f"  响应内容预览: {response.text[:200]}")
            return []
        except Exception as e:
            print(f"  解析响应失败: {e}")
            import traceback
            traceback.print_exc()
            return []

    def parse_dynamic_item(self, item):
        """
        解析单个动态项

        Args:
            item: 动态项数据

        Returns:
            dict: 动态信息
        """
        dynamic = {}

        try:
            # 动态ID
            dynamic['id'] = str(item.get('id') or item.get('dyn_id') or item.get('dynamic_id') or hash(str(item)))

            # 发布时间
            timestamp = item.get('pub_time') or item.get('timestamp') or item.get('pub_ts')
            if timestamp:
                try:
                    if isinstance(timestamp, int) and timestamp > 1000000000:  # Unix时间戳
                        pub_time = datetime.fromtimestamp(timestamp)
                        dynamic['publish_time'] = pub_time.strftime('%Y-%m-%d %H:%M:%S')
                    else:
                        dynamic['publish_time'] = str(timestamp)
                except:
                    dynamic['publish_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            else:
                dynamic['publish_time'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

            # 动态内容 - 尝试多个字段
            content = ''
            for field in ['content', 'text', 'desc', 'description', 'raw_text', 'card']:
                value = item.get(field)
                if isinstance(value, str) and len(value) > 0:
                    content = value
                    break
                elif isinstance(value, dict):
                    # 可能是嵌套的内容对象
                    for subfield in ['text', 'content', 'desc']:
                        subvalue = value.get(subfield)
                        if isinstance(subvalue, str) and len(subvalue) > 0:
                            content = subvalue
                            break
            
            dynamic['content'] = content.strip()

            # 互动数据
            stats = item.get('stat') or item.get('stats') or {}
            dynamic['likes'] = str(stats.get('like') or stats.get('likes') or 0)
            dynamic['comments'] = str(stats.get('comment') or stats.get('comments') or 0)
            dynamic['shares'] = str(stats.get('share') or stats.get('repost') or 0)

            # 图片信息
            dynamic['has_images'] = False
            dynamic['image_count'] = 0
            pictures = item.get('pictures') or item.get('image') or []
            if pictures and len(pictures) > 0:
                dynamic['has_images'] = True
                dynamic['image_count'] = len(pictures)
                if isinstance(pictures, list) and len(pictures) > 0:
                    first_pic = pictures[0]
                    if isinstance(first_pic, dict):
                        dynamic['first_image'] = first_pic.get('img_src') or first_pic.get('url') or first_pic.get('src')
                    elif isinstance(first_pic, str):
                        dynamic['first_image'] = first_pic

            # 视频信息
            dynamic['has_video'] = False
            video = item.get('video') or item.get('archive') or item.get('major')
            if video:
                dynamic['has_video'] = True

            return dynamic

        except Exception as e:
            print(f"  解析动态项失败: {e}")
            import traceback
            traceback.print_exc()
            return None

    def close(self):
        """关闭会话"""
        self.session.close()


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
    print("B站动态监测测试 Demo - API版本")
    print("=" * 60)
    print()
    print("说明：使用requests直接调用B站API获取用户动态")
    print("要求：已安装requests库")
    print()
    print("注意：")
    print("1. B站API可能需要Cookie才能正常访问")
    print("2. 如果遇到412/403错误，请添加Cookie")
    print("3. 获取Cookie方法：")
    print("   - 登录B站网页版")
    print("   - 打开浏览器开发者工具")
    print("   - 复制Cookie并在代码第42行添加")
    print()

    # 定义要监控的B站用户
    accounts = [
        {'uid': '37754047', 'name': '咻咻满'},
        {'uid': '480116537', 'name': '咻小满'}
    ]

    # 初始化监控器
    monitor = BilibiliDynamicMonitorAPI()

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
            output_file = f'{output_dir}/bilibili_dynamic_{account["name"]}_api_{timestamp}.json'

            save_result(account, dynamics, output_file)

            # 显示简要信息
            print(f"\n  最新动态预览:")
            for i, dyn in enumerate(dynamics[:3], 1):
                print(f"    [{i}] {dyn['publish_time']}")
                content_preview = dyn['content'][:50] + '...' if len(dyn['content']) > 50 else dyn['content']
                print(f"        {content_preview}")
                print(f"        点赞: {dyn['likes']} 评论: {dyn['comments']}")
        else:
            print("  未获取到动态，可能是API限制或账号未公开动态")

        # 避免请求过快
        time.sleep(random.uniform(1, 3))

    # 关闭会话
    monitor.close()

    print()
    print("=" * 60)
    print("监测完成！")
    print("=" * 60)


if __name__ == '__main__':
    main()
