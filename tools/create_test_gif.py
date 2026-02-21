#!/usr/bin/env python3
"""
创建测试 GIF 动图
"""
import os
from PIL import Image, ImageDraw, ImageFont

def create_test_gif(output_path, num_frames=10, duration=500):
    """创建测试 GIF 动图"""
    frames = []

    # 颜色配置
    colors = [
        (248, 177, 149),  # 蜜桃粉
        (142, 182, 155),  # 豆沙绿
        (74, 55, 40),     # 大地棕
    ]

    for i in range(num_frames):
        # 创建图片
        img = Image.new('RGB', (400, 400), colors[i % len(colors)])
        draw = ImageDraw.Draw(img)

        # 添加文字
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
        except:
            font = ImageFont.load_default()

        # 计算文字位置（居中）
        text = f"GIF {i + 1}"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (400 - text_width) // 2
        y = (400 - text_height) // 2

        # 绘制文字
        draw.text((x, y), text, fill=(255, 255, 255), font=font)

        # 添加到帧列表
        frames.append(img)

    # 保存为 GIF
    frames[0].save(
        output_path,
        save_all=True,
        append_images=frames[1:],
        duration=duration,
        loop=0
    )

    print(f"创建 GIF 动图: {output_path}")
    print(f"帧数: {num_frames}, 每帧时长: {duration}ms")

if __name__ == '__main__':
    # 获取媒体目录
    media_path = os.path.join(os.path.dirname(__file__), '..', 'repo', 'xxm_fans_backend', 'media')

    # 创建表情包图集目录
    emoji_path = os.path.join(media_path, 'gallery', 'emoji')
    os.makedirs(emoji_path, exist_ok=True)

    # 创建测试 GIF
    create_test_gif(os.path.join(emoji_path, '001.gif'), num_frames=10, duration=500)
    create_test_gif(os.path.join(emoji_path, '002.gif'), num_frames=8, duration=300)

    # 创建封面
    from create_test_gallery_images import create_test_image
    create_test_image(800, 600, (248, 177, 149), '表情包合集', os.path.join(emoji_path, 'cover.jpg'))

    print("\n测试 GIF 动图创建完成！")
    print("请运行以下命令同步图集数据:")
    print("  cd repo/xxm_fans_backend")
    print("  python3 manage.py sync_gallery_from_folder")