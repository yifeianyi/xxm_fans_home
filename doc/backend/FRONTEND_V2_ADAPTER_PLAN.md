# 前端 V2 大版本更新后端适配方案

## 文档信息

- **创建日期**: 2026-01-19
- **版本**: 1.0
- **作者**: iFlow CLI
- **状态**: 待实施

---

## 一、概述

前端项目完成了大版本更新（V2），新增了 4 个页面、3 个功能组件和 12 个数据类型。本方案详细说明后端需要进行的适配工作，包括新增模型、API接口、数据迁移等。

### 新增功能概览

| 功能模块 | 新增页面 | 新增组件 | 优先级 |
|---------|---------|---------|-------|
| 图集管理 | GalleryPage | - | 高 |
| 直播纪事 | LivestreamPage | - | 高 |
| 关于页面 | AboutPage | - | 中 |
| 数据分析 | DataAnalysisPage | TimelineChart | 低 |
| 音乐播放 | - | MusicPlayer | 中 |
| 原创作品 | - | OriginalsList | 中 |

---

## 二、现有后端架构分析

### 2.1 现有应用结构

```
xxm_fans_backend/
├── core/                    # 核心模块（缓存、异常、响应格式）
├── song_management/         # 歌曲管理应用
├── fansDIY/                 # 粉丝二创作品管理应用
├── site_settings/           # 网站设置应用
├── data_analytics/          # 数据分析应用
└── songlist/                # 模板化歌单应用
```

### 2.2 现有数据模型

- **song_management**: Song, SongRecord, Style, Tag, SongStyle, SongTag
- **fansDIY**: Collection, Work
- **site_settings**: SiteSettings, Recommendation
- **data_analytics**: WorkStatic, WorkMetricsHour, CrawlSession
- **songlist**: 动态创建的 ArtistSong, ArtistSiteSetting

### 2.3 现有API端点

- `/api/songs/` - 歌曲管理
- `/api/fansDIY/` - 粉丝二创
- `/api/site-settings/` - 网站设置
- `/api/data-analytics/` - 数据分析
- `/api/songlist/` - 模板化歌单

---

## 三、后端适配方案

### 3.1 高优先级适配（核心功能）

#### 3.1.1 图集管理模块

**需求说明**:
- 支持多个图集分类
- 每个图集包含多张图片
- 支持图片标签和日期
- 支持图片灯箱预览

**数据模型设计**:

```python
# gallery/models.py

from django.db import models
from django.core.validators import FileExtensionValidator


class Gallery(models.Model):
    """图集模型"""
    title = models.CharField(max_length=200, verbose_name="图集标题")
    description = models.TextField(blank=True, verbose_name="图集描述")
    cover_image = models.ImageField(
        upload_to='gallery/covers/',
        verbose_name="封面图片"
    )
    tags = models.JSONField(default=list, verbose_name="标签列表")
    is_active = models.BooleanField(default=True, verbose_name="是否激活")
    display_order = models.IntegerField(default=0, verbose_name="显示顺序")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "图集"
        verbose_name_plural = "图集"
        ordering = ['display_order', '-created_at']

    def __str__(self):
        return self.title

    @property
    def image_count(self):
        """返回图集内图片数量"""
        return self.images.count()


class GalleryImage(models.Model):
    """图集图片模型"""
    gallery = models.ForeignKey(
        Gallery,
        on_delete=models.CASCADE,
        related_name='images',
        verbose_name="所属图集"
    )
    image = models.ImageField(
        upload_to='gallery/images/%Y/%m/',
        validators=[FileExtensionValidator(['jpg', 'jpeg', 'png', 'webp'])],
        verbose_name="图片文件"
    )
    title = models.CharField(max_length=200, blank=True, verbose_name="图片标题")
    description = models.TextField(blank=True, verbose_name="图片描述")
    date = models.DateField(blank=True, null=True, verbose_name="拍摄日期")
    tags = models.JSONField(default=list, verbose_name="标签列表")
    display_order = models.IntegerField(default=0, verbose_name="显示顺序")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "图集图片"
        verbose_name_plural = "图集图片"
        ordering = ['display_order', 'created_at']

    def __str__(self):
        return f"{self.gallery.title} - {self.title or self.id}"
```

**API接口设计**:

```python
# gallery/api/views.py

from rest_framework import generics
from rest_framework.decorators import api_view
from core.responses import success_response, error_response, paginated_response
from .serializers import GallerySerializer, GalleryImageSerializer
from .models import Gallery, GalleryImage


class GalleryListView(generics.ListCreateAPIView):
    """图集列表"""
    serializer_class = GallerySerializer

    def get_queryset(self):
        is_active = self.request.query_params.get("is_active")
        tags = self.request.query_params.get("tags")

        queryset = Gallery.objects.all()

        if is_active is not None:
            queryset = queryset.filter(is_active=is_active.lower() == 'true')

        if tags:
            tag_list = tags.split(',')
            queryset = queryset.filter(tags__contains=tag_list)

        return queryset.order_by('display_order', '-created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)


class GalleryDetailView(generics.RetrieveAPIView):
    """图集详情"""
    queryset = Gallery.objects.all()
    serializer_class = GallerySerializer


class GalleryImageListView(generics.ListAPIView):
    """图集图片列表"""
    serializer_class = GalleryImageSerializer

    def get_queryset(self):
        gallery_id = self.kwargs['gallery_id']
        return GalleryImage.objects.filter(
            gallery_id=gallery_id
        ).order_by('display_order', 'created_at')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)
```

**API端点**:

- `GET /api/gallery/galleries/` - 获取图集列表
- `GET /api/gallery/galleries/{id}/` - 获取图集详情
- `GET /api/gallery/galleries/{id}/images/` - 获取图集内图片列表

**Admin配置**:

```python
# gallery/admin.py

from django.contrib import admin
from .models import Gallery, GalleryImage


class GalleryImageInline(admin.TabularInline):
    model = GalleryImage
    extra = 0
    fields = ['image', 'title', 'description', 'date', 'tags', 'display_order']


@admin.register(Gallery)
class GalleryAdmin(admin.ModelAdmin):
    list_display = ['title', 'image_count', 'is_active', 'display_order', 'created_at']
    list_filter = ['is_active', 'tags']
    search_fields = ['title', 'description']
    inlines = [GalleryImageInline]


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['gallery', 'title', 'date', 'display_order', 'created_at']
    list_filter = ['gallery', 'date', 'tags']
    search_fields = ['title', 'description']
```

**实施步骤**:
1. 创建 `gallery` 应用
2. 定义数据模型
3. 创建序列化器
4. 实现API视图
5. 配置Admin后台
6. 配置URL路由
7. 执行数据库迁移
8. 配置媒体文件服务

---

#### 3.1.2 直播纪事模块

**需求说明**:
- 支持直播日历视图（按月展示）
- 支持直播档案详情展示
- 支持完整回放视频播放
- 支持歌切列表（当日演唱歌曲）
- 支持直播截图回顾
- 支持弹幕词云分析

**数据模型设计**:

```python
# livestream/models.py

from django.db import models


class Livestream(models.Model):
    """直播记录模型"""
    title = models.CharField(max_length=500, verbose_name="直播标题")
    summary = models.TextField(blank=True, verbose_name="直播摘要")
    cover_image = models.ImageField(
        upload_to='livestream/covers/%Y/%m/',
        blank=True,
        verbose_name="封面图片"
    )
    start_time = models.DateTimeField(verbose_name="开始时间")
    end_time = models.DateTimeField(verbose_name="结束时间")
    duration = models.DurationField(blank=True, null=True, verbose_name="时长")
    view_count = models.IntegerField(default=0, verbose_name="观看人数")
    danmaku_count = models.IntegerField(default=0, verbose_name="弹幕数量")
    danmaku_cloud_image = models.ImageField(
        upload_to='livestream/danmaku_clouds/',
        blank=True,
        verbose_name="弹幕词云图片"
    )
    platform = models.CharField(
        max_length=50,
        default='bilibili',
        verbose_name="平台"
    )
    is_active = models.BooleanField(default=True, verbose_name="是否有效")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "直播记录"
        verbose_name_plural = "直播记录"
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['start_time']),
        ]

    def __str__(self):
        return f"{self.title} - {self.start_time.strftime('%Y-%m-%d')}"

    @property
    def formatted_duration(self):
        """格式化时长"""
        if self.duration:
            total_seconds = int(self.duration.total_seconds())
            hours = total_seconds // 3600
            minutes = (total_seconds % 3600) // 60
            if hours > 0:
                return f"{hours}小时{minutes}分钟"
            return f"{minutes}分钟"
        return ""


class LivestreamRecording(models.Model):
    """直播录像模型"""
    livestream = models.ForeignKey(
        Livestream,
        on_delete=models.CASCADE,
        related_name='recordings',
        verbose_name="所属直播"
    )
    title = models.CharField(max_length=500, verbose_name="录像标题")
    video_url = models.URLField(max_length=500, verbose_name="视频URL")
    platform_video_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="平台视频ID"
    )
    duration = models.DurationField(blank=True, null=True, verbose_name="时长")
    display_order = models.IntegerField(default=0, verbose_name="显示顺序")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "直播录像"
        verbose_name_plural = "直播录像"
        ordering = ['display_order', 'created_at']

    def __str__(self):
        return self.title


class LivestreamSongCut(models.Model):
    """直播歌切模型"""
    livestream = models.ForeignKey(
        Livestream,
        on_delete=models.CASCADE,
        related_name='song_cuts',
        verbose_name="所属直播"
    )
    song_name = models.CharField(max_length=200, verbose_name="歌曲名称")
    original_artist = models.CharField(max_length=200, blank=True, verbose_name="原唱")
    video_url = models.URLField(max_length=500, verbose_name="视频URL")
    timestamp = models.CharField(max_length=50, blank=True, verbose_name="时间戳")
    display_order = models.IntegerField(default=0, verbose_name="显示顺序")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "直播歌切"
        verbose_name_plural = "直播歌切"
        ordering = ['display_order', 'created_at']

    def __str__(self):
        return self.song_name


class LivestreamScreenshot(models.Model):
    """直播截图模型"""
    livestream = models.ForeignKey(
        Livestream,
        on_delete=models.CASCADE,
        related_name='screenshots',
        verbose_name="所属直播"
    )
    image = models.ImageField(
        upload_to='livestream/screenshots/%Y/%m/',
        verbose_name="截图图片"
    )
    title = models.CharField(max_length=200, blank=True, verbose_name="截图标题")
    timestamp = models.CharField(max_length=50, blank=True, verbose_name="时间戳")
    display_order = models.IntegerField(default=0, verbose_name="显示顺序")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "直播截图"
        verbose_name_plural = "直播截图"
        ordering = ['display_order', 'created_at']

    def __str__(self):
        return f"{self.livestream.title} - {self.title or self.id}"
```

**API接口设计**:

```python
# livestream/api/views.py

from rest_framework import generics
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.utils import timezone
from datetime import datetime
from core.responses import success_response, error_response
from .serializers import (
    LivestreamSerializer,
    LivestreamDetailSerializer,
)
from .models import Livestream


class LivestreamListView(generics.ListAPIView):
    """直播列表"""
    serializer_class = LivestreamSerializer

    def get_queryset(self):
        year = self.request.query_params.get("year")
        month = self.request.query_params.get("month")

        queryset = Livestream.objects.filter(is_active=True)

        if year and month:
            # 按月筛选
            queryset = queryset.filter(
                start_time__year=int(year),
                start_time__month=int(month)
            )
        elif year:
            # 按年筛选
            queryset = queryset.filter(start_time__year=int(year))

        return queryset.order_by('-start_time')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)


class LivestreamDetailView(generics.RetrieveAPIView):
    """直播详情"""
    queryset = Livestream.objects.all()
    serializer_class = LivestreamDetailSerializer


@api_view(['GET'])
def LivestreamCalendarView(request):
    """直播日历视图"""
    year = int(request.query_params.get("year", timezone.now().year))
    month = int(request.query_params.get("month", timezone.now().month))

    try:
        livestreams = Livestream.objects.filter(
            start_time__year=year,
            start_time__month=month,
            is_active=True
        ).order_by('start_time')

        # 按日期分组
        calendar_data = {}
        for livestream in livestreams:
            date = livestream.start_time.strftime('%Y-%m-%d')
            if date not in calendar_data:
                calendar_data[date] = []
            calendar_data[date].append(LivestreamSerializer(livestream).data)

        return success_response(data={
            'year': year,
            'month': month,
            'dates': calendar_data
        })
    except Exception as e:
        return error_response(message=str(e))
```

**API端点**:

- `GET /api/livestream/livestreams/` - 获取直播列表
- `GET /api/livestream/livestreams/{id}/` - 获取直播详情
- `GET /api/livestream/calendar/` - 获取直播日历

**Admin配置**:

```python
# livestream/admin.py

from django.contrib import admin
from .models import Livestream, LivestreamRecording, LivestreamSongCut, LivestreamScreenshot


class LivestreamRecordingInline(admin.TabularInline):
    model = LivestreamRecording
    extra = 0
    fields = ['title', 'video_url', 'duration', 'display_order']


class LivestreamSongCutInline(admin.TabularInline):
    model = LivestreamSongCut
    extra = 0
    fields = ['song_name', 'original_artist', 'video_url', 'timestamp', 'display_order']


class LivestreamScreenshotInline(admin.TabularInline):
    model = LivestreamScreenshot
    extra = 0
    fields = ['image', 'title', 'timestamp', 'display_order']


@admin.register(Livestream)
class LivestreamAdmin(admin.ModelAdmin):
    list_display = ['title', 'start_time', 'end_time', 'view_count', 'is_active']
    list_filter = ['is_active', 'platform', 'start_time']
    search_fields = ['title', 'summary']
    date_hierarchy = 'start_time'
    inlines = [LivestreamRecordingInline, LivestreamSongCutInline, LivestreamScreenshotInline]


@admin.register(LivestreamRecording)
class LivestreamRecordingAdmin(admin.ModelAdmin):
    list_display = ['livestream', 'title', 'duration', 'display_order']
    list_filter = ['livestream']


@admin.register(LivestreamSongCut)
class LivestreamSongCutAdmin(admin.ModelAdmin):
    list_display = ['livestream', 'song_name', 'original_artist', 'display_order']
    list_filter = ['livestream']
    search_fields = ['song_name', 'original_artist']


@admin.register(LivestreamScreenshot)
class LivestreamScreenshotAdmin(admin.ModelAdmin):
    list_display = ['livestream', 'title', 'timestamp', 'display_order']
    list_filter = ['livestream']
```

**实施步骤**:
1. 创建 `livestream` 应用
2. 定义数据模型
3. 创建序列化器
4. 实现API视图
5. 配置Admin后台
6. 配置URL路由
7. 执行数据库迁移
8. 配置媒体文件服务

---

### 3.2 中优先级适配（增强功能）

#### 3.2.1 关于页面模块

**需求说明**:
- 展示艺人个人信息（生日、星座、栖息地、爱好）
- 展示声线特色（戏韵、治愈、张力、灵动）
- 展示成长里程碑时间线
- 展示社交媒体链接（Bilibili、微博、网易云音乐）

**数据模型设计**:

```python
# site_settings/models.py (扩展现有模型)

class SiteSettings(models.Model):
    """网站设置模型"""
    favicon = models.ImageField(
        upload_to='settings/',
        blank=True,
        null=True,
        verbose_name="网站图标"
    )
    # 新增字段
    artist_name = models.CharField(max_length=100, blank=True, verbose_name="艺人名称")
    artist_avatar = models.ImageField(
        upload_to='settings/',
        blank=True,
        null=True,
        verbose_name="艺人头像"
    )
    artist_birthday = models.DateField(blank=True, null=True, verbose_name="艺人生日")
    artist_constellation = models.CharField(max_length=50, blank=True, verbose_name="星座")
    artist_location = models.CharField(max_length=200, blank=True, verbose_name="栖息地")
    artist_hobbies = models.JSONField(default=list, verbose_name="爱好")
    artist_voice_features = models.JSONField(default=list, verbose_name="声线特色")

    # 社交媒体链接
    bilibili_url = models.URLField(max_length=500, blank=True, verbose_name="B站链接")
    weibo_url = models.URLField(max_length=500, blank=True, verbose_name="微博链接")
    netease_music_url = models.URLField(max_length=500, blank=True, verbose_name="网易云音乐链接")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "网站设置"
        verbose_name_plural = "网站设置"

    def __str__(self):
        return "网站设置"


class Milestone(models.Model):
    """里程碑模型"""
    year = models.IntegerField(verbose_name="年份")
    title = models.CharField(max_length=200, verbose_name="里程碑标题")
    description = models.TextField(verbose_name="里程碑描述")
    display_order = models.IntegerField(default=0, verbose_name="显示顺序")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "里程碑"
        verbose_name_plural = "里程碑"
        ordering = ['display_order', 'year']

    def __str__(self):
        return f"{self.year} - {self.title}"
```

**API接口设计**:

```python
# site_settings/api/views.py (扩展现有视图)

from rest_framework.generics import ListAPIView
from core.responses import success_response
from .serializers import MilestoneSerializer
from .models import Milestone


class MilestoneListView(ListAPIView):
    """里程碑列表"""
    serializer_class = MilestoneSerializer

    def get_queryset(self):
        return Milestone.objects.all().order_by('display_order', 'year')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)
```

**API端点**:

- `GET /api/site-settings/settings/` - 获取网站设置（已存在，需扩展）
- `GET /api/site-settings/milestones/` - 获取里程碑列表（新增）

**实施步骤**:
1. 扩展 `SiteSettings` 模型
2. 创建 `Milestone` 模型
3. 创建 `MilestoneSerializer`
4. 扩展 `SiteSettingsSerializer`
5. 实现 `MilestoneListView`
6. 配置Admin后台
7. 配置URL路由
8. 执行数据库迁移

---

#### 3.2.2 原创作品模块

**需求说明**:
- 展示精选原创作品（3首）
- 展示作品档案库列表（29首）
- 支持随机播放功能
- 集成网易云音乐播放器

**数据模型设计**:

```python
# site_settings/models.py (扩展现有模型)

class OriginalWork(models.Model):
    """原创作品模型"""
    title = models.CharField(max_length=200, verbose_name="作品标题")
    artist = models.CharField(max_length=200, verbose_name="艺人")
    release_date = models.DateField(verbose_name="发布日期")
    description = models.TextField(blank=True, verbose_name="作品描述")
    cover_image = models.ImageField(
        upload_to='originals/covers/',
        blank=True,
        verbose_name="封面图片"
    )
    netease_music_id = models.CharField(
        max_length=100,
        blank=True,
        verbose_name="网易云音乐ID"
    )
    video_url = models.URLField(
        max_length=500,
        blank=True,
        verbose_name="视频链接"
    )
    is_featured = models.BooleanField(default=False, verbose_name="是否精选")
    display_order = models.IntegerField(default=0, verbose_name="显示顺序")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "原创作品"
        verbose_name_plural = "原创作品"
        ordering = ['-is_featured', 'display_order', '-release_date']

    def __str__(self):
        return self.title
```

**API接口设计**:

```python
# site_settings/api/views.py (扩展现有视图)

from rest_framework.generics import ListAPIView
from rest_framework.decorators import api_view
from core.responses import success_response
from .serializers import OriginalWorkSerializer
from .models import OriginalWork


class OriginalWorkListView(ListAPIView):
    """原创作品列表"""
    serializer_class = OriginalWorkSerializer

    def get_queryset(self):
        is_featured = self.request.query_params.get("featured")
        queryset = OriginalWork.objects.all()

        if is_featured is not None:
            queryset = queryset.filter(is_featured=is_featured.lower() == 'true')

        return queryset.order_by('-is_featured', 'display_order', '-release_date')

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        return success_response(data=serializer.data)


@api_view(['GET'])
def RandomOriginalWorkView(request):
    """随机原创作品"""
    import random
    works = OriginalWork.objects.all()
    if works:
        random_work = random.choice(works)
        serializer = OriginalWorkSerializer(random_work)
        return success_response(data=serializer.data)
    return success_response(data=None)
```

**API端点**:

- `GET /api/site-settings/originals/` - 获取原创作品列表
- `GET /api/site-settings/originals/random/` - 获取随机原创作品

**实施步骤**:
1. 创建 `OriginalWork` 模型
2. 创建 `OriginalWorkSerializer`
3. 实现 `OriginalWorkListView`
4. 实现 `RandomOriginalWorkView`
5. 配置Admin后台
6. 配置URL路由
7. 执行数据库迁移

---

### 3.3 低优先级适配（高级功能）

#### 3.3.1 数据分析增强模块

**需求说明**:
- 全站粉丝增长趋势（总量、净增）
- 单一投稿深度分析（播放、点赞、弹幕时序数据）
- 稿件对比实验室（多维度对比表格）
- 增长关联性实验室（视频播放与粉丝增长相关性）

**数据模型扩展**:

```python
# data_analytics/models.py (扩展现有模型)

class AccountData(models.Model):
    """账号数据模型"""
    platform = models.CharField(max_length=50, verbose_name="平台")
    account_id = models.CharField(max_length=100, verbose_name="账号ID")
    account_name = models.CharField(max_length=200, verbose_name="账号名称")
    total_followers = models.IntegerField(default=0, verbose_name="总粉丝数")
    crawl_time = models.DateTimeField(verbose_name="爬取时间")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "账号数据"
        verbose_name_plural = "账号数据"
        ordering = ['-crawl_time']
        indexes = [
            models.Index(fields=['platform', 'account_id']),
            models.Index(fields=['crawl_time']),
        ]

    def __str__(self):
        return f"{self.account_name} - {self.crawl_time.strftime('%Y-%m-%d %H:%M')}"


class VideoMetrics(models.Model):
    """视频指标模型"""
    work_static = models.ForeignKey(
        WorkStatic,
        on_delete=models.CASCADE,
        related_name='metrics',
        verbose_name="作品"
    )
    view_count = models.IntegerField(default=0, verbose_name="播放量")
    like_count = models.IntegerField(default=0, verbose_name="点赞数")
    comment_count = models.IntegerField(default=0, verbose_name="评论数")
    share_count = models.IntegerField(default=0, verbose_name="分享数")
    favorite_count = models.IntegerField(default=0, verbose_name="收藏数")
    danmaku_count = models.IntegerField(default=0, verbose_name="弹幕数")
    coin_count = models.IntegerField(default=0, verbose_name="投币数")
    crawl_time = models.DateTimeField(verbose_name="爬取时间")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "视频指标"
        verbose_name_plural = "视频指标"
        ordering = ['-crawl_time']
        indexes = [
            models.Index(fields=['work_static', 'crawl_time']),
        ]

    def __str__(self):
        return f"{self.work_static.title} - {self.crawl_time.strftime('%Y-%m-%d %H:%M')}"
```

**API接口设计**:

```python
# data_analytics/api/views.py (扩展现有视图)

from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.db.models import Sum, Avg
from core.responses import success_response, error_response
from .models import AccountData, VideoMetrics, WorkStatic
from .serializers import AccountDataSerializer, VideoMetricsSerializer


@api_view(['GET'])
def AccountGrowthTrendView(request):
    """账号增长趋势"""
    platform = request.query_params.get("platform", "bilibili")
    account_id = request.query_params.get("account_id")
    granularity = request.query_params.get("granularity", "DAY")  # HOUR, DAY, MONTH
    days = int(request.query_params.get("days", 30))

    try:
        from django.utils import timezone
        from datetime import timedelta

        end_time = timezone.now()
        start_time = end_time - timedelta(days=days)

        queryset = AccountData.objects.filter(
            platform=platform,
            crawl_time__gte=start_time,
            crawl_time__lte=end_time
        )

        if account_id:
            queryset = queryset.filter(account_id=account_id)

        queryset = queryset.order_by('crawl_time')

        serializer = AccountDataSerializer(queryset, many=True)

        # 计算增长数据
        data = []
        prev_followers = None
        for item in serializer.data:
            delta = 0
            if prev_followers is not None:
                delta = item['total_followers'] - prev_followers
            data.append({
                'time': item['crawl_time'],
                'value': item['total_followers'],
                'delta': delta
            })
            prev_followers = item['total_followers']

        return success_response(data=data)
    except Exception as e:
        return error_response(message=str(e))


@api_view(['GET'])
def VideoDetailTrendView(request, platform, work_id):
    """视频详情趋势"""
    granularity = request.query_params.get("granularity", "DAY")
    days = int(request.query_params.get("days", 30))

    try:
        from django.utils import timezone
        from datetime import timedelta

        end_time = timezone.now()
        start_time = end_time - timedelta(days=days)

        work = WorkStatic.objects.get(platform=platform, work_id=work_id)

        queryset = VideoMetrics.objects.filter(
            work_static=work,
            crawl_time__gte=start_time,
            crawl_time__lte=end_time
        ).order_by('crawl_time')

        serializer = VideoMetricsSerializer(queryset, many=True)

        # 转换为前端需要的格式
        data = {
            'views': [],
            'likes': [],
            'danmaku': [],
        }

        for item in serializer.data:
            time = item['crawl_time']
            data['views'].append({
                'time': time,
                'value': item['view_count'],
                'delta': 0  # 需要计算增量
            })
            data['likes'].append({
                'time': time,
                'value': item['like_count'],
                'delta': 0
            })
            data['danmaku'].append({
                'time': time,
                'value': item['danmaku_count'],
                'delta': 0
            })

        return success_response(data=data)
    except WorkStatic.DoesNotExist:
        return error_response(message="作品不存在", status_code=404)
    except Exception as e:
        return error_response(message=str(e))


@api_view(['GET'])
def VideoComparisonView(request):
    """视频对比"""
    platform = request.query_params.get("platform", "bilibili")
    work_ids = request.query_params.get("work_ids", "").split(",")

    try:
        works = WorkStatic.objects.filter(
            platform=platform,
            work_id__in=work_ids
        )

        comparison_data = []
        for work in works:
            # 获取最新指标
            latest_metrics = VideoMetrics.objects.filter(
                work_static=work
            ).order_by('-crawl_time').first()

            comparison_data.append({
                'id': work.work_id,
                'title': work.title,
                'publish_time': work.publish_time,
                'views': latest_metrics.view_count if latest_metrics else 0,
                'likes': latest_metrics.like_count if latest_metrics else 0,
                'danmaku': latest_metrics.danmaku_count if latest_metrics else 0,
            })

        return success_response(data=comparison_data)
    except Exception as e:
        return error_response(message=str(e))


@api_view(['GET'])
def GrowthCorrelationView(request):
    """增长关联性分析"""
    platform = request.query_params.get("platform", "bilibili")
    work_id = request.query_params.get("work_id")
    granularity = request.query_params.get("granularity", "DAY")
    days = int(request.query_params.get("days", 30))

    try:
        from django.utils import timezone
        from datetime import timedelta

        end_time = timezone.now()
        start_time = end_time - timedelta(days=days)

        work = WorkStatic.objects.get(platform=platform, work_id=work_id)

        # 获取视频指标
        video_metrics = VideoMetrics.objects.filter(
            work_static=work,
            crawl_time__gte=start_time,
            crawl_time__lte=end_time
        ).order_by('crawl_time')

        # 获取账号数据
        account_data = AccountData.objects.filter(
            platform=platform,
            crawl_time__gte=start_time,
            crawl_time__lte=end_time
        ).order_by('crawl_time')

        # 计算关联数据
        correlation_data = []
        # 这里需要根据时间对齐数据，简化处理

        return success_response(data=correlation_data)
    except Exception as e:
        return error_response(message=str(e))
```

**API端点**:

- `GET /api/data-analytics/accounts/trend/` - 账号增长趋势
- `GET /api/data-analytics/videos/{platform}/{work_id}/trend/` - 视频详情趋势
- `GET /api/data-analytics/videos/comparison/` - 视频对比
- `GET /api/data-analytics/correlation/` - 增长关联性分析

**实施步骤**:
1. 创建 `AccountData` 模型
2. 创建 `VideoMetrics` 模型
3. 创建序列化器
4. 实现API视图
5. 配置Admin后台
6. 配置URL路由
7. 执行数据库迁移
8. 配置爬虫任务（如果需要）

---

#### 3.3.2 月度记录模块

**需求说明**:
- 年度投稿时间线可视化
- 蛇形月度布局（1-6月左到右，7-12月右到左）
- 月度详情视图
- 投稿记录卡片展示

**API接口设计**:

```python
# song_management/api/views.py (扩展现有视图)

from rest_framework.decorators import api_view
from core.responses import success_response, error_response
from ..models import SongRecord
from ..serializers import SongRecordSerializer


@api_view(['GET'])
def MonthlyRecordsView(request):
    """月度投稿记录"""
    year = int(request.query_params.get("year", 2025))
    month = int(request.query_params.get("month", 1))

    try:
        from django.utils import timezone
        from datetime import datetime

        # 获取指定年月的记录
        start_date = datetime(year, month, 1)
        if month == 12:
            end_date = datetime(year + 1, 1, 1)
        else:
            end_date = datetime(year, month + 1, 1)

        records = SongRecord.objects.filter(
            performed_at__gte=start_date,
            performed_at__lt=end_date
        ).order_by('performed_at')

        serializer = SongRecordSerializer(records, many=True)

        # 按日期分组
        daily_records = {}
        for record in serializer.data:
            date = record['performed_at'].split('T')[0]
            if date not in daily_records:
                daily_records[date] = []
            daily_records[date].append(record)

        return success_response(data={
            'year': year,
            'month': month,
            'dates': daily_records
        })
    except Exception as e:
        return error_response(message=str(e))


@api_view(['GET'])
def YearlyTimelineView(request):
    """年度时间线"""
    year = int(request.query_params.get("year", 2025))

    try:
        from django.db.models import Count
        from datetime import datetime

        # 获取全年每个月的活跃天数
        monthly_data = {}
        for month in range(1, 13):
            start_date = datetime(year, month, 1)
            if month == 12:
                end_date = datetime(year + 1, 1, 1)
            else:
                end_date = datetime(year, month + 1, 1)

            # 获取该月有记录的日期
            dates = SongRecord.objects.filter(
                performed_at__gte=start_date,
                performed_at__lt=end_date
            ).values_list('performed_at__date', flat=True).distinct()

            monthly_data[month] = {
                'active_days': len(dates),
                'dates': [d.strftime('%Y-%m-%d') for d in dates]
            }

        return success_response(data={
            'year': year,
            'months': monthly_data
        })
    except Exception as e:
        return error_response(message=str(e))
```

**API端点**:

- `GET /api/songs/records/monthly/` - 月度投稿记录
- `GET /api/songs/records/yearly-timeline/` - 年度时间线

**实施步骤**:
1. 在 `song_management` 应用中扩展API视图
2. 配置URL路由
3. 测试API接口

---

## 四、URL路由配置

### 4.1 主路由配置更新

```python
# xxm_fans_home/urls.py

urlpatterns = [
    # 现有路由
    path('api/', include('song_management.urls')),
    path('api/data-analytics/', include('data_analytics.urls')),
    path('api/site-settings/', include('site_settings.urls')),
    path('api/recommendation/', include('site_settings.urls')),
    path('api/fansDIY/', include('fansDIY.urls')),
    path('api/youyou/', include('songlist.urls')),
    path('api/bingjie/', include('songlist.urls')),
    path('api/songlist/', include('songlist.urls')),

    # 新增路由
    path('api/gallery/', include('gallery.urls')),
    path('api/livestream/', include('livestream.urls')),

    path('admin/', admin.site.urls),
    # ... 其他路由
]
```

---

## 五、实施计划

### 5.1 第一阶段（高优先级）

**目标**: 实现核心功能（图集、直播纪事）

**任务清单**:
- [ ] 创建 `gallery` 应用
- [ ] 创建 `livestream` 应用
- [ ] 定义数据模型
- [ ] 创建序列化器
- [ ] 实现API视图
- [ ] 配置Admin后台
- [ ] 配置URL路由
- [ ] 执行数据库迁移
- [ ] 配置媒体文件服务
- [ ] API测试

**预计时间**: 3-5天

### 5.2 第二阶段（中优先级）

**目标**: 实现增强功能（关于页面、原创作品）

**任务清单**:
- [ ] 扩展 `SiteSettings` 模型
- [ ] 创建 `Milestone` 模型
- [ ] 创建 `OriginalWork` 模型
- [ ] 创建序列化器
- [ ] 实现API视图
- [ ] 配置Admin后台
- [ ] 配置URL路由
- [ ] 执行数据库迁移
- [ ] API测试

**预计时间**: 2-3天

### 5.3 第三阶段（低优先级）

**目标**: 实现高级功能（数据分析增强、月度记录）

**任务清单**:
- [ ] 创建 `AccountData` 模型
- [ ] 创建 `VideoMetrics` 模型
- [ ] 创建序列化器
- [ ] 实现API视图
- [ ] 扩展 `song_management` API
- [ ] 配置Admin后台
- [ ] 配置URL路由
- [ ] 执行数据库迁移
- [ ] 配置爬虫任务（如果需要）
- [ ] API测试

**预计时间**: 3-5天

---

## 六、数据迁移策略

### 6.1 图集数据迁移

```python
# gallery/migrations/0002_initial_data.py

from django.db import migrations

def create_initial_galleries(apps, schema_editor):
    Gallery = apps.get_model('gallery', 'Gallery')

    # 创建示例图集
    galleries_data = [
        {
            'title': '演唱会现场',
            'description': '2024年演唱会现场照片',
            'tags': ['演唱会', '现场', '2024'],
            'is_active': True,
            'display_order': 1,
        },
        {
            'title': '日常生活',
            'description': '日常生活记录',
            'tags': ['日常', '生活'],
            'is_active': True,
            'display_order': 2,
        },
    ]

    for data in galleries_data:
        Gallery.objects.create(**data)


class Migration(migrations.Migration):
    dependencies = [
        ('gallery', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_galleries),
    ]
```

### 6.2 直播数据迁移

```python
# livestream/migrations/0002_initial_data.py

from django.db import migrations
from django.utils import timezone

def create_initial_livestreams(apps, schema_editor):
    Livestream = apps.get_model('livestream', 'Livestream')

    # 创建示例直播记录
    livestreams_data = [
        {
            'title': '2025年1月直播',
            'summary': '新年第一场直播',
            'start_time': timezone.datetime(2025, 1, 15, 20, 0, tzinfo=timezone.utc),
            'end_time': timezone.datetime(2025, 1, 15, 23, 30, tzinfo=timezone.utc),
            'view_count': 10000,
            'danmaku_count': 5000,
            'platform': 'bilibili',
            'is_active': True,
        },
    ]

    for data in livestreams_data:
        Livestream.objects.create(**data)


class Migration(migrations.Migration):
    dependencies = [
        ('livestream', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(create_initial_livestreams),
    ]
```

---

## 七、测试策略

### 7.1 API测试

使用 Django REST Framework 的测试框架创建测试用例：

```python
# gallery/tests.py

from django.test import TestCase
from rest_framework.test import APIClient
from .models import Gallery, GalleryImage


class GalleryAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.gallery = Gallery.objects.create(
            title="测试图集",
            description="测试描述",
            tags=["测试"]
        )

    def test_get_galleries(self):
        response = self.client.get('/api/gallery/galleries/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['data']), 1)

    def test_get_gallery_detail(self):
        response = self.client.get(f'/api/gallery/galleries/{self.gallery.id}/')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['data']['title'], '测试图集')
```

### 7.2 集成测试

```python
# tests/integration_test.py

from django.test import TestCase
from rest_framework.test import APIClient


class FrontendIntegrationTestCase(TestCase):
    def test_frontend_api_compatibility(self):
        """测试前端API兼容性"""
        client = APIClient()

        # 测试图集API
        response = client.get('/api/gallery/galleries/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('code', response.data)
        self.assertIn('data', response.data)

        # 测试直播API
        response = client.get('/api/livestream/livestreams/')
        self.assertEqual(response.status_code, 200)
        self.assertIn('code', response.data)
        self.assertIn('data', response.data)
```

---

## 八、性能优化建议

### 8.1 数据库优化

1. **添加索引**: 为常用查询字段添加索引
2. **查询优化**: 使用 `select_related` 和 `prefetch_related` 减少查询次数
3. **分页优化**: 使用 Django REST Framework 的分页类

### 8.2 缓存优化

1. **Redis缓存**: 对热点数据进行缓存
2. **查询缓存**: 缓存复杂查询结果
3. **CDN缓存**: 对静态资源使用CDN

### 8.3 图片优化

1. **图片压缩**: 使用 Pillow 压缩图片
2. **懒加载**: 前端实现图片懒加载
3. **缩略图**: 生成不同尺寸的缩略图

---

## 九、安全性考虑

### 9.1 文件上传安全

1. **文件类型验证**: 只允许特定类型的文件上传
2. **文件大小限制**: 限制上传文件大小
3. **文件名处理**: 避免文件名冲突和安全问题

### 9.2 API安全

1. **认证授权**: 对敏感API添加认证
2. **速率限制**: 防止API滥用
3. **输入验证**: 对所有输入进行验证

### 9.3 数据安全

1. **SQL注入防护**: 使用 ORM 避免SQL注入
2. **XSS防护**: 对用户输入进行转义
3. **CSRF防护**: 使用 Django 的 CSRF 保护

---

## 十、部署注意事项

### 10.1 环境变量

```bash
# env/backend.env

# 新增配置
DJANGO_MAX_UPLOAD_SIZE=10485760  # 10MB
DJANGO_ALLOWED_IMAGE_TYPES=jpg,jpeg,png,webp
DJANGO_GALLERY_MAX_IMAGES=1000
DJANGO_LIVESTREAM_MAX_RECORDINGS=20
```

### 10.2 Nginx配置更新

```nginx
# infra/nginx/xxm_nginx.conf

# 新增媒体文件路径
location /media/gallery/ {
    alias /home/yifeianyi/Desktop/xxm_fans_home/media/gallery/;
    expires 30d;
}

location /media/livestream/ {
    alias /home/yifeianyi/Desktop/xxm_fans_home/media/livestream/;
    expires 30d;
}

location /media/originals/ {
    alias /home/yifeianyi/Desktop/xxm_fans_home/media/originals/;
    expires 30d;
}
```

### 10.3 数据库备份

```bash
# 备份脚本
python manage.py dumpdata gallery livestream site_settings > backup_$(date +%Y%m%d).json
```

---

## 十一、维护计划

### 11.1 日常维护

1. **数据清理**: 定期清理无效数据
2. **日志监控**: 监控API错误日志
3. **性能监控**: 监控API响应时间

### 11.2 数据更新

1. **图集更新**: 定期更新图集内容
2. **直播数据**: 定期同步直播数据
3. **原创作品**: 定期添加新作品

### 11.3 功能迭代

1. **用户反馈**: 收集用户反馈
2. **功能优化**: 根据反馈优化功能
3. **性能优化**: 持续优化性能

---

## 十二、总结

本适配方案详细说明了前端 V2 大版本更新后，后端需要进行的所有适配工作。主要内容包括：

1. **新增2个应用**: `gallery`（图集管理）、`livestream`（直播纪事）
2. **扩展现有应用**: `site_settings`（关于页面、原创作品）、`data_analytics`（数据分析增强）、`song_management`（月度记录）
3. **新增数据模型**: Gallery, GalleryImage, Livestream, LivestreamRecording, LivestreamSongCut, LivestreamScreenshot, Milestone, OriginalWork, AccountData, VideoMetrics
4. **新增API接口**: 约20个新接口
5. **扩展Admin后台**: 为所有新模型配置Admin界面

按照本方案实施，后端将完全支持前端 V2 的所有新功能，为用户提供更丰富的内容和更好的用户体验。

---

**附录**

### A. 前端API文档参考

- `/home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_frontend/doc/API_doc.md`
- `/home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_frontend/doc/feature_migration_report.md`

### B. 后端现有API文档

- `/home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend/doc/API文档.md`

### C. 项目结构文档

- `/home/yifeianyi/Desktop/xxm_fans_home/IFLOW.md`

---

**文档版本历史**

| 版本 | 日期 | 作者 | 说明 |
|------|------|------|------|
| 1.0 | 2026-01-19 | iFlow CLI | 初始版本 |