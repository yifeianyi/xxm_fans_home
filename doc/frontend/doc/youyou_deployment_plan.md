# YouYou SongList 部署方案

## 项目结构分析

1. 主项目(xxmfans)运行在3000端口，域名为xxm8777.cn
2. 新项目(youyou_SongList)需要部署到youyou.xxm8777.cn子域名
3. youyou_SongList包含：
   - Django后端API (通过`/api/youyou/`访问)
   - Vue.js前端应用 (构建后的静态文件)

## Nginx配置方案

### 1. 前提条件

- 确保主项目(xxmfans)已经在运行，并监听3000端口
- 确保youyou_SongList的Django应用已正确集成到主项目中
- 确保youyou_SongList前端已构建完成(通过`npm run build`)

### 2. Nginx配置文件

创建Nginx配置文件 `/etc/nginx/sites-available/youyou.xxm8777.cn`:

```nginx
server {
    listen 80;
    server_name youyou.xxm8777.cn;

    # 重定向所有HTTP请求到HTTPS
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl http2;
    server_name youyou.xxm8777.cn;

    # SSL证书配置(需要替换为实际路径)
    ssl_certificate /path/to/your/certificate.crt;
    ssl_certificate_key /path/to/your/private.key;

    # SSL配置
    ssl_protocols TLSv1.2 TLSv1.3;
    ssl_ciphers ECDHE-RSA-AES256-GCM-SHA512:DHE-RSA-AES256-GCM-SHA512:ECDHE-RSA-AES256-GCM-SHA384:DHE-RSA-AES256-GCM-SHA384;
    ssl_prefer_server_ciphers off;

    # 静态文件服务
    location / {
        root /path/to/xxm_fans_home/youyou_SongList_frontend/dist;
        try_files $uri $uri/ /index.html;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # YouYou特定的图片文件
    location /photos/ {
        alias /home/yifeianyi/Desktop/xxm_fans_home/youyou_SongList_frontend/photos/;
    }
}
```

### 3. 启用配置

```bash
# 创建软链接启用站点
sudo ln -s /etc/nginx/sites-available/youyou.xxm8777.cn /etc/nginx/sites-enabled/

# 测试Nginx配置
sudo nginx -t

# 重新加载Nginx
sudo systemctl reload nginx
```

## 部署步骤

### 1. 构建前端应用

```bash
cd /path/to/xxm_fans_home/youyou_SongList_frontend
npm run build
```

### 2. 配置Django静态文件

确保在Django设置中正确配置了静态文件收集:

```python
# settings.py
STATIC_URL = 'static/'
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_DIRS = [
    BASE_DIR / "static",
]
```

然后运行:

```bash
python manage.py collectstatic
```

### 3. 配置域名解析

在DNS服务商处添加A记录:
- 记录类型: A
- 主机记录: youyou
- 记录值: 服务器IP地址

### 4. SSL证书配置

可以使用Let's Encrypt免费获取SSL证书:

```bash
# 安装certbot
sudo apt install certbot python3-certbot-nginx

# 获取证书
sudo certbot --nginx -d youyou.xxm8777.cn
```

## 注意事项

1. 确保服务器防火墙允许80和443端口
2. 确保Django应用在生产环境中正确配置了ALLOWED_HOSTS
3. 确保所有文件路径在配置中正确设置
4. 定期更新SSL证书
5. 监控应用日志以排查问题