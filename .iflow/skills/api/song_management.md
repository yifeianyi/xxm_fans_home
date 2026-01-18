# song_management API Reference

## Module Overview

**Purpose**: Manage songs, performance records, styles, and tags

**Prefix**: `/api/`

**Views**: Class-based views using Django REST Framework

## Endpoints

### 1. Song List

**Endpoint**: `GET /api/songs/`

**Description**: Get list of songs with filtering, pagination, and sorting

**Query Parameters**:
- `q` - Search query (searches song_name and singer)
- `page` - Page number (default: 1)
- `limit` - Items per page (default: 20)
- `language` - Filter by language (comma-separated, e.g., "中文,英文")
- `styles` - Filter by styles (comma-separated, e.g., "流行,摇滚")
- `tags` - Filter by tags (comma-separated, e.g., "原创,翻唱")
- `ordering` - Sort field (options: singer, last_performed, perform_count, first_performed; prefix with `-` for descending)

**Example**:
```bash
GET /api/songs/?q=晴天&language=中文&page=1&limit=20
```

**Response**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "results": [
      {
        "id": 1,
        "song_name": "晴天",
        "singer": "周杰伦",
        "language": "中文",
        "first_perform": "2024-01-01",
        "last_performed": "2024-12-31",
        "perform_count": 10,
        "styles": ["流行"],
        "tags": ["翻唱"]
      }
    ]
  }
}
```

### 2. Song Records List

**Endpoint**: `GET /api/songs/<song_id>/records/`

**Description**: Get performance records for a specific song

**Path Parameters**:
- `song_id` - Song ID (integer)

**Query Parameters**:
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20)

**Example**:
```bash
GET /api/songs/1/records/?page=1
```

**Response**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 10,
    "page": 1,
    "page_size": 20,
    "results": [
      {
        "id": 1,
        "song": 1,
        "performed_at": "2024-12-31",
        "url": "https://www.bilibili.com/video/...",
        "notes": "精彩演出",
        "cover_url": "/covers/..."
      }
    ]
  }
}
```

### 3. Style List

**Endpoint**: `GET /api/styles/`

**Description**: Get list of all music styles

**Example**:
```bash
GET /api/styles/
```

**Response**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "name": "流行",
      "description": "流行音乐"
    },
    {
      "id": 2,
      "name": "摇滚",
      "description": "摇滚音乐"
    }
  ]
}
```

### 4. Tag List

**Endpoint**: `GET /api/tags/`

**Description**: Get list of all tags

**Example**:
```bash
GET /api/tags/
```

**Response**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "name": "原创",
      "description": "原创作品"
    },
    {
      "id": 2,
      "name": "翻唱",
      "description": "翻唱作品"
    }
  ]
}
```

### 5. Top Songs

**Endpoint**: `GET /api/top_songs/`

**Description**: Get top songs by performance count

**Query Parameters**:
- `range` - Time range (options: 7days, 30days, 90days, all)
- `limit` - Number of results (default: 10)

**Example**:
```bash
GET /api/top_songs/?range=30days&limit=10
```

**Response**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "song_name": "晴天",
      "singer": "周杰伦",
      "perform_count": 15
    }
  ]
}
```

### 6. Random Song

**Endpoint**: `GET /api/random-song/`

**Description**: Get a random song

**Example**:
```bash
GET /api/random-song/
```

**Response**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "song_name": "晴天",
    "singer": "周杰伦",
    "language": "中文"
  }
}
```

## Common Use Cases

### Search Songs
```bash
# Search by name or singer
GET /api/songs/?q=周杰伦

# Search with filters
GET /api/songs/?q=晴天&language=中文&styles=流行
```

### Get Song Performance History
```bash
# Get all records for a song
GET /api/songs/1/records/

# Get paginated records
GET /api/songs/1/records/?page=1&page_size=20
```

### Get Popular Songs
```bash
# Top 10 songs in last 30 days
GET /api/top_songs/?range=30days&limit=10

# Top 20 songs all time
GET /api/top_songs/?range=all&limit=20
```

## Error Handling

### Song Not Found
```json
{
  "code": 404,
  "message": "Song not found",
  "errors": {}
}
```

### Invalid Parameters
```json
{
  "code": 400,
  "message": "Invalid parameters",
  "errors": {
    "page": "Page must be a positive integer"
  }
}
```

## Special Notes

- All list endpoints support pagination
- Search is case-insensitive
- Multiple values for language, styles, tags should be comma-separated
- Default ordering is by last_performed (descending)
- Styles and tags are returned as arrays in song objects