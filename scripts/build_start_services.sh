#!/bin/bash

# XXM Fans Home 生产环境服务启动脚本
# 使用 Next.js standalone + Gunicorn + Nginx

echo "========================================="
echo "XXM Fans Home 生产环境服务启动"
echo "========================================="
echo ""

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 检查是否已运行
check_running() {
    if ps aux | grep -v grep | grep -q "$1"; then
        return 0
    else
        return 1
    fi
}

# 1. 构建前端
echo "1. 构建前端生产版本 (Next.js)..."
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_frontend
if [ ! -f ".next/standalone/server.js" ]; then
    echo "   正在执行前端构建..."
    npm run build
    if [ $? -ne 0 ]; then
        echo -e "   ${RED}前端构建失败，停止启动${NC}"
        exit 1
    fi
    echo -e "   ${GREEN}前端构建成功${NC}"
else
    echo "   前端构建产物已存在 (.next/standalone/)，跳过构建"
fi
sleep 1

# 2. 启动 Next.js standalone 服务
echo "2. 启动 Next.js 前端服务..."
if check_running "next-server.*3000"; then
    echo "   Next.js 前端已在运行"
else
    cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_frontend/.next/standalone
    nohup node server.js > /tmp/nextjs.log 2>&1 &
    echo -e "   ${GREEN}Next.js 前端启动成功 (端口 3000)${NC}"
fi
sleep 2

# 3. 收集静态文件
echo "3. 收集后端静态文件..."
cd /home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend

# 先清理 staticfiles 目录（如果存在）
if [ -d "staticfiles" ]; then
    echo "   清理旧的静态文件..."
    rm -rf staticfiles
fi

# 重新收集静态文件
python3 manage.py collectstatic --noinput --clear
if [ $? -eq 0 ]; then
    echo -e "   ${GREEN}静态文件收集成功${NC}"
else
    echo -e "   ${YELLOW}静态文件收集失败，继续启动${NC}"
fi
sleep 1

# 4. 启动后端（使用 Gunicorn）
echo "4. 启动 Django 后端服务 (Gunicorn)..."
if check_running "gunicorn.*xxm_fans_home.wsgi"; then
    echo "   Django 后端已在运行"
else
    # 检查 gunicorn 是否安装，如果没有则安装
    if ! command -v gunicorn &> /dev/null; then
        echo "   安装 gunicorn..."
        pip3 install gunicorn
    fi

    # 使用配置文件启动 Gunicorn
    nohup gunicorn -c /home/yifeianyi/Desktop/xxm_fans_home/infra/gunicorn/gunicorn_config.py \
        xxm_fans_home.wsgi:application > /tmp/gunicorn.log 2>&1 &
    echo -e "   ${GREEN}Django 后端启动成功 (端口 8000)${NC}"
fi
sleep 2

# 5. 启动Nginx（使用生产配置）
echo "5. 启动 Nginx 代理服务..."
if check_running "nginx.*prod-xxm_nginx.conf"; then
    echo "   Nginx 已在运行"
else
    mkdir -p /tmp/nginx
    nginx -c /home/yifeianyi/Desktop/xxm_fans_home/infra/nginx/prod-xxm_nginx.conf -p /tmp/nginx 2>&1 | grep -v "alert"
    echo -e "   ${GREEN}Nginx 启动成功 (端口 8080)${NC}"
fi

echo ""
echo "========================================="
echo "生产环境服务启动完成！"
echo "========================================="
echo ""
echo "访问地址："
echo "  - 前端页面: http://localhost:8080/"
echo "  - 后端API:  http://localhost:8080/api/"
echo "  - 媒体文件: http://localhost:8080/media/"
echo ""
echo "日志文件："
echo "  - Next.js日志:     /tmp/nextjs.log"
echo "  - Gunicorn日志:    /tmp/gunicorn.log"
echo "  - Gunicorn访问日志: /tmp/gunicorn_access.log"
echo "  - Gunicorn错误日志: /tmp/gunicorn_error.log"
echo "  - Nginx日志:       /tmp/nginx/"
echo ""
echo "停止服务: ./build_stop_services.sh"
echo ""
