#!/bin/bash

# =============================================================================
# 添加新歌手自动化部署脚本
# =============================================================================
# 用途: 自动化完成新歌手生产环境部署的全部步骤
# 用法: ./deploy_new_artist.sh <artist_key> <subdomain>
# 示例: ./deploy_new_artist.sh newartist newartist
# =============================================================================

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 项目路径
PROJECT_ROOT="/home/yifeianyi/Desktop/xxm_fans_home"
BACKEND_DIR="$PROJECT_ROOT/repo/xxm_fans_backend"
FRONTEND_DIR="$PROJECT_ROOT/repo/TempSongListFrontend"
SCRIPTS_DIR="$PROJECT_ROOT/scripts"

# 显示帮助信息
show_help() {
    echo "用法: $0 <artist_key> <subdomain>"
    echo ""
    echo "参数:"
    echo "  artist_key  歌手配置键名（如: eva, baojingbi）"
    echo "  subdomain   子域名前缀（如: eva, baojingbi）"
    echo ""
    echo "示例:"
    echo "  $0 eva eva"
    echo "  $0 baojingbi baojingbi"
    echo ""
    echo "注意:"
    echo "  - 需要在服务器上运行"
    echo "  - 需要 sudo 权限"
    echo "  - 执行前确保代码已提交并推送到远程仓库"
}

# 打印带颜色的信息
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 检查命令是否存在
check_command() {
    if ! command -v "$1" &> /dev/null; then
        print_error "$1 未安装"
        exit 1
    fi
}

# 检查是否为 root 或使用 sudo
check_sudo() {
    if [ "$EUID" -ne 0 ]; then
        print_error "请使用 sudo 运行此脚本"
        exit 1
    fi
}

# 检查参数
if [ $# -ne 2 ]; then
    print_error "参数错误"
    show_help
    exit 1
fi

ARTIST_KEY=$1
SUBDOMAIN=$2
DOMAIN="${SUBDOMAIN}.xxm8777.cn"

echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  添加新歌手自动化部署${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
print_info "歌手键名: $ARTIST_KEY"
print_info "子域名: $DOMAIN"
echo ""

# 检查环境
check_sudo
check_command git
check_command python3
check_command nginx
check_command certbot

# 确认提示
echo -e "${YELLOW}即将执行以下操作:${NC}"
echo "  1. 拉取后端代码更新"
echo "  2. 执行数据库迁移"
echo "  3. 配置前端域名映射 (.env)"
echo "  4. 配置 Nginx + SSL"
echo "  5. 更新 ALLOWED_HOSTS"
echo "  6. 重启后端服务"
echo ""
read -p "是否继续? (y/N): " -n 1 -r
echo
if [[ ! $REPLY =~ ^[Yy]$ ]]; then
    print_info "操作已取消"
    exit 0
fi

echo ""

# =============================================================================
# 步骤 1: 拉取后端代码更新
# =============================================================================
print_info "[1/6] 拉取后端代码更新..."
cd "$BACKEND_DIR"

# 检查是否有未提交的更改
if [ -n "$(git status --porcelain)" ]; then
    print_warning "后端代码有未提交的更改，请先提交或 stash"
    git status --short
    exit 1
fi

# 拉取最新代码
if git pull origin main; then
    print_success "后端代码更新成功"
else
    print_error "后端代码更新失败"
    exit 1
fi

# =============================================================================
# 步骤 2: 执行数据库迁移
# =============================================================================
print_info "[2/6] 执行数据库迁移..."
cd "$BACKEND_DIR"
source venv/bin/activate

# 检查歌手是否在配置中
if ! grep -q "'$ARTIST_KEY':" songlist/models.py; then
    print_error "歌手 '$ARTIST_KEY' 未在 songlist/models.py 中配置"
    print_info "请先修改 models.py 添加歌手配置，然后提交代码"
    exit 1
fi

# 执行迁移
python manage.py migrate
python manage.py migrate --database=songlist_db
print_success "数据库迁移完成"

# =============================================================================
# 步骤 3: 配置前端域名映射
# =============================================================================
print_info "[3/6] 配置前端域名映射..."
cd "$FRONTEND_DIR"

# 检查 .env 文件是否存在
if [ ! -f ".env" ]; then
    print_warning ".env 文件不存在，创建默认配置"
    cat > .env << EOF
# 模板歌单前端 - 域名映射配置
# 格式: 域名=歌手键名

leyou.xxm8777.cn=youyou
bingjie.xxm8777.cn=bingjie
${DOMAIN}=${ARTIST_KEY}

# 默认歌手
DEFAULT_ARTIST=youyou
EOF
    print_success ".env 文件已创建"
else
    # 检查是否已存在该域名配置
    if grep -q "^${DOMAIN}=" .env; then
        print_warning "域名配置已存在，更新歌手键名"
        sed -i "s/^${DOMAIN}=.*/${DOMAIN}=${ARTIST_KEY}/" .env
    else
        # 添加新配置
        echo "${DOMAIN}=${ARTIST_KEY}" >> .env
        print_success "域名映射已添加: ${DOMAIN}=${ARTIST_KEY}"
    fi
fi

# 重新构建前端
print_info "正在构建前端..."
if npm run build > /tmp/frontend_build.log 2>&1; then
    print_success "前端构建成功"
else
    print_error "前端构建失败，日志: /tmp/frontend_build.log"
    cat /tmp/frontend_build.log
    exit 1
fi

# =============================================================================
# 步骤 4: 配置 Nginx + SSL
# =============================================================================
print_info "[4/6] 配置 Nginx + SSL..."

# 检查是否已存在 Nginx 配置
NGINX_CONF="/etc/nginx/sites-available/${SUBDOMAIN}-songlist.conf"
if [ -f "$NGINX_CONF" ]; then
    print_warning "Nginx 配置已存在: $NGINX_CONF"
    read -p "是否重新配置? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        print_info "跳过 Nginx 配置"
    else
        # 删除旧配置重新配置
        rm -f "/etc/nginx/sites-enabled/${SUBDOMAIN}-songlist.conf"
        rm -f "$NGINX_CONF"
        
        # 使用 setup_songlist_subdomain.sh 脚本
        cd "$SCRIPTS_DIR"
        if [ -f "setup_songlist_subdomain.sh" ]; then
            # 脚本需要交互，使用 expect 或手动执行
            print_info "使用 setup_songlist_subdomain.sh 配置..."
            ./setup_songlist_subdomain.sh "$SUBDOMAIN" "$ARTIST_KEY"
        else
            print_error "setup_songlist_subdomain.sh 脚本不存在"
            exit 1
        fi
    fi
else
    # 使用 setup_songlist_subdomain.sh 脚本
    cd "$SCRIPTS_DIR"
    if [ -f "setup_songlist_subdomain.sh" ]; then
        print_info "使用 setup_songlist_subdomain.sh 配置..."
        ./setup_songlist_subdomain.sh "$SUBDOMAIN" "$ARTIST_KEY"
    else
        print_error "setup_songlist_subdomain.sh 脚本不存在"
        exit 1
    fi
fi

# =============================================================================
# 步骤 5: 更新 ALLOWED_HOSTS
# =============================================================================
print_info "[5/6] 更新 ALLOWED_HOSTS..."

BACKEND_ENV="$BACKEND_DIR/.env"
if [ ! -f "$BACKEND_ENV" ]; then
    print_error "后端 .env 文件不存在: $BACKEND_ENV"
    exit 1
fi

# 检查是否已存在该域名
if grep -q "$DOMAIN" "$BACKEND_ENV"; then
    print_success "域名已在 ALLOWED_HOSTS 中"
else
    # 更新 ALLOWED_HOSTS
    # 读取当前配置
    CURRENT_HOSTS=$(grep "DJANGO_ALLOWED_HOSTS=" "$BACKEND_ENV" | cut -d'=' -f2)
    
    # 添加新域名
    NEW_HOSTS="${CURRENT_HOSTS},${DOMAIN}"
    sed -i "s/DJANGO_ALLOWED_HOSTS=.*/DJANGO_ALLOWED_HOSTS=${NEW_HOSTS}/" "$BACKEND_ENV"
    
    print_success "ALLOWED_HOSTS 已更新"
    print_info "新配置: $NEW_HOSTS"
fi

# =============================================================================
# 步骤 6: 重启服务
# =============================================================================
print_info "[6/6] 重启服务..."

# 重启后端服务
systemctl restart xxm-backend.service
if systemctl is-active --quiet xxm-backend.service; then
    print_success "后端服务重启成功"
else
    print_error "后端服务重启失败"
    systemctl status xxm-backend.service --no-pager
    exit 1
fi

# 重载 Nginx
if nginx -t; then
    systemctl reload nginx
    print_success "Nginx 重载成功"
else
    print_error "Nginx 配置测试失败"
    exit 1
fi

# =============================================================================
# 部署完成
# =============================================================================
echo ""
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  部署完成!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
print_info "部署摘要:"
echo "  歌手键名: $ARTIST_KEY"
echo "  访问地址: https://$DOMAIN"
echo "  Nginx 配置: /etc/nginx/sites-available/${SUBDOMAIN}-songlist.conf"
echo ""
print_info "验证命令:"
echo "  curl https://$DOMAIN/api/songlist/site-settings/?artist=$ARTIST_KEY"
echo ""
print_warning "注意:"
echo "  - 确保 DNS 已配置并生效（A 记录: $SUBDOMAIN -> 服务器IP）"
echo "  - 在 Django Admin 中添加歌曲数据和站点设置"
echo "  - 查看日志: sudo journalctl -u xxm-backend.service -f"
echo ""
