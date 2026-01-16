# B站粉丝数据Django Admin集成方案

## 需求分析

在Django Admin中方便查看B站粉丝数爬虫数据，无需SSH登录服务器查看JSON文件。

## 方案概述

提供两种实现方案：
1. **纯文件读取方案**（推荐）：不涉及数据库迁移，直接读取JSON文件
2. **数据库存储方案**：将数据存储到数据库，便于查询和统计

---

## 方案一：纯文件读取方案（推荐，无需数据库迁移）

### 1. 创建应用

```bash
cd repo/xxm_fans_backend
python manage.py startapp bilibili_fans
```

### 2. 创建数据模型（不迁移到数据库）

```python
# repo/xxm_fans_backend/bilibili_fans/models.py
from django.db import models
import json
import os
from datetime import datetime
from django.conf import settings

class BilibiliFansData:
    """B站粉丝数据模型（纯内存，不存储到数据库）"""
    
    # 数据文件路径
    DATA_DIR = os.path.join(settings.BASE_DIR, '../../data/spider/fans_count')
    
    def __init__(self, data_file, data):
        self.data_file = data_file
        self.update_time = data.get('update_time')
        self.accounts = data.get('accounts', [])
        
        # 解析文件名获取时间信息
        filename = os.path.basename(data_file)
        parts = filename.replace('b_fans_count_', '').replace('.json', '').split('-')
        if len(parts) >= 4:
            self.year = parts[0]
            self.month = parts[1]
            self.day = parts[2]
            self.hour = parts[3]
        else:
            self.year = ''
            self.month = ''
            self.day = ''
            self.hour = ''
        
        # 提取账号数据
        self.xiaoman_fans = None
        self.xiaoman_status = None
        self.xiaoxiaoman_fans = None
        self.xiaoxiaoman_status = None
        
        for account in self.accounts:
            if account.get('uid') == 37754047:  # 咻咻满
                self.xiaoman_fans = account.get('follower')
                self.xiaoman_status = account.get('status')
            elif account.get('uid') == 480116537:  # 咻小满
                self.xiaoxiaoman_fans = account.get('follower')
                self.xiaoxiaoman_status = account.get('status')
    
    @classmethod
    def get_all(cls, limit=100):
        """获取所有数据"""
        data_list = []
        
        if not os.path.exists(cls.DATA_DIR):
            return data_list
        
        # 遍历数据文件
        for year in sorted(os.listdir(cls.DATA_DIR), reverse=True):
            year_path = os.path.join(cls.DATA_DIR, year)
            if not os.path.isdir(year_path):
                continue
            
            for month in sorted(os.listdir(year_path), reverse=True):
                month_path = os.path.join(year_path, month)
                if not os.path.isdir(month_path):
                    continue
                
                for filename in sorted(os.listdir(month_path), reverse=True):
                    if not filename.endswith('.json'):
                        continue
                    
                    file_path = os.path.join(month_path, filename)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        data_list.append(cls(file_path, data))
                        
                        if len(data_list) >= limit:
                            return data_list
                            
                    except Exception as e:
                        print(f"Error loading {file_path}: {e}")
                        continue
        
        return data_list
    
    @classmethod
    def get_latest(cls):
        """获取最新数据"""
        all_data = cls.get_all(limit=1)
        return all_data[0] if all_data else None
    
    @classmethod
    def get_by_date(cls, year, month, day=None):
        """按日期获取数据"""
        data_list = []
        data_dir = os.path.join(cls.DATA_DIR, year, month)
        
        if not os.path.exists(data_dir):
            return data_list
        
        for filename in sorted(os.listdir(data_dir), reverse=True):
            if not filename.endswith('.json'):
                continue
            
            if day and day not in filename:
                continue
            
            file_path = os.path.join(data_dir, filename)
            
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                data_list.append(cls(file_path, data))
                
            except Exception as e:
                print(f"Error loading {file_path}: {e}")
                continue
        
        return data_list
```

### 3. 创建Admin视图（使用自定义视图）

```python
# repo/xxm_fans_backend/bilibili_fans/admin.py
from django.contrib import admin
from django.urls import path
from django.shortcuts import render
from django.http import JsonResponse
from .models import BilibiliFansData
import os

class BilibiliFansAdminSite(admin.AdminSite):
    """自定义Admin站点"""
    site_header = 'B站粉丝数据管理'
    site_title = 'B站粉丝数据'
    index_title = '首页'

bilibili_admin = BilibiliFansAdminSite(name='bilibili_admin')

@bilibili_admin.register_view('fans-data/', name='粉丝数据')
def fans_data_view(request):
    """粉丝数据列表视图"""
    page = int(request.GET.get('page', 1))
    per_page = 20
    year = request.GET.get('year')
    month = request.GET.get('month')
    
    # 获取数据
    if year and month:
        data_list = BilibiliFansData.get_by_date(year, month)
    else:
        data_list = BilibiliFansData.get_all()
    
    # 分页
    total = len(data_list)
    start = (page - 1) * per_page
    end = start + per_page
    page_data = data_list[start:end]
    
    # 获取可用的年月
    available_dates = []
    data_dir = BilibiliFansData.DATA_DIR
    if os.path.exists(data_dir):
        for year in sorted(os.listdir(data_dir), reverse=True):
            year_path = os.path.join(data_dir, year)
            if os.path.isdir(year_path):
                for month in sorted(os.listdir(year_path), reverse=True):
                    available_dates.append(f"{year}-{month}")
    
    context = {
        'data_list': page_data,
        'page': page,
        'total_pages': (total + per_page - 1) // per_page,
        'total': total,
        'year': year,
        'month': month,
        'available_dates': available_dates,
        'latest': BilibiliFansData.get_latest(),
    }
    
    return render(request, 'bilibili_fans/fans_data.html', context)

@bilibili_admin.register_view('api/latest/', name='最新数据API')
def latest_data_api(request):
    """最新数据API"""
    latest = BilibiliFansData.get_latest()
    
    if latest:
        data = {
            'update_time': latest.update_time,
            'xiaoman_fans': latest.xiaoman_fans,
            'xiaoxiaoman_fans': latest.xiaoxiaoman_fans,
            'xiaoman_status': latest.xiaoman_status,
            'xiaoxiaoman_status': latest.xiaoxiaoman_status,
        }
        return JsonResponse({'success': True, 'data': data})
    else:
        return JsonResponse({'success': False, 'message': '暂无数据'})
```

### 4. 创建模板

```html
<!-- repo/xxm_fans_backend/bilibili_fans/templates/bilibili_fans/fans_data.html -->
{% extends "admin/base_site.html" %}

{% load static %}

{% block content %}
<div id="content-main">
    <!-- 统计卡片 -->
    {% if latest %}
    <div class="module">
        <h2>最新数据统计</h2>
        <table>
            <thead>
                <tr>
                    <th>更新时间</th>
                    <th>咻咻满粉丝数</th>
                    <th>咻小满粉丝数</th>
                    <th>数据文件</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>{{ latest.update_time }}</td>
                    <td style="color: #1890ff; font-weight: bold; font-size: 16px;">
                        {{ latest.xiaoman_fans|default:"-"|intcomma }}
                    </td>
                    <td style="color: #52c41a; font-weight: bold; font-size: 16px;">
                        {{ latest.xiaoxiaoman_fans|default:"-"|intcomma }}
                    </td>
                    <td>{{ latest.data_file|slice:"-30:" }}</td>
                </tr>
            </tbody>
        </table>
    </div>
    {% endif %}
    
    <!-- 筛选器 -->
    <div class="module">
        <h2>数据筛选</h2>
        <form method="get" style="margin: 10px 0;">
            <label>
                年月：
                <select name="year" onchange="this.form.submit()">
                    <option value="">全部</option>
                    {% for date in available_dates %}
                    {% with year_month=date|split:"-" %}
                    <option value="{{ year_month.0 }}" {% if year == year_month.0 %}selected{% endif %}>
                        {{ year_month.0 }}年
                    </option>
                    {% endwith %}
                    {% endfor %}
                </select>
            </label>
            {% if year %}
            <label>
                月份：
                <select name="month" onchange="this.form.submit()">
                    <option value="">全部</option>
                    {% for date in available_dates %}
                    {% with year_month=date|split:"-" %}
                    {% if year_month.0 == year %}
                    <option value="{{ year_month.1 }}" {% if month == year_month.1 %}selected{% endif %}>
                        {{ year_month.1 }}月
                    </option>
                    {% endif %}
                    {% endwith %}
                    {% endfor %}
                </select>
            </label>
            {% endif %}
        </form>
    </div>
    
    <!-- 数据列表 -->
    <div class="module">
        <h2>历史数据 (共 {{ total }} 条)</h2>
        <table>
            <thead>
                <tr>
                    <th>更新时间</th>
                    <th>咻咻满粉丝数</th>
                    <th>咻小满粉丝数</th>
                    <th>咻咻满状态</th>
                    <th>咻小满状态</th>
                    <th>数据文件</th>
                </tr>
            </thead>
            <tbody>
                {% for item in data_list %}
                <tr>
                    <td>{{ item.update_time }}</td>
                    <td style="color: #1890ff; font-weight: bold;">
                        {{ item.xiaoman_fans|default:"-"|intcomma }}
                    </td>
                    <td style="color: #52c41a; font-weight: bold;">
                        {{ item.xiaoxiaoman_fans|default:"-"|intcomma }}
                    </td>
                    <td>
                        <span class="status-{{ item.xiaoman_status }}">
                            {{ item.xiaoman_status }}
                        </span>
                    </td>
                    <td>
                        <span class="status-{{ item.xiaoxiaoman_status }}">
                            {{ item.xiaoxiaoman_status }}
                        </span>
                    </td>
                    <td>{{ item.data_file|slice:"-40:" }}</td>
                </tr>
                {% empty %}
                <tr>
                    <td colspan="6" style="text-align: center;">暂无数据</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        
        <!-- 分页 -->
        {% if total_pages > 1 %}
        <div class="pagination" style="margin-top: 10px;">
            <span>第 {{ page }} / {{ total_pages }} 页</span>
            {% if page > 1 %}
            <a href="?page={{ page|add:-1 }}{% if year %}&year={{ year }}{% endif %}{% if month %}&month={{ month }}{% endif %}">上一页</a>
            {% endif %}
            {% if page < total_pages %}
            <a href="?page={{ page|add:1 }}{% if year %}&year={{ year }}{% endif %}{% if month %}&month={{ month }}{% endif %}">下一页</a>
            {% endif %}
        </div>
        {% endif %}
    </div>
</div>

<style>
.status-success {
    color: #52c41a;
    font-weight: bold;
}
.status-error, .status-failed {
    color: #ff4d4f;
    font-weight: bold;
}
.pagination {
    text-align: center;
}
.pagination a {
    margin: 0 5px;
    padding: 5px 10px;
    background: #1890ff;
    color: white;
    text-decoration: none;
    border-radius: 3px;
}
.pagination a:hover {
    background: #40a9ff;
}
</style>
{% endblock %}
```

### 5. 配置URL

```python
# repo/xxm_fans_backend/bilibili_fans/urls.py
from django.urls import path
from .admin import bilibili_admin

urlpatterns = [
    path('bilibili-admin/', bilibili_admin.urls),
]
```

### 6. 主URL配置

```python
# repo/xxm_fans_backend/xxm_fans_home/urls.py
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('bilibili-admin/', include('bilibili_fans.urls')),
]
```

### 7. 注册应用

```python
# repo/xxm_fans_backend/xxm_fans_home/settings.py

INSTALLED_APPS = [
    # ... 其他应用
    'bilibili_fans',
]
```

### 8. 创建模板目录

```bash
mkdir -p repo/xxm_fans_backend/bilibili_fans/templates/bilibili_fans
```

### 9. 添加模板过滤器

```python
# repo/xxm_fans_backend/bilibili_fans/templatetags/__init__.py
# 空文件

# repo/xxm_fans_backend/bilibili_fans/templatetags/custom_filters.py
from django import template

register = template.Library()

@register.filter
def split(value, delimiter):
    return value.split(delimiter)

@register.filter
def add(value, arg):
    return int(value) + int(arg)
```

### 10. 使用方法

访问: `http://your-domain/bilibili-admin/`

无需任何数据库迁移，直接从JSON文件读取数据并展示。

---

## 方案二：数据库存储方案（需要数据库迁移）

#### 1. 创建应用

```bash
cd repo/xxm_fans_backend
python manage.py startapp bilibili_fans
```

#### 2. 数据模型设计

```python
# repo/xxm_fans_backend/bilibili_fans/models.py
from django.db import models
import json
import os
from django.conf import settings

class BilibiliFansData(models.Model):
    """B站粉丝数据模型（只读，从JSON文件加载）"""
    
    # 数据文件路径
    DATA_DIR = os.path.join(settings.BASE_DIR, '../../data/spider/fans_count')
    
    # 主要字段
    update_time = models.DateTimeField(verbose_name="更新时间")
    year = models.CharField(max_length=4, verbose_name="年份")
    month = models.CharField(max_length=2, verbose_name="月份")
    hour = models.CharField(max_length=2, verbose_name="小时")
    data_file = models.CharField(max_length=255, verbose_name="数据文件")
    
    # 咻咻满数据
    xiaoman_uid = models.IntegerField(default=37754047, verbose_name="咻咻满UID")
    xiaoman_name = models.CharField(max_length=50, default="咻咻满", verbose_name="咻咻满")
    xiaoman_fans = models.BigIntegerField(null=True, blank=True, verbose_name="咻咻满粉丝数")
    xiaoman_status = models.CharField(max_length=20, verbose_name="咻咻满状态")
    
    # 咻小满数据
    xiaoxiaoman_uid = models.IntegerField(default=480116537, verbose_name="咻小满UID")
    xiaoxiaoman_name = models.CharField(max_length=50, default="咻小满", verbose_name="咻小满")
    xiaoxiaoman_fans = models.BigIntegerField(null=True, blank=True, verbose_name="咻小满粉丝数")
    xiaoxiaoman_status = models.CharField(max_length=20, verbose_name="咻小满状态")
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="记录创建时间")
    
    class Meta:
        db_table = 'bilibili_fans_data'
        verbose_name = 'B站粉丝数据'
        verbose_name_plural = 'B站粉丝数据'
        ordering = ['-update_time']
        indexes = [
            models.Index(fields=['-update_time']),
            models.Index(fields=['year', 'month']),
        ]
    
    def __str__(self):
        return f"{self.update_time.strftime('%Y-%m-%d %H:00')} - 咻咻满:{self.xiaoman_fans:,} 咻小满:{self.xiaoxiaoman_fans:,}"
    
    @classmethod
    def load_from_files(cls):
        """从JSON文件加载数据到数据库"""
        data_dir = cls.DATA_DIR
        
        if not os.path.exists(data_dir):
            return 0
        
        loaded_count = 0
        
        # 遍历年月目录
        for year in os.listdir(data_dir):
            year_path = os.path.join(data_dir, year)
            if not os.path.isdir(year_path):
                continue
            
            for month in os.listdir(year_path):
                month_path = os.path.join(year_path, month)
                if not os.path.isdir(month_path):
                    continue
                
                # 遍历JSON文件
                for filename in os.listdir(month_path):
                    if not filename.endswith('.json'):
                        continue
                    
                    file_path = os.path.join(month_path, filename)
                    
                    try:
                        with open(file_path, 'r', encoding='utf-8') as f:
                            data = json.load(f)
                        
                        # 解析文件名获取时间信息
                        # 格式: b_fans_count_YYYY-MM-DD-HH.json
                        parts = filename.replace('b_fans_count_', '').replace('.json', '').split('-')
                        if len(parts) >= 4:
                            file_year, file_month, file_day, file_hour = parts[:4]
                        else:
                            continue
                        
                        # 查找或创建记录
                        obj, created = cls.objects.update_or_create(
                            data_file=file_path,
                            defaults={
                                'update_time': data.get('update_time'),
                                'year': file_year,
                                'month': file_month,
                                'hour': file_hour,
                            }
                        )
                        
                        # 更新账号数据
                        accounts = data.get('accounts', [])
                        for account in accounts:
                            if account.get('uid') == 37754047:  # 咻咻满
                                obj.xiaoman_fans = account.get('follower')
                                obj.xiaoman_status = account.get('status')
                            elif account.get('uid') == 480116537:  # 咻小满
                                obj.xiaoxiaoman_fans = account.get('follower')
                                obj.xiaoxiaoman_status = account.get('status')
                        
                        obj.save()
                        loaded_count += 1
                        
                    except Exception as e:
                        print(f"Error loading {file_path}: {e}")
                        continue
        
        return loaded_count
    
    @classmethod
    def sync_latest(cls):
        """同步最新的数据文件"""
        data_dir = cls.DATA_DIR
        latest_file = None
        latest_time = None
        
        if not os.path.exists(data_dir):
            return 0
        
        # 查找最新的文件
        for year in os.listdir(data_dir):
            year_path = os.path.join(data_dir, year)
            if not os.path.isdir(year_path):
                continue
            
            for month in os.listdir(year_path):
                month_path = os.path.join(year_path, month)
                if not os.path.isdir(month_path):
                    continue
                
                for filename in os.listdir(month_path):
                    if not filename.endswith('.json'):
                        continue
                    
                    file_path = os.path.join(month_path, filename)
                    file_mtime = os.path.getmtime(file_path)
                    
                    if latest_time is None or file_mtime > latest_time:
                        latest_time = file_mtime
                        latest_file = file_path
        
        if latest_file:
            # 加载最新文件
            try:
                with open(latest_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                
                parts = os.path.basename(latest_file).replace('b_fans_count_', '').replace('.json', '').split('-')
                if len(parts) >= 4:
                    file_year, file_month, file_day, file_hour = parts[:4]
                    
                    obj, created = cls.objects.update_or_create(
                        data_file=latest_file,
                        defaults={
                            'update_time': data.get('update_time'),
                            'year': file_year,
                            'month': file_month,
                            'hour': file_hour,
                        }
                    )
                    
                    accounts = data.get('accounts', [])
                    for account in accounts:
                        if account.get('uid') == 37754047:
                            obj.xiaoman_fans = account.get('follower')
                            obj.xiaoman_status = account.get('status')
                        elif account.get('uid') == 480116537:
                            obj.xiaoxiaoman_fans = account.get('follower')
                            obj.xiaoxiaoman_status = account.get('status')
                    
                    obj.save()
                    return 1
            except Exception as e:
                print(f"Error loading latest file: {e}")
        
        return 0
```

#### 3. Admin配置

```python
# repo/xxm_fans_backend/bilibili_fans/admin.py
from django.contrib import admin
from .models import BilibiliFansData
from django.utils.html import format_html
from django.db.models import Sum, Max

@admin.register(BilibiliFansData)
class BilibiliFansDataAdmin(admin.ModelAdmin):
    """B站粉丝数据Admin"""
    
    list_display = [
        'update_time',
        'xiaoman_fans_display',
        'xiaoxiaoman_fans_display',
        'xiaoman_status',
        'xiaoxiaoman_status',
        'data_file_short',
    ]
    
    list_filter = [
        'year',
        'month',
        'xiaoman_status',
        'xiaoxiaoman_status',
    ]
    
    search_fields = [
        'update_time',
        'data_file',
    ]
    
    date_hierarchy = 'update_time'
    
    readonly_fields = [
        'update_time',
        'year',
        'month',
        'hour',
        'data_file',
        'xiaoman_uid',
        'xiaoman_name',
        'xiaoman_fans',
        'xiaoman_status',
        'xiaoxiaoman_uid',
        'xiaoxiaoman_name',
        'xiaoxiaoman_fans',
        'xiaoxiaoman_status',
        'created_at',
    ]
    
    actions = ['sync_data']
    
    def has_add_permission(self, request):
        """禁止手动添加"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """只允许同步操作"""
        return True
    
    def has_delete_permission(self, request, obj=None):
        """允许删除"""
        return True
    
    def xiaoman_fans_display(self, obj):
        """咻咻满粉丝数显示"""
        if obj.xiaoman_fans:
            return format_html(
                '<span style="color: #1890ff; font-weight: bold;">{:,}</span>',
                obj.xiaoman_fans
            )
        return '-'
    xiaoman_fans_display.short_description = '咻咻满粉丝数'
    
    def xiaoxiaoman_fans_display(self, obj):
        """咻小满粉丝数显示"""
        if obj.xiaoxiaoman_fans:
            return format_html(
                '<span style="color: #52c41a; font-weight: bold;">{:,}</span>',
                obj.xiaoxiaoman_fans
            )
        return '-'
    xiaoxiaoman_fans_display.short_description = '咻小满粉丝数'
    
    def data_file_short(self, obj):
        """数据文件路径缩略显示"""
        if obj.data_file:
            return obj.data_file.split('/')[-1]
        return '-'
    data_file_short.short_description = '数据文件'
    
    def sync_data(self, request, queryset):
        """同步数据操作"""
        count = BilibiliFansData.sync_latest()
        self.message_user(request, f'已同步 {count} 条最新数据')
    sync_data.short_description = '同步最新数据'
    
    def changelist_view(self, request, extra_context=None):
        """自定义列表视图，显示统计信息"""
        response = super().changelist_view(request, extra_context)
        
        try:
            # 获取统计数据
            latest = BilibiliFansData.objects.first()
            total_count = BilibiliFansData.objects.count()
            
            extra_context = extra_context or {}
            extra_context.update({
                'latest_xiaoman_fans': latest.xiaoman_fans if latest else 0,
                'latest_xiaoxiaoman_fans': latest.xiaoxiaoman_fans if latest else 0,
                'latest_update_time': latest.update_time if latest else None,
                'total_count': total_count,
            })
        except:
            pass
        
        return response
```

#### 4. 注册应用

```python
# repo/xxm_fans_backend/xxm_fans_home/settings.py

INSTALLED_APPS = [
    # ... 其他应用
    'bilibili_fans',
]
```

#### 5. 数据库迁移

```bash
cd repo/xxm_fans_backend
python manage.py makemigrations bilibili_fans
python manage.py migrate bilibili_fans
```

#### 6. 创建管理命令

```python
# repo/xxm_fans_backend/bilibili_fans/management/commands/sync_bilibili_fans.py
from django.core.management.base import BaseCommand
from bilibili_fans.models import BilibiliFansData

class Command(BaseCommand):
    help = '同步B站粉丝数据'

    def add_arguments(self, parser):
        parser.add_argument(
            '--all',
            action='store_true',
            help='加载所有历史数据',
        )

    def handle(self, *args, **options):
        if options['all']:
            count = BilibiliFansData.load_from_files()
            self.stdout.write(self.style.SUCCESS(f'已加载 {count} 条历史数据'))
        else:
            count = BilibiliFansData.sync_latest()
            self.stdout.write(self.style.SUCCESS(f'已同步 {count} 条最新数据'))
```

### 方案二：集成到现有应用

如果不想创建新应用，可以集成到现有的 `site_settings` 应用中：

1. 在 `site_settings/models.py` 中添加模型
2. 在 `site_settings/admin.py` 中添加Admin配置
3. 使用相同的数据加载逻辑

## 使用方法

### 1. 首次加载数据

```bash
cd repo/xxm_fans_backend
python manage.py sync_bilibili_fans --all
```

### 2. 同步最新数据

```bash
python manage.py sync_bilibili_fans
```

### 3. 在Admin中查看

访问: `http://your-domain/admin/bilibili_fans/bilibilifansdata/`

### 4. 自动同步（可选）

在cron定时任务中添加同步命令：

```bash
# 每小时运行爬虫并同步数据
0 * * * * /home/yifeianyi/Desktop/xxm_fans_home/scripts/bilibili_fans_count_cron.sh && /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend/manage.py sync_bilibili_fans
```

## 优点

1. **无需SSH登录**: 直接在Admin后台查看数据
2. **可视化展示**: 列表展示、筛选、搜索、排序
3. **统计分析**: 可以进行粉丝数趋势分析
4. **操作便捷**: 一键同步最新数据
5. **数据持久化**: 数据存储在数据库中，查询速度快

## 注意事项

1. **数据库表**: 需要创建数据库表存储数据
2. **存储空间**: 长期运行会占用数据库空间，建议定期清理旧数据
3. **同步频率**: 可以根据需要调整同步频率
4. **数据一致性**: 确保爬虫数据文件格式稳定

## 扩展功能

### 1. 数据可视化图表

使用 `django-chartjs` 或 `plotly` 添加粉丝数趋势图。

### 2. 数据导出

添加导出Excel/CSV功能。

### 3. 告警通知

当粉丝数增长超过阈值时发送通知。

### 4. API接口

提供REST API接口供前端调用。

## 总结

推荐使用**方案一**（创建独立应用），这样职责清晰，便于维护和扩展。通过Admin后台可以方便地查看和管理B站粉丝数据，无需SSH登录服务器。