# B站投稿数据爬虫

## 简介

定时捕获 B站投稿数据（播放数、弹幕数、评论数、点赞数、投币数、收藏数、转发数），支持小时级数据存储。

## 目录结构

```
spider/
├── run_views_crawler.py          # 主控脚本（入口）
└── README.md                     # 本文件

repo/xxm_fans_backend/tools/spider/
├── export_views.py               # 数据导出模块
├── crawl_views.py                # 核心爬虫模块
├── import_views.py               # 数据导入模块
└── utils/
    └── logger.py                 # 日志工具
```

## 使用方法

### 手动执行

```bash
# 进入项目目录
cd /home/yifeianyi/Desktop/xxm_fans_home

# 完整流程（导出 -> 爬取 -> 导入）
python spider/run_views_crawler.py --full

# 仅导出 views.json
python spider/run_views_crawler.py --export-only

# 仅爬取数据
python spider/run_views_crawler.py --crawl-only

# 仅导入数据（当前小时）
python spider/run_views_crawler.py --import-only

# 导入指定日期和小时的数据
python spider/run_views_crawler.py --import-only --date 2026-02-06 --hour 14
```

### 定时任务

```bash
# 激活定时任务
sudo systemctl enable --now infra/systemd/bilibili-views-crawler.timer

# 查看定时任务状态
systemctl list-timers --all | grep bilibili

# 手动触发
sudo systemctl start infra/systemd/bilibili-views-crawler.service
```

## 输出文件

### JSON 数据文件

```
data/spider/views/{year}/{month}/{day}/{date}-{hour}_views_data.json

示例:
data/spider/views/2026/02/06/2026-02-06-14_views_data.json
```

### SQLite 数据库

```
data/view_data.sqlite3
```

## 日志文件

```
logs/spider/views_crawler_YYYYMMDD.log    # 爬虫日志
logs/spider/views_import_YYYYMMDD.log     # 导入日志
logs/spider/run_views_crawler_YYYYMMDD.log # 主控脚本日志
```

## 配置说明

### 爬虫参数

- **请求间隔**: 0.2 - 0.5 秒（随机间隔，避免被反爬虫检测）
- **超时时间**: 10 秒
- **重试次数**: 3 次

### 数据表结构

#### work_metrics 表

| 字段 | 类型 | 说明 |
|------|------|------|
| platform | TEXT | 平台标识 |
| work_id | TEXT | 作品ID（BV号）|
| title | TEXT | 标题 |
| crawl_date | TEXT | 爬取日期 (YYYY-MM-DD) |
| crawl_hour | TEXT | 爬取小时 (HH) |
| crawl_time | TEXT | 爬取时间 (HH:MM:SS) |
| view_count | INTEGER | 播放数 |
| danmaku_count | INTEGER | 弹幕数 |
| comment_count | INTEGER | 评论数 |
| like_count | INTEGER | 点赞数 |
| coin_count | INTEGER | 投币数 |
| favorite_count | INTEGER | 收藏数 |
| share_count | INTEGER | 转发数 |

## 自动触发机制

当 `data_analytics_workstatic` 表有数据更新时，会自动触发 `views.json` 导出（防抖机制：10秒内只触发一次）。
