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