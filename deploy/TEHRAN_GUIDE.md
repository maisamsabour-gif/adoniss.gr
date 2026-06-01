# 🇮🇷 راهنمای نصب برای تیم تهران

## فایل‌های لازم
1. `adonis-fa-deploy.zip` - کل پروژه
2. `database_backup.sql` - بکاپ دیتابیس (اختیاری)

---

## مرحله 1: آماده‌سازی سرور

### SSH به سرور:
```bash
ssh ubuntu@37.152.186.190
```

### نصب پیش‌نیازها:
```bash
sudo apt update && sudo apt upgrade -y

sudo apt install -y python3 python3-pip python3-venv python3-dev \
    git nginx certbot python3-certbot-nginx \
    postgresql postgresql-contrib libpq-dev \
    build-essential unzip curl
```

---

## مرحله 2: آپلود و استخراج پروژه

### از کامپیوتر خودتان:
```bash
scp adonis-fa-deploy.zip ubuntu@37.152.186.190:~/
```

### روی سرور:
```bash
sudo mkdir -p /var/www/adonis-fa
cd /var/www/adonis-fa
sudo unzip ~/adonis-fa-deploy.zip -d .
sudo chown -R root:root /var/www/adonis-fa
```

---

## مرحله 3: تنظیم دیتابیس

```bash
# ساخت یوزر و دیتابیس
sudo -u postgres psql << EOF
CREATE USER adonis_user WITH PASSWORD 'YourStrongPassword123';
CREATE DATABASE adonis_prod OWNER adonis_user;
GRANT ALL PRIVILEGES ON DATABASE adonis_prod TO adonis_user;
EOF
```

### اگر فایل backup دارید:
```bash
scp database_backup.sql ubuntu@37.152.186.190:~/
sudo -u postgres psql adonis_prod < ~/database_backup.sql
```

---

## مرحله 4: تنظیم Virtual Environment

```bash
cd /var/www/adonis-fa
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
pip install gunicorn psycopg2-binary
```

---

## مرحله 5: ساخت فایل .env

```bash
cat > /var/www/adonis-fa/.env << 'EOF'
ENV=production
DEBUG=0
DJANGO_SECRET_KEY=your-random-64-char-secret-key-here-change-this

ALLOWED_HOSTS=adonis.gr,www.adonis.gr,37.152.186.190,localhost,127.0.0.1
CSRF_TRUSTED_ORIGINS=https://adonis.gr,https://www.adonis.gr,http://37.152.186.190

DB_ENGINE=postgres
POSTGRES_DB=adonis_prod
POSTGRES_USER=adonis_user
POSTGRES_PASSWORD=YourStrongPassword123
POSTGRES_HOST=127.0.0.1
POSTGRES_PORT=5432

USE_S3_MEDIA=0
BACKUP_LOCAL_DIR=/var/www/adonis-fa/backups
TELEGRAM_SOURCE_LABEL=🇮🇷 سایت فارسی
EOF

chmod 600 /var/www/adonis-fa/.env
```

⚠️ **مهم:** `DJANGO_SECRET_KEY` و `POSTGRES_PASSWORD` را تغییر دهید!

---

## مرحله 6: Migrations و Static Files

```bash
cd /var/www/adonis-fa
source venv/bin/activate
mkdir -p logs backups staticfiles media

python manage.py migrate --noinput
python manage.py collectstatic --noinput
```

---

## مرحله 7: سرویس Gunicorn

```bash
sudo cat > /etc/systemd/system/adonis.service << 'EOF'
[Unit]
Description=Adonis Gunicorn
After=network.target

[Service]
User=root
WorkingDirectory=/var/www/adonis-fa
Environment="PATH=/var/www/adonis-fa/venv/bin"
ExecStart=/var/www/adonis-fa/venv/bin/gunicorn adonis.wsgi:application --bind 127.0.0.1:8000 --workers 3
Restart=always

[Install]
WantedBy=multi-user.target
EOF

sudo systemctl daemon-reload
sudo systemctl enable adonis
sudo systemctl start adonis
```

### تست:
```bash
curl http://127.0.0.1:8000/fa-new/
```

---

## مرحله 8: تنظیم Nginx

```bash
sudo cat > /etc/nginx/sites-available/adonis << 'EOF'
server {
    listen 80;
    server_name adonis.gr www.adonis.gr 37.152.186.190;

    location /static/ {
        alias /var/www/adonis-fa/staticfiles/;
    }
    location /media/ {
        alias /var/www/adonis-fa/media/;
    }
    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOF

sudo rm -f /etc/nginx/sites-enabled/default
sudo ln -sf /etc/nginx/sites-available/adonis /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

---

## مرحله 9: فعال‌سازی SSL (بعد از DNS)

```bash
sudo certbot --nginx -d adonis.gr -d www.adonis.gr
```

---

## تست نهایی

- [ ] `http://37.152.186.190/fa-new/` باز می‌شود
- [ ] `http://37.152.186.190/fa-admin/` باز می‌شود
- [ ] تصاویر و CSS لود می‌شوند
- [ ] فرم‌ها کار می‌کنند

---

## دستورات مفید

| کار | دستور |
|-----|--------|
| ریستارت Django | `sudo systemctl restart adonis` |
| لاگ‌ها | `sudo journalctl -u adonis -f` |
| وضعیت | `sudo systemctl status adonis nginx` |

---

## مشکلات احتمالی

### خطای 502:
```bash
sudo systemctl restart adonis
```

### مشکل دیتابیس:
```bash
cd /var/www/adonis-fa && source venv/bin/activate
python manage.py migrate
```

### مشکل static:
```bash
python manage.py collectstatic --clear --noinput
```

---

**تماس:** اگر مشکلی بود، اسکرین‌شات از خطا بفرستید.
