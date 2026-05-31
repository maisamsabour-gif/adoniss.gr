from django import forms
from django.contrib import admin
from django.utils.html import format_html
from django_ckeditor_5.widgets import CKEditor5Widget

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
)


class PersianBaseAdmin(admin.ModelAdmin):
    ordering = ("id",)

    class Media:
        css = {"all": ("css/persian-admin.css",)}


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
    list_display = ("title", "page_type", "public_link", "is_published", "seo_status", "sort_order")
    list_editable = ("is_published", "seo_status", "sort_order")
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
        return format_html('<a href="{}" target="_blank" rel="noopener">{}</a>', url, url)

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
            return format_html(
                '<div style="position:relative">'
                '<a href="{0}" target="_blank">'
                '<img src="{0}" style="height:60px;width:90px;object-fit:cover;border-radius:8px;'
                'box-shadow:0 2px 8px rgba(0,0,0,0.15)" /></a>'
                '{1}</div>',
                img.url,
                '<span style="position:absolute;top:2px;right:2px;background:#c9a227;color:#fff;'
                'font-size:9px;padding:1px 4px;border-radius:3px">ویژه</span>' if obj.is_featured else '',
            )
        return format_html('<span style="color:#999">—</span>')
    
    @admin.display(description='موقعیت')
    def location_display(self, obj):
        parts = [p for p in [obj.area, obj.location, obj.city] if p]
        return ' • '.join(parts) if parts else '—'
    
    @admin.display(description='قیمت')
    def price_display(self, obj):
        if obj.price_label:
            return format_html(
                '<span style="font-weight:600;color:#1a5f2a">{}</span>',
                obj.price_label,
            )
        if obj.price:
            formatted_price = f'€{obj.price:,.0f}'
            return format_html(
                '<span style="font-weight:600;color:#1a5f2a">{}</span>',
                formatted_price,
            )
        return '—'
    
    @admin.display(description='وضعیت')
    def status_badge(self, obj):
        colors = {
            'available': ('#059669', '#d1fae5'),
            'reserved': ('#d97706', '#fef3c7'),
            'sold_out_soon': ('#dc2626', '#fee2e2'),
            'sold_out': ('#6b7280', '#f3f4f6'),
        }
        bg, text_bg = colors.get(obj.status, ('#6b7280', '#f3f4f6'))
        return format_html(
            '<span style="background:{};color:#fff;padding:3px 8px;border-radius:12px;'
            'font-size:11px;font-weight:500">{}</span>',
            bg, obj.get_status_display(),
        )
    
    @admin.display(description='عملیات')
    def edit_button(self, obj):
        return format_html(
            '<a href="/fa-admin/persian_cms/faproperty/{}/change/" '
            'style="background:linear-gradient(135deg,#c9a227,#e8d48a);color:#1a1a2e;'
            'padding:6px 14px;border-radius:6px;text-decoration:none;font-weight:600;'
            'font-size:12px;display:inline-flex;align-items:center;gap:4px;'
            'box-shadow:0 2px 6px rgba(201,162,39,0.3);transition:all 0.2s">'
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
