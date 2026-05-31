"""
FA SEO Content Pipeline — Django Admin (Unfold).

YouTube-Studio-style list view with thumbnail, info column, status badges,
view counts, and one-click action buttons.
"""
import threading

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.urls import path, reverse
from django.utils import timezone
from django.utils.html import format_html
from unfold.admin import ModelAdmin

from .models_pipeline import ContentSchedule, FaContentPipeline


# ─────────────────────────────────────────────────────────────────────────────
# Status badge colours
# ─────────────────────────────────────────────────────────────────────────────

_STATUS_STYLES = {
    FaContentPipeline.STATUS_PENDING: (
        'background:#f3f4f6;color:#374151;border:1px solid #d1d5db;'
    ),
    FaContentPipeline.STATUS_GENERATING: (
        'background:#dbeafe;color:#1d4ed8;border:1px solid #93c5fd;'
    ),
    FaContentPipeline.STATUS_REVIEW: (
        'background:#fef3c7;color:#92400e;border:1px solid #fcd34d;'
    ),
    FaContentPipeline.STATUS_PUBLISHED: (
        'background:#d1fae5;color:#065f46;border:1px solid #6ee7b7;'
    ),
    FaContentPipeline.STATUS_FAILED: (
        'background:#fee2e2;color:#991b1b;border:1px solid #fca5a5;'
    ),
}

_STATUS_LABELS = {
    FaContentPipeline.STATUS_PENDING:    'در انتظار',
    FaContentPipeline.STATUS_GENERATING: '⟳ در حال تولید',
    FaContentPipeline.STATUS_REVIEW:     'بررسی',
    FaContentPipeline.STATUS_PUBLISHED:  '✓ منتشر',
    FaContentPipeline.STATUS_FAILED:     '✕ خطا',
}


# ─────────────────────────────────────────────────────────────────────────────
# Main Admin
# ─────────────────────────────────────────────────────────────────────────────

@admin.register(FaContentPipeline)
class FaContentPipelineAdmin(ModelAdmin):
    list_display        = [
        'thumbnail_preview',
        'title_and_info',
        'status_badge',
        'views_count',
        'created_at',
        'action_buttons',
    ]
    list_display_links  = None          # clicking thumbnail/title → change view
    search_fields       = ['keyword', 'title']
    list_filter         = ['status']
    list_per_page       = 20
    readonly_fields     = [
        'created_at', 'updated_at', 'published_at',
        'cover_image_url', 'cover_image_thumb',
        'cover_image_credit', 'unsplash_photo_id',
        'ai_generated', 'error_log', 'views',
    ]

    fieldsets = (
        ('📝 محتوا', {
            'fields': (
                'keyword', 'status', 'title', 'slug',
                'excerpt', 'content',
            ),
        }),
        ('🔍 SEO', {
            'fields': (
                'focus_keywords', 'meta_title', 'meta_description',
            ),
        }),
        ('🖼 تصویر', {
            'fields': (
                'cover_image_url', 'cover_image_thumb',
                'cover_image_credit', 'unsplash_photo_id',
            ),
        }),
        ('⚙ تنظیمات', {
            'fields': (
                'ai_generated', 'views',
                'scheduled_publish', 'published_at',
                'error_log',
                'created_at', 'updated_at',
            ),
        }),
    )

    # ── Custom URLs ───────────────────────────────────────────────────────────

    def get_urls(self):
        custom = [
            path(
                'generate/<int:item_id>/',
                self.admin_site.admin_view(self.generate_view),
                name='pipeline_generate',
            ),
            path(
                'publish/<int:item_id>/',
                self.admin_site.admin_view(self.publish_view),
                name='pipeline_publish',
            ),
        ]
        return custom + super().get_urls()

    def _changelist_url(self):
        return reverse('admin:properties_facontentpipeline_changelist')

    def generate_view(self, request, item_id):
        """Trigger run_pipeline in a background thread and redirect back."""
        try:
            item = FaContentPipeline.objects.get(pk=item_id)
        except FaContentPipeline.DoesNotExist:
            messages.error(request, 'محتوا پیدا نشد.')
            return HttpResponseRedirect(self._changelist_url())

        if item.status == FaContentPipeline.STATUS_GENERATING:
            messages.warning(request, f'«{item.keyword}» در حال تولید است.')
            return HttpResponseRedirect(self._changelist_url())

        from .pipeline_service import run_pipeline

        def _run():
            run_pipeline(item)

        t = threading.Thread(target=_run, daemon=True)
        t.start()

        messages.success(
            request,
            f'🚀 تولید محتوا برای «{item.keyword}» شروع شد. '
            'صفحه را رفرش کنید تا وضعیت به‌روز شود.',
        )
        return HttpResponseRedirect(self._changelist_url())

    def publish_view(self, request, item_id):
        """Set status→published and save published_at."""
        try:
            item = FaContentPipeline.objects.get(pk=item_id)
        except FaContentPipeline.DoesNotExist:
            messages.error(request, 'محتوا پیدا نشد.')
            return HttpResponseRedirect(self._changelist_url())

        item.status      = FaContentPipeline.STATUS_PUBLISHED
        item.published_at = timezone.now()
        item.save(update_fields=['status', 'published_at', 'updated_at'])

        # Push the generated content to the live Persian blog (/fa-new/blog/).
        try:
            from .pipeline_service import publish_to_persian_blog
            post = publish_to_persian_blog(item)
            messages.success(
                request,
                f'✓ «{item.title or item.keyword}» منتشر شد و روی سایت قرار گرفت: '
                f'/fa-new/blog/{post.slug}/',
            )
        except Exception as exc:
            messages.warning(
                request,
                f'وضعیت پایپ‌لاین «منتشر» شد، ولی انتقال به بلاگ زنده خطا داد: {exc}',
            )
        return HttpResponseRedirect(self._changelist_url())

    # ── list_display columns ──────────────────────────────────────────────────

    @admin.display(description='تصویر')
    def thumbnail_preview(self, obj):
        style = (
            'width:160px;height:90px;object-fit:cover;'
            'border-radius:8px;display:block;'
        )
        if obj.cover_image_thumb:
            change_url = reverse(
                'admin:properties_facontentpipeline_change', args=[obj.pk]
            )
            return format_html(
                '<a href="{url}">'
                '<img src="{src}" style="{style}" loading="lazy" />'
                '</a>',
                url=change_url, src=obj.cover_image_thumb, style=style,
            )
        placeholder_style = (
            'width:160px;height:90px;border-radius:8px;'
            'background:#e5e7eb;display:flex;align-items:center;'
            'justify-content:center;font-size:12px;color:#9ca3af;'
        )
        change_url = reverse(
            'admin:properties_facontentpipeline_change', args=[obj.pk]
        )
        return format_html(
            '<a href="{url}" style="text-decoration:none;">'
            '<div style="{style}">بدون تصویر</div>'
            '</a>',
            url=change_url, style=placeholder_style,
        )

    @admin.display(description='عنوان / اطلاعات')
    def title_and_info(self, obj):
        change_url = reverse(
            'admin:properties_facontentpipeline_change', args=[obj.pk]
        )
        title_html = format_html(
            '<a href="{url}" style="font-weight:600;color:#111827;'
            'text-decoration:none;font-size:14px;">{title}</a>',
            url=change_url,
            title=obj.title or '(بدون عنوان)',
        )
        keyword_html = format_html(
            '<div style="font-size:12px;color:#6b7280;margin-top:2px;">'
            '🔑 {kw}</div>',
            kw=obj.keyword,
        )
        excerpt = (obj.excerpt or '')[:100]
        excerpt_html = format_html(
            '<div style="font-size:12px;color:#9ca3af;margin-top:4px;">'
            '{exc}</div>',
            exc=excerpt,
        ) if excerpt else ''

        return format_html(
            '<div>{title}{kw}{exc}</div>',
            title=title_html, kw=keyword_html, exc=excerpt_html,
        )

    @admin.display(description='وضعیت')
    def status_badge(self, obj):
        style = (
            'display:inline-block;padding:3px 10px;border-radius:20px;'
            'font-size:12px;font-weight:600;'
            + _STATUS_STYLES.get(obj.status, '')
        )
        label = _STATUS_LABELS.get(obj.status, obj.status)
        return format_html('<span style="{}">{}</span>', style, label)

    @admin.display(description='👁 بازدید')
    def views_count(self, obj):
        return format_html(
            '<span style="font-size:13px;">👁 {}</span>',
            obj.views,
        )

    @admin.display(description='عملیات')
    def action_buttons(self, obj):
        if obj.status == FaContentPipeline.STATUS_PENDING:
            url = reverse('admin:pipeline_generate', args=[obj.pk])
            return format_html(
                '<a href="{}" style="'
                'background:#16a34a;color:#fff;padding:5px 12px;'
                'border-radius:6px;text-decoration:none;font-size:12px;'
                'font-weight:600;white-space:nowrap;">'
                '▶ تولید</a>',
                url,
            )

        if obj.status == FaContentPipeline.STATUS_GENERATING:
            return format_html(
                '<span style="color:#1d4ed8;font-size:12px;">⟳ در حال پردازش…</span>'
            )

        if obj.status == FaContentPipeline.STATUS_REVIEW:
            url = reverse('admin:pipeline_publish', args=[obj.pk])
            return format_html(
                '<a href="{}" style="'
                'background:#2563eb;color:#fff;padding:5px 12px;'
                'border-radius:6px;text-decoration:none;font-size:12px;'
                'font-weight:600;white-space:nowrap;">'
                '✓ انتشار</a>',
                url,
            )

        if obj.status == FaContentPipeline.STATUS_PUBLISHED:
            return format_html(
                '<span style="'
                'background:#f3f4f6;color:#374151;padding:5px 12px;'
                'border-radius:6px;font-size:12px;font-weight:600;">'
                '↗ منتشر</span>'
            )

        if obj.status == FaContentPipeline.STATUS_FAILED:
            url = reverse('admin:pipeline_generate', args=[obj.pk])
            return format_html(
                '<a href="{}" style="'
                'background:#dc2626;color:#fff;padding:5px 12px;'
                'border-radius:6px;text-decoration:none;font-size:12px;'
                'font-weight:600;white-space:nowrap;">'
                '↺ تلاش مجدد</a>',
                url,
            )

        return format_html('<span style="color:#9ca3af;">—</span>')


# ─────────────────────────────────────────────────────────────────────────────
# ContentSchedule Admin
# ─────────────────────────────────────────────────────────────────────────────

@admin.register(ContentSchedule)
class ContentScheduleAdmin(ModelAdmin):
    list_display   = ['__str__', 'is_active', 'posts_per_week', 'last_run']
    list_editable  = ['is_active', 'posts_per_week']
    fields         = ['is_active', 'posts_per_week', 'base_topics', 'last_run']
    readonly_fields = ['last_run']


# ─────────────────────────────────────────────────────────────────────────────
# English SEO Content Pipeline Admin
# ─────────────────────────────────────────────────────────────────────────────

from .models_pipeline import EnContentPipeline  # noqa: E402

_EN_STATUS_STYLES = {
    EnContentPipeline.STATUS_PENDING: (
        'background:#f3f4f6;color:#374151;border:1px solid #d1d5db;'
    ),
    EnContentPipeline.STATUS_GENERATING: (
        'background:#dbeafe;color:#1d4ed8;border:1px solid #93c5fd;'
    ),
    EnContentPipeline.STATUS_REVIEW: (
        'background:#fef3c7;color:#92400e;border:1px solid #fcd34d;'
    ),
    EnContentPipeline.STATUS_PUBLISHED: (
        'background:#d1fae5;color:#065f46;border:1px solid #6ee7b7;'
    ),
    EnContentPipeline.STATUS_FAILED: (
        'background:#fee2e2;color:#991b1b;border:1px solid #fca5a5;'
    ),
}

_EN_STATUS_LABELS = {
    EnContentPipeline.STATUS_PENDING:    'Pending',
    EnContentPipeline.STATUS_GENERATING: '⟳ Generating',
    EnContentPipeline.STATUS_REVIEW:     'Review',
    EnContentPipeline.STATUS_PUBLISHED:  '✓ Published',
    EnContentPipeline.STATUS_FAILED:     '✕ Failed',
}


@admin.register(EnContentPipeline)
class EnContentPipelineAdmin(ModelAdmin):
    list_display        = [
        'thumbnail_preview',
        'title_and_info',
        'status_badge',
        'views_count',
        'created_at',
        'action_buttons',
    ]
    list_display_links  = None
    search_fields       = ['keyword', 'title']
    list_filter         = ['status', 'language']
    list_per_page       = 20
    readonly_fields     = [
        'created_at', 'updated_at', 'published_at',
        'cover_image_url', 'cover_image_thumb',
        'cover_image_credit', 'unsplash_photo_id',
        'ai_generated', 'error_log', 'views',
    ]

    fieldsets = (
        ('📝 Content', {
            'fields': (
                'keyword', 'language', 'status', 'title', 'slug',
                'excerpt', 'content',
            ),
        }),
        ('🔍 SEO', {
            'fields': (
                'focus_keywords', 'meta_title', 'meta_description',
            ),
        }),
        ('🖼 Cover Image', {
            'fields': (
                'cover_image_url', 'cover_image_thumb',
                'cover_image_credit', 'unsplash_photo_id',
            ),
        }),
        ('⚙ Settings', {
            'fields': (
                'ai_generated', 'views',
                'scheduled_publish', 'published_at',
                'error_log',
                'created_at', 'updated_at',
            ),
        }),
    )

    # ── Custom URLs ───────────────────────────────────────────────────────────

    def get_urls(self):
        custom = [
            path(
                'en-generate/<int:item_id>/',
                self.admin_site.admin_view(self.generate_view),
                name='en_pipeline_generate',
            ),
            path(
                'en-publish/<int:item_id>/',
                self.admin_site.admin_view(self.publish_view),
                name='en_pipeline_publish',
            ),
        ]
        return custom + super().get_urls()

    def _changelist_url(self):
        return reverse('admin:properties_encontentpipeline_changelist')

    def generate_view(self, request, item_id):
        try:
            item = EnContentPipeline.objects.get(pk=item_id)
        except EnContentPipeline.DoesNotExist:
            messages.error(request, 'Content not found.')
            return HttpResponseRedirect(self._changelist_url())

        if item.status == EnContentPipeline.STATUS_GENERATING:
            messages.warning(request, f'"{item.keyword}" is already generating.')
            return HttpResponseRedirect(self._changelist_url())

        from .pipeline_service import run_english_pipeline

        def _run():
            run_english_pipeline(item)

        t = threading.Thread(target=_run, daemon=True)
        t.start()

        messages.success(
            request,
            f'🚀 Content generation started for "{item.keyword}". '
            'Refresh the page to see the updated status.',
        )
        return HttpResponseRedirect(self._changelist_url())

    def publish_view(self, request, item_id):
        try:
            item = EnContentPipeline.objects.get(pk=item_id)
        except EnContentPipeline.DoesNotExist:
            messages.error(request, 'Content not found.')
            return HttpResponseRedirect(self._changelist_url())

        item.status       = EnContentPipeline.STATUS_PUBLISHED
        item.published_at = timezone.now()
        item.save(update_fields=['status', 'published_at', 'updated_at'])
        messages.success(request, f'✓ "{item.title or item.keyword}" published.')
        return HttpResponseRedirect(self._changelist_url())

    # ── list_display columns ──────────────────────────────────────────────────

    @admin.display(description='Thumbnail')
    def thumbnail_preview(self, obj):
        style = (
            'width:160px;height:90px;object-fit:cover;'
            'border-radius:8px;display:block;'
        )
        if obj.cover_image_thumb:
            change_url = reverse(
                'admin:properties_encontentpipeline_change', args=[obj.pk]
            )
            return format_html(
                '<a href="{url}">'
                '<img src="{src}" style="{style}" loading="lazy" />'
                '</a>',
                url=change_url, src=obj.cover_image_thumb, style=style,
            )
        placeholder_style = (
            'width:160px;height:90px;border-radius:8px;'
            'background:#e5e7eb;display:flex;align-items:center;'
            'justify-content:center;font-size:12px;color:#9ca3af;'
        )
        change_url = reverse(
            'admin:properties_encontentpipeline_change', args=[obj.pk]
        )
        return format_html(
            '<a href="{url}" style="text-decoration:none;">'
            '<div style="{style}">No image</div>'
            '</a>',
            url=change_url, style=placeholder_style,
        )

    @admin.display(description='Title / Info')
    def title_and_info(self, obj):
        change_url = reverse(
            'admin:properties_encontentpipeline_change', args=[obj.pk]
        )
        title_html = format_html(
            '<a href="{url}" style="font-weight:600;color:#111827;'
            'text-decoration:none;font-size:14px;">{title}</a>',
            url=change_url,
            title=obj.title or '(untitled)',
        )
        keyword_html = format_html(
            '<div style="font-size:12px;color:#6b7280;margin-top:2px;">'
            '🔑 {kw} &nbsp;·&nbsp; 🌐 {lang}</div>',
            kw=obj.keyword,
            lang=obj.get_language_display(),
        )
        excerpt = (obj.excerpt or '')[:100]
        excerpt_html = format_html(
            '<div style="font-size:12px;color:#9ca3af;margin-top:4px;">'
            '{exc}</div>',
            exc=excerpt,
        ) if excerpt else ''

        return format_html(
            '<div>{title}{kw}{exc}</div>',
            title=title_html, kw=keyword_html, exc=excerpt_html,
        )

    @admin.display(description='Status')
    def status_badge(self, obj):
        style = (
            'display:inline-block;padding:3px 10px;border-radius:20px;'
            'font-size:12px;font-weight:600;'
            + _EN_STATUS_STYLES.get(obj.status, '')
        )
        label = _EN_STATUS_LABELS.get(obj.status, obj.status)
        return format_html('<span style="{}">{}</span>', style, label)

    @admin.display(description='👁 Views')
    def views_count(self, obj):
        return format_html(
            '<span style="font-size:13px;">👁 {}</span>',
            obj.views,
        )

    @admin.display(description='Actions')
    def action_buttons(self, obj):
        if obj.status == EnContentPipeline.STATUS_PENDING:
            url = reverse('admin:en_pipeline_generate', args=[obj.pk])
            return format_html(
                '<a href="{}" style="'
                'background:#16a34a;color:#fff;padding:5px 12px;'
                'border-radius:6px;text-decoration:none;font-size:12px;'
                'font-weight:600;white-space:nowrap;">'
                '▶ Generate</a>',
                url,
            )

        if obj.status == EnContentPipeline.STATUS_GENERATING:
            return format_html(
                '<span style="color:#1d4ed8;font-size:12px;">⟳ Processing…</span>'
            )

        if obj.status == EnContentPipeline.STATUS_REVIEW:
            url = reverse('admin:en_pipeline_publish', args=[obj.pk])
            return format_html(
                '<a href="{}" style="'
                'background:#2563eb;color:#fff;padding:5px 12px;'
                'border-radius:6px;text-decoration:none;font-size:12px;'
                'font-weight:600;white-space:nowrap;">'
                '✓ Publish</a>',
                url,
            )

        if obj.status == EnContentPipeline.STATUS_PUBLISHED:
            return format_html(
                '<span style="'
                'background:#f3f4f6;color:#374151;padding:5px 12px;'
                'border-radius:6px;font-size:12px;font-weight:600;">'
                '↗ Published</span>'
            )

        if obj.status == EnContentPipeline.STATUS_FAILED:
            url = reverse('admin:en_pipeline_generate', args=[obj.pk])
            return format_html(
                '<a href="{}" style="'
                'background:#dc2626;color:#fff;padding:5px 12px;'
                'border-radius:6px;text-decoration:none;font-size:12px;'
                'font-weight:600;white-space:nowrap;">'
                '↺ Retry</a>',
                url,
            )

        return format_html('<span style="color:#9ca3af;">—</span>')
