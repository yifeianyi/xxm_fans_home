#!/bin/bash

# XXM Fans Home 后端部署脚本
# 上传后端代码到服务器并重启服务

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
DEFAULT_REMOTE_BACKEND_PATH="/home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend"

# 从配置文件读取（如果存在）
if [ -f "$CONFIG_FILE" ]; then
    SERVER_HOST=$(grep -E "^\s*host:" "$CONFIG_FILE" | head -1 | sed 's/.*:\s*"\([^"]*\)".*/\1/')
    SERVER_USER=$(grep -E "^\s*username:" "$CONFIG_FILE" | head -1 | sed 's/.*:\s*"\([^"]*\)".*/\1/')
    SERVER_PORT=$(grep -E "^\s*port:" "$CONFIG_FILE" | head -1 | sed 's/.*:\s*\([0-9]*\).*/\1/')
    REMOTE_BACKEND_PATH=$(grep -E "^\s*backend:" "$CONFIG_FILE" | head -1 | sed 's/.*:\s*"\([^"]*\)".*/\1/')
fi

# 使用默认值（如果配置未读取到）
SERVER_HOST=${SERVER_HOST:-$DEFAULT_SERVER_HOST}
SERVER_USER=${SERVER_USER:-$DEFAULT_SERVER_USER}
SERVER_PORT=${SERVER_PORT:-$DEFAULT_SERVER_PORT}
REMOTE_BACKEND_PATH=${REMOTE_BACKEND_PATH:-$DEFAULT_REMOTE_BACKEND_PATH}

# 本地路径
LOCAL_BACKEND_PATH="/home/yifeianyi/Desktop/xxm_fans_home/repo/xxm_fans_backend"

# 显示配置
echo "========================================="
echo "XXM Fans Home 后端部署"
echo "========================================="
echo -e "服务器地址: ${BLUE}${SERVER_HOST}:${SERVER_PORT}${NC}"
echo -e "服务器用户: ${BLUE}${SERVER_USER}${NC}"
echo -e "远程路径:   ${BLUE}${REMOTE_BACKEND_PATH}${NC}"
echo ""

# 解析参数
SKIP_MIGRATE=false
SKIP_STATIC=false
if [ "$1" == "--skip-migrate" ]; then
    SKIP_MIGRATE=true
    echo -e "${YELLOW}跳过数据库迁移${NC}"
fi
if [ "$2" == "--skip-static" ] || [ "$1" == "--skip-static" ]; then
    SKIP_STATIC=true
    echo -e "${YELLOW}跳过静态文件收集${NC}"
fi

# 询问确认
echo -n "是否继续部署后端? (y/n): "
read -r confirm
if [ "$confirm" != "y" ] && [ "$confirm" != "Y" ]; then
    echo -e "${YELLOW}已取消部署${NC}"
    exit 0
fi

echo ""

# 步骤 1: 上传代码
echo "========================================="
echo "步骤 1/3: 上传后端代码"
echo "========================================="

# 检查 ssh 连接
echo "测试 SSH 连接..."
if ! ssh -o ConnectTimeout=5 -o StrictHostKeyChecking=no -p "$SERVER_PORT" "${SERVER_USER}@${SERVER_HOST}" "echo 'SSH OK'" > /dev/null 2>&1; then
    echo -e "${RED}错误: 无法连接到服务器${NC}"
    exit 1
fi
echo -e "${GREEN}✓ SSH 连接正常${NC}"

# 创建远程备份
echo "创建远程备份..."
BACKUP_DIR="${REMOTE_BACKEND_PATH}/../backups"
ssh -p "$SERVER_PORT" "${SERVER_USER}@${SERVER_HOST}" "
    mkdir -p ${BACKUP_DIR}
    if [ -d ${REMOTE_BACKEND_PATH} ]; then
        BACKUP_NAME=\"backend_\$(date +%Y%m%d_%H%M%S).tar.gz\"
        tar -czf ${BACKUP_DIR}/\${BACKUP_NAME} -C ${REMOTE_BACKEND_PATH}/.. xxm_fans_backend --exclude='*.pyc' --exclude='__pycache__' --exclude='venv' 2>/dev/null || true
        # 只保留最近3个备份
        ls -t ${BACKUP_DIR} | tail -n +4 | xargs -I {} rm -f ${BACKUP_DIR}/{} 2>/dev/null || true
        echo \"备份完成: \${BACKUP_NAME}\"
    fi
"

# 上传代码（排除不需要的文件）
echo "上传后端代码..."
rsync -avz --progress \
    -e "ssh -p ${SERVER_PORT}" \
    --exclude='.git' \
    --exclude='venv' \
    --exclude='__pycache__' \
    --exclude='*.pyc' \
    --exclude='db.sqlite3' \
    --exclude='staticfiles' \
    --exclude='*.log' \
    --exclude='.env' \
    "${LOCAL_BACKEND_PATH}/" \
    "${SERVER_USER}@${SERVER_HOST}:${REMOTE_BACKEND_PATH}/"

if [ $? -ne 0 ]; then
    echo -e "${RED}错误: 上传失败${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 上传完成${NC}"

echo ""

# 步骤 2: 执行部署命令
echo "========================================="
echo "步骤 2/3: 执行服务器部署命令"
echo "========================================="

ssh -p "$SERVER_PORT" "${SERVER_USER}@${SERVER_HOST}" "
    set -e
    cd ${REMOTE_BACKEND_PATH}
    
    # 激活虚拟环境
    source venv/bin/activate
    
    # 安装依赖
    echo '安装依赖...'
    pip install -r requirements.txt -q
    
    # 数据库迁移
    if [ '$SKIP_MIGRATE' = false ]; then
        echo '执行数据库迁移...'
        python manage.py migrate
        python manage.py migrate --database=songlist_db
    else
        echo '跳过数据库迁移'
    fi
    
    # 收集静态文件
    if [ '$SKIP_STATIC' = false ]; then
        echo '收集静态文件...'
        python manage.py collectstatic --noinput --clear
    else
        echo '跳过静态文件收集'
    fi
    
    # 重启后端服务
    echo '重启后端服务...'
    sudo systemctl restart xxm-home-backend.service
    
    # 检查服务状态
    sleep 2
    if sudo systemctl is-active --quiet xxm-home-backend.service; then
        echo '后端服务重启成功'
    else
        echo '错误: 后端服务启动失败'
        sudo systemctl status xxm-home-backend.service --no-pager
        exit 1
    fi
"

if [ $? -ne 0 ]; then
    echo -e "${RED}错误: 后端部署失败${NC}"
    exit 1
fi

echo -e "${GREEN}✓ 后端部署完成${NC}"

echo ""

# 步骤 3: 重载 Nginx
echo "========================================="
echo "步骤 3/3: 重载 Nginx 配置"
echo "========================================="

ssh -p "$SERVER_PORT" "${SERVER_USER}@${SERVER_HOST}" "
    set -e
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

if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Nginx 配置重载完成${NC}"
else
    echo ""
    echo -e "${RED}✗ Nginx 重载失败${NC}"
    exit 1
fi

echo ""
echo "========================================="
echo -e "${GREEN}后端部署成功！${NC}"
echo "========================================="
echo ""
echo "查看日志:"
echo "  ssh -p ${SERVER_PORT} ${SERVER_USER}@${SERVER_HOST} 'sudo journalctl -u xxm-home-backend.service -f'"
echo ""
