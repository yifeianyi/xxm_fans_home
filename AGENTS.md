# XXM Fans Home - 项目上下文文档

本文档为 AI Agent 提供项目完整的技术背景、架构信息和开发规范，帮助 AI 更好地理解并协助项目开发。

---

## 项目概述

**XXM Fans Home** 是一个现代化的音乐粉丝网站框架，采用前后端分离架构，提供完整的音乐管理、演唱记录追踪、排行榜、粉丝二创作品展示、直播日历、图集管理、数据分析等核心功能。项目可作为音乐人、歌手或艺术家的粉丝站建设模板，支持快速搭建和定制化开发。

**示范案例**: [小满虫之家](https://www.xxm8777.cn) - 基于本框架建设的咻咻满（XXM）粉丝网站。

---

## 技术架构

### 后端技术栈
- **框架**: Django 5.2.3 + Django REST Framework 3.15.2
- **数据库**: SQLite (开发环境)，支持多数据库配置（songlist 独立数据库）
- **编程语言**: Python 3.10+
- **API**: RESTful API
- **依赖**: python-dotenv, Pillow, django-cors-headers, requests, mysqlclient

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
- **定时任务**: systemd timer (B站数据爬虫)

---

## 项目结构

```
xxm_fans_home/
├── .agents/                  # AI Agent 技能配置
│   └── skills/              # 自定义技能模块
│       ├── bilibili-tools/  # B站工具集
│       ├── module/          # 通用模块
│       ├── skill-create/    # 技能创建模板
│       └── ui-ux-pro-max/   # UI/UX 优化技能
├── env/                      # 环境配置目录（统一配置管理）
│   ├── backend.env          # 后端环境变量配置
│   └── frontend.env         # 前端环境变量配置
├── infra/                    # 基础设施配置
│   ├── gunicorn/            # Gunicorn配置
│   ├── nginx/               # Nginx配置
│   └── systemd/             # systemd服务配置
├── media/                    # 媒体文件目录
│   ├── covers/              # 封面图片
│   ├── footprint/           # 二创图片资源
│   ├── gallery/             # 图集图片资源
│   ├── cloud_picture/       # 弹幕云图资源
│   ├── data_analytics/      # 数据分析资源
│   └── songlist/            # 歌单资源
├── repo/                     # 代码仓库（Git子模块）
│   ├── xxm_fans_backend/    # Django后端项目
│   ├── xxm_fans_frontend/   # React前端项目
│   └── TempSongListFrontend/ # Vue模板化歌单前端
├── scripts/                  # 部署和工具脚本
├── spider/                   # 爬虫目录
├── tools/                    # 实用工具脚本
├── data/                     # 数据目录
│   ├── backups/             # 备份数据
│   ├── cache/               # 缓存数据
│   └── spider/              # 爬虫数据
└── doc/                      # 项目文档
```

---

## 构建和运行

### 快速启动（开发环境）

```bash
# 1. 创建软链接
cd /home/yifeianyi/Desktop/xxm_fans_home/scripts
./create_symlinks.sh

# 2. 启动开发环境服务
./dev_start_services.sh

# 3. 访问应用
# 主前端:     http://localhost:8080/
# 模板化歌单: http://localhost:8080/songlist/
# 后端API:    http://localhost:8080/api/
# Admin:      http://localhost:8080/admin/

# 4. 停止服务
./dev_stop_services.sh
```

### 后端开发命令

```bash
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend

# 激活虚拟环境
source venv/bin/activate  # Linux/Mac

# 安装依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate
python manage.py migrate --database=songlist_db

# 运行开发服务器
python manage.py runserver

# 创建超级用户
python manage.py createsuperuser

# 收集静态文件（生产环境）
python manage.py collectstatic --noinput
```

### 前端开发命令

```bash
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_frontend

# 安装依赖
npm install

# 开发环境
npm run dev                # http://localhost:5173

# 构建
npm run build              # 生产构建（vite.config.prod.ts）
npm run build:dev          # 开发构建
npm run preview            # 预览生产构建

# 类型检查
npx tsc --noEmit
```

### 模板化歌单前端

```bash
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/TempSongListFrontend

# 开发环境
npm run dev                # http://localhost:5174

# 构建
npm run build

# 通过 URL 参数访问不同歌手
# http://localhost:5174?artist=youyou
# http://localhost:5174?artist=bingjie
```

### 性能测试

```bash
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend/test

# Linux/Mac
./run_performance_test.sh
```

---

## 核心功能模块

### 后端应用模块

#### 1. song_management - 音乐资产管理
- **Song**: 音乐作品基本信息
- **SongRecord**: 演出/表演记录
- **Style**: 曲风分类
- **Tag**: 标签系统
- **Admin功能**: 合并作品、拆分作品、批量标记、BV号导入

#### 2. fansDIY - 粉丝二创作品管理
- **Collection**: 二创作品合集分类
- **Work**: 单个二创作品信息
- **Admin功能**: BV号导入、封面管理、批量标记

#### 3. site_settings - 网站设置
- **SiteSettings**: 全局配置管理
- **Recommendation**: 个性化推荐内容

#### 4. data_analytics - 数据分析
- **WorkStatic**: 数据统计分析
- **WorkMetricsHour**: 小时级指标追踪
- **CrawlSession**: 爬取任务管理
- **FollowerMetrics**: 粉丝数指标追踪
- **核心功能**: B站粉丝数自动追踪、作品数据爬取

#### 5. gallery - 图集管理
- **Gallery**: 图集模型（支持自引用外键实现多级层级）
- **GalleryItem**: 图集图片项
- **GalleryCover**: 图集封面管理
- **核心功能**: 多级分类、自动缩略图、图片懒加载、面包屑导航

#### 6. livestream - 直播日历
- **Livestream**: 直播记录模型
- **LivestreamService**: 直播服务
- **核心功能**: 直播日历、分段视频播放、当日歌切列表、直播截图轮播、BV号导入

#### 7. songlist - 模板化歌单
- **设计理念**: 配置驱动的动态模型创建
- **核心特性**: 一行配置添加艺术家、自动生成模型和API、独立权限管理

#### 8. core - 核心共享模块
- **cache.py**: 缓存管理工具
- **exceptions.py**: 自定义异常类
- **responses.py**: 统一响应格式
- **thumbnail_generator.py**: 通用缩略图生成器
- **middleware.py**: 自定义中间件

### 前端功能模块

#### 领域层 (domain/)
- **types.ts**: 定义所有领域模型类型
- **api/ISongService.ts**: 定义服务接口
- **api/ISubmissionService.ts**: 投稿服务接口

#### 基础设施层 (infrastructure/)
- **api/**: 真实后端API服务实现
  - `RealSongService.ts`: 歌曲服务
  - `RealGalleryService.ts`: 图集服务
  - `RealSiteSettingsService.ts`: 网站设置服务
  - `RealDataAnalyticsService.ts`: 数据分析服务
  - `RealSubmissionService.ts`: 投稿服务
- **config/**: 配置管理（config.ts、constants.ts、routes.ts）
- **hooks/**: 基础设施层 Hooks（useData、useSWRConfig）
- **components/**: SEO、SWRProvider 等基础设施组件

#### 表现层 (presentation/)
- **components/**: React组件
  - common/: 通用组件（ErrorBoundary、Loading、VideoModal、LazyImage、MusicPlayer、MysteryBoxModal、SmartPlayController等）
  - features/: 功能组件（SongTable、RecordList、RankingChart、OriginalsList、TimelineChart等）
  - layout/: 布局组件（Navbar、Footer）
- **pages/**: 页面组件
  - HomePage: 首页
  - SongsPage: 歌曲列表
  - FansDIYPage: 粉丝二创
  - GalleryPage: 图集页面（含子组件）
  - LivestreamPage: 直播日历（含日历组件）
  - DataAnalysisPage: 数据分析（含图表组件）
  - OriginalsPage: 原创作品
  - AboutPage: 关于页面
  - ContactPage: 联系页面
- **hooks/**: 自定义Hook

#### 共享层 (shared/)
- **hooks/**: 共享 Hooks（useClickOutside、useDebounce、useLocalStorage、useMediaQuery、useScrollPosition）
- **services/**: 共享服务（VideoPlayerService）
- **utils/**: 工具函数（device、videoUtils、seoUtils）

---

## 开发规范

### 后端开发规范

**分层架构规范**:
- **models/**: 只包含数据模型定义，不包含业务逻辑
- **services/**: 包含所有业务逻辑，可被API和Admin复用
- **api/**: 只负责HTTP请求处理和响应格式化
- **admin/**: Django Admin后台管理配置

**统一响应格式规范**:
- 使用 `core/responses.py` 提供的响应函数
- 成功响应使用 `success_response()`
- 错误响应使用 `error_response()`
- 分页响应使用 `paginated_response()`

**异常处理规范**:
- 使用 `core/exceptions.py` 提供的异常类
- 在services层抛出业务异常
- 在api层捕获异常并返回错误响应

**代码约束**:
- 不能修改 SongRecord 和 Song 核心模型结构
- 遵循现有的代码风格和架构模式
- 保持API接口的向后兼容性

### 前端开发规范

**架构原则**:
- **依赖倒置**: 高层模块不依赖低层模块，两者都依赖抽象（接口）
- **单一职责**: 每个类、函数、组件只负责一件事
- **领域驱动**: 业务逻辑集中在领域层，技术实现在基础设施层

**命名规范**:
- **组件**: PascalCase (如 `SongTable`, `LazyImage`)
- **Hooks**: `use` 前缀 + PascalCase (如 `useSongData`)
- **Services**: PascalCase 类，lowercase 实例 (如 `songService`)
- **Types/Interfaces**: PascalCase (如 `Song`, `ApiResult`)
- **Constants**: UPPER_SNAKE_CASE (如 `GENRES`, `TAGS`)
- **Functions**: camelCase (如 `formatDate`, `copyToClipboard`)

**TypeScript 规范**:
- Strict mode 启用
- 定义返回类型（尤其是公共API）
- 领域类型在 `domain/types.ts` 中定义
- API 类型在 `infrastructure/api/apiTypes.ts` 中定义

**React 规范**:
- 函数式组件 + Hooks（无类组件）
- 定义 Props 接口
- 使用 `useCallback` 缓存事件处理函数
- 使用 `useMemo` 缓存计算结果

**样式规范**:
- **Tailwind CSS** 用于所有样式
- 使用 CSS 变量：`--sage-bg`, `--meadow-green`, `--peach-accent`
- 响应式设计：mobile-first 使用 `md:`, `lg:` 前缀

**导入顺序**:
```typescript
// 1. 外部库
import React from 'react';
import { Search } from 'lucide-react';

// 2. 领域类型
import { Song, FilterState } from '../domain/types';

// 3. 基础设施/服务
import { songService } from '../infrastructure/api';

// 4. 组件
import { Loading } from './components/common/Loading';

// 5. 工具函数
import { formatDate } from '../shared/utils';
```

---

## API接口

### 音乐资产管理
- `GET /api/songs/` - 音乐作品列表（支持搜索、筛选、分页、排序）
- `GET /api/songs/<id>/records/` - 演出/表演记录
- `GET /api/styles/` - 曲风列表
- `GET /api/tags/` - 标签列表
- `GET /api/top_songs/` - 排行榜
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
- `GET /api/songlist/settings/?artist=artist_id` - 网站设置

### 图集管理
- `GET /api/gallery/` - 图集列表
- `GET /api/gallery/<id>/` - 图集详情
- `GET /api/gallery/<id>/items/` - 图集下的图片列表
- `POST /api/gallery/sync/` - 同步文件夹图片到数据库

### 直播日历
- `GET /api/livestream/` - 直播记录列表
- `GET /api/livestream/<id>/` - 直播记录详情
- `GET /api/livestream/calendar/` - 直播日历数据
- `GET /api/livestream/<id>/segments/` - 分段视频列表
- `GET /api/livestream/<id>/song-cuts/` - 当日歌切列表
- `GET /api/livestream/<id>/screenshots/` - 直播截图列表

### 媒体文件
- `/covers/*` - 封面图片
- `/footprint/*` - 二创图片资源
- `/gallery/*` - 图集图片资源
- `/gallery/thumbnails/*` - 图集缩略图
- `/cloud_picture/*` - 弹幕云图资源
- `/data_analytics/*` - 数据分析相关资源

---

## 环境变量配置

### 后端环境变量 (env/backend.env)
```bash
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=django-insecure-dev-key-for-local-testing-only
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1

# Spotify API配置(可选)
SPOTIPY_CLIENT_ID=your_client_id_here
SPOTIPY_CLIENT_SECRET=your_client_secret_here
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8080
```

### 前端环境变量 (env/frontend.env)
```bash
VITE_API_BASE_URL=/api
```

---

## 软链接配置

项目使用软链接实现配置和资源共享：

**应用级软链接**（必需）：
- `repo/xxm_fans_backend/.env -> env/backend.env`
- `repo/xxm_fans_frontend/.env -> env/frontend.env`
- `repo/xxm_fans_backend/static/covers -> media/covers`
- `repo/xxm_fans_backend/static/footprint -> media/footprint`
- `repo/xxm_fans_backend/static/gallery -> media/gallery`

**创建软链接**：
```bash
cd /home/yifeianyi/Desktop/xxm_fans_home/scripts
./create_symlinks.sh
```

---

## 爬虫系统

### 分层爬虫优化方案

针对B站投稿数据爬虫的优化方案，根据发布时间将作品分为**热数据**和**冷数据**，采用不同的爬取频率。

| 数据类型 | 发布时间 | 爬取频率 | 爬取时段 |
|---------|---------|---------|---------|
| **热数据** | ≤ 7天 | **每小时** | 全天24小时 |
| **冷数据** | > 7天 | **每天3次** | 00:00, 08:00, 16:00 |

**优势**：
- 大幅降低服务器压力（平时每小时只爬取0-1条）
- 保证新作品实时性
- 历史数据适度更新

### 爬虫脚本

| 脚本 | 说明 |
|-----|------|
| `spider/run_tiered_crawler.py` | 分层爬虫主控脚本 |
| `spider/run_views_crawler.py` | 作品数据爬虫主控脚本 |
| `spider/get_bilibili_fans_count.py` | B站粉丝数爬虫 |
| `spider/bilibili_dynamic_monitor.py` | B站动态监控 |
| `spider/weibo_monitor_selenium.py` | 微博监控（Selenium） |

### 分层爬虫使用

```bash
# 查看分层统计信息
python spider/run_tiered_crawler.py --stats

# 只爬取热数据（7天内发布的作品）
python spider/run_tiered_crawler.py --hot

# 只爬取冷数据（7天前发布的作品）
python spider/run_tiered_crawler.py --cold

# 爬取全部数据
python spider/run_tiered_crawler.py --all

# 根据当前时间自动选择（用于定时任务）
python spider/run_tiered_crawler.py --scheduled
```

### 定时任务

使用 systemd timer 管理定时任务：

| 服务 | 说明 |
|-----|------|
| `bilibili-tiered-crawler.timer` | 分层爬虫定时器（每小时） |
| `bilibili-views-crawler.timer` | 作品数据爬虫定时器 |
| `bilibili-spider.timer` | 粉丝数爬虫定时器 |

```bash
# 启用分层爬虫定时任务
sudo systemctl enable --now infra/systemd/bilibili-tiered-crawler.timer

# 查看定时任务状态
systemctl list-timers --all | grep bilibili
```

---

## 实用工具

### 部署脚本 (scripts/)
- `dev_start_services.sh` - 开发环境启动脚本
- `dev_stop_services.sh` - 开发环境停止脚本
- `build_start_services.sh` - 生产环境启动脚本
- `build_stop_services.sh` - 生产环境停止脚本
- `create_symlinks.sh` - 创建应用级软链接
- `create_infra_symlinks.sh` - 创建基础设施软链接
- `bilibili_tiered_cron.sh` - 分层爬虫定时任务脚本
- `bilibili_views_cron.sh` - 作品数据爬虫定时任务脚本
- `bilibili_fans_count_cron.sh` - B站粉丝数爬虫定时任务脚本
- `auto_sync_gallery.py` - 自动同步图集数据
- `sync_cloud_picture.py` - 同步弹幕云图
- `import_cloud_picture_to_livestream.py` - 导入弹幕云图到直播日历
- `setup_songlist_subdomain.sh` - 设置歌单子域名

### 后端工具 (repo/xxm_fans_backend/tools/)
- `import_public_data.py` - 导入公开数据
- `import_song_records.py` - 导入演唱记录
- `import_livestream_data.py` - 导入直播数据
- `download_covers.py` - 下载封面图片
- `migrate_livestream_cover.py` - 迁移直播封面
- `ingest_follower_data.py` - 导入粉丝数据
- **spider/** - 爬虫工具模块
  - `export_views.py` - 数据导出模块
  - `crawl_views.py` - 核心爬虫模块
  - `import_views.py` - 数据导入模块
  - `export_tiered.py` - 分层数据导出模块
- **bilibili/** - B站 API 封装模块（供其他脚本调用）
  - `api_client.py` - B站 API 客户端
  - `cover_downloader.py` - 封面下载工具类
  - `models.py` - B站数据模型

### 项目工具 (tools/)
- `download_workstatic_covers.py` - 下载作品封面
- `reorganize_gallery_structure.py` - 重组图集结构
- `reorganize_weibo_gallery.py` - 重组微博图集
- `update_gallery_database.py` - 更新图集数据库

---

## 项目亮点

1. **模块化设计**: 核心功能拆分为独立应用，便于维护和扩展
2. **模板化歌单系统**: 配置驱动的动态模型创建，一行配置添加艺术家
3. **统一响应格式**: 标准化的API响应格式
4. **DDD架构**: 前端采用领域驱动设计
5. **性能测试**: 内置完整的Locust性能测试套件
6. **图集管理**: 完整的图集管理系统，支持多级分类、自动缩略图生成
7. **直播日历**: 完整的直播记录管理系统，支持BV号导入
8. **智能爬虫系统**: 分层爬虫优化（热数据每小时、冷数据每天3次）、定时任务管理、粉丝数追踪
9. **双CDN支持**: 支持双 CDN 配置
10. **配置集中管理**: 统一的 `env/` 目录管理所有环境变量
11. **AI Agent 技能**: 内置自定义技能模块，支持 B站工具、UI优化等

---

## 关键约束

1. **不能修改** SongRecord 和 Song 核心模型结构
2. **遵循** 现有的代码风格和架构模式
3. **保持** API接口的向后兼容性
4. **使用** 统一的响应格式和异常处理机制
5. **遵循** DDD架构原则（前端）
6. **使用** TypeScript严格模式
7. **使用** Tailwind CSS进行样式管理

---

## 文档资源

- `README.md` - 项目说明文档
- `repo/xxm_fans_frontend/AGENTS.md` - 前端开发规范
- `repo/xxm_fans_backend/IFLOW.md` - 后端技术文档
- `spider/TIERED_CRAWLER_README.md` - 分层爬虫文档
- `spider/README.md` - 爬虫使用文档
- `scripts/AUTO_SYNC_GALLERY_README.md` - 图集同步文档
- `doc/` 目录 - 详细的功能文档和技术报告

---

## 更新日志

| 日期 | 更新内容 |
|-----|---------|
| 2026-02-12 | 更新爬虫系统文档，添加分层爬虫说明；更新前端架构描述；添加 AI Agent 技能模块说明 |
