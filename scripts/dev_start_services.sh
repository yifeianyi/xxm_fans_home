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
echo "2. 启动 Vite 前端服务..."
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_frontend
if check_running "vite.*5173"; then
    echo "   Vite 前端已在运行"
else
    nohup npm run dev > /tmp/frontend.log 2>&1 &
    echo "   Vite 前端启动成功 (端口 5173)"
fi
sleep 3

# 启动模板化歌单前端
echo "2.5. 启动模板化歌单前端服务..."
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/TempSongListFrontend
if check_running "vite.*5174"; then
    echo "   模板化歌单前端已在运行"
else
    nohup npm run dev -- --port 5174 > /tmp/songlist_frontend.log 2>&1 &
    echo "   模板化歌单前端启动成功 (端口 5174)"
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
echo "  - 主前端页面:        http://localhost:8080/"
echo "  - 模板化歌单:        http://localhost:8080/songlist/"
echo "  - 模板化歌单(乐游):  http://localhost:8080/songlist/?artist=youyou"
echo "  - 模板化歌单(冰洁):  http://localhost:8080/songlist/?artist=bingjie"
echo "  - 后端API:           http://localhost:8080/api/"
echo "  - 媒体文件:          http://localhost:8080/media/"
echo ""
echo "直接访问端口："
echo "  - 主前端(Vite):      http://localhost:5173/"
echo "  - 模板化歌单(Vite):  http://localhost:5174/"
echo "  - 后端(Django):      http://localhost:8000/"
echo ""
echo "API 测试："
echo "  - 歌曲列表:          http://localhost:8080/api/songlist/songs/?artist=youyou"
echo "  - 语言列表:          http://localhost:8080/api/songlist/languages/?artist=youyou"
echo "  - 曲风列表:          http://localhost:8080/api/songlist/styles/?artist=youyou"
echo "  - 网站设置:          http://localhost:8080/api/songlist/site-settings/?artist=youyou"
echo ""
echo "日志文件："
echo "  - 后端日志:          /tmp/backend.log"
echo "  - 前端日志:          /tmp/frontend.log"
echo "  - 注意: 主前端使用 Vite (端口 5173)"
echo "  - 歌单日志:          /tmp/songlist_frontend.log"
echo "  - Nginx日志:         /tmp/nginx/"
echo ""
echo "停止服务: ./dev_stop_services.sh"
echo "测试服务: ./test_integration.sh"
echo ""