# راهنمای دیپلوی روی سرور ابرآروان

## پیش‌نیازها
- سرور ابرآروان با Ubuntu 22.04/24.04
- دسترسی SSH به سرور
- SSH Key برای GitHub (برای clone پروژه)

---

## روش 1: اجرای مستقیم (ساده‌ترین)

### قدم 1: SSH به سرور
```bash
ssh ubuntu@37.152.186.190
```

### قدم 2: دانلود و اجرای اسکریپت
```bash
# اول SSH key برای GitHub اضافه کن
ssh-keygen -t ed25519 -C "arvan-server"
cat ~/.ssh/id_ed25519.pub
# این کلید را به GitHub Settings → SSH Keys اضافه کن

# بعد اسکریپت را اجرا کن
curl -sSL https://raw.githubusercontent.com/maisamsabour-gif/adoniss.gr/main/deploy/scripts/deploy-arvan.sh -o deploy.sh
sudo bash deploy.sh
```

---

## روش 2: کپی دستی فایل‌ها

### از کامپیوتر خودت:
```bash
# کپی اسکریپت به سرور
scp /path/to/deploy-arvan.sh ubuntu@37.152.186.190:~/

# اتصال و اجرا
ssh ubuntu@37.152.186.190
sudo bash deploy.sh
```

---

## بعد از نصب

### 1. تنظیم DNS در ابرآروان
```
A record:  @   → 37.152.186.190
A record:  www → 37.152.186.190
```

### 2. فعال‌سازی SSL
```bash
sudo certbot --nginx -d adonis.gr -d www.adonis.gr --email admin@adonis.gr --agree-tos
```

### 3. تست سایت
```
http://37.152.186.190/fa-new/
http://37.152.186.190/fa-admin/
```

### 4. ساخت Superuser (اگر لازم است)
```bash
cd /var/www/adonis-fa
source venv/bin/activate
python manage.py createsuperuser
```

### 5. انتقال دیتابیس از سرور قبلی (اختیاری)
```bash
# روی سرور قدیمی (R1Cloud):
pg_dump -h 127.0.0.1 -U adoniss_user adoniss_prod > backup.sql
scp backup.sql ubuntu@37.152.186.190:~/

# روی سرور جدید (Arvan):
sudo -u postgres psql adonis_prod < backup.sql
```

---

## دستورات مفید

| کار | دستور |
|-----|--------|
| وضعیت سرویس‌ها | `sudo systemctl status adonis nginx` |
| ریستارت Django | `sudo systemctl restart adonis` |
| ریلود Nginx | `sudo systemctl reload nginx` |
| لاگ Django | `tail -f /var/www/adonis-fa/logs/gunicorn-error.log` |
| لاگ Nginx | `tail -f /var/log/nginx/adonis.error.log` |
| Shell Django | `cd /var/www/adonis-fa && source venv/bin/activate && python manage.py shell` |

---

## عیب‌یابی

### سایت لود نمی‌شود
```bash
sudo systemctl status adonis
tail -100 /var/www/adonis-fa/logs/gunicorn-error.log
```

### خطای 502
```bash
curl http://127.0.0.1:8000/health/
sudo systemctl restart adonis
```

### مشکل دیتابیس
```bash
sudo -u postgres psql -c "\\l"  # لیست دیتابیس‌ها
sudo -u postgres psql -c "\\du" # لیست یوزرها
```
