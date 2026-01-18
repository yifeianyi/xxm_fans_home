# bilibili_fans API Reference

## Module Overview

**Purpose**: Track Bilibili fan count over time

**Prefix**: `/api/`

**Views**: Function-based views

## Endpoints

### 1. Fans Data View

**Endpoint**: `GET /api/fans-data/`

**Description**: Get Bilibili fan count data

**Example**:
```bash
GET /api/fans-data/
```

**Response**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "uid": "123456789",
      "username": "用户名",
      "fans_count": 10000,
      "recorded_at": "2024-12-31T00:00:00Z"
    }
  ]
}
```

### 2. Latest API

**Endpoint**: `GET /api/latest/`

**Description**: Get latest fan count data

**Example**:
```bash
GET /api/latest/
```

**Response**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "uid": "123456789",
    "username": "用户名",
    "fans_count": 10000,
    "recorded_at": "2024-12-31T00:00:00Z"
  }
}
```

## Common Use Cases

### Get Fan Count History
```bash
GET /api/fans-data/
```

### Get Latest Fan Count
```bash
GET /api/latest/
```

## Error Handling

### No Data Available
```json
{
  "code": 404,
  "message": "No fan data available",
  "errors": {}
}
```

### API Error
```json
{
  "code": 500,
  "message": "Failed to fetch fan data",
  "errors": {}
}
```

## Special Notes

- This module tracks fan count for Bilibili accounts
- Data is typically updated via scheduled tasks (cron)
- Fan count is recorded periodically to track growth over time
- Simple API with minimal functionality
- Primarily used for monitoring and analytics
- No authentication required (public data)
- Timestamps are in ISO 8601 format