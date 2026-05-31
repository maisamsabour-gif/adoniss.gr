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
