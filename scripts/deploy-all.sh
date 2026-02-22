#!/bin/bash

# XXM Fans Home 完整部署脚本
# 一键部署前端和后端到服务器

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# 显示配置
echo "========================================="
echo "XXM Fans Home 完整部署"
echo "========================================="
echo ""
echo "此脚本将依次执行："
echo "  1. 部署前端 (build + upload + restart)"
echo "  2. 部署后端 (upload + migrate + restart)"
echo "  3. 重载 Nginx"
echo ""

# 解析参数
FRONTEND_ONLY=false
BACKEND_ONLY=false
SKIP_BUILD=false
SKIP_MIGRATE=false

for arg in "$@"; do
    case $arg in
        --frontend-only)
            FRONTEND_ONLY=true
            echo -e "${YELLOW}仅部署前端${NC}"
            ;;
        --backend-only)
            BACKEND_ONLY=true
            echo -e "${YELLOW}仅部署后端${NC}"
            ;;
        --skip-build)
            SKIP_BUILD=true
            echo -e "${YELLOW}跳过前端构建${NC}"
            ;;
        --skip-migrate)
            SKIP_MIGRATE=true
            echo -e "${YELLOW}跳过数据库迁移${NC}"
            ;;
        --help|-h)
            echo "用法: ./deploy-all.sh [选项]"
            echo ""
            echo "选项:"
            echo "  --frontend-only   仅部署前端"
            echo "  --backend-only    仅部署后端"
            echo "  --skip-build      跳过前端构建（使用现有构建产物）"
            echo "  --skip-migrate    跳过数据库迁移"
            echo "  --help, -h        显示此帮助"
            echo ""
            echo "示例:"
            echo "  ./deploy-all.sh                    # 完整部署"
            echo "  ./deploy-all.sh --frontend-only    # 仅部署前端"
            echo "  ./deploy-all.sh --skip-build       # 使用现有构建，不重新构建"
            exit 0
            ;;
    esac
done

echo ""

# 询问确认
echo -n "是否继续部署? (y/n): "
read -r confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo -e "${YELLOW}已取消部署${NC}"
    exit 0
fi

echo ""
START_TIME=$(date +%s)

# 部署前端
if [ "$BACKEND_ONLY" = false ]; then
    echo ""
    echo "========================================="
    echo -e "${BLUE}>>> 开始部署前端${NC}"
    echo "========================================="
    echo ""
    
    if [ "$SKIP_BUILD" = true ]; then
        "$SCRIPT_DIR/deploy-to-server.sh" --skip-build
    else
        "$SCRIPT_DIR/deploy-to-server.sh"
    fi
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}前端部署失败${NC}"
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}✓ 前端部署完成${NC}"
fi

# 部署后端
if [ "$FRONTEND_ONLY" = false ]; then
    echo ""
    echo "========================================="
    echo -e "${BLUE}>>> 开始部署后端${NC}"
    echo "========================================="
    echo ""
    
    if [ "$SKIP_MIGRATE" = true ]; then
        "$SCRIPT_DIR/deploy-backend.sh" --skip-migrate
    else
        "$SCRIPT_DIR/deploy-backend.sh"
    fi
    
    if [ $? -ne 0 ]; then
        echo -e "${RED}后端部署失败${NC}"
        exit 1
    fi
    
    echo ""
    echo -e "${GREEN}✓ 后端部署完成${NC}"
fi

# 计算耗时
END_TIME=$(date +%s)
ELAPSED=$((END_TIME - START_TIME))
MINUTES=$((ELAPSED / 60))
SECONDS=$((ELAPSED % 60))

echo ""
echo "========================================="
echo -e "${GREEN}全部部署成功！${NC}"
echo "========================================="
echo ""
echo "耗时: ${MINUTES}分${SECONDS}秒"
echo ""
echo "部署内容:"
[ "$BACKEND_ONLY" = false ] && echo "  ✓ 前端已更新"
[ "$FRONTEND_ONLY" = false ] && echo "  ✓ 后端已更新"
echo ""
echo "Nginx 已重载"
echo ""
