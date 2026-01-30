```mermaid
erDiagram
    %% ==================== 主数据库 (default) ====================

    %% 歌曲管理模块
    Song ||--o{ SongRecord : "has many"
    Song ||--o{ SongStyle : "has many"
    Song ||--o{ SongTag : "has many"
    Song ||--o{ Recommendation : "recommended in"
    Style ||--o{ SongStyle : "used in"
    Tag ||--o{ SongTag : "used in"

    %% 粉丝二创模块
    Collection ||--o{ Work : "contains"

    %% 网站设置模块
    SiteSettings ||--o{ Recommendation : "has many"
    Song ||--o{ Recommendation : "recommended in"

    %% ==================== 模板化歌单数据库 (songlist_db) ====================

    ArtistSong ||--o{ ArtistSiteSetting : "has settings"

    %% ==================== 数据分析数据库 (analytics_db) ====================

    CrawlSession ||--o{ WorkMetricsHour : "generates"

    %% ==================== 模型定义 ====================

    Song {
        int id PK
        string song_name "歌曲名称"
        string singer "歌手"
        date first_perform "首次演唱时间"
        date last_performed "最近演唱时间"
        int perform_count "演唱次数"
        string language "语言"
    }

    SongRecord {
        int id PK
        int song_id FK "歌曲ID"
        date performed_at "演唱时间"
        string url "视频链接"
        text notes "备注"
        string cover_url "封面URL"
    }

    Style {
        int id PK
        string name "曲风名称"
        text description "描述"
    }

    SongStyle {
        int id PK
        int song_id FK "歌曲ID"
        int style_id FK "曲风ID"
    }

    Tag {
        int id PK
        string name "标签名称"
        text description "描述"
    }

    SongTag {
        int id PK
        int song_id FK "歌曲ID"
        int tag_id FK "标签ID"
    }

    Collection {
        int id PK
        string name "合集名称"
        int works_count "作品数量"
        int display_order "显示顺序"
        int position "位置"
        datetime created_at "创建时间"
        datetime updated_at "更新时间"
    }

    Work {
        int id PK
        int collection_id FK "合集ID"
        string title "作品标题"
        string cover_url "封面图片地址"
        string view_url "观看链接"
        string author "作者"
        text notes "备注"
        int display_order "显示顺序"
        int position "位置"
    }

    SiteSettings {
        int id PK
        image favicon "网站图标"
        datetime created_at "创建时间"
        datetime updated_at "更新时间"
    }

    Recommendation {
        int id PK
        text content "推荐语内容"
        boolean is_active "是否激活显示"
        datetime created_at "创建时间"
        datetime updated_at "更新时间"
    }

    %% 模板化歌单模型（动态生成）
    ArtistSong {
        int id PK
        string song_name "歌曲名称"
        string singer "原唱歌手"
        string language "语言"
        string style "曲风"
        text note "备注"
    }

    ArtistSiteSetting {
        int id PK
        string photo_url "图片URL"
        int position "位置 (1:头像图标, 2:背景图片)"
    }

    %% 数据分析模型
    WorkStatic {
        int id PK
        string platform "平台 (bilibili, youtube, etc.)"
        string work_id "作品ID"
        string title "作品标题"
        string author "作者"
        string cover_url "封面URL"
        datetime created_at "创建时间"
        datetime updated_at "更新时间"
    }

    WorkMetricsHour {
        int id PK
        string platform "平台"
        string work_id "作品ID"
        datetime crawl_time "爬取时间"
        int view_count "观看数"
        int like_count "点赞数"
        int coin_count "投币数"
        int favorite_count "收藏数"
        int danmaku_count "弹幕数"
        int comment_count "评论数"
        int session_id FK "爬取会话ID"
        datetime ingest_time "入库时间"
    }

    CrawlSession {
        int id PK
        datetime start_time "开始时间"
        datetime end_time "结束时间"
        string status "状态 (running, completed, failed)"
        int works_count "爬取作品数"
        text error_message "错误信息"
    }
```