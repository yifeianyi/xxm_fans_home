#!/bin/bash

# XXM Fans Home 前端构建脚本
# 支持本地构建和一键部署到服务器

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
LOCAL_FRONTEND_PATH="/home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_frontend"

# 显示帮助
show_help() {
    echo "XXM Fans Home 前端构建脚本"
    echo ""
    echo "用法: ./build-frontend.sh [选项]"
    echo ""
    echo "选项:"
    echo "  --deploy, -d      构建完成后自动部署到服务器"
    echo "  --skip-build, -s  跳过构建，仅部署现有构建产物"
    echo "  --help, -h        显示此帮助"
    echo ""
    echo "示例:"
    echo "  ./build-frontend.sh              # 仅构建"
    echo "  ./build-frontend.sh --deploy     # 构建并部署"
    echo "  ./build-frontend.sh -d           # 同上"
    echo "  ./build-frontend.sh -d -s        # 使用现有构建产物直接部署"
    echo ""
}

# 解析参数
AUTO_DEPLOY=false
SKIP_BUILD=false

for arg in "$@"; do
    case $arg in
        --deploy|-d)
            AUTO_DEPLOY=true
            ;;
        --skip-build|-s)
            SKIP_BUILD=true
            ;;
        --help|-h)
            show_help
            exit 0
            ;;
    esac
done

echo "========================================="
echo "XXM Fans Home 前端构建"
echo "========================================="
echo ""

# 构建步骤
if [ "$SKIP_BUILD" = false ]; then
    echo "步骤: 构建 Next.js 前端"
    echo ""
    
    cd "$LOCAL_FRONTEND_PATH"
    
    # 清理旧构建
    echo "清理旧构建..."
    rm -rf .next
    
    # 安装依赖
    echo "安装依赖..."
    npm install
    
    # 构建
    echo "开始构建..."
    npm run build
    
    # 复制 public 目录到 standalone (关键！)
    echo "复制静态资源到 standalone..."
    cp -r public .next/standalone/
    
    # 验证关键文件
    echo "验证构建产物..."
    if [ ! -f ".next/standalone/public/homepage.webp" ]; then
        echo -e "${RED}ERROR: homepage.webp not found!${NC}"
        exit 1
    fi
    
    if [ ! -f ".next/standalone/public/favicon.ico" ]; then
        echo -e "${RED}ERROR: favicon.ico not found!${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ 构建完成${NC}"
else
    # 验证现有构建产物
    if [ ! -d "$LOCAL_FRONTEND_PATH/.next/standalone" ]; then
        echo -e "${RED}错误: 构建产物不存在，请先运行构建${NC}"
        exit 1
    fi
    echo -e "${YELLOW}使用现有构建产物${NC}"
fi

echo ""
echo "========================================="
echo -e "${GREEN}构建阶段完成！${NC}"
echo "========================================="
echo ""

# 自动部署
if [ "$AUTO_DEPLOY" = true ]; then
    echo -e "${BLUE}>>> 开始自动部署到服务器${NC}"
    echo ""
    "$SCRIPT_DIR/deploy-to-server.sh" --skip-build
else
    echo "构建产物位置:"
    echo "  ${LOCAL_FRONTEND_PATH}/.next/standalone/"
    echo ""
    echo "手动部署命令:"
    echo "  ./deploy-to-server.sh"
    echo ""
    echo "或使用快捷命令:"
    echo "  ./build-frontend.sh --deploy"
    echo "  ./build-frontend.sh -d"
fi
