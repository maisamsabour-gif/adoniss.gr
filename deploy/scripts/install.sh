#!/bin/bash
#═══════════════════════════════════════════════════════════════════════════════
#  🇮🇷  نصب یک‌کلیکی سایت ادونیس روی ابرآروان
#
#  فقط این دستور را روی سرور اجرا کن:
#
#    curl -sSL https://raw.githubusercontent.com/maisamsabour-gif/adoniss.gr/main/deploy/scripts/install.sh | sudo bash
#
#═══════════════════════════════════════════════════════════════════════════════

set -e

# ─── رنگ‌ها ───
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

# ─── تنظیمات ───
DOMAIN="adoniss.gr"
PROJECT_DIR="/var/www/adoniss"
GIT_REPO="https://github.com/maisamsabour-gif/adoniss.gr.git"
DB_NAME="adoniss_db"
DB_USER="adoniss_user"
DB_PASS="$(openssl rand -base64 18 | tr -dc 'a-zA-Z0-9' | head -c 20)"
SECRET_KEY="$(openssl rand -base64 48 | tr -dc 'a-zA-Z0-9_-' | head -c 64)"
SERVER_IP=$(curl -s ifconfig.me 2>/dev/null || hostname -I | awk '{print $1}')

clear
echo ""
echo -e "${CYAN}╔═══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${CYAN}║                                                                   ║${NC}"
echo -e "${CYAN}║   🏛️  نصب‌کننده خودکار سایت ادونیس فارسی                          ║${NC}"
echo -e "${CYAN}║                                                                   ║${NC}"
echo -e "${CYAN}╚═══════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "   ${YELLOW}دامنه:${NC}     $DOMAIN"
echo -e "   ${YELLOW}IP سرور:${NC}   $SERVER_IP"
echo ""

# ─── بررسی روت ───
if [ "$EUID" -ne 0 ]; then
    echo -e "${RED}❌ این اسکریپت باید با sudo اجرا شود${NC}"
    echo -e "   دستور صحیح: ${YELLOW}sudo bash install.sh${NC}"
    exit 1
fi

log() { echo -e "${GREEN}✓${NC} $1"; }
warn() { echo -e "${YELLOW}!${NC} $1"; }
step() { echo -e "\n${BLUE}━━━ $1 ━━━${NC}\n"; }

# ═══════════════════════════════════════════════════════════════════════════════
step "مرحله ۱/۸: نصب پیش‌نیازها"
# ═══════════════════════════════════════════════════════════════════════════════

apt update -qq
apt install -y -qq \
    python3 python3-pip python3-venv python3-dev \
    git nginx certbot python3-certbot-nginx \
    postgresql postgresql-contrib libpq-dev \
    build-essential curl > /dev/null 2>&1

log "پیش‌نیازها نصب شدند"

# ═══════════════════════════════════════════════════════════════════════════════
step "مرحله ۲/۸: تنظیم فایروال"
# ═══════════════════════════════════════════════════════════════════════════════

ufw allow ssh > /dev/null 2>&1 || true
ufw allow http > /dev/null 2>&1 || true
ufw allow https > /dev/null 2>&1 || true
ufw --force enable > /dev/null 2>&1 || true

log "فایروال تنظیم شد"

# ═══════════════════════════════════════════════════════════════════════════════
step "مرحله ۳/۸: تنظیم دیتابیس PostgreSQL"
# ═══════════════════════════════════════════════════════════════════════════════

systemctl start postgresql
systemctl enable postgresql > /dev/null 2>&1

sudo -u postgres psql -tc "SELECT 1 FROM pg_roles WHERE rolname='$DB_USER'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE USER $DB_USER WITH PASSWORD '$DB_PASS';" > /dev/null 2>&1

sudo -u postgres psql -tc "SELECT 1 FROM pg_database WHERE datname='$DB_NAME'" | grep -q 1 || \
    sudo -u postgres psql -c "CREATE DATABASE $DB_NAME OWNER $DB_USER;" > /dev/null 2>&1

sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" > /dev/null 2>&1

log "دیتابیس $DB_NAME ساخته شد"

# ═══════════════════════════════════════════════════════════════════════════════
step "مرحله ۴/۸: دانلود پروژه از GitHub"
# ═══════════════════════════════════════════════════════════════════════════════

mkdir -p /var/www

if [ -d "$PROJECT_DIR" ]; then
    warn "پوشه قبلی پیدا شد، آپدیت می‌کنم..."
    cd "$PROJECT_DIR"
    git pull origin main 2>/dev/null || git pull origin master 2>/dev/null || true
else
    git clone "$GIT_REPO" "$PROJECT_DIR"
    log "پروژه دانلود شد"
fi

cd "$PROJECT_DIR"

# ═══════════════════════════════════════════════════════════════════════════════
step "مرحله ۵/۸: نصب کتابخانه‌های پایتون"
# ═══════════════════════════════════════════════════════════════════════════════

python3 -m venv venv
source venv/bin/activate

pip install --upgrade pip wheel setuptools -q
pip install -r requirements.txt -q
pip install gunicorn psycopg2-binary -q

log "کتابخانه‌ها نصب شدند"

# ═══════════════════════════════════════════════════════════════════════════════
step "مرحله ۶/۸: تنظیم فایل پیکربندی"
# ═══════════════════════════════════════════════════════════════════════════════

cat > "$PROJECT_DIR/.env" << EOF
ENV=production
DEBUG=0
DJANGO_SECRET_KEY=$SECRET_KEY

ALLOWED_HOSTS=$DOMAIN,www.$DOMAIN,$SERVER_IP,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://$DOMAIN,https://www.$DOMAIN,http://$SERVER_IP

DB_ENGINE=postgres
POSTGRES_DB=$DB_NAME
POSTGRES_USER=$DB_USER
POSTGRES_PASSWORD=$DB_PASS
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432

USE_S3_MEDIA=0
BACKUP_LOCAL_DIR=$PROJECT_DIR/backups
TELEGRAM_SOURCE_LABEL=🇮🇷 سایت فارسی $DOMAIN
EOF

chmod 600 "$PROJECT_DIR/.env"
log "فایل تنظیمات ساخته شد"

# ═══════════════════════════════════════════════════════════════════════════════
step "مرحله ۷/۸: آماده‌سازی دیتابیس و فایل‌ها"
# ═══════════════════════════════════════════════════════════════════════════════

mkdir -p logs backups staticfiles media

source venv/bin/activate
python manage.py migrate --noinput > /dev/null 2>&1
python manage.py collectstatic --noinput --clear > /dev/null 2>&1

log "دیتابیس و فایل‌های استاتیک آماده شدند"

# ═══════════════════════════════════════════════════════════════════════════════
step "مرحله ۸/۸: راه‌اندازی سرویس‌ها"
# ═══════════════════════════════════════════════════════════════════════════════

# Gunicorn Service
cat > /etc/systemd/system/adoniss.service << EOF
[Unit]
Description=Adoniss Persian Site
After=network.target postgresql.service

[Service]
User=root
WorkingDirectory=$PROJECT_DIR
Environment="PATH=$PROJECT_DIR/venv/bin"
ExecStart=$PROJECT_DIR/venv/bin/gunicorn adonis.wsgi:application --bind 127.0.0.1:8000 --workers 3
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable adoniss > /dev/null 2>&1
systemctl restart adoniss

# Nginx Config
cat > /etc/nginx/sites-available/adoniss << EOF
server {
    listen 80;
    server_name $DOMAIN www.$DOMAIN $SERVER_IP;

    client_max_body_size 64M;

    location /static/ {
        alias $PROJECT_DIR/staticfiles/;
        expires 30d;
    }

    location /media/ {
        alias $PROJECT_DIR/media/;
        expires 7d;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }
}
EOF

rm -f /etc/nginx/sites-enabled/default
ln -sf /etc/nginx/sites-available/adoniss /etc/nginx/sites-enabled/

nginx -t > /dev/null 2>&1 && systemctl reload nginx

log "سرویس‌ها راه‌اندازی شدند"

# ═══════════════════════════════════════════════════════════════════════════════
# خلاصه
# ═══════════════════════════════════════════════════════════════════════════════

echo ""
echo -e "${GREEN}╔═══════════════════════════════════════════════════════════════════╗${NC}"
echo -e "${GREEN}║                                                                   ║${NC}"
echo -e "${GREEN}║   ✅  نصب با موفقیت انجام شد!                                     ║${NC}"
echo -e "${GREEN}║                                                                   ║${NC}"
echo -e "${GREEN}╚═══════════════════════════════════════════════════════════════════╝${NC}"
echo ""
echo -e "   ${CYAN}📍 آدرس سایت:${NC}"
echo -e "      http://$SERVER_IP/fa-new/"
echo ""
echo -e "   ${CYAN}🔐 اطلاعات دیتابیس (ذخیره کن!):${NC}"
echo -e "      نام:     $DB_NAME"
echo -e "      کاربر:   $DB_USER"
echo -e "      رمز:     ${YELLOW}$DB_PASS${NC}"
echo ""
echo -e "   ${CYAN}📂 مسیر پروژه:${NC}  $PROJECT_DIR"
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "   ${CYAN}قدم بعدی - تنظیم DNS:${NC}"
echo ""
echo -e "   در پنل ابرآروان، این رکوردها را اضافه کن:"
echo -e "   ${YELLOW}A    @      →   $SERVER_IP${NC}"
echo -e "   ${YELLOW}A    www    →   $SERVER_IP${NC}"
echo ""
echo -e "   ${CYAN}بعد از تنظیم DNS، SSL را فعال کن:${NC}"
echo -e "   ${YELLOW}sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN${NC}"
echo ""
echo -e "${YELLOW}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "   ${CYAN}دستورات مفید:${NC}"
echo -e "   ریستارت:  ${YELLOW}sudo systemctl restart adoniss${NC}"
echo -e "   وضعیت:    ${YELLOW}sudo systemctl status adoniss${NC}"
echo -e "   لاگ:      ${YELLOW}sudo journalctl -u adoniss -f${NC}"
echo ""
