# data_analytics API Reference

## Module Overview

**Purpose**: Track data analytics and metrics for works

**Prefix**: `/api/data-analytics/`

**Views**: Class-based views using Django REST Framework

## Endpoints

### 1. Works List

**Endpoint**: `GET /api/data-analytics/works/`

**Description**: Get list of works with static information

**Example**:
```bash
GET /api/data-analytics/works/
```

**Response**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "platform": "bilibili",
      "work_id": "BV1234567890",
      "title": "作品标题",
      "related_song": 1
    }
  ]
}
```

### 2. Work Detail

**Endpoint**: `GET /api/data-analytics/works/<platform>/<work_id>/`

**Description**: Get detailed information about a specific work

**Path Parameters**:
- `platform` - Platform name (e.g., "bilibili")
- `work_id` - Work ID (e.g., "BV1234567890")

**Example**:
```bash
GET /api/data-analytics/works/bilibili/BV1234567890/
```

**Response**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "platform": "bilibili",
    "work_id": "BV1234567890",
    "title": "作品标题",
    "related_song": 1,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-12-31T00:00:00Z"
  }
}
```

### 3. Work Metrics

**Endpoint**: `GET /api/data-analytics/works/<platform>/<work_id>/metrics/`

**Description**: Get hourly metrics for a specific work

**Path Parameters**:
- `platform` - Platform name
- `work_id` - Work ID

**Query Parameters**:
- `page` - Page number (default: 1)
- `page_size` - Items per page (default: 20)

**Example**:
```bash
GET /api/data-analytics/works/bilibili/BV1234567890/metrics/?page=1
```

**Response**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 24,
    "page": 1,
    "page_size": 20,
    "results": [
      {
        "hour": "2024-12-31T00:00:00Z",
        "views": 1000,
        "likes": 50,
        "comments": 10
      }
    ]
  }
}
```

### 4. Work Metrics Summary

**Endpoint**: `GET /api/data-analytics/works/<platform>/<work_id>/metrics/summary/`

**Description**: Get summary statistics for a specific work

**Path Parameters**:
- `platform` - Platform name
- `work_id` - Work ID

**Example**:
```bash
GET /api/data-analytics/works/bilibili/BV1234567890/metrics/summary/
```

**Response**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total_views": 100000,
    "total_likes": 5000,
    "total_comments": 1000,
    "average_views_per_hour": 4167,
    "peak_views_hour": "2024-12-31T20:00:00Z",
    "peak_views_count": 10000
  }
}
```

### 5. Platform Statistics

**Endpoint**: `GET /api/data-analytics/platform/<platform>/statistics/`

**Description**: Get overall statistics for a specific platform

**Path Parameters**:
- `platform` - Platform name (e.g., "bilibili")

**Example**:
```bash
GET /api/data-analytics/platform/bilibili/statistics/
```

**Response**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "platform": "bilibili",
    "total_works": 100,
    "total_views": 1000000,
    "total_likes": 50000,
    "total_comments": 10000,
    "average_views_per_work": 10000,
    "average_likes_per_work": 500,
    "average_comments_per_work": 100
  }
}
```

### 6. Top Works

**Endpoint**: `GET /api/data-analytics/platform/<platform>/top-works/`

**Description**: Get top works on a specific platform

**Path Parameters**:
- `platform` - Platform name

**Query Parameters**:
- `limit` - Number of results (default: 10)
- `sort_by` - Sort field (options: views, likes, comments)

**Example**:
```bash
GET /api/data-analytics/platform/bilibili/top-works/?limit=10&sort_by=views
```

**Response**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "platform": "bilibili",
      "work_id": "BV1234567890",
      "title": "作品标题",
      "views": 100000,
      "likes": 5000,
      "comments": 1000
    }
  ]
}
```

### 7. Crawl Sessions

**Endpoint**: `GET /api/data-analytics/sessions/`

**Description**: Get list of crawl sessions

**Example**:
```bash
GET /api/data-analytics/sessions/
```

**Response**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "platform": "bilibili",
      "started_at": "2024-12-31T00:00:00Z",
      "ended_at": "2024-12-31T01:00:00Z",
      "status": "completed",
      "works_crawled": 100
    }
  ]
}
```

## Common Use Cases

### Track Work Performance
```bash
# Get work details
GET /api/data-analytics/works/bilibili/BV1234567890/

# Get work metrics
GET /api/data-analytics/works/bilibili/BV1234567890/metrics/

# Get summary statistics
GET /api/data-analytics/works/bilibili/BV1234567890/metrics/summary/
```

### Monitor Platform Statistics
```bash
# Get platform statistics
GET /api/data-analytics/platform/bilibili/statistics/

# Get top works
GET /api/data-analytics/platform/bilibili/top-works/?limit=10&sort_by=views
```

### Review Crawl Sessions
```bash
GET /api/data-analytics/sessions/
```

## Error Handling

### Work Not Found
```json
{
  "code": 404,
  "message": "Work not found",
  "errors": {}
}
```

### Invalid Platform
```json
{
  "code": 400,
  "message": "Invalid platform",
  "errors": {
    "platform": "Platform must be one of: bilibili, youtube"
  }
}
```

### No Metrics Available
```json
{
  "code": 404,
  "message": "No metrics available for this work",
  "errors": {}
}
```

## Special Notes

- Work IDs are platform-specific (e.g., BV codes for Bilibili)
- Metrics are tracked hourly
- Multiple platforms are supported (bilibili, youtube, etc.)
- Works can be linked to songs via related_song field
- Crawl sessions track data collection activities
- All timestamps are in ISO 8601 format
- Metrics summary provides aggregated statistics