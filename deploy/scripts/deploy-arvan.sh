#!/bin/bash
#═══════════════════════════════════════════════════════════════════════════════
# ADONIS Persian Site - Full Deployment Script for Arvan Cloud
# 
# این اسکریپت را روی سرور ابرآروان اجرا کن:
#   ssh ubuntu@37.152.186.190
#   curl -sSL https://raw.githubusercontent.com/maisamsabour-gif/adoniss.gr/main/deploy/scripts/deploy-arvan.sh | sudo bash
#
# یا فایل را کپی کن و اجرا کن:
#   scp deploy-arvan.sh ubuntu@37.152.186.190:~/
#   ssh ubuntu@37.152.186.190 "sudo bash deploy-arvan.sh"
#═══════════════════════════════════════════════════════════════════════════════

set -e

# ─── Configuration ────────────────────────────────────────────────────────────
PROJECT_NAME="adonis"
DOMAIN="adonis.gr"
WWW_DOMAIN="www.adonis.gr"
GIT_REPO="git@github.com:maisamsabour-gif/adoniss.gr.git"
PROJECT_DIR="/var/www/adonis-fa"
VENV_DIR="$PROJECT_DIR/venv"
USER="www-data"
DB_NAME="adonis_prod"
DB_USER="adonis_user"
DB_PASS="$(openssl rand -base64 24 | tr -dc 'a-zA-Z0-9' | head -c 24)"
SECRET_KEY="$(openssl rand -base64 48 | tr -dc 'a-zA-Z0-9_-' | head -c 64)"
SERVER_IP="37.152.186.190"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

log() { echo -e "${GREEN}[✓]${NC} $1"; }
warn() { echo -e "${YELLOW}[!]${NC} $1"; }
error() { echo -e "${RED}[✗]${NC} $1"; exit 1; }
step() { echo -e "\n${BLUE}═══════════════════════════════════════════════════════════════${NC}"; echo -e "${BLUE}   $1${NC}"; echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}\n"; }

# ─── Check Root ───────────────────────────────────────────────────────────────
if [ "$EUID" -ne 0 ]; then
    error "این اسکریپت باید با sudo اجرا شود"
fi

step "1/9 - بروزرسانی سیستم و نصب پیش‌نیازها"

apt update && apt upgrade -y

apt install -y \
    python3 python3-pip python3-venv python3-dev \
    git nginx certbot python3-certbot-nginx \
    postgresql postgresql-contrib libpq-dev \
    build-essential libffi-dev libssl-dev \
    curl wget htop ufw fail2ban

log "پیش‌نیازها نصب شدند"

step "2/9 - تنظیم فایروال"

ufw default deny incoming
ufw default allow outgoing
ufw allow ssh
ufw allow http
ufw allow https
ufw --force enable

log "فایروال تنظیم شد"

step "3/9 - تنظیم PostgreSQL"

sudo -u postgres psql -c "SELECT 1 FROM pg_user WHERE usename = '$DB_USER'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';"

sudo -u postgres psql -c "SELECT 1 FROM pg_database WHERE datname = '$DB_NAME'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;"

sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;"

log "PostgreSQL تنظیم شد"
log "Database: $DB_NAME"
log "User: $DB_USER"
log "Password: $DB_PASS"

step "4/9 - کلون پروژه از Git"

mkdir -p /var/www
if [ -d "$PROJECT_DIR" ]; then
    warn "پوشه پروژه وجود دارد، pull می‌کنم..."
    cd "$PROJECT_DIR"
    git pull origin main || git pull origin master
else
    log "کلون پروژه..."
    git clone "$GIT_REPO" "$PROJECT_DIR"
fi

cd "$PROJECT_DIR"
log "پروژه در $PROJECT_DIR کلون شد"

step "5/9 - ساخت Virtual Environment و نصب Dependencies"

python3 -m venv "$VENV_DIR"
source "$VENV_DIR/bin/activate"

pip install --upgrade pip wheel setuptools
pip install -r requirements.txt
pip install gunicorn psycopg2-binary

log "Dependencies نصب شدند"

step "6/9 - ساخت فایل .env"

cat > "$PROJECT_DIR/.env" << EOF
# Production Environment - Generated $(date)
ENV=production
DEBUG=0
DJANGO_SECRET_KEY=$SECRET_KEY

ALLOWED_HOSTS=$DOMAIN,$WWW_DOMAIN,$SERVER_IP,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://$DOMAIN,https://$WWW_DOMAIN,http://$SERVER_IP

# Database
DB_ENGINE=postgres
POSTGRES_DB=$DB_NAME
POSTGRES_USER=$DB_USER
POSTGRES_PASSWORD=$DB_PASS
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432
POSTGRES_CONN_MAX_AGE=120
DB_ENV_TAG=production

# Media
USE_S3_MEDIA=0

# Backup
BACKUP_LOCAL_DIR=$PROJECT_DIR/backups
BACKUP_RETENTION_DAYS=30
BACKUP_REQUIRE_OFFSITE=0

# Security
SECURE_HSTS_SECONDS=31536000

# Telegram
TELEGRAM_SOURCE_LABEL=🇮🇷 سایت فارسی adonis.gr

# API Keys (fill these manually)
OPENAI_API_KEY=
ANTHROPIC_API_KEY=
GOOGLE_MAPS_API_KEY=
TELEGRAM_BOT_TOKEN=
TELEGRAM_CHAT_ID=
EOF

chmod 600 "$PROJECT_DIR/.env"
log "فایل .env ساخته شد"

step "7/9 - اجرای Migrations و Collectstatic"

cd "$PROJECT_DIR"
source "$VENV_DIR/bin/activate"

mkdir -p "$PROJECT_DIR/logs"
mkdir -p "$PROJECT_DIR/backups"
mkdir -p "$PROJECT_DIR/staticfiles"
mkdir -p "$PROJECT_DIR/media"

python manage.py migrate --noinput
python manage.py collectstatic --noinput --clear

log "Migrations و Static files انجام شد"

step "8/9 - تنظیم Gunicorn با systemd"

cat > /etc/systemd/system/adonis.service << EOF
[Unit]
Description=Adonis Persian Site Gunicorn Daemon
After=network.target postgresql.service
Wants=postgresql.service

[Service]
User=root
Group=root
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$VENV_DIR/bin:/usr/local/bin:/usr/bin:/bin"
EnvironmentFile=$PROJECT_DIR/.env
ExecStart=$VENV_DIR/bin/gunicorn adonis.wsgi:application \\
    --bind 127.0.0.1:8000 \\
    --workers 3 \\
    --threads 2 \\
    --timeout 60 \\
    --access-logfile $PROJECT_DIR/logs/gunicorn-access.log \\
    --error-logfile $PROJECT_DIR/logs/gunicorn-error.log
ExecReload=/bin/kill -s HUP \$MAINPID
KillMode=mixed
TimeoutStopSec=30
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable adonis
systemctl start adonis
sleep 3

if systemctl is-active --quiet adonis; then
    log "سرویس Gunicorn فعال شد"
else
    error "سرویس Gunicorn شروع نشد!"
fi

step "9/9 - تنظیم Nginx"

cat > /etc/nginx/sites-available/adonis.gr << EOF
upstream adonis_app {
    server 127.0.0.1:8000;
    keepalive 16;
}

# Redirect www to non-www
server {
    listen 80;
    listen [::]:80;
    server_name www.$DOMAIN;
    return 301 http://$DOMAIN\$request_uri;
}

# Main server
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN $SERVER_IP;

    client_max_body_size 64M;
    charset utf-8;

    access_log /var/log/nginx/adonis.access.log;
    error_log  /var/log/nginx/adonis.error.log;

    # Proxy settings
    proxy_http_version 1.1;
    proxy_set_header Host \$host;
    proxy_set_header X-Real-IP \$remote_addr;
    proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
    proxy_set_header X-Forwarded-Proto \$scheme;
    proxy_set_header Connection "";
    proxy_redirect off;

    # Static files
    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    # Media files
    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 7d;
        add_header Cache-Control "public";
    }

    # Django app
    location / {
        proxy_pass http://adonis_app;
    }
}
EOF

rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/adonis.gr /etc/nginx/sites-enabled/

nginx -t && systemctl reload nginx

log "Nginx تنظیم شد"

# ─── Summary ──────────────────────────────────────────────────────────────────
step "✅ نصب کامل شد!"

echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${GREEN}   اطلاعات مهم - این‌ها را ذخیره کن!${NC}"
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "📂 مسیر پروژه:     ${YELLOW}$PROJECT_DIR${NC}"
echo -e "🔑 Secret Key:     ${YELLOW}$SECRET_KEY${NC}"
echo -e "🗄️  Database:       ${YELLOW}$DB_NAME${NC}"
echo -e "👤 DB User:        ${YELLOW}$DB_USER${NC}"
echo -e "🔒 DB Password:    ${YELLOW}$DB_PASS${NC}"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   دستورات مفید${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "وضعیت سرویس‌ها:    ${YELLOW}systemctl status adonis nginx${NC}"
echo -e "ریستارت Django:   ${YELLOW}systemctl restart adonis${NC}"
echo -e "لاگ‌ها:            ${YELLOW}tail -f $PROJECT_DIR/logs/gunicorn-error.log${NC}"
echo ""
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo -e "${BLUE}   قدم‌های بعدی${NC}"
echo -e "${BLUE}═══════════════════════════════════════════════════════════════${NC}"
echo ""
echo -e "1. ${YELLOW}DNS را تنظیم کن:${NC}"
echo -e "   A record: @ → $SERVER_IP"
echo -e "   A record: www → $SERVER_IP"
echo ""
echo -e "2. ${YELLOW}SSL را فعال کن (بعد از DNS):${NC}"
echo -e "   sudo certbot --nginx -d $DOMAIN -d $WWW_DOMAIN"
echo ""
echo -e "3. ${YELLOW}سایت را تست کن:${NC}"
echo -e "   http://$SERVER_IP/fa-new/"
echo ""
echo -e "${GREEN}═══════════════════════════════════════════════════════════════${NC}"
