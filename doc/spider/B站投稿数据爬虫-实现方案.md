# B站投稿数据爬虫 - 实现方案

## 1. 总体架构

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           B站投稿数据爬虫系统                                │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│   spider/                              repo/xxm_fans_backend/tools/spider/ │
│   ├─ run_views_crawler.py (主控)  ─────▶├─ __init__.py                     │
│   └─ README.md                          ├─ export_views.py (导出模块)       │
│                                         ├─ crawl_views.py (爬虫模块)        │
│                                         ├─ import_views.py (导入模块)       │
│                                         ├─ utils/                           │
│                                         │   ├─ __init__.py                  │
│                                         │   ├─ logger.py                    │
│                                         │   └─ db.py                        │
│                                         └─ config.py                        │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

## 2. 目录结构

```
spider/
├── run_views_crawler.py          # 主控脚本（入口）
└── README.md                     # 使用说明

repo/xxm_fans_backend/tools/spider/
├── __init__.py                   # 包初始化
├── export_views.py               # 数据导出模块
├── crawl_views.py                # 核心爬虫模块
├── import_views.py               # 数据导入模块
├── config.py                     # 配置文件
└── utils/
    ├── __init__.py
    ├── logger.py                 # 日志工具
    └── db.py                     # SQLite 数据库工具

data/
├── spider/
│   ├── views.json                # 导出的作品列表
│   └── views/                    # 按日期存储的爬取结果
│       └── 2026/
│           └── 02/
│               └── 06/
│                   └── 2026-02-06-14_views_data.json   # 含小时
└── view_data.sqlite3             # SQLite 数据库

logs/
└── spider/
    ├── views_crawler_20260206.log    # 爬虫日志
    └── views_import_20260206.log     # 导入日志
```

## 3. 模块设计

### 3.1 数据导出模块

**路径**: `repo/xxm_fans_backend/tools/spider/export_views.py`

**职责**: 将 Django 数据库中的 `WorkStatic` 表数据导出为 JSON 文件

**核心功能**:
- 查询所有作品静态信息
- 生成 `data/spider/views.json` 文件
- 在 `WorkStatic` 数据变更时自动触发更新

**输出格式** (`views.json`):
```json
{
  "export_time": "2026-02-06T11:30:00",
  "total_count": 150,
  "valid_count": 142,
  "works": [
    {
      "platform": "bilibili",
      "work_id": "BV1xx411c7mD",
      "title": "视频标题",
      "author": "作者名",
      "publish_time": "2024-01-15T20:00:00",
      "cover_url": "https://...",
      "is_valid": true
    }
  ]
}
```

**触发方式**:
1. **信号触发**: 通过 Django `post_save` 信号自动触发
2. **手动触发**: 命令行执行 `python export_views.py`
3. **定时触发**: 通过 systemd timer 定期执行

---

### 3.2 核心爬虫模块

**路径**: `repo/xxm_fans_backend/tools/spider/crawl_views.py`

**职责**: 根据 `views.json` 爬取 B站视频数据

**核心功能**:
- 读取 `views.json` 文件
- 根据 `is_valid` 字段筛选需要爬取的视频
- 使用 `bilibili-tools` API 客户端获取视频统计信息
- 按日期目录结构保存爬取结果（**含小时维度**）
- 记录详细的爬取日志

**爬取数据字段**:
| 字段名 | 说明 | 来源 |
|--------|------|------|
| `view_count` | 播放数 | `stat.view` |
| `danmaku_count` | 弹幕数 | `stat.danmaku` |
| `comment_count` | 评论数 | `stat.reply` |
| `like_count` | 点赞数 | `stat.like` |
| `coin_count` | 投币数 | `stat.coin` |
| `favorite_count` | 收藏数 | `stat.favorite` |
| `share_count` | 转发数 | `stat.share` |

**输出文件命名规则**（含小时）:
```
data/spider/views/{year}/{month}/{day}/{year}-{month}-{day}-{hour}_views_data.json

示例:
data/spider/views/2026/02/06/2026-02-06-14_views_data.json
```

**输出格式**:
```json
{
  "session_id": "crawl_20260206143000",
  "crawl_time": "2026-02-06T14:30:00",
  "crawl_hour": "14",
  "total_count": 142,
  "success_count": 140,
  "fail_count": 2,
  "data": [
    {
      "platform": "bilibili",
      "work_id": "BV1xx411c7mD",
      "title": "视频标题",
      "crawl_time": "2026-02-06T14:30:00",
      "view_count": 100000,
      "danmaku_count": 5000,
      "comment_count": 1200,
      "like_count": 8000,
      "coin_count": 3000,
      "favorite_count": 2500,
      "share_count": 800,
      "status": "success"
    }
  ],
  "errors": [
    {
      "work_id": "BV1yy411c7mD",
      "error": "视频不存在或已删除",
      "status": "failed"
    }
  ]
}
```

---

### 3.3 数据导入模块

**路径**: `repo/xxm_fans_backend/tools/spider/import_views.py`

**职责**: 将爬取结果导入到 SQLite 数据库

**核心功能**:
- 读取指定日期/小时的爬取结果文件
- 创建/更新 `view_data.sqlite3` 数据库
- 维护数据表结构
- 记录导入日志

**SQLite 数据库结构**:

```sql
-- 作品数据表
CREATE TABLE work_metrics (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    platform TEXT NOT NULL,
    work_id TEXT NOT NULL,
    title TEXT,
    crawl_date TEXT NOT NULL,          -- 爬取日期 (YYYY-MM-DD)
    crawl_hour TEXT NOT NULL,          -- 爬取小时 (HH)
    crawl_time TEXT NOT NULL,          -- 完整时间 (HH:MM:SS)
    view_count INTEGER DEFAULT 0,
    danmaku_count INTEGER DEFAULT 0,
    comment_count INTEGER DEFAULT 0,
    like_count INTEGER DEFAULT 0,
    coin_count INTEGER DEFAULT 0,
    favorite_count INTEGER DEFAULT 0,
    share_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(platform, work_id, crawl_date, crawl_hour)
);

-- 爬取会话表
CREATE TABLE crawl_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    session_id TEXT UNIQUE NOT NULL,
    crawl_date TEXT NOT NULL,
    crawl_hour TEXT NOT NULL,
    start_time TEXT,
    end_time TEXT,
    total_count INTEGER DEFAULT 0,
    success_count INTEGER DEFAULT 0,
    fail_count INTEGER DEFAULT 0,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 索引
CREATE INDEX idx_work_metrics_platform_work_id ON work_metrics(platform, work_id);
CREATE INDEX idx_work_metrics_crawl_date ON work_metrics(crawl_date);
CREATE INDEX idx_work_metrics_crawl_hour ON work_metrics(crawl_date, crawl_hour);
CREATE INDEX idx_crawl_sessions_date ON crawl_sessions(crawl_date);
CREATE INDEX idx_crawl_sessions_hour ON crawl_sessions(crawl_date, crawl_hour);
```

---

### 3.4 主控脚本

**路径**: `spider/run_views_crawler.py`

**职责**: 整合所有模块，提供统一的执行入口

**执行流程**:
```
1. 导出 views.json (可选)
2. 读取 views.json
3. 爬取 B站数据
4. 保存到日期目录 (含小时)
5. 导入到 SQLite
6. 记录执行日志
```

**命令行参数**:
```bash
# 完整流程：导出 -> 爬取 -> 导入
python spider/run_views_crawler.py --full

# 仅爬取（使用现有的 views.json）
python spider/run_views_crawler.py --crawl-only

# 指定日期导入
python spider/run_views_crawler.py --import-only --date 2026-02-06 --hour 14

# 导出 views.json
python spider/run_views_crawler.py --export-only
```

---

### 3.5 信号处理模块 (Django Signals)

**路径**: `repo/xxm_fans_backend/data_analytics/models/signals.py`

**新增信号处理器**:

```python
@receiver(post_save, sender=WorkStatic)
def auto_export_views_on_save(sender, instance, created, **kwargs):
    """
    当 WorkStatic 数据变更时，自动触发 views.json 导出
    """
    from threading import Thread
    import time
    
    current_time = time.time()
    
    # 防抖: 10秒内只触发一次
    if not hasattr(auto_export_views_on_save, '_last_trigger'):
        auto_export_views_on_save._last_trigger = 0
    
    if current_time - auto_export_views_on_save._last_trigger < 10:
        return
    
    auto_export_views_on_save._last_trigger = current_time
    
    def delayed_export():
        time.sleep(5)
        try:
            from django.core.management import call_command
            call_command('export_views', silent=True)
        except Exception as e:
            logger.error(f"自动导出 views.json 失败: {e}")
    
    Thread(target=delayed_export, daemon=True).start()
```

---

## 4. 异常处理机制

### 4.1 异常分类

| 异常类型 | 说明 | 处理策略 |
|----------|------|----------|
| `NetworkError` | 网络连接失败 | 指数退避重试，最多3次 |
| `APIError` | B站API返回错误 | 记录错误，跳过该视频，继续执行 |
| `RateLimitError` | 请求频率限制 | 延长等待时间，继续重试 |
| `DataValidationError` | 数据格式错误 | 记录错误，跳过该条目 |
| `DatabaseError` | 数据库操作失败 | 回滚事务，记录错误 |

### 4.2 重试策略

```python
class RetryPolicy:
    """重试策略"""
    
    def __init__(self, max_retries=3, base_delay=1.0):
        self.max_retries = max_retries
        self.base_delay = base_delay
    
    def execute(self, func, *args, **kwargs):
        for attempt in range(self.max_retries):
            try:
                return func(*args, **kwargs)
            except NetworkError as e:
                if attempt == self.max_retries - 1:
                    raise
                delay = self.base_delay * (2 ** attempt)
                logger.warning(f"网络错误，{delay}秒后重试")
                time.sleep(delay)
            except RateLimitError as e:
                delay = 60
                logger.warning(f"触发频率限制，等待{delay}秒")
                time.sleep(delay)
```

---

## 5. 日志系统

**路径**: `repo/xxm_fans_backend/tools/spider/utils/logger.py`

### 5.1 日志配置

```python
import logging
from datetime import datetime
import os

def setup_logger(name: str, log_dir: str = "logs/spider") -> logging.Logger:
    """设置日志记录器"""
    
    os.makedirs(log_dir, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"{name}_{date_str}.log")
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
```

---

## 6. 定时任务配置

### 6.1 Systemd Timer 配置

**文件**: `infra/systemd/bilibili-views-crawler.service`

```ini
[Unit]
Description=B站投稿数据爬虫
After=network.target

[Service]
Type=oneshot
User=www-data
WorkingDirectory=/home/yifeianyi/Desktop/xxm_fans_home
ExecStart=/home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend/venv/bin/python spider/run_views_crawler.py --full
Environment=PYTHONPATH=/home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend
```

**文件**: `infra/systemd/bilibili-views-crawler.timer`

```ini
[Unit]
Description=B站投稿数据爬虫定时器

[Timer]
# 每小时执行一次
OnCalendar=hourly
Persistent=true

[Install]
WantedBy=timers.target
```

---

## 7. 核心代码实现

### 7.1 数据导出模块

**路径**: `repo/xxm_fans_backend/tools/spider/export_views.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据导出模块
将 WorkStatic 表数据导出为 views.json
"""

import json
import os
import sys
from datetime import datetime
from typing import List, Dict, Any

# Django 设置
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_backend.settings')

import django
django.setup()

from data_analytics.models import WorkStatic
from utils.logger import setup_logger

logger = setup_logger("export_views")

# 项目根目录
PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
OUTPUT_FILE = os.path.join(PROJECT_ROOT, "data", "spider", "views.json")


class ViewsExporter:
    """作品数据导出器"""
    
    def __init__(self):
        self.works = []
    
    def fetch_works(self) -> List[Dict[str, Any]]:
        """从数据库获取作品数据"""
        works = []
        queryset = WorkStatic.objects.all().order_by('-publish_time')
        
        for work in queryset:
            works.append({
                "platform": work.platform,
                "work_id": work.work_id,
                "title": work.title,
                "author": work.author,
                "publish_time": work.publish_time.isoformat() if work.publish_time else None,
                "cover_url": work.cover_url,
                "is_valid": work.is_valid
            })
        
        logger.info(f"从数据库获取了 {len(works)} 条作品记录")
        return works
    
    def export(self) -> bool:
        """导出数据到 JSON 文件"""
        try:
            os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
            
            works = self.fetch_works()
            valid_count = sum(1 for w in works if w['is_valid'])
            
            output_data = {
                "export_time": datetime.now().isoformat(),
                "total_count": len(works),
                "valid_count": valid_count,
                "works": works
            }
            
            with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
                json.dump(output_data, f, ensure_ascii=False, indent=2)
            
            logger.info(f"成功导出到 {OUTPUT_FILE}，总计 {len(works)} 条记录")
            return True
            
        except Exception as e:
            logger.error(f"导出失败: {e}")
            return False


def main():
    exporter = ViewsExporter()
    success = exporter.export()
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
```

### 7.2 核心爬虫模块

**路径**: `repo/xxm_fans_backend/tools/spider/crawl_views.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
核心爬虫模块
爬取 B站视频数据并保存
"""

import json
import os
import sys
import time
import random
from datetime import datetime
from typing import List, Dict, Any, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_backend.settings')

import django
django.setup()

from tools.bilibili import BilibiliAPIClient, BilibiliAPIError
from utils.logger import setup_logger

logger = setup_logger("crawl_views")

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
VIEWS_FILE = os.path.join(PROJECT_ROOT, "data", "spider", "views.json")
OUTPUT_DIR = os.path.join(PROJECT_ROOT, "data", "spider", "views")


class ViewsCrawler:
    """B站投稿数据爬虫"""
    
    def __init__(self, request_delay_min: float = 0.2, request_delay_max: float = 0.5, max_retries: int = 3):
        self.request_delay_min = request_delay_min
        self.request_delay_max = request_delay_max
        self.max_retries = max_retries
        self.api_client = BilibiliAPIClient(
            timeout=10,
            retry_times=max_retries,
            retry_delay=1
        )
        self.session_id = f"crawl_{datetime.now().strftime('%Y%m%d%H%M%S')}"
        self.results = []
        self.errors = []
    
    def load_views(self) -> List[Dict[str, Any]]:
        """加载 views.json"""
        if not os.path.exists(VIEWS_FILE):
            raise FileNotFoundError(f"找不到 {VIEWS_FILE}，请先执行导出")
        
        with open(VIEWS_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        valid_works = [w for w in data.get('works', []) if w.get('is_valid', True)]
        logger.info(f"从 views.json 加载了 {len(valid_works)} 个有效作品")
        return valid_works
    
    def crawl_video(self, work: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """爬取单个视频数据"""
        work_id = work['work_id']
        platform = work.get('platform', 'bilibili')
        
        if platform != 'bilibili':
            logger.debug(f"跳过非B站作品: {work_id}")
            return None
        
        bvid = work_id if work_id.startswith('BV') else f"BV{work_id}"
        
        try:
            logger.info(f"开始爬取: {bvid} - {work.get('title', 'Unknown')}")
            
            video_info = self.api_client.get_video_info(bvid)
            
            result = {
                "platform": platform,
                "work_id": work_id,
                "title": video_info.title,
                "crawl_time": datetime.now().isoformat(),
                "view_count": video_info.get_view_count(),
                "danmaku_count": video_info.get_danmaku_count(),
                "comment_count": video_info.stat.get('reply', 0),
                "like_count": video_info.get_like_count(),
                "coin_count": video_info.stat.get('coin', 0),
                "favorite_count": video_info.stat.get('favorite', 0),
                "share_count": video_info.stat.get('share', 0),
                "status": "success"
            }
            
            logger.info(f"爬取成功: {bvid} view_count={result['view_count']}")
            return result
            
        except BilibiliAPIError as e:
            error_msg = f"API错误: {e.message}"
            logger.error(f"爬取失败: {bvid} - {error_msg}")
            self.errors.append({
                "work_id": work_id,
                "title": work.get('title', 'Unknown'),
                "error": error_msg,
                "status": "failed"
            })
            return None
        except Exception as e:
            error_msg = f"未知错误: {str(e)}"
            logger.error(f"爬取失败: {bvid} - {error_msg}")
            self.errors.append({
                "work_id": work_id,
                "title": work.get('title', 'Unknown'),
                "error": error_msg,
                "status": "failed"
            })
            return None
    
    def crawl(self) -> str:
        """执行爬取任务"""
        start_time = datetime.now()
        works = self.load_views()
        
        total = len(works)
        success = 0
        failed = 0
        
        logger.info(f"开始爬取任务: {self.session_id}，总计 {total} 个作品")
        
        for i, work in enumerate(works, 1):
            logger.info(f"进度: {i}/{total}")
            
            result = self.crawl_video(work)
            if result:
                self.results.append(result)
                success += 1
            else:
                failed += 1
            
            if i < total:
                # 随机间隔 0.2-0.5 秒
                delay = random.uniform(self.request_delay_min, self.request_delay_max)
                time.sleep(delay)
        
        # 构建输出数据
        output_data = {
            "session_id": self.session_id,
            "crawl_time": start_time.isoformat(),
            "crawl_hour": start_time.strftime('%H'),
            "total_count": total,
            "success_count": success,
            "fail_count": failed,
            "data": self.results,
            "errors": self.errors
        }
        
        output_path = self._save_output(output_data, start_time)
        
        logger.info(f"爬取完成: 成功 {success}，失败 {failed}，总计 {total}")
        logger.info(f"结果已保存到: {output_path}")
        
        return output_path
    
    def _save_output(self, data: Dict[str, Any], dt: datetime) -> str:
        """保存输出到文件（含小时）"""
        year = dt.strftime('%Y')
        month = dt.strftime('%m')
        day = dt.strftime('%d')
        hour = dt.strftime('%H')
        date_str = dt.strftime('%Y-%m-%d')
        
        output_dir = os.path.join(OUTPUT_DIR, year, month, day)
        os.makedirs(output_dir, exist_ok=True)
        
        # 文件名包含小时
        output_file = os.path.join(output_dir, f"{date_str}-{hour}_views_data.json")
        
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        return output_file


def main():
    crawler = ViewsCrawler(request_delay_min=0.2, request_delay_max=0.5, max_retries=3)
    try:
        output_path = crawler.crawl()
        print(f"爬取完成，结果保存到: {output_path}")
        sys.exit(0)
    except Exception as e:
        logger.error(f"爬取任务失败: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
```

### 7.3 数据导入模块

**路径**: `repo/xxm_fans_backend/tools/spider/import_views.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
数据导入模块
将爬取结果导入到 SQLite 数据库
"""

import json
import os
import sqlite3
import sys
from datetime import datetime
from typing import Dict, Any, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from utils.logger import setup_logger

logger = setup_logger("import_views")

PROJECT_ROOT = os.path.join(os.path.dirname(__file__), '..', '..', '..', '..')
SQLITE_DB = os.path.join(PROJECT_ROOT, "data", "view_data.sqlite3")
VIEWS_DIR = os.path.join(PROJECT_ROOT, "data", "spider", "views")


class ViewsImporter:
    """数据导入器"""
    
    def __init__(self):
        self.conn = None
        self.cursor = None
    
    def connect(self):
        """连接数据库"""
        os.makedirs(os.path.dirname(SQLITE_DB), exist_ok=True)
        self.conn = sqlite3.connect(SQLITE_DB)
        self.cursor = self.conn.cursor()
        self._init_tables()
    
    def close(self):
        """关闭连接"""
        if self.conn:
            self.conn.close()
    
    def _init_tables(self):
        """初始化数据表"""
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS work_metrics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                platform TEXT NOT NULL,
                work_id TEXT NOT NULL,
                title TEXT,
                crawl_date TEXT NOT NULL,
                crawl_hour TEXT NOT NULL,
                crawl_time TEXT NOT NULL,
                view_count INTEGER DEFAULT 0,
                danmaku_count INTEGER DEFAULT 0,
                comment_count INTEGER DEFAULT 0,
                like_count INTEGER DEFAULT 0,
                coin_count INTEGER DEFAULT 0,
                favorite_count INTEGER DEFAULT 0,
                share_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(platform, work_id, crawl_date, crawl_hour)
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS crawl_sessions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT UNIQUE NOT NULL,
                crawl_date TEXT NOT NULL,
                crawl_hour TEXT NOT NULL,
                start_time TEXT,
                end_time TEXT,
                total_count INTEGER DEFAULT 0,
                success_count INTEGER DEFAULT 0,
                fail_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # 创建索引
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_work_metrics_platform_work_id 
            ON work_metrics(platform, work_id)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_work_metrics_crawl_date 
            ON work_metrics(crawl_date)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_work_metrics_crawl_hour 
            ON work_metrics(crawl_date, crawl_hour)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_crawl_sessions_date 
            ON crawl_sessions(crawl_date)
        """)
        self.cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_crawl_sessions_hour 
            ON crawl_sessions(crawl_date, crawl_hour)
        """)
        
        self.conn.commit()
        logger.info("数据库表初始化完成")
    
    def load_crawl_data(self, date_str: Optional[str] = None, 
                        hour_str: Optional[str] = None) -> Optional[Dict[str, Any]]:
        """加载爬取数据"""
        if date_str is None:
            date_str = datetime.now().strftime('%Y-%m-%d')
        if hour_str is None:
            hour_str = datetime.now().strftime('%H')
        
        year, month, day = date_str.split('-')
        data_file = os.path.join(
            VIEWS_DIR, year, month, day, 
            f"{date_str}-{hour_str}_views_data.json"
        )
        
        if not os.path.exists(data_file):
            logger.error(f"找不到数据文件: {data_file}")
            return None
        
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        logger.info(f"加载数据文件: {data_file}")
        return data
    
    def import_data(self, data: Dict[str, Any]) -> bool:
        """导入数据到数据库"""
        try:
            crawl_time = data.get('crawl_time', datetime.now().isoformat())
            crawl_date = crawl_time[:10]
            crawl_hour = data.get('crawl_hour', crawl_time[11:13] if len(crawl_time) > 13 else "00")
            crawl_time_str = crawl_time[11:19] if len(crawl_time) > 10 else "00:00:00"
            
            session_id = data.get('session_id', 'unknown')
            total_count = data.get('total_count', 0)
            success_count = data.get('success_count', 0)
            fail_count = data.get('fail_count', 0)
            
            self.conn.execute("BEGIN TRANSACTION")
            
            # 插入会话记录
            self.cursor.execute("""
                INSERT OR REPLACE INTO crawl_sessions 
                (session_id, crawl_date, crawl_hour, start_time, end_time, 
                 total_count, success_count, fail_count)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                session_id, crawl_date, crawl_hour, crawl_time_str,
                datetime.now().strftime('%H:%M:%S'),
                total_count, success_count, fail_count
            ))
            
            # 插入作品数据
            metrics_data = data.get('data', [])
            imported = 0
            
            for item in metrics_data:
                if item.get('status') != 'success':
                    continue
                
                self.cursor.execute("""
                    INSERT OR REPLACE INTO work_metrics 
                    (platform, work_id, title, crawl_date, crawl_hour, crawl_time,
                     view_count, danmaku_count, comment_count, like_count,
                     coin_count, favorite_count, share_count)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item.get('platform', 'bilibili'),
                    item.get('work_id'),
                    item.get('title'),
                    crawl_date,
                    crawl_hour,
                    crawl_time_str,
                    item.get('view_count', 0),
                    item.get('danmaku_count', 0),
                    item.get('comment_count', 0),
                    item.get('like_count', 0),
                    item.get('coin_count', 0),
                    item.get('favorite_count', 0),
                    item.get('share_count', 0)
                ))
                imported += 1
            
            self.conn.commit()
            logger.info(f"导入完成: 成功导入 {imported} 条记录")
            return True
            
        except Exception as e:
            self.conn.rollback()
            logger.error(f"导入失败: {e}")
            return False
    
    def import_by_date(self, date_str: Optional[str] = None, 
                       hour_str: Optional[str] = None) -> bool:
        """按日期导入数据"""
        data = self.load_crawl_data(date_str, hour_str)
        if not data:
            return False
        return self.import_data(data)


def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='导入B站投稿数据到SQLite')
    parser.add_argument('--date', type=str, help='指定日期 (YYYY-MM-DD)，默认为今天')
    parser.add_argument('--hour', type=str, help='指定小时 (HH)，默认为当前小时')
    args = parser.parse_args()
    
    importer = ViewsImporter()
    try:
        importer.connect()
        success = importer.import_by_date(args.date, args.hour)
        sys.exit(0 if success else 1)
    except Exception as e:
        logger.error(f"导入任务失败: {e}")
        sys.exit(1)
    finally:
        importer.close()


if __name__ == '__main__':
    main()
```

### 7.4 主控脚本

**路径**: `spider/run_views_crawler.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
主控脚本
整合导出、爬取、导入流程

路径: spider/run_views_crawler.py

用法:
    python spider/run_views_crawler.py --full        # 完整流程
    python spider/run_views_crawler.py --export-only # 仅导出
    python spider/run_views_crawler.py --crawl-only  # 仅爬取
    python spider/run_views_crawler.py --import-only # 仅导入
"""

import argparse
import sys
import os

# 项目根目录
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BACKEND_TOOLS = os.path.join(PROJECT_ROOT, 'repo', 'xxm_fans_backend', 'tools', 'spider')

# 添加后端工具路径
sys.path.insert(0, BACKEND_TOOLS)
sys.path.insert(0, os.path.join(PROJECT_ROOT, 'repo', 'xxm_fans_backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_backend.settings')

import django
django.setup()

from export_views import ViewsExporter, OUTPUT_FILE
from crawl_views import ViewsCrawler, VIEWS_FILE
from import_views import ViewsImporter
from utils.logger import setup_logger

logger = setup_logger("run_views_crawler", 
                      log_dir=os.path.join(PROJECT_ROOT, "logs", "spider"))


def run_full_pipeline():
    """执行完整流程"""
    logger.info("=" * 60)
    logger.info("开始执行完整流程: 导出 -> 爬取 -> 导入")
    logger.info("=" * 60)
    
    # 1. 导出数据
    logger.info("\n[1/3] 导出作品数据...")
    exporter = ViewsExporter()
    if not exporter.export():
        logger.error("导出失败，终止流程")
        return False
    
    # 2. 爬取数据
    logger.info("\n[2/3] 爬取B站数据...")
    crawler = ViewsCrawler(request_delay_min=0.2, request_delay_max=0.5, max_retries=3)
    try:
        output_path = crawler.crawl()
        logger.info(f"爬取完成: {output_path}")
    except Exception as e:
        logger.error(f"爬取失败: {e}")
        return False
    
    # 3. 导入数据
    logger.info("\n[3/3] 导入数据到SQLite...")
    importer = ViewsImporter()
    try:
        importer.connect()
        success = importer.import_by_date()
        importer.close()
        if not success:
            logger.error("导入失败")
            return False
    except Exception as e:
        logger.error(f"导入失败: {e}")
        return False
    
    logger.info("\n" + "=" * 60)
    logger.info("完整流程执行成功!")
    logger.info("=" * 60)
    return True


def main():
    parser = argparse.ArgumentParser(description='B站投稿数据爬虫')
    parser.add_argument('--full', action='store_true', help='执行完整流程')
    parser.add_argument('--export-only', action='store_true', help='仅导出 views.json')
    parser.add_argument('--crawl-only', action='store_true', help='仅爬取数据')
    parser.add_argument('--import-only', action='store_true', help='仅导入数据')
    parser.add_argument('--date', type=str, help='指定日期 (YYYY-MM-DD)，用于导入')
    parser.add_argument('--hour', type=str, help='指定小时 (HH)，用于导入')
    
    args = parser.parse_args()
    
    if not any([args.full, args.export_only, args.crawl_only, args.import_only]):
        args.full = True
    
    success = False
    
    try:
        if args.full:
            success = run_full_pipeline()
        elif args.export_only:
            exporter = ViewsExporter()
            success = exporter.export()
        elif args.crawl_only:
            crawler = ViewsCrawler(request_delay_min=0.2, request_delay_max=0.5)
            output_path = crawler.crawl()
            success = True
            print(f"爬取完成: {output_path}")
        elif args.import_only:
            importer = ViewsImporter()
            importer.connect()
            success = importer.import_by_date(args.date, args.hour)
            importer.close()
    except Exception as e:
        logger.error(f"执行失败: {e}")
        success = False
    
    sys.exit(0 if success else 1)


if __name__ == '__main__':
    main()
```

### 7.5 Django 信号处理器

**添加到**: `repo/xxm_fans_backend/data_analytics/models/signals.py`

```python
# 添加到文件末尾

import logging
from threading import Thread
import time
import os
import sys

logger = logging.getLogger(__name__)

# 项目根目录
PROJECT_ROOT = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))),
    '..', '..'
)
SPIDER_TOOLS = os.path.join(PROJECT_ROOT, 'repo', 'xxm_fans_backend', 'tools', 'spider')


@receiver(post_save, sender=WorkStatic)
def auto_export_views_on_save(sender, instance, created, **kwargs):
    """
    当 WorkStatic 数据创建或更新时，自动触发 views.json 导出
    使用延迟和防抖机制，避免频繁触发
    """
    current_time = time.time()
    
    # 防抖: 10秒内只触发一次
    if not hasattr(auto_export_views_on_save, '_last_trigger'):
        auto_export_views_on_save._last_trigger = 0
    
    if current_time - auto_export_views_on_save._last_trigger < 10:
        return
    
    auto_export_views_on_save._last_trigger = current_time
    
    def delayed_export():
        """延迟执行导出，避免频繁操作"""
        time.sleep(5)
        try:
            # 动态导入，避免循环依赖
            if SPIDER_TOOLS not in sys.path:
                sys.path.insert(0, SPIDER_TOOLS)
            
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'xxm_fans_backend.settings')
            
            from export_views import ViewsExporter
            
            exporter = ViewsExporter()
            exporter.export()
            logger.info(f"WorkStatic {instance.work_id} 变更，自动导出成功")
            
        except Exception as e:
            logger.error(f"自动导出 views.json 失败: {e}")
    
    thread = Thread(target=delayed_export, daemon=True)
    thread.start()
    logger.debug(f"WorkStatic {instance.work_id} 变更，已触发自动导出任务")
```

### 7.6 包初始化文件

**路径**: `repo/xxm_fans_backend/tools/spider/__init__.py`

```python
"""
Spider 工具包
提供B站投稿数据爬取相关功能
"""

from .export_views import ViewsExporter
from .crawl_views import ViewsCrawler
from .import_views import ViewsImporter

__all__ = [
    'ViewsExporter',
    'ViewsCrawler', 
    'ViewsImporter',
]
```

### 7.7 工具模块

**路径**: `repo/xxm_fans_backend/tools/spider/utils/logger.py`

```python
"""
日志工具模块
"""

import logging
from datetime import datetime
import os

# 默认日志目录（相对于项目根目录）
DEFAULT_LOG_DIR = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))),
    "logs", "spider"
)


def setup_logger(name: str, log_dir: str = None) -> logging.Logger:
    """
    设置日志记录器
    
    Args:
        name: 日志记录器名称
        log_dir: 日志目录，默认为项目根目录下的 logs/spider
    
    Returns:
        配置好的日志记录器
    """
    if log_dir is None:
        log_dir = DEFAULT_LOG_DIR
    
    os.makedirs(log_dir, exist_ok=True)
    
    date_str = datetime.now().strftime("%Y%m%d")
    log_file = os.path.join(log_dir, f"{name}_{date_str}.log")
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # 避免重复添加处理器
    if logger.handlers:
        return logger
    
    # 文件处理器
    file_handler = logging.FileHandler(log_file, encoding='utf-8')
    file_handler.setLevel(logging.INFO)
    
    # 控制台处理器
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    
    # 格式
    formatter = logging.Formatter(
        '[%(asctime)s] %(levelname)-8s %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    file_handler.setFormatter(formatter)
    console_handler.setFormatter(formatter)
    
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger
```

**路径**: `repo/xxm_fans_backend/tools/spider/utils/__init__.py`

```python
"""
Spider 工具子包
"""

from .logger import setup_logger

__all__ = ['setup_logger']
```

---

## 8. 运行和部署

### 8.1 手动运行

```bash
# 进入项目目录
cd /home/yifeianyi/Desktop/xxm_fans_home

# 完整流程
python spider/run_views_crawler.py --full

# 仅导出
python spider/run_views_crawler.py --export-only

# 仅爬取
python spider/run_views_crawler.py --crawl-only

# 仅导入（当前小时）
python spider/run_views_crawler.py --import-only

# 导入指定日期和小时
python spider/run_views_crawler.py --import-only --date 2026-02-06 --hour 14
```

### 8.2 定时任务

```bash
# 激活 systemd timer
sudo systemctl enable --now bilibili-views-crawler.timer

# 查看定时任务状态
systemctl list-timers --all | grep bilibili

# 手动触发
sudo systemctl start bilibili-views-crawler.service
```

### 8.3 日志查看

```bash
# 查看最新爬虫日志
tail -f logs/spider/views_crawler_$(date +%Y%m%d).log

# 查看最新导入日志
tail -f logs/spider/views_import_$(date +%Y%m%d).log
```

---

## 9. 数据查询示例

```sql
-- 查询某作品的历史数据
SELECT * FROM work_metrics 
WHERE work_id = 'BV1xx411c7mD' 
ORDER BY crawl_date DESC, crawl_hour DESC;

-- 查询某日某时的所有数据
SELECT * FROM work_metrics 
WHERE crawl_date = '2026-02-06' AND crawl_hour = '14'
ORDER BY view_count DESC;

-- 查询某作品的小时级增长趋势
SELECT 
    crawl_date || ' ' || crawl_hour || ':00' as time_point,
    view_count,
    view_count - LAG(view_count) OVER (ORDER BY crawl_date, crawl_hour) as view_growth
FROM work_metrics 
WHERE work_id = 'BV1xx411c7mD'
ORDER BY crawl_date, crawl_hour;

-- 查询每日数据汇总（取每小时最后一条）
SELECT 
    crawl_date,
    work_id,
    title,
    MAX(view_count) as max_views,
    MAX(like_count) as max_likes
FROM work_metrics 
GROUP BY crawl_date, work_id
ORDER BY crawl_date DESC;
```

---

## 10. 更新摘要

相比上一版方案，主要更新：

| 项目 | 旧方案 | 新方案 |
|------|--------|--------|
| **文件名** | `{date}_views_data.json` | `{date}-{hour}_views_data.json` |
| **存储粒度** | 每天一个文件 | 每小时一个文件 |
| **目录结构** | 全部放在 `spider/` | 主控脚本在 `spider/`，其他模块在 `repo/xxm_fans_backend/tools/spider/` |
| **SQLite 表** | 只有 `crawl_date` | 新增 `crawl_hour` 字段 |
| **索引** | 按天索引 | 按天+小时索引 |
