# 图集功能实现方案

## 1. 概述

本方案实现一个支持动态多级分类的图集管理系统，采用**数据库存储元数据 + 静态资源存储图片**的混合架构。

### 核心特性

- ✅ 支持任意层级的图集结构（单层、双层、多层）
- ✅ 图片完全走静态资源，性能优秀
- ✅ 通过 Admin 后台动态管理图集
- ✅ 自动扫描文件夹生成图集树
- ✅ 面包屑导航，清晰的层级关系

---

## 2. 架构设计

### 2.1 数据模型

```python
# gallery/models.py
from django.db import models

class Gallery(models.Model):
    """图集模型 - 支持多级分类"""
    
    id = models.CharField(
        primary_key=True,
        max_length=50,
        verbose_name='图集ID'
    )
    title = models.CharField(
        max_length=200,
        verbose_name='标题'
    )
    description = models.TextField(
        blank=True,
        verbose_name='描述'
    )
    cover_url = models.CharField(
        max_length=500,
        verbose_name='封面图片URL'
    )
    
    # 层级关系
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='children',
        verbose_name='父图集'
    )
    level = models.IntegerField(
        default=0,
        verbose_name='层级'
    )
    
    # 图片信息
    image_count = models.IntegerField(
        default=0,
        verbose_name='图片数量'
    )
    folder_path = models.CharField(
        max_length=500,
        verbose_name='文件夹路径'
    )
    
    # 元数据
    tags = models.JSONField(
        default=list,
        verbose_name='标签'
    )
    sort_order = models.IntegerField(
        default=0,
        verbose_name='排序'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='是否启用'
    )
    
    # 时间戳
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='创建时间'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='更新时间'
    )
    
    class Meta:
        db_table = 'gallery'
        verbose_name = '图集'
        verbose_name_plural = '图集'
        ordering = ['sort_order', 'id']
    
    def __str__(self):
        return self.title
    
    def is_leaf(self):
        """判断是否为叶子节点（无子图集）"""
        return not self.children.exists()
    
    def get_breadcrumbs(self):
        """获取面包屑路径"""
        breadcrumbs = []
        current = self
        while current:
            breadcrumbs.insert(0, {
                'id': current.id,
                'title': current.title
            })
            current = current.parent
        return breadcrumbs
```

### 2.2 目录结构

```
media/gallery/
├── 2024/                          # 根图集（年份）
│   ├── cover.jpg
│   ├── 01/                       # 子图集（1月）
│   │   ├── cover.jpg
│   │   ├── 001.jpg
│   │   ├── 002.jpg
│   │   └── ...
│   ├── 02/                       # 子图集（2月）
│   │   ├── cover.jpg
│   │   └── ...
│   └── 03/                       # 子图集（3月）
│       ├── cover.jpg
│       └── ...
├── concert/                       # 根图集（演唱会，单层）
│   ├── cover.jpg
│   ├── 001.jpg
│   ├── 002.jpg
│   └── ...
├── daily/                         # 根图集（日常，单层）
│   ├── cover.jpg
│   └── ...
└── behind-scenes/                 # 根图集（幕后，单层）
    ├── cover.jpg
    └── ...
```

---

## 3. Admin 后台管理

### 3.1 Admin 配置

```python
# gallery/admin.py
from django.contrib import admin
from django.urls import path, reverse
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.core.files.storage import default_storage
from django.conf import settings
import os
from .models import Gallery

@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    """图集管理后台"""
    
    list_display = [
        'id', 'title', 'parent', 'level', 
        'image_count', 'is_active', 'created_at',
        'manage_images_link'
    ]
    list_filter = ['level', 'is_active', 'created_at']
    search_fields = ['id', 'title', 'description']
    readonly_fields = [
        'created_at', 'updated_at', 'image_count', 
        'folder_path_display', 'images_preview'
    ]
    
    fieldsets = (
        ('基本信息', {
            'fields': ('id', 'title', 'description', 'cover_url')
        }),
        ('层级关系', {
            'fields': ('parent', 'level', 'sort_order', 'is_active')
        }),
        ('文件夹信息', {
            'fields': ('folder_path_display', 'image_count')
        }),
        ('图片管理', {
            'fields': ('images_preview',),
            'classes': ('collapse',)
        }),
        ('元数据', {
            'fields': ('tags',)
        }),
        ('时间戳', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    change_form_template = 'admin/gallery/change_form.html'
    
    def get_urls(self):
        """添加自定义 URL"""
        urls = super().get_urls()
        custom_urls = [
            path(
                '<path:object_id>/upload-image/', 
                self.admin_site.admin_view(self.upload_image_view), 
                name='gallery_upload_image'
            ),
            path(
                '<path:object_id>/delete-image/<str:filename>/', 
                self.admin_site.admin_view(self.delete_image_view), 
                name='gallery_delete_image'
            ),
            path(
                '<path:object_id>/update-cover/', 
                self.admin_site.admin_view(self.update_cover_view), 
                name='gallery_update_cover'
            ),
            path(
                '<path:object_id>/refresh-count/', 
                self.admin_site.admin_view(self.refresh_count_view), 
                name='gallery_refresh_count'
            ),
        ]
        return custom_urls + urls
    
    def folder_path_display(self, obj):
        """显示文件夹路径"""
        return obj.folder_path or '未设置'
    folder_path_display.short_description = '文件夹路径'
    
    def images_preview(self, obj):
        """显示图片预览"""
        images = obj.get_images()
        
        if not images:
            return '<p style="color: #999;">暂无图片</p>'
        
        html = '<div style="display: flex; flex-wrap: wrap; gap: 10px; max-height: 400px; overflow-y: auto;">'
        
        # 最多显示 12 张
        for img in images[:12]:
            html += f'''
                <div style="position: relative; width: 100px; height: 100px;">
                    <img src="{img['url']}" style="width: 100%; height: 100%; object-fit: cover; border-radius: 8px;">
                    <span style="position: absolute; bottom: 2px; right: 2px; background: rgba(0,0,0,0.7); color: white; font-size: 10px; padding: 2px 4px; border-radius: 4px;">{img['filename']}</span>
                </div>
            '''
        
        if len(images) > 12:
            html += f'<p style="color: #999; font-size: 12px;">还有 {len(images) - 12} 张图片...</p>'
        
        html += '</div>'
        return html
    images_preview.short_description = '图片预览'
    images_preview.allow_tags = True
    
    def manage_images_link(self, obj):
        """图片管理链接"""
        url = reverse('admin:gallery_gallery_change', args=[obj.id])
        return f'<a href="{url}#images-section">管理图片</a>'
    manage_images_link.short_description = '图片管理'
    manage_images_link.allow_tags = True
    
    def upload_image_view(self, request, object_id):
        """上传图片视图"""
        gallery = get_object_or_404(Gallery, id=object_id)
        
        if request.method == 'POST':
            image_file = request.FILES.get('image')
            
            if not image_file:
                return JsonResponse({'success': False, 'message': '未选择图片'})
            
            # 验证文件类型
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
            if image_file.content_type not in allowed_types:
                return JsonResponse({'success': False, 'message': '仅支持 JPG、PNG、WEBP 格式'})
            
            # 添加图片
            filename = gallery.add_image(image_file)
            
            return JsonResponse({
                'success': True,
                'filename': filename,
                'url': f"{gallery.folder_path}{filename}",
                'image_count': gallery.image_count
            })
        
        return render(request, 'admin/gallery/upload_image.html', {'gallery': gallery})
    
    def delete_image_view(self, request, object_id, filename):
        """删除图片视图"""
        gallery = get_object_or_404(Gallery, id=object_id)
        
        if request.method == 'POST':
            # 安全检查：防止删除 cover.jpg
            if filename == 'cover.jpg':
                return JsonResponse({'success': False, 'message': '不能删除封面图片'})
            
            success = gallery.delete_image(filename)
            
            if success:
                return JsonResponse({
                    'success': True,
                    'filename': filename,
                    'image_count': gallery.image_count
                })
            else:
                return JsonResponse({'success': False, 'message': '文件不存在'})
        
        return JsonResponse({'success': False, 'message': '仅支持 POST 请求'})
    
    def update_cover_view(self, request, object_id):
        """更新封面视图"""
        gallery = get_object_or_404(Gallery, id=object_id)
        
        if request.method == 'POST':
            cover_file = request.FILES.get('cover')
            
            if not cover_file:
                return JsonResponse({'success': False, 'message': '未选择封面'})
            
            # 验证文件类型
            allowed_types = ['image/jpeg', 'image/jpg', 'image/png', 'image/webp']
            if cover_file.content_type not in allowed_types:
                return JsonResponse({'success': False, 'message': '仅支持 JPG、PNG、WEBP 格式'})
            
            gallery.update_cover(cover_file)
            
            return JsonResponse({
                'success': True,
                'cover_url': gallery.cover_url
            })
        
        return JsonResponse({'success': False, 'message': '仅支持 POST 请求'})
    
    def refresh_count_view(self, request, object_id):
        """刷新图片数量视图"""
        gallery = get_object_or_404(Gallery, id=object_id)
        
        if request.method == 'POST':
            gallery.refresh_image_count()
            
            return JsonResponse({
                'success': True,
                'image_count': gallery.image_count
            })
        
        return JsonResponse({'success': False, 'message': '仅支持 POST 请求'})
```

### 3.2 模型方法扩展

```python
# gallery/models.py (添加方法)
class Gallery(models.Model):
    # ... 原有字段 ...
    
    def get_images(self):
        """获取图集下的所有图片"""
        folder_path = self.folder_path.lstrip('/')
        
        if not folder_path or not default_storage.exists(folder_path):
            return []
        
        try:
            files = default_storage.listdir(folder_path)[1] if hasattr(default_storage, 'listdir') else []
            image_files = sorted([
                f for f in files 
                if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')) 
                and f != 'cover.jpg'
            ])
            
            return [{
                'filename': f,
                'url': f"{self.folder_path}{f}",
                'title': f"{self.title} - {idx + 1}"
            } for idx, f in enumerate(image_files)]
        except Exception:
            return []
    
    def add_image(self, image_file, filename=None):
        """添加图片到图集"""
        if not filename:
            # 自动生成文件名
            existing_images = self.get_images()
            next_num = len(existing_images) + 1
            ext = os.path.splitext(image_file.name)[1].lower()
            filename = f"{str(next_num).zfill(3)}{ext}"
        
        folder_path = self.folder_path.lstrip('/')
        
        # 确保文件夹存在
        if not default_storage.exists(folder_path):
            default_storage.makedirs(folder_path)
        
        # 保存图片
        save_path = os.path.join(folder_path, filename)
        default_storage.save(save_path, image_file)
        
        # 更新图片数量
        self.refresh_image_count()
        
        return filename
    
    def delete_image(self, filename):
        """删除图集中的图片"""
        folder_path = self.folder_path.lstrip('/')
        file_path = os.path.join(folder_path, filename)
        
        if default_storage.exists(file_path):
            default_storage.delete(file_path)
            self.refresh_image_count()
            return True
        
        return False
    
    def update_cover(self, cover_file):
        """更新封面图片"""
        folder_path = self.folder_path.lstrip('/')
        
        # 确保文件夹存在
        if not default_storage.exists(folder_path):
            default_storage.makedirs(folder_path)
        
        # 保存封面
        cover_path = os.path.join(folder_path, 'cover.jpg')
        default_storage.save(cover_path, cover_file)
        
        # 更新封面 URL
        self.cover_url = f"{self.folder_path}cover.jpg"
        self.save()
    
    def refresh_image_count(self):
        """刷新图片数量"""
        images = self.get_images()
        self.image_count = len(images)
        self.save()
```

### 3.3 Admin 模板

**上传图片模板** - `templates/admin/gallery/upload_image.html`:
```html
{% extends "admin/base_site.html" %}

{% block content %}
<div class="module" style="max-width: 800px; margin: 0 auto;">
    <h2>上传图片到 {{ gallery.title }}</h2>
    
    <div class="form-row">
        <div>
            <label>图集路径：</label>
            <code>{{ gallery.folder_path }}</code>
        </div>
        <div>
            <label>当前图片数量：</label>
            <strong>{{ gallery.image_count }}</strong>
        </div>
    </div>
    
    <form method="post" enctype="multipart/form-data" id="upload-form" style="margin-top: 20px;">
        {% csrf_token %}
        
        <div class="form-row">
            <div>
                <label for="image-input" style="display: block; margin-bottom: 5px; font-weight: bold;">
                    选择图片：
                </label>
                <input 
                    type="file" 
                    name="image" 
                    accept="image/jpeg,image/jpg,image/png,image/webp" 
                    id="image-input"
                    style="width: 100%; padding: 8px; border: 1px solid #ddd; border-radius: 4px;"
                >
                <p style="font-size: 12px; color: #666; margin-top: 5px;">
                    支持 JPG、PNG、WEBP 格式，建议大小不超过 5MB
                </p>
            </div>
        </div>
        
        <div style="margin-top: 20px;">
            <button 
                type="submit" 
                class="button"
                style="padding: 10px 20px; background: #417690; color: white; border: none; border-radius: 4px; cursor: pointer;"
            >
                上传图片
            </button>
            <a 
                href="{% url 'admin:gallery_gallery_change' gallery.id %}"
                style="margin-left: 10px; color: #666; text-decoration: none;"
            >
                返回
            </a>
        </div>
    </form>
    
    <div id="upload-progress" style="display: none; margin-top: 30px; padding: 20px; background: #f5f5f5; border-radius: 4px;">
        <p style="margin-bottom: 10px; font-weight: bold;">上传中...</p>
        <progress id="progress-bar" value="0" max="100" style="width: 100%;"></progress>
        <p id="progress-text" style="margin-top: 10px; font-size: 14px; color: #666;">0%</p>
    </div>
    
    <div id="upload-result" style="margin-top: 20px;"></div>
</div>

<script>
document.getElementById('upload-form').addEventListener('submit', function(e) {
    e.preventDefault();
    
    const formData = new FormData();
    const fileInput = document.getElementById('image-input');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('请选择图片');
        return;
    }
    
    // 文件大小检查（5MB）
    if (file.size > 5 * 1024 * 1024) {
        alert('图片大小不能超过 5MB');
        return;
    }
    
    formData.append('image', file);
    
    const xhr = new XMLHttpRequest();
    xhr.open('POST', '', true);
    
    // 上传进度
    xhr.upload.onprogress = function(e) {
        if (e.lengthComputable) {
            const percent = Math.round((e.loaded / e.total) * 100);
            document.getElementById('progress-bar').value = percent;
            document.getElementById('progress-text').textContent = percent + '%';
        }
    };
    
    xhr.onload = function() {
        document.getElementById('upload-progress').style.display = 'none';
        
        if (xhr.status === 200) {
            const response = JSON.parse(xhr.responseText);
            if (response.success) {
                document.getElementById('upload-result').innerHTML = 
                    '<div style="padding: 15px; background: #d4edda; border: 1px solid #c3e6cb; border-radius: 4px; color: #155724;">' +
                    '<strong>上传成功！</strong><br>' +
                    '文件名: ' + response.filename + '<br>' +
                    '当前图片数量: ' + response.image_count +
                    '</div>';
                
                // 2秒后返回详情页
                setTimeout(() => {
                    window.location.href = "{% url 'admin:gallery_gallery_change' gallery.id %}";
                }, 2000);
            } else {
                document.getElementById('upload-result').innerHTML = 
                    '<div style="padding: 15px; background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 4px; color: #721c24;">' +
                    '<strong>上传失败！</strong><br>' +
                    response.message +
                    '</div>';
            }
        } else {
            document.getElementById('upload-result').innerHTML = 
                '<div style="padding: 15px; background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 4px; color: #721c24;">' +
                '<strong>上传失败！</strong><br>' +
                '服务器错误，请稍后重试' +
                '</div>';
        }
    };
    
    xhr.onerror = function() {
        document.getElementById('upload-progress').style.display = 'none';
        document.getElementById('upload-result').innerHTML = 
            '<div style="padding: 15px; background: #f8d7da; border: 1px solid #f5c6cb; border-radius: 4px; color: #721c24;">' +
            '<strong>上传失败！</strong><br>' +
            '网络错误，请检查连接后重试' +
            '</div>';
    };
    
    document.getElementById('upload-progress').style.display = 'block';
    xhr.send(formData);
});
</script>
{% endblock %}
```

**图集详情页模板** - `templates/admin/gallery/change_form.html`:
```html
{% extends "admin/change_form.html" %}

{% block extrahead %}
{{ block.super }}
<style>
#images-section {
    background: #f9f9f9;
    padding: 20px;
    border-radius: 8px;
    margin-top: 20px;
}

.toolbar {
    display: flex;
    gap: 10px;
    margin-bottom: 20px;
    flex-wrap: wrap;
}

.toolbar button {
    padding: 8px 16px;
    border: 1px solid #ddd;
    background: white;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
}

.toolbar button:hover {
    background: #f0f0f0;
}

.toolbar button.primary {
    background: #417690;
    color: white;
    border-color: #417690;
}

.toolbar button.primary:hover {
    background: #3a6a80;
}

.images-grid {
    display: grid;
    grid-template-columns: repeat(auto-fill, minmax(120px, 1fr));
    gap: 15px;
    max-height: 600px;
    overflow-y: auto;
    padding: 10px;
    background: white;
    border: 1px solid #ddd;
    border-radius: 4px;
}

.image-item {
    position: relative;
    aspect-ratio: 1;
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    transition: transform 0.2s;
}

.image-item:hover {
    transform: scale(1.05);
    box-shadow: 0 4px 8px rgba(0,0,0,0.2);
}

.image-item img {
    width: 100%;
    height: 100%;
    object-fit: cover;
}

.image-info {
    position: absolute;
    bottom: 0;
    left: 0;
    right: 0;
    background: rgba(0,0,0,0.7);
    color: white;
    padding: 5px;
    font-size: 11px;
    text-align: center;
}

.delete-btn {
    position: absolute;
    top: 5px;
    right: 5px;
    width: 24px;
    height: 24px;
    background: rgba(220, 53, 69, 0.9);
    color: white;
    border: none;
    border-radius: 50%;
    cursor: pointer;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 16px;
    opacity: 0;
    transition: opacity 0.2s;
}

.image-item:hover .delete-btn {
    opacity: 1;
}

.delete-btn:hover {
    background: rgba(220, 53, 69, 1);
}

.empty-state {
    text-align: center;
    padding: 60px 20px;
    color: #999;
}

.cover-badge {
    position: absolute;
    top: 5px;
    left: 5px;
    background: rgba(255, 193, 7, 0.9);
    color: white;
    padding: 2px 6px;
    border-radius: 4px;
    font-size: 10px;
    font-weight: bold;
}
</style>
{% endblock %}

{% block after_field_sets %}
{{ block.super }}

<div id="images-section">
    <h3 style="margin-top: 0; margin-bottom: 15px;">📸 图片管理</h3>
    
    <div class="toolbar">
        <button type="button" class="primary" onclick="uploadImage()">
            ➕ 上传图片
        </button>
        <button type="button" onclick="updateCover()">
            🖼️ 更新封面
        </button>
        <button type="button" onclick="refreshCount()">
            🔄 刷新数量
        </button>
        <button type="button" onclick="refreshImages()">
            📷 刷新列表
        </button>
    </div>
    
    <div id="images-container">
        <div class="empty-state">加载中...</div>
    </div>
</div>

<script>
const galleryId = '{{ original.id }}';
const galleryFolderPath = '{{ original.folder_path }}';

// 页面加载时获取图片
document.addEventListener('DOMContentLoaded', function() {
    loadImages();
});

// 加载图片列表
function loadImages() {
    fetch(`/admin/gallery/gallery/${galleryId}/images/`)
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                renderImages(data.images);
            } else {
                document.getElementById('images-container').innerHTML = 
                    '<div class="empty-state">加载失败: ' + data.message + '</div>';
            }
        })
        .catch(error => {
            document.getElementById('images-container').innerHTML = 
                '<div class="empty-state">加载失败: ' + error.message + '</div>';
        });
}

// 渲染图片
function renderImages(images) {
    const container = document.getElementById('images-container');
    
    if (!images || images.length === 0) {
        container.innerHTML = '<div class="empty-state">暂无图片<br><small>点击"上传图片"添加</small></div>';
        return;
    }
    
    let html = '<div class="images-grid">';
    
    // 封面图片
    if (images.cover) {
        html += `
            <div class="image-item">
                <img src="${images.cover.url}" alt="封面">
                <div class="cover-badge">封面</div>
                <div class="image-info">cover.jpg</div>
            </div>
        `;
    }
    
    // 其他图片
    images.others.forEach(img => {
        html += `
            <div class="image-item">
                <img src="${img.url}" alt="${img.filename}">
                <button class="delete-btn" onclick="deleteImage('${img.filename}')" title="删除图片">×</button>
                <div class="image-info">${img.filename}</div>
            </div>
        `;
    });
    
    html += '</div>';
    container.innerHTML = html;
}

// 上传图片
function uploadImage() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/jpeg,image/jpg,image/png,image/webp';
    
    input.onchange = function() {
        if (input.files.length === 0) return;
        
        const file = input.files[0];
        
        // 文件大小检查
        if (file.size > 5 * 1024 * 1024) {
            alert('图片大小不能超过 5MB');
            return;
        }
        
        const formData = new FormData();
        formData.append('image', file);
        
        fetch(`/admin/gallery/gallery/${galleryId}/upload-image/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('上传成功！');
                loadImages();
                // 刷新页面以更新图片数量
                setTimeout(() => location.reload(), 500);
            } else {
                alert('上传失败: ' + data.message);
            }
        })
        .catch(error => {
            alert('上传失败: ' + error.message);
        });
    };
    
    input.click();
}

// 删除图片
function deleteImage(filename) {
    if (!confirm(`确定要删除图片 "${filename}" 吗？`)) {
        return;
    }
    
    fetch(`/admin/gallery/gallery/${galleryId}/delete-image/${filename}/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('删除成功！');
            loadImages();
            // 刷新页面以更新图片数量
            setTimeout(() => location.reload(), 500);
        } else {
            alert('删除失败: ' + data.message);
        }
    })
    .catch(error => {
        alert('删除失败: ' + error.message);
    });
}

// 更新封面
function updateCover() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'image/jpeg,image/jpg,image/png,image/webp';
    
    input.onchange = function() {
        if (input.files.length === 0) return;
        
        const file = input.files[0];
        
        // 文件大小检查
        if (file.size > 5 * 1024 * 1024) {
            alert('图片大小不能超过 5MB');
            return;
        }
        
        if (!confirm(`确定要将 "${file.name}" 设置为封面吗？`)) {
            return;
        }
        
        const formData = new FormData();
        formData.append('cover', file);
        
        fetch(`/admin/gallery/gallery/${galleryId}/update-cover/`, {
            method: 'POST',
            body: formData,
            headers: {
                'X-CSRFToken': getCookie('csrftoken')
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('封面更新成功！');
                loadImages();
            } else {
                alert('更新失败: ' + data.message);
            }
        })
        .catch(error => {
            alert('更新失败: ' + error.message);
        });
    };
    
    input.click();
}

// 刷新图片数量
function refreshCount() {
    fetch(`/admin/gallery/gallery/${galleryId}/refresh-count/`, {
        method: 'POST',
        headers: {
            'X-CSRFToken': getCookie('csrftoken')
        }
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            alert('图片数量已刷新: ' + data.image_count);
            setTimeout(() => location.reload(), 500);
        } else {
            alert('刷新失败');
        }
    })
    .catch(error => {
        alert('刷新失败: ' + error.message);
    });
}

// 刷新图片列表
function refreshImages() {
    loadImages();
}

// 获取 CSRF token
function getCookie(name) {
    let cookieValue = null;
    if (document.cookie && document.cookie !== '') {
        const cookies = document.cookie.split(';');
        for (let i = 0; i < cookies.length; i++) {
            const cookie = cookies[i].trim();
            if (cookie.substring(0, name.length + 1) === (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}
</script>
{% endblock %}
```

### 3.4 添加图片列表 API（仅 Admin 使用）

```python
# gallery/views.py (添加)
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from .models import Gallery

@staff_member_required
def get_gallery_images(request, gallery_id):
    """获取图集图片列表（仅 Admin 使用）"""
    try:
        gallery = Gallery.objects.get(id=gallery_id)
        images = gallery.get_images()
        
        # 分离封面和其他图片
        cover = None
        others = []
        
        for img in images:
            if img['filename'] == 'cover.jpg':
                cover = img
            else:
                others.append(img)
        
        return JsonResponse({
            'success': True,
            'images': {
                'cover': cover,
                'others': others
            },
            'total': len(images)
        })
    except Gallery.DoesNotExist:
        return JsonResponse({'success': False, 'message': '图集不存在'})
```

```python
# gallery/urls.py (添加)
from django.urls import path
from .views import get_gallery_images

urlpatterns = [
    # ... 原有 URL ...
    path('<str:gallery_id>/images/', get_gallery_images, name='gallery_images_admin'),
]
```

---

## 4. 前端实现

### 4.1 类型定义

```typescript
// domain/types.ts
export interface Gallery {
  id: string;
  title: string;
  description: string;
  cover_url: string;
  level: number;
  image_count: number;
  folder_path: string;
  tags: string[];
  children?: Gallery[];
}

export interface GalleryImage {
  url: string;
  title: string;
  date: string;
}
```

### 4.2 图集页面组件

```typescript
// presentation/pages/GalleryPage.tsx
import React, { useState, useEffect } from 'react';
import { mockApi } from '../../infrastructure/api/mockApi';
import { Gallery, GalleryImage } from '../../domain/types';
import { Camera, ArrowLeft, Maximize2, X, ChevronRight } from 'lucide-react';

const GalleryPage: React.FC = () => {
  const [galleryTree, setGalleryTree] = useState<Gallery[]>([]);
  const [currentGallery, setCurrentGallery] = useState<Gallery | null>(null);
  const [images, setImages] = useState<GalleryImage[]>([]);
  const [breadcrumbs, setBreadcrumbs] = useState<{id: string, title: string}[]>([]);
  const [loading, setLoading] = useState(false);
  const [lightboxImage, setLightboxImage] = useState<GalleryImage | null>(null);

  // 加载图集树
  useEffect(() => {
    loadGalleryTree();
  }, []);

  const loadGalleryTree = async () => {
    setLoading(true);
    const data = await mockApi.getGalleryTree();
    setGalleryTree(data);
    setLoading(false);
  };

  // 判断是否为叶子节点
  const isLeafGallery = (gallery: Gallery): boolean => {
    return !gallery.children || gallery.children.length === 0;
  };

  // 处理图集点击
  const handleGalleryClick = async (gallery: Gallery) => {
    if (isLeafGallery(gallery)) {
      // 叶子节点：加载图片
      setCurrentGallery(gallery);
      loadImages(gallery.id);
      updateBreadcrumbs(gallery);
    } else {
      // 非叶子节点：进入子图集
      setCurrentGallery(gallery);
      updateBreadcrumbs(gallery);
    }
  };

  // 加载图片
  const loadImages = async (galleryId: string) => {
    setLoading(true);
    const data = await mockApi.getGalleryImages(galleryId);
    setImages(data.images);
    setLoading(false);
  };

  // 更新面包屑
  const updateBreadcrumbs = async (gallery: Gallery) => {
    const data = await mockApi.getGalleryDetail(gallery.id);
    setBreadcrumbs(data.breadcrumbs);
  };

  // 返回上级
  const handleBreadcrumbClick = (breadcrumb: {id: string, title: string}) => {
    if (breadcrumb.id === currentGallery?.id) return;
    
    if (breadcrumb.id === 'root') {
      setCurrentGallery(null);
      setBreadcrumbs([]);
      setImages([]);
    } else {
      // 查找对应的图集
      const findGallery = (tree: Gallery[], id: string): Gallery | null => {
        for (const gallery of tree) {
          if (gallery.id === id) return gallery;
          if (gallery.children) {
            const found = findGallery(gallery.children, id);
            if (found) return found;
          }
        }
        return null;
      };
      
      const gallery = findGallery(galleryTree, breadcrumb.id);
      if (gallery) {
        handleGalleryClick(gallery);
      }
    }
  };

  // 返回列表
  const handleBack = () => {
    if (breadcrumbs.length > 1) {
      handleBreadcrumbClick(breadcrumbs[breadcrumbs.length - 2]);
    } else {
      setCurrentGallery(null);
      setBreadcrumbs([]);
      setImages([]);
    }
  };

  return (
    <div className="max-w-7xl mx-auto px-4 py-12 space-y-16">
      {/* Header */}
      <div className="text-center space-y-6">
        <div className="inline-flex items-center gap-3 px-6 py-2 bg-[#fef5f0] text-[#f8b195] rounded-full border border-[#f8b195]/20 shadow-sm">
          <Camera size={18} />
          <span className="text-xs font-black uppercase tracking-[0.4em]">Forest Collection</span>
        </div>
        <h1 className="text-5xl md:text-7xl font-black text-[#4a3728] tracking-tighter">
          {currentGallery ? currentGallery.title : '森林图册'}
        </h1>
        <p className="text-[#8eb69b] font-bold text-lg max-w-2xl mx-auto">
          {currentGallery ? currentGallery.description : '每一帧定格，都是藏在时光信封里的绝色。'}
        </p>
      </div>

      {/* Breadcrumbs */}
      {breadcrumbs.length > 0 && (
        <div className="flex items-center gap-2 text-sm">
          <button 
            onClick={() => handleBreadcrumbClick({id: 'root', title: '首页'})}
            className="text-[#8eb69b] hover:text-[#f8b195] transition-colors"
          >
            首页
          </button>
          {breadcrumbs.map((breadcrumb, idx) => (
            <React.Fragment key={breadcrumb.id}>
              <ChevronRight size={16} className="text-[#8eb69b]/50" />
              <button
                onClick={() => handleBreadcrumbClick(breadcrumb)}
                className={`font-black transition-colors ${
                  idx === breadcrumbs.length - 1 
                    ? 'text-[#f8b195]' 
                    : 'text-[#8eb69b] hover:text-[#f8b195]'
                }`}
              >
                {breadcrumb.title}
              </button>
            </React.Fragment>
          ))}
        </div>
      )}

      {/* Back Button */}
      {currentGallery && (
        <button
          onClick={handleBack}
          className="group flex items-center gap-3 px-8 py-4 bg-white rounded-3xl text-[#8eb69b] font-black hover:text-[#f8b195] transition-all border-2 border-white shadow-sm hover:shadow-xl active:scale-95 mx-auto"
        >
          <ArrowLeft size={20} className="group-hover:-translate-x-1 transition-transform" />
          <span>返回</span>
        </button>
      )}

      {/* Loading */}
      {loading && (
        <div className="py-48 flex flex-col items-center gap-6">
          <div className="w-16 h-16 border-8 border-[#f8b195]/20 border-t-[#f8b195] rounded-full animate-spin"></div>
          <span className="text-[#8eb69b] font-black tracking-widest uppercase text-xs">正在加载...</span>
        </div>
      )}

      {/* Image Gallery (Leaf Node) */}
      {!loading && currentGallery && isLeafGallery(currentGallery) && images.length > 0 && (
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-8">
          {images.map((img, idx) => (
            <div
              key={idx}
              className="group relative bg-white rounded-[2.5rem] overflow-hidden shadow-sm hover:shadow-2xl transition-all duration-700"
              onClick={() => setLightboxImage(img)}
            >
              <div className="aspect-[3/4] overflow-hidden bg-[#fef5f0]">
                <img 
                  src={img.url} 
                  alt={img.title} 
                  className="w-full h-full object-cover group-hover:scale-110 transition-transform duration-1000" 
                />
                <div className="absolute inset-0 bg-black/20 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center">
                  <Maximize2 size={32} className="text-white" />
                </div>
              </div>
              <div className="p-6">
                <h3 className="font-black text-[#4a3728] text-lg">{img.title}</h3>
                <p className="text-[#8eb69b] text-xs font-black uppercase tracking-wider mt-2">{img.date}</p>
              </div>
            </div>
          ))}
        </div>
      )}

      {/* Gallery List (Non-leaf Node) */}
      {!loading && currentGallery && !isLeafGallery(currentGallery) && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-12">
          {currentGallery.children?.map((gallery, idx) => (
            <GalleryCard key={gallery.id} gallery={gallery} onClick={handleGalleryClick} />
          ))}
        </div>
      )}

      {/* Root Gallery List */}
      {!loading && !currentGallery && (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-12">
          {galleryTree.map((gallery, idx) => (
            <GalleryCard key={gallery.id} gallery={gallery} onClick={handleGalleryClick} />
          ))}
        </div>
      )}

      {/* Lightbox */}
      {lightboxImage && (
        <div
          className="fixed inset-0 z-[200] bg-black/95 backdrop-blur-xl flex items-center justify-center p-4 md:p-12"
          onClick={() => setLightboxImage(null)}
        >
          <button className="absolute top-8 right-8 text-white/50 hover:text-white transition-colors">
            <X size={40} />
          </button>
          <img
            src={lightboxImage.url}
            alt={lightboxImage.title}
            className="max-w-full max-h-[80vh] object-contain rounded-2xl shadow-2xl"
          />
        </div>
      )}
    </div>
  );
};

// Gallery Card Component
const GalleryCard: React.FC<{gallery: Gallery, onClick: (gallery: Gallery) => void}> = ({ gallery, onClick }) => (
  <div
    className="group relative cursor-pointer"
    onClick={() => onClick(gallery)}
  >
    <div className="absolute inset-0 bg-white rounded-[3.5rem] rotate-3 translate-y-2 translate-x-1 shadow-sm opacity-50 transition-transform group-hover:rotate-6"></div>
    <div className="absolute inset-0 bg-white rounded-[3.5rem] -rotate-2 translate-y-1 shadow-sm opacity-80 transition-transform group-hover:-rotate-4"></div>
    <div className="relative bg-white rounded-[3.5rem] overflow-hidden shadow-lg border-4 border-white transition-all group-hover:-translate-y-4">
      <div className="aspect-[4/5] overflow-hidden">
        <img 
          src={gallery.cover_url} 
          alt={gallery.title} 
          className="w-full h-full object-cover group-hover:scale-105 transition-transform duration-1000" 
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/60 via-transparent to-transparent opacity-60"></div>
      </div>
      <div className="absolute bottom-0 left-0 right-0 p-8 text-white space-y-2">
        <div className="flex items-center gap-2">
          {gallery.tags.map(t => (
            <span key={t} className="px-2 py-0.5 bg-white/20 backdrop-blur-md rounded-md text-[9px] font-black uppercase tracking-widest">{t}</span>
          ))}
        </div>
        <h2 className="text-3xl font-black tracking-tight">{gallery.title}</h2>
        <div className="flex items-center justify-between pt-2 border-t border-white/20">
          <span className="text-xs font-bold opacity-80">{gallery.image_count} 张瞬间</span>
          <ArrowLeft className="rotate-180 opacity-0 group-hover:opacity-100 transition-all translate-x-4 group-hover:translate-x-0" size={18} />
        </div>
      </div>
    </div>
  </div>
);

export default GalleryPage;
```

---

## 5. 工具脚本

### 7.1 自动扫描文件夹生成图集

```python
# tools/sync_gallery_from_folder.py
import os
import json
from django.core.management.base import BaseCommand
from gallery.models import Gallery
from django.conf import settings

class Command(BaseCommand):
    help = '从文件夹结构自动生成图集树'
    
    def handle(self, *args, **options):
        gallery_root = os.path.join(settings.MEDIA_ROOT, 'gallery')
        
        if not os.path.exists(gallery_root):
            self.stdout.write(self.style.ERROR(f'图集目录不存在: {gallery_root}'))
            return
        
        # 递归扫描文件夹
        def scan_folder(folder_path, parent=None, level=0):
            for item in os.listdir(folder_path):
                item_path = os.path.join(folder_path, item)
                
                if os.path.isdir(item_path):
                    # 计算相对路径
                    rel_path = os.path.relpath(item_path, settings.MEDIA_ROOT)
                    folder_url = '/' + rel_path.replace('\\', '/') + '/'
                    
                    # 检查是否有封面
                    cover_path = os.path.join(item_path, 'cover.jpg')
                    cover_url = f'{folder_url}cover.jpg' if os.path.exists(cover_path) else ''
                    
                    # 计算图片数量
                    image_files = [f for f in os.listdir(item_path) 
                                 if f.lower().endswith(('.jpg', '.jpeg', '.png', '.webp')) 
                                 and f != 'cover.jpg']
                    
                    # 生成图集ID
                    gallery_id = rel_path.replace('\\', '-').replace('/', '-')
                    
                    # 创建或更新图集
                    gallery, created = Gallery.objects.update_or_create(
                        id=gallery_id,
                        defaults={
                            'title': item,
                            'description': f'{item}图集',
                            'cover_url': cover_url,
                            'parent': parent,
                            'level': level,
                            'image_count': len(image_files),
                            'folder_path': folder_url,
                            'tags': [],
                            'is_active': True
                        }
                    )
                    
                    action = '创建' if created else '更新'
                    self.stdout.write(self.style.SUCCESS(f'{action}图集: {gallery.title}'))
                    
                    # 递归处理子文件夹
                    scan_folder(item_path, gallery, level + 1)
        
        # 开始扫描
        scan_folder(gallery_root)
        
        self.stdout.write(self.style.SUCCESS('图集同步完成！'))
```

使用方法：
```bash
python manage.py sync_gallery_from_folder
```

---

## 6. 部署步骤

### 6.1 后端部署

1. **创建 Django App**
```bash
cd repo/xxm_fans_backend
python manage.py startapp gallery
```

2. **创建模型和迁移**
```bash
python manage.py makemigrations gallery
python manage.py migrate
```

3. **注册到 INSTALLED_APPS**
```python
# xxm_fans_home/settings.py
INSTALLED_APPS = [
    ...
    'gallery',
]
```

4. **配置 URL**
```python
# xxm_fans_home/urls.py
urlpatterns = [
    ...
    path('admin/gallery/', include('gallery.urls')),
]
```

5. **创建模板目录**
```bash
mkdir -p repo/xxm_fans_backend/templates/admin/gallery
```

6. **创建模板文件**
将上面的模板代码保存到对应位置

### 6.2 前端部署

前端无需特殊配置，直接通过静态资源 URL 访问图片即可：

```typescript
// GalleryPage.tsx 中直接使用
const images = Array.from({ length: gallery.image_count }, (_, i) => ({
  url: `${gallery.folder_path}${String(i + 1).padStart(3, '0')}.jpg`,
  title: `${gallery.title} - ${i + 1}`,
  date: gallery.created_at
}));
```

### 6.3 Nginx 配置

```nginx
# 在 infra/nginx/xxm_nginx.conf 中添加
location /gallery/ {
    alias /path/to/media/gallery/;
    expires 30d;
    add_header Cache-Control "public, immutable";
}
```

### 6.4 初始化数据

1. **创建图集目录**
```bash
mkdir -p media/gallery/2024/01
mkdir -p media/gallery/2024/02
mkdir -p media/gallery/concert
```

2. **上传图片**
将图片按目录结构上传到对应文件夹

3. **运行同步脚本**
```bash
python manage.py sync_gallery_from_folder
```

4. **通过 Admin 管理图集**
- 登录 Admin 后台（`/admin/gallery/gallery/`）
- 调整图集标题、描述、标签
- 调整排序顺序
- 上传/删除图片
- 更新封面图片

---

## 7. 使用示例

### 场景1：单层图集（演唱会）

```
media/gallery/concert/
├── cover.jpg
├── 001.jpg
├── 002.jpg
└── ...
```

用户点击"演唱会现场" → 直接显示图片流

### 场景2：双层图集（按年月）

```
media/gallery/2024/
├── cover.jpg
├── 01/
│   ├── cover.jpg
│   └── 001.jpg ~ 020.jpg
└── 02/
    ├── cover.jpg
    └── 001.jpg ~ 015.jpg
```

用户点击"2024年" → 显示1月、2月等子图集 → 点击"2024年1月" → 显示图片流

### 场景3：三层图集（按年月日）

```
media/gallery/2024/
├── 01/
│   ├── 15/
│   │   └── 001.jpg ~ 010.jpg
│   └── 16/
│       └── 001.jpg ~ 008.jpg
```

用户点击"2024年" → "1月" → "15日" → 显示图片流

---

## 8. 优势总结

✅ **灵活性**：支持任意层级的图集结构（单层、双层、多层）  
✅ **性能优秀**：图片走静态资源，Nginx 直接提供服务，无需数据库查询  
✅ **易于维护**：文件夹结构直观，便于管理和备份  
✅ **Admin 管理**：完整的 Admin 后台，支持动态上传/删除图片、更新封面  
✅ **自动化**：提供工具脚本自动扫描文件夹生成图集树  
✅ **用户体验**：面包屑导航，清晰的层级关系  
✅ **扩展性**：未来可平滑迁移到完全数据库方案  
✅ **无 API 依赖**：前端直接访问静态资源，简化架构

---

## 9. 注意事项

1. **图片命名规范**：建议使用 `001.jpg`, `002.jpg` 格式，便于排序
2. **封面图片**：每个图集文件夹应包含 `cover.jpg` 作为封面
3. **文件夹命名**：避免使用特殊字符，建议使用英文或数字
4. **图片优化**：建议压缩图片，优化加载速度
5. **缓存策略**：Nginx 配置了30天缓存，更新图片后需要清除缓存
6. **Admin 权限**：只有具有 Admin 权限的用户才能上传/删除图片
7. **文件大小限制**：单张图片建议不超过 5MB
8. **备份策略**：定期备份 `media/gallery/` 目录和数据库

---

## 10. 未来扩展

- [ ] 支持图片元数据（标题、描述、标签）- 可扩展 GalleryImage 模型
- [ ] 支持图片搜索和筛选
- [ ] 支持批量上传和删除
- [ ] 支持图片压缩和优化
- [ ] 支持图片水印
- [ ] 支持多语言
- [ ] 支持图片评论和点赞（需要扩展数据库模型）
- [ ] 支持图片下载和分享（需要添加 API）