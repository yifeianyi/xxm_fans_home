# XXM Fans Home 前后端联调指南

## 概述

本文档说明如何在本地环境启动和测试 XXM Fans Home 的前后端联调。

## 服务架构

```
┌─────────────────────────────────────────────────────────┐
│                        浏览器                            │
│                   http://localhost:8080                  │
└────────────────────┬────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────┐
│                      Nginx (8080)                        │
│  - / → 前端 (5173)                                        │
│  - /api/ → 后端 API (8000)                               │
│  - /media/ → 媒体文件 (8000)                             │
└───────┬───────────────┬───────────────┬─────────────────┘
        │               │               │
        ▼               ▼               ▼
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ React 前端   │  │ Django 后端  │  │  媒体文件    │
│   (5173)     │  │   (8000)     │  │  /media/     │
└──────────────┘  └──────────────┘  └──────────────┘
```

## 快速开始

### 1. 启动所有服务

```bash
cd /home/yifeianyi/Desktop/xxm_fans_home
./start_services.sh
```

### 2. 测试服务

```bash
./test_integration.sh
```

### 3. 访问应用

打开浏览器访问：http://localhost:8080/

### 4. 停止所有服务

```bash
./stop_services.sh
```

## 服务端口

| 服务 | 端口 | 说明 |
|------|------|------|
| Nginx | 8080 | 统一入口，代理前端和后端 |
| React 前端 | 5173 | Vite 开发服务器 |
| Django 后端 | 8000 | Django 开发服务器 |

## 目录结构

```
xxm_fans_home/
├── repo/
│   ├── xxm_fans_backend/      # Django 后端
│   │   ├── media/             # 媒体文件（符号链接）
│   │   ├── covers/            # 封面图片（符号链接）
│   │   ├── db.sqlite3         # 主数据库
│   │   ├── songlist.sqlite3   # 歌单数据库
│   │   └── view_data.sqlite3  # 数据分析数据库
│   └── xxm_fans_frontend/     # React 前端
├── media/                     # 媒体文件目录
│   └── covers/                # 封面图片
├── infra/nginx/               # Nginx 配置
│   └── xxm_nginx.conf         # Nginx 配置文件
├── start_services.sh          # 启动脚本
├── stop_services.sh           # 停止脚本
└── test_integration.sh        # 测试脚本
```

## 符号链接说明

为了支持当前的目录结构，创建了以下符号链接：

1. **后端 media 链接**:
   ```bash
   /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend/media
   → /home/yifeianyi/Desktop/xxm_fans_home/media
   ```

2. **后端 covers 链接**:
   ```bash
   /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend/covers
   → /home/yifeianyi/Desktop/xxm_fans_home/media/covers
   ```

## 日志文件

| 日志 | 路径 |
|------|------|
| 后端日志 | `/tmp/backend.log` |
| 前端日志 | `/tmp/frontend.log` |
| Nginx 错误日志 | `/tmp/nginx/error.log` |
| Nginx 访问日志 | `/tmp/nginx/access.log` |

## API 接口测试

### 主要接口

```bash
# 歌曲列表
curl http://localhost:8080/api/songs/

# 曲风列表
curl http://localhost:8080/api/styles/

# 标签列表
curl http://localhost:8080/api/tags/

# 推荐语
curl http://localhost:8080/api/recommendation/

# 粉丝二创合集
curl http://localhost:8080/api/fansDIY/collections/
```

### 媒体文件测试

```bash
# 默认封面
curl -I http://localhost:8080/media/covers/default.jpg

# 咻咻满头像
curl -I http://localhost:8080/media/covers/咻咻满.jpg
```

## 常见问题

### 1. 端口被占用

如果端口被占用，可以修改配置文件中的端口号：

- **Nginx 端口**: `infra/nginx/xxm_nginx.conf` 中的 `listen 8080;`
- **Django 端口**: 启动命令中的 `0.0.0.0:8000`
- **Vite 端口**: `repo/xxm_fans_frontend/vite.config.ts` 中的 `server.port`

### 2. 图片无法加载

确保符号链接正确创建：

```bash
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend
ls -la media
ls -la covers
```

### 3. 数据库连接失败

检查数据库文件是否存在：

```bash
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend
ls -lh *.sqlite3
```

如果数据库不存在，运行迁移：

```bash
python3 manage.py migrate
```

### 4. 服务启动失败

查看日志文件排查问题：

```bash
# 查看后端日志
tail -f /tmp/backend.log

# 查看前端日志
tail -f /tmp/frontend.log

# 查看 Nginx 日志
tail -f /tmp/nginx/error.log
```

## 手动启动服务

如果需要手动启动各个服务：

### 启动 Django 后端

```bash
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend
python3 manage.py runserver 0.0.0.0:8000
```

### 启动 React 前端

```bash
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_frontend
npm run dev
```

### 启动 Nginx

```bash
mkdir -p /tmp/nginx
nginx -c /home/yifeianyi/Desktop/xxm_fans_home/infra/nginx/xxm_nginx.conf -p /tmp/nginx
```

## 测试检查清单

启动服务后，确保以下功能正常：

- [ ] 前端页面可以访问
- [ ] 可以浏览歌曲列表
- [ ] 可以查看演唱记录
- [ ] 可以查看热歌榜
- [ ] 可以浏览粉丝二创作品
- [ ] 图片可以正常加载
- [ ] API 接口返回正确的数据
- [ ] 没有控制台错误

## 性能优化建议

1. **启用缓存**: 配置 Redis 缓存以提高 API 响应速度
2. **静态文件**: 生产环境使用 Nginx 直接提供静态文件
3. **数据库优化**: 为常用查询字段添加索引
4. **前端优化**: 使用生产构建配置 `vite.config.prod.ts`

## 下一步

- [ ] 导入测试数据
- [ ] 配置 Redis 缓存
- [ ] 设置生产环境部署
- [ ] 配置 HTTPS
- [ ] 添加监控和日志

## 联系方式

如有问题，请查看项目文档或提交 Issue。