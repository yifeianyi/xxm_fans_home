#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
B站粉丝数爬虫脚本
获取指定B站账号的粉丝数并保存为JSON文件
"""

import json
import time
import requests
import os
from datetime import datetime


def get_fans_count(uid):
    """
    获取指定B站账号的粉丝数

    Args:
        uid (int): B站账号UID

    Returns:
        dict: 包含账号信息和粉丝数的字典
    """
    url = f"https://api.bilibili.com/x/relation/stat?vmid={uid}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Referer': 'https://www.bilibili.com'
    }

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get('code') == 0:
            follower = data['data']['follower']
            return {
                'uid': uid,
                'follower': follower,
                'status': 'success',
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
        else:
            return {
                'uid': uid,
                'follower': None,
                'status': 'error',
                'message': data.get('message', 'Unknown error'),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
    except requests.RequestException as e:
        return {
            'uid': uid,
            'follower': None,
            'status': 'error',
            'message': str(e),
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }


def main():
    """主函数"""
    # 定义要查询的B站账号
    accounts = [
        {'uid': 37754047, 'name': '咻咻满'},
        {'uid': 480116537, 'name': '咻小满'}
    ]

    results = []

    print("开始获取B站粉丝数...")
    print("-" * 50)

    for account in accounts:
        print(f"正在获取 {account['name']} (UID: {account['uid']}) 的粉丝数...")
        result = get_fans_count(account['uid'])
        result['name'] = account['name']
        results.append(result)

        if result['status'] == 'success':
            print(f"✓ {account['name']}: {result['follower']:,} 粉丝")
        else:
            print(f"✗ {account['name']}: 获取失败 - {result.get('message', 'Unknown error')}")

        # 避免请求过快
        time.sleep(1)

    print("-" * 50)

    # 保存为JSON文件，文件名包含日期时间戳
    now = datetime.now()
    timestamp = now.strftime('%Y-%m-%d-%H')
    year = now.strftime('%Y')
    month = now.strftime('%m')

    # 创建输出目录（相对路径）
    output_dir = f'data/spider/fans_count/{year}/{month}'
    os.makedirs(output_dir, exist_ok=True)

    output_file = f'{output_dir}/b_fans_count_{timestamp}.json'
    output_data = {
        'update_time': now.strftime('%Y-%m-%d %H:%M:%S'),
        'accounts': results
    }

    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(output_data, f, ensure_ascii=False, indent=2)

    print(f"\n数据已保存到: {output_file}")
    print(f"共获取 {len(results)} 个账号的信息")


if __name__ == '__main__':
    main()