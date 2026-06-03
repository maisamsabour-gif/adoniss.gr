from django import forms
from django.contrib import admin
from django.utils.html import format_html, mark_safe
from django_ckeditor_5.widgets import CKEditor5Widget

# Sortable admin for drag-and-drop
try:
    from adminsortable2.admin import SortableAdminMixin, SortableInlineAdminMixin
    SORTABLE_AVAILABLE = True
except ImportError:
    SORTABLE_AVAILABLE = False
    SortableAdminMixin = object
    SortableInlineAdminMixin = object

from core.admin import (
    FaFooterSettingsAdmin,
    FaNavMenuItemAdmin,
    FaNewSectionAdmin,
    FaNewSettingsAdmin,
)
from core.models import (
    FaFooterSettings,
    FaNavMenuItem,
    FaNewSection,
    FaNewSettings,
)

from .admin_site import persian_admin_site
from .models import (
    FaProperty,
    FaPropertyMedia,
    PersianBlogPost,
    PersianCTA,
    PersianExportLog,
    PersianFAQ,
    PersianFooterSettings,
    PersianHeroSlide,
    PersianMediaAsset,
    PersianMenuItem,
    PersianPage,
    PersianRedirectMap,
    PersianSEOSettings,
    PersianSection,
    # Golden Visa Landing Page Models
    GoldenVisaLandingPage,
    GVHeroSection, GVHeroFloatingCard,
    GVBenefitsSection, GVBenefitCard,
    GVEligibilitySection, GVEligibilityCard,
    GVProcessSection, GVProcessStep,
    GVStatisticsSection, GVStatItem,
    GVProjectsSection, GVProject, GVProjectUnit, GVProjectGalleryImage,
    GVFaPropertyRelation,
    GVFamilySection, GVFamilyMemberCard,
    GVDocumentsSection, GVDocumentItem,
    GVCostSection, GVCostItem,
    GVTestimonialsSection, GVTestimonial,
    GVFAQSection, GVFAQItem,
    GVFinalCTASection,
    GVSEOSettings, GVAnimationSettings, GVDesignSettings,
)


class PersianBaseAdmin(admin.ModelAdmin):
    ordering = ("id",)

    class Media:
        css = {"all": ("css/persian-admin.css",)}
        js = ("js/persian-admin.js", "js/ckeditor5-word-cleanup.js",)


class PersianPageAdminForm(forms.ModelForm):
    """Rich-text (CKEditor 5, RTL, image + video embed) editor for page body."""

    class Meta:
        model = PersianPage
        fields = "__all__"
        widgets = {
            "body": CKEditor5Widget(
                config_name="persian_blog",
                attrs={"class": "django_ckeditor_5"},
            ),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # route_path is auto-generated from the slug; never force the editor to type it.
        if "route_path" in self.fields:
            self.fields["route_path"].required = False
        if "slug" in self.fields:
            self.fields["slug"].required = False


@admin.register(PersianPage, site=persian_admin_site)
class PersianPageAdmin(PersianBaseAdmin):
    form = PersianPageAdminForm
    list_display = ("title", "page_type", "public_link", "is_published", "seo_status_badge", "sort_order", "edit_button")
    list_editable = ("is_published", "sort_order")
    search_fields = ("title", "slug", "route_path")
    list_filter = ("page_type", "is_published", "noindex", "seo_status")
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("public_url_box",)

    fieldsets = (
        ("📄 محتوای صفحه", {
            "fields": ("title", "slug", "page_type", "is_published", "body"),
        }),
        ("🔗 آدرس عمومی (برای افزودن به منو این آدرس را کپی کنید)", {
            "fields": ("public_url_box", "route_path"),
        }),
        ("🔍 سئو", {
            "classes": ("collapse",),
            "fields": ("meta_title", "meta_description", "canonical_url",
                       "og_title", "og_description", "og_image",
                       "focus_keyword", "noindex", "seo_status", "sort_order"),
        }),
    )

    @admin.display(description="آدرس صفحه")
    def public_link(self, obj):
        url = obj.get_absolute_url()
        return format_html(
            '<a href="{}" target="_blank" rel="noopener" style="color:#2563eb;text-decoration:none">{}</a>',
            url, url
        )

    @admin.display(description="وضعیت سئو")
    def seo_status_badge(self, obj):
        colors = {
            'draft': ('#6b7280', 'پیش‌نویس'),
            'needs_review': ('#d97706', 'نیاز به بررسی'),
            'optimized': ('#059669', 'بهینه شده'),
        }
        color, label = colors.get(obj.seo_status, ('#6b7280', obj.seo_status))
        return format_html(
            '<span style="background:{};color:#fff;padding:4px 10px;border-radius:20px;'
            'font-size:11px;font-weight:500;white-space:nowrap">{}</span>',
            color, label
        )

    @admin.display(description="عملیات")
    def edit_button(self, obj):
        return format_html(
            '<a href="/fa-admin/persian_cms/persianpage/{}/change/" '
            'style="background:#2563eb;color:#fff;'
            'padding:6px 12px;border-radius:6px;text-decoration:none;font-weight:500;'
            'font-size:12px;display:inline-flex;align-items:center;gap:4px;'
            'white-space:nowrap">'
            '✏️ ویرایش</a>',
            obj.pk,
        )

    @admin.display(description="آدرس عمومی این صفحه")
    def public_url_box(self, obj):
        if not obj or not obj.pk:
            return "بعد از ذخیره، آدرس عمومی این‌جا نمایش داده می‌شود."
        url = obj.get_absolute_url()
        return format_html(
            '<div style="display:flex;gap:8px;align-items:center;flex-wrap:wrap">'
            '<code style="background:#0f172a;color:#e2e8f0;padding:6px 10px;border-radius:8px;direction:ltr">{}</code>'
            '<a class="button" href="{}" target="_blank" rel="noopener">باز کردن</a>'
            '<span style="color:#64748b">— این آدرس را در «لینک» آیتم منو وارد کنید.</span>'
            '</div>',
            url, url,
        )


@admin.register(PersianSection, site=persian_admin_site)
class PersianSectionAdmin(PersianBaseAdmin):
    list_display = ("internal_name", "section_type", "page", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")
    list_filter = ("section_type", "is_active")
    search_fields = ("internal_name", "title", "anchor_id")


@admin.register(PersianHeroSlide, site=persian_admin_site)
class PersianHeroSlideAdmin(PersianBaseAdmin):
    list_display = ("title", "section", "start_progress", "end_progress", "sort_order")
    list_editable = ("sort_order",)
    search_fields = ("title", "highlight")


class PersianBlogPostAdminForm(forms.ModelForm):
    """Rich-text (CKEditor 5, self-hosted, RTL) editor for the blog body."""

    class Meta:
        model = PersianBlogPost
        fields = "__all__"
        widgets = {
            "body": CKEditor5Widget(
                config_name="persian_blog",
                attrs={"class": "django_ckeditor_5"},
            ),
        }


@admin.register(PersianBlogPost, site=persian_admin_site)
class PersianBlogPostAdmin(PersianBaseAdmin):
    form = PersianBlogPostAdminForm
    list_display = ("title", "slug", "is_published", "noindex", "seo_status", "published_at")
    list_filter = ("is_published", "noindex", "seo_status")
    search_fields = ("title", "slug", "excerpt")
    prepopulated_fields = {"slug": ("title",)}


@admin.register(PersianSEOSettings, site=persian_admin_site)
class PersianSEOSettingsAdmin(PersianBaseAdmin):
    list_display = ("page_key", "meta_title", "noindex", "seo_status", "robots_index", "robots_follow", "canonical_preview")
    list_filter = ("robots_index", "robots_follow", "noindex", "seo_status")
    search_fields = ("page_key", "meta_title", "meta_description")

    @admin.display(description="Canonical")
    def canonical_preview(self, obj: PersianSEOSettings):
        if not obj.canonical_url:
            return "—"
        return format_html('<a href="{}" target="_blank" rel="noopener">{}</a>', obj.canonical_url, obj.canonical_url)


@admin.register(PersianMenuItem, site=persian_admin_site)
class PersianMenuItemAdmin(PersianBaseAdmin):
    list_display = ("label", "parent", "url", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")
    search_fields = ("label", "url")


@admin.register(PersianFooterSettings, site=persian_admin_site)
class PersianFooterSettingsAdmin(PersianBaseAdmin):
    list_display = ("brand_name", "phone", "email")

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(PersianMediaAsset, site=persian_admin_site)
class PersianMediaAssetAdmin(PersianBaseAdmin):
    list_display = ("title", "file", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("title", "alt_text")


@admin.register(PersianCTA, site=persian_admin_site)
class PersianCTAAdmin(PersianBaseAdmin):
    list_display = ("label", "target_page", "url", "style", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")
    list_filter = ("style", "is_active")
    search_fields = ("label", "url")


@admin.register(PersianFAQ, site=persian_admin_site)
class PersianFAQAdmin(PersianBaseAdmin):
    list_display = ("question", "page", "is_active", "sort_order")
    list_editable = ("is_active", "sort_order")
    list_filter = ("is_active",)
    search_fields = ("question", "answer")


@admin.register(PersianRedirectMap, site=persian_admin_site)
class PersianRedirectMapAdmin(PersianBaseAdmin):
    list_display = ("source_path", "destination_path", "status_code", "is_active")
    list_editable = ("status_code", "is_active")
    list_filter = ("status_code", "is_active")
    search_fields = ("source_path", "destination_path")


@admin.register(PersianExportLog, site=persian_admin_site)
class PersianExportLogAdmin(PersianBaseAdmin):
    list_display = ("file", "note", "created_at")
    readonly_fields = ("created_at",)

    def has_add_permission(self, request):
        return False


# ══════════════════════════════════════════════════════════════════════════════
# Persian Properties Admin — طراحی حرفه‌ای و لاکچری
# جدا از سایت انگلیسی — مدیریت کامل پروژه‌های ملکی فارسی
# ══════════════════════════════════════════════════════════════════════════════

class FaPropertyAdminForm(forms.ModelForm):
    """Custom form for FaProperty with working file upload widgets."""
    
    class Meta:
        model = FaProperty
        fields = '__all__'
        widgets = {}
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Use standard ClearableFileInput for all image fields to ensure uploads work
        from django.forms.widgets import ClearableFileInput
        
        # Accept all common image formats including HEIC from iPhone
        image_accept = (
            'image/*,'
            '.jpg,.jpeg,.png,.webp,.gif,.bmp,.tiff,.tif,'
            '.heic,.heif,.avif,.svg,.ico,'
            'image/heic,image/heif,image/avif'
        )
        video_accept = 'video/*,.mp4,.mov,.avi,.mkv,.webm'
        
        image_fields = [f'image_{i}' for i in range(1, 16)]
        image_fields.extend(['cover_image', 'video_1_poster', 'video_2_poster'])
        video_fields = ['video_1', 'video_2']
        
        for field_name in image_fields:
            if field_name in self.fields:
                self.fields[field_name].widget = ClearableFileInput(attrs={
                    'accept': image_accept,
                    'class': 'fa-file-input',
                })
        
        for field_name in video_fields:
            if field_name in self.fields:
                self.fields[field_name].widget = ClearableFileInput(attrs={
                    'accept': video_accept,
                    'class': 'fa-file-input',
                })


class FaPropertyMediaInline(admin.TabularInline):
    """Inline for additional media beyond the 15 direct slots."""
    model = FaPropertyMedia
    extra = 2
    max_num = 30
    fields = ['order', 'is_cover', 'image', 'video', 'poster', 'caption']
    ordering = ['order']
    verbose_name = 'رسانه اضافی'
    verbose_name_plural = 'رسانه‌های اضافی (علاوه بر ۱۵ عکس اصلی)'


@admin.register(FaProperty, site=persian_admin_site)
class FaPropertyAdmin(PersianBaseAdmin):
    """
    Admin for Persian properties — Professional Luxury Real Estate Management.
    
    طراحی حرفه‌ای برای مدیریت پروژه‌های ملکی لاکچری با:
    - سئو کامل (Meta، OG، Schema)
    - گالری عکس با Alt و Caption
    - امکانات و ویژگی‌های کامل
    - مدیریت قیمت و وضعیت
    """
    
    # ── Use Custom Form for File Uploads ─────────────────────────────────────────
    form = FaPropertyAdminForm
    
    # ── List View ────────────────────────────────────────────────────────────────
    list_display = (
        'thumbnail_preview',
        'name',
        'property_type',
        'location_display',
        'price_display',
        'status_badge',
        'display_order',
        'is_featured',
        'is_active',
        'edit_button',
    )
    list_display_links = ('name',)
    list_editable = ('display_order', 'is_featured', 'is_active')
    list_filter = (
        'is_active',
        'is_featured',
        'is_new',
        'status',
        'property_type',
        'price_tier',
        'timeline_stage',
        'golden_visa_eligible',
        'city',
    )
    search_fields = (
        'name', 'slug', 'tagline', 'headline',
        'location', 'area', 'city', 'address',
        'description', 'short_description',
        'meta_title', 'meta_description', 'focus_keyword',
    )
    list_per_page = 20
    date_hierarchy = 'created_at'
    
    # ── Form Configuration ───────────────────────────────────────────────────────
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['display_order', '-is_featured', '-created_at']
    inlines = [FaPropertyMediaInline]
    save_on_top = True
    
    # ── Custom List Display Methods ──────────────────────────────────────────────
    @admin.display(description='تصویر')
    def thumbnail_preview(self, obj):
        img = obj.main_image
        if img:
            featured_badge = (
                '<span style="position:absolute;top:4px;right:4px;background:#c9a227;color:#fff;'
                'font-size:9px;padding:2px 6px;border-radius:4px;font-weight:600">⭐</span>'
            ) if obj.is_featured else ''
            
            return format_html(
                '<div style="position:relative;display:inline-block">'
                '<img src="{}" style="height:50px;width:70px;object-fit:cover;border-radius:6px;'
                'box-shadow:0 2px 6px rgba(0,0,0,0.12);display:block" />'
                '{}</div>',
                img.url,
                mark_safe(featured_badge),
            )
        return format_html('<span style="color:#9ca3af;font-size:12px">بدون تصویر</span>')
    
    @admin.display(description='موقعیت')
    def location_display(self, obj):
        parts = [p for p in [obj.city, obj.area] if p]
        if parts:
            return format_html(
                '<span style="color:#374151;font-size:13px">{}</span>',
                ' • '.join(parts),
            )
        return format_html('<span style="color:#9ca3af">—</span>')
    
    @admin.display(description='قیمت')
    def price_display(self, obj):
        if obj.price_label:
            return format_html(
                '<span style="font-weight:600;color:#059669;font-size:13px;direction:ltr;display:inline-block">{}</span>',
                obj.price_label,
            )
        if obj.price:
            formatted_price = f'€{obj.price:,.0f}'
            return format_html(
                '<span style="font-weight:600;color:#059669;font-size:13px;direction:ltr;display:inline-block">{}</span>',
                formatted_price,
            )
        return format_html('<span style="color:#9ca3af">—</span>')
    
    @admin.display(description='وضعیت')
    def status_badge(self, obj):
        colors = {
            'available': ('#059669', '#dcfce7'),      # سبز - موجود
            'reserved': ('#d97706', '#fef3c7'),       # نارنجی - رزرو
            'sold_out_soon': ('#dc2626', '#fee2e2'),  # قرمز - رو به اتمام
            'sold_out': ('#6b7280', '#f3f4f6'),       # خاکستری - فروخته شده
        }
        bg_color, text_bg = colors.get(obj.status, ('#6b7280', '#f3f4f6'))
        return format_html(
            '<span style="background:{};color:#fff;padding:4px 10px;border-radius:20px;'
            'font-size:11px;font-weight:500;white-space:nowrap">{}</span>',
            bg_color, obj.get_status_display(),
        )
    
    @admin.display(description='عملیات')
    def edit_button(self, obj):
        return format_html(
            '<a href="/fa-admin/persian_cms/faproperty/{}/change/" '
            'style="background:#2563eb;color:#fff;'
            'padding:6px 12px;border-radius:6px;text-decoration:none;font-weight:500;'
            'font-size:12px;display:inline-flex;align-items:center;gap:4px;'
            'white-space:nowrap">'
            '✏️ ویرایش</a>',
            obj.pk,
        )
    
    # ── Fieldsets — Organized Professional Layout ────────────────────────────────
    fieldsets = (
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # SECTION 1: BASIC INFO
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        ('📋 اطلاعات پایه پروژه', {
            'fields': (
                ('name', 'slug'),
                'property_type',
                'headline',
                'tagline',
                'short_description',
                'description',
            ),
            'description': '‎<div style="background:linear-gradient(135deg,#1a1a2e,#16213e);color:#eee;'
                          'padding:15px 20px;border-radius:10px;margin-bottom:15px;direction:rtl">'
                          '<strong style="color:#c9a227">💡 راهنما:</strong> '
                          'نام پروژه و توضیحات را با دقت وارد کنید. '
                          'این اطلاعات در کارت و صفحه جزئیات نمایش داده می‌شوند.'
                          '</div>',
        }),
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # SECTION 2: PRICING
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        ('💰 قیمت‌گذاری و سرمایه‌گذاری', {
            'fields': (
                ('price', 'price_label'),
                ('price_tier', 'price_per_sqm'),
                ('rental_yield', 'golden_visa_eligible'),
            ),
            'classes': ('collapse',) if False else (),
        }),
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # SECTION 3: LOCATION
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        ('📍 موقعیت مکانی', {
            'fields': (
                ('city', 'location'),
                ('area', 'address'),
                ('map_latitude', 'map_longitude'),
                ('distance_to_sea', 'distance_to_center', 'distance_to_airport'),
            ),
        }),
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # SECTION 4: PROPERTY DETAILS
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        ('🏠 مشخصات فنی', {
            'fields': (
                ('total_units', 'available_units'),
                ('floors', 'parking_spaces'),
                ('bedrooms_min', 'bedrooms_max'),
                ('size_min', 'size_max'),
                ('bathrooms', 'year_built'),
            ),
        }),
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # SECTION 5: FEATURES & AMENITIES
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        ('✨ ویژگی‌ها و امکانات', {
            'fields': (
                ('feature_1', 'feature_2'),
                ('feature_3', 'feature_4'),
                'amenities',
                'investment_highlights',
            ),
            'description': '‎<div style="background:#fef3c7;color:#92400e;padding:12px 16px;'
                          'border-radius:8px;margin-bottom:15px;direction:rtl">'
                          '<strong>💡 ویژگی‌های برجسته:</strong> '
                          '۴ ویژگی اول در کارت نمایش داده می‌شوند. از ایموجی استفاده کنید!'
                          '<br><strong>مثال:</strong> 🏊 استخر خصوصی • 🌅 ویو دریا • 🛗 آسانسور • 🔒 امنیت ۲۴/۷'
                          '</div>',
        }),
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # SECTION 6: STATUS & TIMELINE
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        ('📊 وضعیت و زمان‌بندی', {
            'fields': (
                ('status', 'timeline_stage'),
                'delivery_date',
            ),
        }),
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # SECTION 7: GALLERY — Images with Alt & Caption
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        ('🖼️ عکس کاور (اصلی)', {
            'fields': (
                'cover_image',
                'cover_image_alt',
                'cover_image_slot',
            ),
            'description': '‎<div style="background:linear-gradient(135deg,#1e3a5f,#2d5a87);color:#fff;'
                          'padding:15px 20px;border-radius:10px;margin-bottom:20px;direction:rtl">'
                          '<strong style="color:#fbbf24">📸 راهنمای آپلود تصاویر:</strong><br>'
                          '• <strong>عکس کاور</strong> در کارت و اشتراک‌گذاری نمایش داده می‌شود<br>'
                          '• تصاویر با کیفیت بالا (حداقل 1200×800 پیکسل) آپلود کنید<br>'
                          '• برای سئو حتماً <strong>Alt Text</strong> بنویسید<br>'
                          '• فرمت‌های مجاز: JPG, PNG, WebP, HEIC (آیفون)'
                          '</div>',
        }),
        
        # Image slots 1-5
        ('📷 تصاویر ۱ تا ۵', {
            'fields': (
                'image_1', ('image_1_alt', 'image_1_caption'),
                'image_2', ('image_2_alt', 'image_2_caption'),
                'image_3', ('image_3_alt', 'image_3_caption'),
                'image_4', ('image_4_alt', 'image_4_caption'),
                'image_5', ('image_5_alt', 'image_5_caption'),
            ),
        }),
        
        # Image slots 6-10
        ('📷 تصاویر ۶ تا ۱۰', {
            'fields': (
                'image_6', ('image_6_alt', 'image_6_caption'),
                'image_7', ('image_7_alt', 'image_7_caption'),
                'image_8', ('image_8_alt', 'image_8_caption'),
                'image_9', ('image_9_alt', 'image_9_caption'),
                'image_10', ('image_10_alt', 'image_10_caption'),
            ),
        }),
        
        # Image slots 11-15
        ('📷 تصاویر ۱۱ تا ۱۵', {
            'classes': ('collapse',),
            'fields': (
                'image_11', ('image_11_alt', 'image_11_caption'),
                'image_12', ('image_12_alt', 'image_12_caption'),
                'image_13', ('image_13_alt', 'image_13_caption'),
                'image_14', ('image_14_alt', 'image_14_caption'),
                'image_15', ('image_15_alt', 'image_15_caption'),
            ),
        }),
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # SECTION 8: VIDEOS
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        ('🎬 ویدیو و تور مجازی', {
            'classes': ('collapse',),
            'fields': (
                ('video_1', 'video_1_poster'),
                'video_1_title',
                ('video_2', 'video_2_poster'),
                'video_2_title',
                'youtube_url',
                'virtual_tour_url',
            ),
        }),
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # SECTION 9: SEO
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        ('🔍 سئو و بهینه‌سازی گوگل', {
            'classes': ('collapse',),
            'fields': (
                'focus_keyword',
                ('meta_title', 'noindex'),
                'meta_description',
                ('og_title', 'og_description'),
                'canonical_url',
                'schema_markup',
            ),
            'description': '‎<div style="background:#ecfdf5;color:#065f46;padding:12px 16px;'
                          'border-radius:8px;margin-bottom:15px;direction:rtl">'
                          '<strong>🎯 راهنمای سئو:</strong><br>'
                          '• <strong>Meta Title:</strong> حداکثر ۷۰ کاراکتر<br>'
                          '• <strong>Meta Description:</strong> حداکثر ۱۶۰ کاراکتر<br>'
                          '• <strong>کلمه کلیدی:</strong> کلمه‌ای که می‌خواهید در گوگل رتبه بگیرید'
                          '</div>',
        }),
        
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        # SECTION 10: DISPLAY SETTINGS
        # ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
        ('⚙️ تنظیمات نمایش', {
            'fields': (
                ('display_order', 'is_active'),
                ('is_featured', 'is_new'),
            ),
        }),
    )
    
    # ── Custom CSS for this Admin ────────────────────────────────────────────────
    class Media:
        css = {
            'all': (
                'css/persian-admin.css',
                'css/fa-property-admin.css',
            ),
        }
        js = ('js/fa-property-admin.js',)


@admin.register(FaPropertyMedia, site=persian_admin_site)
class FaPropertyMediaAdmin(PersianBaseAdmin):
    """Admin for additional Persian property media items."""
    list_display = ('property', 'media_preview', 'order', 'is_cover', 'caption_preview', 'created_at')
    list_filter = ('is_cover', 'property')
    search_fields = ('property__name', 'caption')
    ordering = ['property', 'order']
    list_per_page = 30
    
    @admin.display(description='پیش‌نمایش')
    def media_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height:50px;width:75px;object-fit:cover;border-radius:6px;'
                'box-shadow:0 2px 6px rgba(0,0,0,0.1)" />',
                obj.image.url,
            )
        if obj.video:
            return format_html(
                '<span style="background:#1e40af;color:#fff;padding:4px 10px;border-radius:4px;'
                'font-size:11px">🎬 ویدیو</span>',
            )
        return format_html('<span style="color:#999">—</span>')
    
    @admin.display(description='توضیح')
    def caption_preview(self, obj):
        if obj.caption:
            return obj.caption[:50] + '...' if len(obj.caption) > 50 else obj.caption
        return '—'


# ══════════════════════════════════════════════════════════════════════════════
# GOLDEN VISA LANDING PAGE ADMIN - PROFESSIONAL PAGE BUILDER
# مدیریت حرفه‌ای صفحه لندینگ گلدن ویزا
# ══════════════════════════════════════════════════════════════════════════════


# ── Custom Forms with CKEditor5 ───────────────────────────────────────────────

class GoldenVisaLandingPageForm(forms.ModelForm):
    """Form with CKEditor5 for all rich text fields - uses persian_clean for Word paste cleanup."""
    
    class Meta:
        model = GoldenVisaLandingPage
        fields = '__all__'
        widgets = {
            'intro_body': CKEditor5Widget(
                config_name='persian_clean',
                attrs={'class': 'django_ckeditor_5', 'dir': 'rtl'},
            ),
            'benefits_body': CKEditor5Widget(
                config_name='persian_clean',
                attrs={'class': 'django_ckeditor_5', 'dir': 'rtl'},
            ),
            'requirements_body': CKEditor5Widget(
                config_name='persian_clean',
                attrs={'class': 'django_ckeditor_5', 'dir': 'rtl'},
            ),
            'process_body': CKEditor5Widget(
                config_name='persian_clean',
                attrs={'class': 'django_ckeditor_5', 'dir': 'rtl'},
            ),
            'faq_body': CKEditor5Widget(
                config_name='persian_clean',
                attrs={'class': 'django_ckeditor_5', 'dir': 'rtl'},
            ),
        }


class GVFAQItemForm(forms.ModelForm):
    """Form with CKEditor5 for FAQ answers - uses persian_clean for Word paste cleanup."""
    
    class Meta:
        model = GVFAQItem
        fields = '__all__'
        widgets = {
            'answer': CKEditor5Widget(
                config_name='persian_clean',
                attrs={'class': 'django_ckeditor_5', 'dir': 'rtl'},
            ),
        }


class GVBenefitCardForm(forms.ModelForm):
    """Form with CKEditor5 for benefit descriptions - uses persian_clean for Word paste cleanup."""
    
    class Meta:
        model = GVBenefitCard
        fields = '__all__'
        widgets = {
            'description': CKEditor5Widget(
                config_name='persian_clean',
                attrs={'class': 'django_ckeditor_5', 'dir': 'rtl'},
            ),
        }


class GVProcessStepForm(forms.ModelForm):
    """Form with CKEditor5 for process step descriptions - uses persian_clean for Word paste cleanup."""
    
    class Meta:
        model = GVProcessStep
        fields = '__all__'
        widgets = {
            'description': CKEditor5Widget(
                config_name='persian_clean',
                attrs={'class': 'django_ckeditor_5', 'dir': 'rtl'},
            ),
        }


class GVEligibilityCardForm(forms.ModelForm):
    """Form with CKEditor5 for eligibility descriptions - uses persian_clean for Word paste cleanup."""
    
    class Meta:
        model = GVEligibilityCard
        fields = '__all__'
        widgets = {
            'description': CKEditor5Widget(
                config_name='persian_clean',
                attrs={'class': 'django_ckeditor_5', 'dir': 'rtl'},
            ),
        }


# ── Image Preview Mixin ───────────────────────────────────────────────────────

class ImagePreviewMixin:
    """Mixin to add image preview functionality to admin."""
    
    def image_preview(self, obj):
        """Show image thumbnail preview."""
        if hasattr(obj, 'main_image') and obj.main_image:
            return format_html(
                '<img src="{}" style="max-width:120px;max-height:80px;'
                'object-fit:cover;border-radius:8px;border:1px solid #ddd;"/>',
                obj.main_image.url
            )
        if hasattr(obj, 'image') and obj.image:
            return format_html(
                '<img src="{}" style="max-width:120px;max-height:80px;'
                'object-fit:cover;border-radius:8px;border:1px solid #ddd;"/>',
                obj.image.url
            )
        if hasattr(obj, 'icon_image') and obj.icon_image:
            return format_html(
                '<img src="{}" style="max-width:60px;max-height:60px;'
                'object-fit:contain;border-radius:4px;"/>',
                obj.icon_image.url
            )
        return '—'
    image_preview.short_description = 'پیش‌نمایش'


# ── Enhanced Inline Classes with Full Fields ──────────────────────────────────

class GVHeroFloatingCardInline(admin.StackedInline):
    model = GVHeroFloatingCard
    extra = 0
    min_num = 0
    max_num = 5
    verbose_name = 'کارت شناور'
    verbose_name_plural = '📌 کارت‌های شناور هیرو'
    classes = ['collapse']
    ordering = ['display_order', 'pk']
    fields = [
        ('title', 'is_active'),
        'text',
        ('icon', 'icon_image'),
        'display_order',
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('display_order', 'pk')


class GVBenefitCardInline(admin.StackedInline):
    model = GVBenefitCard
    form = GVBenefitCardForm
    extra = 0
    min_num = 0
    max_num = 12
    verbose_name = 'کارت مزیت'
    verbose_name_plural = '⭐ کارت‌های مزایا'
    classes = ['collapse']
    ordering = ['display_order', 'pk']
    fields = [
        ('title', 'is_active'),
        'description',
        ('icon', 'icon_image'),
        ('card_image', 'display_order'),
        ('button_text', 'button_link'),
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('display_order', 'pk')


class GVEligibilityCardInline(admin.StackedInline):
    model = GVEligibilityCard
    form = GVEligibilityCardForm
    extra = 0
    min_num = 0
    max_num = 6
    verbose_name = 'کارت شرایط'
    verbose_name_plural = '💰 کارت‌های شرایط سرمایه‌گذاری'
    classes = ['collapse']
    ordering = ['display_order', 'pk']
    fields = [
        ('investment_amount', 'tier', 'is_active'),
        ('area_name', 'property_type'),
        ('minimum_area', 'badge_text'),
        'description',
        ('icon', 'icon_image'),
        ('is_featured', 'display_order'),
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('display_order', 'pk')


class GVProcessStepInline(admin.StackedInline):
    model = GVProcessStep
    form = GVProcessStepForm
    extra = 0
    min_num = 0
    max_num = 12
    verbose_name = 'مرحله'
    verbose_name_plural = '📊 مراحل فرآیند'
    classes = ['collapse']
    ordering = ['display_order', 'step_number']
    fields = [
        ('step_number', 'title', 'is_active'),
        'description',
        ('estimated_time', 'display_order'),
        ('icon', 'icon_image'),
        'step_image',
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('display_order', 'step_number')


class GVStatItemInline(admin.StackedInline):
    model = GVStatItem
    extra = 0
    min_num = 0
    max_num = 8
    verbose_name = 'آیتم آمار'
    verbose_name_plural = '📈 آیتم‌های آمار'
    classes = ['collapse']
    ordering = ['display_order', 'pk']
    fields = [
        ('number', 'prefix', 'suffix', 'is_active'),
        ('label', 'description'),
        ('icon', 'icon_image'),
        'display_order',
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('display_order', 'pk')


class GVProjectInline(admin.StackedInline):
    model = GVProject
    extra = 0
    min_num = 0
    max_num = 12
    verbose_name = 'پروژه'
    verbose_name_plural = '🏗️ پروژه‌های گلدن ویزا (جدید)'
    classes = ['collapse']
    ordering = ['display_order', 'pk']
    show_change_link = True
    fields = [
        ('name', 'status', 'is_active'),
        'short_description',
        ('main_image', 'project_video'),
        ('location_title', 'area'),
        ('starting_price', 'golden_visa_eligible'),
        ('progress_percentage', 'delivery_date'),
        ('cta_text', 'cta_link'),
        ('google_maps_link', 'display_order'),
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('display_order', 'pk')


class GVFaPropertyRelationInline(admin.TabularInline):
    model = GVFaPropertyRelation
    extra = 1
    min_num = 0
    max_num = 20
    verbose_name = 'پروژه مرتبط'
    verbose_name_plural = '🏠 پروژه‌های مرتبط از FaProperty'
    classes = ['collapse']
    ordering = ['display_order', 'pk']
    autocomplete_fields = ['property']
    fields = ['property', 'display_title', 'badge_text', 'display_order', 'is_active']
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('display_order', 'pk')


class GVFamilyMemberCardInline(admin.StackedInline):
    model = GVFamilyMemberCard
    extra = 0
    min_num = 0
    max_num = 8
    verbose_name = 'کارت عضو خانواده'
    verbose_name_plural = '👨‍👩‍👧 کارت‌های اعضای خانواده'
    classes = ['collapse']
    ordering = ['display_order', 'pk']
    fields = [
        ('title', 'is_active'),
        'description',
        ('icon', 'icon_image'),
        'display_order',
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('display_order', 'pk')


class GVDocumentItemInline(admin.StackedInline):
    model = GVDocumentItem
    extra = 0
    min_num = 0
    max_num = 20
    verbose_name = 'مدرک'
    verbose_name_plural = '📋 مدارک مورد نیاز'
    classes = ['collapse']
    ordering = ['display_order', 'pk']
    fields = [
        ('title', 'is_required', 'is_active'),
        'description',
        ('icon', 'icon_image'),
        'display_order',
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('display_order', 'pk')


class GVCostItemInline(admin.StackedInline):
    model = GVCostItem
    extra = 0
    min_num = 0
    max_num = 15
    verbose_name = 'آیتم هزینه'
    verbose_name_plural = '💵 آیتم‌های هزینه'
    classes = ['collapse']
    ordering = ['display_order', 'pk']
    fields = [
        ('title', 'is_active'),
        ('amount', 'currency'),
        'description',
        'display_order',
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('display_order', 'pk')


class GVTestimonialInline(admin.StackedInline):
    model = GVTestimonial
    extra = 0
    min_num = 0
    max_num = 10
    verbose_name = 'نظر مشتری'
    verbose_name_plural = '💬 نظرات مشتریان'
    classes = ['collapse']
    ordering = ['display_order', 'pk']
    fields = [
        ('client_name', 'client_country', 'is_active'),
        'review_text',
        ('client_image', 'video_url'),
        ('rating', 'display_order'),
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('display_order', 'pk')


class GVFAQItemInline(admin.StackedInline):
    model = GVFAQItem
    form = GVFAQItemForm
    extra = 0
    min_num = 0
    max_num = 30
    verbose_name = 'سوال متداول'
    verbose_name_plural = '❓ سوالات متداول'
    classes = ['collapse']
    ordering = ['display_order', 'pk']
    fields = [
        ('question', 'is_active'),
        'answer',
        ('category', 'display_order'),
    ]
    
    def get_queryset(self, request):
        return super().get_queryset(request).order_by('display_order', 'pk')


class GVProjectUnitInline(admin.TabularInline):
    model = GVProjectUnit
    extra = 1
    fields = ['floor', 'unit_number', 'area_sqm', 'bedrooms', 'bathrooms', 'price', 'status', 'display_order', 'is_active']


class GVProjectGalleryImageInline(admin.TabularInline):
    model = GVProjectGalleryImage
    extra = 2
    fields = ['image', 'caption', 'alt_text', 'display_order']


# ── Section Inlines with All Fields ───────────────────────────────────────────

class GVHeroSectionInline(admin.StackedInline):
    model = GVHeroSection
    extra = 0
    max_num = 1
    can_delete = False
    verbose_name = 'Hero Section'
    verbose_name_plural = '🎬 بخش هیرو (Hero)'
    fieldsets = (
        ('تنظیمات کلی', {
            'fields': ('is_enabled', 'display_order'),
        }),
        ('متن‌های اصلی', {
            'fields': (
                'main_title',
                'highlighted_word',
                'subtitle',
                'description',
            ),
        }),
        ('دکمه‌ها', {
            'fields': (
                ('primary_cta_text', 'primary_cta_link'),
                ('secondary_cta_text', 'secondary_cta_link'),
            ),
        }),
        ('تصاویر و ویدیو', {
            'fields': (
                'hero_main_visual',
                'hero_image_alt',
                ('background_image', 'mobile_background_image'),
                'background_video',
            ),
            'classes': ('collapse',),
        }),
    )


class GVBenefitsSectionInline(admin.StackedInline):
    model = GVBenefitsSection
    extra = 0
    max_num = 1
    can_delete = False
    verbose_name = 'Benefits Section'
    verbose_name_plural = '⭐ بخش مزایا'
    fieldsets = (
        (None, {
            'fields': (
                ('is_enabled', 'display_order'),
                'section_title',
                'section_subtitle',
                'section_description',
                'layout_style',
            ),
        }),
        ('تصاویر و ویدیو', {
            'fields': (
                ('background_image', 'side_image'),
                'side_image_alt',
                ('section_video', 'video_poster'),
            ),
            'classes': ('collapse',),
        }),
    )


class GVEligibilitySectionInline(admin.StackedInline):
    model = GVEligibilitySection
    extra = 0
    max_num = 1
    can_delete = False
    verbose_name = 'Eligibility Section'
    verbose_name_plural = '💰 بخش شرایط سرمایه‌گذاری'
    fieldsets = (
        (None, {
            'fields': (
                ('is_enabled', 'display_order'),
                'section_title',
                'section_subtitle',
                'section_description',
                ('cta_text', 'cta_link'),
                'layout_style',
            ),
        }),
        ('تصاویر و ویدیو', {
            'fields': (
                ('background_image', 'side_image'),
                'side_image_alt',
                ('section_video', 'video_poster'),
            ),
            'classes': ('collapse',),
        }),
    )


class GVProcessSectionInline(admin.StackedInline):
    model = GVProcessSection
    extra = 0
    max_num = 1
    can_delete = False
    verbose_name = 'Process Section'
    verbose_name_plural = '📊 بخش مراحل'
    fieldsets = (
        (None, {
            'fields': (
                ('is_enabled', 'display_order'),
                'section_title',
                'section_subtitle',
                'section_description',
                'layout_style',
            ),
        }),
        ('تصاویر و ویدیو', {
            'fields': (
                ('background_image', 'side_image'),
                'side_image_alt',
                ('section_video', 'video_poster'),
            ),
            'classes': ('collapse',),
        }),
    )


class GVStatisticsSectionInline(admin.StackedInline):
    model = GVStatisticsSection
    extra = 0
    max_num = 1
    can_delete = False
    verbose_name = 'Statistics Section'
    verbose_name_plural = '📈 بخش آمار'
    fieldsets = (
        (None, {
            'fields': (
                ('is_enabled', 'display_order'),
                'section_title',
                'section_subtitle',
                'layout_style',
            ),
        }),
        ('تصاویر و ویدیو', {
            'fields': (
                ('background_image', 'side_image'),
                'side_image_alt',
                ('section_video', 'video_poster'),
            ),
            'classes': ('collapse',),
        }),
    )


class GVProjectsSectionInline(admin.StackedInline):
    model = GVProjectsSection
    extra = 0
    max_num = 1
    can_delete = False
    verbose_name = 'Projects Section'
    verbose_name_plural = '🏗️ بخش پروژه‌ها'
    fieldsets = (
        (None, {
            'fields': (
                'is_enabled',
                'section_title',
                'section_subtitle',
                'section_description',
                ('cta_text', 'cta_link'),
                'display_order',
            ),
        }),
    )


class GVFamilySectionInline(admin.StackedInline):
    model = GVFamilySection
    extra = 0
    max_num = 1
    can_delete = False
    verbose_name = 'Family Section'
    verbose_name_plural = '👨‍👩‍👧 بخش خانواده'
    fieldsets = (
        (None, {
            'fields': (
                ('is_enabled', 'display_order'),
                'section_title',
                'section_subtitle',
                'section_description',
                'layout_style',
            ),
        }),
        ('تصاویر و ویدیو', {
            'fields': (
                ('main_image', 'main_image_alt'),
                'background_image',
                ('section_video', 'video_poster'),
            ),
            'classes': ('collapse',),
        }),
    )


class GVDocumentsSectionInline(admin.StackedInline):
    model = GVDocumentsSection
    extra = 0
    max_num = 1
    can_delete = False
    verbose_name = 'Documents Section'
    verbose_name_plural = '📋 بخش مدارک'
    fieldsets = (
        (None, {
            'fields': (
                ('is_enabled', 'display_order'),
                'section_title',
                'section_subtitle',
                'section_description',
                'layout_style',
            ),
        }),
        ('تصاویر و ویدیو', {
            'fields': (
                ('background_image', 'side_image'),
                'side_image_alt',
                ('section_video', 'video_poster'),
            ),
            'classes': ('collapse',),
        }),
    )


class GVCostSectionInline(admin.StackedInline):
    model = GVCostSection
    extra = 0
    max_num = 1
    can_delete = False
    verbose_name = 'Cost Section'
    verbose_name_plural = '💵 بخش هزینه‌ها'
    fieldsets = (
        (None, {
            'fields': (
                ('is_enabled', 'display_order'),
                'section_title',
                'section_subtitle',
                'section_description',
                'layout_style',
            ),
        }),
        ('تصاویر و ویدیو', {
            'fields': (
                ('background_image', 'side_image'),
                'side_image_alt',
                ('section_video', 'video_poster'),
            ),
            'classes': ('collapse',),
        }),
    )


class GVTestimonialsSectionInline(admin.StackedInline):
    model = GVTestimonialsSection
    extra = 0
    max_num = 1
    can_delete = False
    verbose_name = 'Testimonials Section'
    verbose_name_plural = '💬 بخش نظرات'
    fieldsets = (
        (None, {
            'fields': (
                ('is_enabled', 'display_order'),
                'section_title',
                'section_subtitle',
                'section_description',
                'layout_style',
            ),
        }),
        ('تصاویر و ویدیو', {
            'fields': (
                ('background_image', 'side_image'),
                'side_image_alt',
                ('section_video', 'video_poster'),
            ),
            'classes': ('collapse',),
        }),
    )


class GVFAQSectionInline(admin.StackedInline):
    model = GVFAQSection
    extra = 0
    max_num = 1
    can_delete = False
    verbose_name = 'FAQ Section'
    verbose_name_plural = '❓ بخش سوالات متداول'
    fieldsets = (
        (None, {
            'fields': (
                ('is_enabled', 'display_order'),
                'section_title',
                'section_subtitle',
                'layout_style',
            ),
        }),
        ('تصاویر و ویدیو', {
            'fields': (
                ('background_image', 'side_image'),
                'side_image_alt',
                ('section_video', 'video_poster'),
            ),
            'classes': ('collapse',),
        }),
    )


class GVFinalCTASectionInline(admin.StackedInline):
    model = GVFinalCTASection
    extra = 0
    max_num = 1
    can_delete = False
    verbose_name = 'Final CTA Section'
    verbose_name_plural = '📢 بخش فراخوان نهایی (CTA)'
    fieldsets = (
        ('تنظیمات کلی', {
            'fields': ('is_enabled', 'display_order'),
        }),
        ('متن‌ها', {
            'fields': (
                'title',
                'subtitle',
                'description',
            ),
        }),
        ('دکمه‌ها', {
            'fields': (
                ('primary_cta_text', 'primary_cta_link'),
                ('secondary_cta_text', 'secondary_cta_link'),
            ),
        }),
        ('تماس', {
            'fields': (
                ('whatsapp_number', 'phone_number'),
            ),
        }),
        ('تصاویر', {
            'fields': (
                'background_image',
                'background_video',
            ),
            'classes': ('collapse',),
        }),
    )


class GVSEOSettingsInline(admin.StackedInline):
    model = GVSEOSettings
    extra = 0
    max_num = 1
    can_delete = False
    verbose_name = 'SEO Settings'
    verbose_name_plural = '🔍 تنظیمات سئو'
    fieldsets = (
        ('متا تگ‌های اصلی', {
            'fields': (
                'seo_title',
                'meta_description',
                'meta_keywords',
                'canonical_url',
            ),
        }),
        ('تنظیمات اشتراک‌گذاری (Open Graph)', {
            'fields': (
                'og_title',
                'og_description',
                ('og_image', 'twitter_image'),
            ),
            'classes': ('collapse',),
        }),
        ('تنظیمات خزنده‌ها', {
            'fields': (
                ('robots_index', 'robots_follow'),
                'include_in_sitemap',
            ),
        }),
        ('Schema JSON-LD', {
            'fields': ('schema_json',),
            'classes': ('collapse',),
        }),
    )


class GVAnimationSettingsInline(admin.StackedInline):
    model = GVAnimationSettings
    extra = 0
    max_num = 1
    can_delete = False
    verbose_name = 'Animation Settings'
    verbose_name_plural = '✨ تنظیمات انیمیشن'
    classes = ['collapse']
    fieldsets = (
        ('تنظیمات کلی', {
            'fields': (
                ('animations_enabled', 'parallax_enabled', 'floating_cards_enabled'),
                ('animation_duration', 'animation_delay'),
            ),
        }),
        ('انیمیشن بخش‌ها', {
            'fields': (
                ('hero_animation', 'benefits_animation'),
                ('eligibility_animation', 'process_animation'),
                ('stats_animation', 'projects_animation'),
                ('family_animation', 'documents_animation'),
                ('cost_animation', 'testimonials_animation'),
                ('faq_animation', 'cta_animation'),
            ),
            'classes': ('collapse',),
        }),
    )


class GVDesignSettingsInline(admin.StackedInline):
    model = GVDesignSettings
    extra = 1
    max_num = 1
    can_delete = False
    verbose_name = '🎨 تنظیمات طراحی'
    verbose_name_plural = '🎨 تنظیمات طراحی'
    fieldsets = (
        ('رنگ‌ها', {
            'fields': (
                ('primary_color', 'secondary_color'),
                ('accent_color', 'background_color'),
                'text_color',
            ),
        }),
        ('فونت و استایل', {
            'fields': (
                ('card_style', 'font_family'),
                ('section_spacing', 'border_radius'),
                'custom_font_url',
            ),
        }),
    )


# ── Main Landing Page Admin - Professional Page Builder ───────────────────────

@admin.register(GoldenVisaLandingPage, site=persian_admin_site)
class GoldenVisaLandingPageAdmin(PersianBaseAdmin):
    """
    Professional Page Builder Admin for Golden Visa Landing Page.
    
    ویرایشگر حرفه‌ای صفحه لندینگ گلدن ویزا
    تمام بخش‌های صفحه از یک جا قابل مدیریت هستند.
    """
    
    form = GoldenVisaLandingPageForm
    list_display = ('title', 'slug', 'is_active', 'updated_at', 'edit_link')
    list_display_links = ('title',)
    prepopulated_fields = {'slug': ('title',)}
    list_filter = ('is_active',)
    search_fields = ('title', 'slug')
    save_on_top = True
    
    @admin.display(description='ویرایش')
    def edit_link(self, obj):
        return format_html(
            '<a href="/fa-admin/persian_cms/goldenvisalandingpage/{}/change/" '
            'style="background:#2563eb;color:#fff;padding:6px 12px;border-radius:6px;'
            'text-decoration:none;font-size:12px;">✏️ ویرایش</a>',
            obj.pk
        )
    
    fieldsets = (
        ('تنظیمات اصلی', {
            'fields': ('title', 'slug', 'is_active'),
        }),
        ('🎨 تنظیمات استایل (فونت، رنگ، سایز)', {
            'fields': (
                'style_font_family',
                ('style_primary_color', 'style_secondary_color'),
                ('style_hero_title_size', 'style_section_title_size', 'style_body_text_size'),
                ('style_button_radius', 'style_card_radius'),
                'style_hero_overlay_opacity',
            ),
            'description': 'از اینجا می‌توانید فونت، رنگ‌ها و سایز المان‌های صفحه را تغییر دهید',
        }),
        ('هیرو (Hero Section)', {
            'fields': (
                'hero_title',
                'hero_subtitle',
                'hero_image',
                'hero_video',
                'hero_cta_text',
                'hero_cta_link',
            ),
        }),
        ('معرفی', {
            'fields': ('intro_title', 'intro_body'),
        }),
        ('مزایا', {
            'fields': ('benefits_title', 'benefits_body'),
        }),
        ('شرایط', {
            'fields': ('requirements_title', 'requirements_body'),
        }),
        ('مراحل', {
            'fields': ('process_title', 'process_body'),
        }),
        ('سوالات متداول', {
            'fields': ('faq_title', 'faq_body'),
        }),
        ('بنر CTA', {
            'fields': ('cta_banner_title', 'cta_banner_text', 'cta_banner_button'),
        }),
        ('سئو', {
            'fields': ('meta_description', 'meta_keywords', 'og_image'),
        }),
    )
    
    # All section inlines - each section can have media/layout settings
    inlines = [
        GVHeroSectionInline,
        GVBenefitsSectionInline,
        GVEligibilitySectionInline,
        GVProcessSectionInline,
        GVStatisticsSectionInline,
        GVProjectsSectionInline,
        GVFamilySectionInline,
        GVDocumentsSectionInline,
        GVCostSectionInline,
        GVTestimonialsSectionInline,
        GVFAQSectionInline,
        GVFinalCTASectionInline,
        GVSEOSettingsInline,
        GVAnimationSettingsInline,
        GVDesignSettingsInline,
    ]
    
    class Media:
        css = {'all': ('css/persian-admin.css', 'css/gv-admin-fix.css',)}
        js = ('js/ckeditor5-word-cleanup.js',)
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        # Force white background on all text fields
        white_style = 'background-color: #fff !important; color: #1f2937 !important; border: 1px solid #d1d5db;'
        for field_name in form.base_fields:
            field = form.base_fields[field_name]
            if hasattr(field.widget, 'attrs'):
                existing_style = field.widget.attrs.get('style', '')
                field.widget.attrs['style'] = existing_style + white_style
        return form


# ── Section Admin Classes with Nested Items ───────────────────────────────────

@admin.register(GVHeroSection, site=persian_admin_site)
class GVHeroSectionAdmin(PersianBaseAdmin, ImagePreviewMixin):
    list_display = ('main_title', 'landing_page', 'is_enabled', 'cards_count')
    list_filter = ('is_enabled',)
    inlines = [GVHeroFloatingCardInline]
    
    fieldsets = (
        ('تنظیمات', {
            'fields': ('landing_page', 'is_enabled', 'display_order'),
        }),
        ('متن‌ها', {
            'fields': ('main_title', 'highlighted_word', 'subtitle', 'description'),
        }),
        ('دکمه‌ها', {
            'fields': (
                ('primary_cta_text', 'primary_cta_link'),
                ('secondary_cta_text', 'secondary_cta_link'),
            ),
        }),
        ('تصاویر و ویدیو', {
            'fields': (
                'hero_main_visual', 'hero_image_alt',
                'background_image', 'mobile_background_image',
                'background_video',
            ),
            'classes': ('collapse',),
        }),
    )
    
    @admin.display(description='کارت‌های شناور')
    def cards_count(self, obj):
        count = obj.floating_cards.count()
        return f'{count} کارت'


@admin.register(GVBenefitsSection, site=persian_admin_site)
class GVBenefitsSectionAdmin(PersianBaseAdmin):
    list_display = ('section_title', 'landing_page', 'is_enabled', 'cards_count')
    list_filter = ('is_enabled',)
    inlines = [GVBenefitCardInline]
    
    @admin.display(description='کارت‌های مزیت')
    def cards_count(self, obj):
        count = obj.benefit_cards.count()
        return f'{count} کارت'


@admin.register(GVEligibilitySection, site=persian_admin_site)
class GVEligibilitySectionAdmin(PersianBaseAdmin):
    list_display = ('section_title', 'landing_page', 'is_enabled', 'cards_count')
    list_filter = ('is_enabled',)
    inlines = [GVEligibilityCardInline]
    
    @admin.display(description='کارت‌های شرایط')
    def cards_count(self, obj):
        count = obj.eligibility_cards.count()
        return f'{count} کارت'


@admin.register(GVProcessSection, site=persian_admin_site)
class GVProcessSectionAdmin(PersianBaseAdmin):
    list_display = ('section_title', 'landing_page', 'is_enabled', 'steps_count')
    list_filter = ('is_enabled',)
    inlines = [GVProcessStepInline]
    
    @admin.display(description='مراحل')
    def steps_count(self, obj):
        count = obj.steps.count()
        return f'{count} مرحله'


@admin.register(GVStatisticsSection, site=persian_admin_site)
class GVStatisticsSectionAdmin(PersianBaseAdmin):
    list_display = ('section_title', 'landing_page', 'is_enabled', 'items_count')
    list_filter = ('is_enabled',)
    inlines = [GVStatItemInline]
    
    @admin.display(description='آیتم‌ها')
    def items_count(self, obj):
        count = obj.stat_items.count()
        return f'{count} آیتم'


@admin.register(GVProjectsSection, site=persian_admin_site)
class GVProjectsSectionAdmin(PersianBaseAdmin):
    list_display = ('section_title', 'landing_page', 'is_enabled', 'projects_count', 'relations_count')
    list_filter = ('is_enabled',)
    inlines = [GVProjectInline, GVFaPropertyRelationInline]
    
    fieldsets = (
        ('تنظیمات بخش', {
            'fields': ('landing_page', 'is_enabled', 'display_order'),
        }),
        ('محتوا', {
            'fields': ('section_title', 'section_subtitle', 'section_description'),
        }),
        ('دکمه CTA', {
            'fields': ('cta_text', 'cta_link'),
        }),
    )
    
    @admin.display(description='پروژه‌های جدید')
    def projects_count(self, obj):
        count = obj.projects.count()
        return f'{count} پروژه'
    
    @admin.display(description='پروژه‌های FaProperty')
    def relations_count(self, obj):
        count = obj.property_relations.count()
        return f'{count} پروژه'


@admin.register(GVProject, site=persian_admin_site)
class GVProjectAdmin(PersianBaseAdmin, ImagePreviewMixin):
    list_display = ('name', 'image_preview', 'starting_price', 'status', 'golden_visa_eligible', 'display_order', 'is_active')
    list_filter = ('status', 'golden_visa_eligible', 'is_active')
    search_fields = ('name', 'area', 'location_title')
    list_editable = ('display_order', 'is_active')
    inlines = [GVProjectUnitInline, GVProjectGalleryImageInline]
    
    fieldsets = (
        ('اطلاعات پروژه', {
            'fields': ('projects_section', 'name', 'short_description', 'is_active'),
        }),
        ('رسانه', {
            'fields': ('main_image', 'project_video'),
        }),
        ('موقعیت', {
            'fields': ('location_title', 'area', 'google_maps_link'),
        }),
        ('قیمت و وضعیت', {
            'fields': (
                ('starting_price', 'golden_visa_eligible'),
                ('status', 'progress_percentage'),
                'delivery_date',
            ),
        }),
        ('دکمه CTA', {
            'fields': ('cta_text', 'cta_link', 'display_order'),
        }),
    )


@admin.register(GVFaPropertyRelation, site=persian_admin_site)
class GVFaPropertyRelationAdmin(PersianBaseAdmin):
    list_display = ('get_title', 'property', 'badge_text', 'display_order', 'is_active')
    list_filter = ('is_active',)
    search_fields = ('display_title', 'property__name')
    list_editable = ('display_order', 'is_active')
    autocomplete_fields = ['property']
    
    @admin.display(description='عنوان نمایشی')
    def get_title(self, obj):
        return obj.display_title or obj.property.name


@admin.register(GVFamilySection, site=persian_admin_site)
class GVFamilySectionAdmin(PersianBaseAdmin):
    list_display = ('section_title', 'landing_page', 'is_enabled', 'cards_count')
    list_filter = ('is_enabled',)
    inlines = [GVFamilyMemberCardInline]
    
    @admin.display(description='کارت‌ها')
    def cards_count(self, obj):
        count = obj.member_cards.count()
        return f'{count} کارت'


@admin.register(GVDocumentsSection, site=persian_admin_site)
class GVDocumentsSectionAdmin(PersianBaseAdmin):
    list_display = ('section_title', 'landing_page', 'is_enabled', 'items_count')
    list_filter = ('is_enabled',)
    inlines = [GVDocumentItemInline]
    
    @admin.display(description='مدارک')
    def items_count(self, obj):
        count = obj.document_items.count()
        return f'{count} مدرک'


@admin.register(GVCostSection, site=persian_admin_site)
class GVCostSectionAdmin(PersianBaseAdmin):
    list_display = ('section_title', 'landing_page', 'is_enabled', 'items_count')
    list_filter = ('is_enabled',)
    inlines = [GVCostItemInline]
    
    @admin.display(description='هزینه‌ها')
    def items_count(self, obj):
        count = obj.cost_items.count()
        return f'{count} آیتم'


@admin.register(GVTestimonialsSection, site=persian_admin_site)
class GVTestimonialsSectionAdmin(PersianBaseAdmin):
    list_display = ('section_title', 'landing_page', 'is_enabled', 'items_count')
    list_filter = ('is_enabled',)
    inlines = [GVTestimonialInline]
    
    @admin.display(description='نظرات')
    def items_count(self, obj):
        count = obj.testimonials.count()
        return f'{count} نظر'


@admin.register(GVFAQSection, site=persian_admin_site)
class GVFAQSectionAdmin(PersianBaseAdmin):
    list_display = ('section_title', 'landing_page', 'is_enabled', 'items_count')
    list_filter = ('is_enabled',)
    inlines = [GVFAQItemInline]
    
    @admin.display(description='سوالات')
    def items_count(self, obj):
        count = obj.faq_items.count()
        return f'{count} سوال'


@admin.register(GVFinalCTASection, site=persian_admin_site)
class GVFinalCTASectionAdmin(PersianBaseAdmin):
    list_display = ('title', 'landing_page', 'is_enabled')
    list_filter = ('is_enabled',)


@admin.register(GVSEOSettings, site=persian_admin_site)
class GVSEOSettingsAdmin(PersianBaseAdmin):
    list_display = ('seo_title', 'landing_page', 'robots_index', 'include_in_sitemap')
    
    fieldsets = (
        ('متا تگ‌ها', {
            'fields': ('landing_page', 'seo_title', 'meta_description', 'meta_keywords', 'canonical_url'),
        }),
        ('Open Graph', {
            'fields': ('og_title', 'og_description', 'og_image', 'twitter_image'),
            'classes': ('collapse',),
        }),
        ('ربات‌ها', {
            'fields': ('robots_index', 'robots_follow', 'include_in_sitemap'),
        }),
        ('Schema', {
            'fields': ('schema_json',),
            'classes': ('collapse',),
        }),
    )


@admin.register(GVAnimationSettings, site=persian_admin_site)
class GVAnimationSettingsAdmin(PersianBaseAdmin):
    list_display = ('landing_page', 'animations_enabled', 'parallax_enabled')


@admin.register(GVDesignSettings, site=persian_admin_site)
class GVDesignSettingsAdmin(PersianBaseAdmin):
    list_display = ('landing_page', 'card_style', 'font_family', 'primary_color')


def _register_legacy_fa_models():
    """Expose the full /fa-new/ layout controls in the Persian admin."""
    for model, admin_class in (
        (FaNewSettings, FaNewSettingsAdmin),
        (FaNewSection, FaNewSectionAdmin),
        (FaNavMenuItem, FaNavMenuItemAdmin),
        (FaFooterSettings, FaFooterSettingsAdmin),
    ):
        try:
            persian_admin_site.register(model, admin_class)
        except admin.sites.AlreadyRegistered:
            continue


_register_legacy_fa_models()
