#!/bin/bash

# XXM Fans Home - Next.js 开发环境停止脚本

echo "========================================="
echo "XXM Fans Home - Next.js 开发环境停止"
echo "========================================="
echo ""

# 停止 Next.js 开发服务器
echo "1. 停止 Next.js 开发服务器..."
NEXTJS_PIDS=$(ps aux | grep -v grep | grep "next.*dev" | awk '{print $2}')
if [ -n "$NEXTJS_PIDS" ]; then
    echo "$NEXTJS_PIDS" | xargs kill -TERM 2>/dev/null
    sleep 2
    # 强制终止未关闭的进程
    NEXTJS_PIDS=$(ps aux | grep -v grep | grep "next.*dev" | awk '{print $2}')
    if [ -n "$NEXTJS_PIDS" ]; then
        echo "$NEXTJS_PIDS" | xargs kill -KILL 2>/dev/null
    fi
    echo "   Next.js 开发服务器已停止"
else
    echo "   Next.js 开发服务器未运行"
fi

# 停止 Django 后端
echo "2. 停止 Django 后端服务..."
BACKEND_PIDS=$(ps aux | grep -v grep | grep "manage.py runserver" | awk '{print $2}')
if [ -n "$BACKEND_PIDS" ]; then
    echo "$BACKEND_PIDS" | xargs kill -TERM 2>/dev/null
    sleep 1
    echo "   Django 后端已停止"
else
    echo "   Django 后端未运行"
fi

# 停止 Nginx（如果是 Next.js 专用配置）
echo "3. 停止 Nginx 服务..."
NGINX_PIDS=$(ps aux | grep -v grep | grep "nginx.*nextjs_nginx.conf" | awk '{print $2}')
if [ -n "$NGINX_PIDS" ]; then
    echo "$NGINX_PIDS" | xargs kill -TERM 2>/dev/null
    sleep 1
    echo "   Nginx 已停止"
else
    echo "   Nginx 未运行或未使用 Next.js 配置"
fi

echo ""
echo "========================================="
echo "Next.js 开发环境已停止"
echo "========================================="
echo ""

# 清理日志（可选）
read -p "是否清理日志文件? (y/N): " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    rm -f /tmp/nextjs_dev.log /tmp/backend_nextjs.log
    echo "日志文件已清理"
fi

echo ""
echo "已停止的服务："
echo "  - Next.js 开发服务器 (端口 3000)"
echo "  - Django 后端 (端口 8000/8001)"
echo "  - Nginx (端口 8080) [如果已启动]"
echo ""
