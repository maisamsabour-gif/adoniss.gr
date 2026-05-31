from django.contrib import admin
from django.urls import path
from django.shortcuts import redirect
from django.contrib import messages as dj_messages
from django.utils.html import format_html

from core.admin_seo import BaseSEOAdmin
from .conversion import start_conversion_thread
from .models import Brochure


@admin.register(Brochure)
class BrochureAdmin(BaseSEOAdmin, admin.ModelAdmin):
    list_display    = ['title', 'status_badge', 'page_count', 'is_published', 'created_at', 'action_buttons']
    list_filter     = ['conversion_status', 'is_published']
    search_fields   = ['title', 'slug']
    prepopulated_fields = {'slug': ('title',)}
    list_per_page   = 20
    list_editable   = ['is_published']

    class Media:
        css = {'all': ('admin/css/seo_preview.css',)}
        js = ('admin/js/seo_preview.js',)

    readonly_fields = [
        'page_count', 'page_width', 'page_height',
        'conversion_status', 'conversion_error',
        'created_at', 'updated_at',
        'cover_preview', 'preview_link',
    ]

    fieldsets = (
        ('Brochure Info', {
            'fields': ('title', 'slug', 'is_published'),
        }),
        ('Files', {
            'fields': ('pdf_file', 'cover_image', 'cover_image_alt', 'cover_preview'),
            'description': (
                'Upload the PDF file. Pages are automatically converted to WebP images '
                'in the background after saving. <strong>Add cover ALT text for SEO.</strong>'
            ),
        }),
        ('Preview', {
            'fields': ('preview_link',),
        }),
        ('Conversion Details', {
            'fields': ('conversion_status', 'page_count', 'page_width', 'page_height', 'conversion_error'),
            'classes': ('collapse',),
        }),
        ('🔍 SEO Settings', {
            'fields': (
                'seo_title', 'meta_description', 'focus_keyword',
                'canonical_url', 'og_image',
                'robots_index', 'robots_follow', 'seo_allow_publish_override',
            ),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )

    actions = ['action_reconvert']

    # ── List display helpers ─────────────────────────────────────────────────

    @admin.display(description='Status')
    def status_badge(self, obj):
        palette = {
            'pending':    ('#f59e0b', '⏳ Pending'),
            'processing': ('#3b82f6', '⚙️ Processing'),
            'ready':      ('#22c55e', '✅ Ready'),
            'failed':     ('#ef4444', '❌ Failed'),
        }
        color, label = palette.get(obj.conversion_status, ('#94a3b8', obj.conversion_status))
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 10px;border-radius:12px;'
            'font-size:11px;font-weight:600;">{}</span>',
            color, label,
        )

    @admin.display(description='Actions')
    def action_buttons(self, obj):
        view_url      = obj.get_absolute_url()
        reconvert_url = f'/admin/brochures/brochure/{obj.pk}/reconvert/'
        return format_html(
            '<a href="{}" target="_blank" style="background:#0D5EAF;color:#fff;padding:4px 10px;'
            'border-radius:6px;font-size:11px;text-decoration:none;margin-right:4px;">👁 View</a>'
            '<a href="{}" style="background:#f59e0b;color:#fff;padding:4px 10px;'
            'border-radius:6px;font-size:11px;text-decoration:none;">🔄 Re-convert</a>',
            view_url, reconvert_url,
        )

    # ── Readonly field helpers ───────────────────────────────────────────────

    @admin.display(description='Cover Preview')
    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="max-height:140px;border-radius:8px;margin-top:6px;'
                'box-shadow:0 4px 12px rgba(0,0,0,.15);">',
                obj.cover_image.url,
            )
        return '—'

    @admin.display(description='Live Preview')
    def preview_link(self, obj):
        if obj.pk and obj.is_ready:
            return format_html(
                '<a href="{}" target="_blank" class="button" '
                'style="background:#0D5EAF;color:#fff;padding:6px 18px;border-radius:8px;'
                'text-decoration:none;font-weight:600;">🔖 Open Flipbook</a>',
                obj.get_absolute_url(),
            )
        return '—'

    # ── Save hook – trigger conversion on new/changed PDF ───────────────────

    def save_model(self, request, obj, form, change):
        is_new_pdf = (not change) or ('pdf_file' in form.changed_data)
        super().save_model(request, obj, form, change)

        if is_new_pdf and obj.pdf_file:
            obj.conversion_status = Brochure.STATUS_PENDING
            obj.save(update_fields=['conversion_status'])
            start_conversion_thread(obj.pk)
            self.message_user(
                request,
                f'✅ PDF uploaded for "{obj.title}". Converting pages in the background… '
                f'Refresh this page in a moment to see progress.',
                level='success',
            )

    # ── Custom URL: /admin/brochures/brochure/<pk>/reconvert/ ────────────────

    def get_urls(self):
        return [
            path(
                '<int:pk>/reconvert/',
                self.admin_site.admin_view(self._reconvert_view),
                name='brochure_reconvert',
            ),
        ] + super().get_urls()

    def _reconvert_view(self, request, pk):
        try:
            b = Brochure.objects.get(pk=pk)
            b.conversion_status = Brochure.STATUS_PENDING
            b.save(update_fields=['conversion_status'])
            start_conversion_thread(b.pk)
            dj_messages.success(request, f'🔄 Re-conversion started for "{b.title}".')
        except Brochure.DoesNotExist:
            dj_messages.error(request, 'Brochure not found.')
        return redirect('/admin/brochures/brochure/')

    # ── Bulk action ──────────────────────────────────────────────────────────

    @admin.action(description='🔄 Re-convert selected PDFs to images')
    def action_reconvert(self, request, queryset):
        count = 0
        for b in queryset.filter(pdf_file__isnull=False).exclude(pdf_file=''):
            b.conversion_status = Brochure.STATUS_PENDING
            b.save(update_fields=['conversion_status'])
            start_conversion_thread(b.pk)
            count += 1
        self.message_user(request, f'Re-conversion started for {count} brochure(s).')
