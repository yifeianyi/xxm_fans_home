# Bilibili API Client Module

## Module Overview

**Purpose**: Unified Bilibili API client with automatic error handling and retry mechanism

**Path**: `repo/xxm_fans_backend/tools/bilibili/api_client.py`

**Features**:
- Unified Bilibili API interface
- Automatic error handling and retry mechanism
- Support for multiple API endpoints
- Consistent response format

## Key Methods

### get_video_info(bvid: str) -> VideoInfo

Get video information from Bilibili.

**Parameters**:
- `bvid` (str): Bilibili video ID (e.g., "BV1xx411c7mD")

**Returns**: `VideoInfo` object

**Example**:
```python
video_info = api_client.get_video_info("BV1xx411c7mD")
print(video_info.title)
print(video_info.get_author_name())
print(video_info.get_view_count())
```

### get_video_pagelist(bvid: str) -> List[PageInfo]

Get video page list (for multi-part videos).

**Parameters**:
- `bvid` (str): Bilibili video ID

**Returns**: List of `PageInfo` objects

**Example**:
```python
pagelist = api_client.get_video_pagelist("BV1xx411c7mD")
for page in pagelist:
    print(f"Page {page.page}: {page.part}")
    print(f"Player URL: {page.get_player_url(bvid)}")
```

### get_fans_count(uid: int) -> Dict[str, Any]

Get user follower count.

**Parameters**:
- `uid` (int): Bilibili user ID

**Returns**: Dictionary with `follower` and `following` keys

**Example**:
```python
fans_data = api_client.get_fans_count(uid=12345678)
print(f"Followers: {fans_data['follower']}")
print(f"Following: {fans_data['following']}")
```

### batch_get_video_info(bvids: List[str]) -> Dict[str, VideoInfo]

Batch fetch video information for multiple BV IDs.

**Parameters**:
- `bvids` (List[str]): List of Bilibili video IDs

**Returns**: Dictionary mapping BV ID to VideoInfo object (or None if failed)

**Example**:
```python
results = api_client.batch_get_video_info(["BV1xx411c7mD", "BV1yy411c7mD"])
for bvid, info in results.items():
    if info:
        print(f"{bvid}: {info.title}")
    else:
        print(f"{bvid}: Failed to fetch")
```

## Initialization

```python
from tools.bilibili import BilibiliAPIClient

api_client = BilibiliAPIClient(
    timeout=10,          # Request timeout (seconds), default 10
    retry_times=3,       # Retry count, default 3
    retry_delay=1        # Retry delay (seconds), default 1
)
```

## Error Handling

All methods can raise `BilibiliAPIError`:

```python
from tools.bilibili import BilibiliAPIError

try:
    video_info = api_client.get_video_info("BV1xx411c7mD")
except BilibiliAPIError as e:
    print(f"API Error: {e.message}")
    print(f"Error Code: {e.code}")
```

## API Endpoints

| Method | Endpoint | Method Type |
|--------|----------|-------------|
| `get_video_info()` | `/x/web-interface/view` | GET |
| `get_video_pagelist()` | `/x/player/pagelist` | GET |
| `get_fans_count()` | `/x/relation/stat` | GET |

## Retry Mechanism

The API client has built-in retry logic:
- **Default retry times**: 3
- **Default retry delay**: 1 second
- **Retries on**: Network errors, timeouts, API errors (code != 0)

No need to implement your own retry logic.

## Configuration

### Default Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `timeout` | 10s | Request timeout |
| `retry_times` | 3 | Retry count |
| `retry_delay` | 1s | Retry delay |

### Custom Configuration

```python
api_client = BilibiliAPIClient(
    timeout=15,          # 15 seconds
    retry_times=5,       # 5 retries
    retry_delay=2        # 2 seconds delay
)
```

## Common Issues

### Issue: API Timeout

**Cause**: Network issues or Bilibili API slow response

**Solution**: The client automatically retries. If still fails, check network connectivity or increase timeout.

### Issue: Invalid BV ID

**Cause**: BV ID format is incorrect

**Solution**: Validate BV ID format before calling API:

```python
import re

if not re.match(r'^BV[a-zA-Z0-9]+$', bvid):
    raise ValueError("Invalid BV ID format")
```

### Issue: Rate Limiting

**Cause**: Too many requests in short time

**Solution**: Implement rate limiting or add delays between requests:

```python
import time

for bvid in bvid_list:
    video_info = api_client.get_video_info(bvid)
    time.sleep(1)  # Wait 1 second between requests
```

## Best Practices

1. **Always handle errors** - Wrap API calls in try-except
2. **Validate inputs** - Check BV ID format before API calls
3. **Use batch methods** - For multiple videos, use `batch_get_video_info()`
4. **Implement rate limiting** - Avoid hitting Bilibili rate limits
5. **Log errors** - Record API errors for debugging

## Complete Example

```python
from tools.bilibili import BilibiliAPIClient, BilibiliAPIError
import logging

logger = logging.getLogger(__name__)

def fetch_video_info(bvid):
    """Fetch video info with error handling"""
    api_client = BilibiliAPIClient(timeout=10, retry_times=3)
    
    try:
        video_info = api_client.get_video_info(bvid)
        logger.info(f"Successfully fetched: {video_info.title}")
        return video_info
    except BilibiliAPIError as e:
        logger.error(f"Failed to fetch {bvid}: {e.message}")
        return None
```