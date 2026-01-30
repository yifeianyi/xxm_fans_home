# 图集缩略图优化方案

## 一、背景与目标

### 1.1 当前状况
- 图集目录大小：约 647MB
- 图片数量：310 个文件
- 文件类型：JPG、PNG、GIF、MP4
- 访问方式：直接加载原图

### 1.2 问题分析
1. **带宽压力大**：所有图片（包括 GIF）都直接加载原图
2. **首屏加载慢**：用户需要等待所有图片加载完成
3. **移动端体验差**：小屏设备加载大图浪费流量
4. **CDN 成本高**：原图传输消耗大量带宽

### 1.3 优化目标
1. **列表页展示缩略图**：减少带宽消耗，提升加载速度
2. **点击后显示原图**：保证图片质量
3. **支持 GIF 缩略图**：GIF 文件也生成缩略图
4. **保持向后兼容**：现有功能不受影响

---

## 二、技术方案

### 2.1 整体架构

采用 **Django 视图代理 + Pillow 图像处理** 方案：

```
用户请求图片
    ↓
Django 视图 (检查缩略图)
    ↓
缩略图存在? → 返回缩略图
    ↓ 否
生成缩略图 → 保存 → 返回缩略图
```

### 2.2 缩略图规范

#### 2.2.1 缩略图尺寸
- **列表展示**：宽 300px，高度自适应（保持宽高比）
- **最大尺寸**：限制最长边为 400px
- **质量设置**：JPEG 质量 85，WebP 质量 80

#### 2.2.2 缩略图存储
- **存储位置**：`media/gallery/thumbnails/`
- **命名规则**：`{hash}_{width}x{height}.{ext}`
  - hash：原文件路径的 MD5 哈希
  - 示例：`abc123_300x200.webp`

#### 2.2.3 支持格式
- **输入**：JPG、PNG、GIF、WEBP
- **输出**：统一使用 WEBP 格式（更小体积，更好的压缩率）
- **GIF 处理**：提取第一帧作为缩略图

### 2.3 缓存策略

1. **HTTP 缓存**：设置 `Cache-Control: max-age=31536000`（1 年）
2. **文件级缓存**：缩略图生成后永久存储，不删除
3. **浏览器缓存**：通过 URL 哈希避免缓存冲突

---

## 三、实现步骤

### 3.1 后端实现

#### 3.1.1 创建缩略图工具模块

**文件路径**：`repo/xxm_fans_backend/gallery/utils.py`

```python
import os
import hashlib
from pathlib import Path
from PIL import Image
from django.core.files.storage import default_storage
from django.conf import settings

class ThumbnailGenerator:
    """缩略图生成器"""

    THUMBNAIL_DIR = 'gallery/thumbnails/'
    THUMBNAIL_SIZE = (400, 400)  # 最大宽高
    QUALITY = 85

    @classmethod
    def get_thumbnail_path(cls, original_path: str) -> str:
        """获取缩略图存储路径"""
        # 生成原路径的哈希值
        path_hash = hashlib.md5(original_path.encode()).hexdigest()
        # 解析原文件扩展名
        ext = Path(original_path).suffix.lower()

        # 统一使用 webp 格式（除了 GIF）
        if ext == '.gif':
            output_ext = '.gif'
        else:
            output_ext = '.webp'

        thumbnail_name = f"{path_hash}_thumb{output_ext}"
        return os.path.join(cls.THUMBNAIL_DIR, thumbnail_name)

    @classmethod
    def generate_thumbnail(cls, original_path: str) -> str:
        """生成缩略图"""
        original_path = original_path.lstrip('/')
        thumbnail_path = cls.get_thumbnail_path(original_path)

        # 检查缩略图是否已存在
        if default_storage.exists(thumbnail_path):
            return thumbnail_path

        # 读取原图片
        try:
            with default_storage.open(original_path, 'rb') as f:
                img = Image.open(f)

                # 处理 GIF：只取第一帧
                if getattr(img, 'is_animated', False):
                    img.seek(0)
                    img = img.convert('RGB')

                # 计算缩略图尺寸（保持宽高比）
                img.thumbnail(cls.THUMBNAIL_SIZE, Image.Resampling.LANCZOS)

                # 创建缩略图目录
                thumb_dir = os.path.dirname(thumbnail_path)
                if not default_storage.exists(thumb_dir):
                    default_storage.makedirs(thumb_dir)

                # 保存缩略图
                output_ext = Path(thumbnail_path).suffix.lower()
                save_kwargs = {}

                if output_ext in ['.jpg', '.jpeg']:
                    img.save(thumbnail_path, 'JPEG', quality=cls.QUALITY, optimize=True)
                elif output_ext == '.png':
                    img.save(thumbnail_path, 'PNG', optimize=True)
                elif output_ext == '.webp':
                    img.save(thumbnail_path, 'WEBP', quality=cls.QUALITY, method=6)
                elif output_ext == '.gif':
                    img.save(thumbnail_path, 'GIF')

                return thumbnail_path

        except Exception as e:
            print(f"生成缩略图失败: {original_path}, 错误: {e}")
            return original_path  # 失败时返回原图路径

    @classmethod
    def get_thumbnail_url(cls, original_url: str) -> str:
        """获取缩略图 URL"""
        if not original_url:
            return original_url

        original_path = original_url.lstrip('/')
        thumbnail_path = cls.generate_thumbnail(original_path)

        if thumbnail_path == original_path:
            return original_url

        # 转换为 URL
        if thumbnail_path.startswith(cls.THUMBNAIL_DIR):
            return f"/media/{thumbnail_path}"

        return original_url
```

#### 3.1.2 添加缩略图 API 视图

**文件路径**：`repo/xxm_fans_backend/gallery/views.py`

```python
from django.http import HttpResponse, FileResponse
from django.views.decorators.http import require_GET
from django.views.decorators.cache import cache_page
from django.core.files.storage import default_storage
from .utils import ThumbnailGenerator

@api_view(['GET'])
def get_thumbnail(request):
    """获取图片缩略图"""
    image_path = request.GET.get('path')

    if not image_path:
        return HttpResponse('Missing path parameter', status=400)

    # 生成缩略图
    thumbnail_path = ThumbnailGenerator.generate_thumbnail(image_path)

    # 返回缩略图
    try:
        if default_storage.exists(thumbnail_path):
            file = default_storage.open(thumbnail_path, 'rb')
            response = FileResponse(file)
            response['Cache-Control'] = 'public, max-age=31536000'
            response['Content-Type'] = 'image/webp'
            return response
        else:
            # 降级到原图
            if default_storage.exists(image_path):
                file = default_storage.open(image_path, 'rb')
                response = FileResponse(file)
                response['Cache-Control'] = 'public, max-age=86400'
                return response
            else:
                return HttpResponse('Image not found', status=404)
    except Exception as e:
        return HttpResponse(f'Error: {str(e)}', status=500)
```

#### 3.1.3 更新 URL 配置

**文件路径**：`repo/xxm_fans_backend/gallery/urls.py`

```python
from django.urls import path
from .views import (
    gallery_tree, gallery_detail, gallery_images,
    gallery_children_images, get_thumbnail
)
from .admin import get_gallery_images

app_name = 'gallery'

urlpatterns = [
    # API 路由
    path('tree/', gallery_tree, name='tree'),
    path('<str:gallery_id>/', gallery_detail, name='detail'),
    path('<str:gallery_id>/images/', gallery_images, name='images'),
    path('<str:gallery_id>/children-images/', gallery_children_images, name='children_images'),
    path('thumbnail/', get_thumbnail, name='thumbnail'),  # 新增缩略图接口
    # Admin 路由
    path('admin/<str:gallery_id>/images/', get_gallery_images, name='gallery_images_admin'),
]
```

#### 3.1.4 更新图集模型（添加缩略图 URL）

**文件路径**：`repo/xxm_fans_backend/gallery/models.py`

```python
from .utils import ThumbnailGenerator

class Gallery(models.Model):
    # ... 现有代码 ...

    def get_images(self):
        """获取图集下的所有图片"""
        folder_path = self.folder_path.lstrip('/')

        if not folder_path or not default_storage.exists(folder_path):
            return []

        try:
            files = default_storage.listdir(folder_path)[1] if hasattr(default_storage, 'listdir') else []
            image_files = sorted([
                f for f in files
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif', '.mp4'))
                and f != 'cover.jpg'
            ])

            return [{
                'filename': f,
                'url': f"{self.folder_path}{f}",
                'thumbnail_url': f"/api/gallery/thumbnail/?path={self.folder_path}{f}",
                'title': f"{self.title} - {idx + 1}"
            } for idx, f in enumerate(image_files)]
        except Exception:
            return []
```

#### 3.1.5 更新 API 响应

**文件路径**：`repo/xxm_fans_backend/gallery/views.py`

```python
@api_view(['GET'])
def gallery_images(request, gallery_id):
    """获取图集图片列表"""
    try:
        gallery = Gallery.objects.get(id=gallery_id, is_active=True)
        images = gallery.get_images()

        # 构建图片列表
        image_list = []
        for img in images:
            image_list.append({
                'url': img['url'],
                'thumbnail_url': img.get('thumbnail_url', img['url']),  # 使用缩略图 URL
                'title': img['title'],
                'filename': img['filename'],
            })

        return success_response({
            'images': image_list,
            'total': len(image_list)
        }, '获取图片列表成功')
    except Gallery.DoesNotExist:
        return error_response('图集不存在', status_code=404)
    except Exception as e:
        return error_response(str(e))
```

### 3.2 前端实现

#### 3.2.1 更新类型定义

**文件路径**：`repo/xxm_fans_frontend/domain/types.ts`

```typescript
export interface GalleryImage {
  id: string;
  url: string;
  thumbnailUrl?: string;  // 新增缩略图 URL
  title: string;
  filename: string;
  isGif?: boolean;
  isVideo?: boolean;
}
```

#### 3.2.2 更新图片组件

**文件路径**：`repo/xxm_fans_frontend/presentation/pages/GalleryPage.tsx`

修改图片加载逻辑，优先使用缩略图：

```typescript
// 图片网格组件
<img
  src={img.thumbnailUrl || img.url}  // 优先使用缩略图
  alt={img.title}
  onClick={() => handleImageClick(img, index, currentImages)}
  loading="lazy"  // 懒加载
  className="w-full h-full object-cover"
/>

// 点击时加载原图
const handleImageClick = (img: GalleryImage, index: number, allImages?: GalleryImage[]) => {
  // 使用原图 URL
  const fullSizeImage = { ...img, url: img.url };  // 确保使用原图
  setLightboxImage(fullSizeImage);
  setCurrentImageIndex(index);
  setCurrentImages(allImages || images);
};
```

#### 3.2.3 添加占位符优化

添加图片加载占位符和错误处理：

```typescript
const [imageLoading, setImageLoading] = useState<{ [key: string]: boolean }>({});
const [imageError, setImageError] = useState<{ [key: string]: boolean }>({});

<img
  src={img.thumbnailUrl || img.url}
  alt={img.title}
  loading="lazy"
  className="w-full h-full object-cover"
  onLoad={() => setImageLoading(prev => ({ ...prev, [img.id]: false }))}
  onError={() => {
    setImageError(prev => ({ ...prev, [img.id]: true }));
    setImageLoading(prev => ({ ...prev, [img.id]: false }));
  }}
/>
```

### 3.3 批量生成缩略图脚本

创建管理命令批量生成现有图片的缩略图：

**文件路径**：`repo/xxm_fans_backend/gallery/management/commands/generate_thumbnails.py`

```python
from django.core.management.base import BaseCommand
from gallery.utils import ThumbnailGenerator
from django.core.files.storage import default_storage

class Command(BaseCommand):
    help = '批量生成图集缩略图'

    def handle(self, *args, **options):
        self.stdout.write('开始生成缩略图...')

        # 扫描 gallery 目录
        gallery_dir = 'gallery'
        if not default_storage.exists(gallery_dir):
            self.stdout.write(self.style.ERROR('gallery 目录不存在'))
            return

        # 递归扫描所有图片
        total_count = 0
        success_count = 0

        def scan_directory(directory):
            nonlocal total_count, success_count

            try:
                dirs, files = default_storage.listdir(directory)
                for file in files:
                    if file.lower().endswith(('.jpg', '.jpeg', '.png', '.webp', '.gif')):
                        total_count += 1
                        file_path = f"{directory}/{file}"

                        try:
                            thumbnail_path = ThumbnailGenerator.generate_thumbnail(file_path)
                            if thumbnail_path != file_path:
                                success_count += 1
                                self.stdout.write(f'✓ {file_path} -> {thumbnail_path}')
                            else:
                                self.stdout.write(f'- {file_path} (跳过)')
                        except Exception as e:
                            self.stdout.write(self.style.ERROR(f'✗ {file_path}: {e}'))

                for subdir in dirs:
                    scan_directory(f"{directory}/{subdir}")
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'扫描目录失败 {directory}: {e}'))

        scan_directory(gallery_dir)

        self.stdout.write(
            self.style.SUCCESS(
                f'完成！总共处理 {total_count} 个文件，成功生成 {success_count} 个缩略图'
            )
        )
```

使用方法：
```bash
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend
python manage.py generate_thumbnails
```

---

## 四、优化效果预期

### 4.1 带宽优化
- **原图平均大小**：约 2MB/张
- **缩略图平均大小**：约 50KB/张（减少 97.5%）
- **总带宽节省**：约 602MB（310 张图片）

### 4.2 性能提升
- **首屏加载时间**：从 5-10 秒降至 1-2 秒
- **图片加载速度**：提升 10-20 倍
- **用户体验**：即时响应，无等待感

### 4.3 成本节约
- **CDN 流量成本**：降低 95% 以上
- **服务器带宽**：大幅减少带宽占用

---

## 五、实施计划

### 5.1 阶段一：后端开发（1-2 天）
1. 创建 `ThumbnailGenerator` 工具类
2. 实现缩略图 API 视图
3. 更新 URL 配置
4. 修改图集模型返回缩略图 URL
5. 测试缩略图生成功能

### 5.2 阶段二：前端适配（0.5 天）
1. 更新类型定义
2. 修改图片加载逻辑
3. 添加占位符和错误处理
4. 测试前端展示效果

### 5.3 阶段三：批量生成（0.5 天）
1. 创建批量生成脚本
2. 执行批量生成命令
3. 验证缩略图生成结果

### 5.4 阶段四：测试与优化（1 天）
1. 功能测试
2. 性能测试
3. 移动端测试
4. 边界情况处理

---

## 六、注意事项

### 6.1 存储空间
- 缩略图将占用额外存储空间（约 15-20MB）
- 建议定期检查存储空间使用情况

### 6.2 生成性能
- 首次访问时需要实时生成，可能会有 100-500ms 延迟
- 建议在低峰期执行批量生成命令

### 6.3 GIF 处理
- GIF 缩略图只显示第一帧
- 如果需要展示动态效果，点击后加载原图

### 6.4 缓存清理
- 缩略图永久存储，无需定期清理
- 如需更新缩略图，删除对应缩略图文件即可重新生成

### 6.5 兼容性
- 向后兼容：如果缩略图生成失败，自动降级到原图
- 前端兼容：如果 `thumbnailUrl` 不存在，使用 `url`

---

## 七、扩展优化（可选）

### 7.1 多尺寸缩略图
```python
# 支持多种尺寸
THUMBNAIL_SIZES = {
    'small': (200, 200),
    'medium': (400, 400),
    'large': (800, 800),
}
```

### 7.2 WebP 自动降级
检测浏览器支持情况，不支持时返回 JPEG：
```python
def get_thumbnail_url(cls, original_url: str, format: str = 'webp') -> str:
    # 根据请求头 Accept 判断支持的格式
    # 生成对应格式的缩略图
```

### 7.3 CDN 集成
将缩略图存储到 CDN：
```python
# 使用 CDN 存储后端
CDN_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
```

---

## 八、风险评估

| 风险 | 影响 | 概率 | 应对措施 |
|------|------|------|----------|
| 缩略图生成失败 | 功能降级到原图 | 低 | 异常捕获 + 降级方案 |
| 存储空间不足 | 无法生成新缩略图 | 低 | 定期监控 + 清理策略 |
| 性能影响（首次生成） | 用户等待时间增加 | 中 | 批量预生成 + 异步处理 |
| GIF 动画丢失 | 缩略图不显示动画 | 低 | 文档说明 + 点击查看原图 |

---

## 九、总结

本方案通过 **Django 视图代理 + Pillow 图像处理** 实现图集缩略图功能，具有以下优势：

1. **实施简单**：无需第三方服务，基于 Django 生态
2. **性能优秀**：带宽节省 95% 以上，加载速度提升 10-20 倍
3. **向后兼容**：无缝集成现有系统，不影响现有功能
4. **易于维护**：代码结构清晰，扩展性强
5. **成本可控**：减少 CDN 流量成本，优化服务器资源

建议按照实施计划逐步推进，确保系统稳定性和用户体验。