from __future__ import annotations

from pathlib import Path

from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils.text import slugify

# Register HEIC/HEIF support with Pillow for iPhone images
try:
    from pillow_heif import register_heif_opener
    register_heif_opener()
except ImportError:
    pass  # pillow-heif not installed, HEIC support disabled

SEO_STATUS_CHOICES = [
    ('needs_review', 'Needs review'),
    ('ready', 'Ready'),
    ('critical', 'Critical issues'),
]


class PersianTimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class PersianPage(PersianTimeStampedModel):
    PAGE_TYPES = (
        ("home", "خانه"),
        ("about", "درباره ما"),
        ("blog", "بلاگ"),
        ("golden_visa", "گلدن ویزا"),
        ("contact", "تماس"),
        ("custom", "سفارشی"),
    )

    page_type = models.CharField(max_length=30, choices=PAGE_TYPES, default="custom", verbose_name="نوع صفحه")
    title = models.CharField(max_length=220, verbose_name="عنوان صفحه")
    slug = models.SlugField(max_length=220, unique=True, allow_unicode=True, verbose_name="اسلاگ")
    route_path = models.CharField(
        max_length=300,
        unique=True,
        blank=True,
        verbose_name="مسیر عمومی",
        help_text="خودکار از روی اسلاگ ساخته می‌شود. برای صفحات سفارشی: /fa-new/p/<اسلاگ>/",
    )
    body = models.TextField(blank=True, verbose_name="محتوا")
    is_published = models.BooleanField(default=True, verbose_name="منتشر شده")
    meta_title = models.CharField(max_length=260, blank=True, verbose_name="Meta Title")
    meta_description = models.TextField(blank=True, verbose_name="Meta Description")
    canonical_url = models.URLField(blank=True, verbose_name="Canonical URL")
    og_title = models.CharField(max_length=260, blank=True, verbose_name="OG Title")
    og_description = models.TextField(blank=True, verbose_name="OG Description")
    og_image = models.ImageField(upload_to="persian_cms/og/", blank=True, null=True, verbose_name="OG Image")
    focus_keyword = models.CharField(max_length=180, blank=True, verbose_name="Focus Keyword")
    noindex = models.BooleanField(default=False, verbose_name="Noindex")
    seo_status = models.CharField(
        max_length=20,
        choices=SEO_STATUS_CHOICES,
        default='needs_review',
        verbose_name='SEO Status',
    )
    sort_order = models.PositiveIntegerField(default=0, db_index=True, verbose_name="ترتیب")

    class Meta:
        db_table = "persian_cms_page"
        ordering = ["sort_order", "id"]
        verbose_name = "صفحه فارسی"
        verbose_name_plural = "صفحات فارسی"

    # Fixed public paths for the built-in page types.
    FIXED_ROUTES = {
        "home": "/fa-new/",
        "about": "/fa-new/about/",
        "contact": "/fa-new/contact/",
        "golden_visa": "/fa-new/golden-visa/",
        "blog": "/fa-new/blog/",
    }

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return self.route_path or self._auto_route_path()

    def _auto_route_path(self) -> str:
        if self.page_type in self.FIXED_ROUTES:
            return self.FIXED_ROUTES[self.page_type]
        slug = self.slug or slugify(self.title, allow_unicode=True)
        return f"/fa-new/p/{slug}/"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        # Auto-fill route_path when left blank so the editor never has to.
        if not self.route_path:
            self.route_path = self._auto_route_path()
        path = self.route_path.strip()
        if not path.startswith("/"):
            path = f"/{path}"
        if not path.endswith("/"):
            path = f"{path}/"
        self.route_path = path
        super().save(*args, **kwargs)


class PersianSEOSettings(PersianTimeStampedModel):
    page = models.OneToOneField(
        PersianPage,
        on_delete=models.CASCADE,
        related_name="seo_settings",
        null=True,
        blank=True,
        verbose_name="صفحه مرتبط",
    )
    page_key = models.CharField(
        max_length=80,
        unique=True,
        verbose_name="کلید صفحه",
        help_text="برای صفحه اصلی مقدار home را استفاده کنید.",
    )
    meta_title = models.CharField(max_length=260, blank=True, verbose_name="Meta Title")
    meta_description = models.TextField(blank=True, verbose_name="Meta Description")
    canonical_url = models.URLField(blank=True, verbose_name="Canonical URL")
    og_title = models.CharField(max_length=260, blank=True, verbose_name="OG Title")
    og_description = models.TextField(blank=True, verbose_name="OG Description")
    og_image = models.ImageField(upload_to="persian_cms/og/", blank=True, null=True, verbose_name="OG Image")
    focus_keyword = models.CharField(max_length=180, blank=True, verbose_name="Focus Keyword")
    noindex = models.BooleanField(default=False, verbose_name="Noindex")
    seo_status = models.CharField(
        max_length=20,
        choices=SEO_STATUS_CHOICES,
        default='needs_review',
        verbose_name='SEO Status',
    )
    robots_index = models.BooleanField(default=True, verbose_name="اجازه ایندکس")
    robots_follow = models.BooleanField(default=True, verbose_name="اجازه دنبال‌کردن لینک‌ها")

    class Meta:
        db_table = "persian_cms_seo_settings"
        ordering = ["page_key"]
        verbose_name = "تنظیمات سئو فارسی"
        verbose_name_plural = "تنظیمات سئو فارسی"

    def __str__(self):
        return f"SEO: {self.page_key}"

    @classmethod
    def for_page(cls, page_key: str) -> "PersianSEOSettings | None":
        return cls.objects.filter(page_key=page_key).first()

    @property
    def robots_content(self) -> str:
        force_noindex = self.noindex
        index_part = "noindex" if force_noindex else ("index" if self.robots_index else "noindex")
        follow_part = "follow" if self.robots_follow else "nofollow"
        return f"{index_part}, {follow_part}"


class PersianSection(PersianTimeStampedModel):
    SECTION_TYPES = (
        ("hero", "هیرو"),
        ("why_greece", "چرا یونان"),
        ("why_adonis", "چرا آدونیس"),
        ("routes", "مسیرها"),
        ("projects", "پروژه‌ها"),
        ("faq", "سوالات متداول"),
        ("landing_block", "بلوک لندینگ"),
        ("custom", "سفارشی"),
    )

    page = models.ForeignKey(
        PersianPage,
        on_delete=models.CASCADE,
        related_name="sections",
        null=True,
        blank=True,
        verbose_name="صفحه",
    )
    section_type = models.CharField(max_length=30, choices=SECTION_TYPES, default="custom", verbose_name="نوع بخش")
    internal_name = models.CharField(max_length=180, blank=True, verbose_name="نام داخلی")
    anchor_id = models.SlugField(max_length=120, blank=True, verbose_name="Anchor ID")
    title = models.CharField(max_length=240, blank=True, verbose_name="عنوان")
    subtitle = models.TextField(blank=True, verbose_name="زیرعنوان")
    body = models.TextField(blank=True, verbose_name="محتوا")
    image = models.ImageField(upload_to="persian_cms/sections/", blank=True, null=True, verbose_name="تصویر")
    cta_label = models.CharField(max_length=120, blank=True, verbose_name="متن CTA")
    cta_url = models.CharField(max_length=500, blank=True, verbose_name="لینک CTA")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    show_on_mobile = models.BooleanField(default=True, verbose_name="نمایش در موبایل")
    show_on_desktop = models.BooleanField(default=True, verbose_name="نمایش در دسکتاپ")
    sort_order = models.PositiveIntegerField(default=0, db_index=True, verbose_name="ترتیب")

    class Meta:
        db_table = "persian_cms_section"
        ordering = ["sort_order", "id"]
        verbose_name = "بخش فارسی"
        verbose_name_plural = "بخش‌های فارسی"

    def __str__(self):
        return self.internal_name or self.title or self.get_section_type_display()

    def save(self, *args, **kwargs):
        if not self.anchor_id:
            source = self.internal_name or self.title or self.section_type
            self.anchor_id = slugify(source, allow_unicode=True)[:120]
        super().save(*args, **kwargs)


class PersianHeroSlide(PersianTimeStampedModel):
    section = models.ForeignKey(
        PersianSection,
        on_delete=models.CASCADE,
        related_name="hero_slides",
        verbose_name="بخش هیرو",
    )
    title = models.CharField(max_length=260, verbose_name="عنوان")
    subtitle = models.TextField(blank=True, verbose_name="زیرعنوان")
    highlight = models.CharField(max_length=120, blank=True, verbose_name="کلمه طلایی")
    start_progress = models.FloatField(default=0, validators=[MinValueValidator(0), MaxValueValidator(101)], verbose_name="شروع (%)")
    end_progress = models.FloatField(default=30, validators=[MinValueValidator(0), MaxValueValidator(101)], verbose_name="پایان (%)")
    cta_label = models.CharField(max_length=120, blank=True, verbose_name="متن CTA")
    cta_url = models.CharField(max_length=500, blank=True, verbose_name="لینک CTA")
    sort_order = models.PositiveIntegerField(default=0, db_index=True, verbose_name="ترتیب")

    class Meta:
        db_table = "persian_cms_hero_slide"
        ordering = ["sort_order", "id"]
        verbose_name = "اسلاید هیرو فارسی"
        verbose_name_plural = "اسلایدهای هیرو فارسی"

    def __str__(self):
        return self.title


class PersianBlogPost(PersianTimeStampedModel):
    title = models.CharField(max_length=260, verbose_name="عنوان")
    slug = models.SlugField(max_length=260, unique=True, allow_unicode=True, verbose_name="اسلاگ")
    excerpt = models.TextField(blank=True, verbose_name="خلاصه")
    body = models.TextField(verbose_name="متن")
    featured_image = models.ImageField(upload_to="persian_cms/blog/", blank=True, null=True, verbose_name="تصویر شاخص")
    meta_title = models.CharField(max_length=260, blank=True, verbose_name="Meta Title")
    meta_description = models.TextField(blank=True, verbose_name="Meta Description")
    canonical_url = models.URLField(blank=True, verbose_name="Canonical URL")
    og_title = models.CharField(max_length=260, blank=True, verbose_name="OG Title")
    og_description = models.TextField(blank=True, verbose_name="OG Description")
    og_image = models.ImageField(upload_to="persian_cms/blog/og/", blank=True, null=True, verbose_name="OG Image")
    focus_keyword = models.CharField(max_length=180, blank=True, verbose_name="Focus Keyword")
    noindex = models.BooleanField(default=False, verbose_name="Noindex")
    seo_status = models.CharField(
        max_length=20,
        choices=SEO_STATUS_CHOICES,
        default='needs_review',
        verbose_name='SEO Status',
    )
    published_at = models.DateTimeField(blank=True, null=True, verbose_name="تاریخ انتشار")
    is_published = models.BooleanField(default=False, verbose_name="منتشر شده")

    class Meta:
        db_table = "persian_cms_blog_post"
        ordering = ["-published_at", "-id"]
        verbose_name = "پست بلاگ فارسی"
        verbose_name_plural = "پست‌های بلاگ فارسی"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)


class PersianMenuItem(PersianTimeStampedModel):
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="والد",
    )
    label = models.CharField(max_length=120, verbose_name="متن")
    url = models.CharField(max_length=500, verbose_name="لینک")
    open_in_new_tab = models.BooleanField(default=False, verbose_name="باز شدن در تب جدید")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    sort_order = models.PositiveIntegerField(default=0, db_index=True, verbose_name="ترتیب")

    class Meta:
        db_table = "persian_cms_menu_item"
        ordering = ["sort_order", "id"]
        verbose_name = "آیتم منوی فارسی"
        verbose_name_plural = "آیتم‌های منوی فارسی"

    def __str__(self):
        return self.label


class PersianFooterSettings(PersianTimeStampedModel):
    brand_name = models.CharField(max_length=180, default="آدونیس | ADONIS", verbose_name="نام برند")
    brand_tagline = models.CharField(max_length=260, blank=True, verbose_name="شعار")
    footer_logo = models.ImageField(upload_to="persian_cms/footer/", blank=True, null=True, verbose_name="لوگو")
    address = models.CharField(max_length=320, blank=True, verbose_name="آدرس")
    phone = models.CharField(max_length=80, blank=True, verbose_name="تلفن")
    email = models.EmailField(blank=True, verbose_name="ایمیل")
    whatsapp_url = models.CharField(max_length=320, blank=True, verbose_name="واتس‌اپ")
    links_title = models.CharField(max_length=120, default="دسترسی سریع", verbose_name="عنوان لینک‌ها")
    contact_title = models.CharField(max_length=120, default="تماس", verbose_name="عنوان تماس")
    copyright_text = models.CharField(max_length=300, blank=True, verbose_name="کپی‌رایت")

    class Meta:
        db_table = "persian_cms_footer_settings"
        verbose_name = "تنظیمات فوتر فارسی"
        verbose_name_plural = "تنظیمات فوتر فارسی"

    def __str__(self):
        return "Persian Footer"

    def save(self, *args, **kwargs):
        self.pk = 1
        super().save(*args, **kwargs)

    @classmethod
    def get_settings(cls) -> "PersianFooterSettings":
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj


class PersianMediaAsset(PersianTimeStampedModel):
    title = models.CharField(max_length=180, verbose_name="عنوان")
    file = models.FileField(upload_to="persian_cms/media/", verbose_name="فایل")
    alt_text = models.CharField(max_length=220, blank=True, verbose_name="متن جایگزین")
    is_active = models.BooleanField(default=True, verbose_name="فعال")

    class Meta:
        db_table = "persian_cms_media_asset"
        ordering = ["-created_at"]
        verbose_name = "رسانه فارسی"
        verbose_name_plural = "رسانه‌های فارسی"

    def __str__(self):
        return self.title


class PersianCTA(PersianTimeStampedModel):
    target_page = models.ForeignKey(
        PersianPage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="ctas",
        verbose_name="صفحه هدف",
    )
    label = models.CharField(max_length=140, verbose_name="متن دکمه")
    url = models.CharField(max_length=500, verbose_name="لینک")
    style = models.CharField(max_length=40, default="primary", verbose_name="استایل")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    sort_order = models.PositiveIntegerField(default=0, db_index=True, verbose_name="ترتیب")

    class Meta:
        db_table = "persian_cms_cta"
        ordering = ["sort_order", "id"]
        verbose_name = "CTA فارسی"
        verbose_name_plural = "CTAهای فارسی"

    def __str__(self):
        return self.label


class PersianFAQ(PersianTimeStampedModel):
    page = models.ForeignKey(
        PersianPage,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="faqs",
        verbose_name="صفحه",
    )
    question = models.CharField(max_length=280, verbose_name="سوال")
    answer = models.TextField(verbose_name="پاسخ")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    sort_order = models.PositiveIntegerField(default=0, db_index=True, verbose_name="ترتیب")

    class Meta:
        db_table = "persian_cms_faq"
        ordering = ["sort_order", "id"]
        verbose_name = "سوال متداول فارسی"
        verbose_name_plural = "سوالات متداول فارسی"

    def __str__(self):
        return self.question


class PersianRedirectMap(PersianTimeStampedModel):
    source_path = models.CharField(max_length=320, unique=True, verbose_name="مسیر مبدا")
    destination_path = models.CharField(max_length=320, verbose_name="مسیر مقصد")
    status_code = models.PositiveSmallIntegerField(default=301, verbose_name="کد ریدایرکت")
    is_active = models.BooleanField(default=True, verbose_name="فعال")
    notes = models.CharField(max_length=280, blank=True, verbose_name="یادداشت")

    class Meta:
        db_table = "persian_cms_redirect_map"
        ordering = ["source_path"]
        verbose_name = "نگاشت ریدایرکت فارسی"
        verbose_name_plural = "نگاشت ریدایرکت فارسی"

    def __str__(self):
        return f"{self.source_path} -> {self.destination_path}"

    def save(self, *args, **kwargs):
        for field_name in ("source_path", "destination_path"):
            value = getattr(self, field_name, "") or ""
            value = value.strip()
            if not value.startswith("/"):
                value = f"/{value}"
            if self.status_code == 301 and not value.endswith("/"):
                value = f"{value}/"
            setattr(self, field_name, value)
        super().save(*args, **kwargs)


class PersianExportLog(PersianTimeStampedModel):
    file = models.FileField(upload_to="persian_cms/exports/", verbose_name="فایل خروجی")
    note = models.CharField(max_length=280, blank=True, verbose_name="یادداشت")

    class Meta:
        db_table = "persian_cms_export_log"
        ordering = ["-created_at"]
        verbose_name = "لاگ خروجی فارسی"
        verbose_name_plural = "لاگ‌های خروجی فارسی"

    def __str__(self):
        return Path(self.file.name).name if self.file else f"export-{self.pk}"


# ── Persian Properties (جدا از سایت انگلیسی) ──────────────────────────────────
# These models are completely separate from the English properties app.
# Admin can manage Persian properties with their own images/videos here.

def _fa_property_image_upload_path(instance, filename):
    """Upload path for Persian property images."""
    import os, uuid, re
    from django.utils.text import slugify
    
    _, ext = os.path.splitext(filename.lower())
    # Accept all common image formats including HEIC
    allowed_extensions = (
        '.jpg', '.jpeg', '.png', '.webp', '.gif', '.bmp', '.tiff', '.tif',
        '.heic', '.heif', '.avif', '.svg', '.ico'
    )
    if ext not in allowed_extensions:
        ext = '.jpg'
    
    # Generate a safe ASCII slug from the property name/slug
    base = ''
    if instance.pk:
        base = f'property-{instance.pk}'
    elif instance.slug:
        # Convert Persian slug to ASCII-safe version
        base = slugify(instance.slug, allow_unicode=False) or f'prop-{uuid.uuid4().hex[:6]}'
    elif instance.name:
        base = slugify(instance.name, allow_unicode=False) or f'prop-{uuid.uuid4().hex[:6]}'
    else:
        base = 'property'
    
    # Ensure base is safe for filesystem
    base = re.sub(r'[^a-z0-9-]', '', base.lower())[:30].rstrip('-')
    if not base:
        base = 'property'
    
    uid = uuid.uuid4().hex[:8]
    return f'persian_cms/properties/{base}-{uid}{ext}'


class FaProperty(PersianTimeStampedModel):
    """Persian property model - completely separate from English properties.
    
    This model stores property data for the Persian site with its own images,
    videos, and all content in Persian. Designed for luxury real estate.
    """
    
    STATUS_CHOICES = [
        ('available', 'موجود برای فروش'),
        ('reserved', 'رزرو شده'),
        ('sold_out_soon', 'واحدهای محدود'),
        ('sold_out', 'فروخته شده'),
    ]
    
    TIMELINE_CHOICES = [
        ('off_plan', 'پیش‌فروش'),
        ('under_construction', 'در حال ساخت'),
        ('ready_to_start', 'آماده شروع بازسازی'),
        ('under_renovation', 'در حال بازسازی'),
        ('finishing_soon', 'به‌زودی تحویل'),
        ('ready', 'آماده تحویل'),
    ]
    
    PRICE_TIER_CHOICES = [
        ('250', '€250K Plan'),
        ('400', '€400K Plan'),
        ('800', '€800K Plan'),
        ('custom', 'قیمت سفارشی'),
    ]
    
    PROPERTY_TYPE_CHOICES = [
        ('apartment', 'آپارتمان'),
        ('villa', 'ویلا'),
        ('penthouse', 'پنت‌هاوس'),
        ('duplex', 'دوبلکس'),
        ('townhouse', 'تاون‌هاوس'),
        ('commercial', 'تجاری'),
        ('land', 'زمین'),
    ]
    
    # ══════════════════════════════════════════════════════════════════════════════
    # 1. BASIC INFO — اطلاعات پایه
    # ══════════════════════════════════════════════════════════════════════════════
    name = models.CharField(
        max_length=200,
        verbose_name='نام پروژه',
        help_text='نام رسمی پروژه که در عنوان صفحه نمایش داده می‌شود',
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        allow_unicode=True,
        verbose_name='اسلاگ URL',
        help_text='آدرس صفحه: /fa-new/properties/[slug]/',
    )
    property_type = models.CharField(
        max_length=20,
        choices=PROPERTY_TYPE_CHOICES,
        default='apartment',
        verbose_name='نوع ملک',
    )
    tagline = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='شعار / توضیح کوتاه',
        help_text='یک جمله جذاب که در کارت نمایش داده می‌شود (مثلاً: زندگی لوکس در قلب آتن)',
    )
    headline = models.CharField(
        max_length=400,
        blank=True,
        verbose_name='تیتر اصلی صفحه',
        help_text='عنوان H1 صفحه جزئیات ملک — اگر خالی باشد، از نام پروژه استفاده می‌شود',
    )
    description = models.TextField(
        blank=True,
        verbose_name='توضیحات کامل',
        help_text='توضیحات کامل پروژه برای صفحه جزئیات (HTML مجاز)',
    )
    short_description = models.TextField(
        max_length=500,
        blank=True,
        verbose_name='خلاصه توضیحات',
        help_text='خلاصه ۲-۳ جمله‌ای برای نمایش در کارت و پیش‌نمایش',
    )
    
    # ══════════════════════════════════════════════════════════════════════════════
    # 2. PRICING — قیمت‌گذاری
    # ══════════════════════════════════════════════════════════════════════════════
    price = models.DecimalField(
        max_digits=12,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name='قیمت شروع (یورو)',
        help_text='قیمت شروع به یورو — فقط عدد بدون علامت',
    )
    price_label = models.CharField(
        max_length=80,
        blank=True,
        verbose_name='برچسب قیمت',
        help_text='متن نمایشی قیمت (مثلاً: از €۲۵۰,۰۰۰ یا تماس بگیرید)',
    )
    price_tier = models.CharField(
        max_length=10,
        choices=PRICE_TIER_CHOICES,
        default='250',
        verbose_name='پلن گلدن ویزا',
    )
    price_per_sqm = models.DecimalField(
        max_digits=10,
        decimal_places=0,
        null=True,
        blank=True,
        verbose_name='قیمت هر متر مربع (یورو)',
    )
    rental_yield = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='بازده اجاره',
        help_text='مثلاً: ۵-۷٪ سالانه',
    )
    
    # ══════════════════════════════════════════════════════════════════════════════
    # 3. LOCATION — موقعیت مکانی
    # ══════════════════════════════════════════════════════════════════════════════
    city = models.CharField(
        max_length=100,
        default='آتن',
        verbose_name='شهر',
    )
    location = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='منطقه',
        help_text='مثلاً: جنوب آتن',
    )
    area = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='محله / ناحیه',
        help_text='مثلاً: گلیفادا، آلیموس',
    )
    address = models.CharField(
        max_length=300,
        blank=True,
        verbose_name='آدرس کامل',
        help_text='آدرس دقیق برای نقشه (اختیاری)',
    )
    map_latitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        verbose_name='عرض جغرافیایی',
    )
    map_longitude = models.DecimalField(
        max_digits=10,
        decimal_places=7,
        null=True,
        blank=True,
        verbose_name='طول جغرافیایی',
    )
    distance_to_sea = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='فاصله تا دریا',
        help_text='مثلاً: ۵۰۰ متر',
    )
    distance_to_center = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='فاصله تا مرکز شهر',
    )
    distance_to_airport = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='فاصله تا فرودگاه',
    )
    
    # ══════════════════════════════════════════════════════════════════════════════
    # 4. PROPERTY DETAILS — مشخصات ملک
    # ══════════════════════════════════════════════════════════════════════════════
    total_units = models.PositiveIntegerField(
        default=1,
        verbose_name='تعداد کل واحدها',
    )
    available_units = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='واحدهای موجود',
    )
    floors = models.PositiveIntegerField(
        default=1,
        verbose_name='تعداد طبقات',
    )
    bedrooms_min = models.PositiveIntegerField(
        default=1,
        verbose_name='حداقل اتاق خواب',
    )
    bedrooms_max = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='حداکثر اتاق خواب',
    )
    bathrooms = models.PositiveIntegerField(
        default=1,
        verbose_name='سرویس بهداشتی',
    )
    size_min = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='حداقل متراژ (m²)',
    )
    size_max = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='حداکثر متراژ (m²)',
    )
    parking_spaces = models.PositiveIntegerField(
        default=0,
        verbose_name='پارکینگ',
    )
    year_built = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name='سال ساخت',
    )
    
    # ══════════════════════════════════════════════════════════════════════════════
    # 5. FEATURES & AMENITIES — امکانات و ویژگی‌ها
    # ══════════════════════════════════════════════════════════════════════════════
    # Quick feature badges (shown on cards)
    feature_1 = models.CharField(max_length=100, blank=True, verbose_name='ویژگی برجسته ۱',
                                help_text='مثلاً: 🏊 استخر خصوصی')
    feature_2 = models.CharField(max_length=100, blank=True, verbose_name='ویژگی برجسته ۲')
    feature_3 = models.CharField(max_length=100, blank=True, verbose_name='ویژگی برجسته ۳')
    feature_4 = models.CharField(max_length=100, blank=True, verbose_name='ویژگی برجسته ۴')
    
    # Detailed amenities (JSON array for flexibility)
    amenities = models.TextField(
        blank=True,
        verbose_name='امکانات کامل',
        help_text='هر امکان در یک خط جدید (مثلاً: استخر\\nسونا\\nباشگاه)',
    )
    
    # Investment highlights
    investment_highlights = models.TextField(
        blank=True,
        verbose_name='مزایای سرمایه‌گذاری',
        help_text='هر مزیت در یک خط جدید',
    )
    
    # ══════════════════════════════════════════════════════════════════════════════
    # 6. STATUS & TIMELINE — وضعیت و زمان‌بندی
    # ══════════════════════════════════════════════════════════════════════════════
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
        verbose_name='وضعیت فروش',
    )
    timeline_stage = models.CharField(
        max_length=20,
        choices=TIMELINE_CHOICES,
        default='ready',
        verbose_name='مرحله پروژه',
    )
    delivery_date = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='تاریخ تحویل',
        help_text='مثلاً: Q4 2025 یا تابستان ۱۴۰۴',
    )
    golden_visa_eligible = models.BooleanField(
        default=True,
        verbose_name='واجد شرایط گلدن ویزا',
    )
    
    # ══════════════════════════════════════════════════════════════════════════════
    # 7. SEO & METADATA — سئو و متادیتا
    # ══════════════════════════════════════════════════════════════════════════════
    meta_title = models.CharField(
        max_length=70,
        blank=True,
        verbose_name='عنوان سئو (Meta Title)',
        help_text='حداکثر ۷۰ کاراکتر — اگر خالی باشد از نام پروژه استفاده می‌شود',
    )
    meta_description = models.TextField(
        max_length=160,
        blank=True,
        verbose_name='توضیح سئو (Meta Description)',
        help_text='حداکثر ۱۶۰ کاراکتر — توضیح کوتاه برای نمایش در نتایج گوگل',
    )
    focus_keyword = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='کلمه کلیدی اصلی',
        help_text='کلمه کلیدی هدف برای سئو',
    )
    og_title = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='عنوان شبکه اجتماعی (OG Title)',
    )
    og_description = models.TextField(
        max_length=300,
        blank=True,
        verbose_name='توضیح شبکه اجتماعی (OG Description)',
    )
    canonical_url = models.URLField(
        blank=True,
        verbose_name='آدرس Canonical',
        help_text='فقط در صورت نیاز به آدرس متفاوت',
    )
    noindex = models.BooleanField(
        default=False,
        verbose_name='جلوگیری از ایندکس (noindex)',
    )
    schema_markup = models.TextField(
        blank=True,
        verbose_name='Schema Markup (JSON-LD)',
        help_text='کد JSON-LD سفارشی برای Rich Snippets',
    )
    
    # ══════════════════════════════════════════════════════════════════════════════
    # 8. DISPLAY SETTINGS — تنظیمات نمایش
    # ══════════════════════════════════════════════════════════════════════════════
    display_order = models.PositiveIntegerField(
        default=0,
        verbose_name='ترتیب نمایش',
        help_text='عدد کمتر = نمایش زودتر',
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name='پروژه ویژه',
        help_text='نمایش در بخش ویژه صفحه اصلی',
    )
    is_new = models.BooleanField(
        default=False,
        verbose_name='پروژه جدید',
        help_text='نمایش برچسب «جدید»',
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال',
    )
    
    # Cover image - dedicated field for main property image
    cover_image = models.ImageField(
        upload_to=_fa_property_image_upload_path,
        blank=True,
        verbose_name='عکس کاور اصلی',
        help_text='عکس اصلی که در کارت و اشتراک‌گذاری نمایش داده می‌شود',
    )
    cover_image_alt = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Alt عکس کاور',
        help_text='توضیح عکس برای سئو و دسترس‌پذیری',
    )
    
    # Cover image selection from gallery (fallback)
    cover_image_slot = models.PositiveSmallIntegerField(
        default=0,
        choices=[(0, 'خودکار — اولین عکس موجود')] + [(i, f'عکس {i}') for i in range(1, 16)],
        verbose_name='انتخاب از گالری',
        help_text='کدام عکس در کارت و اشتراک‌گذاری نمایش داده شود',
    )
    
    # ══════════════════════════════════════════════════════════════════════════════
    # 9. GALLERY — گالری عکس (۱۵ اسلات با ALT و Caption)
    # ══════════════════════════════════════════════════════════════════════════════
    # Image 1
    image_1 = models.ImageField(upload_to=_fa_property_image_upload_path, blank=True, verbose_name='عکس ۱')
    image_1_alt = models.CharField(max_length=200, blank=True, verbose_name='Alt عکس ۱',
                                   help_text='توضیح عکس برای سئو و دسترس‌پذیری')
    image_1_caption = models.CharField(max_length=300, blank=True, verbose_name='کپشن عکس ۱',
                                       help_text='توضیح زیر عکس در گالری')
    # Image 2
    image_2 = models.ImageField(upload_to=_fa_property_image_upload_path, blank=True, verbose_name='عکس ۲')
    image_2_alt = models.CharField(max_length=200, blank=True, verbose_name='Alt عکس ۲')
    image_2_caption = models.CharField(max_length=300, blank=True, verbose_name='کپشن عکس ۲')
    # Image 3
    image_3 = models.ImageField(upload_to=_fa_property_image_upload_path, blank=True, verbose_name='عکس ۳')
    image_3_alt = models.CharField(max_length=200, blank=True, verbose_name='Alt عکس ۳')
    image_3_caption = models.CharField(max_length=300, blank=True, verbose_name='کپشن عکس ۳')
    # Image 4
    image_4 = models.ImageField(upload_to=_fa_property_image_upload_path, blank=True, verbose_name='عکس ۴')
    image_4_alt = models.CharField(max_length=200, blank=True, verbose_name='Alt عکس ۴')
    image_4_caption = models.CharField(max_length=300, blank=True, verbose_name='کپشن عکس ۴')
    # Image 5
    image_5 = models.ImageField(upload_to=_fa_property_image_upload_path, blank=True, verbose_name='عکس ۵')
    image_5_alt = models.CharField(max_length=200, blank=True, verbose_name='Alt عکس ۵')
    image_5_caption = models.CharField(max_length=300, blank=True, verbose_name='کپشن عکس ۵')
    # Image 6
    image_6 = models.ImageField(upload_to=_fa_property_image_upload_path, blank=True, verbose_name='عکس ۶')
    image_6_alt = models.CharField(max_length=200, blank=True, verbose_name='Alt عکس ۶')
    image_6_caption = models.CharField(max_length=300, blank=True, verbose_name='کپشن عکس ۶')
    # Image 7
    image_7 = models.ImageField(upload_to=_fa_property_image_upload_path, blank=True, verbose_name='عکس ۷')
    image_7_alt = models.CharField(max_length=200, blank=True, verbose_name='Alt عکس ۷')
    image_7_caption = models.CharField(max_length=300, blank=True, verbose_name='کپشن عکس ۷')
    # Image 8
    image_8 = models.ImageField(upload_to=_fa_property_image_upload_path, blank=True, verbose_name='عکس ۸')
    image_8_alt = models.CharField(max_length=200, blank=True, verbose_name='Alt عکس ۸')
    image_8_caption = models.CharField(max_length=300, blank=True, verbose_name='کپشن عکس ۸')
    # Image 9
    image_9 = models.ImageField(upload_to=_fa_property_image_upload_path, blank=True, verbose_name='عکس ۹')
    image_9_alt = models.CharField(max_length=200, blank=True, verbose_name='Alt عکس ۹')
    image_9_caption = models.CharField(max_length=300, blank=True, verbose_name='کپشن عکس ۹')
    # Image 10
    image_10 = models.ImageField(upload_to=_fa_property_image_upload_path, blank=True, verbose_name='عکس ۱۰')
    image_10_alt = models.CharField(max_length=200, blank=True, verbose_name='Alt عکس ۱۰')
    image_10_caption = models.CharField(max_length=300, blank=True, verbose_name='کپشن عکس ۱۰')
    # Image 11
    image_11 = models.ImageField(upload_to=_fa_property_image_upload_path, blank=True, verbose_name='عکس ۱۱')
    image_11_alt = models.CharField(max_length=200, blank=True, verbose_name='Alt عکس ۱۱')
    image_11_caption = models.CharField(max_length=300, blank=True, verbose_name='کپشن عکس ۱۱')
    # Image 12
    image_12 = models.ImageField(upload_to=_fa_property_image_upload_path, blank=True, verbose_name='عکس ۱۲')
    image_12_alt = models.CharField(max_length=200, blank=True, verbose_name='Alt عکس ۱۲')
    image_12_caption = models.CharField(max_length=300, blank=True, verbose_name='کپشن عکس ۱۲')
    # Image 13
    image_13 = models.ImageField(upload_to=_fa_property_image_upload_path, blank=True, verbose_name='عکس ۱۳')
    image_13_alt = models.CharField(max_length=200, blank=True, verbose_name='Alt عکس ۱۳')
    image_13_caption = models.CharField(max_length=300, blank=True, verbose_name='کپشن عکس ۱۳')
    # Image 14
    image_14 = models.ImageField(upload_to=_fa_property_image_upload_path, blank=True, verbose_name='عکس ۱۴')
    image_14_alt = models.CharField(max_length=200, blank=True, verbose_name='Alt عکس ۱۴')
    image_14_caption = models.CharField(max_length=300, blank=True, verbose_name='کپشن عکس ۱۴')
    # Image 15
    image_15 = models.ImageField(upload_to=_fa_property_image_upload_path, blank=True, verbose_name='عکس ۱۵')
    image_15_alt = models.CharField(max_length=200, blank=True, verbose_name='Alt عکس ۱۵')
    image_15_caption = models.CharField(max_length=300, blank=True, verbose_name='کپشن عکس ۱۵')
    
    # ══════════════════════════════════════════════════════════════════════════════
    # 10. VIDEOS — ویدیوها
    # ══════════════════════════════════════════════════════════════════════════════
    video_1 = models.FileField(
        upload_to='persian_cms/properties/videos/',
        blank=True,
        verbose_name='ویدیو ۱',
        help_text='فایل MP4 (حداکثر ۵۰۰ مگابایت)',
    )
    video_1_poster = models.ImageField(
        upload_to='persian_cms/properties/posters/',
        blank=True,
        verbose_name='تصویر پوستر ویدیو ۱',
    )
    video_1_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='عنوان ویدیو ۱',
    )
    video_2 = models.FileField(
        upload_to='persian_cms/properties/videos/',
        blank=True,
        verbose_name='ویدیو ۲',
    )
    video_2_poster = models.ImageField(
        upload_to='persian_cms/properties/posters/',
        blank=True,
        verbose_name='تصویر پوستر ویدیو ۲',
    )
    video_2_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='عنوان ویدیو ۲',
    )
    youtube_url = models.URLField(
        blank=True,
        verbose_name='لینک یوتیوب',
        help_text='آدرس ویدیو یوتیوب (اختیاری)',
    )
    virtual_tour_url = models.URLField(
        blank=True,
        verbose_name='لینک تور مجازی',
        help_text='آدرس تور ۳۶۰ درجه (اختیاری)',
    )
    
    class Meta:
        db_table = "persian_cms_property"
        ordering = ['display_order', '-is_featured', '-created_at']
        verbose_name = 'پروژه ملکی'
        verbose_name_plural = 'پروژه‌های ملکی'
        indexes = [
            models.Index(fields=['is_active', 'display_order']),
            models.Index(fields=['is_featured', 'display_order']),
            models.Index(fields=['property_type', 'is_active']),
            models.Index(fields=['price_tier', 'is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name, allow_unicode=True)
        super().save(*args, **kwargs)
    
    @property
    def main_image(self):
        """Cover image FieldFile — used by list/card templates."""
        # First check dedicated cover image
        if self.cover_image and self.cover_image.name:
            return self.cover_image
        # Then check selected slot
        slot = self.cover_image_slot or 0
        if 1 <= slot <= 15:
            picked = getattr(self, f'image_{slot}', None)
            if picked and picked.name:
                return picked
        # Fallback to first available image
        for i in range(1, 16):
            f = getattr(self, f'image_{i}', None)
            if f and f.name:
                return f
        return None
    
    @property
    def main_image_alt(self):
        """Alt text for cover image."""
        # First check dedicated cover image
        if self.cover_image and self.cover_image.name:
            return self.cover_image_alt or self.name
        # Then check selected slot
        slot = self.cover_image_slot or 0
        if 1 <= slot <= 15:
            picked = getattr(self, f'image_{slot}', None)
            if picked and picked.name:
                return getattr(self, f'image_{slot}_alt', '') or self.name
        # Fallback to first available image
        for i in range(1, 16):
            f = getattr(self, f'image_{i}', None)
            if f and f.name:
                return getattr(self, f'image_{i}_alt', '') or self.name
        return self.name
    
    @property
    def direct_images(self):
        """Non-empty direct image FieldFiles with alt/caption data."""
        result = []
        for i in range(1, 16):
            f = getattr(self, f'image_{i}', None)
            if f and f.name:
                result.append({
                    'image': f,
                    'alt': getattr(self, f'image_{i}_alt', '') or self.name,
                    'caption': getattr(self, f'image_{i}_caption', ''),
                })
        return result
    
    def get_features_list(self):
        """Return list of non-empty feature badges."""
        features = [self.feature_1, self.feature_2, self.feature_3, self.feature_4]
        return [f for f in features if f]
    
    def get_amenities_list(self):
        """Return amenities as a list."""
        if not self.amenities:
            return []
        return [a.strip() for a in self.amenities.split('\n') if a.strip()]
    
    def get_investment_highlights_list(self):
        """Return investment highlights as a list."""
        if not self.investment_highlights:
            return []
        return [h.strip() for h in self.investment_highlights.split('\n') if h.strip()]
    
    def get_bedrooms_display(self):
        """Human-readable bedrooms range."""
        if self.bedrooms_max and self.bedrooms_max != self.bedrooms_min:
            return f'{self.bedrooms_min}-{self.bedrooms_max}'
        return str(self.bedrooms_min)
    
    def get_size_display(self):
        """Human-readable size range."""
        if self.size_min and self.size_max and self.size_max != self.size_min:
            return f'{self.size_min}-{self.size_max} m²'
        if self.size_min:
            return f'{self.size_min} m²'
        if self.size_max:
            return f'{self.size_max} m²'
        return ''
    
    def get_seo_title(self):
        """Return SEO title or fallback to name."""
        return self.meta_title or f'{self.name} | خرید ملک در {self.city}'
    
    def get_seo_description(self):
        """Return SEO description or generate from content."""
        if self.meta_description:
            return self.meta_description
        if self.short_description:
            return self.short_description[:160]
        if self.tagline:
            return self.tagline[:160]
        return f'{self.name} - {self.get_property_type_display()} در {self.area or self.location or self.city}'
    
    def get_absolute_url(self):
        return f'/fa-new/properties/{self.slug}/'


class FaPropertyMedia(PersianTimeStampedModel):
    """Additional media items for Persian properties (beyond the 15 direct slots)."""
    
    property = models.ForeignKey(
        FaProperty,
        on_delete=models.CASCADE,
        related_name='media',
        verbose_name='ملک',
    )
    image = models.ImageField(
        upload_to='persian_cms/properties/gallery/',
        blank=True,
        verbose_name='عکس',
    )
    video = models.FileField(
        upload_to='persian_cms/properties/videos/',
        blank=True,
        verbose_name='ویدیو',
    )
    poster = models.ImageField(
        upload_to='persian_cms/properties/posters/',
        blank=True,
        verbose_name='پوستر ویدیو',
    )
    caption = models.CharField(max_length=200, blank=True, verbose_name='توضیح/ALT')
    is_cover = models.BooleanField(default=False, verbose_name='عکس کاور')
    order = models.PositiveIntegerField(default=0, verbose_name='ترتیب')
    
    class Meta:
        db_table = "persian_cms_property_media"
        ordering = ['order', 'pk']
        verbose_name = 'رسانه ملک'
        verbose_name_plural = 'رسانه‌های ملک'
    
    def __str__(self):
        if self.video:
            return f'ویدیو — {self.property.name}'
        return f'عکس {self.order} — {self.property.name}'


# ══════════════════════════════════════════════════════════════════════════════
# GOLDEN VISA LANDING PAGE MODELS
# ══════════════════════════════════════════════════════════════════════════════

class GVBaseModel(PersianTimeStampedModel):
    """Base abstract model for Golden Visa landing page components."""
    
    class Meta:
        abstract = True


# ── Main Landing Page ─────────────────────────────────────────────────────────

class GoldenVisaLandingPage(GVBaseModel):
    """Main Golden Visa landing page container."""
    
    slug = models.SlugField(
        max_length=100,
        unique=True,
        default='golden-visa-greece',
        verbose_name='اسلاگ',
        help_text='آدرس صفحه: /fa-new/golden-visa/[slug]/',
    )
    title = models.CharField(
        max_length=200,
        default='گلدن ویزای یونان | اقامت اروپا با خرید ملک',
        verbose_name='عنوان صفحه',
    )
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    admin_note = models.TextField(
        blank=True,
        verbose_name='یادداشت ادمین',
        help_text='توضیح کوتاه داخلی برای مدیران (در سایت نمایش داده نمی‌شود)',
    )
    
    class Meta:
        db_table = 'gv_landing_page'
        verbose_name = 'صفحه لندینگ گلدن ویزا'
        verbose_name_plural = 'صفحات لندینگ گلدن ویزا'
    
    def __str__(self):
        return self.title


# ── 1. Hero Section ───────────────────────────────────────────────────────────

class GVHeroSection(GVBaseModel):
    """Hero section at the top of landing page."""
    
    landing_page = models.OneToOneField(
        GoldenVisaLandingPage,
        on_delete=models.CASCADE,
        related_name='hero_section',
        verbose_name='صفحه لندینگ',
    )
    is_enabled = models.BooleanField(default=True, verbose_name='فعال')
    main_title = models.CharField(
        max_length=300,
        default='اقامت اروپا با خرید ملک در یونان',
        verbose_name='عنوان اصلی',
    )
    highlighted_word = models.CharField(
        max_length=100,
        blank=True,
        default='اروپا',
        verbose_name='کلمه برجسته',
        help_text='این کلمه با رنگ طلایی نمایش داده می‌شود',
    )
    subtitle = models.CharField(
        max_length=300,
        blank=True,
        default='گلدن ویزای یونان',
        verbose_name='زیرعنوان',
    )
    description = models.TextField(
        blank=True,
        default='با سرمایه‌گذاری از ۲۵۰ هزار یورو، اقامت ۵ ساله اروپا را برای خود و خانواده‌تان دریافت کنید.',
        verbose_name='توضیحات',
    )
    primary_cta_text = models.CharField(
        max_length=100,
        default='دریافت مشاوره رایگان',
        verbose_name='متن دکمه اصلی',
    )
    primary_cta_link = models.CharField(
        max_length=500,
        default='#contact',
        verbose_name='لینک دکمه اصلی',
    )
    secondary_cta_text = models.CharField(
        max_length=100,
        blank=True,
        default='مشاهده پروژه‌ها',
        verbose_name='متن دکمه ثانویه',
    )
    secondary_cta_link = models.CharField(
        max_length=500,
        blank=True,
        default='#projects',
        verbose_name='لینک دکمه ثانویه',
    )
    background_image = models.ImageField(
        upload_to='gv_landing/hero/',
        blank=True,
        verbose_name='تصویر پس‌زمینه',
    )
    background_video = models.FileField(
        upload_to='gv_landing/hero/videos/',
        blank=True,
        verbose_name='ویدیو پس‌زمینه',
    )
    mobile_background_image = models.ImageField(
        upload_to='gv_landing/hero/',
        blank=True,
        verbose_name='تصویر پس‌زمینه موبایل',
    )
    hero_main_visual = models.ImageField(
        upload_to='gv_landing/hero/',
        blank=True,
        verbose_name='تصویر اصلی هیرو',
        help_text='تصویری که در کنار متن نمایش داده می‌شود',
    )
    hero_image_alt = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Alt Text تصویر هیرو',
        help_text='توضیح تصویر برای سئو و دسترسی‌پذیری',
    )
    display_order = models.PositiveIntegerField(default=1, verbose_name='ترتیب نمایش')
    
    class Meta:
        db_table = 'gv_hero_section'
        verbose_name = '۱. بخش هیرو'
        verbose_name_plural = '۱. بخش هیرو'
    
    def __str__(self):
        return f'Hero - {self.landing_page.title}'


class GVHeroFloatingCard(GVBaseModel):
    """Floating cards shown in hero section."""
    
    hero_section = models.ForeignKey(
        GVHeroSection,
        on_delete=models.CASCADE,
        related_name='floating_cards',
        verbose_name='بخش هیرو',
    )
    title = models.CharField(max_length=100, verbose_name='عنوان کارت')
    text = models.CharField(max_length=200, blank=True, verbose_name='متن کارت')
    icon = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='آیکون',
        help_text='نام آیکون FontAwesome یا کلاس آیکون',
    )
    icon_image = models.ImageField(
        upload_to='gv_landing/icons/',
        blank=True,
        verbose_name='تصویر آیکون',
    )
    display_order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    
    class Meta:
        db_table = 'gv_hero_floating_card'
        ordering = ['display_order', 'pk']
        verbose_name = 'کارت شناور هیرو'
        verbose_name_plural = 'کارت‌های شناور هیرو'
    
    def __str__(self):
        return self.title


# ── 2. Benefits Section ───────────────────────────────────────────────────────

class GVBenefitsSection(GVBaseModel):
    """Benefits section showing advantages of Golden Visa."""
    
    landing_page = models.OneToOneField(
        GoldenVisaLandingPage,
        on_delete=models.CASCADE,
        related_name='benefits_section',
        verbose_name='صفحه لندینگ',
    )
    is_enabled = models.BooleanField(default=True, verbose_name='فعال')
    section_title = models.CharField(
        max_length=200,
        default='مزایای گلدن ویزای یونان',
        verbose_name='عنوان بخش',
    )
    section_subtitle = models.TextField(
        blank=True,
        default='چرا هزاران سرمایه‌گذار، یونان را انتخاب می‌کنند؟',
        verbose_name='زیرعنوان',
    )
    section_description = models.TextField(blank=True, verbose_name='توضیحات بخش')
    background_image = models.ImageField(
        upload_to='gv_landing/benefits/',
        blank=True,
        verbose_name='تصویر پس‌زمینه',
    )
    display_order = models.PositiveIntegerField(default=2, verbose_name='ترتیب نمایش')
    
    class Meta:
        db_table = 'gv_benefits_section'
        verbose_name = '۲. بخش مزایا'
        verbose_name_plural = '۲. بخش مزایا'
    
    def __str__(self):
        return f'Benefits - {self.landing_page.title}'


class GVBenefitCard(GVBaseModel):
    """Individual benefit card."""
    
    benefits_section = models.ForeignKey(
        GVBenefitsSection,
        on_delete=models.CASCADE,
        related_name='benefit_cards',
        verbose_name='بخش مزایا',
    )
    title = models.CharField(max_length=150, verbose_name='عنوان')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    icon = models.CharField(max_length=100, blank=True, verbose_name='آیکون')
    icon_image = models.ImageField(
        upload_to='gv_landing/benefits/icons/',
        blank=True,
        verbose_name='تصویر آیکون',
    )
    card_image = models.ImageField(
        upload_to='gv_landing/benefits/',
        blank=True,
        verbose_name='تصویر کارت',
    )
    button_text = models.CharField(max_length=100, blank=True, verbose_name='متن دکمه')
    button_link = models.CharField(max_length=500, blank=True, verbose_name='لینک دکمه')
    display_order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    
    class Meta:
        db_table = 'gv_benefit_card'
        ordering = ['display_order', 'pk']
        verbose_name = 'کارت مزیت'
        verbose_name_plural = 'کارت‌های مزایا'
    
    def __str__(self):
        return self.title


# ── 3. Eligibility Section ────────────────────────────────────────────────────

class GVEligibilitySection(GVBaseModel):
    """Eligibility requirements section with investment tiers."""
    
    landing_page = models.OneToOneField(
        GoldenVisaLandingPage,
        on_delete=models.CASCADE,
        related_name='eligibility_section',
        verbose_name='صفحه لندینگ',
    )
    is_enabled = models.BooleanField(default=True, verbose_name='فعال')
    section_title = models.CharField(
        max_length=200,
        default='شرایط دریافت گلدن ویزا',
        verbose_name='عنوان بخش',
    )
    section_subtitle = models.TextField(
        blank=True,
        default='سه مسیر سرمایه‌گذاری متناسب با بودجه شما',
        verbose_name='زیرعنوان',
    )
    section_description = models.TextField(blank=True, verbose_name='توضیحات بخش')
    background_image = models.ImageField(
        upload_to='gv_landing/eligibility/',
        blank=True,
        verbose_name='تصویر پس‌زمینه',
    )
    cta_text = models.CharField(
        max_length=100,
        blank=True,
        default='مشاوره رایگان',
        verbose_name='متن دکمه CTA',
    )
    cta_link = models.CharField(
        max_length=500,
        blank=True,
        default='#contact',
        verbose_name='لینک دکمه CTA',
    )
    display_order = models.PositiveIntegerField(default=3, verbose_name='ترتیب نمایش')
    
    class Meta:
        db_table = 'gv_eligibility_section'
        verbose_name = '۳. بخش شرایط واجدین'
        verbose_name_plural = '۳. بخش شرایط واجدین'
    
    def __str__(self):
        return f'Eligibility - {self.landing_page.title}'


class GVEligibilityCard(GVBaseModel):
    """Investment tier card."""
    
    TIER_CHOICES = [
        ('250k', '€250,000'),
        ('400k', '€400,000'),
        ('800k', '€800,000'),
        ('custom', 'سفارشی'),
    ]
    
    eligibility_section = models.ForeignKey(
        GVEligibilitySection,
        on_delete=models.CASCADE,
        related_name='eligibility_cards',
        verbose_name='بخش شرایط',
    )
    investment_amount = models.CharField(
        max_length=100,
        verbose_name='مبلغ سرمایه‌گذاری',
        help_text='مثلاً: €۲۵۰,۰۰۰',
    )
    tier = models.CharField(
        max_length=20,
        choices=TIER_CHOICES,
        default='250k',
        verbose_name='سطح',
    )
    area_name = models.CharField(
        max_length=200,
        verbose_name='نام منطقه',
        help_text='مثلاً: سایر مناطق یونان',
    )
    property_type = models.CharField(max_length=150, blank=True, verbose_name='نوع ملک')
    minimum_area = models.CharField(max_length=100, blank=True, verbose_name='حداقل متراژ')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    badge_text = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='متن نشان',
        help_text='مثلاً: محبوب‌ترین',
    )
    icon = models.CharField(max_length=100, blank=True, verbose_name='آیکون')
    icon_image = models.ImageField(
        upload_to='gv_landing/eligibility/icons/',
        blank=True,
        verbose_name='تصویر آیکون',
    )
    is_featured = models.BooleanField(default=False, verbose_name='برجسته')
    display_order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    
    class Meta:
        db_table = 'gv_eligibility_card'
        ordering = ['display_order', 'pk']
        verbose_name = 'کارت شرایط سرمایه‌گذاری'
        verbose_name_plural = 'کارت‌های شرایط سرمایه‌گذاری'
    
    def __str__(self):
        return f'{self.tier} - {self.area_name}'


# ── 4. Process Section ────────────────────────────────────────────────────────

class GVProcessSection(GVBaseModel):
    """Process steps section."""
    
    landing_page = models.OneToOneField(
        GoldenVisaLandingPage,
        on_delete=models.CASCADE,
        related_name='process_section',
        verbose_name='صفحه لندینگ',
    )
    is_enabled = models.BooleanField(default=True, verbose_name='فعال')
    section_title = models.CharField(
        max_length=200,
        default='مراحل دریافت گلدن ویزا',
        verbose_name='عنوان بخش',
    )
    section_subtitle = models.TextField(
        blank=True,
        default='از مشاوره تا دریافت کارت اقامت',
        verbose_name='زیرعنوان',
    )
    section_description = models.TextField(blank=True, verbose_name='توضیحات بخش')
    display_order = models.PositiveIntegerField(default=4, verbose_name='ترتیب نمایش')
    
    class Meta:
        db_table = 'gv_process_section'
        verbose_name = '۴. بخش مراحل فرآیند'
        verbose_name_plural = '۴. بخش مراحل فرآیند'
    
    def __str__(self):
        return f'Process - {self.landing_page.title}'


class GVProcessStep(GVBaseModel):
    """Individual process step."""
    
    process_section = models.ForeignKey(
        GVProcessSection,
        on_delete=models.CASCADE,
        related_name='steps',
        verbose_name='بخش مراحل',
    )
    step_number = models.PositiveIntegerField(default=1, verbose_name='شماره مرحله')
    title = models.CharField(max_length=200, verbose_name='عنوان مرحله')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    icon = models.CharField(max_length=100, blank=True, verbose_name='آیکون')
    icon_image = models.ImageField(
        upload_to='gv_landing/process/icons/',
        blank=True,
        verbose_name='تصویر آیکون',
    )
    step_image = models.ImageField(
        upload_to='gv_landing/process/',
        blank=True,
        verbose_name='تصویر مرحله',
    )
    estimated_time = models.CharField(
        max_length=100,
        blank=True,
        verbose_name='زمان تقریبی',
        help_text='مثلاً: ۱-۲ هفته',
    )
    display_order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    
    class Meta:
        db_table = 'gv_process_step'
        ordering = ['display_order', 'step_number']
        verbose_name = 'مرحله فرآیند'
        verbose_name_plural = 'مراحل فرآیند'
    
    def __str__(self):
        return f'{self.step_number}. {self.title}'


# ── 5. Statistics Section ─────────────────────────────────────────────────────

class GVStatisticsSection(GVBaseModel):
    """Statistics/counter section."""
    
    landing_page = models.OneToOneField(
        GoldenVisaLandingPage,
        on_delete=models.CASCADE,
        related_name='statistics_section',
        verbose_name='صفحه لندینگ',
    )
    is_enabled = models.BooleanField(default=True, verbose_name='فعال')
    section_title = models.CharField(
        max_length=200,
        blank=True,
        default='آدونیس در یک نگاه',
        verbose_name='عنوان بخش',
    )
    section_subtitle = models.TextField(blank=True, verbose_name='زیرعنوان')
    background_image = models.ImageField(
        upload_to='gv_landing/stats/',
        blank=True,
        verbose_name='تصویر پس‌زمینه',
    )
    display_order = models.PositiveIntegerField(default=5, verbose_name='ترتیب نمایش')
    
    class Meta:
        db_table = 'gv_statistics_section'
        verbose_name = '۵. بخش آمار'
        verbose_name_plural = '۵. بخش آمار'
    
    def __str__(self):
        return f'Statistics - {self.landing_page.title}'


class GVStatItem(GVBaseModel):
    """Individual statistic item."""
    
    statistics_section = models.ForeignKey(
        GVStatisticsSection,
        on_delete=models.CASCADE,
        related_name='stat_items',
        verbose_name='بخش آمار',
    )
    number = models.CharField(
        max_length=50,
        verbose_name='عدد',
        help_text='مثلاً: 500',
    )
    prefix = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='پیشوند',
        help_text='مثلاً: +',
    )
    suffix = models.CharField(
        max_length=20,
        blank=True,
        verbose_name='پسوند',
        help_text='مثلاً: %',
    )
    label = models.CharField(
        max_length=150,
        verbose_name='برچسب',
        help_text='مثلاً: پروژه موفق',
    )
    description = models.CharField(max_length=200, blank=True, verbose_name='توضیح کوتاه')
    icon = models.CharField(max_length=100, blank=True, verbose_name='آیکون')
    icon_image = models.ImageField(
        upload_to='gv_landing/stats/icons/',
        blank=True,
        verbose_name='تصویر آیکون',
    )
    display_order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    
    class Meta:
        db_table = 'gv_stat_item'
        ordering = ['display_order', 'pk']
        verbose_name = 'آیتم آمار'
        verbose_name_plural = 'آیتم‌های آمار'
    
    def __str__(self):
        return f'{self.prefix}{self.number}{self.suffix} {self.label}'


# ── 6. Projects Section ───────────────────────────────────────────────────────

class GVProjectsSection(GVBaseModel):
    """Featured projects section."""
    
    landing_page = models.OneToOneField(
        GoldenVisaLandingPage,
        on_delete=models.CASCADE,
        related_name='projects_section',
        verbose_name='صفحه لندینگ',
    )
    is_enabled = models.BooleanField(default=True, verbose_name='فعال')
    section_title = models.CharField(
        max_length=200,
        default='پروژه‌های منتخب گلدن ویزا',
        verbose_name='عنوان بخش',
    )
    section_subtitle = models.TextField(
        blank=True,
        default='پروژه‌های واجد شرایط گلدن ویزا با بهترین موقعیت مکانی',
        verbose_name='زیرعنوان',
    )
    section_description = models.TextField(blank=True, verbose_name='توضیحات بخش')
    cta_text = models.CharField(
        max_length=100,
        blank=True,
        default='مشاهده همه پروژه‌ها',
        verbose_name='متن دکمه CTA',
    )
    cta_link = models.CharField(
        max_length=500,
        blank=True,
        default='/fa-new/properties/',
        verbose_name='لینک دکمه CTA',
    )
    display_order = models.PositiveIntegerField(default=6, verbose_name='ترتیب نمایش')
    
    class Meta:
        db_table = 'gv_projects_section'
        verbose_name = '۶. بخش پروژه‌ها'
        verbose_name_plural = '۶. بخش پروژه‌ها'
    
    def __str__(self):
        return f'Projects - {self.landing_page.title}'


class GVProject(GVBaseModel):
    """Individual project for Golden Visa landing page."""
    
    STATUS_CHOICES = [
        ('available', 'موجود'),
        ('reserved', 'رزرو شده'),
        ('limited', 'واحدهای محدود'),
        ('sold_out', 'فروخته شده'),
    ]
    
    projects_section = models.ForeignKey(
        GVProjectsSection,
        on_delete=models.CASCADE,
        related_name='projects',
        verbose_name='بخش پروژه‌ها',
    )
    name = models.CharField(max_length=200, verbose_name='نام پروژه')
    short_description = models.TextField(max_length=500, blank=True, verbose_name='توضیح کوتاه')
    main_image = models.ImageField(
        upload_to='gv_landing/projects/',
        verbose_name='تصویر اصلی',
    )
    project_video = models.FileField(
        upload_to='gv_landing/projects/videos/',
        blank=True,
        verbose_name='ویدیو پروژه',
    )
    location_title = models.CharField(max_length=200, blank=True, verbose_name='عنوان موقعیت')
    google_maps_link = models.URLField(blank=True, verbose_name='لینک گوگل مپ')
    area = models.CharField(max_length=100, blank=True, verbose_name='منطقه')
    starting_price = models.CharField(
        max_length=100,
        verbose_name='قیمت شروع',
        help_text='مثلاً: از €۲۵۰,۰۰۰',
    )
    golden_visa_eligible = models.BooleanField(default=True, verbose_name='واجد شرایط گلدن ویزا')
    progress_percentage = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(100)],
        verbose_name='درصد پیشرفت',
    )
    delivery_date = models.CharField(max_length=100, blank=True, verbose_name='تاریخ تحویل')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
        verbose_name='وضعیت',
    )
    cta_text = models.CharField(max_length=100, default='جزئیات پروژه', verbose_name='متن دکمه')
    cta_link = models.CharField(max_length=500, blank=True, verbose_name='لینک دکمه')
    display_order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    
    class Meta:
        db_table = 'gv_project'
        ordering = ['display_order', 'pk']
        verbose_name = 'پروژه گلدن ویزا'
        verbose_name_plural = 'پروژه‌های گلدن ویزا'
    
    def __str__(self):
        return self.name


class GVProjectUnit(GVBaseModel):
    """Individual unit within a project."""
    
    STATUS_CHOICES = [
        ('available', 'موجود'),
        ('reserved', 'رزرو شده'),
        ('sold', 'فروخته شده'),
    ]
    
    project = models.ForeignKey(
        GVProject,
        on_delete=models.CASCADE,
        related_name='units',
        verbose_name='پروژه',
    )
    floor = models.CharField(max_length=50, verbose_name='طبقه')
    unit_number = models.CharField(max_length=50, verbose_name='شماره واحد')
    area_sqm = models.PositiveIntegerField(verbose_name='متراژ (m²)')
    bedrooms = models.PositiveIntegerField(default=1, verbose_name='اتاق خواب')
    bathrooms = models.PositiveIntegerField(default=1, verbose_name='سرویس')
    price = models.CharField(max_length=100, verbose_name='قیمت')
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='available',
        verbose_name='وضعیت',
    )
    notes = models.CharField(max_length=200, blank=True, verbose_name='یادداشت')
    display_order = models.PositiveIntegerField(default=0, verbose_name='ترتیب')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    
    class Meta:
        db_table = 'gv_project_unit'
        ordering = ['display_order', 'floor', 'unit_number']
        verbose_name = 'واحد پروژه'
        verbose_name_plural = 'واحدهای پروژه'
    
    def __str__(self):
        return f'{self.project.name} - طبقه {self.floor} واحد {self.unit_number}'


class GVProjectGalleryImage(GVBaseModel):
    """Gallery image for a project."""
    
    project = models.ForeignKey(
        GVProject,
        on_delete=models.CASCADE,
        related_name='gallery_images',
        verbose_name='پروژه',
    )
    image = models.ImageField(
        upload_to='gv_landing/projects/gallery/',
        verbose_name='تصویر',
    )
    caption = models.CharField(max_length=200, blank=True, verbose_name='توضیح')
    alt_text = models.CharField(max_length=200, blank=True, verbose_name='Alt Text')
    display_order = models.PositiveIntegerField(default=0, verbose_name='ترتیب')
    
    class Meta:
        db_table = 'gv_project_gallery_image'
        ordering = ['display_order', 'pk']
        verbose_name = 'تصویر گالری پروژه'
        verbose_name_plural = 'تصاویر گالری پروژه'
    
    def __str__(self):
        return f'{self.project.name} - تصویر {self.display_order}'


class GVFaPropertyRelation(GVBaseModel):
    """Link existing FaProperty projects to the Golden Visa landing page.
    
    This allows selecting existing properties from persian_cms instead of
    duplicating data in GVProject.
    """
    
    projects_section = models.ForeignKey(
        GVProjectsSection,
        on_delete=models.CASCADE,
        related_name='property_relations',
        verbose_name='بخش پروژه‌ها',
    )
    property = models.ForeignKey(
        'persian_cms.FaProperty',
        on_delete=models.CASCADE,
        related_name='gv_landing_relations',
        verbose_name='پروژه ملکی',
        help_text='پروژه را از لیست پروژه‌های ملکی فارسی انتخاب کنید',
    )
    display_title = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='عنوان نمایشی',
        help_text='عنوان جایگزین برای نمایش در لندینگ (اختیاری)',
    )
    display_description = models.TextField(
        blank=True,
        verbose_name='توضیح نمایشی',
        help_text='توضیح کوتاه جایگزین (اختیاری)',
    )
    badge_text = models.CharField(
        max_length=100,
        blank=True,
        default='مناسب گلدن ویزا',
        verbose_name='متن نشان',
        help_text='مثلاً: مناسب گلدن ویزا، پیشنهاد ویژه',
    )
    display_order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    
    class Meta:
        db_table = 'gv_fa_property_relation'
        ordering = ['display_order', 'pk']
        verbose_name = 'پروژه مرتبط (از FaProperty)'
        verbose_name_plural = 'پروژه‌های مرتبط (از FaProperty)'
        unique_together = [['projects_section', 'property']]
    
    def __str__(self):
        return self.display_title or str(self.property)
    
    def get_title(self):
        """Return display title or original property name."""
        return self.display_title or self.property.name
    
    def get_description(self):
        """Return display description or original property tagline."""
        return self.display_description or self.property.tagline


# ── 7. Family Section ─────────────────────────────────────────────────────────

class GVFamilySection(GVBaseModel):
    """Family members eligibility section."""
    
    landing_page = models.OneToOneField(
        GoldenVisaLandingPage,
        on_delete=models.CASCADE,
        related_name='family_section',
        verbose_name='صفحه لندینگ',
    )
    is_enabled = models.BooleanField(default=True, verbose_name='فعال')
    section_title = models.CharField(
        max_length=200,
        default='اقامت برای تمام اعضای خانواده',
        verbose_name='عنوان بخش',
    )
    section_subtitle = models.TextField(
        blank=True,
        default='با گلدن ویزای یونان، تمام اعضای خانواده شما اقامت دریافت می‌کنند',
        verbose_name='زیرعنوان',
    )
    section_description = models.TextField(blank=True, verbose_name='توضیحات بخش')
    background_image = models.ImageField(
        upload_to='gv_landing/family/',
        blank=True,
        verbose_name='تصویر پس‌زمینه',
    )
    main_image = models.ImageField(
        upload_to='gv_landing/family/',
        blank=True,
        verbose_name='تصویر اصلی',
    )
    display_order = models.PositiveIntegerField(default=7, verbose_name='ترتیب نمایش')
    
    class Meta:
        db_table = 'gv_family_section'
        verbose_name = '۷. بخش اعضای خانواده'
        verbose_name_plural = '۷. بخش اعضای خانواده'
    
    def __str__(self):
        return f'Family - {self.landing_page.title}'


class GVFamilyMemberCard(GVBaseModel):
    """Family member eligibility card."""
    
    family_section = models.ForeignKey(
        GVFamilySection,
        on_delete=models.CASCADE,
        related_name='member_cards',
        verbose_name='بخش خانواده',
    )
    title = models.CharField(
        max_length=150,
        verbose_name='عنوان',
        help_text='مثلاً: متقاضی اصلی',
    )
    description = models.TextField(blank=True, verbose_name='توضیحات')
    icon = models.CharField(max_length=100, blank=True, verbose_name='آیکون')
    icon_image = models.ImageField(
        upload_to='gv_landing/family/icons/',
        blank=True,
        verbose_name='تصویر آیکون',
    )
    display_order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    
    class Meta:
        db_table = 'gv_family_member_card'
        ordering = ['display_order', 'pk']
        verbose_name = 'کارت عضو خانواده'
        verbose_name_plural = 'کارت‌های اعضای خانواده'
    
    def __str__(self):
        return self.title


# ── 8. Documents Section ──────────────────────────────────────────────────────

class GVDocumentsSection(GVBaseModel):
    """Required documents section."""
    
    landing_page = models.OneToOneField(
        GoldenVisaLandingPage,
        on_delete=models.CASCADE,
        related_name='documents_section',
        verbose_name='صفحه لندینگ',
    )
    is_enabled = models.BooleanField(default=True, verbose_name='فعال')
    section_title = models.CharField(
        max_length=200,
        default='مدارک مورد نیاز',
        verbose_name='عنوان بخش',
    )
    section_subtitle = models.TextField(
        blank=True,
        default='لیست مدارک لازم برای ثبت درخواست گلدن ویزا',
        verbose_name='زیرعنوان',
    )
    section_description = models.TextField(blank=True, verbose_name='توضیحات بخش')
    display_order = models.PositiveIntegerField(default=8, verbose_name='ترتیب نمایش')
    
    class Meta:
        db_table = 'gv_documents_section'
        verbose_name = '۸. بخش مدارک'
        verbose_name_plural = '۸. بخش مدارک'
    
    def __str__(self):
        return f'Documents - {self.landing_page.title}'


class GVDocumentItem(GVBaseModel):
    """Individual required document."""
    
    documents_section = models.ForeignKey(
        GVDocumentsSection,
        on_delete=models.CASCADE,
        related_name='document_items',
        verbose_name='بخش مدارک',
    )
    title = models.CharField(max_length=200, verbose_name='عنوان مدرک')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    icon = models.CharField(max_length=100, blank=True, verbose_name='آیکون')
    icon_image = models.ImageField(
        upload_to='gv_landing/documents/icons/',
        blank=True,
        verbose_name='تصویر آیکون',
    )
    is_required = models.BooleanField(default=True, verbose_name='اجباری')
    display_order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    
    class Meta:
        db_table = 'gv_document_item'
        ordering = ['display_order', 'pk']
        verbose_name = 'مدرک مورد نیاز'
        verbose_name_plural = 'مدارک مورد نیاز'
    
    def __str__(self):
        return self.title


# ── 9. Cost Section ───────────────────────────────────────────────────────────

class GVCostSection(GVBaseModel):
    """Costs breakdown section."""
    
    landing_page = models.OneToOneField(
        GoldenVisaLandingPage,
        on_delete=models.CASCADE,
        related_name='cost_section',
        verbose_name='صفحه لندینگ',
    )
    is_enabled = models.BooleanField(default=True, verbose_name='فعال')
    section_title = models.CharField(
        max_length=200,
        default='هزینه‌های دریافت گلدن ویزا',
        verbose_name='عنوان بخش',
    )
    section_subtitle = models.TextField(
        blank=True,
        default='تمام هزینه‌ها به صورت شفاف',
        verbose_name='زیرعنوان',
    )
    section_description = models.TextField(blank=True, verbose_name='توضیحات بخش')
    display_order = models.PositiveIntegerField(default=9, verbose_name='ترتیب نمایش')
    
    class Meta:
        db_table = 'gv_cost_section'
        verbose_name = '۹. بخش هزینه‌ها'
        verbose_name_plural = '۹. بخش هزینه‌ها'
    
    def __str__(self):
        return f'Costs - {self.landing_page.title}'


class GVCostItem(GVBaseModel):
    """Individual cost item."""
    
    cost_section = models.ForeignKey(
        GVCostSection,
        on_delete=models.CASCADE,
        related_name='cost_items',
        verbose_name='بخش هزینه‌ها',
    )
    title = models.CharField(max_length=200, verbose_name='عنوان هزینه')
    amount = models.CharField(
        max_length=100,
        verbose_name='مبلغ',
        help_text='مثلاً: ۳.۰۹٪ یا €۱,۵۰۰',
    )
    currency = models.CharField(max_length=20, blank=True, default='EUR', verbose_name='واحد پول')
    description = models.TextField(blank=True, verbose_name='توضیحات')
    display_order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    
    class Meta:
        db_table = 'gv_cost_item'
        ordering = ['display_order', 'pk']
        verbose_name = 'آیتم هزینه'
        verbose_name_plural = 'آیتم‌های هزینه'
    
    def __str__(self):
        return f'{self.title}: {self.amount}'


# ── 10. Testimonials Section ──────────────────────────────────────────────────

class GVTestimonialsSection(GVBaseModel):
    """Client testimonials section."""
    
    landing_page = models.OneToOneField(
        GoldenVisaLandingPage,
        on_delete=models.CASCADE,
        related_name='testimonials_section',
        verbose_name='صفحه لندینگ',
    )
    is_enabled = models.BooleanField(default=True, verbose_name='فعال')
    section_title = models.CharField(
        max_length=200,
        default='نظرات مشتریان',
        verbose_name='عنوان بخش',
    )
    section_subtitle = models.TextField(
        blank=True,
        default='تجربه واقعی مشتریان آدونیس',
        verbose_name='زیرعنوان',
    )
    section_description = models.TextField(blank=True, verbose_name='توضیحات بخش')
    display_order = models.PositiveIntegerField(default=10, verbose_name='ترتیب نمایش')
    
    class Meta:
        db_table = 'gv_testimonials_section'
        verbose_name = '۱۰. بخش نظرات مشتریان'
        verbose_name_plural = '۱۰. بخش نظرات مشتریان'
    
    def __str__(self):
        return f'Testimonials - {self.landing_page.title}'


class GVTestimonial(GVBaseModel):
    """Individual client testimonial."""
    
    testimonials_section = models.ForeignKey(
        GVTestimonialsSection,
        on_delete=models.CASCADE,
        related_name='testimonials',
        verbose_name='بخش نظرات',
    )
    client_name = models.CharField(max_length=150, verbose_name='نام مشتری')
    client_image = models.ImageField(
        upload_to='gv_landing/testimonials/',
        blank=True,
        verbose_name='تصویر مشتری',
    )
    client_country = models.CharField(max_length=100, blank=True, verbose_name='کشور مشتری')
    review_text = models.TextField(verbose_name='متن نظر')
    video_url = models.URLField(blank=True, verbose_name='لینک ویدیو')
    rating = models.PositiveIntegerField(
        default=5,
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name='امتیاز',
    )
    display_order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    
    class Meta:
        db_table = 'gv_testimonial'
        ordering = ['display_order', 'pk']
        verbose_name = 'نظر مشتری'
        verbose_name_plural = 'نظرات مشتریان'
    
    def __str__(self):
        return f'{self.client_name} - {self.rating}⭐'


# ── 11. FAQ Section ───────────────────────────────────────────────────────────

class GVFAQSection(GVBaseModel):
    """Frequently asked questions section."""
    
    landing_page = models.OneToOneField(
        GoldenVisaLandingPage,
        on_delete=models.CASCADE,
        related_name='faq_section',
        verbose_name='صفحه لندینگ',
    )
    is_enabled = models.BooleanField(default=True, verbose_name='فعال')
    section_title = models.CharField(
        max_length=200,
        default='سوالات متداول',
        verbose_name='عنوان بخش',
    )
    section_subtitle = models.TextField(
        blank=True,
        default='پاسخ به سوالات رایج درباره گلدن ویزای یونان',
        verbose_name='زیرعنوان',
    )
    display_order = models.PositiveIntegerField(default=11, verbose_name='ترتیب نمایش')
    
    class Meta:
        db_table = 'gv_faq_section'
        verbose_name = '۱۱. بخش سوالات متداول'
        verbose_name_plural = '۱۱. بخش سوالات متداول'
    
    def __str__(self):
        return f'FAQ - {self.landing_page.title}'


class GVFAQItem(GVBaseModel):
    """Individual FAQ item."""
    
    CATEGORY_CHOICES = [
        ('general', 'عمومی'),
        ('investment', 'سرمایه‌گذاری'),
        ('process', 'فرآیند'),
        ('family', 'خانواده'),
        ('documents', 'مدارک'),
        ('legal', 'حقوقی'),
        ('other', 'سایر'),
    ]
    
    faq_section = models.ForeignKey(
        GVFAQSection,
        on_delete=models.CASCADE,
        related_name='faq_items',
        verbose_name='بخش سوالات',
    )
    question = models.CharField(max_length=500, verbose_name='سوال')
    answer = models.TextField(verbose_name='پاسخ')
    category = models.CharField(
        max_length=20,
        choices=CATEGORY_CHOICES,
        default='general',
        blank=True,
        verbose_name='دسته‌بندی',
    )
    display_order = models.PositiveIntegerField(default=0, verbose_name='ترتیب نمایش')
    is_active = models.BooleanField(default=True, verbose_name='فعال')
    
    class Meta:
        db_table = 'gv_faq_item'
        ordering = ['display_order', 'pk']
        verbose_name = 'سوال متداول'
        verbose_name_plural = 'سوالات متداول'
    
    def __str__(self):
        return self.question[:50]


# ── 12. Final CTA Section ─────────────────────────────────────────────────────

class GVFinalCTASection(GVBaseModel):
    """Final call-to-action section at the bottom."""
    
    landing_page = models.OneToOneField(
        GoldenVisaLandingPage,
        on_delete=models.CASCADE,
        related_name='final_cta_section',
        verbose_name='صفحه لندینگ',
    )
    is_enabled = models.BooleanField(default=True, verbose_name='فعال')
    title = models.CharField(
        max_length=300,
        default='همین امروز شروع کنید',
        verbose_name='عنوان',
    )
    subtitle = models.CharField(
        max_length=300,
        blank=True,
        default='مشاوره رایگان با کارشناسان آدونیس',
        verbose_name='زیرعنوان',
    )
    description = models.TextField(
        blank=True,
        default='تیم متخصص ما آماده پاسخگویی به تمام سوالات شما درباره گلدن ویزای یونان است.',
        verbose_name='توضیحات',
    )
    background_image = models.ImageField(
        upload_to='gv_landing/cta/',
        blank=True,
        verbose_name='تصویر پس‌زمینه',
    )
    background_video = models.FileField(
        upload_to='gv_landing/cta/videos/',
        blank=True,
        verbose_name='ویدیو پس‌زمینه',
    )
    primary_cta_text = models.CharField(
        max_length=100,
        default='دریافت مشاوره رایگان',
        verbose_name='متن دکمه اصلی',
    )
    primary_cta_link = models.CharField(
        max_length=500,
        default='#contact',
        verbose_name='لینک دکمه اصلی',
    )
    secondary_cta_text = models.CharField(
        max_length=100,
        blank=True,
        default='تماس مستقیم',
        verbose_name='متن دکمه ثانویه',
    )
    secondary_cta_link = models.CharField(
        max_length=500,
        blank=True,
        default='tel:+306985989596',
        verbose_name='لینک دکمه ثانویه',
    )
    whatsapp_number = models.CharField(
        max_length=50,
        blank=True,
        default='+306985989596',
        verbose_name='شماره واتس‌اپ',
    )
    phone_number = models.CharField(
        max_length=50,
        blank=True,
        default='+30 210 7000 570',
        verbose_name='شماره تلفن',
    )
    display_order = models.PositiveIntegerField(default=12, verbose_name='ترتیب نمایش')
    
    class Meta:
        db_table = 'gv_final_cta_section'
        verbose_name = '۱۲. بخش فراخوان نهایی'
        verbose_name_plural = '۱۲. بخش فراخوان نهایی'
    
    def __str__(self):
        return f'Final CTA - {self.landing_page.title}'


# ── 13. SEO Settings ──────────────────────────────────────────────────────────

class GVSEOSettings(GVBaseModel):
    """SEO settings for the landing page."""
    
    landing_page = models.OneToOneField(
        GoldenVisaLandingPage,
        on_delete=models.CASCADE,
        related_name='seo_settings',
        verbose_name='صفحه لندینگ',
    )
    seo_title = models.CharField(
        max_length=70,
        default='گلدن ویزای یونان | اقامت اروپا با خرید ملک | آدونیس',
        verbose_name='عنوان سئو',
        help_text='حداکثر ۷۰ کاراکتر',
    )
    meta_description = models.TextField(
        max_length=160,
        default='با خرید ملک در یونان از ۲۵۰ هزار یورو، اقامت ۵ ساله اروپا برای خود و خانواده دریافت کنید. مشاوره رایگان با آدونیس.',
        verbose_name='Meta Description',
        help_text='حداکثر ۱۶۰ کاراکتر',
    )
    meta_keywords = models.CharField(
        max_length=300,
        blank=True,
        default='گلدن ویزا یونان، اقامت یونان، خرید ملک در یونان، سرمایه‌گذاری یونان، اقامت اروپا',
        verbose_name='Meta Keywords',
    )
    canonical_url = models.URLField(blank=True, verbose_name='Canonical URL')
    og_title = models.CharField(max_length=100, blank=True, verbose_name='OG Title')
    og_description = models.TextField(max_length=300, blank=True, verbose_name='OG Description')
    og_image = models.ImageField(
        upload_to='gv_landing/seo/',
        blank=True,
        verbose_name='OG Image',
        help_text='تصویر اشتراک‌گذاری در شبکه‌های اجتماعی (1200x630 پیکسل)',
    )
    twitter_image = models.ImageField(
        upload_to='gv_landing/seo/',
        blank=True,
        verbose_name='Twitter Image',
    )
    schema_json = models.TextField(
        blank=True,
        verbose_name='Schema JSON-LD',
        help_text='کد JSON-LD برای Rich Snippets',
    )
    robots_index = models.BooleanField(default=True, verbose_name='اجازه ایندکس')
    robots_follow = models.BooleanField(default=True, verbose_name='اجازه دنبال‌کردن لینک‌ها')
    include_in_sitemap = models.BooleanField(default=True, verbose_name='نمایش در Sitemap')
    
    class Meta:
        db_table = 'gv_seo_settings'
        verbose_name = '۱۳. تنظیمات سئو'
        verbose_name_plural = '۱۳. تنظیمات سئو'
    
    def __str__(self):
        return f'SEO - {self.landing_page.title}'


# ── 14. Animation Settings ────────────────────────────────────────────────────

class GVAnimationSettings(GVBaseModel):
    """Animation settings for landing page sections."""
    
    ANIMATION_CHOICES = [
        ('fade-up', 'Fade Up'),
        ('fade-in', 'Fade In'),
        ('slide-left', 'Slide Left'),
        ('slide-right', 'Slide Right'),
        ('scale', 'Scale'),
        ('parallax', 'Parallax'),
        ('none', 'بدون انیمیشن'),
    ]
    
    landing_page = models.OneToOneField(
        GoldenVisaLandingPage,
        on_delete=models.CASCADE,
        related_name='animation_settings',
        verbose_name='صفحه لندینگ',
    )
    animations_enabled = models.BooleanField(default=True, verbose_name='فعال‌سازی انیمیشن‌ها')
    hero_animation = models.CharField(
        max_length=20,
        choices=ANIMATION_CHOICES,
        default='fade-up',
        verbose_name='انیمیشن هیرو',
    )
    benefits_animation = models.CharField(
        max_length=20,
        choices=ANIMATION_CHOICES,
        default='fade-up',
        verbose_name='انیمیشن مزایا',
    )
    eligibility_animation = models.CharField(
        max_length=20,
        choices=ANIMATION_CHOICES,
        default='scale',
        verbose_name='انیمیشن شرایط',
    )
    process_animation = models.CharField(
        max_length=20,
        choices=ANIMATION_CHOICES,
        default='slide-left',
        verbose_name='انیمیشن مراحل',
    )
    stats_animation = models.CharField(
        max_length=20,
        choices=ANIMATION_CHOICES,
        default='fade-up',
        verbose_name='انیمیشن آمار',
    )
    projects_animation = models.CharField(
        max_length=20,
        choices=ANIMATION_CHOICES,
        default='fade-up',
        verbose_name='انیمیشن پروژه‌ها',
    )
    family_animation = models.CharField(
        max_length=20,
        choices=ANIMATION_CHOICES,
        default='fade-in',
        verbose_name='انیمیشن خانواده',
    )
    documents_animation = models.CharField(
        max_length=20,
        choices=ANIMATION_CHOICES,
        default='slide-right',
        verbose_name='انیمیشن مدارک',
    )
    cost_animation = models.CharField(
        max_length=20,
        choices=ANIMATION_CHOICES,
        default='fade-up',
        verbose_name='انیمیشن هزینه‌ها',
    )
    testimonials_animation = models.CharField(
        max_length=20,
        choices=ANIMATION_CHOICES,
        default='fade-in',
        verbose_name='انیمیشن نظرات',
    )
    faq_animation = models.CharField(
        max_length=20,
        choices=ANIMATION_CHOICES,
        default='fade-up',
        verbose_name='انیمیشن سوالات',
    )
    cta_animation = models.CharField(
        max_length=20,
        choices=ANIMATION_CHOICES,
        default='scale',
        verbose_name='انیمیشن CTA',
    )
    animation_duration = models.PositiveIntegerField(
        default=600,
        verbose_name='مدت انیمیشن (میلی‌ثانیه)',
    )
    animation_delay = models.PositiveIntegerField(
        default=100,
        verbose_name='تاخیر انیمیشن (میلی‌ثانیه)',
    )
    parallax_enabled = models.BooleanField(default=True, verbose_name='فعال‌سازی پارالکس')
    floating_cards_enabled = models.BooleanField(default=True, verbose_name='فعال‌سازی کارت‌های شناور')
    
    class Meta:
        db_table = 'gv_animation_settings'
        verbose_name = '۱۴. تنظیمات انیمیشن'
        verbose_name_plural = '۱۴. تنظیمات انیمیشن'
    
    def __str__(self):
        return f'Animations - {self.landing_page.title}'


# ── 15. Design Settings ───────────────────────────────────────────────────────

class GVDesignSettings(GVBaseModel):
    """Design/theming settings for landing page."""
    
    CARD_STYLE_CHOICES = [
        ('solid', 'جامد'),
        ('glass', 'شیشه‌ای (Glassmorphism)'),
        ('minimal', 'مینیمال'),
    ]
    
    FONT_FAMILY_CHOICES = [
        ('vazirmatn', 'وزیر‌متن'),
        ('estedad', 'استعداد'),
        ('dana', 'دانا'),
        ('yekan', 'یکان'),
        ('sahel', 'ساحل'),
        ('custom', 'سفارشی'),
    ]
    
    landing_page = models.OneToOneField(
        GoldenVisaLandingPage,
        on_delete=models.CASCADE,
        related_name='design_settings',
        verbose_name='صفحه لندینگ',
    )
    primary_color = models.CharField(
        max_length=20,
        default='#c9a227',
        verbose_name='رنگ اصلی',
        help_text='رنگ طلایی پیش‌فرض: #c9a227',
    )
    secondary_color = models.CharField(
        max_length=20,
        default='#0a1530',
        verbose_name='رنگ ثانویه',
        help_text='رنگ تیره پیش‌فرض: #0a1530',
    )
    accent_color = models.CharField(
        max_length=20,
        default='#3b82f6',
        verbose_name='رنگ تاکیدی',
    )
    background_color = models.CharField(
        max_length=20,
        default='#0a0f1a',
        verbose_name='رنگ پس‌زمینه',
    )
    text_color = models.CharField(
        max_length=20,
        default='#ffffff',
        verbose_name='رنگ متن',
    )
    section_spacing = models.CharField(
        max_length=20,
        default='120px',
        verbose_name='فاصله بین بخش‌ها',
    )
    border_radius = models.CharField(
        max_length=20,
        default='16px',
        verbose_name='گردی گوشه‌ها',
    )
    card_style = models.CharField(
        max_length=20,
        choices=CARD_STYLE_CHOICES,
        default='glass',
        verbose_name='استایل کارت‌ها',
    )
    font_family = models.CharField(
        max_length=20,
        choices=FONT_FAMILY_CHOICES,
        default='vazirmatn',
        verbose_name='فونت اصلی',
    )
    custom_font_url = models.URLField(
        blank=True,
        verbose_name='لینک فونت سفارشی',
        help_text='لینک Google Fonts یا فونت سفارشی',
    )
    custom_css = models.TextField(
        blank=True,
        verbose_name='CSS سفارشی',
        help_text='کد CSS اضافی برای سفارشی‌سازی',
    )
    
    class Meta:
        db_table = 'gv_design_settings'
        verbose_name = '۱۵. تنظیمات طراحی'
        verbose_name_plural = '۱۵. تنظیمات طراحی'
    
    def __str__(self):
        return f'Design - {self.landing_page.title}'
