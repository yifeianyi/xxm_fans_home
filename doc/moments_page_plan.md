# 满の动态 页面实现计划

## 概述

为小满虫之家添加"满の动态"页面，抓取咻咻满的微博和B站动态，起到快照作用。

## 架构总览

| 层级 | 新增/修改内容 |
|------|-------------|
| 后端 Django App | 新建 `moments` 应用（模型、API、服务层） |
| 爬虫脚本 | 新建 `spider/crawl_moments.py`（统一微博+B站动态爬取） |
| 定时任务 | 新建 systemd timer（每5分钟） |
| 前端页面 | 新建 `MomentsPage` 页面组件 |
| 前端路由 | App.tsx 添加 `/moments` 路由 |
| 导航栏 | Navbar 左侧最前面新增"满の动态"入口 |

## 后端实现

### 数据模型

- **Moment**: 统一动态内容（source, source_id, content, images, publish_time, 互动数据等）
- **PlatformCookie**: Cookie管理（platform, cookie_string, is_valid, expire_notified）

### API

- `GET /api/moments/` - 动态列表（分页，按 source 筛选，时间倒序）
- `GET /api/moments/<id>/` - 单条动态详情

### 服务层

- `cookie_service.py` - Cookie 读写 + 过期检测 + 邮件通知
- `image_service.py` - 图片下载 + 缩略图生成（复用 ThumbnailGenerator）

### 邮件配置

新增 SMTP 配置到 settings.py，环境变量在 env/backend.env 中配置。

## 爬虫脚本

- B站：requests 调用 `x/polymer/web-dynamic/v1/feed/space` API
- 微博：requests 调用 `m.weibo.cn/api/container/getIndex` API
- 每5分钟增量爬取 → 去重 → 写DB → 下载图片 → 生成缩略图
- 检测cookie过期 → 标记无效 → 发邮件

## 定时任务

- systemd timer: `OnCalendar=*-*-* *:0/5:00`
- 调用 `scripts/moments_cron.sh`

## 前端实现

- 页面组件: `MomentsPage.tsx` - 时间线布局，支持全部/微博/B站筛选
- Navbar: 左侧最前面添加"满の动态"入口（Newspaper 图标）
- 路由: `/moments`，lazy-load

## 测试

| 测试类型 | 框架 | 文件 |
|---------|------|------|
| 后端模型 | Django unittest | `moments/tests.py` |
| 后端 API | DRF APITestCase | `moments/tests.py` |
| 服务层 | Django TestCase + mock | `moments/tests.py` |
| 爬虫 | Python unittest + mock | `spider/test_crawl_moments.py` |
| 前端 API | Node.js 集成测试 | `test/test-moments-api.js` |
