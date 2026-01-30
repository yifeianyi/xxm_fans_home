# Use Cases Module

## Module Overview

**Purpose**: Complete implementation examples for common Bilibili-related features

**Contents**:
- Import song records from BV ID
- Import fan works from BV ID
- Import analytics data from BV ID
- Fetch user follower count

## Use Case 1: Import Song Records from BV ID

**File**: `repo/xxm_fans_backend/song_management/services/bilibili_import_service.py`

**Purpose**: Import song performance records from Bilibili video pages

**Workflow**:
1. Get video page list using `get_video_pagelist()`
2. Get video cover using `get_video_info()`
3. Parse page titles to extract song name and date
4. Download covers using `download_by_date()`
5. Create `SongRecord` objects

**Complete Implementation**:

```python
import re
from datetime import datetime
from collections import defaultdict
from django.conf import settings
from song_management.models import Song, SongRecord
from tools.bilibili import BilibiliAPIClient, BilibiliCoverDownloader, BilibiliAPIError

class BilibiliImporter:
    """B站视频信息导入器"""
    
    def __init__(self):
        self.api_client = BilibiliAPIClient(timeout=10, retry_times=3)
        self.cover_downloader = BilibiliCoverDownloader()
    
    def import_bv_song(self, bvid, selected_song_id=None, pending_parts=None):
        """导入BV歌曲"""
        print(f"[BV:{bvid}] 开始导入")
        
        # 如果没有待处理分P，则解析整个BV
        if pending_parts is None:
            try:
                pending_parts = self._parse_bv_parts(bvid)
                print(f"[BV:{bvid}] 解析完成，找到 {len(pending_parts)} 个分P")
            except Exception as e:
                print(f"[BV:{bvid}] 解析过程中发生异常: {e}")
                return [], [], None
        
        results = []
        cur_song_counts = defaultdict(int)
        remaining_parts = []
        conflict_info = None
        
        if not pending_parts:
            print(f"[BV:{bvid}] 没有找到有效的分P信息")
            return results, [], conflict_info
        
        # 处理当前分P（如果有选定的歌曲ID）
        if selected_song_id and pending_parts:
            results, remaining_parts, conflict_info = self._process_current_part(
                bvid, pending_parts, selected_song_id, cur_song_counts
            )
            if conflict_info:
                return results, remaining_parts, conflict_info
        
        # 处理剩余分P
        parts_to_process = remaining_parts if selected_song_id else pending_parts
        print(f"[BV:{bvid}] 开始处理剩余分P，共 {len(parts_to_process)} 个")
        new_results = self._process_remaining_parts(bvid, parts_to_process, cur_song_counts)
        results.extend(new_results)
        
        print(f"[BV:{bvid}] 导入完成，共导入 {len(results)} 条")
        return results, [], conflict_info
    
    def _parse_bv_parts(self, bvid):
        """解析BV的所有分P信息"""
        print(f"[BV:{bvid}] 开始解析分P信息")
        
        # Step 1: 获取分P信息
        try:
            pagelist = self.api_client.get_video_pagelist(bvid)
            print(f"[BV:{bvid}] 获取分P信息成功，共 {len(pagelist)} 个分P")
        except BilibiliAPIError as e:
            print(f"[BV:{bvid}] 获取分P信息失败: {e.message}")
            return []
        
        # Step 2: 获取视频总封面
        fallback_cover_url = None
        try:
            video_info = self.api_client.get_video_info(bvid)
            fallback_cover_url = video_info.get_cover_url()
            print(f"[BV:{bvid}] 获取总封面成功")
        except BilibiliAPIError as e:
            print(f"[BV:{bvid}] 获取总封面失败: {e.message}")
        
        # 解析所有分P信息并下载封面
        pending_parts = []
        downloaded_covers = {}
        
        for page_info in pagelist:
            # 提取日期：2025年6月12日
            match = re.search(r"(\d{4})年(\d{1,2})月(\d{1,2})日", page_info.part)
            if match:
                try:
                    year, month, day = map(int, match.groups())
                    performed_date = datetime(year, month, day).date()
                    song_name = re.sub(r"\d{4}年\d{1,2}月\d{1,2}日", "", page_info.part).strip("- ").strip()
                    
                    # 下载封面（每个日期只下载一次）
                    date_str = performed_date.strftime("%Y-%m-%d")
                    if date_str not in downloaded_covers:
                        cover_path = self.cover_downloader.download_by_date(
                            fallback_cover_url,
                            performed_date
                        )
                        if not cover_path:
                            cover_path = fallback_cover_url
                        downloaded_covers[date_str] = cover_path
                    
                    pending_parts.append({
                        "song_name": song_name,
                        "performed_date": performed_date.strftime("%Y-%m-%d"),
                        "url": page_info.get_player_url(bvid),
                        "cover_url": downloaded_covers[date_str]
                    })
                except Exception as e:
                    print(f"[BV:{bvid}] 分P解析失败: {e}")
        
        return pending_parts
    
    def _process_remaining_parts(self, bvid, parts_to_process, cur_song_counts):
        """处理剩余分P"""
        results = []
        
        for part in parts_to_process:
            song_name = part["song_name"]
            performed_date = datetime.strptime(part["performed_date"], "%Y-%m-%d").date()
            
            try:
                song_obj, created_song = Song.objects.get_or_create(song_name=song_name)
            except Song.MultipleObjectsReturned:
                # 处理冲突
                candidates = Song.objects.filter(song_name=song_name)
                conflict_parts = [part] + parts_to_process[parts_to_process.index(part)+1:]
                conflict_info = {
                    "song_name": song_name,
                    "candidates": candidates,
                    "current_part": part,
                    "remaining_parts": conflict_parts
                }
                return results, [], conflict_info
            
            if SongRecord.objects.filter(song=song_obj, performed_at=performed_date).exists():
                continue
            
            cur_song_counts[song_name] += 1
            count = cur_song_counts[song_name]
            note = f"同批版本 {count}" if count > 1 else None
            
            SongRecord.objects.create(
                song=song_obj,
                performed_at=performed_date,
                url=part["url"],
                notes=note,
                cover_url=part["cover_url"]
            )
            
            results.append({
                "song_name": song_name,
                "url": part["url"],
                "note": note,
                "cover_url": part["cover_url"]
            })
        
        return results
```

## Use Case 2: Import Fan Works from BV ID

**File**: `repo/xxm_fans_backend/fansDIY/utils.py`

**Purpose**: Import fan-created works from Bilibili videos

**Complete Implementation**:

```python
from tools.bilibili import BilibiliAPIClient, BilibiliCoverDownloader, BilibiliAPIError
from fansDIY.models import Collection, Work

class FansDIYBilibiliImporter:
    """B站视频导入器（粉丝DIY）"""
    
    def __init__(self):
        self.api_client = BilibiliAPIClient(timeout=10, retry_times=3)
        self.cover_downloader = BilibiliCoverDownloader()
    
    def import_bv_work(self, bvid, collection_name, notes=""):
        """从B站BV号导入作品到指定合集"""
        print(f"[BV:{bvid}] 开始导入到合集: {collection_name}")
        
        try:
            # 1. 获取视频信息
            video_info = self.api_client.get_video_info(bvid)
            
            # 2. 下载封面
            cover_path = self.cover_downloader.download_by_collection(
                video_info.get_cover_url(),
                collection_name,
                video_info.get_publish_time()
            )
            
            if not cover_path:
                cover_path = video_info.get_cover_url()
            
            # 3. 获取或创建合集
            collection, _ = Collection.objects.get_or_create(
                name=collection_name,
                defaults={'description': f"Imported from BV: {bvid}"}
            )
            
            # 4. 创建作品
            view_url = f"https://player.bilibili.com/player.html?bvid={bvid}"
            
            work = Work.objects.create(
                collection=collection,
                title=video_info.title,
                url=view_url,
                cover_url=cover_path,
                author=video_info.get_author_name(),
                pubdate=video_info.get_publish_time(),
                notes=notes
            )
            
            print(f"[BV:{bvid}] 导入成功: {video_info.title}")
            return True, f"导入成功: {video_info.title}", work
            
        except BilibiliAPIError as e:
            print(f"[BV:{bvid}] API错误: {e.message}")
            return False, f"API错误: {e.message}", None
        except Exception as e:
            print(f"[BV:{bvid}] 导入失败: {e}")
            return False, f"导入失败: {str(e)}", None

# Convenience function
def import_bv_work(bvid, collection_name, notes=""):
    """从B站BV号导入作品到指定合集"""
    importer = FansDIYBilibiliImporter()
    return importer.import_bv_work(bvid, collection_name, notes)
```

## Use Case 3: Import Analytics Data from BV ID

**File**: `repo/xxm_fans_backend/data_analytics/services/bilibili_service.py`

**Purpose**: Import static video information for analytics

**Complete Implementation**:

```python
from tools.bilibili import BilibiliAPIClient, BilibiliCoverDownloader, BilibiliAPIError
from data_analytics.models import WorkStatic

class BilibiliWorkStaticImporter:
    """B站作品静态信息导入器"""
    
    def __init__(self):
        self.api_client = BilibiliAPIClient(timeout=10, retry_times=3)
        self.cover_downloader = BilibiliCoverDownloader()
    
    def import_bv_work_static(self, bvid):
        """导入B站视频的静态信息"""
        print(f"[BV:{bvid}] 开始导入作品静态信息")
        
        try:
            # 1. 获取视频信息
            video_info = self.api_client.get_video_info(bvid)
            
            # 2. 检查是否已存在
            if WorkStatic.objects.filter(platform="bilibili", work_id=bvid).exists():
                print(f"[BV:{bvid}] 作品已存在，跳过")
                return True, "作品已存在", None
            
            # 3. 下载封面
            cover_path = self.cover_downloader.download_by_bvid(
                video_info.get_cover_url(),
                bvid
            )
            
            if not cover_path:
                cover_path = video_info.get_cover_url()
            
            # 4. 创建WorkStatic记录
            work_static = WorkStatic.objects.create(
                platform="bilibili",
                work_id=bvid,
                title=video_info.title,
                author=video_info.get_author_name(),
                cover_url=cover_path,
                publish_time=video_info.get_publish_time(),
                view_count=video_info.get_view_count(),
                like_count=video_info.get_like_count(),
                danmaku_count=video_info.get_danmaku_count(),
                description=video_info.desc
            )
            
            print(f"[BV:{bvid}] 导入成功")
            return True, "导入成功", work_static
            
        except BilibiliAPIError as e:
            print(f"[BV:{bvid}] API错误: {e.message}")
            return False, f"API错误: {e.message}", None
        except Exception as e:
            print(f"[BV:{bvid}] 导入失败: {e}")
            return False, f"导入失败: {str(e)}", None
```

## Use Case 4: Fetch Follower Count

**File**: `spider/get_bilibili_fans_count.py`

**Purpose**: Get user follower count for monitoring

**Complete Implementation**:

```python
#!/usr/bin/env python3
"""B站粉丝数爬虫脚本"""

import sys
import json
import logging
from datetime import datetime
from tools.bilibili import BilibiliAPIClient, BilibiliAPIError

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def get_fans_count(uid):
    """获取用户粉丝数"""
    api_client = BilibiliAPIClient(timeout=10, retry_times=3)
    
    try:
        fans_data = api_client.get_fans_count(uid)
        return fans_data
    except BilibiliAPIError as e:
        logger.error(f"获取粉丝数失败: {e.message}")
        return None

def save_fans_data(uid, fans_data):
    """保存粉丝数数据"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    data = {
        "uid": uid,
        "follower": fans_data["follower"],
        "following": fans_data["following"],
        "timestamp": timestamp
    }
    
    filename = f"bilibili_fans_{uid}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    logger.info(f"数据已保存到: {filename}")

def main():
    if len(sys.argv) != 2:
        print("Usage: python get_bilibili_fans_count.py <uid>")
        sys.exit(1)
    
    uid = int(sys.argv[1])
    
    logger.info(f"开始获取用户 {uid} 的粉丝数")
    
    fans_data = get_fans_count(uid)
    
    if fans_data:
        logger.info(f"粉丝数: {fans_data['follower']:,}")
        logger.info(f"关注数: {fans_data['following']:,}")
        save_fans_data(uid, fans_data)
    else:
        logger.error("获取失败")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

## Usage

### Import Song Records

```python
from song_management.services.bilibili_import_service import BilibiliImporter

importer = BilibiliImporter()
results, remaining, conflict = importer.import_bv_song("BV1xx411c7mD")
```

### Import Fan Works

```python
from fansDIY.utils import import_bv_work

success, message, work = import_bv_work(
    bvid="BV1xx411c7mD",
    collection_name="My Collection",
    notes="Imported on 2025-01-29"
)
```

### Import Analytics Data

```python
from data_analytics.services.bilibili_service import BilibiliWorkStaticImporter

importer = BilibiliWorkStaticImporter()
success, message, work_static = importer.import_bv_work_static("BV1xx411c7mD")
```

### Fetch Follower Count

```bash
python spider/get_bilibili_fans_count.py 12345678
```

## Best Practices

1. **Handle all errors** - Wrap API calls in try-except
2. **Check return values** - Download methods can return None
3. **Log operations** - Record import operations for debugging
4. **Use transactions** - For database operations, use transactions
5. **Provide feedback** - Show progress and results to users