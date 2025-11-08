#!/bin/bash
###############################################################################
# Nginx + HTTPS 自动配置脚本
# 配置域名、反向代理、SSL 证书
###############################################################################

set -e

# 颜色输出
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log() {
    echo -e "${GREEN}[$(date +'%H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1"
    exit 1
}

warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

# ============================================================================
# 检查是否以 root 运行
# ============================================================================

if [ "$EUID" -ne 0 ]; then
    error "请使用 sudo 运行此脚本: sudo bash setup-nginx.sh"
fi

# ============================================================================
# 获取配置信息
# ============================================================================

echo "========================================="
echo "Nginx + HTTPS 配置向导"
echo "========================================="
echo ""

read -p "请输入域名（例如：timecapsule.example.com）: " DOMAIN_NAME
read -p "是否配置 www 子域名？(y/n): " SETUP_WWW
read -p "FastAPI 运行端口（默认 8000）: " APP_PORT
APP_PORT=${APP_PORT:-8000}

read -p "是否配置 SSL 证书（Let's Encrypt）？(y/n): " SETUP_SSL
if [ "$SETUP_SSL" = "y" ]; then
    read -p "请输入邮箱（用于 SSL 证书通知）: " EMAIL
fi

echo ""
echo "========================================="
echo "配置信息确认："
echo "========================================="
echo "域名: $DOMAIN_NAME"
[ "$SETUP_WWW" = "y" ] && echo "WWW 子域名: www.$DOMAIN_NAME"
echo "应用端口: $APP_PORT"
echo "SSL 证书: $SETUP_SSL"
[ "$SETUP_SSL" = "y" ] && echo "邮箱: $EMAIL"
echo "========================================="
echo ""

read -p "确认配置无误？(y/n): " CONFIRM
if [ "$CONFIRM" != "y" ]; then
    error "配置已取消"
fi

# ============================================================================
# 安装 Nginx
# ============================================================================

log "检查 Nginx 安装状态..."

if ! command -v nginx &> /dev/null; then
    log "安装 Nginx..."
    apt update
    apt install nginx -y
else
    log "Nginx 已安装"
fi

# 启动 Nginx
systemctl start nginx
systemctl enable nginx

# ============================================================================
# 配置 Nginx
# ============================================================================

log "创建 Nginx 配置..."

CONFIG_FILE="/etc/nginx/sites-available/$DOMAIN_NAME"

# 构建 server_name
if [ "$SETUP_WWW" = "y" ]; then
    SERVER_NAME="$DOMAIN_NAME www.$DOMAIN_NAME"
else
    SERVER_NAME="$DOMAIN_NAME"
fi

# 创建配置文件
cat > "$CONFIG_FILE" <<EOF
# 时光胶囊项目 Nginx 配置
# 域名: $DOMAIN_NAME
# 生成时间: $(date)

server {
    listen 80;
    server_name $SERVER_NAME;

    # 日志
    access_log /var/log/nginx/${DOMAIN_NAME}-access.log;
    error_log /var/log/nginx/${DOMAIN_NAME}-error.log;

    # 客户端最大请求体大小（支持文件上传）
    client_max_body_size 50M;

    # 反向代理到 FastAPI 应用
    location / {
        proxy_pass http://127.0.0.1:${APP_PORT};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;

        # 超时设置
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;

        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection "upgrade";
    }

    # API 文档
    location /docs {
        proxy_pass http://127.0.0.1:${APP_PORT}/docs;
        proxy_set_header Host \$host;
    }

    location /redoc {
        proxy_pass http://127.0.0.1:${APP_PORT}/redoc;
        proxy_set_header Host \$host;
    }

    # 健康检查（不记录日志）
    location /health {
        proxy_pass http://127.0.0.1:${APP_PORT}/health;
        access_log off;
    }

    # OpenAPI JSON
    location /openapi.json {
        proxy_pass http://127.0.0.1:${APP_PORT}/openapi.json;
    }
}
EOF

log "配置文件已创建: $CONFIG_FILE"

# 启用站点
ln -sf "$CONFIG_FILE" "/etc/nginx/sites-enabled/"

# 删除默认站点（如果存在）
if [ -f /etc/nginx/sites-enabled/default ]; then
    rm /etc/nginx/sites-enabled/default
    log "已删除默认站点配置"
fi

# 测试配置
log "测试 Nginx 配置..."
nginx -t || error "Nginx 配置测试失败"

# 重载 Nginx
log "重载 Nginx..."
systemctl reload nginx

# ============================================================================
# 配置防火墙
# ============================================================================

log "配置防火墙..."

if command -v ufw &> /dev/null; then
    ufw allow 'Nginx Full'
    log "防火墙规则已添加"
else
    warn "未检测到 ufw，请手动配置防火墙允许 80 和 443 端口"
fi

# ============================================================================
# 配置 SSL 证书
# ============================================================================

if [ "$SETUP_SSL" = "y" ]; then
    log "配置 SSL 证书..."

    # 安装 Certbot
    if ! command -v certbot &> /dev/null; then
        log "安装 Certbot..."
        apt install certbot python3-certbot-nginx -y
    fi

    # 获取证书
    log "获取 Let's Encrypt 证书..."

    if [ "$SETUP_WWW" = "y" ]; then
        certbot --nginx -d "$DOMAIN_NAME" -d "www.$DOMAIN_NAME" \
            --non-interactive --agree-tos --email "$EMAIL" \
            --redirect || warn "SSL 证书配置失败，请检查域名 DNS 是否正确指向本服务器"
    else
        certbot --nginx -d "$DOMAIN_NAME" \
            --non-interactive --agree-tos --email "$EMAIL" \
            --redirect || warn "SSL 证书配置失败，请检查域名 DNS 是否正确指向本服务器"
    fi

    # 测试自动续期
    log "测试证书自动续期..."
    certbot renew --dry-run || warn "证书续期测试失败"
fi

# ============================================================================
# 完成
# ============================================================================

echo ""
echo "========================================="
echo "✅ 配置完成！"
echo "========================================="
echo ""
echo "访问地址："

if [ "$SETUP_SSL" = "y" ]; then
    echo "  https://$DOMAIN_NAME"
    [ "$SETUP_WWW" = "y" ] && echo "  https://www.$DOMAIN_NAME"
    echo ""
    echo "API 文档："
    echo "  https://$DOMAIN_NAME/docs"
    echo "  https://$DOMAIN_NAME/redoc"
else
    echo "  http://$DOMAIN_NAME"
    [ "$SETUP_WWW" = "y" ] && echo "  http://www.$DOMAIN_NAME"
    echo ""
    echo "API 文档："
    echo "  http://$DOMAIN_NAME/docs"
    echo "  http://$DOMAIN_NAME/redoc"
fi

echo ""
echo "配置文件位置："
echo "  $CONFIG_FILE"
echo ""
echo "日志文件："
echo "  /var/log/nginx/${DOMAIN_NAME}-access.log"
echo "  /var/log/nginx/${DOMAIN_NAME}-error.log"
echo ""
echo "常用命令："
echo "  sudo nginx -t                    # 测试配置"
echo "  sudo systemctl reload nginx      # 重载配置"
echo "  sudo systemctl status nginx      # 查看状态"
echo "  sudo certbot renew              # 手动续期证书"
echo ""
echo "⚠️  注意事项："
echo "  1. 确保域名 DNS 已正确解析到本服务器 IP"
echo "  2. 确保 FastAPI 应用运行在端口 $APP_PORT"
echo "  3. SSL 证书每 90 天自动续期"
echo ""
echo "========================================="
