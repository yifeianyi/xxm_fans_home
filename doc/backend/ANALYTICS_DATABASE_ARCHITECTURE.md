# 数据分析数据库架构设计文档

## 文档信息

- **创建日期**: 2026-01-19
- **版本**: 1.0
- **作者**: iFlow CLI
- **状态**: 待实施

---

## 一、概述

本文档详细说明了数据分析模块的数据库架构设计，包括数据库选型、数据量估算、性能优化策略和实施计划。

### 背景

前端 V2 版本新增了数据分析页面，需要支持：
- 全站粉丝增长趋势（总量、净增）
- 单一投稿深度分析（播放、点赞、弹幕时序数据）
- 稿件对比实验室（多维度对比表格）
- 增长关联性实验室（视频播放与粉丝增长相关性）

爬虫每小时爬取数据并保存为JSON文件，需要决策是否入库以及数据库架构。

---

## 二、数据量分析

### 2.1 数据来源

1. **作品指标数据**（WorkMetricsHour）
   - 爬取频率：每小时一次
   - 跟踪作品数：假设 100-300 个
   - 年数据量：365天 × 24小时 × 100-300作品 = **876,000 - 2,628,000条/年**

2. **账号数据**（AccountData，新增）
   - 爬取频率：每小时一次
   - 跟踪账号数：假设 10-30 个
   - 年数据量：365天 × 24小时 × 10-30账号 = **87,600 - 262,800条/年**

3. **视频指标数据**（VideoMetrics，新增）
   - 爬取频率：每小时一次
   - 跟踪视频数：假设 50-100 个
   - 年数据量：365天 × 24小时 × 50-100视频 = **438,000 - 876,000条/年**

4. **其他数据**（CrawlSession、WorkStatic等）
   - 年数据量：**约 10,000 - 50,000条/年**

### 2.2 总数据量估算

| 数据类型 | 年数据量（保守） | 年数据量（乐观） |
|---------|----------------|----------------|
| WorkMetricsHour | 876,000 | 2,628,000 |
| AccountData | 87,600 | 262,800 |
| VideoMetrics | 438,000 | 876,000 |
| 其他数据 | 10,000 | 50,000 |
| **总计** | **1,411,600** | **3,816,800** |

**结论**：后续一年的爬虫数据预计在 **200w-300w条** 范围内。

---

## 三、数据库选型分析

### 3.1 是否需要入库？

**答案：需要入库**

**原因**：

1. **前端查询需求**
   - 时间序列查询（按小时/天/月粒度）
   - 数据聚合计算（增长趋势、极值、相关性）
   - 多维度筛选（平台、账号、时间范围）
   - 实时响应（用户切换时间粒度）

2. **JSON文件的局限性**
   - ❌ 无法高效查询（需要遍历所有文件）
   - ❌ 无法进行聚合计算
   - ❌ 无法支持复杂筛选条件
   - ❌ 无法支持分页
   - ❌ 无法支持实时查询

3. **现有架构**
   - 项目已有 `data_analytics` 应用
   - 已有 `WorkMetricsHour` 模型（已入库）
   - 已有 `WorkStatic`、`CrawlSession` 模型

### 3.2 SQLite性能分析

| 数据量 | 性能表现 | 适用场景 |
|--------|---------|---------|
| < 10万条 | 优秀 | 小型应用 |
| 10万-100万条 | 良好 | 中型应用 |
| 100万-500万条 | 一般 | 大型应用（需优化） |
| > 500万条 | 较差 | 不推荐 |

**200w-300w条数据的问题**：

1. **查询性能**
   - 简单查询：< 1秒
   - 复杂查询（JOIN、聚合）：3-5秒
   - 时间范围查询：可能超时

2. **写入性能**
   - 并发写入时可能出现锁等待
   - 大批量导入耗时增加

3. **文件大小**
   - 数据库文件可能达到 **2-5GB**
   - 备份和恢复时间长

4. **对主业务的影响**
   - 数据库文件增大影响主业务查询
   - 并发访问可能影响主业务性能

### 3.3 是否需要单独数据库？

**答案：需要单独数据库**

**原因**：

1. **性能隔离**
   - 数据分析查询不影响主业务性能
   - 可以独立优化数据库配置

2. **维护便利**
   - 独立备份和恢复
   - 独立的数据归档策略

3. **扩展性**
   - 未来可以迁移到专门的时序数据库
   - 可以独立进行性能优化

---

## 四、数据库架构设计

### 4.1 数据库配置

```python
# xxm_fans_home/settings.py

DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(DATA_DIR / 'db.sqlite3'),
        'OPTIONS': {
            'timeout': 20,
        },
    },
    # 数据分析专用数据库
    'analytics_db': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(DATA_DIR / 'analytics.sqlite3'),
        'OPTIONS': {
            'timeout': 30,  # 增加超时时间
            'journal_mode': 'WAL',  # 写前日志，提高并发
            'synchronous': 'NORMAL',  # 降低同步级别
            'cache_size': -64000,  # 64MB缓存
            'page_size': 4096,  # 4KB页大小
        },
    },
    'songlist_db': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': str(DATA_DIR / 'songlist.sqlite3'),
        'OPTIONS': {
            'timeout': 20,
        },
    }
}
```

### 4.2 数据库路由

```python
# data_analytics/routers.py

class AnalyticsRouter:
    """数据分析数据库路由"""

    analytics_apps = {'data_analytics'}

    def db_for_read(self, model, **hints):
        """读操作路由"""
        if model._meta.app_label in self.analytics_apps:
            return 'analytics_db'
        return None

    def db_for_write(self, model, **hints):
        """写操作路由"""
        if model._meta.app_label in self.analytics_apps:
            return 'analytics_db'
        return None

    def allow_relation(self, obj1, obj2, **hints):
        """允许跨数据库关系"""
        if (
            obj1._meta.app_label in self.analytics_apps or
            obj2._meta.app_label in self.analytics_apps
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """迁移路由"""
        if app_label in self.analytics_apps:
            return db == 'analytics_db'
        return None
```

### 4.3 路由配置

```python
# xxm_fans_home/settings.py

DATABASE_ROUTERS = [
    'data_analytics.routers.AnalyticsRouter',
]
```

---

## 五、数据模型设计

### 5.1 现有模型

#### WorkStatic（作品静态信息）

```python
class WorkStatic(models.Model):
    """作品静态信息表"""
    platform = models.CharField(max_length=50, verbose_name="平台")
    work_id = models.CharField(max_length=100, verbose_name="作品ID")
    title = models.CharField(max_length=500, verbose_name="标题")
    author = models.CharField(max_length=200, verbose_name="作者")
    publish_time = models.DateTimeField(verbose_name="发布时间")
    cover_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="封面URL")
    is_valid = models.BooleanField(default=True, verbose_name="投稿是否有效")

    class Meta:
        verbose_name = "作品静态信息"
        verbose_name_plural = "作品静态信息"
        unique_together = ("platform", "work_id")
        ordering = ['-publish_time']
        indexes = [
            models.Index(fields=['platform', 'work_id']),
            models.Index(fields=['publish_time']),
        ]
```

#### WorkMetricsHour（作品小时级指标）

```python
class WorkMetricsHour(models.Model):
    """作品小时级指标表"""
    platform = models.CharField(max_length=50, verbose_name="平台")
    work_id = models.CharField(max_length=100, verbose_name="作品ID")
    crawl_time = models.DateTimeField(verbose_name="爬取时间")
    view_count = models.IntegerField(default=0, verbose_name="播放数")
    like_count = models.IntegerField(default=0, verbose_name="点赞数")
    coin_count = models.IntegerField(default=0, verbose_name="投币数")
    favorite_count = models.IntegerField(default=0, verbose_name="收藏数")
    danmaku_count = models.IntegerField(default=0, verbose_name="弹幕数")
    comment_count = models.IntegerField(default=0, verbose_name="评论数")
    session_id = models.IntegerField(verbose_name="会话ID")
    ingest_time = models.DateTimeField(auto_now_add=True, verbose_name="入库时间")

    class Meta:
        verbose_name = "作品小时指标"
        verbose_name_plural = "作品小时指标"
        ordering = ['-crawl_time']
        indexes = [
            models.Index(fields=['platform', 'work_id']),
            models.Index(fields=['crawl_time']),
            models.Index(fields=['session_id']),
            # 优化后的索引
            models.Index(fields=['platform', 'crawl_time']),
            models.Index(fields=['work_id', 'crawl_time']),
        ]
```

#### CrawlSession（爬取会话）

```python
class CrawlSession(models.Model):
    """爬取会话表"""
    source = models.CharField(max_length=50, verbose_name="数据源")
    node_id = models.CharField(max_length=100, verbose_name="节点ID")
    start_time = models.DateTimeField(verbose_name="开始时间")
    end_time = models.DateTimeField(blank=True, null=True, verbose_name="结束时间")
    total_work_count = models.IntegerField(default=0, verbose_name="总作品数")
    success_count = models.IntegerField(default=0, verbose_name="成功数")
    fail_count = models.IntegerField(default=0, verbose_name="失败数")
    note = models.TextField(blank=True, null=True, verbose_name="备注")

    class Meta:
        verbose_name = "爬取会话"
        verbose_name_plural = "爬取会话"
        ordering = ['-start_time']
        indexes = [
            models.Index(fields=['source', 'node_id']),
            models.Index(fields=['start_time']),
        ]
```

### 5.2 新增模型

#### AccountData（账号数据）

```python
class AccountData(models.Model):
    """账号数据模型"""
    platform = models.CharField(max_length=50, verbose_name="平台")
    account_id = models.CharField(max_length=100, verbose_name="账号ID")
    account_name = models.CharField(max_length=200, verbose_name="账号名称")
    total_followers = models.IntegerField(default=0, verbose_name="总粉丝数")
    total_likes = models.IntegerField(default=0, verbose_name="总点赞数")
    total_views = models.IntegerField(default=0, verbose_name="总播放量")
    crawl_time = models.DateTimeField(verbose_name="爬取时间", db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "账号数据"
        verbose_name_plural = "账号数据"
        ordering = ['-crawl_time']
        unique_together = ("platform", "account_id", "crawl_time")
        indexes = [
            models.Index(fields=['platform', 'account_id']),
            models.Index(fields=['crawl_time']),
            models.Index(fields=['platform', 'crawl_time']),
        ]

    def __str__(self):
        return f"{self.account_name} - {self.crawl_time.strftime('%Y-%m-%d %H:%M')}"
```

#### VideoMetrics（视频指标）

```python
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
            models.Index(fields=['crawl_time']),
        ]

    def __str__(self):
        return f"{self.work_static.title} - {self.crawl_time.strftime('%Y-%m-%d %H:%M')}"
```

#### WorkStatic（扩展）

```python
class WorkStatic(models.Model):
    """作品静态信息表（扩展）"""
    platform = models.CharField(max_length=50, verbose_name="平台")
    work_id = models.CharField(max_length=100, verbose_name="作品ID")
    title = models.CharField(max_length=500, verbose_name="标题")
    author = models.CharField(max_length=200, verbose_name="作者")
    publish_time = models.DateTimeField(verbose_name="发布时间")
    cover_url = models.URLField(max_length=500, blank=True, null=True, verbose_name="封面URL")
    is_valid = models.BooleanField(default=True, verbose_name="投稿是否有效")

    # 新增：关联歌曲ID（手动维护外键）
    related_song_id = models.IntegerField(
        blank=True,
        null=True,
        verbose_name="关联歌曲ID",
        db_index=True
    )

    def get_related_song(self):
        """手动获取关联歌曲"""
        if self.related_song_id:
            from song_management.models import Song
            try:
                return Song.objects.using('default').get(id=self.related_song_id)
            except Song.DoesNotExist:
                return None
        return None

    class Meta:
        verbose_name = "作品静态信息"
        verbose_name_plural = "作品静态信息"
        unique_together = ("platform", "work_id")
        ordering = ['-publish_time']
        indexes = [
            models.Index(fields=['platform', 'work_id']),
            models.Index(fields=['publish_time']),
            models.Index(fields=['related_song_id']),
        ]
```

---

## 六、外键关联处理

由于跨数据库无法使用Django的外键，需要手动处理关联：

### 6.1 手动维护关联ID

```python
class WorkStatic(models.Model):
    # ... 字段定义
    related_song_id = models.IntegerField(blank=True, null=True)

    def get_related_song(self):
        """获取关联歌曲"""
        if self.related_song_id:
            from song_management.models import Song
            try:
                return Song.objects.using('default').get(id=self.related_song_id)
            except Song.DoesNotExist:
                return None
        return None

    def set_related_song(self, song):
        """设置关联歌曲"""
        if song:
            self.related_song_id = song.id
        else:
            self.related_song_id = None
```

### 6.2 批量关联查询

```python
def get_works_with_songs(work_ids):
    """批量获取作品及其关联歌曲"""
    works = WorkStatic.objects.filter(work_id__in=work_ids)

    song_ids = [w.related_song_id for w in works if w.related_song_id]
    songs = Song.objects.using('default').filter(id__in=song_ids)
    song_map = {s.id: s for s in songs}

    for work in works:
        work._related_song = song_map.get(work.related_song_id)

    return works
```

---

## 七、性能优化策略

### 7.1 数据库配置优化

```python
# xxm_fans_home/settings.py

ANALYTICS_DB_OPTIONS = {
    'timeout': 30,                    # 增加超时时间
    'journal_mode': 'WAL',            # 写前日志，提高并发
    'synchronous': 'NORMAL',          # 降低同步级别
    'cache_size': -64000,             # 64MB缓存
    'page_size': 4096,                # 4KB页大小
    'temp_store': 'MEMORY',           # 临时表使用内存
    'mmap_size': 268435456,           # 256MB内存映射
}
```

**优化说明**：
- **WAL模式**：允许读写并发，提高性能
- **NORMAL同步**：平衡性能和数据安全
- **大缓存**：减少磁盘I/O
- **内存映射**：提高大文件访问速度

### 7.2 索引优化

```python
class WorkMetricsHour(models.Model):
    # ... 字段定义

    class Meta:
        indexes = [
            # 基础索引
            models.Index(fields=['platform', 'work_id']),
            models.Index(fields=['crawl_time']),
            models.Index(fields=['session_id']),

            # 复合索引（优化常用查询）
            models.Index(fields=['platform', 'crawl_time']),
            models.Index(fields=['work_id', 'crawl_time']),
            models.Index(fields=['platform', 'work_id', 'crawl_time']),
        ]
```

### 7.3 查询优化

```python
# 使用values减少数据传输
def get_account_growth_trend(platform, account_id, days=30):
    """优化后的查询"""
    from django.db.models import Max, Min

    queryset = AccountData.objects.filter(
        platform=platform,
        account_id=account_id,
        crawl_time__gte=timezone.now() - timedelta(days=days)
    ).order_by('crawl_time')

    # 只查询需要的字段
    data = queryset.values('crawl_time', 'total_followers')

    return list(data)

# 使用select_related/prefetch_related
def get_work_with_metrics(work_id):
    """优化关联查询"""
    work = WorkStatic.objects.select_related().get(work_id=work_id)
    metrics = work.metrics.all()  # 已通过related_name优化

    return work, metrics

# 使用批量查询
def get_multiple_accounts_growth(account_ids, days=30):
    """批量查询多个账号"""
    cutoff_date = timezone.now() - timedelta(days=days)

    data = AccountData.objects.filter(
        account_id__in=account_ids,
        crawl_time__gte=cutoff_date
    ).values('account_id', 'crawl_time', 'total_followers')

    return list(data)
```

### 7.4 数据归档策略

```python
# data_analytics/management/commands/archive_old_data.py

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from data_analytics.models import WorkMetricsHour, AccountData
import json
import os

class Command(BaseCommand):
    help = '归档6个月前的数据'

    def handle(self, *args, **options):
        cutoff_date = timezone.now() - timedelta(days=180)

        # 归档WorkMetricsHour
        old_metrics = WorkMetricsHour.objects.filter(
            crawl_time__lt=cutoff_date
        )

        # 导出到JSON
        archive_dir = 'data/analytics_archive'
        os.makedirs(archive_dir, exist_ok=True)

        archive_file = f'{archive_dir}/metrics_{cutoff_date.strftime("%Y%m%d")}.json'
        with open(archive_file, 'w') as f:
            json.dump(list(old_metrics.values()), f)

        # 删除旧数据
        count = old_metrics.count()
        old_metrics.delete()

        self.stdout.write(f'已归档 {count} 条指标记录到 {archive_file}')

        # 归档AccountData
        old_accounts = AccountData.objects.filter(
            crawl_time__lt=cutoff_date
        )

        archive_file = f'{archive_dir}/accounts_{cutoff_date.strftime("%Y%m%d")}.json'
        with open(archive_file, 'w') as f:
            json.dump(list(old_accounts.values()), f)

        count = old_accounts.count()
        old_accounts.delete()

        self.stdout.write(f'已归档 {count} 条账号记录到 {archive_file}')
```

### 7.5 分页优化

```python
from rest_framework.pagination import PageNumberPagination

class AnalyticsPagination(PageNumberPagination):
    """数据分析专用分页"""
    page_size = 100
    page_size_query_param = 'page_size'
    max_page_size = 1000

    def get_paginated_response(self, data):
        return Response({
            'code': 200,
            'message': '获取成功',
            'data': {
                'total': self.page.paginator.count,
                'page': self.page.number,
                'page_size': self.get_page_size(self.request),
                'results': data
            }
        })
```

---

## 八、数据迁移策略

### 8.1 创建数据库

```bash
# 执行迁移
python manage.py migrate --database=analytics_db

# 只迁移data_analytics应用
python manage.py migrate data_analytics --database=analytics_db
```

### 8.2 数据导入脚本

```python
# data_analytics/management/commands/import_spider_data.py

from django.core.management.base import BaseCommand
from django.utils import timezone
import json
import os
from datetime import datetime

class Command(BaseCommand):
    help = '从JSON文件导入爬虫数据'

    def handle(self, *args, **options):
        # 查找最新的JSON文件
        spider_dir = 'data/spider/fans_count'
        json_files = []

        for root, dirs, files in os.walk(spider_dir):
            for file in files:
                if file.endswith('.json'):
                    json_files.append(os.path.join(root, file))

        if not json_files:
            self.stdout.write('没有找到JSON文件')
            return

        # 获取最新的文件
        latest_file = max(json_files, key=os.path.getmtime)

        with open(latest_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        # 导入账号数据
        from data_analytics.models import AccountData

        for account in data.get('accounts', []):
            AccountData.objects.create(
                platform='bilibili',
                account_id=str(account['uid']),
                account_name=account['name'],
                total_followers=account['follower'],
                crawl_time=datetime.strptime(
                    account['timestamp'],
                    '%Y-%m-%d %H:%M:%S'
                )
            )

        self.stdout.write(f'已导入数据到 analytics_db')
```

### 8.3 定时任务配置

```bash
# crontab -e

# 每小时导入爬虫数据
0 * * * * cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend && python manage.py import_spider_data

# 每月归档旧数据
0 0 1 * * cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend && python manage.py archive_old_data
```

---

## 九、维护策略

### 9.1 定期备份

```bash
#!/bin/bash
# scripts/backup_analytics_db.sh

BACKUP_DIR="data/backups/analytics"
DATE=$(date +%Y%m%d_%H%M%S)

# 创建备份目录
mkdir -p $BACKUP_DIR

# 备份数据库
cp data/analytics.sqlite3 $BACKUP_DIR/analytics_$DATE.sqlite3

# 压缩备份
gzip $BACKUP_DIR/analytics_$DATE.sqlite3

# 删除7天前的备份
find $BACKUP_DIR -name "analytics_*.sqlite3.gz" -mtime +7 -delete

echo "备份完成: analytics_$DATE.sqlite3.gz"
```

### 9.2 性能监控

```python
# data_analytics/middleware.py

import time
import logging

logger = logging.getLogger(__name__)

class AnalyticsQueryMiddleware:
    """数据分析查询监控中间件"""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path.startswith('/api/data-analytics/'):
            start_time = time.time()
            response = self.get_response(request)
            elapsed = time.time() - start_time

            if elapsed > 1.0:
                logger.warning(
                    f'Slow analytics query: {request.path} took {elapsed:.2f}s'
                )

            response['X-Analytics-Time'] = f'{elapsed:.3f}'
            return response

        return self.get_response(request)
```

### 9.3 数据清理

```python
# data_analytics/management/commands/cleanup_invalid_data.py

from django.core.management.base import BaseCommand

class Command(BaseCommand):
    help = '清理无效数据'

    def handle(self, *args, **options):
        from data_analytics.models import WorkMetricsHour

        # 删除没有对应作品的指标
        invalid_metrics = WorkMetricsHour.objects.filter(
            work_static__isnull=True
        )

        count = invalid_metrics.count()
        invalid_metrics.delete()

        self.stdout.write(f'已删除 {count} 条无效指标记录')
```

---

## 十、实施计划

### 10.1 第一阶段：数据库配置

**任务清单**：
- [ ] 修改 `settings.py` 添加 `analytics_db` 配置
- [ ] 创建 `data_analytics/routers.py` 数据库路由
- [ ] 配置 `DATABASE_ROUTERS`
- [ ] 执行数据库迁移

**预计时间**：1天

### 10.2 第二阶段：模型扩展

**任务清单**：
- [ ] 创建 `AccountData` 模型
- [ ] 创建 `VideoMetrics` 模型
- [ ] 扩展 `WorkStatic` 模型（添加 `related_song_id`）
- [ ] 优化索引配置
- [ ] 执行数据库迁移

**预计时间**：2天

### 10.3 第三阶段：API实现

**任务清单**：
- [ ] 实现账号增长趋势API
- [ ] 实现视频详情趋势API
- [ ] 实现视频对比API
- [ ] 实现增长关联性API
- [ ] 实现月度记录API
- [ ] 实现年度时间线API

**预计时间**：3天

### 10.4 第四阶段：数据导入

**任务清单**：
- [ ] 创建数据导入脚本
- [ ] 创建数据归档脚本
- [ ] 配置定时任务
- [ ] 测试数据导入

**预计时间**：2天

### 10.5 第五阶段：优化和监控

**任务清单**：
- [ ] 实现查询优化
- [ ] 实现分页优化
- [ ] 配置性能监控
- [ ] 配置定期备份
- [ ] 性能测试

**预计时间**：2天

**总计**：10天

---

## 十一、风险评估

### 11.1 性能风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| 查询超时 | 中 | 高 | 索引优化、查询优化、分页 |
| 写入锁等待 | 低 | 中 | WAL模式、异步写入 |
| 数据库文件过大 | 高 | 中 | 数据归档、定期清理 |

### 11.2 数据一致性风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| 跨库关联失败 | 中 | 中 | 手动维护关联ID、批量查询优化 |
| 数据导入失败 | 低 | 高 | 事务处理、错误日志、重试机制 |

### 11.3 维护风险

| 风险 | 概率 | 影响 | 缓解措施 |
|------|------|------|---------|
| 备份失败 | 低 | 高 | 定期测试备份、多副本备份 |
| 归档数据丢失 | 低 | 中 | 归档文件备份、归档日志 |

---

## 十二、总结

### 12.1 核心结论

1. **需要入库**：前端数据分析需求复杂，JSON文件无法满足
2. **需要单独数据库**：200w-300w条数据会影响主业务性能
3. **使用独立SQLite**：通过优化配置可以满足性能需求
4. **手动维护关联**：跨数据库无法使用外键，需要手动处理

### 12.2 关键技术点

1. **数据库路由**：使用Django数据库路由实现多数据库
2. **WAL模式**：提高并发性能
3. **索引优化**：复合索引优化常用查询
4. **数据归档**：定期归档旧数据控制数据量
5. **性能监控**：监控慢查询及时优化

### 12.3 后续优化方向

1. **时序数据库**：如果数据量继续增长，考虑迁移到InfluxDB
2. **缓存优化**：使用Redis缓存热点数据
3. **读写分离**：考虑使用主从数据库
4. **分布式存储**：考虑使用分布式数据库

---

## 附录

### A. 参考文档

- [Django数据库路由](https://docs.djangoproject.com/en/5.2/topics/db/multi-db/)
- [SQLite性能优化](https://www.sqlite.org/performance.html)
- [SQLite WAL模式](https://www.sqlite.org/wal.html)

### B. 相关文档

- `/home/yifeianyi/Desktop/xxm_fans_home/doc/backend/FRONTEND_V2_ADAPTER_PLAN.md`
- `/home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_frontend/doc/feature_directory_analysis_report.md`

### C. 数据库文件结构

```
data/
├── db.sqlite3              # 主数据库
├── analytics.sqlite3       # 数据分析数据库（新增）
├── songlist.sqlite3        # 歌单数据库
└── backups/
    └── analytics/
        └── analytics_20260119_120000.sqlite3.gz
```

---

**文档版本历史**

| 版本 | 日期 | 作者 | 说明 |
|------|------|------|------|
| 1.0 | 2026-01-19 | iFlow CLI | 初始版本 |