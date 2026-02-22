#!/bin/bash

# XXM Fans Home 部署脚本
# 本地打包后上传到服务器部署

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
DEFAULT_REMOTE_FRONTEND_PATH="/home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_frontend"
DEFAULT_REMOTE_BACKEND_PATH="/home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend"

# 本地路径
LOCAL_FRONTEND_PATH="/home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_frontend"
LOCAL_BUILD_PATH="${LOCAL_FRONTEND_PATH}/.next/standalone"

# 从配置文件读取（如果存在）
if [ -f "$CONFIG_FILE" ]; then
    SERVER_HOST=$(grep -E "^\s*host:" "$CONFIG_FILE" | head -1 | sed 's/.*:\s*"\([^"]*\)".*/\1/')
    SERVER_USER=$(grep -E "^\s*username:" "$CONFIG_FILE" | head -1 | sed 's/.*:\s*"\([^"]*\)".*/\1/')
    SERVER_PORT=$(grep -E "^\s*port:" "$CONFIG_FILE" | head -1 | sed 's/.*:\s*\([0-9]*\).*/\1/')
    REMOTE_FRONTEND_PATH=$(grep -E "^\s*frontend:" "$CONFIG_FILE" | head -1 | sed 's/.*:\s*"\([^"]*\)".*/\1/')
fi

# 使用默认值（如果配置未读取到）
SERVER_HOST=${SERVER_HOST:-$DEFAULT_SERVER_HOST}
SERVER_USER=${SERVER_USER:-$DEFAULT_SERVER_USER}
SERVER_PORT=${SERVER_PORT:-$DEFAULT_SERVER_PORT}
REMOTE_FRONTEND_PATH=${REMOTE_FRONTEND_PATH:-$DEFAULT_REMOTE_FRONTEND_PATH}

# 构建产物远程存放路径
REMOTE_STANDALONE_PATH="${REMOTE_FRONTEND_PATH}/.next/standalone"

# 显示配置
echo "========================================="
echo "XXM Fans Home 部署配置"
echo "========================================="
echo -e "服务器地址: ${BLUE}${SERVER_HOST}:${SERVER_PORT}${NC}"
echo -e "服务器用户: ${BLUE}${SERVER_USER}${NC}"
echo -e "远程路径:   ${BLUE}${REMOTE_FRONTEND_PATH}${NC}"
echo ""

# 检查参数
SKIP_BUILD=false
if [ "$1" == "--skip-build" ]; then
    SKIP_BUILD=true
    echo -e "${YELLOW}跳过构建步骤，使用现有构建产物${NC}"
fi

# 询问确认
echo -n "是否继续部署? (y/n): "
read -r confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo -e "${YELLOW}已取消部署${NC}"
    exit 0
fi

echo ""

# 步骤 1: 本地构建
if [ "$SKIP_BUILD" = false ]; then
    echo "========================================="
    echo "步骤 1/4: 本地构建前端"
    echo "========================================="
    
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
    
    # 复制 public 目录到 standalone
    echo "复制静态资源..."
    cp -r public .next/standalone/
    
    # 验证关键文件
    if [ ! -f ".next/standalone/server.js" ]; then
        echo -e "${RED}错误: 构建产物 server.js 不存在${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}✓ 本地构建完成${NC}"
else
    # 验证现有构建产物
    if [ ! -d "$LOCAL_BUILD_PATH" ]; then
        echo -e "${RED}错误: 构建产物不存在，请先运行构建${NC}"
        exit 1
    fi
    echo -e "${GREEN}✓ 使用现有构建产物${NC}"
fi

echo ""

# 步骤 2: 上传到服务器
echo "========================================="
echo "步骤 2/4: 上传构建产物到服务器"
echo "========================================="

# 检查 ssh 连接
echo "测试 SSH 连接..."
if ! ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no -p "$SERVER_PORT" "${SERVER_USER}@${SERVER_HOST}" "echo 'SSH OK'" > /dev/null 2>&1; then
    echo -e "${RED}错误: 无法连接到服务器${NC}"
    echo "请确保:"
    echo "  1. SSH 密钥已配置: ssh-copy-id ${SERVER_USER}@${SERVER_HOST}"
    echo "  2. 服务器地址和端口正确"
    exit 1
fi
echo -e "${GREEN}✓ SSH 连接正常${NC}"

# 创建远程备份（保留最近3个版本）
echo "创建远程备份..."
BACKUP_DIR="${REMOTE_FRONTEND_PATH}/.next/backups"
ssh -p "$SERVER_PORT" "${SERVER_USER}@${SERVER_HOST}" "
    mkdir -p ${BACKUP_DIR}
    if [ -d ${REMOTE_STANDALONE_PATH} ]; then
        BACKUP_NAME=\"standalone_\$(date +%Y%m%d_%H%M%S)\"
        cp -r ${REMOTE_STANDALONE_PATH} ${BACKUP_DIR}/\${BACKUP_NAME}
        # 只保留最近3个备份
        ls -t ${BACKUP_DIR} | tail -n +4 | xargs -I {} rm -rf ${BACKUP_DIR}/{} 2>/dev/null || true
        echo \"备份完成: \${BACKUP_NAME}\"
    fi
"

# 清理远程旧构建
echo "清理远程旧构建..."
ssh -p "$SERVER_PORT" "${SERVER_USER}@${SERVER_HOST}" "rm -rf ${REMOTE_STANDALONE_PATH}"

# 上传新构建
echo "上传构建产物（这可能需要几分钟）..."
rsync -avz --progress \
    -e "ssh -p ${SERVER_PORT}" \
    --exclude='node_modules' \
    --exclude='.git' \
    "${LOCAL_BUILD_PATH}/" \
    "${SERVER_USER}@${SERVER_HOST}:${REMOTE_STANDALONE_PATH}/"

if [ $? -ne 0 ]; then
    echo -e "${RED}错误: 上传失败${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 上传完成${NC}"

echo ""

# 步骤 3: 重启服务
echo "========================================="
echo "步骤 3/4: 重启服务器服务"
echo "========================================="

# 在服务器上执行部署命令
ssh -p "$SERVER_PORT" "${SERVER_USER}@${SERVER_HOST}" "
    set -e
    echo '检查 Next.js 服务状态...'
    
    # 查找并停止现有的 Next.js 进程
    NEXT_PID=\$(pgrep -f 'next-server' || echo '')
    if [ -n \"\$NEXT_PID\" ]; then
        echo '停止现有 Next.js 服务...'
        kill \$NEXT_PID 2>/dev/null || true
        sleep 2
    fi
    
    # 启动新的 Next.js 服务
    echo '启动 Next.js 服务...'
    cd ${REMOTE_STANDALONE_PATH}
    nohup node server.js > /tmp/nextjs.log 2>&1 &
    sleep 2
    
    # 检查服务是否启动成功
    NEW_PID=\$(pgrep -f 'next-server' || echo '')
    if [ -n \"\$NEW_PID\" ]; then
        echo \"Next.js 服务已启动 (PID: \$NEW_PID)\"
    else
        echo '错误: Next.js 服务启动失败'
        exit 1
    fi
    
    echo 'Next.js 服务重启完成'
"

if [ $? -ne 0 ]; then
    echo -e "${RED}错误: 服务重启失败${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 服务重启完成${NC}"

echo ""

# 步骤 4: 重载 Nginx
echo "========================================="
echo "步骤 4/4: 重载 Nginx 配置"
echo "========================================="

ssh -p "$SERVER_PORT" "${SERVER_USER}@${SERVER_HOST}" "
    # 测试 Nginx 配置
    echo '测试 Nginx 配置...'
    if sudo nginx -t; then
        echo '配置测试通过，重载 Nginx...'
        sudo nginx -s reload
        echo 'Nginx 重载完成'
    else
        echo '错误: Nginx 配置测试失败'
        exit 1
    fi
"

if [ $? -ne 0 ]; then
    echo -e "${RED}错误: Nginx 重载失败${NC}"
    exit 1
fi

echo -e "${GREEN}✓ Nginx 重载完成${NC}"

echo ""
echo "========================================="
echo -e "${GREEN}部署成功！${NC}"
echo "========================================="
echo ""
echo "访问地址:"
echo "  - 主站: http://${SERVER_HOST}/"
echo ""
echo "查看日志:"
echo "  ssh -p ${SERVER_PORT} ${SERVER_USER}@${SERVER_HOST} 'tail -f /tmp/nextjs.log'"
echo ""
echo "回滚命令（如需要）:"
echo "  ssh -p ${SERVER_PORT} ${SERVER_USER}@${SERVER_HOST} 'ls -la ${BACKUP_DIR}'"
echo ""
