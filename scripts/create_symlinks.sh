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

# 3. 后端 MEDIA_ROOT 软链接（确保上传文件保存到正确位置）
echo "创建后端 MEDIA_ROOT 软链接..."

BACKEND_MEDIA="$PROJECT_ROOT/repo/xxm_fans_backend/media"
TARGET_MEDIA="$PROJECT_ROOT/media"

if [ -e "$BACKEND_MEDIA" ]; then
    if [ -L "$BACKEND_MEDIA" ]; then
        echo "✓ 后端 media 软链接已存在"
    else
        # 备份真实目录中的文件到目标位置
        echo "发现后端 media 真实目录，正在迁移文件..."
        if [ -d "$BACKEND_MEDIA" ]; then
            cp -r "$BACKEND_MEDIA"/* "$TARGET_MEDIA"/ 2>/dev/null || true
            rm -rf "$BACKEND_MEDIA"
            ln -s "$TARGET_MEDIA" "$BACKEND_MEDIA"
            echo "✓ 后端 media 软链接创建成功（文件已迁移）"
        fi
    fi
else
    ln -s "$TARGET_MEDIA" "$BACKEND_MEDIA"
    echo "✓ 后端 media 软链接创建成功"
fi

echo "所有软链接创建完成！"