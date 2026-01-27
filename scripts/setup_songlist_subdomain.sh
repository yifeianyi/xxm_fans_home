#!/bin/bash

# 模板歌单子域名配置脚本
# 用途: 快速为新歌手创建 Nginx 配置和 SSL 证书

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# 项目根目录
PROJECT_ROOT="/home/yifeianyi/Desktop/xxm_fans_home"
NGINX_TEMPLATES_DIR="$PROJECT_ROOT/infra/nginx"
NGINX_SITES_AVAILABLE="/etc/nginx/sites-available"
NGINX_SITES_ENABLED="/etc/nginx/sites-enabled"

# 显示帮助信息
show_help() {
    echo "用法: $0 <subdomain> <artist_key>"
    echo ""
    echo "参数:"
    echo "  subdomain   子域名（如: leyou, youyou）"
    echo "  artist_key  歌手配置键名（需要在 songlist/ARTIST_CONFIG 中定义）"
    echo ""
    echo "示例:"
    echo "  $0 leyou youyou"
    echo "  $0 youyou youyou"
    echo ""
    echo "功能:"
    echo "  1. 创建 Nginx 配置文件"
    echo "  2. 申请 SSL 证书"
    echo "  3. 启用 Nginx 配置"
    echo "  4. 更新前端域名配置"
    echo ""
    echo "注意事项:"
    echo "  - 需要 root 权限执行"
    echo "  - 需要确保域名已解析到服务器"
    echo "  - 歌手配置需要在后端 songlist 应用中定义"
}

# 检查参数
if [ $# -ne 2 ]; then
    echo -e "${RED}错误: 缺少参数${NC}"
    show_help
    exit 1
fi

SUBDOMAIN=$1
ARTIST_KEY=$2
DOMAIN="${SUBDOMAIN}.xxm8777.cn"

echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  模板歌单子域名配置向导${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "子域名: $DOMAIN"
echo "歌手键名: $ARTIST_KEY"
echo ""

# 检查是否为 root 用户
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}错误: 请使用 root 权限运行此脚本${NC}"
    echo "使用 sudo $0 $SUBDOMAIN $ARTIST_KEY"
    exit 1
fi

# 检查模板文件是否存在
TEMPLATE_FILE="$NGINX_TEMPLATES_DIR/songlist-template.conf"
if [ ! -f "$TEMPLATE_FILE" ]; then
    echo -e "${RED}错误: 模板文件不存在: $TEMPLATE_FILE${NC}"
    exit 1
fi

# 检查配置是否已存在
NGINX_CONF_FILE="$NGINX_SITES_AVAILABLE/${SUBDOMAIN}-songlist.conf"
if [ -f "$NGINX_CONF_FILE" ]; then
    echo -e "${YELLOW}警告: Nginx 配置文件已存在: $NGINX_CONF_FILE${NC}"
    read -p "是否覆盖? (y/N): " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "操作已取消"
        exit 0
    fi
fi

# 创建 Nginx 配置
echo -e "${YELLOW}[1/5] 创建 Nginx 配置文件...${NC}"
sed "s/{{DOMAIN}}/$DOMAIN/g" "$TEMPLATE_FILE" > "$NGINX_CONF_FILE"
echo -e "${GREEN}✓ 配置文件已创建: $NGINX_CONF_FILE${NC}"

# 申请 SSL 证书
echo -e "${YELLOW}[2/5] 申请 SSL 证书...${NC}"
echo "请确保域名 $DOMAIN 已正确解析到服务器"
read -p "继续申请 SSL 证书? (Y/n): " -n 1 -r
echo
if [[ $REPLY =~ ^[Nn]$ ]]; then
    echo "跳过 SSL 证书申请"
else
    if certbot --nginx -d "$DOMAIN" --non-interactive --agree-tos --redirect; then
        echo -e "${GREEN}✓ SSL 证书申请成功${NC}"
    else
        echo -e "${RED}错误: SSL 证书申请失败${NC}"
        echo "请手动检查域名解析和 Certbot 配置"
        exit 1
    fi
fi

# 启用 Nginx 配置
echo -e "${YELLOW}[3/5] 启用 Nginx 配置...${NC}"
ln -sf "$NGINX_CONF_FILE" "$NGINX_SITES_ENABLED/"
if nginx -t; then
    systemctl reload nginx
    echo -e "${GREEN}✓ Nginx 配置已启用并重载${NC}"
else
    echo -e "${RED}错误: Nginx 配置测试失败${NC}"
    exit 1
fi

# 更新前端域名配置
echo -e "${YELLOW}[4/5] 更新前端域名配置...${NC}"
FRONTEND_ENV_FILE="$PROJECT_ROOT/repo/TempSongListFrontend/.env"
if [ -f "$FRONTEND_ENV_FILE" ]; then
    # 检查是否已存在该域名配置
    if grep -q "^${DOMAIN}=" "$FRONTEND_ENV_FILE"; then
        echo -e "${YELLOW}域名配置已存在，更新歌手键名${NC}"
        sed -i "s/^${DOMAIN}=.*/${DOMAIN}=${ARTIST_KEY}/" "$FRONTEND_ENV_FILE"
    else
        echo "${DOMAIN}=${ARTIST_KEY}" >> "$FRONTEND_ENV_FILE"
    fi
    echo -e "${GREEN}✓ 前端域名配置已更新${NC}"
else
    echo -e "${YELLOW}警告: 前端环境变量文件不存在: $FRONTEND_ENV_FILE${NC}"
    echo "请手动添加以下配置:"
    echo "${DOMAIN}=${ARTIST_KEY}"
fi

# 提示 DNS 配置
echo -e "${YELLOW}[5/5] 检查 DNS 配置...${NC}"
echo "请确保已在域名服务商处添加以下 DNS 记录:"
echo ""
echo "类型: A"
echo "主机记录: $SUBDOMAIN"
echo "记录值: $(curl -s ifconfig.me)"
echo "TTL: 600"
echo ""

# 验证配置
echo -e "${GREEN}========================================${NC}"
echo -e "${GREEN}  配置完成!${NC}"
echo -e "${GREEN}========================================${NC}"
echo ""
echo "配置摘要:"
echo "  子域名: $DOMAIN"
echo "  歌手键名: $ARTIST_KEY"
echo "  Nginx 配置: $NGINX_CONF_FILE"
echo "  SSL 证书: /etc/letsencrypt/live/$DOMAIN/"
echo ""
echo "后续步骤:"
echo "  1. 等待 DNS 生效（通常 10-30 分钟）"
echo "  2. 访问 https://$DOMAIN 测试"
echo "  3. 在后端 Admin 中配置该歌手的歌曲数据"
echo "  4. 重新构建前端（如需要）: cd repo/TempSongListFrontend && npm run build"
echo ""
echo "常用命令:"
echo "  查看 Nginx 状态: sudo systemctl status nginx"
echo "  查看 SSL 证书: sudo certbot certificates"
echo "  查看 Nginx 日志: sudo tail -f /var/log/nginx/access.log"
echo ""