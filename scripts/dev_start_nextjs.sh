#!/bin/bash

# XXM Fans Home - Next.js 开发环境启动脚本
# 用于 Next.js 迁移开发和测试

echo "========================================="
echo "XXM Fans Home - Next.js 开发环境启动"
echo "========================================="
echo ""

# 配置
PROJECT_ROOT="/home/yifeianyi/Desktop/xxm_fans_home"
NEXTJS_DIR="$PROJECT_ROOT/repo/xxm_fans_frontend"
NEXTJS_WORKSPACE="$PROJECT_ROOT/repo/xxm_nextjs"
BACKEND_DIR="$PROJECT_ROOT/repo/xxm_fans_backend"
API_PORT=8000
NEXTJS_PORT=3000
NGINX_PORT=8080

# 检查是否已运行
check_running() {
    if ps aux | grep -v grep | grep -q "$1"; then
        return 0
    else
        return 1
    fi
}

# 检查端口是否被占用
check_port() {
    if lsof -Pi :"$1" -sTCP:LISTEN -t >/dev/null 2>&1; then
        return 0
    else
        return 1
    fi
}

# 启动后端 API
echo "1. 启动 Django 后端服务..."
cd "$BACKEND_DIR"
if check_running "manage.py runserver.*$API_PORT"; then
    echo "   Django 后端已在运行 (端口 $API_PORT)"
else
    # 检查端口是否被占用
    if check_port "$API_PORT"; then
        echo "   警告: 端口 $API_PORT 已被占用，尝试使用其他端口"
        API_PORT=8001
    fi
    
    source venv/bin/activate 2>/dev/null || echo "   注意: 未找到 venv，使用系统 Python"
    nohup python3 manage.py runserver 0.0.0.0:$API_PORT > /tmp/backend_nextjs.log 2>&1 &
    echo "   Django 后端启动成功 (端口 $API_PORT)"
    
    # 等待后端启动
    sleep 3
    
    # 验证后端是否可用
    if curl -s "http://localhost:$API_PORT/api/songs/" > /dev/null; then
        echo "   后端 API 验证成功"
    else
        echo "   警告: 后端 API 可能未完全启动，将继续..."
    fi
fi

# 确定 Next.js 项目目录
if [ -d "$NEXTJS_WORKSPACE" ]; then
    NEXTJS_PROJECT="$NEXTJS_WORKSPACE"
    echo ""
    echo "2. 使用独立工作目录的 Next.js 项目..."
else
    NEXTJS_PROJECT="$NEXTJS_DIR"
    echo ""
    echo "2. 使用原项目目录的 Next.js..."
fi

# 检查 Next.js 项目是否存在
if [ ! -f "$NEXTJS_PROJECT/package.json" ]; then
    echo "   错误: 未找到 Next.js 项目"
    echo "   请先完成 Phase 1 的项目初始化"
    echo "   预期目录: $NEXTJS_WORKSPACE 或 $NEXTJS_DIR"
    exit 1
fi

# 启动 Next.js 开发服务器
echo "3. 启动 Next.js 开发服务器..."
cd "$NEXTJS_PROJECT"

# 检查 node_modules 是否存在
if [ ! -d "node_modules" ]; then
    echo "   安装依赖..."
    npm install
fi

if check_running "next.*$NEXTJS_PORT"; then
    echo "   Next.js 开发服务器已在运行 (端口 $NEXTJS_PORT)"
else
    # 检查端口是否被占用
    if check_port "$NEXTJS_PORT"; then
        echo "   警告: 端口 $NEXTJS_PORT 已被占用，Next.js 将自动选择其他端口"
    fi
    
    nohup npm run dev > /tmp/nextjs_dev.log 2>&1 &
    echo "   Next.js 开发服务器启动中..."
    
    # 等待启动
    sleep 5
    
    # 检查是否成功启动
    for i in {1..10}; do
        if check_running "next.*dev"; then
            echo "   Next.js 开发服务器启动成功"
            break
        fi
        sleep 1
    done
fi

# 启动 Nginx
echo ""
echo "4. 启动 Nginx 代理服务..."
if check_running "nginx.*nextjs_nginx.conf"; then
    echo "   Nginx 已在运行 (端口 $NGINX_PORT)"
else
    # 检查 Next.js 专用 Nginx 配置是否存在
    if [ -f "$PROJECT_ROOT/infra/nginx/nextjs_nginx.conf" ]; then
        mkdir -p /tmp/nginx
        nginx -c $PROJECT_ROOT/infra/nginx/nextjs_nginx.conf -p /tmp/nginx 2>&1 | grep -v "alert"
        echo "   Nginx 启动成功 (端口 $NGINX_PORT)"
    else
        echo "   错误: 未找到 Next.js 专用 Nginx 配置"
        echo "   预期路径: $PROJECT_ROOT/infra/nginx/nextjs_nginx.conf"
        exit 1
    fi
fi

echo ""
echo "========================================="
echo "Next.js 开发环境启动完成！"
echo "========================================="
echo ""
echo "✅ 推荐访问地址（通过 Nginx 代理）："
echo "  - 前端页面:          http://localhost:8080/"
echo "  - 后端 API:          http://localhost:8080/api/"
echo "  - 后端 Admin:        http://localhost:8080/admin/"
echo "  - 媒体文件:          http://localhost:8080/media/"
echo ""
echo "⚠️  注意：请使用 8080 端口访问，Nginx 会统一处理前端、API 和媒体文件"
echo ""
echo "直接访问端口（调试用）："
echo "  - Next.js 前端:      http://localhost:3000/"
echo "  - Django 后端:       http://localhost:$API_PORT/"
echo ""
echo "API 测试："
echo "  - 歌曲列表:          http://localhost:8080/api/songs/"
echo "  - 图集列表:          http://localhost:8080/api/gallery/"
echo "  - 直播记录:          http://localhost:8080/api/livestream/"
echo "  - 二创合集:          http://localhost:8080/api/fansDIY/collections/"
echo ""
echo "日志文件："
echo "  - 后端日志:          /tmp/backend_nextjs.log"
echo "  - Next.js 日志:      /tmp/nextjs_dev.log"
echo "  - Nginx 日志:        /tmp/nginx/"
echo ""
echo "常用命令："
echo "  - 停止服务:          ./dev_stop_nextjs.sh"
echo "  - 查看日志:          tail -f /tmp/nextjs_dev.log"
echo ""

# 显示当前运行的服务
echo "当前运行的服务："
ps aux | grep -E "(next|manage.py|nginx)" | grep -v grep | awk '{print "  - " $11 " (PID: " $2 ")"}'
echo ""
