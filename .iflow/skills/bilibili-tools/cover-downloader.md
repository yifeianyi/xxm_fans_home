# Cover Downloader Module

## Module Overview

**Purpose**: Unified cover download interface with multiple download strategies

**Path**: `repo/xxm_fans_backend/tools/bilibili/cover_downloader.py`

**Features**:
- Unified cover download interface
- Support for multiple path configurations
- Automatic file existence check
- File size limit (default 10MB)
- Error handling

## Initialization

```python
from tools.bilibili import BilibiliCoverDownloader

downloader = BilibiliCoverDownloader(
    base_dir=settings.MEDIA_ROOT,  # Base directory, default Django MEDIA_ROOT
    timeout=10,                    # Download timeout (seconds), default 10
    max_size=10 * 1024 * 1024      # Max file size (bytes), default 10MB
)
```

## Download Methods

### download_by_date(cover_url, performed_date, filename=None)

Download cover for song records (organized by date).

**Parameters**:
- `cover_url` (str): Cover image URL
- `performed_date` (datetime): Performance date
- `filename` (str, optional): Custom filename (default: "YYYY-MM-DD.jpg")

**Returns**: Relative path string or `None` on failure

**Storage Path**: `covers/YYYY/MM/YYYY-MM-DD.jpg`

**Example**:
```python
from datetime import datetime

performed_date = datetime(2025, 1, 15)
cover_path = downloader.download_by_date(
    cover_url="https://example.com/cover.jpg",
    performed_date=performed_date
)
# Returns: "covers/2025/01/2025-01-15.jpg"

if cover_path:
    print(f"Cover saved: {cover_path}")
else:
    print("Download failed")
```

### download_by_bvid(cover_url, bvid)

Download cover for analytics (organized by BV ID).

**Parameters**:
- `cover_url` (str): Cover image URL
- `bvid` (str): Bilibili video ID

**Returns**: Relative path string or `None` on failure

**Storage Path**: `views/BVxxxxxx.jpg`

**Example**:
```python
cover_path = downloader.download_by_bvid(
    cover_url="https://example.com/cover.jpg",
    bvid="BV1xx411c7mD"
)
# Returns: "views/BV1xx411c7mD.jpg"
```

### download_by_collection(cover_url, collection_name, pubdate)

Download cover for fan works (organized by collection).

**Parameters**:
- `cover_url` (str): Cover image URL
- `collection_name` (str): Collection/folder name
- `pubdate` (datetime): Publish date

**Returns**: Relative path string or `None` on failure

**Storage Path**: `footprint/Collection/{collection_name}/YYYY-MM-DD.jpg`

**Example**:
```python
from datetime import datetime

pubdate = datetime(2025, 1, 15)
cover_path = downloader.download_by_collection(
    cover_url="https://example.com/cover.jpg",
    collection_name="My Collection",
    pubdate=pubdate
)
# Returns: "footprint/Collection/My Collection/2025-01-15.jpg"
```

### download(cover_url, sub_path, filename, check_exists=True)

Generic download method for custom paths.

**Parameters**:
- `cover_url` (str): Cover image URL
- `sub_path` (str): Subdirectory path (e.g., "covers/2025/01")
- `filename` (str): File name
- `check_exists` (bool): Whether to check if file already exists

**Returns**: Relative path string or `None` on failure

**Example**:
```python
cover_path = downloader.download(
    cover_url="https://example.com/cover.jpg",
    sub_path="custom/path",
    filename="my_cover.jpg",
    check_exists=True
)
# Returns: "custom/path/my_cover.jpg"
```

## Choosing the Right Method

| Use Case | Method | Storage Path |
|----------|--------|--------------|
| Song covers | `download_by_date()` | `covers/YYYY/MM/` |
| Analytics | `download_by_bvid()` | `views/` |
| Fan works | `download_by_collection()` | `footprint/Collection/` |
| Custom | `download()` | Custom path |

## Configuration

### Default Parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| `base_dir` | `settings.MEDIA_ROOT` | Base directory for downloads |
| `timeout` | 10s | Download timeout |
| `max_size` | 10MB | Maximum file size |

### Custom Configuration

```python
downloader = BilibiliCoverDownloader(
    base_dir="/custom/path",         # Custom base directory
    timeout=15,                      # 15 seconds timeout
    max_size=20 * 1024 * 1024       # 20MB max size
)
```

## Return Values

All download methods return:
- **Success**: Relative path string (e.g., "covers/2025/01/2025-01-15.jpg")
- **Failure**: `None`

Always check the return value:

```python
cover_path = downloader.download_by_date(cover_url, date)
if cover_path is None:
    # Handle failure
    cover_path = cover_url  # Use fallback
```

## File Existence Check

By default, download methods check if file already exists and skip download:

```python
# First call - downloads file
cover_path = downloader.download_by_date(cover_url, date)

# Second call - skips download, returns existing path
cover_path = downloader.download_by_date(cover_url, date)
```

To force re-download:

```python
cover_path = downloader.download(
    cover_url=cover_url,
    sub_path="covers/2025/01",
    filename="2025-01-15.jpg",
    check_exists=False  # Force re-download
)
```

## Common Issues

### Issue 1: Download Returns None

**Possible Causes**:
- File size exceeds limit (10MB)
- Network error
- Invalid URL
- Permission denied

**Solution**:
```python
cover_path = downloader.download_by_date(cover_url, date)
if cover_path is None:
    # Use fallback URL
    cover_path = cover_url
    # Or skip the operation
    continue
```

### Issue 2: File Permission Error

**Cause**: No write permission to base directory

**Solution**: Ensure Django MEDIA_ROOT has write permissions:

```bash
chmod -R 755 media/
```

### Issue 3: Slow Download

**Cause**: Network issues or large file size

**Solution**: Increase timeout:

```python
downloader = BilibiliCoverDownloader(timeout=30)
```

## Best Practices

1. **Always check return value** - Methods return `None` on failure
2. **Use appropriate method** - Match method to use case
3. **Handle fallback** - Have a fallback URL for failed downloads
4. **Validate URLs** - Check cover URL before downloading
5. **Log errors** - Record download failures for debugging

## Complete Example

```python
from tools.bilibili import BilibiliCoverDownloader
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def download_song_cover(cover_url, performed_date):
    """Download song cover with error handling"""
    downloader = BilibiliCoverDownloader(
        base_dir=settings.MEDIA_ROOT,
        timeout=15,
        max_size=10 * 1024 * 1024
    )
    
    try:
        cover_path = downloader.download_by_date(
            cover_url=cover_url,
            performed_date=performed_date
        )
        
        if cover_path:
            logger.info(f"Cover downloaded: {cover_path}")
            return cover_path
        else:
            logger.warning(f"Download failed, using original URL: {cover_url}")
            return cover_url
            
    except Exception as e:
        logger.error(f"Download error: {e}")
        return cover_url
```

## Storage Structure

```
media/
├── covers/
│   ├── 2025/
│   │   ├── 01/
│   │   │   ├── 2025-01-15.jpg
│   │   │   └── 2025-01-20.jpg
│   │   └── 02/
│   │       └── 2025-02-10.jpg
│   └── 2026/
│       └── 01/
│           └── 2026-01-05.jpg
├── views/
│   ├── BV1xx411c7mD.jpg
│   ├── BV1yy411c7mD.jpg
│   └── ...
└── footprint/
    └── Collection/
        ├── Collection A/
        │   ├── 2025-01-15.jpg
        │   └── 2025-01-20.jpg
        └── Collection B/
            └── 2025-02-10.jpg
```