import sys
from PIL import Image, ImageDraw, ImageFont
import json

def img_to_dot_matrix(img_path, threshold=128, max_size=32):
    img = Image.open(img_path).convert('L')
    w, h = img.size
    scale = min(max_size/w, max_size/h, 1)
    img = img.resize((int(w*scale), int(h*scale)), Image.NEAREST)
    arr = img.load()
    dots = []
    for y in range(img.height):
        for x in range(img.width):
            if arr[x, y] < threshold:
                dots.append([x, y])
    return dots

def text_to_dot_matrix(text, font_path=None, font_size=32, threshold=128):
    font = ImageFont.truetype(font_path or '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf', font_size)
    w, h = font.getsize(text)
    img = Image.new('L', (w, h), 255)
    draw = ImageDraw.Draw(img)
    draw.text((0, 0), text, font=font, fill=0)
    arr = img.load()
    dots = []
    for y in range(img.height):
        for x in range(img.width):
            if arr[x, y] < threshold:
                dots.append([x, y])
    return dots

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='图片/文字转点阵JSON')
    parser.add_argument('--img', help='图片路径')
    parser.add_argument('--text', help='要转为点阵的文字')
    parser.add_argument('--font', help='字体路径')
    parser.add_argument('--size', type=int, default=32, help='最大尺寸/字体大小')
    parser.add_argument('--out', help='输出json文件名', default='dot_matrix.json')
    args = parser.parse_args()
    if args.img:
        dots = img_to_dot_matrix(args.img, max_size=args.size)
    elif args.text:
        dots = text_to_dot_matrix(args.text, font_path=args.font, font_size=args.size)
    else:
        print('请指定 --img 或 --text')
        sys.exit(1)
    with open(args.out, 'w') as f:
        json.dump(dots, f)
    print(f'点阵已保存到 {args.out}，共 {len(dots)} 个点') 