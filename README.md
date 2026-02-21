# XXM Fans Home - 音乐粉丝网站框架

一个现代化的音乐粉丝网站框架，采用前后端分离架构，提供完整的音乐管理、演唱记录追踪、排行榜、粉丝二创作品展示等核心功能。本项目可作为音乐人、歌手或艺术家的粉丝站建设模板，支持快速搭建和定制化开发。

**示范案例**：[小满虫之家](https://www.xxm8777.cn) - 基于本框架建设的咻咻满（XXM）粉丝网站。

## 🎯 适用场景

本框架适用于以下场景：

- **音乐人粉丝站**: 为歌手、音乐人、乐队建立粉丝网站
- **艺术家作品展示**: 展示艺术家作品、演出记录和创作历程
- **音乐社区平台**: 搭建音乐爱好者交流和分享的平台
- **音乐数据管理**: 管理音乐作品、演出记录和粉丝二创内容
- **音乐排行榜**: 展示热门作品和实时排行榜数据

## 🎵 核心功能

- **音乐资产管理**: 歌曲、演唱记录、曲风、标签管理，支持BV号批量导入
- **直播日历**: 直播记录管理、日历视图、分段播放、歌切列表
- **图集管理**: 多级分类、自动缩略图、面包屑导航
- **粉丝二创平台**: 合集管理、作品展示
- **模板化歌单**: 配置驱动，一键添加艺术家
- **数据分析**: 作品数据爬取、粉丝数追踪
- **智能爬虫**: 分层优化（热数据每小时、冷数据每天3次）

## 🏗️ 技术架构

### 后端技术栈
- **框架**: Django 5.2.3 + Django REST Framework 3.15.2
- **数据库**: SQLite (开发环境)，支持多数据库配置（songlist 独立数据库）
- **编程语言**: Python 3.10+
- **API**: RESTful API
- **环境管理**: python-dotenv 1.0.1
- **其他依赖**:
  - Pillow 10.2.0 (图片处理)
  - django-cors-headers 4.9.0 (跨域支持)
  - requests 2.31.0 (HTTP请求)
  - mysqlclient 2.1.1 (MySQL支持)

### 前端技术栈
- **框架**: React 19.2.3 + TypeScript 5.8.2
- **构建工具**: Vite 6.2.0
- **路由**: React Router DOM 7.12.0
- **数据获取**: SWR 2.4.0
- **图标**: Lucide React 0.562.0
- **样式**: Tailwind CSS 4.1.18
- **图片处理**: Sharp 0.34.5

### 模板化歌单前端 (TempSongListFrontend)
- **框架**: Vue 3.2 + Element Plus 2.0
- **构建工具**: Vite 4.0
- **用途**: 多歌手共享歌单模板，通过域名或 URL 参数区分

### 部署架构
- **Web服务器**: Nginx
- **应用服务器**: Gunicorn
- **进程管理**: systemd
- **缓存**: Redis (可选)

## 📁 项目结构

```
xxm_fans_home/
├── .agents/                 # AI Agent 技能配置
│   └── skills/              # 自定义技能模块
│       ├── bilibili-tools/  # B站工具集
│       ├── module/          # 通用模块
│       ├── skill-create/    # 技能创建模板
│       └── ui-ux-pro-max/   # UI/UX 优化技能
├── data/                    # 数据目录
│   ├── backups/            # 备份数据
│   ├── cache/              # 缓存数据
│   └── spider/             # 爬虫数据
├── doc/                     # 项目文档
│   ├── backend/            # 后端文档
│   ├── frontend/           # 前端文档
│   ├── feature/            # 功能文档
│   ├── bugs-report/        # Bug 报告
│   └── spider/             # 爬虫文档
├── env/                     # 环境配置目录（统一配置管理）
│   ├── backend.env         # 后端环境变量配置
│   └── frontend.env        # 前端环境变量配置
├── infra/                   # 基础设施配置
│   ├── gunicorn/           # Gunicorn配置
│   │   ├── gunicorn_config.py  # Gunicorn配置文件
│   │   ├── README.md            # 使用说明
│   │   └── CHANGELOG.md         # 优化记录
│   ├── nginx/              # Nginx配置
│   │   ├── xxm_nginx.conf       # 开发环境配置
│   │   ├── prod-xxm_nginx.conf  # 生产环境配置
│   │   └── FOOTPRINT_CONFIG.md  # 二创资源配置说明
│   └── systemd/            # systemd服务配置
│       ├── bilibili-tiered-crawler.timer  # 分层爬虫定时器
│       ├── bilibili-views-crawler.timer   # 作品数据爬虫定时器
│       └── bilibili-spider.timer          # 粉丝数爬虫定时器
├── logs/                    # 日志目录
├── media/                   # 媒体文件目录
│   ├── covers/             # 封面图片
│   ├── footprint/          # 二创图片资源
│   ├── gallery/            # 图集图片资源
│   ├── cloud_picture/      # 弹幕云图资源
│   ├── data_analytics/     # 数据分析资源
│   └── songlist/           # 歌单相关图片
├── repo/                    # 代码仓库（Git子模块）
│   ├── xxm_fans_backend/    # Django后端项目
│   │   ├── core/           # 核心模块（缓存、异常、响应格式、缩略图生成）
│   │   ├── song_management/ # 歌曲管理应用
│   │   ├── fansDIY/        # 粉丝二创作品管理应用
│   │   ├── site_settings/  # 网站设置应用
│   │   ├── data_analytics/ # 数据分析应用
│   │   ├── gallery/        # 图集管理应用
│   │   ├── livestream/     # 直播日历应用
│   │   ├── songlist/       # 模板化歌单应用
│   │   ├── xxm_fans_home/  # Django项目配置
│   │   ├── tools/          # 实用工具脚本
│   │   │   ├── spider/     # 爬虫工具模块
│   │   │   └── bilibili/   # B站 API 封装模块
│   │   ├── test/           # 性能测试（Locust）
│   │   └── requirements.txt # Python依赖
│   ├── xxm_fans_frontend/   # React前端项目
│   │   ├── domain/         # 领域层（业务模型和服务接口）
│   │   ├── infrastructure/ # 基础设施层（API实现和配置）
│   │   ├── presentation/   # 表现层（React组件和页面）
│   │   ├── shared/         # 共享层（工具函数和服务）
│   │   └── package.json    # 项目依赖
│   └── TempSongListFrontend/ # Vue模板化歌单前端
├── scripts/                 # 部署和工具脚本
│   ├── dev_start_services.sh          # 开发环境启动脚本
│   ├── dev_stop_services.sh           # 开发环境停止脚本
│   ├── build_start_services.sh        # 生产环境启动脚本
│   ├── build_stop_services.sh         # 生产环境停止脚本
│   ├── create_symlinks.sh             # 创建应用级软链接
│   ├── create_infra_symlinks.sh       # 创建基础设施软链接
│   ├── bilibili_tiered_cron.sh        # 分层爬虫定时任务脚本
│   ├── bilibili_views_cron.sh         # 作品数据爬虫定时任务脚本
│   ├── bilibili_fans_count_cron.sh    # B站粉丝数爬虫定时任务脚本
│   ├── auto_sync_gallery.py           # 自动同步图集数据
│   ├── sync_cloud_picture.py          # 同步弹幕云图
│   └── import_cloud_picture_to_livestream.py # 导入弹幕云图到直播日历
├── spider/                  # 爬虫目录
│   ├── run_tiered_crawler.py          # 分层爬虫主控脚本
│   ├── run_views_crawler.py           # 作品数据爬虫主控脚本
│   ├── get_bilibili_fans_count.py     # B站粉丝数爬虫
│   ├── bilibili_dynamic_monitor.py    # B站动态监控
│   ├── weibo_monitor_selenium.py      # 微博监控
│   ├── TIERED_CRAWLER_README.md       # 分层爬虫文档
│   └── README.md                      # 爬虫使用文档
├── tools/                   # 实用工具脚本
│   ├── download_workstatic_covers.py  # 下载作品封面
│   ├── reorganize_gallery_structure.py # 重组图集结构
│   ├── reorganize_weibo_gallery.py    # 重组微博图集
│   └── update_gallery_database.py     # 更新图集数据库
├── .gitignore               # Git忽略配置
├── .gitmodules              # Git子模块配置
├── README.md                # 项目说明文档（本文件）
└── AGENTS.md                # 项目上下文文档（AI交互使用）
```

## 🚀 快速开始

### 环境要求

- Python 3.10+
- Node.js 18+
- npm

### 开发环境快速启动

```bash
# 1. 创建软链接
cd /path/xxm_fans_home/scripts
./create_symlinks.sh

# 2. 启动开发环境服务
./dev_start_services.sh

# 3. 访问应用
# 前端: http://localhost:8080/
# 后端API: http://localhost:8080/api/
# Admin: http://localhost:8080/admin/

# 4. 停止服务
./dev_stop_services.sh
```

### 生产环境快速启动

```bash
# 1. 创建软链接
cd /path/xxm_fans_home/scripts
./create_symlinks.sh

# 2. 创建基础设施软链接（可选，需要 root 权限）
sudo ./create_infra_symlinks.sh

# 3. 启动生产环境服务
./build_start_services.sh

# 4. 访问应用
# 前端: http://localhost:8080/
# 后端API: http://localhost:8080/api/
# Admin: http://localhost:8080/admin/

# 5. 停止服务
./build_stop_services.sh
```

### 集成测试

```bash
# 后端性能测试
cd /path/xxm_fans_home/repo/xxm_fans_backend/test
./run_performance_test.sh
```

### BV号导入提示

详细使用说明请参考 [BV号导入视频标题格式说明](doc/bugs-report/BV号导入视频标题格式说明.md)

### 手动安装步骤

1. **克隆项目**
```bash
git clone <repository-url>
cd xxm_fans_home
```

2. **创建软链接**
```bash
cd scripts
./create_symlinks.sh
```
> 详细说明请参考 [部署指南](#-部署指南)

3. **后端环境设置**
```bash
cd ../repo/xxm_fans_backend

# 创建并激活虚拟环境
python -m venv venv
# Linux/Mac
source venv/bin/activate
# Windows
venv\Scripts\activate

# 安装Python依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate
python manage.py migrate --database=songlist_db

# 创建超级用户（可选）
python manage.py createsuperuser
```

4. **前端环境设置**
```bash
cd ../xxm_fans_frontend
npm install
```

5. **手动运行项目**
```bash
# 启动后端
cd repo/xxm_fans_backend
python manage.py runserver

# 启动前端（新终端）
cd repo/xxm_fans_frontend
npm run dev
```

## 📊 核心功能模块

### 后端应用模块

#### 1. song_management - 音乐资产管理应用
- **Song**: 音乐作品基本信息（作品名称、原唱艺术家、语言、封面等）
- **SongRecord**: 演出/表演记录（演出记录、视频链接、BV号等）
- **Style**: 曲风分类
- **Tag**: 标签系统
- **Admin功能**: 合并作品、拆分作品、批量标记、BV号导入
  - 支持的视频标题格式：`歌曲名称-YYYY年M月D日`
  - 自动解析歌曲名称和演出日期
  - 自动下载封面图片
  - 支持冲突处理和手动关联歌曲

#### 2. fansDIY - 粉丝二创作品管理应用
- **Collection**: 二创作品合集分类
- **Work**: 单个二创作品信息
- **Admin功能**: BV号导入、封面管理、批量标记
  - 支持通过B站BV号导入二创作品
  - 自动提取作品信息和封面
  - 支持批量导入和关联合集

#### 3. site_settings - 网站设置应用
- **SiteSettings**: 全局配置管理
- **Recommendation**: 个性化推荐内容

#### 4. data_analytics - 数据分析应用
- **WorkStatic**: 数据统计分析
- **WorkMetricsHour**: 小时级指标追踪
- **CrawlSession**: 爬取任务管理
- **Account**: 账户管理
- **FollowerMetrics**: 粉丝数指标追踪
- **核心功能**:
  - 跨应用关联 song_management.Song
  - 小时级数据追踪和分析
  - 爬取任务管理和监控
  - B站粉丝数自动追踪（定时爬虫）

#### 5. gallery - 图集管理应用
- **Gallery**: 图集模型（支持自引用外键实现多级层级）
- **GalleryItem**: 图集图片项
- **GalleryCover**: 图集封面管理
- **核心功能**:
  - 多级图集分类系统，支持任意层级
  - 图片自动同步到数据库，支持增量同步
  - 封面自动（随机选择）或手动设置
  - 图片懒加载和占位符优化
  - 自动缩略图生成（集成 core/thumbnail_generator.py）
  - 面包屑导航
  - 支持图片增删改查和批量操作
  - 图片排序和分组展示
  - 自动检测文件夹变化，更新数据库

#### 6. livestream - 直播日历应用
- **Livestream**: 直播记录模型（包含 B站视频信息、统计数据）
- **LivestreamService**: 直播服务（优先使用数据库，fallback 到 JSON 文件）
- **核心功能**:
  - 直播日历（按月份浏览）
  - 分段视频播放器
  - 当日歌切列表
  - 直播截图轮播
  - 与 song_management.SongRecord 关联
  - 弹幕云图（预留功能）
  - 弹幕云图导入支持

#### 7. songlist - 模板化歌单应用（核心创新）
- **设计理念**: 配置驱动的动态模型创建
- **核心特性**: 一行配置添加艺术家、自动生成模型和API、独立权限管理
- **配置示例**:
```python
ARTIST_CONFIG = {
    'artist1': '艺术家名称1',
    'artist2': '艺术家名称2',
}
```

#### 8. core - 核心共享模块
- **cache.py**: 缓存管理工具
- **exceptions.py**: 自定义异常类
- **responses.py**: 统一响应格式
- **middleware.py**: 自定义中间件
- **thumbnail_generator.py**: 通用缩略图生成器（全站图片缩略图自动生成）
- **utils/**: 通用工具函数

### 前端功能模块

#### 领域层 (domain/)
- **types.ts**: 定义所有领域模型类型
- **api/ISongService.ts**: 定义服务接口

#### 基础设施层 (infrastructure/)
- **api/RealSongService.ts**: 真实后端API服务实现
- **config/**: 配置管理（config.ts、constants.ts、routes.ts）

#### 表现层 (presentation/)
- **components/**: React组件
  - common/: 通用组件（ErrorBoundary、Loading、VideoModal、MysteryBoxModal、LazyImage、MusicPlayer、SmartPlayController）
  - features/: 功能组件（SongTable、RecordList、RankingChart、TimelineChart、OriginalsList）
  - layout/: 布局组件（Navbar、Footer）
- **pages/**: 页面组件（SongsPage、FansDIYPage、LivestreamPage、GalleryPage、OriginalsPage、DataAnalysisPage）
- **hooks/**: 自定义Hook（useSongFilters）

#### 共享层 (shared/)
- **services/**: 共享服务（VideoPlayerService）
- **utils/**: 工具函数（formatDate、copyToClipboard）

## 🔧 API接口文档

### 音乐资产管理
- `GET /api/songs/` - 音乐作品列表（支持搜索、筛选、分页、排序）
- `GET /api/songs/<id>/records/` - 演出/表演记录（支持分页）
- `GET /api/styles/` - 曲风列表
- `GET /api/tags/` - 标签列表
- `GET /api/top_songs/` - 排行榜（支持时间范围）
- `GET /api/random-song/` - 随机音乐作品

### 粉丝二创
- `GET /api/fansDIY/collections/` - 合集列表
- `GET /api/fansDIY/collections/<id>/` - 合集详情
- `GET /api/fansDIY/works/` - 作品列表
- `GET /api/fansDIY/works/<id>/` - 作品详情

### 模板化歌单
- `GET /api/songlist/songs/?artist=artist_id` - 歌单音乐作品列表
- `GET /api/songlist/languages/?artist=artist_id` - 语言列表
- `GET /api/songlist/styles/?artist=artist_id` - 曲风列表
- `GET /api/songlist/random/?artist=artist_id` - 随机音乐作品

### 图集管理
- `GET /api/gallery/` - 图集列表（支持多级分类）
- `GET /api/gallery/<id>/` - 图集详情
- `GET /api/gallery/<id>/items/` - 图集下的图片列表
- `GET /api/gallery/items/<id>/` - 图片详情
- `POST /api/gallery/sync/` - 同步文件夹图片到数据库
- `/gallery/thumbnails/*` - 图集缩略图

### 直播日历
- `GET /api/livestream/` - 直播记录列表
- `GET /api/livestream/<id>/` - 直播记录详情
- `GET /api/livestream/calendar/` - 直播日历数据
- `GET /api/livestream/<id>/segments/` - 分段视频列表
- `GET /api/livestream/<id>/song-cuts/` - 当日歌切列表
- `GET /api/livestream/<id>/screenshots/` - 直播截图列表

### 原唱歌曲
- `GET /api/originals/` - 原唱作品列表
- `GET /api/originals/<id>/` - 原唱作品详情
- `GET /api/originals/<id>/netease/` - 网易云音乐信息

### 其他
- `GET /api/recommendation/` - 推荐语
- `GET /api/site-settings/` - 网站设置
- `GET /api/data-analytics/` - 数据分析接口

### 媒体文件
- `/covers/*` - 封面图片
- `/footprint/*` - 二创图片资源
- `/gallery/*` - 图集图片资源
- `/gallery/thumbnails/*` - 图集缩略图
- `/media/*` - 其他媒体文件
- `/cloud_picture/*` - 弹幕云图资源
- `/data_analytics/*` - 数据分析相关资源

## ⚡ 性能测试

项目内置完整的Locust性能测试套件，位于 `repo/xxm_fans_backend/test/` 目录。

### 运行测试
```bash
cd repo/xxm_fans_backend/test
# Linux/Mac
./run_performance_test.sh
# Windows
run_performance_test.bat
```

### 测试配置
- 并发用户数: 100
- 启动速率: 10 users/second
- 测试时长: 10分钟
- 目标地址: 可配置

### 测试报告
测试完成后生成：
- `load_test_results_stats.csv` - 详细统计信息
- `load_test_results_failures.csv` - 失败请求详情
- `qps.png` - QPS图表
- `response_time.png` - 响应时间图表
- `failures.png` - 失败数图表

## 🛠️ 实用工具

### 部署脚本（位于 scripts/）
- `create_symlinks.sh` - 创建应用级软链接（环境配置和媒体资源）
- `create_infra_symlinks.sh` - 创建基础设施配置软链接
- `dev_start_services.sh` - 开发环境启动脚本
- `dev_stop_services.sh` - 开发环境停止脚本
- `build_start_services.sh` - 生产环境启动脚本
- `build_stop_services.sh` - 生产环境停止脚本
- `setup_songlist_subdomain.sh` - 配置歌单子域名

### 数据管理（位于 repo/xxm_fans_backend/tools/）
- `import_public_data.py` - 导入公开数据
- `import_song_records.py` - 导入演唱记录
- `import_livestream_data.py` - 导入直播数据
- `ingest_follower_data.py` - 导入粉丝数据
- `download_covers.py` - 下载封面图片
- `migrate_livestream_cover.py` - 迁移直播封面

### 图片处理（位于 tools/）
- `download_workstatic_covers.py` - 下载投稿封面
- `reorganize_gallery_structure.py` - 重组图集结构
- `reorganize_weibo_gallery.py` - 重组微博图集
- `update_gallery_database.py` - 更新图集数据库

### B站集成（位于 repo/xxm_fans_backend/tools/bilibili/）
- **api_client.py** - B站 API 客户端（获取视频信息、分P列表等）
- **cover_downloader.py** - 封面下载工具类
- **models.py** - B站数据模型

**BV号导入功能**：
- 支持通过B站BV号批量导入演唱记录
- 自动解析视频分P标题，提取歌曲名称和演出日期
- 支持的视频标题格式：`歌曲名称-YYYY年M月D日`
- 详细的使用说明请参考 [BV号导入视频标题格式说明](doc/bugs-report/BV号导入视频标题格式说明.md)

### 弹幕云图同步（位于 scripts/）
- `auto_sync_gallery.py` - 自动同步图集数据
- `sync_cloud_picture.py` - 同步弹幕云图
- `import_cloud_picture_to_livestream.py` - 导入弹幕云图到直播日历

### 定时爬虫（位于 scripts/）
- `bilibili_tiered_cron.sh` - 分层爬虫定时任务脚本（每小时）
- `bilibili_views_cron.sh` - 作品数据爬虫定时任务脚本
- `bilibili_fans_count_cron.sh` - B站粉丝数爬虫定时任务脚本

### 爬虫（位于 spider/）
- `run_tiered_crawler.py` - 分层爬虫主控脚本
- `run_views_crawler.py` - 作品数据爬虫主控脚本
- `get_bilibili_fans_count.py` - B站粉丝数爬虫
- `bilibili_dynamic_monitor.py` - B站动态监控
- `weibo_monitor_selenium.py` - 微博监控（Selenium）

#### 分层爬虫优化方案

针对B站投稿数据爬虫的优化方案，根据发布时间将作品分为**热数据**和**冷数据**，采用不同的爬取频率：

| 数据类型 | 发布时间 | 爬取频率 | 爬取时段 |
|---------|---------|---------|---------|
| **热数据** | ≤ 7天 | **每小时** | 全天24小时 |
| **冷数据** | > 7天 | **每天3次** | 00:00, 08:00, 16:00 |

**优势**：
- 大幅降低服务器压力（平时每小时只爬取0-1条）
- 保证新作品实时性
- 历史数据适度更新

```bash
# 查看分层统计信息
python spider/run_tiered_crawler.py --stats

# 只爬取热数据（7天内发布的作品）
python spider/run_tiered_crawler.py --hot

# 只爬取冷数据（7天前发布的作品）
python spider/run_tiered_crawler.py --cold

# 根据当前时间自动选择（用于定时任务）
python spider/run_tiered_crawler.py --scheduled
```

## 🚀 部署指南

### 软链接配置

项目部署时需要创建多个软链接，用于环境配置、媒体资源和基础设施配置。详细的软链接配置说明请参考 [DEPLOYMENT_SYMLINKS.md](DEPLOYMENT_SYMLINKS.md)。

#### 应用级软链接（必需）

**环境配置文件软链接**：
```bash
# 后端环境变量
repo/xxm_fans_backend/.env -> env/backend.env

# 前端环境变量
repo/xxm_fans_frontend/.env -> env/frontend.env
```

**媒体资源软链接**：
```bash
# 封面图片
repo/xxm_fans_backend/static/covers -> media/covers

# 二创图片资源
repo/xxm_fans_backend/static/footprint -> media/footprint

# 图集图片资源
repo/xxm_fans_backend/static/gallery -> media/gallery
```

#### 基础设施配置软链接（可选，需要 root 权限）

**Nginx 配置**：
```bash
# 开发环境
/etc/nginx/sites-enabled/xxm_fans_home -> infra/nginx/xxm_nginx.conf

# 生产环境
/etc/nginx/sites-enabled/xxm_fans_home -> infra/nginx/prod-xxm_nginx.conf
```

**Gunicorn 配置**：
```bash
/etc/gunicorn.d/xxm_fans_home.py -> infra/gunicorn/gunicorn_config.py
```

**systemd 服务配置**：
```bash
/etc/systemd/system/xxm-fans-home.service -> infra/systemd/xxm-fans-home.service
```

#### 自动创建软链接

**创建应用级软链接**：
```bash
cd scripts
./create_symlinks.sh
```

**创建基础设施软链接（需要 root 权限）**：
```bash
cd scripts
sudo ./create_infra_symlinks.sh
```

#### 启用定时爬虫（需要 root 权限）
```bash
# 启用并启动分层爬虫定时任务
sudo systemctl enable --now infra/systemd/bilibili-tiered-crawler.timer

# 启用并启动作品数据爬虫定时任务
sudo systemctl enable --now infra/systemd/bilibili-views-crawler.timer

# 启用并启动粉丝数爬虫定时任务
sudo systemctl enable --now infra/systemd/bilibili-spider.timer

# 查看定时任务状态
systemctl list-timers --all | grep bilibili
```

#### 验证软链接

```bash
# 检查应用级软链接
ls -la repo/xxm_fans_backend/.env
ls -la repo/xxm_fans_frontend/.env
ls -la repo/xxm_fans_backend/static/covers
ls -la repo/xxm_fans_backend/static/footprint
ls -la repo/xxm_fans_backend/static/gallery

# 检查基础设施软链接（需要 root 权限）
sudo ls -la /etc/nginx/sites-enabled/xxm_fans_home
sudo ls -la /etc/gunicorn.d/xxm_fans_home.py
sudo ls -la /etc/systemd/system/xxm-fans-home.service
```

### 环境变量配置

项目采用**配置文件集中管理**方案，所有环境变量统一存放在 `env/` 目录下：

```bash
env/
├── backend.env    # 后端环境变量配置
└── frontend.env   # 前端环境变量配置

# 软链接
repo/xxm_fans_backend/.env -> env/backend.env
repo/xxm_fans_frontend/.env -> env/frontend.env
```

**配置管理优势**：
- 统一管理：所有配置集中在 `env/` 目录
- 环境隔离：开发、测试、生产环境可使用不同配置
- 透明读取：应用代码无需修改，仍通过 `.env` 文件读取
- 版本控制友好：可在 `.gitignore` 中忽略软链接

### 前端构建
```bash
cd repo/xxm_fans_frontend

# 生产构建（使用vite.config.prod.ts，包含文件名哈希等优化）
npm run build

# 开发环境构建（使用vite.config.ts）
npm run build:dev

# 预览生产构建
npm run preview
```

### 后端部署

1. **收集静态文件**
```bash
cd repo/xxm_fans_backend
python manage.py collectstatic --noinput
```

2. **使用Gunicorn运行**
```bash
gunicorn xxm_fans_home.wsgi:application -c infra/gunicorn/gunicorn_config.py
```

3. **使用systemd服务管理**
   - 服务配置文件位于 `infra/systemd/`
   - 使用 systemctl 命令管理服务

4. **Nginx配置**
   - 开发环境: `infra/nginx/xxm_nginx.conf`（代理到 Vite 开发服务器）
   - 生产环境: `infra/nginx/prod-xxm_nginx.conf`（提供静态文件）

### 生产环境配置

1. **环境变量设置**
```bash
# 编辑 env/backend.env 文件
export DJANGO_DEBUG=False
export DJANGO_SECRET_KEY='your-secret-key'
export DJANGO_ALLOWED_HOSTS='your-domain.com'
```

2. **数据库配置**
- 生产环境建议使用PostgreSQL或MySQL
- 配置连接池
- 定期备份

3. **缓存**
- 生产环境建议使用Redis
- 配置Redis连接信息

4. **安全设置**
- 确保 `DEBUG = False`
- 设置合适的 `ALLOWED_HOSTS`
- 使用安全的 `SECRET_KEY`
- 配置 HTTPS

## 📝 开发规范

### 后端开发规范

**分层架构规范**:
- **models/**: 只包含数据模型定义，不包含业务逻辑
- **services/**: 包含所有业务逻辑，可被API和Admin复用
- **api/**: 只负责HTTP请求处理和响应格式化
- **admin/**: Django Admin后台管理配置

**统一响应格式规范**:
- 使用`core/responses.py`提供的响应函数
- 成功响应使用`success_response()`
- 错误响应使用`error_response()`
- 分页响应使用`paginated_response()`

**异常处理规范**:
- 使用`core/exceptions.py`提供的异常类
- 在services层抛出业务异常
- 在api层捕获异常并返回错误响应

**代码约束**:
- 不能修改SongRecord和Song核心模型结构
- 遵循现有的代码风格和架构模式
- 保持API接口的向后兼容性

### 前端开发规范

**架构原则**:
- **依赖倒置**: 高层模块不依赖低层模块，两者都依赖抽象（接口）
- **单一职责**: 每个类、函数、组件只负责一件事
- **开闭原则**: 对扩展开放，对修改关闭
- **领域驱动**: 业务逻辑集中在领域层，技术实现在基础设施层

**代码风格**:
- 使用 TypeScript 编写所有代码，充分利用类型系统
- 组件使用函数式组件 + Hooks
- 文件命名：
  - 组件文件：PascalCase（如 `SongTable.tsx`）
  - 工具函数和 Hook：camelCase（如 `useSongData.ts`）
  - 接口定义：PascalCase，以 `I` 开头（如 `ISongService`）

**类型定义规范**:
- **领域类型**：所有业务领域模型在 `domain/types.ts` 中定义
- **接口定义**：服务接口在 `domain/api/` 中定义
- **API 类型**：API 相关类型在 `infrastructure/api/apiTypes.ts` 中定义
- **类型安全**：避免使用 `any` 类型，优先使用具体类型或泛型

**组件开发规范**:
- **组件职责**：每个组件只负责一个功能，保持组件轻量
- **组件拆分**：大型组件（超过200行）应拆分为多个小组件
- **Props 定义**：使用 TypeScript 接口定义 Props 类型
- **事件处理**：使用 `useCallback` 缓存事件处理函数
- **性能优化**：使用 `useMemo` 缓存计算结果
- **样式管理**：使用 Tailwind CSS，保持样式一致性

### Git规范

忽略的文件和目录:
- media/
- static/
- logs/
- data/
- venv/
- node_modules/
- .env（软链接，实际配置文件在 env/ 目录中）

## 📚 文档资源

### 项目文档
- `README.md` - 项目说明文档（本文件）
- `AGENTS.md` - 项目上下文文档（AI交互使用，包含完整项目信息）

### 功能文档（位于 doc/）
- `BV号导入视频标题格式说明.md` - BV号导入功能详细说明
- `DEPLOYMENT_SYMLINKS.md` - 部署软链接配置说明
- `数据库SQLite到MySQL迁移方案.md` - 数据库迁移方案
- `gallery/` - 图集功能文档
- `songlist/` - 模板化歌单文档
- `feature/` - 功能文档

### 爬虫文档（位于 spider/）
- `TIERED_CRAWLER_README.md` - 分层爬虫详细文档
- `README.md` - 爬虫使用文档

### 基础设施文档
- `infra/gunicorn/README.md` - Gunicorn 配置说明
- `infra/gunicorn/CHANGELOG.md` - Gunicorn 优化记录
- `infra/nginx/FOOTPRINT_CONFIG.md` - 二创资源配置说明

## 🌟 项目亮点

1. **模块化设计**: 核心功能拆分为独立应用（7个核心应用），便于维护和扩展
2. **分层架构**: 清晰的models-services-api分层，代码结构清晰
3. **模板化歌单系统**: 配置驱动的动态模型创建，一行配置即可添加新艺术家
4. **统一响应格式**: 标准化的API响应格式，便于前端对接
5. **DDD架构**: 前端采用领域驱动设计，严格遵循依赖倒置原则
6. **性能测试**: 内置完整的Locust性能测试套件
7. **图集管理**: 完整的图集管理系统，支持多级分类、自动缩略图生成
8. **直播日历**: 完整的直播记录管理系统，支持BV号导入
9. **智能爬虫系统**: 分层爬虫优化（热数据每小时、冷数据每天3次）、定时任务管理、粉丝数追踪
11. **配置集中管理**: 统一的 `env/` 目录管理所有环境变量
12. **AI Agent 技能**: 内置自定义技能模块，支持 B站工具、UI优化等

## 🎨 网站信息

### 示范案例：小满虫之家
- **网站名称**: 小满虫之家
- **网站地址**: [www.xxm8777.cn](https://www.xxm8777.cn)
- **ICP 备案**: 鄂ICP备2025100707号-2
- **主题色**: 豆沙绿 (#8eb69b)、蜜桃粉 (#f8b195)、大地棕 (#4a3728)
- **字体**: Quicksand + Noto Sans SC
- **设计风格**: 森林清新风格，毛玻璃效果，圆角卡片设计

### 定制化建议
本框架支持高度定制化开发，您可以根据目标艺术家或品牌的需求：
- 调整主题色和设计风格
- 自定义网站名称和品牌标识
- 配置专属的艺术家信息和作品数据
- 扩展功能模块以适应特定需求

## 🔮 未来改进方向

1. 集成第三方音乐平台API（Spotify、网易云音乐等）自动为作品分配曲风
2. 优化精选二创页面图片懒加载和CDN加速
3. 增加更多数据可视化功能和仪表盘
4. 支持用户评论、点赞和互动功能
5. 移动端适配优化和PWA支持
6. 数据分析功能增强（更多可视化图表和数据分析维度）
7. 添加单元测试和集成测试
8. 实现CI/CD自动化部署
9. 实现图片自动压缩和格式转换
10. 支持多语言国际化
11. 增加用户系统和权限管理
12. 支持RSS订阅和邮件通知
13. 图集功能增强：图片水印、批量编辑、相册分享
14. 直播功能增强：弹幕分析、热门片段提取
15. 音乐播放器增强：歌词显示、播放列表、收藏功能
16. 搜索功能增强：全文搜索、语音搜索、智能推荐

## 🤝 贡献指南

1. Fork 项目
2. 创建功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 创建 Pull Request

## 📄 许可证

本项目采用 MIT 许可证。

---

⭐ 如果这个项目对你有帮助，请给它一个星标！
