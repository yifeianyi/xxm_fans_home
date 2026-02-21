#!/bin/bash

# XXM Fans Home 服务停止脚本

echo "========================================="
echo "XXM Fans Home 服务停止"
echo "========================================="
echo ""

# 停止Nginx
echo "1. 停止 Nginx 服务..."
if ps aux | grep -v grep | grep -q "nginx.*xxm_nginx.conf"; then
    nginx -s stop -c /home/yifeianyi/Desktop/xxm_fans_home/infra/nginx/xxm_nginx.conf -p /tmp/nginx 2>&1 | grep -v "alert"
    echo "   Nginx 已停止"
else
    echo "   Nginx 未运行"
fi

# 停止模板化歌单前端
echo "2. 停止模板化歌单前端服务..."
if ps aux | grep -v grep | grep -q "vite.*5174"; then
    pkill -f "vite.*5174"
    echo "   模板化歌单前端已停止"
else
    echo "   模板化歌单前端未运行"
fi

# 停止主前端
echo "2.5. 停止主前端服务..."
if ps aux | grep -v grep | grep -q "next-server.*3000"; then
    pkill -f "next-server.*3000"
    echo "   Next.js 前端已停止"
else
    echo "   Next.js 前端未运行"
fi

# 停止后端
echo "3. 停止 Django 后端服务..."
if ps aux | grep -v grep | grep -q "manage.py runserver"; then
    pkill -f "manage.py runserver"
    echo "   Django 后端已停止"
else
    echo "   Django 后端未运行"
fi

echo ""
echo "========================================="
echo "所有服务已停止"
echo "========================================="
echo ""