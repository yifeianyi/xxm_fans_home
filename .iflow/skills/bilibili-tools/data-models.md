# Data Models Module

## Module Overview

**Purpose**: Data model classes for Bilibili API responses

**Path**: `repo/xxm_fans_backend/tools/bilibili/models.py`

**Models**:
- `VideoInfo` - Video information data class
- `PageInfo` - Page (multi-part) information data class
- `BilibiliAPIError` - API error exception class

## VideoInfo Class

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `bvid` | str | Bilibili video ID |
| `title` | str | Video title |
| `pic` | str | Cover image URL |
| `owner` | dict | Author information |
| `pubdate` | int | Publish timestamp |
| `desc` | str | Video description |
| `duration` | int | Video duration (seconds) |
| `stat` | dict | Statistics data |

### Methods

#### get_cover_url() -> str

Get the cover image URL.

**Returns**: Cover URL string

**Example**:
```python
cover_url = video_info.get_cover_url()
```

#### get_author_name() -> str

Get the author (uploader) name.

**Returns**: Author name string

**Example**:
```python
author_name = video_info.get_author_name()
```

#### get_author_mid() -> int

Get the author's Bilibili user ID.

**Returns**: User ID integer

**Example**:
```python
author_mid = video_info.get_author_mid()
```

#### get_publish_time() -> datetime

Get the publish time as a datetime object.

**Returns**: `datetime.datetime` object

**Example**:
```python
from datetime import datetime

publish_time = video_info.get_publish_time()
print(f"Published: {publish_time.strftime('%Y-%m-%d %H:%M:%S')}")
```

#### get_view_count() -> int

Get the view/play count.

**Returns**: Integer view count

**Example**:
```python
view_count = video_info.get_view_count()
print(f"Views: {view_count:,}")
```

#### get_danmaku_count() -> int

Get the danmaku (bullet comment) count.

**Returns**: Integer danmaku count

**Example**:
```python
danmaku_count = video_info.get_danmaku_count()
```

#### get_like_count() -> int

Get the like count.

**Returns**: Integer like count

**Example**:
```python
like_count = video_info.get_like_count()
```

### Creation

```python
from tools.bilibili import VideoInfo

# From dictionary (API response)
video_info = VideoInfo.from_dict(api_response_data)
```

### Usage Example

```python
# Get video info
video_info = api_client.get_video_info("BV1xx411c7mD")

# Access properties
print(f"Title: {video_info.title}")
print(f"Author: {video_info.get_author_name()}")
print(f"Cover: {video_info.get_cover_url()}")
print(f"Published: {video_info.get_publish_time()}")
print(f"Views: {video_info.get_view_count():,}")
print(f"Likes: {video_info.get_like_count():,}")
```

## PageInfo Class

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `page` | int | Page number (starting from 1) |
| `cid` | int | Content ID (for video playback) |
| `part` | str | Page title |
| `duration` | int | Page duration (seconds) |

### Methods

#### get_player_url(bvid: str) -> str

Get the Bilibili player URL for this page.

**Parameters**:
- `bvid` (str): Bilibili video ID

**Returns**: Player URL string

**Example**:
```python
player_url = page_info.get_player_url("BV1xx411c7mD")
# Returns: "https://player.bilibili.com/player.html?bvid=BV1xx411c7mD&p=1"
```

### Creation

```python
from tools.bilibili import PageInfo

# From dictionary (API response)
page_info = PageInfo.from_dict(api_response_data)
```

### Usage Example

```python
# Get page list
pagelist = api_client.get_video_pagelist("BV1xx411c7mD")

for page in pagelist:
    print(f"Page {page.page}: {page.part}")
    print(f"Duration: {page.duration}s")
    print(f"Player URL: {page.get_player_url('BV1xx411c7mD')}")
    print("---")
```

## BilibiliAPIError Exception

### Attributes

| Attribute | Type | Description |
|-----------|------|-------------|
| `message` | str | Error message |
| `code` | int | Bilibili API error code |

### Usage

```python
from tools.bilibili import BilibiliAPIError

try:
    video_info = api_client.get_video_info("BV1xx411c7mD")
except BilibiliAPIError as e:
    print(f"Error: {e.message}")
    print(f"Code: {e.code}")
```

### Common Error Codes

| Code | Description |
|------|-------------|
| -400 | Request error |
| -403 | Permission denied |
| -404 | Video not found |
| -412 | Pre-request failed |

## Complete Example

```python
from tools.bilibili import BilibiliAPIClient, BilibiliAPIError, VideoInfo, PageInfo

def process_video(bvid):
    """Process video information and pages"""
    api_client = BilibiliAPIClient()
    
    try:
        # Get video info
        video_info = api_client.get_video_info(bvid)
        
        # Display video info
        print(f"Video: {video_info.title}")
        print(f"Author: {video_info.get_author_name()}")
        print(f"Published: {video_info.get_publish_time()}")
        print(f"Views: {video_info.get_view_count():,}")
        
        # Get page list
        pagelist = api_client.get_video_pagelist(bvid)
        
        # Display pages
        print(f"\nPages ({len(pagelist)}):")
        for page in pagelist:
            print(f"  {page.page}. {page.part} ({page.duration}s)")
            print(f"     {page.get_player_url(bvid)}")
        
        return video_info, pagelist
        
    except BilibiliAPIError as e:
        print(f"Error processing {bvid}: {e.message}")
        return None, []
```

## Best Practices

1. **Use getter methods** - Use `get_author_name()` instead of accessing `owner['name']` directly
2. **Convert timestamps** - Use `get_publish_time()` to get datetime object
3. **Format numbers** - Use format specifiers for large numbers (e.g., `f"{count:,}"`)
4. **Handle missing data** - Some fields may be empty, handle gracefully
5. **Validate data** - Check if expected data exists before using

## Data Flow

```
API Response (JSON)
    ↓
VideoInfo.from_dict()
    ↓
VideoInfo Object
    ↓
Getter Methods (get_author_name(), get_publish_time(), etc.)
    ↓
Formatted Data
```