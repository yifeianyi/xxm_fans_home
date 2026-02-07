# 双CDN实施方案

**项目名称**: XXM Fans Home（小满虫之家）
**方案类型**: 基础设施优化
**制定日期**: 2026年2月2日
**版本**: v1.3
**实施目标**: 实现国内腾讯云CDN加速 + Cloudflare DNS智能解析方案，提升用户访问速度，控制成本，保障安全。

**重要说明**:
1. 本方案基于实际线上配置 `prod_xxm_home.conf` 进行优化
2. 直接修改现有Nginx配置文件，不创建新文件
3. 使用origin子域名作为CDN回源地址，方便后续更换服务器
4. 保持现有SSL证书、域名结构和核心配置不变

---

## 一、方案概述

### 1.1 背景分析

**当前项目状况**:
- 网站包含大量图片资源（约13GB）
- 图片已优化为WebP格式（缩略图15KB/张，原图150KB/张，GIF 2-3MB/张）
- 图集包含87个短视频文件（5秒以内，平均5.14MB/个，总计447MB）
- 预计视频发布后有2-3天流量高峰（日活300-400人）
- 未使用对象存储，静态资源直接从源站服务器提供
- 服务器带宽有限，需要缓解带宽压力

**核心需求**:
1. **加速访问**: 提升国内外用户访问速度
2. **成本控制**: 避免CDN流量费用失控
3. **安全防护**: 防止恶意刷流量、防盗链
4. **高可用性**: 确保CDN停服时有备用方案

**现有配置情况**:
- 已配置Let's Encrypt SSL证书（admin.xxm8777.cn 和 www.xxm8777.cn）
- 已配置HTTP自动重定向到HTTPS
- 已配置主域名到www的重定向
- Admin后台独立域名，直连源站
- 前端和后端已分离配置

**CDN优化重点**:
- 为 www.xxm8777.cn 添加CDN加速
- 优化静态资源缓存策略
- 添加视频文件支持
- 保持现有SSL配置不变

### 1.2 方案选择

采用**腾讯云CDN + Cloudflare DNS**架构:

| 组件 | 服务商 | 选择理由 |
|------|----------|----------|
| **国内CDN** | 腾讯云CDN | 新用户免费100GB/月，控制台功能完善，用量封顶配置简单 |
| **DNS解析** | Cloudflare | 全球免费DNS服务，智能解析，DDoS防护，防劫持 |

**方案工作原理**:
- Cloudflare提供DNS智能解析服务
- 国内用户访问腾讯云CDN节点（通过CNAME）
- 国外用户直接访问源站（延迟可接受）
- CDN回源到origin.xxm8777.cn子域名（便于更换服务器）

---

## 二、架构设计

### 2.1 整体架构图

```
┌─────────────────────────────────────────────────────────────┐
│                         用户访问层                            │
├──────────────────────────────┬──────────────────────────────┤
│       国内用户                │       国外用户                │
│   (IP: 中国大陆)              │   (IP: 中国以外)              │
└──────────────────────────────┼──────────────────────────────┘
                               │
                    DNS智能解析（Cloudflare）
                               │
                ┌──────────────┴──────────────┐
                ↓                             ↓
┌──────────────────────────┐   ┌──────────────────────────┐
│      腾讯云CDN节点         │   │   直连源站（无CDN）      │
│   (国内边缘节点加速)       │   │   (延迟可接受)            │
└──────────────────────────┘   └──────────────────────────┘
                │                             │
                │ CDN回源                    │ 直接访问
                ↓                             ↓
        origin.xxm8777.cn               www.xxm8777.cn
                │                             │
                └──────────────┬──────────────┘
                               │
┌─────────────────────────────────────────────────────────────┐
│                        源站服务器                             │
│   Nginx (端口443 HTTPS)  →  Django API (端口8000)            │
│   静态资源CDN加速         →  动态请求转发处理                 │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 域名规划（基于现有配置）

**当前线上已配置的域名**:

| 用途 | 域名 | 解析方式 | 说明 |
|------|------|----------|------|
| **用户前台** | `www.xxm8777.cn` | CNAME → 腾讯云CDN | 国内CDN加速，已有SSL证书 |
| **管理后台** | `admin.xxm8777.cn` | A记录 → 源站IP | 直连源站，不走CDN，已有SSL证书 |
| **主域名** | `xxm8777.cn` | 重定向到www | 统一访问入口 |

**CDN新增域名**:

| 用途 | 域名 | 解析方式 | 说明 |
|------|------|----------|------|
| **源站回源** | `origin.xxm8777.cn` | A记录 → 源站IP | CDN回源专用，便于更换服务器 |

**安全优势**:
- 管理后台独立域名，已有SSL证书，权限隔离
- 前台和后台访问路径完全分离
- 使用origin子域名回源，更换服务器时只需修改DNS，无需修改CDN配置

---

## 三、DNS配置方案

### 3.1 DNS提供商选择

**推荐**: 使用Cloudflare作为DNS提供商（免费版即可）

**原因**:
1. 提供免费的DNS解析服务
2. 全球DNS节点，解析速度快
3. 支持API管理，方便自动化
4. 提供DDoS防护和DNS劫持防护
5. 免费版功能即可满足需求

### 3.2 DNS记录配置

在Cloudflare DNS管理面板，保留现有记录并添加腾讯云CDN相关记录：

**保留现有记录**:
| 类型 | 名称 | 内容 | 代理状态 | TTL |
|------|------|------|----------|-----|
| **A** | `admin` | 源站服务器IP | 仅DNS（灰色云） | 1小时 |

**新增/修改记录**:
| 类型 | 名称 | 内容 | 代理状态 | TTL | 说明 |
|------|------|------|----------|-----|------|
| **A** | `origin` | 源站服务器IP | 仅DNS（灰色云） | 1小时 | CDN回源专用域名 |
| **CNAME** | `www` | 腾讯云CDN提供的CNAME | 仅DNS（灰色云） | 1分钟 | **需要修改**，从A记录改为CNAME |

**重要说明**:
1. `admin`记录保持不变，继续直连源站
2. `www`记录需要从A记录改为CNAME，指向腾讯云CDN
3. `www`记录的代理状态必须设置为"仅DNS"（灰色云），因为已经配置了腾讯云CDN
4. `origin`域名仅用于CDN回源，不对外暴露

### 3.3 腾讯云CDN域名配置

在腾讯云CDN控制台添加加速域名：

- **加速域名**: `www.xxm8777.cn`
- **业务类型**: 静态加速
- **源站类型**: 源站域名
- **回源域名**: `origin.xxm8777.cn`
- **回源端口**: 443（HTTPS）
- **回源协议**: HTTPS

---

## 四、源站Nginx配置调整

### 4.1 配置目标

1. **优化缓存策略**: 配置合适的HTTP缓存头，差异化缓存
2. **视频文件支持**: 添加HTTP Range支持，支持断点续传
3. **访问日志优化**: 减少不必要的日志记录，节省磁盘IO
4. **保持现有配置**: SSL证书、域名重定向、安全头等保持不变

### 4.2 生产环境Nginx配置（基于现有配置优化）

**注意**: 以下配置基于现有的 `prod_xxm_home.conf` 进行CDN优化，保持SSL证书等现有配置不变。

**新增配置**:
- 添加 `origin.xxm8777.cn` 域名的HTTP和HTTPS配置（用于CDN回源）
- 将admin和主站的HTTP重定向完全分离（独立server块）
- origin和www使用相同的网站配置（都提供静态资源和API）

**修改原则**:
1. 保持所有SSL证书配置不变
2. 保持所有域名重定向规则不变
3. 保持Admin后台配置不变
4. 仅优化主站（www.xxm8777.cn）的静态资源缓存策略

```nginx
# Admin HTTP 重定向：admin.xxm8777.cn → HTTPS
server {
	listen 80;
	server_name admin.xxm8777.cn;
	return 301 https://admin.xxm8777.cn$request_uri;
}

# 源站回源 HTTP 重定向：origin.xxm8777.cn → HTTPS
server {
	listen 80;
	server_name origin.xxm8777.cn;
	return 301 https://origin.xxm8777.cn$request_uri;
}

# 主站 HTTP 重定向：xxm8777.cn 和 www.xxm8777.cn → HTTPS + www
server {
	listen 80;
	server_name xxm8777.cn www.xxm8777.cn;
	return 301 https://www.xxm8777.cn$request_uri;
}

# HTTPS 重定向：xxm8777.cn → www.xxm8777.cn
server {
	listen 443 ssl http2;
	server_name xxm8777.cn;

	# SSL 配置
	ssl_certificate /etc/letsencrypt/live/xxm8777.cn-0001/fullchain.pem;
	ssl_certificate_key /etc/letsencrypt/live/xxm8777.cn-0001/privkey.pem;
	include /etc/nginx/ssl-params.conf;

	# 重定向到 www 域名，避免 CDN 缓存不一致
	return 301 https://www.xxm8777.cn$request_uri;
}

# 管理页面 - Admin 后台（保持不变，直连源站）
server {
	listen 443 ssl;
	server_name admin.xxm8777.cn;

	client_max_body_size 10M;

	# SSL 配置 - 使用 Let's Encrypt 证书
	ssl_certificate /etc/letsencrypt/live/admin.xxm8777.cn/fullchain.pem;
	ssl_certificate_key /etc/letsencrypt/live/admin.xxm8777.cn/privkey.pem;
	include /etc/nginx/ssl-params.conf;

	# 安全头
	add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
	add_header X-Content-Type-Options nosniff always;
	add_header X-Frame-Options "SAMEORIGIN" always;
	add_header X-XSS-Protection "1; mode=block" always;

	location = / {
        	return 301 /admin/;
	}
	# Django Admin 和 API
	location / {
		proxy_pass http://127.0.0.1:8000;
		proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header X-Forwarded-Proto $scheme;

		# Cookie 和 Session 支持
		proxy_cookie_path / /;
		proxy_redirect off;

		# 超时配置
		proxy_connect_timeout 60s;
		proxy_send_timeout 60s;
		proxy_read_timeout 120s;
	}

	# 静态文件
	location /static/ {
		alias /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend/staticfiles/;
		expires 30d;
		add_header Cache-Control "public, immutable";
		access_log off;
	}

	# 封面图片
	location /covers/ {
		alias /home/yifeianyi/Desktop/xxm_fans_home/media/covers/;
		autoindex off;
		expires 30d;
		add_header Cache-Control "public, immutable";
	}

	# 二创图片资源
	location /footprint/ {
		alias /home/yifeianyi/Desktop/xxm_fans_home/media/footprint/;
		autoindex off;
		expires 30d;
		add_header Cache-Control "public, immutable";
	}

	# 媒体文件
	location /media/ {
		alias /home/yifeianyi/Desktop/xxm_fans_home/media/;
		expires 30d;
		add_header Cache-Control "public, immutable";
	}
}

# 源站回源 HTTPS 服务器 - 与主站配置相同（用于CDN回源）
server {
	listen 443 ssl http2;
	server_name origin.xxm8777.cn;

	# SSL 配置 - 使用 Let's Encrypt 证书（与www共用）
	ssl_certificate /etc/letsencrypt/live/xxm8777.cn-0001/fullchain.pem;
	ssl_certificate_key /etc/letsencrypt/live/xxm8777.cn-0001/privkey.pem;
	include /etc/nginx/ssl-params.conf;

	# 安全头
	add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
	add_header X-Content-Type-Options nosniff always;
	add_header X-Frame-Options "SAMEORIGIN" always;
	add_header X-XSS-Protection "1; mode=block" always;

	root /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_frontend/dist;
	index index.html;
	client_max_body_size 3M;

	# 前端静态文件（支持 React Router）
	location / {
		try_files $uri $uri/ /index.html;
		expires 1h;
		add_header Cache-Control "public, must-revalidate";

		# Gzip 压缩配置
		gzip on;
		gzip_vary on;
		gzip_proxied any;
		gzip_comp_level 6;
		gzip_types text/plain text/css text/xml text/javascript application/json
		application/javascript application/xml+rss application/rss+xml font/truetype
		font/opentype application/vnd.ms-fontobject image/svg+xml;
	}

	# Django API
	location /api/ {
		proxy_pass http://127.0.0.1:8000;
		proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header X-Forwarded-Proto $scheme;

		# Cookie 和 Session 支持
		proxy_cookie_path / /;
		proxy_redirect off;

		# 超时配置
		proxy_connect_timeout 60s;
		proxy_send_timeout 60s;
		proxy_read_timeout 120s;

		# API不缓存
		add_header Cache-Control "no-cache, no-store, must-revalidate";
	}

	# Admin 访问限制（origin禁止访问 Admin）
	location /admin/ {
		return 403;
	}

	# SEO 文件 - 动态生成，转发到 Django
	location = /sitemap.xml {
		proxy_pass http://127.0.0.1:8000;
		proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header X-Forwarded-Proto $scheme;
	}

	location = /robots.txt {
		proxy_pass http://127.0.0.1:8000;
		proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header X-Forwarded-Proto $scheme;
	}

	# 静态文件 - Django静态资源
	location /static/ {
		alias /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend/staticfiles/;
		expires 1y;
		add_header Cache-Control "public, immutable";
		access_log off;
	}

	# 封面图片
	location /covers/ {
		alias /home/yifeianyi/Desktop/xxm_fans_home/media/covers/;
		autoindex off;
		expires 30d;
		add_header Cache-Control "public, immutable";
	}

	# 图集图片 - CDN优化（支持视频和差异化缓存）
	location /gallery/ {
		alias /home/yifeianyi/Desktop/xxm_fans_home/media/gallery/;
		autoindex off;

		# 缩略图：长期缓存（1年）
		location ~* /gallery/.*thumbnails/.* {
			expires 1y;
			add_header Cache-Control "public, immutable";
			access_log off;
		}

		# 原图：中长期缓存（30天）
		location ~* /gallery/.*\.(jpg|jpeg|png|webp)$ {
			expires 30d;
			add_header Cache-Control "public, immutable";
		}

		# GIF动画：中等缓存（7天）
		location ~* /gallery/.*\.gif$ {
			expires 7d;
			add_header Cache-Control "public, immutable";
		}

		# 视频文件：中长期缓存（30天），支持断点续传
		location ~* /gallery/.*\.(mp4|webm|mov)$ {
			expires 30d;
			add_header Cache-Control "public, immutable";

			# 支持断点续传（Range请求）
			add_header Accept-Ranges bytes;

			# MIME类型
			types {
				video/mp4 mp4;
				video/webm webm;
				video/quicktime mov;
			}

			# 视频文件不需要访问日志
			access_log off;
		}

		# 缓存状态响应头（用于监控）
		add_header X-Cache-Status $upstream_cache_status;
	}

	# 二创图片资源
	location /footprint/ {
		alias /home/yifeianyi/Desktop/xxm_fans_home/media/footprint/;
		autoindex off;
		expires 30d;
		add_header Cache-Control "public, immutable";
	}

	# 媒体文件 - CDN优化（支持视频）
	location /media/ {
		alias /home/yifeianyi/Desktop/xxm_fans_home/media/;
		expires 30d;
		add_header Cache-Control "public, immutable";

		# 缩略图：长期缓存（1年）
		location ~* /media/.*thumbnails/.* {
			expires 1y;
			add_header Cache-Control "public, immutable";
			access_log off;
		}

		# 原图：中长期缓存（30天）
		location ~* /media/.*\.(jpg|jpeg|png|webp)$ {
			expires 30d;
			add_header Cache-Control "public, immutable";
		}

		# GIF动画：中等缓存（7天）
		location ~* /media/.*\.gif$ {
			expires 7d;
			add_header Cache-Control "public, immutable";
		}

		# 视频文件：中长期缓存（30天），支持断点续传
		location ~* /media/.*\.(mp4|webm|mov)$ {
			expires 30d;
			add_header Cache-Control "public, immutable";

			# 支持断点续传（Range请求）
			add_header Accept-Ranges bytes;

			# MIME类型
			types {
				video/mp4 mp4;
				video/webm webm;
				video/quicktime mov;
			}

			# 视频文件不需要访问日志
			access_log off;
		}
	}
}

# 主 HTTPS 服务器 - 前端网站（仅 www 域名）- CDN优化版
server {
	listen 443 ssl http2;
	server_name www.xxm8777.cn;

	# SSL 配置 - 使用 Let's Encrypt 证书
	ssl_certificate /etc/letsencrypt/live/xxm8777.cn-0001/fullchain.pem;
	ssl_certificate_key /etc/letsencrypt/live/xxm8777.cn-0001/privkey.pem;
	include /etc/nginx/ssl-params.conf;

	# 安全头
	add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
	add_header X-Content-Type-Options nosniff always;
	add_header X-Frame-Options "SAMEORIGIN" always;
	add_header X-XSS-Protection "1; mode=block" always;

	root /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_frontend/dist;
	index index.html;
	client_max_body_size 3M;

	# 前端静态文件（支持 React Router）
	location / {
		try_files $uri $uri/ /index.html;
		expires 1h;
		add_header Cache-Control "public, must-revalidate";

		# Gzip 压缩配置
		gzip on;
		gzip_vary on;
		gzip_proxied any;
		gzip_comp_level 6;
		gzip_types text/plain text/css text/xml text/javascript application/json
		application/javascript application/xml+rss application/rss+xml font/truetype
		font/opentype application/vnd.ms-fontobject image/svg+xml;
	}

	# Django API
	location /api/ {
		proxy_pass http://127.0.0.1:8000;
		proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header X-Forwarded-Proto $scheme;

		# Cookie 和 Session 支持
		proxy_cookie_path / /;
		proxy_redirect off;

		# 超时配置
		proxy_connect_timeout 60s;
		proxy_send_timeout 60s;
		proxy_read_timeout 120s;

		# API不缓存
		add_header Cache-Control "no-cache, no-store, must-revalidate";
	}

	# Admin 访问限制（主站禁止访问 Admin）
	location /admin/ {
		return 403;
	}

	# SEO 文件 - 动态生成，转发到 Django
	location = /sitemap.xml {
		proxy_pass http://127.0.0.1:8000;
		proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header X-Forwarded-Proto $scheme;
	}

	location = /robots.txt {
		proxy_pass http://127.0.0.1:8000;
		proxy_set_header Host $host;
		proxy_set_header X-Real-IP $remote_addr;
		proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
		proxy_set_header X-Forwarded-Proto $scheme;
	}

	# 静态文件 - Django静态资源
	location /static/ {
		alias /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend/staticfiles/;
		expires 1y;
		add_header Cache-Control "public, immutable";
		access_log off;
	}

	# 封面图片
	location /covers/ {
		alias /home/yifeianyi/Desktop/xxm_fans_home/media/covers/;
		autoindex off;
		expires 30d;
		add_header Cache-Control "public, immutable";
	}

	# 图集图片 - CDN优化（支持视频和差异化缓存）
	location /gallery/ {
		alias /home/yifeianyi/Desktop/xxm_fans_home/media/gallery/;
		autoindex off;

		# 缩略图：长期缓存（1年）
		location ~* /gallery/.*thumbnails/.* {
			expires 1y;
			add_header Cache-Control "public, immutable";
			access_log off;
		}

		# 原图：中长期缓存（30天）
		location ~* /gallery/.*\.(jpg|jpeg|png|webp)$ {
			expires 30d;
			add_header Cache-Control "public, immutable";
		}

		# GIF动画：中等缓存（7天）
		location ~* /gallery/.*\.gif$ {
			expires 7d;
			add_header Cache-Control "public, immutable";
		}

		# 视频文件：中长期缓存（30天），支持断点续传
		location ~* /gallery/.*\.(mp4|webm|mov)$ {
			expires 30d;
			add_header Cache-Control "public, immutable";

			# 支持断点续传（Range请求）
			add_header Accept-Ranges bytes;

			# MIME类型
			types {
				video/mp4 mp4;
				video/webm webm;
				video/quicktime mov;
			}

			# 视频文件不需要访问日志
			access_log off;
		}

		# 缓存状态响应头（用于监控）
		add_header X-Cache-Status $upstream_cache_status;
	}

	# 二创图片资源
	location /footprint/ {
		alias /home/yifeianyi/Desktop/xxm_fans_home/media/footprint/;
		autoindex off;
		expires 30d;
		add_header Cache-Control "public, immutable";
	}

	# 媒体文件 - CDN优化（支持视频）
	location /media/ {
		alias /home/yifeianyi/Desktop/xxm_fans_home/media/;
		expires 30d;
		add_header Cache-Control "public, immutable";

		# 缩略图：长期缓存（1年）
		location ~* /media/.*thumbnails/.* {
			expires 1y;
			add_header Cache-Control "public, immutable";
			access_log off;
		}

		# 原图：中长期缓存（30天）
		location ~* /media/.*\.(jpg|jpeg|png|webp)$ {
			expires 30d;
			add_header Cache-Control "public, immutable";
		}

		# GIF动画：中等缓存（7天）
		location ~* /media/.*\.gif$ {
			expires 7d;
			add_header Cache-Control "public, immutable";
		}

		# 视频文件：中长期缓存（30天），支持断点续传
		location ~* /media/.*\.(mp4|webm|mov)$ {
			expires 30d;
			add_header Cache-Control "public, immutable";

			# 支持断点续传（Range请求）
			add_header Accept-Ranges bytes;

			# MIME类型
			types {
				video/mp4 mp4;
				video/webm webm;
				video/quicktime mov;
			}

			# 视频文件不需要访问日志
			access_log off;
		}
	}
}
```

### 4.3 配置说明

**CDN优化要点**:
1. **保持现有SSL配置**: 使用Let's Encrypt证书，无需更改
2. **视频文件支持**: 添加HTTP Range支持，支持断点续传和渐进式加载
3. **差异化缓存策略**: 缩略图1年、图片30天、GIF 7天、视频30天
4. **访问日志优化**: 缩略图和视频文件不记录访问日志，减少磁盘IO
5. **删除无效配置**: 移除GIF的Gzip压缩配置（GIF已经是压缩格式）

**配置差异说明**:
- Admin后台服务器块保持不变，直连源站，不走CDN
- 主站服务器块（www.xxm8777.cn）进行CDN优化
- 所有媒体资源路径支持视频文件
- 缓存策略更加精细
- 直接修改现有配置文件，不创建新文件

### 4.4 配置对比（现有 vs CDN优化）

| 配置项 | 现有配置 | CDN优化后 | 说明 |
|--------|----------|-----------|------|
| **SSL证书** | Let's Encrypt | 保持不变 | 无需更改 |
| **HTTP重定向** | 80→443 | 保持不变 | 无需更改 |
| **域名重定向** | xxm8777.cn→www | 保持不变 | 无需更改 |
| **Admin后台** | admin.xxm8777.cn | 保持不变 | 直连源站 |
| **图片缓存** | 统一30天 | 差异化 | 缩略图1年，图片30天 |
| **GIF缓存** | 30天 | 7天 | 缩短时间，节省流量 |
| **视频缓存** | 不支持 | 30天 | 新增视频支持 |
| **视频Range** | 不支持 | 支持 | 新增断点续传 |
| **API缓存** | 不缓存 | 不缓存 | 保持不变 |
| **访问日志** | 全部记录 | 优化记录 | 缩略图和视频不记录 |
| **GIF Gzip压缩** | 配置了 | 删除 | 无效配置，已移除 |
| **安全头** | HSTS等 | 保持不变 | 无需更改 |

**改动说明**:
1. 直接修改现有 `prod_xxm_home.conf` 文件
2. 保留所有SSL、重定向、Admin配置
3. 仅优化主站（www.xxm8777.cn）的静态资源缓存和视频支持

---

## 五、腾讯云CDN配置（国内）

### 5.1 基础配置

在腾讯云CDN控制台完成以下配置：

#### 5.1.1 添加加速域名

- **域名**: `www.xxm8777.cn`
- **业务类型**: 静态加速
- **源站类型**: 源站域名
- **回源域名**: `origin.xxm8777.cn`（必须配置DNS记录）
- **回源端口**: 443（HTTPS）
- **回源协议**: HTTPS（源站已配置SSL）
- **回源Host**: `www.xxm8777.cn`（与加速域名一致）

**优势**:
- 使用origin子域名回源，更换服务器时只需修改DNS
- 无需修改CDN配置
- 支持多服务器轮询（可选）

#### 5.1.2 域名备案确认

确保域名已备案（ICP备案），否则腾讯云CDN无法正常服务。

#### 5.1.3 HTTPS配置（已有SSL）

由于源站已配置Let's Encrypt SSL证书，CDN配置如下：

1. **回源协议**: HTTPS
2. **回源端口**: 443
3. **回源Host**: `www.xxm8777.cn`（保持一致，避免SSL证书问题）
4. **SNI开启**: 是（支持多域名SSL证书）

**优势**:
- 端到端HTTPS加密，安全性更高
- 无需在CDN端配置SSL证书
- 回源请求也加密，保护源站

### 5.2 缓存配置

在CDN控制台配置缓存规则：

| 规则类型 | 路径匹配 | 缓存时间 | 说明 |
|----------|----------|----------|------|
| **缩略图** | `*thumbnails*` | 365天 | WebP缩略图，长期缓存 |
| **原图** | `*.jpg`, `*.jpeg`, `*.png`, `*.webp` | 30天 | 普通图片 |
| **GIF** | `*.gif` | 7天 | GIF动画 |
| **视频** | `*.mp4`, `*.webm`, `*.mov` | 30天 | 短视频文件（5秒以内，平均5MB） |
| **静态文件** | `*.js`, `*.css` | 365天 | 前端静态资源 |
| **HTML** | `*.html` | 不缓存 | 动态生成页面 |
| **API** | `/api/*` | 不缓存 | API接口 |
| **Admin** | `/admin/*` | 不缓存 | 管理后台 |

**视频文件说明**:
- 当前图集包含87个短视频（MP4格式，平均5.14MB/个，总计447MB）
- 视频文件支持HTTP Range请求，可渐进式加载
- 缓存时间设置为30天，平衡性能与更新需求

### 5.3 安全防护配置

#### 5.3.1 用量封顶（最重要）

**配置位置**: CDN控制台 → 域名管理 → 访问控制 → 用量封顶

**配置参数**:
- **封顶类型**: 流量封顶
- **封顶阈值**: 200GB/月（可根据实际情况调整）
- **解封方式**: 24小时后自动解封
- **告警阈值**: 160GB（阈值的80%）

**成本估算**:
- 200GB × 0.21元/GB = 42元/月（腾讯云CDN价格）
- 即使被攻击，最大损失锁定在42元

#### 5.3.2 Referer防盗链

**配置位置**: CDN控制台 → 域名管理 → 访问控制 → Referer防盗链

**配置参数**:
- **防盗链类型**: 白名单
- **Referer白名单**: `*.xxm8777.cn`
- **允许空Referer**: 是（避免部分浏览器无法访问）

**作用**: 防止其他网站直接盗用图片资源。

#### 5.3.3 IP访问限频

**配置位置**: CDN控制台 → 域名管理 → 访问控制 → IP访问限频

**差异化配置**:

| 路径 | 单IP访问频率 | 说明 |
|------|-------------|------|
| `*thumbnails*` | 100次/分钟 | 缩略图，限制宽松 |
| `*.gif` | 10次/分钟 | GIF动画，限制严格 |
| `*.mp4`, `*.webm`, `*.mov` | 5次/分钟 | 视频文件，最严格限制 |
| 其他图片 | 50次/分钟 | 原图，中等限制 |

**作用**: 限制单个IP的请求频率，防止自动化脚本刷量。视频文件因为体积较大（平均5MB），设置最严格的限频。

#### 5.3.4 用量告警

**配置位置**: CDN控制台 → 域名管理 → 访问控制 → 用量告警

**告警规则**:
- **告警类型**: 流量告警
- **告警阈值**: 160GB（封顶的80%）
- **告警方式**: 短信 + 邮件
- **告警频率**: 每天最多1次

---

## 六、Cloudflare配置（国外）

### 6.1 DNS配置

在Cloudflare控制台完成以下配置：

#### 6.1.1 添加站点

1. 登录Cloudflare控制台
2. 添加站点 `xxm8777.cn`
3. Cloudflare会自动扫描现有DNS记录

#### 6.1.2 配置DNS记录

参考第三章的DNS配置方案。

### 6.2 CDN配置

#### 6.2.1 Cloudflare CDN说明

本方案中Cloudflare仅作为DNS服务提供商，不使用其CDN功能。

**原因**:
- `www`记录已配置为CNAME指向腾讯云CDN
- Cloudflare的CDN功能与腾讯云CDN冲突
- 国外用户直接访问源站，延迟可接受

**国外用户访问路径**:
- 国外用户 → Cloudflare DNS解析 → 源站服务器（443端口）
- 无需CDN加速，直连源站即可

### 6.3 安全配置

#### 6.3.1 防火墙规则

在Cloudflare防火墙中配置：

1. **开启基本DDoS防护**: 免费版已包含
2. **配置访问规则**: 阻止已知的恶意IP
3. **开启Bot管理**: 过滤恶意爬虫（免费版有限制）

#### 6.3.2 速率限制

在Cloudflare速率限制中配置：

- **规则名称**: API限流
- **匹配条件**: 请求路径 `/api/*`
- **限制**: 100次/分钟
- **动作**: 挑战（CAPTCHA）

#### 6.3.3 安全级别

设置为**中等**（Medium），平衡安全性和用户体验。

### 6.4 性能优化

1. **开启自动HTTPS重写**: 自动将HTTP链接转换为HTTPS
2. **开启Brotli压缩**: 提升传输效率
3. **开启HTTP/3 (QUIC)**: 提升连接性能
4. **开启0-RTT连接恢复**: 加速重复连接

---

## 七、前后端配置调整

### 7.1 前端配置

#### 7.1.1 环境变量配置

修改 `env/frontend.env`:

```bash
# API配置（保持相对路径，使用CDN域名）
VITE_API_BASE_URL=/api

# CDN资源域名（可选，用于明确指定CDN域名）
# 如果不配置，默认使用当前域名
VITE_CDN_DOMAIN=https://www.xxm8777.cn
```

#### 7.1.2 图片URL配置

前端代码中的图片URL需要确保：

1. **使用相对路径**: `/media/xxx.jpg`（推荐）
2. **或使用CDN域名**: `https://www.xxm8777.cn/media/xxx.jpg`

**示例**:
```typescript
// 不推荐：硬编码源站
const imageUrl = 'http://origin.xxm8777.cn/media/xxx.jpg';

// 推荐：使用相对路径
const imageUrl = '/media/xxx.jpg';

// 或使用CDN域名
const imageUrl = 'https://www.xxm8777.cn/media/xxx.jpg';
```

### 7.2 后端配置

#### 7.2.1 Django ALLOWED_HOSTS

修改 `env/backend.env`:

```bash
DJANGO_ALLOWED_HOSTS=origin.xxm8777.cn,admin.xxm8777.cn,www.xxm8777.cn,xxm8777.cn
```

#### 7.2.2 Django CORS配置

如果需要跨域请求（一般不需要），在 `xxm_fans_home/settings.py` 中配置：

```python
CORS_ALLOWED_ORIGINS = [
    'https://www.xxm8777.cn',
    'https://xxm8777.cn',
]
```

#### 7.2.3 静态文件URL配置

确保 `MEDIA_URL` 和 `STATIC_URL` 配置正确：

```python
# settings.py
MEDIA_URL = '/media/'
STATIC_URL = '/static/'
```

---

## 八、监控与告警

### 8.1 腾讯云CDN监控

#### 8.1.1 实时监控

在腾讯云CDN控制台查看：
- **带宽使用**: 实时带宽曲线
- **流量消耗**: 实时流量统计
- **请求数**: QPS统计
- **命中率**: 缓存命中率（目标>90%）

#### 8.1.2 告警配置

配置以下告警：
1. **流量告警**: 流量超过160GB时发送短信/邮件
2. **带宽告警**: 带宽异常飙升时告警
3. **错误率告警**: 5xx错误率超过1%时告警

### 8.2 Cloudflare监控

在Cloudflare控制台查看：
- **分析仪表板**: 流量、请求、威胁统计
- **安全性**: DDoS攻击、恶意请求统计
- **性能**: 响应时间、缓存命中率

### 8.3 源站监控

#### 8.3.1 Nginx日志分析

定期分析Nginx访问日志：
```bash
# 查看CDN回源请求
grep 'cdn' /tmp/nginx/access.log | awk '{print $1}' | sort | uniq -c | sort -rn

# 查看回源流量统计
awk '{sum+=$10} END {print "Total bytes:", sum}' /tmp/nginx/access.log
```

#### 8.3.2 服务器资源监控

监控以下指标：
- **CPU使用率**: 正常应<50%
- **内存使用率**: 正常应<80%
- **磁盘IO**: 关注磁盘读写性能
- **网络带宽**: 关注入站/出站流量

---

## 九、实施步骤

### 9.1 准备阶段（Day 0）

#### 步骤1: 域名备案确认
- [ ] 确认域名已完成ICP备案
- [ ] 记录备案号

#### 步骤2: DNS提供商准备
- [ ] 注册Cloudflare账号（如果还没有）
- [ ] 将域名DNS服务器修改为Cloudflare的NS服务器

#### 步骤3: 腾讯云CDN准备
- [ ] 注册腾讯云账号
- [ ] 完成实名认证
- [ ] 开通CDN服务

#### 步骤4: 源站服务器准备
- [ ] 确认源站服务器公网IP
- [ ] 确认Nginx运行正常（端口443 HTTPS）
- [ ] 确认Django服务运行正常（端口8000）
- [ ] 确认SSL证书正常（Let's Encrypt）

### 9.2 配置阶段（Day 1）

#### 步骤5: DNS配置
- [ ] 在Cloudflare添加DNS记录（origin, admin, www）
- [ ] 确认DNS解析生效

#### 步骤6: 源站Nginx配置
- [ ] 备份现有配置文件: `cp /etc/nginx/sites-available/prod_xxm_home.conf /etc/nginx/sites-available/prod_xxm_home.conf.backup`
- [ ] 直接编辑现有配置文件，添加CDN优化配置
- [ ] 测试配置: `nginx -t`
- [ ] 重启Nginx服务: `systemctl restart nginx`

#### 步骤7: 腾讯云CDN配置
- [ ] 添加加速域名 `www.xxm8777.cn`
- [ ] 配置回源信息
- [ ] 配置缓存规则
- [ ] 配置安全防护（用量封顶、防盗链、IP限频、告警）
- [ ] 提交审核

#### 步骤8: 域名解析切换
- [ ] 等待腾讯云CDN审核通过
- [ ] 获取腾讯云CDN提供的CNAME记录
- [ ] 在Cloudflare中更新`www`记录的CNAME

### 9.3 测试阶段（Day 2）

#### 步骤9: 功能测试
- [ ] 测试前台页面访问: `https://www.xxm8777.cn`
- [ ] 测试HTTPS正常工作，检查SSL证书
- [ ] 测试图片加载: 缩略图、原图、GIF
- [ ] 测试视频加载: MP4视频文件，验证断点续传功能
- [ ] 测试API接口: `https://www.xxm8777.cn/api/songs/`等
- [ ] 测试管理后台: `https://admin.xxm8777.cn/admin/`（直连源站，不走CDN）
- [ ] 测试HTTP到HTTPS自动重定向

#### 步骤10: 性能测试
- [ ] 使用国内IP测试访问速度
- [ ] 使用国外IP测试访问速度
- [ ] 检查CDN缓存命中率（目标>90%）

#### 步骤11: 安全测试
- [ ] 测试防盗链功能
- [ ] 测试IP限频功能
- [ ] 模拟异常流量，验证用量封顶

### 9.4 上线阶段（Day 3）

#### 步骤12: 监控部署
- [ ] 确认CDN监控告警正常工作
- [ ] 确认源站Nginx日志正常记录
- [ ] 配置定期日志分析脚本

#### 步骤13: 文档归档
- [ ] 记录所有配置信息
- [ ] 保存CDN控制台截图
- [ ] 编写运维手册

#### 步骤14: 正式上线
- [ ] 通知相关方CDN已上线
- [ ] 密切监控24小时
- [ ] 根据监控数据调整配置

---

## 十、成本预估

### 10.1 腾讯云CDN成本

#### 10.1.1 正常访问场景

**假设条件**:
- 日活用户: 100人
- 每人浏览: 30张缩略图 + 2张原图
- 缩略图大小: 15KB
- 原图大小: 150KB
- GIF访问量: 忽略（点击放大才加载）
- 视频访问量: 假设每人平均查看1个短视频（5.14MB/个）

**月流量计算**:
```
每日流量 = 100人 × (30张 × 15KB + 2张 × 150KB + 1个视频 × 5.14MB)
         = 100 × (450KB + 300KB + 5.14MB)
         = 100 × (0.45MB + 0.3MB + 5.14MB)
         = 100 × 5.89MB
         = 589MB/天

月流量 = 589MB × 30天 = 17.67GB/月
```

**月费用**:
- 腾讯云CDN价格: 0.21元/GB（流量计费）
- 费用: 17.67GB × 0.21元/GB = **3.71元/月**

**说明**: 视频文件占流量消耗的主要部分（约87%），建议后续考虑为视频添加缩略图封面，只在用户点击时才加载视频。

#### 10.1.2 高峰访问场景（视频发布后）

**假设条件**:
- 日活用户: 400人
- 持续时间: 3天
- 每人浏览: 100张缩略图 + 20张原图 + 20张GIF + 5个视频
- GIF大小: 2.5MB
- 视频大小: 5.14MB（平均）

**3天流量计算**:
```
每日流量 = 400人 × (100张 × 15KB + 20张 × 150KB + 20张 × 2.5MB + 5个 × 5.14MB)
         = 400 × (1.5MB + 3MB + 50MB + 25.7MB)
         = 400 × 80.2MB
         = 32.08GB/天

3天总流量 = 32.08GB × 3天 = 96.24GB
```

**费用**:
- 费用: 96.24GB × 0.21元/GB = **20.21元**

**说明**: 高峰期视频流量占比约32%，建议在高峰期适当提高流量封顶阈值（如300GB），以确保服务不中断。

#### 10.1.3 成本上限

**流量封顶**: 200GB/月
- **最大月费用**: 200GB × 0.21元/GB = **42元/月**

**结论**: 即使被攻击，最大损失锁定在42元。

### 10.2 Cloudflare成本

- **DNS服务**: 免费
- **CDN服务**: 免费版（无限流量）
- **DDoS防护**: 免费
- **SSL证书**: 免费（Let's Encrypt，已配置）

**总成本**: 0元/月

**说明**: 源站已配置Let's Encrypt SSL证书，无需额外SSL成本。

### 10.3 总成本预估

| 场景 | 腾讯云CDN | Cloudflare | 总计 |
|------|-----------|------------|------|
| **平时** | 3.71元/月 | 0元/月 | 3.71元/月 |
| **高峰期** | 20.21元/月 | 0元/月 | 20.21元/月 |
| **成本上限**（200GB） | 42元/月 | 0元/月 | 42元/月 |

**结论**:
- 月度成本控制在4-5元（平时），高峰期约20元
- 建议高峰期将流量封顶调整为300GB（约63元），以应对视频流量增长
- 视频文件是主要流量消耗源（约占80%+），后续优化方向：
  1. 为视频添加缩略图封面，减少误加载
  2. 考虑视频压缩优化（降低码率）
  3. 使用视频懒加载技术

---

## 十一、风险控制

### 11.1 风险识别

| 风险 | 可能性 | 影响程度 | 防护措施 |
|------|--------|----------|----------|
| **恶意刷流量** | 中 | 高 | 用量封顶、IP限频、防盗链 |
| **CDN故障** | 低 | 高 | 源站直连备用方案 |
| **DNS劫持** | 低 | 中 | 使用Cloudflare DNS（防劫持） |
| **SSL证书过期** | 低 | 中 | 自动续期、告警提醒 |
| **配置错误** | 中 | 中 | 充分测试、逐步上线 |

### 11.2 应急预案

#### 11.2.1 CDN停服场景

**触发条件**: 流量达到封顶阈值，CDN自动停服

**应急步骤**:
1. **检查流量来源**: 登录CDN控制台查看TOP IP和Referer
2. **确认是否攻击**: 判断是正常高峰还是恶意攻击
3. **选择处理方案**:
   - **如果是恶意攻击**:
     - 保持CDN停服状态
     - 分析攻击IP，在CDN黑名单中添加
     - 24小时后CDN自动恢复
   - **如果是正常高峰**:
     - 提高封顶阈值
     - 等待CDN自动恢复（或手动恢复）

#### 11.2.2 DNS故障场景

**应急步骤**:
1. **确认故障范围**: 使用`nslookup`或`dig`检查DNS解析
2. **临时DNS方案**: 如果Cloudflare DNS故障，可临时切换到其他DNS提供商（如阿里云DNS）
3. **恢复DNS**: Cloudflare恢复后切换回来

#### 11.2.3 源站故障场景

**应急步骤**:
1. **确认源站状态**: 检查服务器CPU、内存、磁盘、网络
2. **快速恢复**:
   - 如果Nginx故障: 重启Nginx服务
   - 如果Django故障: 重启Django服务
   - 如果服务器过载: 升级服务器配置
3. **CDN缓存**: CDN的边缘缓存仍可提供部分服务（缓存命中）

### 11.3 备份方案

#### 11.3.1 数据备份

- **数据库**: 每日自动备份到`data/backups/`
- **媒体文件**: 定期备份到云存储（可选）

#### 11.3.2 配置备份

- **Nginx配置**: 版本控制（Git）
- **DNS配置**: Cloudflare配置导出
- **CDN配置**: 腾讯云配置记录（截图+文档）

---

## 十二、优化建议

### 12.1 短期优化（1个月内）

1. **缓存命中率优化**:
   - 分析CDN日志，找出未命中的原因
   - 调整缓存规则，提高命中率
   - 目标: 命中率>90%

2. **访问速度优化**:
   - 开启HTTP/2和HTTP/3
   - 优化图片压缩（WebP格式）
   - 启用Gzip/Brotli压缩

3. **成本优化**:
   - 监控流量消耗，调整封顶阈值
   - 购买流量包（如果有折扣）
   - 分析热点资源，优化加载策略

4. **视频文件优化**（重要）:
   - **添加视频缩略图封面**: 为每个视频生成首帧缩略图，只在用户点击时才加载视频
   - **视频压缩优化**: 使用FFmpeg重新压缩视频，降低码率（目标: 平均2-3MB/个）
   - **实现视频懒加载**: 前端使用Intersection Observer API，只在视频进入视口时才加载
   - **视频预加载策略**: 对热门视频开启预加载，对冷门视频不预加载

### 12.2 中期优化（3个月内）

1. **全球加速优化**:
   - 测试不同CDN组合（阿里云、华为云等）
   - 使用APM工具监控全球访问质量
   - 优化DNS智能解析规则

2. **安全防护升级**:
   - 启用CDN的WAF功能（高级版）
   - 配置更精细的访问控制规则
   - 定期安全审计

3. **性能监控升级**:
   - 接入APM工具（如New Relic、Datadog）
   - 建立性能基线
   - 自动化性能告警

### 12.3 长期优化（6个月内）

1. **架构升级**:
   - 评估是否需要对象存储（OSS）
   - 评估是否需要CDN预热功能
   - 评估是否需要多源站负载均衡

2. **智能化运营**:
   - 使用AI预测流量高峰
   - 自动化资源调度
   - 智能缓存策略

---

## 十三、运维手册

### 13.1 日常运维

#### 每日
- [ ] 检查CDN监控面板，查看流量和带宽
- [ ] 检查源站服务器资源使用情况
- [ ] 查看CDN告警信息

#### 每周
- [ ] 分析CDN日志，查看缓存命中率
- [ ] 检查DNS解析是否正常
- [ ] 备份关键配置

#### 每月
- [ ] 查看CDN账单，确认费用
- [ ] 评估是否需要调整流量封顶阈值
- [ ] 总结本月运行情况

### 13.2 常见问题处理

#### 问题1: 图片加载缓慢

**排查步骤**:
1. 检查CDN缓存命中率
2. 检查源站响应时间
3. 检查网络带宽

**解决方案**:
- 优化源站Nginx配置
- 调整CDN缓存规则
- 升级源站带宽

#### 问题2: CDN回源失败

**排查步骤**:
1. 检查源站Nginx是否正常运行
2. 检查源站防火墙规则
3. 检查回源域名解析

**解决方案**:
- 重启Nginx服务
- 检查安全组配置
- 验证DNS解析

#### 问题3: 防盗链导致正常用户无法访问

**排查步骤**:
1. 检查防盗链白名单配置
2. 检查用户浏览器Referer

**解决方案**:
- 允许空Referer
- 更新白名单规则

### 13.3 命令速查

```bash
# 检查Nginx配置
nginx -t

# 重启Nginx
systemctl restart nginx

# 查看CDN回源请求（通过User-Agent识别）
grep 'cdn' /var/log/nginx/access.log | awk '{print $1}' | sort | uniq -c

# 查看回源流量
awk '{sum+=$10} END {print sum/1024/1024 " MB"}' /var/log/nginx/access.log

# 测试DNS解析
nslookup www.xxm8777.cn

# 测试CDN节点响应
curl -I https://www.xxm8777.cn/media/test.jpg

# 测试origin子域名解析
nslookup origin.xxm8777.cn
```

---

## 十四、总结

### 14.1 方案优势

1. **成本低廉**: 月度成本控制在25元以内（平时4-5元，高峰期20元）
2. **安全可靠**: 多层防护，最大损失锁定在42元（200GB封顶）
3. **性能优异**: 国内用户访问速度提升3-10倍
4. **易于维护**: 使用origin子域名回源，更换服务器方便
5. **配置简单**: 直接修改现有配置文件，无需创建新文件

### 14.2 关键成功因素

1. **严格的用量封顶**: 确保成本可控
2. **完善的防盗链**: 防止资源被盗用
3. **合理的缓存策略**: 提高缓存命中率
4. **及时的监控告警**: 快速响应异常
5. **充分的测试验证**: 确保上线平稳
6. **origin子域名回源**: 便于后续更换服务器

### 14.3 后续优化方向

1. 考虑引入对象存储，进一步提升性能
2. 探索更多CDN服务商，优化成本
3. **视频文件专项优化**:
   - 实现视频缩略图封面系统，减少视频误加载
   - 使用视频压缩技术，降低视频文件体积（目标降低50%）
   - 探索使用视频CDN专用服务（如阿里云视频点播）
   - 实现视频自适应码率，根据用户网络环境自动选择
4. 使用APM工具，提升监控能力
5. 优化图片加载策略，减少流量消耗

---

## 附录

### A. 参考文档

- [腾讯云CDN文档](https://cloud.tencent.com/document/product/228)
- [Cloudflare文档](https://developers.cloudflare.com/)
- [Nginx文档](https://nginx.org/en/docs/)
- [Django部署文档](https://docs.djangoproject.com/en/5.2/howto/deployment/)

### A.1 视频文件技术细节

**当前视频文件统计**: 87个MP4文件，总计447MB，平均5.14MB/个，时长5秒以内

**CDN配置要点**:
1. **HTTP Range支持**: 必须启用`Accept-Ranges: bytes`
2. **MIME类型正确配置**: 确保Nginx正确识别视频文件类型
3. **缓存策略**: 30天缓存，平衡性能与更新需求
4. **限频控制**: 5次/分钟，防止恶意刷流量

**视频优化建议**:

1. **生成视频缩略图封面**:
   ```bash
   # 使用FFmpeg生成视频第一帧作为缩略图
   ffmpeg -i input.mp4 -ss 00:00:00 -vframes 1 output_thumbnail.jpg
   ```

2. **视频压缩优化**:
   ```bash
   # 降低视频码率，减少文件体积（目标: 2-3MB）
   ffmpeg -i input.mp4 -b:v 500k -b:a 64k -c:v libx264 -c:a aac output_compressed.mp4
   ```

3. **视频格式转换**:
   ```bash
   # 转换为WebM格式（更小的文件体积，更好的浏览器支持）
   ffmpeg -i input.mp4 -c:v libvpx -b:v 500k -c:a libvorbis output.webm
   ```

4. **前端视频懒加载**:
   ```javascript
   // 使用Intersection Observer API实现视频懒加载
   const videoObserver = new IntersectionObserver((entries) => {
     entries.forEach(entry => {
       if (entry.isIntersecting) {
         const video = entry.target;
         video.src = video.dataset.src;
         video.load();
         videoObserver.unobserve(video);
       }
     });
   });
   ```

5. **视频预加载策略**:
   - 对热门视频（访问量前20%）: 设置`preload="metadata"`
   - 对普通视频: 设置`preload="none"`
   - 对冷门视频（访问量后30%）: 不加载，只在用户点击时加载

### B. 联系方式

- **技术支持**: 腾讯云工单系统、Cloudflare社区论坛
- **应急联系**: [填写你的联系方式]

### C. 变更记录

| 版本 | 日期 | 修改内容 | 修改人 |
|------|------|----------|--------|
| v1.0 | 2026-02-02 | 初始版本 | iFlow CLI |
| v1.1 | 2026-02-02 | 添加视频文件支持（87个MP4文件，447MB） | iFlow CLI |
| v1.2 | 2026-02-02 | 基于实际线上配置（prod_xxm_home.conf）优化方案 | iFlow CLI |
| v1.3 | 2026-02-02 | 修复逻辑矛盾和冗余内容 | iFlow CLI |
| | | - 统一端口配置为443（HTTPS） | |
| | | - 明确回源方案：使用origin.xxm8777.cn子域名 | |
| | | - 重新定位方案：腾讯云CDN + Cloudflare DNS | |
| | | - 明确Nginx修改方案：直接修改现有配置文件 | |
| | | - 删除GIF的Gzip压缩配置（无效） | |
| | | - 修正成本描述：25元以内 | |
| | | - 删除重复内容，简化文档结构 | |
| | | - 分离admin和主站的HTTP重定向（独立server块） | |
| | | - 添加origin.xxm8777.cn的完整配置（HTTP + HTTPS） | |
| | | - 优化Nginx配置结构，提高可维护性 | |

---

**文档结束**