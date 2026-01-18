# site_settings API Reference

## Module Overview

**Purpose**: Manage global website settings and recommendations

**Prefix**: `/api/site-settings/` and `/api/recommendation/`

**Views**: Class-based views using Django REST Framework

## Endpoints

### 1. Site Settings (GET)

**Endpoint**: `GET /api/site-settings/settings/`

**Description**: Get current website settings

**Example**:
```bash
GET /api/site-settings/settings/
```

**Response**:
```json
{
  "code": 200,
  "message": "获取网站设置成功",
  "data": {
    "id": 1,
    "favicon": "/media/settings/favicon.ico",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-12-31T00:00:00Z"
  }
}
```

### 2. Site Settings (POST)

**Endpoint**: `POST /api/site-settings/settings/`

**Description**: Create new website settings

**Request Body**:
```json
{
  "favicon": "<file data>"
}
```

**Example**:
```bash
POST /api/site-settings/settings/
Content-Type: multipart/form-data

favicon: <file>
```

**Response**:
```json
{
  "code": 201,
  "message": "创建网站设置成功",
  "data": {
    "id": 1,
    "favicon": "/media/settings/favicon.ico",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-12-31T00:00:00Z"
  }
}
```

### 3. Site Settings (PUT)

**Endpoint**: `PUT /api/site-settings/settings/`

**Description**: Update existing website settings

**Request Body**:
```json
{
  "favicon": "<file data>"
}
```

**Example**:
```bash
PUT /api/site-settings/settings/
Content-Type: multipart/form-data

favicon: <file>
```

**Response**:
```json
{
  "code": 200,
  "message": "更新网站设置成功",
  "data": {
    "id": 1,
    "favicon": "/media/settings/favicon.ico",
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-12-31T00:00:00Z"
  }
}
```

### 4. Recommendation List (Root)

**Endpoint**: `GET /api/recommendation/`

**Description**: Get list of active recommendations

**Query Parameters**:
- `is_active` - Filter by active status (true/false)
- `all` - Get all recommendations including inactive (true/false)

**Example**:
```bash
# Get active recommendations
GET /api/recommendation/

# Get all recommendations
GET /api/recommendation/?all=true

# Get inactive recommendations
GET /api/recommendation/?is_active=false
```

**Response**:
```json
{
  "code": 200,
  "message": "获取推荐语列表成功",
  "data": [
    {
      "id": 1,
      "content": "欢迎来到XXM粉丝之家！",
      "recommended_songs": [1, 2, 3],
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-12-31T00:00:00Z"
    }
  ]
}
```

### 5. Recommendation List (Detailed)

**Endpoint**: `GET /api/site-settings/recommendations/`

**Description**: Get list of recommendations with filtering

**Query Parameters**:
- `is_active` - Filter by active status (true/false)
- `all` - Get all recommendations including inactive (true/false)

**Example**:
```bash
GET /api/site-settings/recommendations/?all=true
```

**Response**:
```json
{
  "code": 200,
  "message": "获取推荐语列表成功",
  "data": [
    {
      "id": 1,
      "content": "欢迎来到XXM粉丝之家！",
      "recommended_songs": [1, 2, 3],
      "is_active": true,
      "created_at": "2024-01-01T00:00:00Z",
      "updated_at": "2024-12-31T00:00:00Z"
    }
  ]
}
```

### 6. Recommendation Detail

**Endpoint**: `GET /api/site-settings/recommendations/<pk>/`

**Description**: Get details of a specific recommendation

**Path Parameters**:
- `pk` - Recommendation ID (integer)

**Example**:
```bash
GET /api/site-settings/recommendations/1/
```

**Response**:
```json
{
  "code": 200,
  "message": "获取推荐语详情成功",
  "data": {
    "id": 1,
    "content": "欢迎来到XXM粉丝之家！",
    "recommended_songs": [1, 2, 3],
    "is_active": true,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-12-31T00:00:00Z"
  }
}
```

### 7. Create Recommendation

**Endpoint**: `POST /api/site-settings/recommendations/`

**Description**: Create a new recommendation

**Request Body**:
```json
{
  "content": "新的推荐语",
  "recommended_songs": [1, 2, 3],
  "is_active": true
}
```

**Example**:
```bash
POST /api/site-settings/recommendations/
Content-Type: application/json

{
  "content": "新的推荐语",
  "recommended_songs": [1, 2, 3],
  "is_active": true
}
```

**Response**:
```json
{
  "code": 201,
  "message": "创建推荐语成功",
  "data": {
    "id": 2,
    "content": "新的推荐语",
    "recommended_songs": [1, 2, 3],
    "is_active": true,
    "created_at": "2024-12-31T00:00:00Z",
    "updated_at": "2024-12-31T00:00:00Z"
  }
}
```

### 8. Update Recommendation

**Endpoint**: `PUT /api/site-settings/recommendations/<pk>/`

**Description**: Update an existing recommendation

**Path Parameters**:
- `pk` - Recommendation ID (integer)

**Request Body**:
```json
{
  "content": "更新后的推荐语",
  "recommended_songs": [1, 2, 3],
  "is_active": false
}
```

**Example**:
```bash
PUT /api/site-settings/recommendations/1/
Content-Type: application/json

{
  "content": "更新后的推荐语",
  "recommended_songs": [1, 2, 3],
  "is_active": false
}
```

**Response**:
```json
{
  "code": 200,
  "message": "更新推荐语成功",
  "data": {
    "id": 1,
    "content": "更新后的推荐语",
    "recommended_songs": [1, 2, 3],
    "is_active": false,
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-12-31T00:00:00Z"
  }
}
```

### 9. Delete Recommendation

**Endpoint**: `DELETE /api/site-settings/recommendations/<pk>/`

**Description**: Delete a recommendation

**Path Parameters**:
- `pk` - Recommendation ID (integer)

**Example**:
```bash
DELETE /api/site-settings/recommendations/1/
```

**Response**:
```json
{
  "code": 200,
  "message": "删除推荐语成功",
  "data": null
}
```

## Common Use Cases

### Get Website Settings
```bash
GET /api/site-settings/settings/
```

### Update Favicon
```bash
PUT /api/site-settings/settings/
Content-Type: multipart/form-data

favicon: <file>
```

### Get Active Recommendations
```bash
GET /api/recommendation/
```

### Create New Recommendation
```bash
POST /api/site-settings/recommendations/
Content-Type: application/json

{
  "content": "欢迎来到XXM粉丝之家！",
  "recommended_songs": [1, 2, 3],
  "is_active": true
}
```

### Toggle Recommendation Status
```bash
PUT /api/site-settings/recommendations/1/
Content-Type: application/json

{
  "is_active": false
}
```

## Error Handling

### Settings Not Found
```json
{
  "code": 404,
  "message": "网站设置不存在",
  "errors": {}
}
```

### Invalid File Format
```json
{
  "code": 400,
  "message": "Invalid file format",
  "errors": {
    "favicon": "File must be an image"
  }
}
```

### Validation Error
```json
{
  "code": 400,
  "message": "Validation error",
  "errors": {
    "content": "This field is required"
  }
}
```

## Special Notes

- Site settings follow singleton pattern (only one record)
- Favicon is uploaded to `/media/settings/` directory
- Recommendations support many-to-many relationship with songs
- By default, only active recommendations are returned
- Use `?all=true` to get all recommendations including inactive
- Timestamps are in ISO 8601 format