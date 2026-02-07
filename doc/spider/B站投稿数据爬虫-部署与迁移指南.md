# B站投稿数据爬虫 - 部署与迁移指南

本文档总结了 B站投稿数据爬虫系统的完整部署、数据库迁移和重新部署流程。

---

## 一、系统概述

### 1.1 架构图

```
┌─────────────────────────────────────────────────────────────────┐
│                     B站投稿数据爬虫系统                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   spider/                        repo/xxm_fans_backend/         │
│   ├── run_views_crawler.py  ───▶ tools/spider/                  │
│   │                              ├── export_views.py (导出)      │
│   │                              ├── crawl_views.py (爬取)       │
│   │                              ├── import_views.py (导入)      │
│   │                              └── utils/logger.py (日志)      │
│   │                                                             │
│   scripts/                                                      │
│   └── bilibili_views_cron.sh  (定时任务脚本)                     │
│                                                                 │
│   data/                                                         │
│   ├── spider/views.json          # 导出的作品列表                │
│   ├── spider/views/              # 按小时存储的爬取结果          │
│   │   └── 2026/02/06/2026-02-06-12_views_data.json              │
│   └── view_data.sqlite3          # SQLite数据库                 │
│                                                                 │
│   logs/spider/views/             # 按日期分层的日志              │
│   └── 2026/02/                                                  │
│       ├── crawl_views_20260206.log                              │
│       ├── import_views_20260206.log                             │
│       └── export_views_20260206.log                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### 1.2 核心组件

| 组件 | 路径 | 功能 |
|------|------|------|
| 主控脚本 | `spider/run_views_crawler.py` | 整合导出→爬取→导入流程 |
| 导出模块 | `tools/spider/export_views.py` | 从 Django 导出作品列表 |
| 爬虫模块 | `tools/spider/crawl_views.py` | 爬取 B站视频数据 |
| 导入模块 | `tools/spider/import_views.py` | 导入数据到 SQLite |
| 日志工具 | `tools/spider/utils/logger.py` | 按日期分层、实时刷新日志 |
| 定时脚本 | `scripts/bilibili_views_cron.sh` | 定时任务执行脚本 |

---

## 二、全新部署步骤

### 2.1 前提条件

- Python 3.8+
- Django 5.2+
- 项目已正确配置软链接

### 2.2 部署步骤

#### 步骤 1: 创建模型迁移

```bash
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend

# 创建数据模型迁移文件
python manage.py makemigrations data_analytics
```

#### 步骤 2: 应用到 view_data_db 数据库

```bash
# 迁移到新数据库
python manage.py migrate data_analytics --database=view_data_db
```

#### 步骤 3: 验证表结构

```bash
# 检查数据库表是否创建成功
sqlite3 data/view_data.sqlite3 ".tables"
```

应该看到：
- `data_analytics_workmetricsspider`
- `data_analytics_crawlsessionspider`

#### 步骤 4: 测试爬虫流程

```bash
cd /home/yifeianyi/Desktop/xxm_fans_home

# 测试导出
python spider/run_views_crawler.py --export-only

# 测试爬取（仅爬取，不导入）
python spider/run_views_crawler.py --crawl-only

# 测试导入（自动查找最新文件）
python spider/run_views_crawler.py --import-only

# 完整流程测试
python spider/run_views_crawler.py --full
```

#### 步骤 5: 配置定时任务（Cron）

```bash
# 1. 确保脚本有执行权限
chmod +x /home/yifeianyi/Desktop/xxm_fans_home/scripts/bilibili_views_cron.sh

# 2. 编辑 crontab
crontab -e

# 3. 添加以下行（每小时执行一次）
0 * * * * /home/yifeianyi/Desktop/xxm_fans_home/scripts/bilibili_views_cron.sh >> /home/yifeianyi/Desktop/xxm_fans_home/logs/spider/cron_execution.log 2>&1

# 4. 保存并退出（nano: Ctrl+O, Ctrl+X; vim: Esc, :wq）

# 5. 验证定时任务
crontab -l
```

**详细配置说明**: 参见 `doc/tools/spider/bilibili_views_cron_setup_guide.md`

---

## 三、数据库迁移（从旧表到新表）

### 3.1 迁移场景

当需要将数据从旧表迁移到新表时：
- 旧表: `data_analytics_workmetricshour`
- 新表: `data_analytics_workmetricsspider`

### 3.2 迁移步骤

#### 步骤 1: 备份现有数据

```bash
cd /home/yifeianyi/Desktop/xxm_fans_home

# 备份整个数据库
cp data/view_data.sqlite3 data/view_data_backup_$(date +%Y%m%d).sqlite3

# 导出旧表数据（如果需要）
sqlite3 data/view_data.sqlite3 ".dump data_analytics_workmetricshour" > backup_workmetricshour.sql
```

#### 步骤 2: 创建新模型迁移

```bash
cd repo/xxm_fans_backend

# 创建新模型的迁移
python manage.py makemigrations data_analytics

# 应用到 view_data_db
python manage.py migrate data_analytics --database=view_data_db
```

#### 步骤 3: 数据迁移（可选）

如果需要迁移历史数据：

```bash
# 使用 Django shell 迁移数据
python manage.py shell << 'EOF'
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_home.settings')
import django
django.setup()

from data_analytics.models import WorkMetricsHour, WorkMetricsSpider

# 迁移数据
for old in WorkMetricsHour.objects.all():
    WorkMetricsSpider.objects.create(
        platform=old.platform,
        work_id=old.work_id,
        crawl_date=old.crawl_time.date(),
        crawl_hour=old.crawl_time.strftime('%H'),
        crawl_time=old.crawl_time.time(),
        view_count=old.view_count,
        like_count=old.like_count,
        coin_count=old.coin_count,
        favorite_count=old.favorite_count,
        danmaku_count=old.danmaku_count,
        comment_count=old.comment_count,
    )

print("数据迁移完成")
EOF
```

### 3.3 验证迁移

```bash
# 检查新表数据量
sqlite3 data/view_data.sqlite3 "SELECT COUNT(*) FROM data_analytics_workmetricsspider;"

# 对比旧表数据量
sqlite3 data/view_data.sqlite3 "SELECT COUNT(*) FROM data_analytics_workmetricshour;"
```

---

## 四、重新部署（已存在系统）

### 4.1 平滑升级步骤

#### 步骤 1: 停止定时任务

```bash
# 编辑 crontab，注释掉相关行
crontab -e
# 在行首添加 # 注释掉任务
# 0 * * * * /home/yifeianyi/Desktop/xxm_fans_home/scripts/bilibili_views_cron.sh ...
```

#### 步骤 2: 备份数据

```bash
cd /home/yifeianyi/Desktop/xxm_fans_home

# 备份数据库
cp data/view_data.sqlite3 data/view_data_backup_$(date +%Y%m%d_%H%M%S).sqlite3

# 备份现有数据文件
tar -czf data/spider_backup_$(date +%Y%m%d).tar.gz data/spider/
```

#### 步骤 3: 拉取最新代码

```bash
# 假设使用 git
git pull origin main

# 更新子模块
git submodule update --init --recursive
```

#### 步骤 4: 执行迁移

```bash
cd repo/xxm_fans_backend

# 创建并应用迁移
python manage.py makemigrations data_analytics
python manage.py migrate data_analytics --database=view_data_db
```

#### 步骤 5: 验证

```bash
cd /home/yifeianyi/Desktop/xxm_fans_home

# 测试导入功能
python spider/run_views_crawler.py --import-only --list

# 完整测试
python spider/run_views_crawler.py --full
```

#### 步骤 6: 重启定时任务

```bash
# 编辑 crontab，取消注释
crontab -e
# 删除行首的 # 恢复任务
0 * * * * /home/yifeianyi/Desktop/xxm_fans_home/scripts/bilibili_views_cron.sh ...

# 验证 cron 服务状态
sudo systemctl status cron
```

---

## 五、关键文件清单

### 5.1 新增/修改的文件

| 文件路径 | 变更类型 | 说明 |
|----------|----------|------|
| `data_analytics/models/work_metrics_spider.py` | 新增 | 新爬虫数据模型 |
| `data_analytics/models/crawl_session_spider.py` | 新增 | 新爬虫会话模型 |
| `data_analytics/models/__init__.py` | 修改 | 导出新模型 |
| `data_analytics/models/signals.py` | 修改 | 新增信号处理器 |
| `data_analytics/admin/__init__.py` | 修改 | 新增 Admin 配置 |
| `tools/spider/import_views.py` | 修改 | 支持自动查找、重复检测 |
| `tools/spider/utils/logger.py` | 修改 | 支持实时刷新、分层目录 |
| `scripts/bilibili_views_cron.sh` | 新增 | 定时任务脚本 |
| `infra/systemd/bilibili-views-crawler-cron.service` | 新增 | Systemd 服务配置 |
| `infra/systemd/bilibili-views-crawler-cron.timer` | 新增 | Systemd 定时器配置 |

---

## 六、常见问题排查

### 6.1 导入时提示"数据已存在"

```
数据已存在: 2026-02-06 12:00
  - 已有作品记录: 219 条
  - 总会话记录: 3 条
```

**解决方案:**
```bash
# 如果需要重新导入，使用 --force 参数
python spider/run_views_crawler.py --import-only --force
```

### 6.2 找不到数据文件

```
未找到任何数据文件，路径: data/spider/views/*/*/*/*_views_data.json
```

**解决方案:**
```bash
# 1. 先执行爬取
python spider/run_views_crawler.py --crawl-only

# 2. 检查数据文件是否存在
ls -la data/spider/views/2026/02/06/
```

### 6.3 数据库表不存在

```
no such table: data_analytics_workmetricsspider
```

**解决方案:**
```bash
cd repo/xxm_fans_backend
python manage.py migrate data_analytics --database=view_data_db
```

### 6.4 日志文件不实时刷新

**验证方法:**
```bash
# 在另一个终端实时监控日志
tail -f logs/spider/views/2026/02/crawl_views_20260206.log

# 运行爬虫，观察是否实时写入
python spider/run_views_crawler.py --crawl-only
```

---

## 七、命令参考

### 7.1 主控脚本

```bash
# 完整流程
python spider/run_views_crawler.py --full

# 仅导出
python spider/run_views_crawler.py --export-only

# 仅爬取
python spider/run_views_crawler.py --crawl-only

# 仅导入（自动查找最新）
python spider/run_views_crawler.py --import-only

# 导入指定时间
python spider/run_views_crawler.py --import-only --date 2026-02-06 --hour 14

# 强制重新导入
python spider/run_views_crawler.py --import-only --force
```

### 7.2 导入模块

```bash
# 自动导入最新
cd repo/xxm_fans_backend
python tools/spider/import_views.py

# 导入指定时间
python tools/spider/import_views.py --date 2026-02-06 --hour 14

# 列出可用文件
python tools/spider/import_views.py --list

# 强制重新导入
python tools/spider/import_views.py --force
```

### 7.3 定时任务管理（Cron）

```bash
# 编辑定时任务
crontab -e

# 查看定时任务列表
crontab -l

# 查看 cron 系统日志
grep CRON /var/log/syslog | tail -20

# 实时查看 cron 日志
tail -f /var/log/syslog | grep CRON

# 查看爬虫执行日志
cat /home/yifeianyi/Desktop/xxm_fans_home/logs/bilibili_views_crawler.json
```

---

## 八、回滚方案

如果需要回滚到旧版本：

```bash
cd /home/yifeianyi/Desktop/xxm_fans_home

# 1. 停止服务
sudo systemctl stop bilibili-views-crawler-cron.timer

# 2. 恢复数据库
cp data/view_data_backup_YYYYMMDD.sqlite3 data/view_data.sqlite3

# 3. 恢复代码（如果使用 git）
git reset --hard HEAD~1

# 4. 重启服务
sudo systemctl start bilibili-views-crawler-cron.timer
```

---

## 九、联系与支持

如有问题，请检查以下日志：

1. **爬虫日志**: `logs/spider/views/{year}/{month}/crawl_views_YYYYMMDD.log`
2. **导入日志**: `logs/spider/views/{year}/{month}/import_views_YYYYMMDD.log`
3. **定时任务日志**: `logs/bilibili_views_crawler.json`
4. **Cron 日志**: `grep CRON /var/log/syslog | tail -20`

---

**文档版本**: v1.0  
**创建时间**: 2026-02-06  
**最后更新**: 2026-02-06
