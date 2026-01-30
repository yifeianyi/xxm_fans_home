# 模板化歌单系统 - 自动化添加新歌手方案

## 当前问题

当前配置添加新歌手需要手动修改 5 个文件 + 运行数据库迁移 + 创建静态文件，扩展性较差。

## 自动化方案

### 方案概述

通过以下改进实现自动化添加新歌手：

1. **后端配置集中化** - 使用 Django Admin 或配置文件管理歌手信息
2. **动态模型注册** - 自动发现和注册模型
3. **前端动态加载** - 从 API 获取歌手配置
4. **静态文件自动映射** - 使用通配符路径匹配
5. **提供管理脚本** - 一键添加新歌手

---

## 后端改进

### 1. 创建歌手配置模型

在 `songlist/models.py` 中添加统一的歌手配置模型：

```python
class ArtistConfig(models.Model):
    """歌手配置表"""
    artist_key = models.CharField(max_length=50, unique=True, verbose_name='歌手标识')
    artist_name = models.CharField(max_length=100, verbose_name='歌手名称')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '歌手配置'
        verbose_name_plural = '歌手配置'
    
    def __str__(self):
        return f"{self.artist_name} ({self.artist_key})"
```

### 2. 改进 models.py - 动态模型注册

```python
from django.db import models
from django.apps import apps

# 获取所有启用的歌手配置
def get_active_artists():
    """获取所有启用的歌手配置"""
    try:
        return ArtistConfig.objects.filter(is_active=True)
    except:
        # 如果表不存在，返回默认配置
        return [
            type('ArtistConfig', (), {
                'artist_key': 'youyou',
                'artist_name': '乐游'
            })(),
            type('ArtistConfig', (), {
                'artist_key': 'bingjie',
                'artist_name': '冰洁'
            })(),
        ]

# 动态创建模型
def create_artist_models(artist_key, artist_name):
    """创建歌手的Song和SiteSetting模型"""
    class_name = artist_key.capitalize()
    
    # 创建Song模型
    song_model = type(
        f'{class_name}Song',
        (models.Model,),
        {
            '__module__': 'songlist.models',
            'song_name': models.CharField(max_length=200, verbose_name='歌曲名称'),
            'singer': models.CharField(max_length=100, verbose_name='原唱歌手'),
            'language': models.CharField(max_length=50, verbose_name='语言'),
            'style': models.CharField(max_length=50, verbose_name='曲风'),
            'note': models.TextField(blank=True, verbose_name='备注'),
            'Meta': type('Meta', (), {
                'verbose_name': f'{artist_name}歌曲',
                'verbose_name_plural': f'{artist_name}歌曲',
                'app_label': 'songlist',
                'ordering': ['song_name']
            }),
            '__str__': lambda self: self.song_name,
        }
    )
    
    # 创建SiteSetting模型
    setting_model = type(
        f'{class_name}SiteSetting',
        (models.Model,),
        {
            '__module__': 'songlist.models',
            'photo_url': models.CharField(max_length=500, verbose_name='图片URL'),
            'position': models.IntegerField(
                verbose_name='位置',
                choices=[(1, '头像图标'), (2, '背景图片')]
            ),
            'Meta': type('Meta', (), {
                'verbose_name': f'{artist_name}网站设置',
                'verbose_name_plural': f'{artist_name}网站设置',
                'app_label': 'songlist'
            }),
            '__str__': lambda self: f"设置 - 位置: {self.get_position_display()}",
        }
    )
    
    return song_model, setting_model

# 动态注册所有模型
ARTIST_MODELS = {}
for artist in get_active_artists():
    song_model, setting_model = create_artist_models(artist.artist_key, artist.artist_name)
    ARTIST_MODELS[artist.artist_key] = {
        'song': song_model,
        'setting': setting_model
    }
    # 注册到全局
    globals()[f'{artist.artist_key.capitalize()}Song'] = song_model
    globals()[f'{artist.artist_key.capitalize()}SiteSetting'] = setting_model

# 导出所有模型
__all__ = ['ArtistConfig'] + \
          [f'{k.capitalize()}Song' for k in ARTIST_MODELS.keys()] + \
          [f'{k.capitalize()}SiteSetting' for k in ARTIST_MODELS.keys()]
```

### 3. 改进 views.py - 动态模型查找

```python
from .models import ARTIST_MODELS

def get_artist_model(artist, model_type='song'):
    """根据歌手标识获取对应的模型"""
    if artist in ARTIST_MODELS:
        return ARTIST_MODELS[artist][model_type]
    return None

# 其他视图函数保持不变，使用 get_artist_model 动态获取模型
```

### 4. 添加歌手管理 API

在 `songlist/views.py` 中添加：

```python
from django.http import JsonResponse
from .models import ArtistConfig

def artist_list(request):
    """获取所有歌手列表"""
    if request.method == 'GET':
        artists = ArtistConfig.objects.filter(is_active=True).values('artist_key', 'artist_name')
        return JsonResponse(list(artists), safe=False)

def add_artist(request):
    """添加新歌手"""
    if request.method == 'POST':
        import json
        data = json.loads(request.body)
        artist_key = data.get('artist_key')
        artist_name = data.get('artist_name')
        
        if not artist_key or not artist_name:
            return JsonResponse({'error': 'Missing required fields'}, status=400)
        
        # 检查是否已存在
        if ArtistConfig.objects.filter(artist_key=artist_key).exists():
            return JsonResponse({'error': 'Artist already exists'}, status=400)
        
        # 创建歌手配置
        artist = ArtistConfig.objects.create(
            artist_key=artist_key,
            artist_name=artist_name
        )
        
        # 创建数据库表
        from django.core.management import call_command
        call_command('makemigrations', 'songlist', '--no-input')
        call_command('migrate', 'songlist', '--no-input')
        
        return JsonResponse({'success': True, 'artist': artist.artist_key})
```

### 5. 添加 URL 路由

在 `songlist/urls.py` 中添加：

```python
urlpatterns = [
    # ... 现有路由
    path('artists/', views.artist_list, name='artist-list'),
    path('artists/add/', views.add_artist, name='add-artist'),
]
```

---

## 前端改进

### 1. 修改 SonglistHeader.tsx - 动态获取歌手名称

```typescript
import React, { useState, useEffect } from 'react';

interface SiteSetting {
  id: number;
  photo_url: string;
  position: number;
}

interface ArtistInfo {
  artist_key: string;
  artist_name: string;
}

interface SonglistHeaderProps {
  artist: string;
  settings: SiteSetting[];
}

const SonglistHeader: React.FC<SonglistHeaderProps> = ({ artist, settings }) => {
  const [artistName, setArtistName] = useState<string>(artist);
  
  // 从 API 获取歌手名称
  useEffect(() => {
    fetch('/api/songlist/artists/')
      .then(res => res.json())
      .then(artists => {
        const found = artists.find((a: ArtistInfo) => a.artist_key === artist);
        if (found) {
          setArtistName(found.artist_name);
        }
      })
      .catch(err => console.error('Failed to fetch artist name:', err));
  }, [artist]);
  
  // ... 其他代码保持不变，使用 artistName 替代 displayName
};
```

---

## Nginx 改进

### 使用通配符路径匹配

在 `infra/nginx/xxm_nginx.conf` 中：

```nginx
# 使用通配符匹配所有歌手的静态文件
location ~ ^/([^/]+)_SongList_frontend/photos/(.*)$ {
    alias /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend/static/$1_SongList_frontend/photos/$2;
    expires 30d;
    add_header Cache-Control "public, immutable";
    add_header X-Frame-Options "DENY" always;
    add_header X-Content-Type-Options "nosniff" always;
}
```

这样就无需为每个歌手单独配置路径。

---

## 管理脚本

### 创建一键添加歌手脚本

创建 `scripts/add_artist.sh`：

```bash
#!/bin/bash

# XXM Fans Home - 添加新歌手脚本

if [ $# -lt 2 ]; then
    echo "用法: $0 <歌手标识> <歌手名称>"
    echo "示例: $0 xiaoming 小明"
    exit 1
fi

ARTIST_KEY=$1
ARTIST_NAME=$2

echo "========================================="
echo "添加新歌手: ${ARTIST_NAME} (${ARTIST_KEY})"
echo "========================================="
echo ""

# 1. 创建静态文件目录
echo "1. 创建静态文件目录..."
STATIC_DIR="/home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend/static/${ARTIST_KEY}_SongList_frontend/photos"
mkdir -p "$STATIC_DIR"
echo "   目录创建成功: $STATIC_DIR"

# 2. 创建占位图片
echo "2. 创建占位图片..."
cat > "${STATIC_DIR}/1.png" << 'EOF'
<svg width="200" height="200" xmlns="http://www.w3.org/2000/svg">
  <rect width="200" height="200" fill="#f8b195"/>
  <text x="100" y="100" font-size="20" text-anchor="middle" fill="#4a3728">头像</text>
</svg>
EOF

cat > "${STATIC_DIR}/2.png" << 'EOF'
<svg width="1200" height="400" xmlns="http://www.w3.org/2000/svg">
  <rect width="1200" height="400" fill="url(#grad)"/>
  <defs>
    <linearGradient id="grad" x1="0%" y1="0%" x2="100%" y2="0%">
      <stop offset="0%" style="stop-color:#f8b195;stop-opacity:1" />
      <stop offset="100%" style="stop-color:#f67280;stop-opacity:1" />
    </linearGradient>
  </defs>
  <text x="600" y="200" font-size="40" text-anchor="middle" fill="#4a3728">背景</text>
</svg>
EOF
echo "   占位图片创建成功"

# 3. 调用 API 添加歌手
echo "3. 调用 API 添加歌手..."
curl -X POST http://localhost:8080/api/songlist/artists/add/ \
  -H "Content-Type: application/json" \
  -d "{\"artist_key\": \"${ARTIST_KEY}\", \"artist_name\": \"${ARTIST_NAME}\"}"

echo ""
echo ""
echo "========================================="
echo "歌手添加完成！"
echo "========================================="
echo ""
echo "访问地址: http://localhost:8080/songlist/${ARTIST_KEY}"
echo ""
echo "后续操作:"
echo "  1. 上传真实的头像和背景图片到: ${STATIC_DIR}"
echo "  2. 在 Django Admin 中添加歌曲数据"
echo "  3. 在 Django Admin 中配置网站设置"
echo ""
```

### 使用方法

```bash
cd /home/yifeianyi/Desktop/xxm_fans_home
chmod +x scripts/add_artist.sh
./scripts/add_artist.sh xiaoming 小明
```

---

## 改进后的添加流程

### 自动化方案（推荐）

只需执行一个命令：

```bash
./scripts/add_artist.sh xiaoming 小明
```

脚本会自动完成：
1. ✅ 创建静态文件目录
2. ✅ 创建占位图片
3. ✅ 调用 API 添加歌手配置
4. ✅ 运行数据库迁移
5. ✅ 返回访问地址

### 手动方案

如果需要手动添加：

1. **后端** - 在 Django Admin 中添加歌手配置
2. **数据库** - 系统自动运行迁移
3. **前端** - 无需修改，自动从 API 加载
4. **Nginx** - 无需修改，使用通配符匹配
5. **静态文件** - 手动创建目录和图片

---

## 优势对比

| 项目 | 当前方案 | 自动化方案 |
|------|---------|-----------|
| 修改文件数 | 5 个 | 0 个（使用脚本） |
| 手动步骤 | 6 步 | 1 步 |
| 出错风险 | 高 | 低 |
| 学习成本 | 高 | 低 |
| 维护成本 | 高 | 低 |

---

## 注意事项

1. **数据库迁移** - 首次使用需要运行 `python manage.py makemigrations songlist` 创建 ArtistConfig 表
2. **图片格式** - 占位图片使用 SVG 格式，生产环境建议使用 PNG/JPG
3. **歌手标识** - 只能包含小写字母和数字，不能包含特殊字符
4. **权限管理** - 建议在生产环境中添加 API 认证

---

## 实施步骤

1. 按照上述方案修改代码
2. 运行数据库迁移：`python manage.py makemigrations songlist && python manage.py migrate`
3. 重启后端服务
4. 测试添加新歌手功能
5. 部署到生产环境

---

## 总结

通过以上改进，添加新歌手从需要修改 5 个文件、6 个手动步骤，简化为执行一个命令即可完成。大大提高了系统的可维护性和扩展性。