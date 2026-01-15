# 部署软链接配置说明

本文档详细说明项目部署时需要创建的所有软链接，包括环境配置、媒体资源和基础设施配置。

## 📋 软链接清单

### 1. 环境配置文件软链接

#### 后端环境变量
```bash
# 源文件
/home/yifeianyi/Desktop/xxm_fans_home/env/backend.env

# 软链接目标
/home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend/.env

# 创建命令
ln -s /home/yifeianyi/Desktop/xxm_fans_home/env/backend.env \
      /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend/.env
```

**说明**：
- Django 通过 `python-dotenv` 加载 `.env` 文件
- 软链接指向统一的配置文件，便于集中管理
- 配置文件包含：DJANGO_DEBUG、DJANGO_SECRET_KEY、DJANGO_ALLOWED_HOSTS、Spotify API配置等

#### 前端环境变量
```bash
# 源文件
/home/yifeianyi/Desktop/xxm_fans_home/env/frontend.env

# 软链接目标
/home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_frontend/.env

# 创建命令
ln -s /home/yifeianyi/Desktop/xxm_fans_home/env/frontend.env \
      /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_frontend/.env
```

**说明**：
- Vite 自动加载 `.env` 文件
- 软链接指向统一的配置文件，便于集中管理
- 配置文件包含：VITE_API_BASE_URL 等前端环境变量

### 2. 媒体资源软链接

#### 封面图片（covers）
```bash
# 源目录
/home/yifeianyi/Desktop/xxm_fans_home/media/covers

# 软链接目标
/home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend/static/covers

# 创建命令
ln -s /home/yifeianyi/Desktop/xxm_fans_home/media/covers \
      /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend/static/covers
```

**说明**：
- Django 静态文件服务需要访问封面图片
- 通过软链接将 `media/covers` 映射到 `static/covers`
- 便于 Nginx 统一提供静态文件服务

#### 二创图片资源（footprint）
```bash
# 源目录
/home/yifeianyi/Desktop/xxm_fans_home/media/footprint

# 软链接目标
/home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend/static/footprint

# 创建命令
ln -s /home/yifeianyi/Desktop/xxm_fans_home/media/footprint \
      /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend/static/footprint
```

**说明**：
- 粉丝二创作品的封面和图片资源
- 通过软链接将 `media/footprint` 映射到 `static/footprint`
- 便于 Nginx 统一提供静态文件服务
- 注意：此软链接可能在某些部署场景下未创建，需要手动创建

### 3. 基础设施配置文件软链接

#### Nginx 配置文件

**开发环境配置**：
```bash
# 源文件
/home/yifeianyi/Desktop/xxm_fans_home/infra/nginx/xxm_nginx.conf

# 软链接目标（可选，根据部署方式）
/etc/nginx/sites-available/xxm_fans_home
/etc/nginx/sites-enabled/xxm_fans_home

# 创建命令（需要 root 权限）
sudo ln -s /home/yifeianyi/Desktop/xxm_fans_home/infra/nginx/xxm_nginx.conf \
      /etc/nginx/sites-available/xxm_fans_home
sudo ln -s /etc/nginx/sites-available/xxm_fans_home \
      /etc/nginx/sites-enabled/xxm_fans_home
```

**生产环境配置**：
```bash
# 源文件
/home/yifeianyi/Desktop/xxm_fans_home/infra/nginx/prod-xxm_nginx.conf

# 软链接目标（可选，根据部署方式）
/etc/nginx/sites-available/xxm_fans_home
/etc/nginx/sites-enabled/xxm_fans_home

# 创建命令（需要 root 权限）
sudo ln -s /home/yifeianyi/Desktop/xxm_fans_home/infra/nginx/prod-xxm_nginx.conf \
      /etc/nginx/sites-available/xxm_fans_home
sudo ln -s /etc/nginx/sites-available/xxm_fans_home \
      /etc/nginx/sites-enabled/xxm_fans_home
```

**说明**：
- Nginx 配置文件位于 `infra/nginx/` 目录
- 根据部署环境选择对应的配置文件
- 软链接到 Nginx 配置目录，便于管理
- 也可以直接复制配置文件到目标位置

#### Gunicorn 配置文件

```bash
# 源文件
/home/yifeianyi/Desktop/xxm_fans_home/infra/gunicorn/gunicorn_config.py

# 软链接目标（可选，根据部署方式）
/etc/gunicorn.d/xxm_fans_home.py

# 创建命令（需要 root 权限）
sudo ln -s /home/yifeianyi/Desktop/xxm_fans_home/infra/gunicorn/gunicorn_config.py \
      /etc/gunicorn.d/xxm_fans_home.py
```

**说明**：
- Gunicorn 配置文件位于 `infra/gunicorn/` 目录
- 软链接到 Gunicorn 配置目录，便于管理
- 也可以在启动时直接指定配置文件路径：`-c /path/to/gunicorn_config.py`

#### systemd 服务配置文件

```bash
# 源文件
/home/yifeianyi/Desktop/xxm_fans_home/infra/systemd/xxm-fans-home.service

# 软链接目标（可选，根据部署方式）
/etc/systemd/system/xxm-fans-home.service

# 创建命令（需要 root 权限）
sudo ln -s /home/yifeianyi/Desktop/xxm_fans_home/infra/systemd/xxm-fans-home.service \
      /etc/systemd/system/xxm-fans-home.service
```

**说明**：
- systemd 服务配置文件位于 `infra/systemd/` 目录
- 软链接到 systemd 配置目录
- 创建后需要执行 `sudo systemctl daemon-reload` 重新加载配置

## 🔧 一键创建脚本

### 创建所有必需的软链接

```bash
#!/bin/bash

# 项目根目录
PROJECT_ROOT="/home/yifeianyi/Desktop/xxm_fans_home"

echo "开始创建软链接..."

# 1. 环境配置文件软链接
echo "创建环境配置文件软链接..."

# 后端环境变量
if [ ! -L "$PROJECT_ROOT/repo/xxm_fans_backend/.env" ]; then
    ln -s "$PROJECT_ROOT/env/backend.env" \
          "$PROJECT_ROOT/repo/xxm_fans_backend/.env"
    echo "✓ 后端环境变量软链接创建成功"
else
    echo "✓ 后端环境变量软链接已存在"
fi

# 前端环境变量
if [ ! -L "$PROJECT_ROOT/repo/xxm_fans_frontend/.env" ]; then
    ln -s "$PROJECT_ROOT/env/frontend.env" \
          "$PROJECT_ROOT/repo/xxm_fans_frontend/.env"
    echo "✓ 前端环境变量软链接创建成功"
else
    echo "✓ 前端环境变量软链接已存在"
fi

# 2. 媒体资源软链接
echo "创建媒体资源软链接..."

# 封面图片
if [ ! -L "$PROJECT_ROOT/repo/xxm_fans_backend/static/covers" ]; then
    ln -s "$PROJECT_ROOT/media/covers" \
          "$PROJECT_ROOT/repo/xxm_fans_backend/static/covers"
    echo "✓ 封面图片软链接创建成功"
else
    echo "✓ 封面图片软链接已存在"
fi

# 二创图片资源
if [ ! -L "$PROJECT_ROOT/repo/xxm_fans_backend/static/footprint" ]; then
    ln -s "$PROJECT_ROOT/media/footprint" \
          "$PROJECT_ROOT/repo/xxm_fans_backend/static/footprint"
    echo "✓ 二创图片资源软链接创建成功"
else
    echo "✓ 二创图片资源软链接已存在"
fi

echo "所有软链接创建完成！"
```

保存为 `scripts/create_symlinks.sh`，然后执行：
```bash
chmod +x scripts/create_symlinks.sh
./scripts/create_symlinks.sh
```

### 创建基础设施配置软链接（需要 root 权限）

```bash
#!/bin/bash

# 项目根目录
PROJECT_ROOT="/home/yifeianyi/Desktop/xxm_fans_home"

echo "开始创建基础设施配置软链接..."

# Nginx 配置（生产环境）
sudo ln -s "$PROJECT_ROOT/infra/nginx/prod-xxm_nginx.conf" \
      /etc/nginx/sites-available/xxm_fans_home
sudo ln -s /etc/nginx/sites-available/xxm_fans_home \
      /etc/nginx/sites-enabled/xxm_fans_home
echo "✓ Nginx 配置软链接创建成功"

# Gunicorn 配置
sudo ln -s "$PROJECT_ROOT/infra/gunicorn/gunicorn_config.py" \
      /etc/gunicorn.d/xxm_fans_home.py
echo "✓ Gunicorn 配置软链接创建成功"

# systemd 服务配置
sudo ln -s "$PROJECT_ROOT/infra/systemd/xxm-fans-home.service" \
      /etc/systemd/system/xxm-fans-home.service
sudo systemctl daemon-reload
echo "✓ systemd 服务配置软链接创建成功"

echo "所有基础设施配置软链接创建完成！"
```

保存为 `scripts/create_infra_symlinks.sh`，然后执行：
```bash
chmod +x scripts/create_infra_symlinks.sh
sudo ./scripts/create_infra_symlinks.sh
```

## 📝 验证软链接

### 检查所有软链接

```bash
# 检查环境配置文件软链接
ls -la /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend/.env
ls -la /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_frontend/.env

# 检查媒体资源软链接
ls -la /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend/static/covers
ls -la /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend/static/footprint

# 检查基础设施配置软链接（需要 root 权限）
sudo ls -la /etc/nginx/sites-enabled/xxm_fans_home
sudo ls -la /etc/gunicorn.d/xxm_fans_home.py
sudo ls -la /etc/systemd/system/xxm-fans-home.service
```

### 测试软链接是否正常工作

```bash
# 测试环境配置文件读取
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend
python -c "from dotenv import load_dotenv; load_dotenv(); import os; print('DJANGO_DEBUG:', os.getenv('DJANGO_DEBUG'))"

cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_frontend
cat .env

# 测试媒体资源访问
ls -la /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend/static/covers
ls -la /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend/static/footprint
```

## ⚠️ 注意事项

1. **权限问题**：基础设施配置软链接需要 root 权限，使用 `sudo` 创建
2. **路径一致性**：确保所有路径使用绝对路径，避免相对路径问题
3. **软链接已存在**：脚本会检查软链接是否已存在，避免重复创建
4. **删除软链接**：如需删除软链接，使用 `rm` 命令（不要使用 `-r` 递归删除）
   ```bash
   rm /path/to/symlink
   ```
5. **更新软链接**：如需更新软链接目标，先删除旧软链接，再创建新软链接
6. **备份重要数据**：在删除或更新软链接前，确保已备份重要数据
7. **环境差异**：开发环境和生产环境的配置文件可能不同，注意选择正确的配置文件

## 🚀 部署流程建议

1. **首次部署**：
   - 运行 `scripts/create_symlinks.sh` 创建应用级软链接
   - 运行 `scripts/create_infra_symlinks.sh` 创建基础设施软链接
   - 验证所有软链接是否正常工作
   - 启动服务并进行测试

2. **更新部署**：
   - 更新配置文件（`env/backend.env`、`env/frontend.env`）
   - 无需重新创建软链接，配置会自动生效
   - 重启相关服务

3. **环境切换**：
   - 修改 `infra/nginx/` 下的 Nginx 配置文件软链接
   - 修改环境变量配置文件
   - 重启服务

## 📚 相关文档

- `IFLOW.md` - 项目技术文档
- `README.md` - 项目说明文档
- `infra/nginx/README.md` - Nginx 配置说明
- `infra/gunicorn/README.md` - Gunicorn 配置说明