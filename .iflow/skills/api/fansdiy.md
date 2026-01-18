# fansDIY API Reference

## Module Overview

**Purpose**: Manage fan-created artwork collections and individual works

**Prefix**: `/api/fansDIY/`

**Views**: Class-based views using Django REST Framework

## Endpoints

### 1. Collection List

**Endpoint**: `GET /api/fansDIY/collections/`

**Description**: Get list of collections with pagination

**Query Parameters**:
- `page` - Page number (default: 1)
- `limit` - Items per page (default: 20)

**Example**:
```bash
GET /api/fansDIY/collections/?page=1&limit=20
```

**Response**:
```json
{
  "code": 200,
  "message": "获取合集列表成功",
  "data": {
    "total": 10,
    "page": 1,
    "page_size": 20,
    "results": [
      {
        "id": 1,
        "name": "插画合集",
        "works_count": 15,
        "display_order": 1,
        "position": 1,
        "created_at": "2024-01-01T00:00:00Z",
        "updated_at": "2024-12-31T00:00:00Z"
      }
    ]
  }
}
```

### 2. Collection Detail

**Endpoint**: `GET /api/fansDIY/collections/<collection_id>/`

**Description**: Get details of a specific collection

**Path Parameters**:
- `collection_id` - Collection ID (integer)

**Example**:
```bash
GET /api/fansDIY/collections/1/
```

**Response**:
```json
{
  "code": 200,
  "message": "获取合集详情成功",
  "data": {
    "id": 1,
    "name": "插画合集",
    "works_count": 15,
    "display_order": 1,
    "position": 1,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-12-31T00:00:00Z"
  }
}
```

### 3. Work List

**Endpoint**: `GET /api/fansDIY/works/`

**Description**: Get list of works with pagination and optional collection filter

**Query Parameters**:
- `page` - Page number (default: 1)
- `limit` - Items per page (default: 20)
- `collection` - Filter by collection ID (optional)

**Example**:
```bash
# Get all works
GET /api/fansDIY/works/?page=1&limit=20

# Get works from specific collection
GET /api/fansDIY/works/?collection=1&page=1
```

**Response**:
```json
{
  "code": 200,
  "message": "获取作品列表成功",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "results": [
      {
        "id": 1,
        "collection": 1,
        "title": "作品标题",
        "cover_url": "/footpath/...",
        "view_url": "https://www.bilibili.com/video/...",
        "author": "作者名",
        "notes": "作品备注",
        "display_order": 1,
        "position": 1
      }
    ]
  }
}
```

### 4. Work Detail

**Endpoint**: `GET /api/fansDIY/works/<work_id>/`

**Description**: Get details of a specific work

**Path Parameters**:
- `work_id` - Work ID (integer)

**Example**:
```bash
GET /api/fansDIY/works/1/
```

**Response**:
```json
{
  "code": 200,
  "message": "获取作品详情成功",
  "data": {
    "id": 1,
    "collection": 1,
    "title": "作品标题",
    "cover_url": "/footprint/...",
    "view_url": "https://www.bilibili.com/video/...",
    "author": "作者名",
    "notes": "作品备注",
    "display_order": 1,
    "position": 1
  }
}
```

## Common Use Cases

### Browse Collections
```bash
# Get all collections
GET /api/fansDIY/collections/

# Get paginated collections
GET /api/fansDIY/collections/?page=2&limit=10
```

### Browse Works
```bash
# Get all works
GET /api/fansDIY/works/

# Get works from specific collection
GET /api/fansDIY/works/?collection=1

# Get paginated works
GET /api/fansDIY/works/?page=1&limit=20
```

### Get Collection Details
```bash
# Get collection info
GET /api/fansDIY/collections/1/

# Then get works from that collection
GET /api/fansDIY/works/?collection=1
```

## Error Handling

### Collection Not Found
```json
{
  "code": 404,
  "message": "Collection not found",
  "errors": {}
}
```

### Work Not Found
```json
{
  "code": 404,
  "message": "Work not found",
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

- Works are automatically sorted by position, display_order, and id
- Collections are automatically sorted by position, display_order, and created_at
- works_count is automatically updated when works are added or removed
- Cover images are served from `/footprint/` path
- All timestamps are in ISO 8601 format