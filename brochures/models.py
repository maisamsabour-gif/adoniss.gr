import os
from django.conf import settings
from django.db import models
from django.urls import reverse
from django.utils.text import slugify

from core.seo_mixin import SEOContentInterface


class Brochure(SEOContentInterface, models.Model):
    STATUS_PENDING    = 'pending'
    STATUS_PROCESSING = 'processing'
    STATUS_READY      = 'ready'
    STATUS_FAILED     = 'failed'

    STATUS_CHOICES = [
        (STATUS_PENDING,    'Pending Conversion'),
        (STATUS_PROCESSING, 'Processing…'),
        (STATUS_READY,      'Ready'),
        (STATUS_FAILED,     'Conversion Failed'),
    ]

    title        = models.CharField(max_length=200, verbose_name='Title')
    slug         = models.SlugField(
        max_length=200, unique=True, verbose_name='URL Slug',
        help_text='Auto-generated from title. Used in URL: /brochure/<slug>/',
    )
    pdf_file     = models.FileField(
        upload_to='brochures/pdf/', verbose_name='PDF File',
        help_text='Upload the brochure PDF. Pages will be auto-converted to images.',
    )
    cover_image  = models.ImageField(
        upload_to='brochures/covers/', blank=True, null=True,
        verbose_name='Cover Image',
        help_text='Optional. Auto-generated from page 1 if left blank.',
    )
    page_count   = models.PositiveIntegerField(default=0, verbose_name='Page Count')
    page_width   = models.PositiveIntegerField(default=0, verbose_name='Page Width (px)')
    page_height  = models.PositiveIntegerField(default=0, verbose_name='Page Height (px)')

    conversion_status = models.CharField(
        max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING,
        verbose_name='Conversion Status',
    )
    conversion_error = models.TextField(blank=True, verbose_name='Conversion Error Log')

    is_published = models.BooleanField(default=True, verbose_name='Published')

    # ── SEO ──────────────────────────────────────────────────────────────────
    seo_title = models.CharField(max_length=70, blank=True, verbose_name='SEO Title')
    meta_description = models.CharField(max_length=160, blank=True, verbose_name='Meta Description')
    focus_keyword = models.CharField(max_length=120, blank=True, verbose_name='Focus Keyword')
    canonical_url = models.URLField(blank=True, verbose_name='Canonical URL')
    robots_index = models.BooleanField(default=True, verbose_name='Allow indexing')
    robots_follow = models.BooleanField(default=True, verbose_name='Follow links')
    og_image = models.ImageField(upload_to='seo/og/', blank=True, null=True, verbose_name='OG Image')
    cover_image_alt = models.CharField(max_length=200, blank=True, verbose_name='Cover Image ALT Text')
    seo_allow_publish_override = models.BooleanField(default=False, verbose_name='Override SEO check')

    created_at   = models.DateTimeField(auto_now_add=True)
    updated_at   = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Brochure'
        verbose_name_plural = 'Brochures'
        indexes = [
            models.Index(fields=['slug']),
            models.Index(fields=['is_published', 'conversion_status']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        from core.models import _record_slug_change
        _record_slug_change(self, slug_fields={'en': 'slug'})
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        return reverse('brochure_viewer', kwargs={'slug': self.slug})

    # ── Helpers ──────────────────────────────────────────────────────────────

    def pages_dir(self):
        """Absolute filesystem path to the converted images directory."""
        return os.path.join(settings.MEDIA_ROOT, 'brochures', self.slug)

    def get_page_url(self, n: int) -> str:
        """Return the MEDIA URL for page n (1-indexed)."""
        return f'{settings.MEDIA_URL}brochures/{self.slug}/page-{n:03d}.webp'

    def get_all_page_urls(self) -> list:
        return [self.get_page_url(i) for i in range(1, self.page_count + 1)]

    @property
    def is_ready(self):
        return self.conversion_status == self.STATUS_READY

    @property
    def aspect_ratio(self):
        """Width/height ratio (float), default A4 portrait if unknown."""
        if self.page_width and self.page_height:
            return self.page_width / self.page_height
        return 0.707  # A4 portrait ≈ 1/√2
