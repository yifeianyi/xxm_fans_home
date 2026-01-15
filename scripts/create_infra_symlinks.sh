#!/bin/bash

# 项目根目录
PROJECT_ROOT="/home/yifeianyi/Desktop/xxm_fans_home"

echo "开始创建基础设施配置软链接..."

# 检查是否有 root 权限
if [ "$EUID" -ne 0 ]; then
    echo "请使用 sudo 运行此脚本"
    exit 1
fi

# Nginx 配置（生产环境）
ln -s "$PROJECT_ROOT/infra/nginx/prod-xxm_nginx.conf" \
      /etc/nginx/sites-available/xxm_fans_home
ln -s /etc/nginx/sites-available/xxm_fans_home \
      /etc/nginx/sites-enabled/xxm_fans_home
echo "✓ Nginx 配置软链接创建成功"

# Gunicorn 配置
ln -s "$PROJECT_ROOT/infra/gunicorn/gunicorn_config.py" \
      /etc/gunicorn.d/xxm_fans_home.py
echo "✓ Gunicorn 配置软链接创建成功"

# systemd 服务配置
if [ -f "$PROJECT_ROOT/infra/systemd/xxm-fans-home.service" ]; then
    ln -s "$PROJECT_ROOT/infra/systemd/xxm-fans-home.service" \
          /etc/systemd/system/xxm-fans-home.service
    systemctl daemon-reload
    echo "✓ systemd 服务配置软链接创建成功"
else
    echo "⚠ systemd 服务配置文件不存在，跳过"
fi

echo "所有基础设施配置软链接创建完成！"