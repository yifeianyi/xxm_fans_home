# XXM Fans Home 数据库 ER 图

## 文档信息

- **创建日期**: 2026-01-21
- **文档版本**: 1.0
- **作者**: XXM Fans Home Team
- **适用项目**: XXM Fans Home (小满虫之家)

---

## 数据库架构概述

本项目采用**多数据库架构**，根据数据特性和访问模式将数据分散到不同的数据库文件中：

### 数据库分布

| 数据库 | 文件路径 | 用途 | 数据特性 |
|--------|----------|------|----------|
| **default** | `data/db.sqlite3` | 主数据库 | 业务数据（歌曲、演唱记录、二创作品等） |
| **songlist_db** | `data/songlist.sqlite3` | 模板化歌单数据库 | 静态数据（艺术家歌曲列表） |
| **analytics_db** | `data/analytics.sqlite3` | 数据分析数据库 | 时间序列数据（WorkMetricsHour） |

### 架构优势

1. **性能隔离**: 时间序列数据的写入不影响主数据库查询
2. **备份策略灵活**: 可针对不同数据采用不同备份策略
3. **迁移成本低**: 未来迁移只需迁移特定数据库文件
4. **维护简单**: 清理历史数据不影响主数据库

---

## ER 图（Mermaid 格式）

```mermaid
erDiagram
    %% ==================== 主数据库 (default) ====================

    %% 歌曲管理模块
    Song ||--o{ SongRecord : "has many"
    Song ||--o{ SongStyle : "has many"
    Song ||--o{ SongTag : "has many"
    Song ||--o{ Recommendation : "recommended in"
    Style ||--o{ SongStyle : "used in"
    Tag ||--o{ SongTag : "used in"

    %% 粉丝二创模块
    Collection ||--o{ Work : "contains"

    %% 网站设置模块
    SiteSettings ||--o{ Recommendation : "has many"
    Song ||--o{ Recommendation : "recommended in"

    %% ==================== 模板化歌单数据库 (songlist_db) ====================

    ArtistSong ||--o{ ArtistSiteSetting : "has settings"

    %% ==================== 数据分析数据库 (analytics_db) ====================

    CrawlSession ||--o{ WorkMetricsHour : "generates"

    %% ==================== 模型定义 ====================

    Song {
        int id PK
        string song_name "歌曲名称"
        string singer "歌手"
        date first_perform "首次演唱时间"
        date last_performed "最近演唱时间"
        int perform_count "演唱次数"
        string language "语言"
    }

    SongRecord {
        int id PK
        int song_id FK "歌曲ID"
        date performed_at "演唱时间"
        string url "视频链接"
        text notes "备注"
        string cover_url "封面URL"
    }

    Style {
        int id PK
        string name "曲风名称"
        text description "描述"
    }

    SongStyle {
        int id PK
        int song_id FK "歌曲ID"
        int style_id FK "曲风ID"
    }

    Tag {
        int id PK
        string name "标签名称"
        text description "描述"
    }

    SongTag {
        int id PK
        int song_id FK "歌曲ID"
        int tag_id FK "标签ID"
    }

    Collection {
        int id PK
        string name "合集名称"
        int works_count "作品数量"
        int display_order "显示顺序"
        int position "位置"
        datetime created_at "创建时间"
        datetime updated_at "更新时间"
    }

    Work {
        int id PK
        int collection_id FK "合集ID"
        string title "作品标题"
        string cover_url "封面图片地址"
        string view_url "观看链接"
        string author "作者"
        text notes "备注"
        int display_order "显示顺序"
        int position "位置"
    }

    SiteSettings {
        int id PK
        image favicon "网站图标"
        datetime created_at "创建时间"
        datetime updated_at "更新时间"
    }

    Recommendation {
        int id PK
        text content "推荐语内容"
        boolean is_active "是否激活显示"
        datetime created_at "创建时间"
        datetime updated_at "更新时间"
    }

    %% 模板化歌单模型（动态生成）
    ArtistSong {
        int id PK
        string song_name "歌曲名称"
        string singer "原唱歌手"
        string language "语言"
        string style "曲风"
        text note "备注"
    }

    ArtistSiteSetting {
        int id PK
        string photo_url "图片URL"
        int position "位置 (1:头像图标, 2:背景图片)"
    }

    %% 数据分析模型
    WorkStatic {
        int id PK
        string platform "平台 (bilibili, youtube, etc.)"
        string work_id "作品ID"
        string title "作品标题"
        string author "作者"
        string cover_url "封面URL"
        datetime created_at "创建时间"
        datetime updated_at "更新时间"
    }

    WorkMetricsHour {
        int id PK
        string platform "平台"
        string work_id "作品ID"
        datetime crawl_time "爬取时间"
        int view_count "观看数"
        int like_count "点赞数"
        int coin_count "投币数"
        int favorite_count "收藏数"
        int danmaku_count "弹幕数"
        int comment_count "评论数"
        int session_id FK "爬取会话ID"
        datetime ingest_time "入库时间"
    }

    CrawlSession {
        int id PK
        datetime start_time "开始时间"
        datetime end_time "结束时间"
        string status "状态 (running, completed, failed)"
        int works_count "爬取作品数"
        text error_message "错误信息"
    }
```

---

## 模型详细说明

### 1. 歌曲管理模块 (song_management)

#### 1.1 Song（歌曲）

**数据库**: default

**字段说明**:
- `id`: 主键
- `song_name`: 歌曲名称
- `singer`: 歌手
- `first_perform`: 首次演唱时间
- `last_performed`: 最近演唱时间
- `perform_count`: 演唱次数（自动计算）
- `language`: 语言

**索引**:
- `song_name`
- `singer`
- `language`

**关系**:
- 1:N SongRecord（一个歌曲有多个演唱记录）
- N:M Style（通过 SongStyle）
- N:M Tag（通过 SongTag）
- N:M Recommendation（推荐的歌曲）

**数据规模**: 约 1,400 条（静态数据）

---

#### 1.2 SongRecord（演唱记录）

**数据库**: default

**字段说明**:
- `id`: 主键
- `song_id`: 外键，关联 Song
- `performed_at`: 演唱时间
- `url`: 视频链接（B站 BV 号等）
- `notes`: 备注
- `cover_url`: 封面 URL

**索引**:
- `song_id`
- `performed_at`

**关系**:
- N:1 Song（多个演唱记录属于一个歌曲）

**数据规模**: 约 14,000 条（静态数据）

---

#### 1.3 Style（曲风）

**数据库**: default

**字段说明**:
- `id`: 主键
- `name`: 曲风名称（唯一）
- `description`: 描述

**关系**:
- 1:N SongStyle（一个曲风被多个歌曲使用）

**数据规模**: 约 20-50 条

---

#### 1.4 SongStyle（歌曲-曲风关联）

**数据库**: default

**字段说明**:
- `id`: 主键
- `song_id`: 外键，关联 Song
- `style_id`: 外键，关联 Style

**约束**:
- `(song_id, style_id)` 唯一

**关系**:
- N:1 Song
- N:1 Style

**数据规模**: 约 2,000-5,000 条

---

#### 1.5 Tag（标签）

**数据库**: default

**字段说明**:
- `id`: 主键
- `name`: 标签名称（唯一）
- `description`: 描述

**关系**:
- 1:N SongTag（一个标签被多个歌曲使用）

**数据规模**: 约 30-80 条

---

#### 1.6 SongTag（歌曲-标签关联）

**数据库**: default

**字段说明**:
- `id`: 主键
- `song_id`: 外键，关联 Song
- `tag_id`: 外键，关联 Tag

**约束**:
- `(song_id, tag_id)` 唯一

**关系**:
- N:1 Song
- N:1 Tag

**数据规模**: 约 3,000-8,000 条

---

### 2. 粉丝二创模块 (fansDIY)

#### 2.1 Collection（二创合集）

**数据库**: default

**字段说明**:
- `id`: 主键
- `name`: 合集名称
- `works_count`: 作品数量（自动计算）
- `display_order`: 显示顺序
- `position`: 位置
- `created_at`: 创建时间
- `updated_at`: 更新时间

**索引**:
- `position`
- `display_order`
- `created_at`

**关系**:
- 1:N Work（一个合集包含多个作品）

**数据规模**: 约 10-20 个

---

#### 2.2 Work（作品记录）

**数据库**: default

**字段说明**:
- `id`: 主键
- `collection_id`: 外键，关联 Collection
- `title`: 作品标题
- `cover_url`: 封面图片地址
- `view_url`: 观看链接
- `author`: 作者
- `notes`: 备注
- `display_order`: 显示顺序
- `position`: 位置

**索引**:
- `collection_id`
- `position`
- `display_order`

**关系**:
- N:1 Collection（多个作品属于一个合集）

**数据规模**: 约 100 条

---

### 3. 网站设置模块 (site_settings)

#### 3.1 SiteSettings（网站设置）

**数据库**: default

**字段说明**:
- `id`: 主键
- `favicon`: 网站图标（ImageField）
- `created_at`: 创建时间
- `updated_at`: 更新时间

**关系**:
- 1:N Recommendation

**数据规模**: 1 条（单例模式）

---

#### 3.2 Recommendation（推荐语）

**数据库**: default

**字段说明**:
- `id`: 主键
- `content`: 推荐语内容
- `is_active`: 是否激活显示
- `created_at`: 创建时间
- `updated_at`: 更新时间

**关系**:
- N:1 SiteSettings
- N:M Song（通过 ManyToManyField）

**数据规模**: 约 5-10 条

---

### 4. 模板化歌单模块 (songlist)

#### 4.1 ArtistSong（艺术家歌曲）

**数据库**: songlist_db

**说明**: 动态生成的模型，根据 `ARTIST_CONFIG` 配置创建

**字段说明**:
- `id`: 主键
- `song_name`: 歌曲名称
- `singer`: 原唱歌手
- `language`: 语言
- `style`: 曲风
- `note`: 备注

**当前配置**:
- `YouyouSong`: 乐游歌曲
- `BingjieSong`: 冰洁歌曲

**数据规模**: 每个艺术家约 50-100 首

---

#### 4.2 ArtistSiteSetting（艺术家网站设置）

**数据库**: songlist_db

**说明**: 动态生成的模型，根据 `ARTIST_CONFIG` 配置创建

**字段说明**:
- `id`: 主键
- `photo_url`: 图片 URL
- `position`: 位置（1: 头像图标, 2: 背景图片）

**当前配置**:
- `YouyouSiteSetting`: 乐游网站设置
- `BingjieSiteSetting`: 冰洁网站设置

**数据规模**: 每个艺术家约 2-5 条

---

### 5. 数据分析模块 (data_analytics)

#### 5.1 WorkStatic（作品静态信息）

**数据库**: analytics_db

**说明**: 存储作品的静态信息，用于"投稿时刻"页面展示

**字段说明**:
- `id`: 主键
- `platform`: 平台（bilibili, youtube, etc.）
- `work_id`: 作品 ID（如 BV 号）
- `title`: 作品标题
- `author`: 作者
- `cover_url`: 封面 URL
- `created_at`: 创建时间
- `updated_at`: 更新时间

**索引**:
- `platform`
- `work_id`
- `(platform, work_id)` 唯一

**数据规模**: 约 50 个作品（投稿时刻）

---

#### 5.2 WorkMetricsHour（作品小时级指标）

**数据库**: analytics_db

**说明**: 存储作品的小时级指标数据，用于"数据分析"页面展示

**字段说明**:
- `id`: 主键
- `platform`: 平台
- `work_id`: 作品 ID
- `crawl_time`: 爬取时间
- `view_count`: 观看数
- `like_count`: 点赞数
- `coin_count`: 投币数
- `favorite_count`: 收藏数
- `danmaku_count`: 弹幕数
- `comment_count`: 评论数
- `session_id`: 爬取会话 ID（外键）
- `ingest_time`: 入库时间

**索引**:
- `platform`
- `work_id`
- `crawl_time`
- `session_id`
- `(platform, work_id, crawl_time)` 唯一

**关系**:
- N:1 CrawlSession

**数据规模**: 约 2,628,000 条/年（300 作品 × 24 小时 × 365 天）

**写入频率**: 每小时 300 条

**查询特点**:
- 时间范围查询
- 数据聚合（SUM, AVG, MAX, MIN）
- 多维度筛选

---

#### 5.3 CrawlSession（爬取会话）

**数据库**: analytics_db

**说明**: 记录每次爬取任务的信息

**字段说明**:
- `id`: 主键
- `start_time`: 开始时间
- `end_time`: 结束时间
- `status`: 状态（running, completed, failed）
- `works_count`: 爬取作品数
- `error_message`: 错误信息

**关系**:
- 1:N WorkMetricsHour

**数据规模**: 约 8,760 条/年（365 天 × 24 小时）

---

## 数据规模汇总

### 主数据库 (default)

| 模型 | 数据量 | 年增长 | 存储空间 | 数据特性 |
|------|--------|--------|----------|----------|
| Song | 1,400 | 0 | ~700 KB | 静态数据 |
| SongRecord | 14,000 | 0 | ~7 MB | 静态数据 |
| Style | 20-50 | 0 | ~10 KB | 静态数据 |
| SongStyle | 2,000-5,000 | 0 | ~500 KB | 静态数据 |
| Tag | 30-80 | 0 | ~15 KB | 静态数据 |
| SongTag | 3,000-8,000 | 0 | ~1 MB | 静态数据 |
| Collection | 10-20 | 0 | ~5 KB | 静态数据 |
| Work | 100 | 0 | ~50 KB | 静态数据 |
| SiteSettings | 1 | 0 | ~5 KB | 静态数据 |
| Recommendation | 5-10 | 0 | ~10 KB | 静态数据 |
| **总计** | **~20,600** | **0** | **~9.3 MB** | **静态数据** |

### 模板化歌单数据库 (songlist_db)

| 模型 | 数据量 | 年增长 | 存储空间 | 数据特性 |
|------|--------|--------|----------|----------|
| ArtistSong | 100-200 | 0 | ~50 KB | 静态数据 |
| ArtistSiteSetting | 4-10 | 0 | ~5 KB | 静态数据 |
| **总计** | **~110** | **0** | **~60 KB** | **静态数据** |

### 数据分析数据库 (analytics_db)

| 模型 | 数据量 | 年增长 | 存储空间 | 数据特性 |
|------|--------|--------|----------|----------|
| WorkStatic | 50 | 0 | ~25 KB | 静态数据（投稿时刻） |
| WorkMetricsHour | 2,628,000 | 2,628,000 | ~600 MB | 时间序列数据（数据分析） |
| CrawlSession | 8,760 | 8,760 | ~5 MB | 时间序列数据 |
| **总计** | **~2,636,810** | **~2,636,760** | **~605 MB** | **时间序列数据** |

### 总体数据规模

| 数据库 | 数据量 | 年增长 | 存储空间 | 数据特性 |
|--------|--------|--------|----------|----------|
| default | ~20,600 | 0 | ~9.3 MB | 静态数据 |
| songlist_db | ~110 | 0 | ~60 KB | 静态数据 |
| analytics_db | ~2,636,810 | ~2,636,760 | ~605 MB | 时间序列数据 |
| **总计** | **~2,657,520** | **~2,636,760** | **~614 MB** | **混合数据** |

---

## 关键关系说明

### 1. 歌曲管理关系

```
Song (歌曲)
  ├── SongRecord (演唱记录) [1:N]
  ├── SongStyle (歌曲-曲风关联) [1:N]
  │   └── Style (曲风) [N:1]
  ├── SongTag (歌曲-标签关联) [1:N]
  │   └── Tag (标签) [N:1]
  └── Recommendation (推荐语) [N:M]
```

### 2. 粉丝二创关系

```
Collection (二创合集)
  └── Work (作品记录) [1:N]
```

### 3. 网站设置关系

```
SiteSettings (网站设置)
  └── Recommendation (推荐语) [1:N]
      └── Song (歌曲) [N:M]
```

### 4. 模板化歌单关系

```
ArtistSong (艺术家歌曲)
  └── ArtistSiteSetting (艺术家网站设置) [1:N]
```

### 5. 数据分析关系

```
WorkStatic (作品静态信息) [投稿时刻]
  └── (无直接关系)

CrawlSession (爬取会话)
  └── WorkMetricsHour (作品小时级指标) [1:N] [数据分析]
```

---

## 数据访问模式

### 读取模式

| 模块 | 操作 | 频率 | 响应要求 |
|------|------|------|----------|
| 歌曲管理 | 查询歌曲列表、演唱记录 | 高 | < 1 秒 |
| 粉丝二创 | 查询合集、作品 | 中 | < 1 秒 |
| 网站设置 | 查询推荐语、网站设置 | 高 | < 1 秒 |
| 模板化歌单 | 查询艺术家歌曲 | 中 | < 1 秒 |
| 数据分析 | 时间线展示、数据聚合 | 中高 | < 2 秒 |

### 写入模式

| 模块 | 操作 | 频率 | 数据量 | 时间要求 |
|------|------|------|--------|----------|
| 歌曲管理 | 添加歌曲、演唱记录 | 低 | 1-10 条 | 即时 |
| 粉丝二创 | 添加合集、作品 | 低 | 1-10 条 | 即时 |
| 网站设置 | 更新推荐语、网站设置 | 低 | 1 条 | 即时 |
| 模板化歌单 | 添加艺术家歌曲 | 低 | 1-10 条 | 即时 |
| 数据分析 | 批量插入指标数据 | 高 | 300 条/小时 | 5-10 分钟 |

---

## 性能优化建议

### 1. 索引优化

**主数据库 (default)**:
- Song: `song_name`, `singer`, `language`
- SongRecord: `song_id`, `performed_at`
- SongStyle: `(song_id, style_id)` 唯一索引
- SongTag: `(song_id, tag_id)` 唯一索引
- Collection: `position`, `display_order`, `created_at`
- Work: `collection_id`, `position`, `display_order`

**数据分析数据库 (analytics_db)**:
- WorkStatic: `platform`, `work_id`, `(platform, work_id)` 唯一索引
- WorkMetricsHour: `platform`, `work_id`, `crawl_time`, `session_id`, `(platform, work_id, crawl_time)` 唯一索引
- CrawlSession: `start_time`, `end_time`, `status`

### 2. 查询优化

**时间序列查询优化**:
- 使用 `crawl_time` 索引进行时间范围查询
- 使用批量查询减少数据库访问次数
- 使用聚合函数预计算常用指标

**关联查询优化**:
- 使用 `select_related` 减少 1:N 关系的查询次数
- 使用 `prefetch_related` 减少 N:M 关系的查询次数
- 避免跨数据库的关联查询

### 3. 写入优化

**批量插入优化**:
- 使用事务批量插入 WorkMetricsHour 数据
- 使用 `bulk_create` 方法批量插入
- 在非高峰期执行批量写入操作

**缓存优化**:
- 使用 Redis 缓存热门歌曲列表
- 使用 Redis 缓存推荐语
- 使用 Redis 缓存数据分析结果

---

## 未来扩展

### 1. 数据库迁移

当满足以下条件时，考虑迁移到 PostgreSQL + TimescaleDB：

- 数据库大小 > 10 GB
- 日活 > 1000 人
- 写入频率 > 10,000 条/小时
- 需要主从复制或读写分离
- 需要高级时间序列查询优化

### 2. 模型扩展

**可能的扩展模型**:
- `User`（用户模型）
- `Comment`（评论模型）
- `Like`（点赞模型）
- `Favorite`（收藏模型）
- `TimelineEvent`（时间线事件）
- `CalendarEvent`（日历事件）
- `GalleryImage`（图集图片）

### 3. 功能扩展

**可能的功能扩展**:
- 用户系统（登录、注册、个人中心）
- 社交功能（评论、点赞、收藏）
- 数据分析增强（更多维度、更长时间范围）
- 推荐系统（个性化推荐）
- 搜索功能（全文搜索）

---

## 附录

### A. Django settings.py 数据库配置

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / '../../data/db.sqlite3',
        'OPTIONS': {
            'timeout': 20,
            'check_same_thread': False,
        },
    },
    'songlist_db': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / '../../data/songlist.sqlite3',
        'OPTIONS': {
            'timeout': 20,
            'check_same_thread': False,
        },
    },
    'analytics_db': {
        'ENGINE': 'django.db.backends.sqlite3',
        'NAME': BASE_DIR / '../../data/analytics.sqlite3',
        'OPTIONS': {
            'timeout': 20,
            'check_same_thread': False,
        },
    },
}

# 数据库路由
DATABASE_ROUTERS = [
    'core.routers.DatabaseRouter',
]
```

### B. 数据库路由配置

```python
# core/routers.py

class DatabaseRouter:
    """数据库路由"""

    def db_for_read(self, model, **hints):
        """读操作路由"""
        if model._meta.app_label == 'songlist':
            return 'songlist_db'
        elif model._meta.app_label == 'data_analytics':
            return 'analytics_db'
        return 'default'

    def db_for_write(self, model, **hints):
        """写操作路由"""
        if model._meta.app_label == 'songlist':
            return 'songlist_db'
        elif model._meta.app_label == 'data_analytics':
            return 'analytics_db'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """关系路由"""
        if (
            obj1._state.db in ('default', 'songlist_db', 'analytics_db') and
            obj2._state.db in ('default', 'songlist_db', 'analytics_db')
        ):
            return True
        return None

    def allow_migrate(self, db, app_label, model_name=None, **hints):
        """迁移路由"""
        if app_label == 'songlist':
            return db == 'songlist_db'
        elif app_label == 'data_analytics':
            return db == 'analytics_db'
        return db == 'default'
```

### C. 模型数据库指定

```python
# data_analytics/models.py

class WorkMetricsHour(models.Model):
    """作品小时级指标"""

    class Meta:
        db_table = 'work_metrics_hour'
        app_label = 'data_analytics'
        managed = True

    # ... 字段定义 ...
```

---

## 更新日志

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0 | 2026-01-21 | 初始版本，基于当前项目需求创建 |

---

## 参考资料

- [Django Models 文档](https://docs.djangoproject.com/en/stable/topics/db/models/)
- [Django Database Routers 文档](https://docs.djangoproject.com/en/stable/topics/db/multi-db/)
- [SQLite3 文档](https://www.sqlite.org/docs.html)
- [PostgreSQL + TimescaleDB 文档](https://docs.timescale.com/)
- [DATABASE_MIGRATION_ANALYSIS.md](./DATABASE_MIGRATION_ANALYSIS.md)