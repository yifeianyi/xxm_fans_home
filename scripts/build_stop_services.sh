#!/bin/bash

# XXM Fans Home 生产环境服务停止脚本

echo "========================================="
echo "XXM Fans Home 生产环境服务停止"
echo "========================================="
echo ""

# 颜色定义
GREEN='\033[0;32m'
NC='\033[0m' # No Color

# 停止Nginx
echo "1. 停止 Nginx 服务..."
if ps aux | grep -v grep | grep -q "nginx.*prod-xxm_nginx.conf"; then
    nginx -s stop -c /home/yifeianyi/Desktop/xxm_fans_home/infra/nginx/prod-xxm_nginx.conf -p /tmp/nginx 2>&1 | grep -v "alert"
    echo -e "   ${GREEN}Nginx 已停止${NC}"
else
    echo "   Nginx 未运行"
fi

# 停止 Next.js 前端
echo "2. 停止 Next.js 前端服务..."
if ps aux | grep -v grep | grep -q "next-server.*3000"; then
    pkill -f "next-server.*3000"
    echo -e "   ${GREEN}Next.js 前端已停止${NC}"
else
    echo "   Next.js 前端未运行"
fi

# 停止后端（Gunicorn）
echo "3. 停止 Django 后端服务 (Gunicorn)..."
if ps aux | grep -v grep | grep -q "xxm_fans_home_gunicorn"; then
    pkill -f "xxm_fans_home_gunicorn"
    echo -e "   ${GREEN}Django 后端已停止${NC}"
else
    echo "   Django 后端未运行"
fi

# 清理临时文件
echo "4. 清理临时日志文件..."
rm -f /tmp/nextjs.log /tmp/gunicorn.log /tmp/gunicorn_access.log /tmp/gunicorn_error.log
echo -e "   ${GREEN}临时日志文件已清理${NC}"

echo ""
echo "========================================="
echo "生产环境所有服务已停止"
echo "========================================="
echo ""
