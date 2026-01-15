#!/bin/bash

# XXM Fans Home 生产环境服务停止脚本

echo "========================================="
echo "XXM Fans Home 生产环境服务停止"
echo "========================================="
echo ""

# 停止Nginx
echo "1. 停止 Nginx 服务..."
if ps aux | grep -v grep | grep -q "nginx.*prod-xxm_nginx.conf"; then
    nginx -s stop -c /home/yifeianyi/Desktop/xxm_fans_home/infra/nginx/prod-xxm_nginx.conf -p /tmp/nginx 2>&1 | grep -v "alert"
    echo "   ${GREEN}Nginx 已停止${NC}"
else
    echo "   Nginx 未运行"
fi

# 停止后端（Gunicorn）
echo "2. 停止 Django 后端服务 (Gunicorn)..."
if ps aux | grep -v grep | grep -q "xxm_fans_home_gunicorn"; then
    pkill -f "xxm_fans_home_gunicorn"
    echo "   ${GREEN}Django 后端已停止${NC}"
else
    echo "   Django 后端未运行"
fi

# 清理临时文件
echo "3. 清理临时日志文件..."
rm -f /tmp/gunicorn.log /tmp/gunicorn_access.log /tmp/gunicorn_error.log
echo "   ${GREEN}临时日志文件已清理${NC}"

echo ""
echo "========================================="
echo "生产环境所有服务已停止"
echo "========================================="
echo ""