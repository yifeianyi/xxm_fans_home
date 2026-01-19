# XXM Fans Home - 项目上下文文档

## 项目概述

XXM Fans Home 是一个现代化的音乐粉丝网站框架，采用前后端分离架构。该项目作为音乐人、歌手或艺术家的粉丝站建设模板，提供完整的音乐管理、演唱记录追踪、排行榜、粉丝二创作品展示等核心功能。

**示范案例**：[小满虫之家](https://www.xxm8777.cn) - 基于本框架建设的咻咻满（XXM）粉丝网站。

### 核心特性

- **音乐资产管理**：完整的歌曲信息、演唱记录、曲风分类和标签管理系统
- **智能搜索筛选**：支持多维度歌曲搜索和高级筛选功能
- **实时排行榜**：多时间维度的热门歌曲排行榜展示
- **粉丝二创平台**：精选二创作品展示和合集管理
- **模板化歌单**：配置驱动的动态歌单系统，一行配置即可添加新歌手或艺术家
- **双环境支持**：完善的开发和生产环境配置
- **配置集中管理**：统一的配置文件管理方案

## 技术架构

### 后端技术栈
- **框架**：Django 5.2.3 + Django REST Framework 3.15.2
- **数据库**：SQLite（开发环境），支持多数据库配置
- **编程语言**：Python 3.8+
- **API**：RESTful API
- **环境管理**：python-dotenv 1.0.1
- **其他依赖**：Pillow 10.2.0、django-cors-headers 4.9.0、requests 2.31.0

### 前端技术栈
- **框架**：React 19.2.3 + TypeScript 5.8.2
- **构建工具**：Vite 6.2.0
- **路由**：React Router DOM 7.12.0
- **图标**：Lucide React 0.562.0
- **样式**：Tailwind CSS（通过 CDN 引入）
- **图片处理**：Sharp 0.34.5

### 部署架构
- **Web服务器**：Nginx
- **应用服务器**：Gunicorn
- **进程管理**：systemd
- **容器化**：Docker（可选）

## 项目结构

```
xxm_fans_home/
├── .iflow/                  # iFlow 技能配置
│   └── skills/
│       ├── api/            # API 相关技能
│       ├── frontend-design/ # 前端设计技能
│       ├── module/         # 模块相关技能
│       └── skill-create/   # 技能创建指南
├── doc/                     # 项目文档
│   ├── backend/            # 后端文档
│   ├── frontend/           # 前端文档
│   └── [各种集成指南和测试报告]
├── env/                     # 环境配置目录（统一配置管理）
│   ├── backend.env         # 后端环境变量配置
│   └── frontend.env        # 前端环境变量配置
├── infra/                   # 基础设施配置
│   ├── gunicorn/           # Gunicorn 配置
│   ├── nginx/              # Nginx 配置
│   └── systemd/            # systemd 服务配置
├── repo/                    # 代码仓库（Git 子模块）
│   ├── xxm_fans_backend/    # Django 后端项目
│   └── xxm_fans_frontend/   # React 前端项目
├── scripts/                 # 部署和工具脚本
├── spider/                  # 爬虫目录
├── .gitignore               # Git 忽略配置
├── .gitmodules              # Git 子模块配置
├── README.md                # 项目说明文档
└── AGENTS.md                # 本文件
```

### 后端应用模块（repo/xxm_fans_backend/）

1. **song_management** - 音乐资产管理应用
   - Song：音乐作品基本信息
   - SongRecord：演出/表演记录
   - Style：曲风分类
   - Tag：标签系统
   - Admin 功能：合并作品、拆分作品、批量标记、BV号导入

2. **fansDIY** - 粉丝二创作品管理应用
   - Collection：二创作品合集分类
   - Work：单个二创作品信息
   - Admin 功能：BV号导入、封面管理、批量标记

3. **site_settings** - 网站设置应用
   - SiteSettings：全局配置管理
   - Recommendation：个性化推荐内容

4. **data_analytics** - 数据分析应用
   - WorkStatic：数据统计分析
   - WorkMetricsHour：小时级指标追踪
   - CrawlSession：爬取任务管理

5. **songlist** - 模板化歌单应用（核心创新）
   - 配置驱动的动态模型创建
   - 一行配置添加艺术家、自动生成模型和API

6. **core** - 核心共享模块
   - cache.py：缓存管理工具
   - exceptions.py：自定义异常类
   - responses.py：统一响应格式
   - utils/：通用工具函数

### 前端功能模块（repo/xxm_fans_frontend/）

- **domain/**：领域层（业务模型和服务接口）
  - types.ts：定义所有领域模型类型
  - api/：定义服务接口
- **infrastructure/**：基础设施层（API实现和配置）
  - api/：真实后端API服务实现
  - config/：配置管理
- **presentation/**：表现层（React组件和页面）
  - components/：React组件
  - pages/：页面组件
  - hooks/：自定义Hook
- **shared/**：共享层（工具函数和服务）
  - services/：共享服务
  - utils/：工具函数

## 快速开始

### 环境要求
- Python 3.8+
- Node.js 18+
- npm

### 初始化 Git 子模块

由于后端和前端代码作为 Git 子模块管理，首次克隆项目后需要初始化子模块：

```bash
# 初始化并更新子模块
git submodule update --init --recursive

# 如果子模块为空，可能需要单独克隆
cd repo/xxm_fans_backend
git checkout main
cd ../xxm_fans_frontend
git checkout main
```

### 开发环境快速启动

```bash
# 1. 创建软链接（Windows 下可能需要手动创建或使用 Git Bash）
cd scripts
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
cd scripts
./create_symlinks.sh

# 2. 创建基础设施软链接（可选，需要 root 权限）
sudo ./create_infra_symlinks.sh

# 3. 启动生产环境服务
./build_start_services.sh

# 4. 停止服务
./build_stop_services.sh
```

### 手动安装步骤

#### 后端环境设置

```bash
cd repo/xxm_fans_backend

# 创建并激活虚拟环境
python -m venv venv
# Windows
venv\Scripts\activate
# Linux/Mac
source venv/bin/activate

# 安装 Python 依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate
python manage.py migrate --database=songlist_db

# 创建超级用户（可选）
python manage.py createsuperuser

# 启动后端
python manage.py runserver 0.0.0.0:8000
```

#### 前端环境设置

```bash
cd repo/xxm_fans_frontend
npm install
npm run dev
```

## 构建和运行

### 前端构建

```bash
cd repo/xxm_fans_frontend

# 生产构建（使用 vite.config.prod.ts）
npm run build

# 开发环境构建（使用 vite.config.ts）
npm run build:dev

# 预览生产构建
npm run preview
```

### 后端部署

```bash
cd repo/xxm_fans_backend

# 收集静态文件
python manage.py collectstatic --noinput

# 使用 Gunicorn 运行
gunicorn xxm_fans_home.wsgi:application -c ../../infra/gunicorn/gunicorn_config.py
```

### 集成测试

```bash
cd scripts
./test_integration.sh
```

## 开发规范

### 后端开发规范

**分层架构规范**：
- **models/**：只包含数据模型定义，不包含业务逻辑
- **services/**：包含所有业务逻辑，可被 API 和 Admin 复用
- **api/**：只负责 HTTP 请求处理和响应格式化
- **admin/**：Django Admin 后台管理配置

**统一响应格式规范**：
- 使用 `core/responses.py` 提供的响应函数
- 成功响应使用 `success_response()`
- 错误响应使用 `error_response()`
- 分页响应使用 `paginated_response()`

**异常处理规范**：
- 使用 `core/exceptions.py` 提供的异常类
- 在 services 层抛出业务异常
- 在 api 层捕获异常并返回错误响应

**代码约束**：
- 不能修改 SongRecord 和 Song 核心模型结构
- 遵循现有的代码风格和架构模式
- 保持 API 接口的向后兼容性

### 前端开发规范

**架构原则**：
- **依赖倒置**：高层模块不依赖低层模块，两者都依赖抽象（接口）
- **单一职责**：每个类、函数、组件只负责一件事
- **开闭原则**：对扩展开放，对修改关闭
- **领域驱动**：业务逻辑集中在领域层，技术实现在基础设施层

**代码风格**：
- 使用 TypeScript 编写所有代码，充分利用类型系统
- 组件使用函数式组件 + Hooks
- 文件命名：
  - 组件文件：PascalCase（如 `SongTable.tsx`）
  - 工具函数和 Hook：camelCase（如 `useSongData.ts`）
  - 接口定义：PascalCase，以 `I` 开头（如 `ISongService`）

**类型定义规范**：
- **领域类型**：所有业务领域模型在 `domain/types.ts` 中定义
- **接口定义**：服务接口在 `domain/api/` 中定义
- **API 类型**：API 相关类型在 `infrastructure/api/apiTypes.ts` 中定义
- **类型安全**：避免使用 `any` 类型，优先使用具体类型或泛型

**组件开发规范**：
- **组件职责**：每个组件只负责一个功能，保持组件轻量
- **组件拆分**：大型组件（超过200行）应拆分为多个小组件
- **Props 定义**：使用 TypeScript 接口定义 Props 类型
- **事件处理**：使用 `useCallback` 缓存事件处理函数
- **性能优化**：使用 `useMemo` 缓存计算结果
- **样式管理**：使用 Tailwind CSS，保持样式一致性

## 环境变量配置

项目采用**配置文件集中管理**方案，所有环境变量统一存放在 `env/` 目录下：

```bash
env/
├── backend.env    # 后端环境变量配置
└── frontend.env   # 前端环境变量配置

# 软链接
repo/xxm_fans_backend/.env -> env/backend.env
repo/xxm_fans_frontend/.env -> env/frontend.env
```

### 后端环境变量（env/backend.env）

```bash
# Django 配置
DJANGO_DEBUG=True
DJANGO_SECRET_KEY=django-insecure-dev-key-for-local-testing-only
DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1,172.27.171.134

# Spotify API 配置（可选）
SPOTIPY_CLIENT_ID=your_client_id_here
SPOTIPY_CLIENT_SECRET=your_client_secret_here
SPOTIPY_REDIRECT_URI=http://127.0.0.1:8080
```

### 前端环境变量（env/frontend.env）

```bash
# API 配置
VITE_API_BASE_URL=/api
```

## 软链接配置

项目部署时需要创建多个软链接，用于环境配置、媒体资源和基础设施配置。

### 应用级软链接（必需）

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
```

### 基础设施配置软链接（可选，需要 root 权限）

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

## API 接口文档

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

### 其他
- `GET /api/recommendation/` - 推荐语
- `GET /api/site-settings/` - 网站设置
- `GET /api/data-analytics/` - 数据分析接口

### 媒体文件
- `/covers/*` - 封面图片
- `/footprint/*` - 二创图片资源
- `/media/*` - 其他媒体文件

## 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| Nginx | 8080 | 统一入口，代理前端和后端 |
| React 前端 | 5173 | Vite 开发服务器 |
| Django 后端 | 8000 | Django 开发服务器 |

## 实用工具

### 部署脚本（位于 scripts/）
- `create_symlinks.sh` - 创建应用级软链接
- `create_infra_symlinks.sh` - 创建基础设施配置软链接（需要 root 权限）
- `dev_start_services.sh` - 开发环境启动脚本
- `dev_stop_services.sh` - 开发环境停止脚本
- `build_start_services.sh` - 生产环境启动脚本
- `build_stop_services.sh` - 生产环境停止脚本
- `test_integration.sh` - 集成测试脚本

### 数据管理（位于 repo/xxm_fans_backend/tools/）
- `import_public_data.py` - 导入公开数据
- `export_public_data.py` - 导出公开数据
- `import_songs_from_json.py` - 从 JSON 导入歌曲
- `import_song_records.py` - 导入演唱记录
- `merge_songs.py` - 合并歌曲

### B站集成
- `bilibili_importer.py` - B站视频导入

**BV号导入功能**：
- 支持通过B站BV号批量导入演唱记录
- 自动解析视频分P标题，提取歌曲名称和演出日期
- 支持的视频标题格式：`歌曲名称-YYYY年M月D日`
  - 示例：`小幸运-2025年6月12日`、`晴天-2024年12月25日`
- 自动下载封面图片
- 支持冲突处理和手动关联歌曲

## 日志文件

| 日志 | 路径 |
|------|------|
| Gunicorn 访问日志 | `/tmp/gunicorn_access.log` |
| Gunicorn 错误日志 | `/tmp/gunicorn_error.log` |
| Nginx 错误日志 | `/tmp/nginx/error.log` |
| Nginx 访问日志 | `/tmp/nginx/access.log` |

## Git 规范

忽略的文件和目录：
- media/
- static/
- logs/
- data/
- venv/
- node_modules/
- .env（软链接，实际配置文件在 env/ 目录中）

## 项目亮点

1. **模块化设计**：核心功能拆分为独立应用，便于维护和扩展
2. **分层架构**：清晰的 models-services-api 分层，代码结构清晰
3. **模板化歌单系统**：配置驱动的动态模型创建，一行配置即可添加新艺术家
4. **统一响应格式**：标准化的 API 响应格式，便于前端对接
5. **自定义异常**：完善的异常处理机制，提升代码健壮性
6. **Admin 优化**：批量标记功能优化，支持搜索和左右分栏布局
7. **DDD 架构**：前端采用领域驱动设计，严格遵循依赖倒置原则
8. **性能测试**：内置完整的 Locust 性能测试套件
9. **工具脚本**：提供丰富的工具脚本，提升开发效率
10. **生产优化**：前端生产构建包含文件名哈希、代码分割、压缩等优化
11. **Gunicorn 配置**：集中化的 Gunicorn 配置，便于性能调优
12. **双环境支持**：完善的开发和生产环境配置和脚本
13. **二创资源**：专门的二创图片资源路径和 Nginx 配置
14. **配置集中管理**：统一的 `env/` 目录管理所有环境变量，通过软链接实现配置共享
15. **高度可定制**：框架化设计，支持快速定制和功能扩展

## 常见问题

### 1. Git 子模块为空

首次克隆项目后，需要初始化子模块：

```bash
git submodule update --init --recursive
```

如果子模块仍然为空，可能需要单独进入子模块目录并 checkout：

```bash
cd repo/xxm_fans_backend
git checkout main
cd ../xxm_fans_frontend
git checkout main
```

### 2. 软链接创建失败（Windows）

在 Windows 系统上，可能需要使用管理员权限或使用 Git Bash 来创建软链接：

```bash
# 使用 Git Bash
cd scripts
bash create_symlinks.sh
```

或者手动创建软链接：

```bash
# Windows 命令提示符（需要管理员权限）
mklink /D "repo\xxm_fans_backend\.env" "env\backend.env"
mklink /D "repo\xxm_fans_frontend\.env" "env\frontend.env"
```

### 3. 端口被占用

如果端口被占用，可以修改配置文件中的端口号：

- **Nginx 端口**：`infra/nginx/xxm_nginx.conf` 中的 `listen 8080;`
- **Django 端口**：启动命令中的 `0.0.0.0:8000`
- **Vite 端口**：`repo/xxm_fans_frontend/vite.config.ts` 中的 `server.port`

### 4. 数据库连接失败

检查数据库文件是否存在：

```bash
cd repo/xxm_fans_backend
ls -lh *.sqlite3
```

如果数据库不存在，运行迁移：

```bash
python manage.py migrate
python manage.py migrate --database=songlist_db
```

### 5. 服务启动失败

查看日志文件排查问题：

```bash
# 查看 Gunicorn 日志
tail -f /tmp/gunicorn_error.log

# 查看 Nginx 日志
tail -f /tmp/nginx/error.log
```

## 文档资源

### 项目文档
- `README.md` - 项目说明文档
- `AGENTS.md` - 本文件，项目上下文文档

### 后端文档
- `repo/xxm_fans_backend/doc/songlist独立表架构说明.md` - 模板化歌单系统完整文档
- `repo/xxm_fans_backend/doc/API文档.md` - API 接口详细文档
- `repo/xxm_fans_backend/doc/ADMIN功能文档.md` - Admin 功能说明
- `repo/xxm_fans_backend/doc/项目结构重构方案.md` - 项目架构设计

### 前端文档
- `repo/xxm_fans_frontend/doc/api_adaptation_plan.md` - API 适配计划
- `repo/xxm_fans_frontend/doc/API_doc.md` - API 文档
- `repo/xxm_fans_frontend/doc/project_analysis_report.md` - 项目分析报告

### 基础设施文档
- `infra/gunicorn/README.md` - Gunicorn 配置说明
- `infra/gunicorn/CHANGELOG.md` - Gunicorn 优化记录
- `infra/nginx/FOOTPRINT_CONFIG.md` - 二创资源配置说明

### 脚本文档
- `scripts/README.md` - 部署脚本说明
- `scripts/FANS_DIY_DATA_COPY.md` - 数据复制文档
- `doc/DEPLOYMENT_SYMLINKS.md` - 部署软链接配置说明

## 性能测试

项目内置完整的 Locust 性能测试套件，位于 `repo/xxm_fans_backend/test/` 目录。

### 运行测试

```bash
cd repo/xxm_fans_backend/test
# Linux/Mac
./run_performance_test.sh
# Windows
run_performance_test.bat
```

### 测试配置
- 并发用户数：100
- 启动速率：10 users/second
- 测试时长：10分钟
- 目标地址：可配置

## 未来改进方向

1. 集成第三方音乐平台 API（Spotify、网易云音乐等）自动为作品分配曲风
2. 优化精选二创页面图片懒加载和 CDN 加速
3. 增加更多数据可视化功能和仪表盘
4. 支持用户评论、点赞和互动功能
5. 移动端适配优化和 PWA 支持
6. 数据分析功能增强
7. 添加单元测试和集成测试
8. 实现 CI/CD 自动化部署
9. CDN 集成优化图片加载速度
10. 实现图片自动压缩和格式转换
11. 支持多语言国际化
12. 增加用户系统和权限管理
13. 支持 RSS 订阅和邮件通知

## 联系方式

如有问题，请查看项目文档或提交 Issue。

---

**最后更新**：2026年1月19日