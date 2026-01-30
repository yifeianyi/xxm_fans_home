# 乐游歌单云端部署指南

本文档详细介绍如何将乐游歌单（leyou.xxm8777.cn）部署到云端服务器。

---

## 目录

1. [准备工作](#准备工作)
2. [服务器环境配置](#服务器环境配置)
3. [后端部署](#后端部署)
4. [前端构建](#前端构建)
5. [Nginx 配置](#nginx-配置)
6. [SSL 证书申请](#ssl-证书申请)
7. [域名解析](#域名解析)
8. [服务启动](#服务启动)
9. [常见问题](#常见问题)
10. [维护和更新](#维护和更新)

---

## 准备工作

### 1. 服务器要求

- **操作系统**: Ubuntu 20.04+ 或 CentOS 7+
- **Python**: 3.8+
- **Node.js**: 18+
- **Nginx**: 1.18+
- **内存**: 最低 1GB，推荐 2GB+
- **存储**: 最低 10GB，推荐 20GB+

### 2. 域名准备

- 确保已拥有域名 `xxm8777.cn`
- 子域名 `leyou.xxm8777.cn` 已在域名服务商处配置 DNS 解析

### 3. 代码部署

将项目代码上传到服务器：

```bash
# 使用 scp 上传代码（从本地）
scp -r /home/yifeianyi/Desktop/xxm_fans_home user@your-server:/home/user/

# 或者使用 git clone（如果代码在 Git 仓库）
git clone git@github.com:yifeianyi/xxm_fans_home.git
```

---

## 服务器环境配置

### 1. 安装 Python 和 pip

```bash
# Ubuntu/Debian
sudo apt update
sudo apt install python3 python3-pip python3-venv

# CentOS/RHEL
sudo yum install python3 python3-pip
```

### 2. 安装 Node.js

```bash
# 使用 NodeSource 仓库安装 Node.js 18
curl -fsSL https://deb.nodesource.com/setup_18.x | sudo -E bash -
sudo apt install -y nodejs

# 验证安装
node --version  # 应该显示 v18.x.x
npm --version   # 应该显示 9.x.x 或更高
```

### 3. 安装 Nginx

```bash
# Ubuntu/Debian
sudo apt install nginx

# CentOS/RHEL
sudo yum install nginx

# 启动 Nginx
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 4. 安装 Certbot（用于 SSL 证书）

```bash
# Ubuntu/Debian
sudo apt install certbot python3-certbot-nginx

# CentOS/RHEL
sudo yum install certbot python3-certbot-nginx
```

---

## 后端部署

### 1. 创建虚拟环境

```bash
cd /home/user/xxm_fans_home/repo/xxm_fans_backend
python3 -m venv venv
source venv/bin/activate
```

### 2. 安装 Python 依赖

```bash
pip install -r requirements.txt
```

### 3. 配置环境变量

```bash
# 复制环境变量配置文件
cp env/backend.env .env

# 编辑 .env 文件，配置数据库等
nano .env
```

关键配置项：

```env
DEBUG=False
SECRET_KEY=your-very-secret-key-here
ALLOWED_HOSTS=leyou.xxm8777.cn,www.xxm8777.cn
DATABASE_URL=sqlite:///data/db.sqlite3
```

### 4. 数据库迁移

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. 收集静态文件

```bash
python manage.py collectstatic --noinput
```

### 6. 创建超级用户（可选）

```bash
python manage.py createsuperuser
```

### 7. 使用 Gunicorn 运行

```bash
# 安装 Gunicorn
pip install gunicorn

# 启动后端服务
gunicorn xxm_fans_home.wsgi:application \
  --bind 127.0.0.1:8000 \
  --workers 3 \
  --timeout 120 \
  --access-logfile logs/access.log \
  --error-logfile logs/error.log
```

### 8. 使用 systemd 管理服务

创建 systemd 服务文件：

```bash
sudo nano /etc/systemd/system/xxm-backend.service
```

内容如下：

```ini
[Unit]
Description=XXM Fans Home Backend
After=network.target

[Service]
Type=notify
User=your-username
Group=www-data
WorkingDirectory=/home/user/xxm_fans_home/repo/xxm_fans_backend
Environment="PATH=/home/user/xxm_fans_home/repo/xxm_fans_backend/venv/bin"
ExecStart=/home/user/xxm_fans_home/repo/xxm_fans_backend/venv/bin/gunicorn xxm_fans_home.wsgi:application --bind 127.0.0.1:8000 --workers 3 --timeout 120
Restart=always

[Install]
WantedBy=multi-user.target
```

启动服务：

```bash
sudo systemctl daemon-reload
sudo systemctl start xxm-backend
sudo systemctl enable xxm-backend
sudo systemctl status xxm-backend
```

---

## 前端构建

### 1. 安装依赖

```bash
cd /home/user/xxm_fans_home/repo/Temp_frontend
npm install
```

### 2. 配置环境变量

编辑 `.env` 文件：

```bash
nano .env
```

配置内容：

```env
# 域名到歌手的映射配置
localhost=youyou
127.0.0.1=youyou
leyou.xxm8777.cn=youyou

# 默认值（当域名不匹配时使用）
DEFAULT_ARTIST=youyou
```

### 3. 生产构建

```bash
npm run build
```

构建完成后，静态文件会生成在 `dist/` 目录中。

---

## Nginx 配置

### 1. 复制配置文件

```bash
# 复制配置文件到 Nginx 配置目录
sudo cp /home/user/xxm_fans_home/infra/nginx/youyou-songlist.conf /etc/nginx/sites-available/youyou-songlist.conf

# 创建软链接启用配置
sudo ln -s /etc/nginx/sites-available/youyou-songlist.conf /etc/nginx/sites-enabled/
```

### 2. 检查配置文件

```bash
sudo nginx -t
```

如果显示 `syntax is ok` 和 `test is successful`，说明配置正确。

### 3. 重载 Nginx

```bash
sudo systemctl reload nginx
```

### 4. 验证 HTTP 访问

在浏览器中访问 `http://leyou.xxm8777.cn`，应该能看到乐游歌单页面。

---

## SSL 证书申请

### 1. 使用 Certbot 申请证书

```bash
sudo certbot --nginx -d leyou.xxm8777.cn
```

按提示操作：
- 输入邮箱地址
- 同意服务条款
- 选择是否共享邮箱
- 选择是否将 HTTP 流量重定向到 HTTPS

### 2. 启用 HTTPS 配置

证书申请成功后，编辑 Nginx 配置文件：

```bash
sudo nano /etc/nginx/sites-available/youyou-songlist.conf
```

取消注释 HTTPS 部分的配置（删除 `#` 注释符号）：

```nginx
# server {
#     listen 443 ssl http2;
#     ...
# }
```

改为：

```nginx
server {
    listen 443 ssl http2;
    ...
}
```

### 3. 重载 Nginx

```bash
sudo nginx -t
sudo systemctl reload nginx
```

### 4. 验证 HTTPS 访问

在浏览器中访问 `https://leyou.xxm8777.cn`，应该能看到安全连接的乐游歌单页面。

---

## 域名解析

### 1. 添加 A 记录

在域名服务商（如阿里云、腾讯云）的 DNS 管理中添加：

| 类型 | 主机记录 | 记录值 | TTL |
|------|----------|--------|-----|
| A    | leyou    | 服务器IP地址 | 600 |

### 2. 验证解析

```bash
# 在本地终端执行
ping leyou.xxm8777.cn

# 或使用 nslookup
nslookup leyou.xxm8777.cn
```

---

## 服务启动

### 1. 启动后端服务

```bash
sudo systemctl start xxm-backend
sudo systemctl enable xxm-backend
```

### 2. 启动 Nginx

```bash
sudo systemctl start nginx
sudo systemctl enable nginx
```

### 3. 检查服务状态

```bash
# 检查后端
sudo systemctl status xxm-backend

# 检查 Nginx
sudo systemctl status nginx

# 检查端口监听
sudo netstat -tlnp | grep -E '80|443|8000'
```

### 4. 查看日志

```bash
# 后端日志
sudo journalctl -u xxm-backend -f

# Nginx 访问日志
sudo tail -f /var/log/nginx/access.log

# Nginx 错误日志
sudo tail -f /var/log/nginx/error.log
```

---

## 常见问题

### 1. 端口被占用

```bash
# 查找占用端口的进程
sudo lsof -i :8000

# 杀死进程
sudo kill -9 PID
```

### 2. 权限问题

```bash
# 修改文件所有者
sudo chown -R your-username:www-data /home/user/xxm_fans_home

# 修改文件权限
sudo chmod -R 755 /home/user/xxm_fans_home
```

### 3. 数据库迁移失败

```bash
# 删除迁移文件（保留 __init__.py）
find . -path "*/migrations/*.py" -not -name "__init__.py" -delete

# 重新迁移
python manage.py makemigrations
python manage.py migrate
```

### 4. 静态文件无法加载

```bash
# 重新收集静态文件
python manage.py collectstatic --noinput

# 检查 Nginx 配置中的静态文件路径
sudo nginx -t
```

### 5. SSL 证书续期失败

```bash
# 手动续期
sudo certbot renew --dry-run

# 查看续期日志
sudo journalctl -u certbot.timer
```

---

## 维护和更新

### 1. 更新代码

```bash
cd /home/user/xxm_fans_home
git pull origin main
```

### 2. 更新后端

```bash
cd repo/xxm_fans_backend

# 激活虚拟环境
source venv/bin/activate

# 安装新依赖
pip install -r requirements.txt

# 数据库迁移
python manage.py migrate

# 收集静态文件
python manage.py collectstatic --noinput

# 重启服务
sudo systemctl restart xxm-backend
```

### 3. 更新前端

```bash
cd repo/Temp_frontend

# 安装新依赖
npm install

# 生产构建
npm run build

# 重载 Nginx
sudo systemctl reload nginx
```

### 4. 数据库备份

```bash
# 创建备份目录
mkdir -p /home/user/backups

# 备份数据库
cp /home/user/xxm_fans_home/data/db.sqlite3 /home/user/backups/db_$(date +%Y%m%d_%H%M%S).sqlite3

# 自动备份脚本（添加到 crontab）
0 2 * * * cp /home/user/xxm_fans_home/data/db.sqlite3 /home/user/backups/db_$(date +\%Y\%m\%d_\%H\%M\%S).sqlite3
```

### 5. SSL 证书自动续期

Certbot 会自动设置定时任务，检查续期配置：

```bash
# 查看定时任务
sudo systemctl status certbot.timer

# 手动测试续期
sudo certbot renew --dry-run
```

### 6. 监控服务

使用监控工具（如 Supervisor 或 PM2）确保服务稳定运行。

---

## 附录

### A. 配置文件路径

| 配置文件 | 路径 |
|----------|------|
| Nginx 配置 | `/etc/nginx/sites-available/youyou-songlist.conf` |
| 后端环境变量 | `/home/user/xxm_fans_home/repo/xxm_fans_backend/.env` |
| 前端环境变量 | `/home/user/xxm_fans_home/repo/Temp_frontend/.env` |
| SSL 证书 | `/etc/letsencrypt/live/leyou.xxm8777.cn/` |
| 后端日志 | `/home/user/xxm_fans_home/repo/xxm_fans_backend/logs/` |
| Nginx 日志 | `/var/log/nginx/` |

### B. 常用命令

```bash
# 后端服务
sudo systemctl start xxm-backend      # 启动
sudo systemctl stop xxm-backend       # 停止
sudo systemctl restart xxm-backend    # 重启
sudo systemctl status xxm-backend     # 状态

# Nginx 服务
sudo systemctl start nginx            # 启动
sudo systemctl stop nginx             # 停止
sudo systemctl restart nginx          # 重启
sudo systemctl reload nginx           # 重载配置
sudo systemctl status nginx           # 状态

# SSL 证书
sudo certbot renew                    # 续期
sudo certbot certificates             # 查看证书
sudo certbot delete --cert-name leyou.xxm8777.cn  # 删除证书

# 日志查看
sudo journalctl -u xxm-backend -f     # 后端日志
sudo tail -f /var/log/nginx/access.log  # Nginx 访问日志
sudo tail -f /var/log/nginx/error.log   # Nginx 错误日志
```

### C. 性能优化建议

1. **启用 Gzip 压缩**：在 Nginx 配置中添加 gzip 压缩
2. **配置缓存**：为静态资源配置适当的缓存时间
3. **使用 CDN**：将静态文件部署到 CDN
4. **数据库优化**：定期清理和优化数据库
5. **监控资源**：使用 htop、vmstat 等工具监控服务器资源

### D. 安全建议

1. **定期更新系统**：`sudo apt update && sudo apt upgrade`
2. **配置防火墙**：使用 ufw 或 iptables 限制访问
3. **禁用 root 登录**：修改 SSH 配置
4. **定期备份数据**：设置自动备份任务
5. **监控日志**：定期检查异常访问记录

---

## 联系支持

如有问题，请参考：
- 项目文档：`/home/user/xxm_fans_home/doc/`
- GitHub Issues：提交问题反馈
- 技术支持：联系系统管理员

---

**文档版本**: 1.0
**最后更新**: 2026-01-27
**维护者**: XXM Fans Home Team