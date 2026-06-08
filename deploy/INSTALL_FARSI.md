# 🇮🇷 راهنمای نصب سایت ادونیس روی ابرآروان

## ✅ فقط ۳ قدم!

---

## قدم ۱: وارد سرور شو

ترمینال باز کن و بزن:

```
ssh root@IP_SERVERت
```

> اگر یوزر `ubuntu` داری: `ssh ubuntu@IP_SERVERت`

---

## قدم ۲: اسکریپت نصب را اجرا کن

این دستور را کپی کن و بزن Enter:

```bash
curl -sSL https://raw.githubusercontent.com/maisamsabour-gif/adoniss.gr/main/deploy/scripts/install.sh | sudo bash
```

⏳ **صبر کن** تا نصب تمام شود (حدود ۵ دقیقه)

---

## قدم ۳: DNS تنظیم کن

بعد از نصب، در **پنل ابرآروان** بخش DNS:

| نوع | نام | مقدار |
|-----|-----|-------|
| A | @ | IP سرور |
| A | www | IP سرور |

---

## قدم ۴ (اختیاری): SSL فعال کن

بعد از اینکه DNS فعال شد (۵-۳۰ دقیقه):

```bash
sudo certbot --nginx -d adoniss.gr -d www.adoniss.gr
```

---

## ✅ تمام!

سایت باید روی این آدرس‌ها کار کنه:
- `http://IP_SERVER/fa-new/`
- `https://adoniss.gr/fa-new/` (بعد از SSL)

---

## 🆘 اگر مشکلی پیش آمد

### ریستارت سرویس:
```bash
sudo systemctl restart adoniss
```

### دیدن خطاها:
```bash
sudo journalctl -u adoniss -f
```

### وضعیت سرویس:
```bash
sudo systemctl status adoniss nginx
```

---

## 📞 کمک

اسکرین‌شات از خطا بفرست!
