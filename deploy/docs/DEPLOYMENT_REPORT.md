# گزارش استقرار سایت فارسی ADONIS

**تاریخ:** 2026-06-01
**سرور:** R1Cloud (116.203.240.156)
**دامنه هدف:** adonis.gr

---

## 1. خلاصه وضعیت

| مورد | وضعیت |
|------|-------|
| پروژه Django | ✅ آماده |
| Gunicorn systemd | ✅ فعال |
| Nginx | ✅ کانفیگ شده |
| SSL | ⏳ منتظر DNS |
| DNS | ⏳ نیاز به تنظیم |
| SEO | ✅ آماده |

---

## 2. مسیرهای مهم

### پروژه
```
/root/adonis_site/              # Root پروژه
├── adonis/                     # تنظیمات Django
│   ├── settings.py
│   └── urls.py
├── apps/persian_cms/           # اپ فارسی
├── venv/                       # Virtual Environment
├── staticfiles/                # Static files (collectstatic)
├── media/                      # Media uploads
├── logs/                       # لاگ‌های Gunicorn
│   ├── gunicorn.log
│   ├── gunicorn-access.log
│   └── gunicorn-error.log
├── .env                        # Environment variables
└── deploy/
    ├── gunicorn/               # کانفیگ Gunicorn
    ├── scripts/                # اسکریپت‌ها
    │   └── setup-ssl.sh        # اسکریپت SSL
    └── docs/                   # مستندات
        ├── DNS_ARVANCLOUD.md   # راهنمای DNS
        └── DEPLOYMENT_REPORT.md # این فایل
```

### Nginx
```
/etc/nginx/sites-available/
├── adonis.gr.conf              # کانفیگ HTTP (فعال)
└── adonis.gr-ssl.conf          # کانفیگ HTTPS (برای بعد از SSL)

/etc/nginx/sites-enabled/
└── adonis.gr.conf -> ../sites-available/adonis.gr.conf
```

### لاگ‌ها
```
/root/adonis_site/logs/         # لاگ‌های Gunicorn
/var/log/nginx/adonis.gr.access.log   # Nginx access
/var/log/nginx/adonis.gr.error.log    # Nginx errors
/root/adonis_site/django_errors.log   # Django errors
```

---

## 3. سرویس‌های فعال

### Gunicorn (adonis.service)
```bash
# وضعیت
sudo systemctl status adonis

# ریستارت
sudo systemctl restart adonis

# لاگ
sudo journalctl -u adonis -f
```

### Nginx
```bash
# وضعیت
sudo systemctl status nginx

# ریلود (بدون قطعی)
sudo systemctl reload nginx

# ریستارت
sudo systemctl restart nginx

# تست کانفیگ
sudo nginx -t
```

### PostgreSQL
```bash
sudo systemctl status postgresql
```

---

## 4. دستورات مفید

### ریستارت کامل
```bash
cd /root/adonis_site
./restart.sh
```

### جمع‌آوری static files
```bash
cd /root/adonis_site
source venv/bin/activate
python manage.py collectstatic --noinput
```

### اجرای migrations
```bash
cd /root/adonis_site
source venv/bin/activate
python manage.py migrate
```

### تست local
```bash
curl -I http://127.0.0.1:8000/fa-new/
curl http://127.0.0.1:8000/robots.txt
curl http://127.0.0.1:8000/fa-new/sitemap.xml
```

---

## 5. DNS Records (برای ابرآروان)

| Type | Name | Value | TTL |
|------|------|-------|-----|
| A | @ | 116.203.240.156 | 300 |
| A | www | 116.203.240.156 | 300 |

📄 **راهنمای کامل:** `deploy/docs/DNS_ARVANCLOUD.md`

---

## 6. بعد از تنظیم DNS

### فعال‌سازی SSL
```bash
cd /root/adonis_site
./deploy/scripts/setup-ssl.sh admin@adonis.gr
```

این اسکریپت:
1. DNS را چک می‌کند
2. با Certbot گواهی SSL می‌گیرد
3. کانفیگ HTTPS را فعال می‌کند
4. Nginx را reload می‌کند

---

## 7. URLهای سایت

### Production (بعد از DNS)
- صفحه اصلی فارسی: `https://adonis.gr/fa-new/`
- پنل ادمین فارسی: `https://adonis.gr/fa-admin/`
- پنل ادمین اصلی: `https://adonis.gr/admin/`
- robots.txt: `https://adonis.gr/robots.txt`
- sitemap فارسی: `https://adonis.gr/fa-new/sitemap.xml`

### فعلی (با IP)
- صفحه اصلی فارسی: `http://116.203.240.156/fa-new/`
- پنل ادمین: `http://116.203.240.156/fa-admin/`

---

## 8. SEO

### robots.txt
- ✅ به صورت داینامیک از Django سرو می‌شود
- ✅ مسیرهای admin بلاک شده
- ✅ sitemap فارسی لینک شده

### Sitemap
- ✅ `/fa-new/sitemap.xml` فعال
- ✅ صفحات استاتیک، بلاگ، و صفحات سفارشی
- ✅ Cache 6 ساعته

### Redirects
- ✅ سیستم redirect از طریق پنل ادمین
- ✅ www به non-www
- ✅ HTTP به HTTPS (بعد از SSL)

### noindex
- ✅ پنل ادمین با X-Robots-Tag: noindex

---

## 9. چک‌لیست قبل از لانچ

- [ ] DNS تنظیم شود (ابرآروان)
- [ ] SSL فعال شود (`./deploy/scripts/setup-ssl.sh`)
- [ ] تست صفحه اصلی با دامنه
- [ ] تست پنل ادمین
- [ ] تست آپلود عکس
- [ ] تست فرم تماس
- [ ] تست موبایل
- [ ] بررسی Google Search Console

---

## 10. مشکلات احتمالی و راه‌حل

### مشکل: سایت لود نمی‌شود
```bash
# چک سرویس‌ها
sudo systemctl status adonis nginx postgresql

# چک لاگ‌ها
tail -100 /root/adonis_site/logs/gunicorn-error.log
tail -100 /var/log/nginx/adonis.gr.error.log
```

### مشکل: Static files نمایش داده نمی‌شوند
```bash
cd /root/adonis_site
source venv/bin/activate
python manage.py collectstatic --noinput --clear
sudo systemctl reload nginx
```

### مشکل: خطای 502 Bad Gateway
```bash
# چک پورت Gunicorn
curl http://127.0.0.1:8000/health/

# ریستارت سرویس
sudo systemctl restart adonis
```

### مشکل: SSL کار نمی‌کند
```bash
# چک گواهی
sudo certbot certificates

# تجدید دستی
sudo certbot renew --dry-run
```

---

## 11. Backup

### Database
```bash
cd /root/adonis_site
source venv/bin/activate
python manage.py backup_full
```

### Media
```bash
tar -czvf media_backup_$(date +%Y%m%d).tar.gz /root/adonis_site/media/
```

---

## 12. تماس و پشتیبانی

- **پشتیبانی ابرآروان:** support@arvancloud.ir
- **مستندات Django:** https://docs.djangoproject.com/
- **مستندات Certbot:** https://certbot.eff.org/docs/

---

*این گزارش به صورت خودکار تولید شده است.*
