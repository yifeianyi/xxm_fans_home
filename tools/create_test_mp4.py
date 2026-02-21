#!/usr/bin/env python3
"""
创建测试 MP4 短视频（10秒以内）
"""
import os
import subprocess

def create_test_mp4(output_path, duration=5, width=400, height=400):
    """使用 FFmpeg 创建测试 MP4 视频"""
    try:
        # 使用 FFmpeg 创建简单的测试视频
        # 生成颜色渐变的视频
        cmd = [
            'ffmpeg',
            '-f', 'lavfi',
            '-i', f'color=c=red:r=25:size={width}x{height}:d={duration}',
            '-vf', 'format=yuv420p',
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-crf', '23',
            '-t', str(duration),
            '-pix_fmt', 'yuv420p',
            '-y',  # 覆盖输出文件
            output_path
        ]

        result = subprocess.run(cmd, capture_output=True, text=True)

        if result.returncode == 0:
            print(f"创建 MP4 视频: {output_path}")
            print(f"时长: {duration}秒, 分辨率: {width}x{height}")
            return True
        else:
            print(f"创建视频失败: {result.stderr}")
            return False

    except FileNotFoundError:
        print("错误: 未找到 FFmpeg，请先安装 FFmpeg")
        return False
    except Exception as e:
        print(f"创建视频时出错: {e}")
        return False

if __name__ == '__main__':
    # 获取媒体目录
    media_path = os.path.join(os.path.dirname(__file__), '..', 'repo', 'xxm_fans_backend', 'media')

    # 创建短视频图集目录
    video_path = os.path.join(media_path, 'gallery', 'short_video')
    os.makedirs(video_path, exist_ok=True)

    # 创建测试 MP4 视频
    create_test_mp4(os.path.join(video_path, '001.mp4'), duration=5)
    create_test_mp4(os.path.join(video_path, '002.mp4'), duration=3)

    # 创建封面
    from create_test_gallery_images import create_test_image
    create_test_image(800, 600, (142, 182, 155), '短视频合集', os.path.join(video_path, 'cover.jpg'))

    print("\n测试 MP4 视频创建完成！")
    print("请运行以下命令同步图集数据:")
    print("  cd repo/xxm_fans_backend")
    print("  python3 manage.py sync_gallery_from_folder")