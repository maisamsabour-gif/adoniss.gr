from django.db import models
from django.utils import timezone


class FaContentPipeline(models.Model):
    STATUS_PENDING    = 'pending'
    STATUS_GENERATING = 'generating'
    STATUS_REVIEW     = 'review'
    STATUS_PUBLISHED  = 'published'
    STATUS_FAILED     = 'failed'

    STATUS_CHOICES = [
        (STATUS_PENDING,    'در انتظار'),
        (STATUS_GENERATING, 'در حال تولید'),
        (STATUS_REVIEW,     'بررسی'),
        (STATUS_PUBLISHED,  'منتشر شده'),
        (STATUS_FAILED,     'خطا'),
    ]

    keyword          = models.CharField(max_length=300, verbose_name='کلیدواژه اصلی')
    focus_keywords   = models.TextField(blank=True, verbose_name='کلیدواژه‌های تمرکز')
    status           = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='وضعیت',
        db_index=True,
    )

    title            = models.CharField(max_length=300, blank=True, verbose_name='عنوان')
    slug             = models.SlugField(
        max_length=400,
        unique=True,
        allow_unicode=True,
        blank=True,
        null=True,
        verbose_name='اسلاگ',
    )
    content          = models.TextField(blank=True, verbose_name='محتوا')
    excerpt          = models.TextField(blank=True, verbose_name='چکیده')
    meta_title       = models.CharField(max_length=120, blank=True, verbose_name='عنوان متا')
    meta_description = models.CharField(max_length=320, blank=True, verbose_name='توضیحات متا')

    cover_image_url    = models.URLField(max_length=1000, blank=True, verbose_name='آدرس تصویر')
    cover_image_thumb  = models.URLField(max_length=1000, blank=True, verbose_name='آدرس تامبنیل')
    cover_image_credit = models.CharField(max_length=300, blank=True, verbose_name='کردیت تصویر')
    unsplash_photo_id  = models.CharField(max_length=50, blank=True, verbose_name='شناسه Unsplash')

    scheduled_publish = models.DateTimeField(null=True, blank=True, verbose_name='زمان انتشار برنامه‌ریزی‌شده')
    published_at      = models.DateTimeField(null=True, blank=True, verbose_name='زمان انتشار')

    ai_generated = models.BooleanField(default=True, verbose_name='تولید شده با AI')
    error_log    = models.TextField(blank=True, verbose_name='لاگ خطا')
    views        = models.IntegerField(default=0, verbose_name='بازدید')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='ایجاد شده در')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='به‌روز شده در')

    class Meta:
        verbose_name          = 'محتوای SEO فارسی'
        verbose_name_plural   = 'محتوای SEO فارسی'
        ordering              = ['-created_at']

    def __str__(self):
        return self.title or self.keyword

    def publish(self):
        self.status      = self.STATUS_PUBLISHED
        self.published_at = timezone.now()
        self.save(update_fields=['status', 'published_at', 'updated_at'])


class ContentSchedule(models.Model):
    is_active      = models.BooleanField(default=True, verbose_name='فعال')
    posts_per_week = models.IntegerField(default=3, verbose_name='پست در هفته')
    base_topics    = models.TextField(
        default='اقامت یونان,گلدن ویزا,خرید ملک یونان,مهاجرت به یونان',
        verbose_name='موضوعات پایه',
        help_text='هر موضوع را با کاما جدا کنید',
    )
    last_run = models.DateTimeField(null=True, blank=True, verbose_name='آخرین اجرا')

    class Meta:
        verbose_name        = 'برنامه تولید محتوا'
        verbose_name_plural = 'برنامه‌های تولید محتوا'

    def __str__(self):
        state = 'فعال' if self.is_active else 'غیرفعال'
        return f'برنامه {state} — {self.posts_per_week} پست/هفته'


# ── English SEO Content Pipeline ─────────────────────────────────────────────

class EnContentPipeline(models.Model):
    STATUS_PENDING    = 'pending'
    STATUS_GENERATING = 'generating'
    STATUS_REVIEW     = 'review'
    STATUS_PUBLISHED  = 'published'
    STATUS_FAILED     = 'failed'

    STATUS_CHOICES = [
        (STATUS_PENDING,    'Pending'),
        (STATUS_GENERATING, 'Generating'),
        (STATUS_REVIEW,     'Review'),
        (STATUS_PUBLISHED,  'Published'),
        (STATUS_FAILED,     'Failed'),
    ]

    LANGUAGE_CHOICES = [
        ('en', 'English'),
        ('tr', 'Turkish'),
    ]

    keyword          = models.CharField(max_length=300, verbose_name='Main Keyword')
    focus_keywords   = models.TextField(blank=True, verbose_name='Focus Keywords')
    language         = models.CharField(
        max_length=5,
        choices=LANGUAGE_CHOICES,
        default='en',
        verbose_name='Language',
    )
    status           = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=STATUS_PENDING,
        verbose_name='Status',
        db_index=True,
    )

    title            = models.CharField(max_length=300, blank=True, verbose_name='Title')
    slug             = models.SlugField(
        max_length=400,
        unique=True,
        allow_unicode=True,
        blank=True,
        null=True,
        verbose_name='Slug',
    )
    content          = models.TextField(blank=True, verbose_name='Content')
    excerpt          = models.TextField(blank=True, verbose_name='Excerpt')
    meta_title       = models.CharField(max_length=120, blank=True, verbose_name='Meta Title')
    meta_description = models.CharField(max_length=320, blank=True, verbose_name='Meta Description')

    cover_image_url    = models.URLField(max_length=1000, blank=True, verbose_name='Cover Image URL')
    cover_image_thumb  = models.URLField(max_length=1000, blank=True, verbose_name='Thumbnail URL')
    cover_image_credit = models.CharField(max_length=300, blank=True, verbose_name='Image Credit')
    unsplash_photo_id  = models.CharField(max_length=50, blank=True, verbose_name='Unsplash Photo ID')

    scheduled_publish = models.DateTimeField(null=True, blank=True, verbose_name='Scheduled Publish')
    published_at      = models.DateTimeField(null=True, blank=True, verbose_name='Published At')

    ai_generated = models.BooleanField(default=True, verbose_name='AI Generated')
    error_log    = models.TextField(blank=True, verbose_name='Error Log')
    views        = models.IntegerField(default=0, verbose_name='Views')

    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Created At')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Updated At')

    class Meta:
        verbose_name        = 'English SEO Content'
        verbose_name_plural = 'English SEO Contents'
        ordering            = ['-created_at']

    def __str__(self):
        return self.title or self.keyword

    def publish(self):
        self.status      = self.STATUS_PUBLISHED
        self.published_at = timezone.now()
        self.save(update_fields=['status', 'published_at', 'updated_at'])
