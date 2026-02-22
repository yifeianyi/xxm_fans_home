#!/bin/bash

# XXM Fans Home - 快速重载 Nginx 配置
# 使用 nginx -s reload 命令重载配置

set -e

# 颜色定义
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 配置（从 config.yaml 读取）
CONFIG_FILE="/home/yifeianyi/Desktop/xxm_fans_home/.agents/skills/prod-env-connect/config.yaml"

# 默认配置
DEFAULT_SERVER_HOST="47.92.253.0"
DEFAULT_SERVER_USER="yifeianyi"
DEFAULT_SERVER_PORT="22"

# 从配置文件读取（如果存在）
if [ -f "$CONFIG_FILE" ]; then
    SERVER_HOST=$(grep -E "^\s*host:" "$CONFIG_FILE" | head -1 | sed 's/.*:\s*"\([^"]*\)".*/\1/')
    SERVER_USER=$(grep -E "^\s*username:" "$CONFIG_FILE" | head -1 | sed 's/.*:\s*"\([^"]*\)".*/\1/')
    SERVER_PORT=$(grep -E "^\s*port:" "$CONFIG_FILE" | head -1 | sed 's/.*:\s*\([0-9]*\).*/\1/')
fi

# 使用默认值（如果配置未读取到）
SERVER_HOST=${SERVER_HOST:-$DEFAULT_SERVER_HOST}
SERVER_USER=${SERVER_USER:-$DEFAULT_SERVER_USER}
SERVER_PORT=${SERVER_PORT:-$DEFAULT_SERVER_PORT}

echo "========================================="
echo "Nginx 配置重载"
echo "========================================="
echo -e "服务器: ${BLUE}${SERVER_USER}@${SERVER_HOST}:${SERVER_PORT}${NC}"
echo ""

# 检查 ssh 连接
echo "测试 SSH 连接..."
if ! ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no -p "$SERVER_PORT" "${SERVER_USER}@${SERVER_HOST}" "echo 'SSH OK'" > /dev/null 2>&1; then
    echo -e "${RED}错误: 无法连接到服务器${NC}"
    exit 1
fi
echo -e "${GREEN}✓ SSH 连接正常${NC}"
echo ""

# 重载 Nginx
echo "执行 nginx -s reload..."
ssh -p "$SERVER_PORT" "${SERVER_USER}@${SERVER_HOST}" "
    set -e
    echo '测试 Nginx 配置...'
    if sudo nginx -t; then
        echo '配置测试通过'
        echo '重载 Nginx...'
        sudo nginx -s reload
        echo 'Nginx 重载成功'
    else
        echo '错误: Nginx 配置测试失败'
        exit 1
    fi
"

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Nginx 配置重载完成${NC}"
else
    echo ""
    echo -e "${RED}✗ Nginx 重载失败${NC}"
    exit 1
fi
