# 小满虫之家后台管理API设计文档

## 1. 文档概述

### 1.1 设计原则
- **RESTful规范**: 使用标准的HTTP方法和状态码
- **统一响应格式**: 与现有系统保持一致
- **权限控制**: 基于JWT Token的身份验证和RBAC权限
- **版本控制**: URL路径中包含版本号 (v1)

### 1.2 基础信息
- **Base URL**: `/api/admin/v1`
- **Content-Type**: `application/json`
- **认证方式**: `Authorization: Bearer <token>`

### 1.3 统一响应格式

#### 成功响应
```json
{
  "code": 200,
  "message": "操作成功",
  "data": { ... }
}
```

#### 分页响应
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "total": 100,
    "page": 1,
    "page_size": 20,
    "results": [ ... ]
  }
}
```

#### 错误响应
```json
{
  "code": 400,
  "message": "参数错误",
  "errors": {
    "field_name": ["错误信息1", "错误信息2"]
  }
}
```

---

## 2. 认证管理模块

### 2.1 用户登录
- **URL**: `POST /auth/login`
- **描述**: 用户登录获取Token
- **请求体**:
```json
{
  "username": "string",
  "password": "string",
  "remember_me": false
}
```
- **响应**:
```json
{
  "code": 200,
  "message": "登录成功",
  "data": {
    "access_token": "string",
    "refresh_token": "string",
    "expires_in": 3600,
    "user": {
      "id": 1,
      "username": "string",
      "nickname": "string",
      "avatar": "string",
      "role": "admin",
      "permissions": ["song:read", "song:write"]
    }
  }
}
```

### 2.2 刷新Token
- **URL**: `POST /auth/refresh`
- **描述**: 使用Refresh Token获取新的Access Token
- **请求体**:
```json
{
  "refresh_token": "string"
}
```

### 2.3 用户登出
- **URL**: `POST /auth/logout`
- **描述**: 用户登出，注销Token
- **响应**: 
```json
{
  "code": 200,
  "message": "登出成功"
}
```

### 2.4 获取当前用户信息
- **URL**: `GET /auth/me`
- **描述**: 获取当前登录用户信息

### 2.5 修改密码
- **URL**: `PUT /auth/password`
- **描述**: 修改当前用户密码
- **请求体**:
```json
{
  "old_password": "string",
  "new_password": "string",
  "confirm_password": "string"
}
```

---

## 3. 仪表盘模块

### 3.1 获取仪表盘数据
- **URL**: `GET /dashboard`
- **描述**: 获取仪表盘统计数据
- **响应**:
```json
{
  "code": 200,
  "message": "获取成功",
  "data": {
    "statistics": {
      "total_songs": 500,
      "today_records": 5,
      "total_livestreams": 200,
      "total_fansdiy": 150,
      "followers_count": 100000,
      "weekly_new_songs": 10,
      "weekly_new_records": 25
    },
    "recent_activities": [
      {
        "id": 1,
        "action": "新增歌曲",
        "target": "《晴天》",
        "user": "管理员",
        "timestamp": "2026-02-17T14:30:00Z"
      }
    ],
    "pending_tasks": [
      {
        "type": "待审核图集",
        "count": 3,
        "link": "/gallery/pending"
      }
    ]
  }
}
```

### 3.2 获取实时数据
- **URL**: `GET /dashboard/realtime`
- **描述**: 获取实时监控数据
- **响应**:
```json
{
  "code": 200,
  "data": {
    "followers_trend": [
      {"time": "00:00", "count": 100000},
      {"time": "01:00", "count": 100050}
    ],
    "recent_submissions": [...],
    "crawler_status": {
      "last_run": "2026-02-17T13:00:00Z",
      "status": "running",
      "next_run": "2026-02-17T14:00:00Z"
    },
    "system_health": {
      "cpu_usage": 45,
      "memory_usage": 60,
      "disk_usage": 70
    }
  }
}
```

---

## 4. 歌曲管理模块

### 4.1 歌曲列表
- **URL**: `GET /songs`
- **描述**: 获取歌曲列表（支持分页、筛选、排序）
- **查询参数**:
  - `page`: 页码 (默认: 1)
  - `page_size`: 每页数量 (默认: 20, 最大: 100)
  - `search`: 关键词搜索（歌名、歌手）
  - `language`: 语言筛选
  - `styles`: 曲风筛选（多个用逗号分隔）
  - `tags`: 标签筛选（多个用逗号分隔）
  - `min_perform_count`: 最小演唱次数
  - `max_perform_count`: 最大演唱次数
  - `first_perform_from`: 首次演唱开始日期
  - `first_perform_to`: 首次演唱结束日期
  - `ordering`: 排序字段（前缀`-`表示降序，如: `-perform_count`）
- **响应**:
```json
{
  "code": 200,
  "data": {
    "total": 500,
    "page": 1,
    "page_size": 20,
    "results": [
      {
        "id": 1,
        "song_name": "晴天",
        "singer": "周杰伦",
        "language": "国语",
        "styles": ["流行", "抒情"],
        "tags": ["经典", "常唱"],
        "perform_count": 15,
        "first_perform": "2024-01-01",
        "last_performed": "2026-02-15",
        "created_at": "2024-01-01T00:00:00Z"
      }
    ]
  }
}
```

### 4.2 获取歌曲详情
- **URL**: `GET /songs/{id}`
- **描述**: 获取单个歌曲详细信息
- **响应**:
```json
{
  "code": 200,
  "data": {
    "id": 1,
    "song_name": "晴天",
    "singer": "周杰伦",
    "language": "国语",
    "styles": ["流行", "抒情"],
    "tags": ["经典", "常唱"],
    "perform_count": 15,
    "first_perform": "2024-01-01",
    "last_performed": "2026-02-15",
    "records": [
      {
        "id": 1,
        "performed_at": "2026-02-15",
        "url": "https://...",
        "notes": "",
        "cover_url": "https://..."
      }
    ],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2026-02-15T00:00:00Z"
  }
}
```

### 4.3 创建歌曲
- **URL**: `POST /songs`
- **描述**: 创建新歌曲
- **请求体**:
```json
{
  "song_name": "string (required)",
  "singer": "string",
  "language": "string",
  "styles": ["string"],
  "tags": ["string"]
}
```
- **响应**:
```json
{
  "code": 201,
  "message": "创建成功",
  "data": {
    "id": 1,
    "song_name": "...",
    ...
  }
}
```

### 4.4 更新歌曲
- **URL**: `PUT /songs/{id}`
- **描述**: 更新歌曲信息
- **请求体**: 同创建，字段可选

### 4.5 删除歌曲
- **URL**: `DELETE /songs/{id}`
- **描述**: 删除歌曲

### 4.6 批量更新歌曲
- **URL**: `PATCH /songs/batch`
- **描述**: 批量更新歌曲信息
- **请求体**:
```json
{
  "ids": [1, 2, 3],
  "action": "add_styles",
  "data": {
    "styles": ["新歌风"]
  }
}
```
- **Actions**: `add_styles`, `remove_styles`, `add_tags`, `remove_tags`, `set_language`, `delete`

### 4.7 导出歌曲
- **URL**: `GET /songs/export`
- **描述**: 导出歌曲数据
- **查询参数**:
  - `format`: 格式 (csv, xlsx)
  - 其他筛选参数同列表接口

### 4.8 演唱记录列表
- **URL**: `GET /songs/records`
- **描述**: 获取所有演唱记录
- **查询参数**:
  - `song_id`: 歌曲ID筛选
  - `from_date`: 开始日期
  - `to_date`: 结束日期
  - `page`, `page_size`, `ordering`

### 4.9 创建演唱记录
- **URL**: `POST /songs/{song_id}/records`
- **描述**: 为指定歌曲添加演唱记录
- **请求体**:
```json
{
  "performed_at": "2026-02-17 (required)",
  "url": "string",
  "notes": "string",
  "cover_url": "string"
}
```

### 4.10 更新演唱记录
- **URL**: `PUT /songs/records/{id}`

### 4.11 删除演唱记录
- **URL**: `DELETE /songs/records/{id}`

### 4.12 从BV号导入记录
- **URL**: `POST /songs/import-from-bvid`
- **描述**: 从B站BV号批量导入演唱记录
- **请求体**:
```json
{
  "bvids": ["BV1xx411c7mD", "BV1xx411c7mE"],
  "auto_match": true,
  "default_song_id": null
}
```

### 4.13 批量导入记录
- **URL**: `POST /songs/records/import`
- **描述**: 从文件批量导入演唱记录
- **Content-Type**: `multipart/form-data`
- **参数**: `file`: Excel/CSV文件

---

## 5. 曲风与标签管理模块

### 5.1 曲风列表
- **URL**: `GET /styles`
- **响应**:
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "name": "流行",
      "description": "流行音乐",
      "song_count": 150
    }
  ]
}
```

### 5.2 创建曲风
- **URL**: `POST /styles`
- **请求体**:
```json
{
  "name": "string (required, unique)",
  "description": "string"
}
```

### 5.3 更新曲风
- **URL**: `PUT /styles/{id}`

### 5.4 删除曲风
- **URL**: `DELETE /styles/{id}`
- **约束**: 有关联歌曲时不能删除

### 5.5 合并曲风
- **URL**: `POST /styles/merge`
- **描述**: 将多个曲风合并到一个目标曲风
- **请求体**:
```json
{
  "source_ids": [1, 2],
  "target_id": 3
}
```

### 5.6 标签列表
- **URL**: `GET /tags`
- **响应**:
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "name": "经典",
      "description": "经典歌曲",
      "color": "#FF6B6B",
      "song_count": 50
    }
  ]
}
```

### 5.7 创建标签
- **URL**: `POST /tags`
- **请求体**:
```json
{
  "name": "string (required, unique)",
  "description": "string",
  "color": "#FF6B6B"
}
```

### 5.8 更新标签
- **URL**: `PUT /tags/{id}`

### 5.9 删除标签
- **URL**: `DELETE /tags/{id}`

### 5.10 合并标签
- **URL**: `POST /tags/merge`
- **请求体**: 同曲风合并

---

## 6. 直播管理模块

### 6.1 直播列表
- **URL**: `GET /livestreams`
- **查询参数**:
  - `year`: 年份筛选
  - `month`: 月份筛选
  - `has_bvid`: 是否有BV号 (true/false)
  - `is_active`: 是否启用 (true/false)
  - `search`: 标题搜索
  - `page`, `page_size`, `ordering`
- **响应**:
```json
{
  "code": 200,
  "data": {
    "total": 200,
    "page": 1,
    "page_size": 20,
    "results": [
      {
        "id": "2026-02-17",
        "date": "2026-02-17",
        "title": "咻咻满-2026年2月17日-录播",
        "summary": "今天唱了很多歌...",
        "bvid": "BV1xx411c7mD",
        "parts": 3,
        "duration_formatted": "3h30m",
        "view_count": "1.2万",
        "danmaku_count": "3.5万",
        "start_time": "20:00",
        "end_time": "23:30",
        "cover_url": "https://...",
        "is_active": true,
        "song_cut_count": 15,
        "screenshot_count": 50
      }
    ]
  }
}
```

### 6.2 获取直播详情
- **URL**: `GET /livestreams/{date}`
- **响应**:
```json
{
  "code": 200,
  "data": {
    "id": "2026-02-17",
    "date": "2026-02-17",
    "title": "...",
    "summary": "...",
    "bvid": "BV1xx411c7mD",
    "parts": 3,
    "duration_seconds": 12600,
    "duration_formatted": "3h30m",
    "view_count": "1.2万",
    "danmaku_count": "3.5万",
    "start_time": "20:00",
    "end_time": "23:30",
    "cover_url": "https://...",
    "danmaku_cloud_url": "https://...",
    "live_moment": "/gallery/LiveMoment/2026/02/17/",
    "is_active": true,
    "sort_order": 0,
    "recordings": [
      {"title": "P1", "url": "https://..."}
    ],
    "song_cuts": [
      {"song_name": "晴天", "performed_at": "2026-02-17", "url": "..."}
    ],
    "screenshots": [
      {"url": "...", "thumbnail_url": "..."}
    ],
    "created_at": "...",
    "updated_at": "..."
  }
}
```

### 6.3 创建直播记录
- **URL**: `POST /livestreams`
- **请求体**:
```json
{
  "date": "2026-02-17 (required)",
  "title": "string (required)",
  "summary": "string",
  "bvid": "string",
  "parts": 1,
  "start_time": "20:00",
  "end_time": "23:30",
  "view_count": "string",
  "danmaku_count": "string",
  "is_active": true
}
```

### 6.4 更新直播记录
- **URL**: `PUT /livestreams/{date}`

### 6.5 删除直播记录
- **URL**: `DELETE /livestreams/{date}`

### 6.6 从BV号获取信息
- **URL**: `GET /livestreams/fetch-bvid-info`
- **描述**: 从B站API获取视频信息
- **查询参数**: `bvid`: BV号
- **响应**: 视频基础信息

### 6.7 批量导入直播
- **URL**: `POST /livestreams/import`
- **Content-Type**: `multipart/form-data`
- **参数**: `file`: Excel/CSV文件

### 6.8 上传直播封面
- **URL**: `POST /livestreams/{date}/cover`
- **Content-Type**: `multipart/form-data`
- **参数**: `cover`: 图片文件

### 6.9 关联歌切记录
- **URL**: `POST /livestreams/{date}/song-cuts`
- **描述**: 手动关联歌切记录
- **请求体**:
```json
{
  "song_id": 1,
  "timestamp": "00:15:30",
  "url": "string"
}
```

### 6.10 上传弹幕云图
- **URL**: `POST /livestreams/{date}/danmaku-cloud`
- **Content-Type**: `multipart/form-data`

---

## 7. 图集管理模块

### 7.1 图集列表
- **URL**: `GET /galleries`
- **查询参数**:
  - `parent_id`: 父图集ID
  - `level`: 层级
  - `is_active`: 是否启用
  - `search`: 标题搜索
  - `tags`: 标签筛选
  - `page`, `page_size`, `ordering`
- **响应**:
```json
{
  "code": 200,
  "data": {
    "total": 50,
    "page": 1,
    "page_size": 20,
    "results": [
      {
        "id": "live-2026",
        "title": "2026年直播",
        "description": "2026年直播截图汇总",
        "cover_url": "https://...",
        "cover_thumbnail_url": "https://...",
        "parent_id": null,
        "level": 0,
        "image_count": 1000,
        "folder_path": "/gallery/LiveMoment/2026/",
        "tags": ["直播", "截图"],
        "sort_order": 0,
        "is_active": true,
        "children_count": 12,
        "created_at": "..."
      }
    ]
  }
}
```

### 7.2 获取图集详情
- **URL**: `GET /galleries/{id}`
- **查询参数**:
  - `include_images`: 是否包含图片列表 (true/false)
  - `include_children`: 是否包含子图集 (true/false)

### 7.3 创建图集
- **URL**: `POST /galleries`
- **请求体**:
```json
{
  "id": "string (required, unique)",
  "title": "string (required)",
  "description": "string",
  "parent_id": "string",
  "folder_path": "string",
  "tags": ["string"],
  "sort_order": 0,
  "is_active": true
}
```

### 7.4 更新图集
- **URL**: `PUT /galleries/{id}`

### 7.5 删除图集
- **URL**: `DELETE /galleries/{id}`
- **查询参数**:
  - `cascade`: 是否级联删除子图集 (默认: false)

### 7.6 获取图集图片
- **URL**: `GET /galleries/{id}/images`
- **响应**:
```json
{
  "code": 200,
  "data": {
    "gallery_id": "live-2026-02",
    "total": 50,
    "images": [
      {
        "filename": "001.jpg",
        "url": "https://...",
        "thumbnail_url": "https://...",
        "title": "2026-02-17 - 1"
      }
    ]
  }
}
```

### 7.7 上传图片
- **URL**: `POST /galleries/{id}/images`
- **Content-Type**: `multipart/form-data`
- **参数**:
  - `images[]`: 图片文件数组（支持多文件）
  - `filenames[]`: 文件名数组（可选）
- **响应**:
```json
{
  "code": 200,
  "message": "上传成功",
  "data": {
    "uploaded": 5,
    "failed": 0,
    "files": ["001.jpg", "002.jpg", ...]
  }
}
```

### 7.8 删除图片
- **URL**: `DELETE /galleries/{id}/images`
- **请求体**:
```json
{
  "filenames": ["001.jpg", "002.jpg"]
}
```

### 7.9 设置封面
- **URL**: `PUT /galleries/{id}/cover`
- **请求体**:
```json
{
  "filename": "001.jpg"
}
```

### 7.10 同步文件夹
- **URL**: `POST /galleries/sync`
- **描述**: 扫描文件夹自动同步到数据库
- **请求体**:
```json
{
  "folder_path": "/gallery/LiveMoment/2026/",
  "create_missing": true,
  "delete_orphan": false
}
```

### 7.11 获取图集树
- **URL**: `GET /galleries/tree`
- **描述**: 获取完整图集树形结构
- **查询参数**:
  - `max_depth`: 最大深度（默认不限制）

---

## 8. 粉丝二创管理模块

### 8.1 合集列表
- **URL**: `GET /fansdiy/collections`
- **响应**:
```json
{
  "code": 200,
  "data": {
    "total": 10,
    "results": [
      {
        "id": 1,
        "name": "精彩翻唱合集",
        "works_count": 25,
        "display_order": 1,
        "position": 1,
        "created_at": "..."
      }
    ]
  }
}
```

### 8.2 创建合集
- **URL**: `POST /fansdiy/collections`
- **请求体**:
```json
{
  "name": "string (required)",
  "display_order": 0,
  "position": 0
}
```

### 8.3 更新合集
- **URL**: `PUT /fansdiy/collections/{id}`

### 8.4 删除合集
- **URL**: `DELETE /fansdiy/collections/{id}`
- **约束**: 有作品时不可删除或需要确认

### 8.5 作品列表
- **URL**: `GET /fansdiy/works`
- **查询参数**:
  - `collection_id`: 合集筛选
  - `author`: 作者搜索
  - `search`: 标题搜索
  - `page`, `page_size`, `ordering`
- **响应**:
```json
{
  "code": 200,
  "data": {
    "total": 150,
    "page": 1,
    "page_size": 20,
    "results": [
      {
        "id": 1,
        "collection_id": 1,
        "collection_name": "精彩翻唱合集",
        "title": "咻咻满翻唱《晴天》",
        "cover_url": "https://...",
        "cover_thumbnail_url": "https://...",
        "view_url": "https://bilibili.com/...",
        "author": "粉丝A",
        "notes": "",
        "display_order": 0,
        "position": 0
      }
    ]
  }
}
```

### 8.6 创建作品
- **URL**: `POST /fansdiy/works`
- **请求体**:
```json
{
  "collection_id": 1,
  "title": "string (required)",
  "view_url": "string",
  "author": "string (required)",
  "notes": "string",
  "display_order": 0,
  "position": 0
}
```

### 8.7 更新作品
- **URL**: `PUT /fansdiy/works/{id}`

### 8.8 删除作品
- **URL**: `DELETE /fansdiy/works/{id}`

### 8.9 上传作品封面
- **URL**: `POST /fansdiy/works/{id}/cover`
- **Content-Type**: `multipart/form-data`

### 8.10 从BV号导入
- **URL**: `POST /fansdiy/import-from-bvid`
- **请求体**:
```json
{
  "bvids": ["BV1xx411c7mD"],
  "collection_id": 1
}
```

### 8.11 批量导入作品
- **URL**: `POST /fansdiy/works/import`
- **Content-Type**: `multipart/form-data`

---

## 9. 数据分析模块

### 9.1 粉丝数据概览
- **URL**: `GET /analytics/followers`
- **查询参数**:
  - `days`: 最近天数 (默认: 30)
- **响应**:
```json
{
  "code": 200,
  "data": {
    "current_count": 100000,
    "total_growth": 5000,
    "daily_growth": [
      {"date": "2026-02-01", "count": 95000, "growth": 100},
      {"date": "2026-02-02", "count": 95100, "growth": 100}
    ],
    "milestones": [
      {"date": "2026-02-01", "title": "10万粉达成", "description": "..."}
    ]
  }
}
```

### 9.2 演唱数据统计
- **URL**: `GET /analytics/songs`
- **查询参数**:
  - `from_date`: 开始日期
  - `to_date`: 结束日期
- **响应**:
```json
{
  "code": 200,
  "data": {
    "total_performances": 500,
    "unique_songs": 200,
    "top_songs": [
      {"song_id": 1, "song_name": "晴天", "count": 15}
    ],
    "style_distribution": [
      {"name": "流行", "count": 300}
    ],
    "daily_distribution": [
      {"date": "2026-02-01", "count": 5}
    ]
  }
}
```

### 9.3 投稿数据列表
- **URL**: `GET /analytics/submissions`
- **查询参数**:
  - `platform`: 平台筛选
  - `from_date`: 开始日期
  - `to_date`: 结束日期
  - `is_valid`: 是否有效
  - `page`, `page_size`, `ordering`

### 9.4 触发数据爬取
- **URL**: `POST /analytics/crawl`
- **请求体**:
```json
{
  "type": "followers",
  "force": false
}
```
- **Types**: `followers`, `submissions`, `all`

### 9.5 获取爬取任务列表
- **URL**: `GET /analytics/crawl-tasks`

### 9.6 获取爬取日志
- **URL**: `GET /analytics/crawl-logs/{task_id}`

---

## 10. 网站设置模块

### 10.1 获取网站设置
- **URL**: `GET /settings`
- **响应**:
```json
{
  "code": 200,
  "data": {
    "general": {
      "artist_name": "咻咻满",
      "artist_birthday": "2000-01-01",
      "artist_constellation": "水瓶座",
      "artist_location": "中国",
      "artist_profession": ["歌手", "主播"],
      "artist_voice_features": ["清亮", "高音"]
    },
    "social": {
      "bilibili_url": "https://space.bilibili.com/...",
      "weibo_url": "https://weibo.com/...",
      "netease_music_url": "...",
      "youtube_url": "...",
      "qq_music_url": "...",
      "xiaohongshu_url": "...",
      "douyin_url": "..."
    },
    "seo": {
      "title": "小满虫之家 - 咻咻满粉丝站",
      "description": "...",
      "keywords": ["咻咻满", "XXM", "粉丝站"]
    }
  }
}
```

### 10.2 更新网站设置
- **URL**: `PUT /settings`
- **请求体**: 部分更新

### 10.3 上传艺人头像
- **URL**: `POST /settings/artist-avatar`
- **Content-Type**: `multipart/form-data`

### 10.4 上传Favicon
- **URL**: `POST /settings/favicon`
- **Content-Type**: `multipart/form-data`

### 10.5 推荐语列表
- **URL**: `GET /settings/recommendations`

### 10.6 创建推荐语
- **URL**: `POST /settings/recommendations`
- **请求体**:
```json
{
  "content": "string (required)",
  "recommended_song_ids": [1, 2],
  "is_active": true
}
```

### 10.7 更新推荐语
- **URL**: `PUT /settings/recommendations/{id}`

### 10.8 删除推荐语
- **URL**: `DELETE /settings/recommendations/{id}`

### 10.9 里程碑列表
- **URL**: `GET /settings/milestones`

### 10.10 创建里程碑
- **URL**: `POST /settings/milestones`
- **请求体**:
```json
{
  "date": "2026-02-01 (required)",
  "title": "string (required)",
  "description": "string (required)",
  "display_order": 0
}
```

### 10.11 更新里程碑
- **URL**: `PUT /settings/milestones/{id}`

### 10.12 删除里程碑
- **URL**: `DELETE /settings/milestones/{id}`

---

## 11. 用户管理模块

### 11.1 用户列表
- **URL**: `GET /users`
- **查询参数**:
  - `role`: 角色筛选
  - `is_active`: 是否启用
  - `search`: 用户名/昵称搜索
  - `page`, `page_size`, `ordering`
- **响应**:
```json
{
  "code": 200,
  "data": {
    "total": 10,
    "results": [
      {
        "id": 1,
        "username": "admin",
        "nickname": "管理员",
        "avatar": "https://...",
        "role": "superadmin",
        "role_name": "超级管理员",
        "is_active": true,
        "last_login": "2026-02-17T14:30:00Z",
        "created_at": "2024-01-01T00:00:00Z"
      }
    ]
  }
}
```

### 11.2 创建用户
- **URL**: `POST /users`
- **请求体**:
```json
{
  "username": "string (required, unique)",
  "password": "string (required)",
  "nickname": "string",
  "role": "string (required)",
  "is_active": true
}
```

### 11.3 更新用户
- **URL**: `PUT /users/{id}`

### 11.4 删除用户
- **URL**: `DELETE /users/{id}`

### 11.5 重置密码
- **URL**: `POST /users/{id}/reset-password`
- **请求体**:
```json
{
  "new_password": "string",
  "send_email": false
}
```

### 11.6 角色列表
- **URL**: `GET /roles`
- **响应**:
```json
{
  "code": 200,
  "data": [
    {
      "id": 1,
      "name": "superadmin",
      "display_name": "超级管理员",
      "description": "拥有所有权限",
      "user_count": 1,
      "permissions": ["*"]
    }
  ]
}
```

### 11.7 创建角色
- **URL**: `POST /roles`
- **请求体**:
```json
{
  "name": "string (required, unique)",
  "display_name": "string (required)",
  "description": "string",
  "permissions": ["song:read", "song:write"]
}
```

### 11.8 更新角色
- **URL**: `PUT /roles/{id}`

### 11.9 删除角色
- **URL**: `DELETE /roles/{id}`
- **约束**: 有用户关联时不可删除

### 11.10 获取权限列表
- **URL**: `GET /permissions`
- **响应**:
```json
{
  "code": 200,
  "data": [
    {
      "code": "song:read",
      "name": "查看歌曲",
      "group": "歌曲管理"
    },
    {
      "code": "song:write",
      "name": "编辑歌曲",
      "group": "歌曲管理"
    }
  ]
}
```

---

## 12. 系统管理模块

### 12.1 操作日志列表
- **URL**: `GET /logs`
- **查询参数**:
  - `user_id`: 用户筛选
  - `module`: 模块筛选 (songs, livestream, gallery, ...)
  - `action`: 操作类型 (create, update, delete, ...)
  - `from_date`: 开始日期
  - `to_date`: 结束日期
  - `page`, `page_size`, `ordering`
- **响应**:
```json
{
  "code": 200,
  "data": {
    "total": 1000,
    "results": [
      {
        "id": 1,
        "user_id": 1,
        "username": "admin",
        "module": "songs",
        "action": "create",
        "target": "歌曲《晴天》",
        "target_id": "1",
        "ip": "192.168.1.1",
        "user_agent": "...",
        "created_at": "2026-02-17T14:30:00Z"
      }
    ]
  }
}
```

### 12.2 导出日志
- **URL**: `GET /logs/export`
- **查询参数**: 同列表接口

### 12.3 获取系统信息
- **URL**: `GET /system/info`
- **响应**:
```json
{
  "code": 200,
  "data": {
    "version": "1.0.0",
    "django_version": "5.2.3",
    "python_version": "3.10.0",
    "database": "sqlite",
    "uptime": "10 days, 5 hours",
    "memory_usage": {
      "used": "500MB",
      "total": "2GB"
    },
    "disk_usage": {
      "used": "10GB",
      "total": "50GB"
    }
  }
}
```

### 12.4 获取缓存统计
- **URL**: `GET /system/cache`

### 12.5 清除缓存
- **URL**: `POST /system/cache/clear`
- **请求体**:
```json
{
  "pattern": "string (可选，如: songs:*)",
  "clear_all": false
}
```

### 12.6 创建备份
- **URL**: `POST /system/backup`
- **请求体**:
```json
{
  "name": "string (可选)",
  "include_media": true
}
```

### 12.7 获取备份列表
- **URL**: `GET /system/backups`

### 12.8 恢复备份
- **URL**: `POST /system/backups/{id}/restore`

### 12.9 删除备份
- **URL**: `DELETE /system/backups/{id}`

---

## 13. 附录

### 13.1 HTTP状态码
| 状态码 | 含义 | 使用场景 |
|--------|------|----------|
| 200 | 成功 | 标准成功响应 |
| 201 | 创建成功 | 资源创建成功 |
| 204 | 无内容 | 删除成功 |
| 400 | 请求参数错误 | 参数校验失败 |
| 401 | 未认证 | Token无效或过期 |
| 403 | 无权限 | 权限不足 |
| 404 | 资源不存在 | 资源未找到 |
| 409 | 冲突 | 资源已存在或状态冲突 |
| 422 | 无法处理 | 业务逻辑错误 |
| 500 | 服务器错误 | 系统内部错误 |

### 13.2 错误码定义
| 错误码 | 含义 | 说明 |
|--------|------|------|
| 400001 | 参数缺失 | 必填参数未提供 |
| 400002 | 参数格式错误 | 参数格式不符合要求 |
| 400003 | 资源已存在 | 唯一性约束冲突 |
| 401001 | Token无效 | JWT Token解析失败 |
| 401002 | Token过期 | JWT Token已过期 |
| 403001 | 无权限 | 当前用户无此操作权限 |
| 404001 | 资源不存在 | 请求的资源不存在 |
| 409001 | 资源冲突 | 如有关联资源无法删除 |
| 422001 | 业务校验失败 | 业务逻辑校验不通过 |
| 500001 | 系统错误 | 服务器内部错误 |

### 13.3 权限编码规范
```
资源:操作
- song:read      查看歌曲
- song:write     编辑歌曲
- song:delete    删除歌曲
- livestream:*   直播管理所有权限
- settings:read  查看设置
- *              所有权限
```

### 13.4 分页参数规范
- `page`: 页码，从1开始
- `page_size`: 每页数量，默认20，最大100
- `ordering`: 排序字段，前缀`-`表示降序
  - 示例: `?ordering=-created_at,name` 表示先按创建时间降序，再按名称升序

### 13.5 搜索参数规范
- `search`: 通用搜索关键词
- 特定字段搜索: `field_name=value`
- 范围搜索: `field_name_from=value&field_name_to=value`
- 多选筛选: `field_name=value1,value2,value3`

### 13.6 文件上传规范
- 使用 `multipart/form-data` 格式
- 单个文件大小限制: 10MB
- 批量上传文件数量限制: 50个
- 支持的图片格式: jpg, jpeg, png, webp, gif
