#!/bin/bash
# 构建并准备 Next.js 前端部署包

set -e

echo "=== Building Next.js Frontend ==="

cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_frontend

# 清理旧构建
rm -rf .next

# 安装依赖
npm install

# 构建
npm run build

# 复制 public 目录到 standalone (关键！)
echo "=== Copying public assets ==="
cp -r public .next/standalone/

# 验证关键文件
if [ ! -f ".next/standalone/public/homepage.webp" ]; then
    echo "ERROR: homepage.webp not found!"
    exit 1
fi

if [ ! -f ".next/standalone/public/favicon.ico" ]; then
    echo "ERROR: favicon.ico not found!"
    exit 1
fi

echo "=== Build completed successfully ==="
echo "Next: Run ./deploy-frontend.sh to deploy"
