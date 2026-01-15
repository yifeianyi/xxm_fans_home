#!/bin/bash

# XXM Fans Home 服务启动脚本

echo "========================================="
echo "XXM Fans Home 服务启动"
echo "========================================="
echo ""

# 检查是否已运行
check_running() {
    if ps aux | grep -v grep | grep -q "$1"; then
        return 0
    else
        return 1
    fi
}

# 启动后端
echo "1. 启动 Django 后端服务..."
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend
if check_running "manage.py runserver"; then
    echo "   Django 后端已在运行"
else
    nohup python3 manage.py runserver 0.0.0.0:8000 > /tmp/backend.log 2>&1 &
    echo "   Django 后端启动成功 (端口 8000)"
fi
sleep 2

# 启动前端
echo "2. 启动 React 前端服务..."
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_frontend
if check_running "vite"; then
    echo "   React 前端已在运行"
else
    nohup npm run dev > /tmp/frontend.log 2>&1 &
    echo "   React 前端启动成功 (端口 5173)"
fi
sleep 3

# 启动Nginx
echo "3. 启动 Nginx 代理服务..."
if check_running "nginx.*xxm_nginx.conf"; then
    echo "   Nginx 已在运行"
else
    mkdir -p /tmp/nginx
    nginx -c /home/yifeianyi/Desktop/xxm_fans_home/infra/nginx/xxm_nginx.conf -p /tmp/nginx 2>&1 | grep -v "alert"
    echo "   Nginx 启动成功 (端口 8080)"
fi

echo ""
echo "========================================="
echo "服务启动完成！"
echo "========================================="
echo ""
echo "访问地址："
echo "  - 前端页面: http://localhost:8080/"
echo "  - 后端API:  http://localhost:8080/api/"
echo "  - 媒体文件: http://localhost:8080/media/"
echo ""
echo "日志文件："
echo "  - 后端日志: /tmp/backend.log"
echo "  - 前端日志: /tmp/frontend.log"
echo "  - Nginx日志: /tmp/nginx/"
echo ""
echo "停止服务: ./stop_services.sh"
echo "测试服务: ./test_integration.sh"
echo ""