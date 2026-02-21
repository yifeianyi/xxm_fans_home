#!/usr/bin/env python3
"""
创建测试图集图片
"""
import os
from PIL import Image, ImageDraw, ImageFont

# 颜色配置
COLORS = {
    'concert': (248, 177, 149),  # 蜜桃粉
    'daily': (142, 182, 155),    # 豆沙绿
    '2024': (74, 55, 40),        # 大地棕
}

def create_test_image(width, height, color, text, output_path):
    """创建测试图片"""
    # 创建图片
    img = Image.new('RGB', (width, height), color)
    draw = ImageDraw.Draw(img)

    # 添加文字
    try:
        # 尝试使用系统字体
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except:
        # 如果找不到字体，使用默认字体
        font = ImageFont.load_default()

    # 计算文字位置（居中）
    bbox = draw.textbbox((0, 0), text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]
    x = (width - text_width) // 2
    y = (height - text_height) // 2

    # 绘制文字
    draw.text((x, y), text, fill=(255, 255, 255), font=font)

    # 保存图片
    img.save(output_path, 'JPEG', quality=90)
    print(f"创建图片: {output_path}")

def create_gallery_images(base_path):
    """创建图集测试图片"""
    gallery_base = os.path.join(base_path, 'gallery')

    # 创建演唱会图集
    concert_path = os.path.join(gallery_base, 'concert')
    os.makedirs(concert_path, exist_ok=True)

    # 创建封面
    create_test_image(800, 600, COLORS['concert'], '演唱会现场', os.path.join(concert_path, 'cover.jpg'))

    # 创建 5 张图片
    for i in range(1, 6):
        create_test_image(800, 600, COLORS['concert'], f'演唱会 #{i}', os.path.join(concert_path, f'{i:03d}.jpg'))

    # 创建日常图集
    daily_path = os.path.join(gallery_base, 'daily')
    os.makedirs(daily_path, exist_ok=True)

    # 创建封面
    create_test_image(800, 600, COLORS['daily'], '森林日常', os.path.join(daily_path, 'cover.jpg'))

    # 创建 3 张图片
    for i in range(1, 4):
        create_test_image(800, 600, COLORS['daily'], f'日常 #{i}', os.path.join(daily_path, f'{i:03d}.jpg'))

    # 创建 2024 年图集
    year_path = os.path.join(gallery_base, '2024')
    os.makedirs(year_path, exist_ok=True)

    # 创建封面
    create_test_image(800, 600, COLORS['2024'], '2024年', os.path.join(year_path, 'cover.jpg'))

    # 创建 1 月图集
    month_path = os.path.join(year_path, '01')
    os.makedirs(month_path, exist_ok=True)

    # 创建封面
    create_test_image(800, 600, COLORS['concert'], '2024年1月', os.path.join(month_path, 'cover.jpg'))

    # 创建 4 张图片
    for i in range(1, 5):
        create_test_image(800, 600, COLORS['concert'], f'1月 #{i}', os.path.join(month_path, f'{i:03d}.jpg'))

if __name__ == '__main__':
    # 获取媒体目录
    media_path = os.path.join(os.path.dirname(__file__), '..', 'repo', 'xxm_fans_backend', 'media')
    create_gallery_images(media_path)
    print("\n测试图片创建完成！")
