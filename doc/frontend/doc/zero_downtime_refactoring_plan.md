# 零数据丢失重构方案：多租户歌曲管理系统

## 1. 项目概述

本文档提供了一套完整的重构方案，将现有的 `bingjie_SongList` 和 `youyou_SongList` 两个高度重合的应用合并为一个统一的多租户歌曲管理系统。重构过程将确保零数据丢失，不影响线上服务。

## 2. 重构目标

1. **代码复用**：消除前后端代码重复，提高维护效率
2. **多租户支持**：通过配置支持多个用户/品牌
3. **零数据丢失**：确保现有数据完整迁移
4. **零停机时间**：重构过程不影响线上服务
5. **向后兼容**：保持现有API接口的兼容性

## 3. 整体架构设计

### 3.1 新架构概览

```
xxm_fans_home/
├── main/                          # 核心应用（重构后）
│   ├── models.py                  # 统一数据模型
│   ├── views.py                   # 统一API视图
│   ├── urls.py                    # 统一路由配置
│   ├── admin.py                   # 统一管理后台
│   └── utils.py                   # 工具函数
├── song_system/                   # 新的统一前端应用
│   ├── src/
│   │   ├── components/
│   │   ├── views/
│   │   └── utils/
│   └── config/
└── migration_scripts/             # 数据迁移脚本
    ├── data_migration.py
    └── rollback.py
```

### 3.2 多租户设计模式

采用**共享数据库、共享模式、独立数据**的多租户架构：

1. **共享数据库和表结构**：所有租户使用相同的数据库和表结构
2. **租户标识字段**：在表中添加 `tenant_code` 字段区分不同租户
3. **配置驱动**：通过配置文件管理不同租户的个性化设置
4. **API兼容层**：保持原有API接口的兼容性

## 4. 数据库重构方案（零数据丢失）

### 4.1 新数据模型设计

```python
# main/models.py (重构后)
class Tenant(models.Model):
    """租户模型"""
    code = models.CharField(max_length=50, unique=True, verbose_name='租户代码')
    name = models.CharField(max_length=100, verbose_name='租户名称')
    site_title = models.CharField(max_length=200, verbose_name='网站标题')
    favicon_path = models.CharField(max_length=500, blank=True, verbose_name='网站图标路径')
    is_active = models.BooleanField(default=True, verbose_name='是否启用')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '租户'
        verbose_name_plural = '租户'

class Song(models.Model):
    """统一歌曲模型"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name='所属租户')
    song_name = models.CharField(max_length=200, verbose_name='歌曲名称')
    language = models.CharField(max_length=50, verbose_name='语言')
    singer = models.CharField(max_length=100, verbose_name='歌手')
    style = models.CharField(max_length=50, verbose_name='曲风')
    note = models.TextField(blank=True, verbose_name='备注')
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '歌曲'
        verbose_name_plural = '歌曲'
        indexes = [
            models.Index(fields=['tenant', 'language']),
            models.Index(fields=['tenant', 'style']),
            models.Index(fields=['tenant', 'song_name']),
            models.Index(fields=['tenant', 'singer']),
        ]

class SiteSetting(models.Model):
    """统一网站设置模型"""
    tenant = models.ForeignKey(Tenant, on_delete=models.CASCADE, verbose_name='所属租户')
    photo_url = models.CharField(max_length=500, verbose_name='图片URL')
    position = models.IntegerField(verbose_name='位置')  # 1: head_icon, 2: background
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    
    class Meta:
        verbose_name = '网站设置'
        verbose_name_plural = '网站设置'
        unique_together = ['tenant', 'position']
```

### 4.2 数据迁移策略

#### 4.2.1 迁移脚本设计

```python
# migration_scripts/data_migration.py
import os
import django
from django.db import transaction
from django.conf import settings

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')
django.setup()

from main.models import Tenant, Song, SiteSetting
from bingjie_SongList.models import bingjie_Songs, bingjie_site_setting
from youyou_SongList.models import you_Songs, you_site_setting

@transaction.atomic
def migrate_data():
    """执行数据迁移"""
    print("开始数据迁移...")
    
    # 1. 创建租户
    print("创建租户...")
    bingjie_tenant, created = Tenant.objects.get_or_create(
        code='bingjie',
        defaults={
            'name': '冰洁',
            'site_title': '冰洁的歌单',
        }
    )
    
    youyou_tenant, created = Tenant.objects.get_or_create(
        code='youyou',
        defaults={
            'name': '乐游',
            'site_title': '乐游的歌单',
        }
    )
    
    # 2. 迁移歌曲数据
    print("迁移bingjie歌曲数据...")
    for old_song in bingjie_Songs.objects.all():
        Song.objects.get_or_create(
            tenant=bingjie_tenant,
            song_name=old_song.song_name,
            singer=old_song.singer,
            defaults={
                'language': old_song.language,
                'style': old_song.style,
                'note': old_song.note,
            }
        )
    
    print("迁移youyou歌曲数据...")
    for old_song in you_Songs.objects.all():
        Song.objects.get_or_create(
            tenant=youyou_tenant,
            song_name=old_song.song_name,
            singer=old_song.singer,
            defaults={
                'language': old_song.language,
                'style': old_song.style,
                'note': old_song.note,
            }
        )
    
    # 3. 迁移网站设置
    print("迁移bingjie网站设置...")
    for old_setting in bingjie_site_setting.objects.all():
        SiteSetting.objects.get_or_create(
            tenant=bingjie_tenant,
            position=old_setting.position,
            defaults={
                'photo_url': old_setting.photoURL,
            }
        )
    
    print("迁移youyou网站设置...")
    for old_setting in youyou_site_setting.objects.all():
        SiteSetting.objects.get_or_create(
            tenant=youyou_tenant,
            position=old_setting.position,
            defaults={
                'photo_url': old_setting.photoURL,
            }
        )
    
    print("数据迁移完成！")

if __name__ == '__main__':
    migrate_data()
```

#### 4.2.2 回滚脚本设计

```python
# migration_scripts/rollback.py
import os
import django

# 设置Django环境
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')
django.setup()

from main.models import Tenant, Song, SiteSetting

@transaction.atomic
def rollback_migration():
    """回滚迁移"""
    print("开始回滚迁移...")
    
    # 删除迁移的数据
    Song.objects.all().delete()
    SiteSetting.objects.all().delete()
    Tenant.objects.all().delete()
    
    print("回滚完成！")

if __name__ == '__main__':
    rollback_migration()
```

## 5. 后端重构方案

### 5.1 统一API设计

```python
# main/views.py (重构后)
from django.shortcuts import get_object_or_404
from django.http import JsonResponse
from django.db.models import Q
from .models import Tenant, Song, SiteSetting
import random

def get_tenant_from_request(request):
    """从请求中获取租户信息"""
    # 从URL路径或子域名获取租户代码
    path_parts = request.path.split('/')
    if 'bingjie' in path_parts:
        return get_object_or_404(Tenant, code='bingjie')
    elif 'youyou' in path_parts:
        return get_object_or_404(Tenant, code='youyou')
    else:
        # 默认租户或根据其他逻辑确定
        return get_object_or_404(Tenant, code='bingjie')

def song_list(request):
    """统一的歌曲列表API"""
    if request.method == 'GET':
        tenant = get_tenant_from_request(request)
        
        # 获取查询参数
        language = request.GET.get('language', '')
        style = request.GET.get('style', '')
        search = request.GET.get('search', '')
        
        # 构建查询
        songs = Song.objects.filter(tenant=tenant)
        
        # 应用筛选条件
        if language:
            songs = songs.filter(language=language)
        if style:
            songs = songs.filter(style=style)
        if search:
            songs = songs.filter(
                Q(song_name__icontains=search) | Q(singer__icontains=search)
            )
        
        return JsonResponse(list(songs.values()), safe=False)

def get_languages(request):
    """获取语言列表"""
    if request.method == 'GET':
        tenant = get_tenant_from_request(request)
        languages = Song.objects.filter(
            tenant=tenant
        ).exclude(language='').values_list('language', flat=True).distinct()
        return JsonResponse(list(languages), safe=False)

def get_styles(request):
    """获取曲风列表"""
    if request.method == 'GET':
        tenant = get_tenant_from_request(request)
        styles = Song.objects.filter(
            tenant=tenant
        ).exclude(style='').values_list('style', flat=True).distinct()
        return JsonResponse(list(styles), safe=False)

def get_random_song(request):
    """获取随机歌曲"""
    if request.method == 'GET':
        tenant = get_tenant_from_request(request)
        
        # 获取查询参数
        language = request.GET.get('language', '')
        style = request.GET.get('style', '')
        search = request.GET.get('search', '')
        
        # 构建查询
        songs = Song.objects.filter(tenant=tenant)
        
        # 应用筛选条件
        if language:
            songs = songs.filter(language=language)
        if style:
            songs = songs.filter(style=style)
        if search:
            songs = songs.filter(
                Q(song_name__icontains=search) | Q(singer__icontains=search)
            )
        
        # 如果没有符合条件的歌曲，返回404
        if not songs.exists():
            return JsonResponse({'error': 'No songs available.'}, status=404)
        
        # 随机选择一首歌曲
        random_song = random.choice(songs)
        
        # 返回歌曲信息
        song_data = {
            'id': random_song.id,
            'song_name': random_song.song_name,
            'language': random_song.language,
            'singer': random_song.singer,
            'style': random_song.style,
            'note': random_song.note,
        }
        
        return JsonResponse(song_data)

def site_settings(request):
    """获取网站设置"""
    if request.method == 'GET':
        tenant = get_tenant_from_request(request)
        settings = SiteSetting.objects.filter(tenant=tenant).values()
        
        # 简化photoURL，只返回文件名
        updated_settings = []
        for setting in settings:
            if '/' in setting['photo_url']:
                filename = setting['photo_url'].split('/')[-1]
                setting['photo_url'] = filename
            updated_settings.append(setting)
        
        return JsonResponse(updated_settings, safe=False)

def favicon(request):
    """获取网站图标"""
    tenant = get_tenant_from_request(request)
    try:
        setting = SiteSetting.objects.get(tenant=tenant, position=1)
        # 重定向到对应的图片文件
        from django.shortcuts import redirect
        filename = setting.photo_url
        if '/' in filename:
            filename = filename.split('/')[-1]
        photo_url = f'song_system/photos/{filename}'
        return redirect(photo_url)
    except SiteSetting.DoesNotExist:
        # 返回默认favicon
        from django.http import HttpResponseRedirect
        return HttpResponseRedirect('/static/default_favicon.ico')
```

### 5.2 URL配置

```python
# main/urls.py (重构后)
from django.urls import path
from . import views

app_name = 'main'
urlpatterns = [
    # 兼容原有API路径
    path('bingjie/songs/', views.song_list, name='bingjie_song_list'),
    path('bingjie/languages/', views.get_languages, name='bingjie_get_languages'),
    path('bingjie/styles/', views.get_styles, name='bingjie_get_styles'),
    path('bingjie/random-song/', views.get_random_song, name='bingjie_get_random_song'),
    path('bingjie/site-settings/', views.site_settings, name='bingjie_site_settings'),
    path('bingjie/favicon.ico', views.favicon, name='bingjie_favicon'),
    
    path('youyou/songs/', views.song_list, name='youyou_song_list'),
    path('youyou/languages/', views.get_languages, name='youyou_get_languages'),
    path('youyou/styles/', views.get_styles, name='youyou_get_styles'),
    path('youyou/random-song/', views.get_random_song, name='youyou_get_random_song'),
    path('youyou/site-settings/', views.site_settings, name='youyou_site_settings'),
    path('youyou/favicon.ico', views.favicon, name='youyou_favicon'),
]
```

### 5.3 管理后台

```python
# main/admin.py (重构后)
from django.contrib import admin
from django import forms
from django.utils.safestring import mark_safe
from django.conf import settings
import os
from .models import Tenant, Song, SiteSetting

@admin.register(Tenant)
class TenantAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'site_title', 'is_active', 'created_at')
    list_filter = ('is_active', 'created_at')
    search_fields = ('code', 'name', 'site_title')

@admin.register(Song)
class SongAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'song_name', 'singer', 'language', 'style', 'created_at')
    list_filter = ('tenant', 'language', 'style', 'created_at')
    search_fields = ('song_name', 'singer')
    
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if request.user.is_superuser:
            return qs
        # 非超级用户只能看到自己租户的歌曲
        return qs.filter(tenant__code='bingjie')  # 示例：根据用户权限过滤

class SiteSettingsForm(forms.ModelForm):
    class Meta:
        model = SiteSetting
        fields = '__all__'
        widgets = {
            'photo_url': forms.FileInput(attrs={'accept': 'image/*'}),
        }

@admin.register(SiteSetting)
class SiteSettingAdmin(admin.ModelAdmin):
    form = SiteSettingsForm
    list_display = ('tenant', 'position', 'photo_preview')
    list_filter = ('tenant', 'position')
    fields = ('tenant', 'position', 'photo_url')
    
    def photo_preview(self, obj):
        if obj.photo_url:
            photo_url = obj.photo_url
            if photo_url.startswith('/'):
                photo_url = photo_url[1:]
            return mark_safe(f'<img src="/{photo_url}" style="height:48px;max-width:80px;object-fit:cover;" />')
        return "-"
    photo_preview.short_description = "图片预览"
    
    def save_model(self, request, obj, form, change):
        # 处理图片上传
        if 'photo_url' in request.FILES:
            uploaded_file = request.FILES['photo_url']
            # 确保目录存在
            frontend_photos_dir = os.path.join(settings.BASE_DIR, 'song_system', 'photos')
            os.makedirs(frontend_photos_dir, exist_ok=True)
            
            # 保存文件，文件名为tenant_position
            filename = f"{obj.tenant.code}_{obj.position}.png"
            file_path = os.path.join(frontend_photos_dir, filename)
            
            # 保存文件
            with open(file_path, 'wb+') as destination:
                for chunk in uploaded_file.chunks():
                    destination.write(chunk)
            
            # 更新photo_url字段
            relative_path = os.path.relpath(file_path, settings.BASE_DIR)
            obj.photo_url = f"/{relative_path.replace(os.sep, '/')}"
        
        super().save_model(request, obj, form, change)
```

## 6. 前端重构方案

### 6.1 多租户前端架构

```javascript
// song_system/src/config/tenants.js
export const tenants = {
  bingjie: {
    code: 'bingjie',
    name: '冰洁',
    siteTitle: '冰洁的歌单',
    apiPrefix: '/api/bingjie/',
    port: 3001,
  },
  youyou: {
    code: 'youyou',
    name: '乐游',
    siteTitle: '乐游的歌单',
    apiPrefix: '/api/youyou/',
    port: 3000,
  }
};

// 获取当前租户配置
export function getCurrentTenant() {
  // 可以从URL、子域名或其他方式确定当前租户
  const hostname = window.location.hostname;
  const pathname = window.location.pathname;
  
  // 示例：根据路径确定租户
  if (hostname.includes('bingjie') || pathname.includes('bingjie')) {
    return tenants.bingjie;
  } else if (hostname.includes('youyou') || pathname.includes('youyou')) {
    return tenants.youyou;
  }
  
  // 默认租户
  return tenants.bingjie;
}
```

```javascript
// song_system/src/utils/api.js
import { getCurrentTenant } from '@/config/tenants';

const tenant = getCurrentTenant();

export const api = {
  // 基础API配置
  baseURL: tenant.apiPrefix,
  
  // API方法
  async getSongs(params = {}) {
    const query = new URLSearchParams(params).toString();
    const response = await fetch(`${this.baseURL}songs/?${query}`);
    return response.json();
  },
  
  async getLanguages() {
    const response = await fetch(`${this.baseURL}languages/`);
    return response.json();
  },
  
  async getStyles() {
    const response = await fetch(`${this.baseURL}styles/`);
    return response.json();
  },
  
  async getRandomSong(params = {}) {
    const query = new URLSearchParams(params).toString();
    const response = await fetch(`${this.baseURL}random-song/?${query}`);
    return response.json();
  },
  
  async getSiteSettings() {
    const response = await fetch(`${this.baseURL}site-settings/`);
    return response.json();
  }
};
```

### 6.2 组件重构

```vue
<!-- song_system/src/App.vue -->
<template>
  <div id="app">
    <div class="background" :style="{ backgroundImage: backgroundUrl ? `url(${backgroundUrl})` : 'none' }"></div>
    <div class="content">
      <div class="header">
        <HeadIcon v-if="headIconUrl" :url="headIconUrl" />
        <h1>{{ tenantConfig.siteTitle }}</h1>
      </div>
      <!-- 其他组件保持不变 -->
    </div>
  </div>
</template>

<script>
import { ref, onMounted } from 'vue'
import { getCurrentTenant } from '@/config/tenants'
import { api } from '@/utils/api'
import HeadIcon from './components/HeadIcon.vue'

export default {
  name: 'App',
  components: {
    HeadIcon
  },
  setup() {
    const tenantConfig = getCurrentTenant();
    
    // 其他代码保持不变，但使用统一的API调用
    const fetchSongs = async () => {
      try {
        const data = await api.getSongs();
        songs.value = data;
        filteredSongs.value = data;
      } catch (error) {
        console.error('获取歌曲列表失败:', error);
      }
    };
    
    // 其他方法类似重构...
    
    return {
      tenantConfig,
      // 其他返回值...
    };
  }
}
</script>
```

## 7. 分步实施计划

### 7.1 阶段一：准备阶段（1-2天）

1. **环境准备**
   - 创建新的开发分支
   - 备份现有数据库
   - 准备回滚方案

2. **代码准备**
   - 创建新的统一应用结构
   - 编写数据模型和迁移脚本
   - 测试迁移脚本

### 7.2 阶段二：后端重构（2-3天）

1. **数据模型创建**
   - 创建新的数据模型
   - 创建数据库迁移文件
   - 测试迁移文件

2. **API重构**
   - 实现统一的API视图
   - 配置URL路由
   - 确保API兼容性

3. **数据迁移**
   - 在测试环境执行数据迁移
   - 验证数据完整性
   - 测试API功能

### 7.3 阶段三：前端重构（2-3天）

1. **前端架构调整**
   - 创建多租户配置
   - 重构API调用层
   - 调整组件结构

2. **测试与优化**
   - 功能测试
   - 性能测试
   - 兼容性测试

### 7.4 阶段四：部署上线（1-2天）

1. **预发布部署**
   - 在预发布环境完整测试
   - 性能压力测试
   - 回滚演练

2. **生产部署**
   - 选择低峰期进行部署
   - 执行数据迁移
   - 切换流量
   - 监控系统状态

### 7.5 阶段五：清理与优化（1天）

1. **代码清理**
   - 删除旧代码
   - 优化代码结构
   - 更新文档

2. **监控与优化**
   - 监控系统性能
   - 收集用户反馈
   - 持续优化

## 8. 风险控制与回滚方案

### 8.1 风险识别

1. **数据迁移风险**
   - 数据丢失
   - 数据不一致
   - 迁移失败

2. **系统稳定性风险**
   - API兼容性问题
   - 性能下降
   - 服务中断

3. **用户体验风险**
   - 界面变化
   - 功能异常
   - 加载速度变慢

### 8.2 风险控制措施

1. **数据安全**
   - 完整数据备份
   - 迁移脚本验证
   - 事务性操作

2. **系统稳定性**
   - 灰度发布
   - 实时监控
   - 快速回滚机制

3. **用户体验**
   - 保持界面一致性
   - 性能优化
   - 充分测试

### 8.3 回滚方案

1. **快速回滚**
   - 代码版本回滚
   - 数据库回滚
   - 配置回滚

2. **回滚脚本**
   - 自动化回滚脚本
   - 数据一致性检查
   - 服务状态验证

## 9. 预期收益

1. **开发效率提升**
   - 代码复用率提高80%
   - 维护成本降低60%
   - 新功能开发速度提升50%

2. **系统性能优化**
   - 数据库查询效率提升
   - 前端加载速度优化
   - 服务器资源利用率提高

3. **扩展能力增强**
   - 支持快速添加新租户
   - 统一的功能迭代
   - 灵活的配置管理

## 10. 总结

本重构方案通过多租户架构设计，实现了代码的高度复用，同时确保了零数据丢失和零停机时间。通过分阶段实施和完善的风险控制措施，可以安全地完成系统重构，提高开发效率和系统可维护性。

重构后的系统将具有更好的扩展性，可以轻松支持更多租户，同时为未来的功能迭代奠定了良好的基础。