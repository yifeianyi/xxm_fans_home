---
name: api-reference
description: Complete reference guide for XXM Fans Home backend API endpoints, organized by module
---

This skill provides comprehensive documentation for all backend API endpoints in the XXM Fans Home project.

## API Architecture Overview

The XXM Fans Home backend uses Django REST Framework with a modular API structure. All API endpoints are prefixed with `/api/`.

### Base URL
```
http://localhost:8080/api/
```

### Available API Modules

1. **[song_management](./song_management.md)** - Core Music Management API
   - Purpose: Manage songs, records, styles, and tags
   - Prefix: `/api/`

2. **[fansDIY](./fansdiy.md)** - Fan-created Content API
   - Purpose: Manage collections and works
   - Prefix: `/api/fansDIY/`

3. **[site_settings](./site_settings.md)** - Website Settings API
   - Purpose: Manage site settings and recommendations
   - Prefix: `/api/site-settings/`

4. **[data_analytics](./data_analytics.md)** - Data Analytics API
   - Purpose: Track data analytics and metrics
   - Prefix: `/api/data-analytics/`

5. **[songlist](./songlist.md)** - Template-based Song List API
   - Purpose: Lightweight song lists for artists
   - Prefix: `/api/songlist/`

6. **[bilibili_fans](./bilibili_fans.md)** - Bilibili Fans Data API
   - Purpose: Track Bilibili fan count
   - Prefix: `/api/`

## Common Response Format

All API endpoints follow a unified response format:

### Success Response
```json
{
  "code": 200,
  "message": "success",
  "data": {}
}
```

### Paginated Response
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "results": []
  }
}
```

### Error Response
```json
{
  "code": 400,
  "message": "error message",
  "errors": {}
}
```

### HTTP Status Codes
- `200` - Success
- `201` - Created
- `400` - Bad Request
- `404` - Not Found
- `500` - Internal Server Error

## Common Query Parameters

### Pagination
- `page` - Page number (default: 1)
- `limit` - Items per page (default: 20)

### Filtering
- `q` - Search query
- `language` - Filter by language (comma-separated)
- `styles` - Filter by styles (comma-separated)
- `tags` - Filter by tags (comma-separated)

### Sorting
- `ordering` - Sort field (prefix with `-` for descending)

## Usage

When working with APIs:

1. **Identify the module** - Determine which API module you need
2. **Read the module guide** - Access the corresponding .md file for detailed endpoints
3. **Check response format** - All endpoints use unified response format
4. **Handle errors** - Check error codes and messages

## Quick Reference

### Song Management APIs
→ Read [song_management.md](./song_management.md)

### Fan-created Content APIs
→ Read [fansdiy.md](./fansdiy.md)

### Website Settings APIs
→ Read [site_settings.md](./site_settings.md)

### Data Analytics APIs
→ Read [data_analytics.md](./data_analytics.md)

### Song List APIs
→ Read [songlist.md](./songlist.md)

### Bilibili Fans APIs
→ Read [bilibili_fans.md](./bilibili_fans.md)

## API Testing

### Using curl
```bash
# Get song list
curl http://localhost:8080/api/songs/

# Get specific song
curl http://localhost:8080/api/songs/1/

# Filter by language
curl http://localhost:8080/api/songs/?language=中文

# Search
curl http://localhost:8080/api/songs/?q=晴天
```

### Using Python requests
```python
import requests

# Get song list
response = requests.get('http://localhost:8080/api/songs/')
data = response.json()

# Filter by language
response = requests.get('http://localhost:8080/api/songs/?language=中文')
data = response.json()
```

## Key Principles

- **Consistency** - All endpoints follow unified response format
- **RESTful** - Use proper HTTP methods (GET, POST, PUT, DELETE)
- **Pagination** - Support pagination for list endpoints
- **Filtering** - Support filtering and sorting where applicable
- **Error Handling** - Return meaningful error messages