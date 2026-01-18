# songlist API Reference

## Module Overview

**Purpose**: Lightweight, configurable song lists for different artists

**Prefix**: `/api/songlist/`

**Views**: Function-based views

**Note**: This API is designed for template-based song lists and can be accessed via different prefixes for different artists.

## Endpoints

### 1. Song List

**Endpoint**: `GET /api/songlist/songs/`

**Description**: Get list of songs for a specific artist

**Query Parameters**:
- `artist` - Artist key (required, e.g., "youyou", "bingjie")

**Example**:
```bash
# Get songs for youyou
GET /api/songlist/songs/?artist=youyou

# Get songs for bingjie
GET /api/songlist/songs/?artist=bingjie
```

**Response**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "song_name": "歌曲名称",
      "singer": "原唱歌手",
      "language": "语言",
      "style": "曲风",
      "note": "备注"
    }
  ]
}
```

### 2. Language List

**Endpoint**: `GET /api/songlist/languages/`

**Description**: Get list of languages for a specific artist

**Query Parameters**:
- `artist` - Artist key (required)

**Example**:
```bash
GET /api/songlist/languages/?artist=youyou
```

**Response**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    "中文",
    "英文",
    "日文"
  ]
}
```

### 3. Style List

**Endpoint**: `GET /api/songlist/styles/`

**Description**: Get list of styles for a specific artist

**Query Parameters**:
- `artist` - Artist key (required)

**Example**:
```bash
GET /api/songlist/styles/?artist=youyou
```

**Response**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    "流行",
    "摇滚",
    "民谣"
  ]
}
```

### 4. Random Song

**Endpoint**: `GET /api/songlist/random-song/`

**Description**: Get a random song for a specific artist

**Query Parameters**:
- `artist` - Artist key (required)

**Example**:
```bash
GET /api/songlist/random-song/?artist=youyou
```

**Response**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "id": 1,
    "song_name": "歌曲名称",
    "singer": "原唱歌手",
    "language": "语言",
    "style": "曲风",
    "note": "备注"
  }
}
```

### 5. Site Settings

**Endpoint**: `GET /api/songlist/site-settings/`

**Description**: Get site settings for a specific artist

**Query Parameters**:
- `artist` - Artist key (required)

**Example**:
```bash
GET /api/songlist/site-settings/?artist=youyou
```

**Response**:
```json
{
  "code": 200,
  "message": "success",
  "data": [
    {
      "id": 1,
      "photo_url": "/media/...",
      "position": 1,
      "position_display": "头像图标"
    },
    {
      "id": 2,
      "photo_url": "/media/...",
      "position": 2,
      "position_display": "背景图片"
    }
  ]
}
```

### 6. Favicon

**Endpoint**: `GET /api/songlist/favicon/`

**Description**: Get favicon for a specific artist

**Query Parameters**:
- `artist` - Artist key (required)

**Example**:
```bash
GET /api/songlist/favicon/?artist=youyou
```

**Response**:
```json
{
  "code": 200,
  "message": "success",
  "data": {
    "url": "/media/..."
  }
}
```

## Artist-Specific Endpoints

For convenience, the same API can be accessed via artist-specific prefixes:

### Youyou (乐游)
```bash
GET /api/youyou/songs/
GET /api/youyou/languages/
GET /api/youyou/styles/
GET /api/youyou/random-song/
GET /api/youyou/site-settings/
GET /api/youyou/favicon/
```

### Bingjie (冰洁)
```bash
GET /api/bingjie/songs/
GET /api/bingjie/languages/
GET /api/bingjie/styles/
GET /api/bingjie/random-song/
GET /api/bingjie/site-settings/
GET /api/bingjie/favicon/
```

## Common Use Cases

### Get Artist's Songs
```bash
# Using generic endpoint
GET /api/songlist/songs/?artist=youyou

# Using artist-specific endpoint
GET /api/youyou/songs/
```

### Get Random Song
```bash
GET /api/songlist/random-song/?artist=youyou
```

### Get Artist's Languages
```bash
GET /api/songlist/languages/?artist=youyou
```

### Get Artist's Site Settings
```bash
GET /api/songlist/site-settings/?artist=youyou
```

## Error Handling

### Invalid Artist
```json
{
  "code": 400,
  "message": "Invalid artist",
  "errors": {
    "artist": "Artist must be one of: youyou, bingjie"
  }
}
```

### Artist Not Found
```json
{
  "code": 404,
  "message": "Artist not found",
  "errors": {}
}
```

### No Songs Available
```json
{
  "code": 200,
  "message": "success",
  "data": []
}
```

## Special Notes

- This API is designed for lightweight, template-based song lists
- Each artist has independent models and data
- Artist-specific endpoints are provided for convenience
- Songs are simple records without complex relationships
- Site settings include photos for different positions (avatar, background)
- Adding a new artist requires updating ARTIST_CONFIG and running migrations
- No pagination (returns all results)
- Simple response format without complex nested structures