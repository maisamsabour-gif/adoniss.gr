"""
core/admin.py — Admin registrations for all core app models.
Reconstructed from bytecode and project conventions.
"""
import json

from django import forms
from django.contrib import admin, messages
from django.db import transaction
from django.http import JsonResponse
from django.urls import path
from django.utils.html import format_html

from django_ckeditor_5.widgets import CKEditor5Widget

from core.admin_base import ModelAdmin, TabularInline, StackedInline, TranslationAdmin
from apps.persian_cms.admin_site import persian_admin_site
from core.admin_dashboard_seo import seo_dashboard
from core.admin_mixins import AuditAdminMixin, RoleProtectedAdminMixin, SoftDeleteAdminMixin
from core.admin_openai import make_translate_actions
from core.admin_seo import BaseSEOAdmin, SEO_FIELDSET
from core.rbac import (
    ROLE_ADMIN,
    ROLE_CONTENT,
    ROLE_CONTENT_ADMIN,
    ROLE_CONTENT_MANAGER,
    ROLE_PROPERTY_BLOG_EDITOR,
    ROLE_PROPERTY_BLOG_MGR,
    ROLE_SALES,
    ROLE_SUPPORT,
    ROLE_SUPERADMIN,
)

from .models import (
    AboutPageSettings,
    AuditLog,
    BlogCategory,
    BlogPost,
    ChatLead,
    ChatMessage,
    ChatSession,
    ChatSessionMessage,
    ContactSubmission,
    Customer,
    ErrorLog,
    Event,
    EventImage,
    FAQ,
    FooterSettings,
    FrontPageSettings,
    GoldenVisaCard,
    GoldenVisaFaLandingPage,
    GoldenVisaFaProcessStep,
    GoldenVisaLandingPage,
    HeaderSettings,
    Office,
    PageSEO,
    PartnerLead,
    PartnershipPageSettings,
    ProcessStep,
    PropertiesPageSettings,
    Service,
    SiteSettings,
    SlugHistory,
    TeamMember,
    Testimonial,
    WebinarLandingSettings,
    WebinarRegistration,
    FaNewSettings,
    FaNewFeaturedProperties,
    FaNewSection,
    FaNewSectionItem,
    FaNewGatewayCard,
    FaNavMenuItem,
    FaFooterSettings,
)

# ── Disable bulk hard-delete globally ─────────────────────────────────────────

if "delete_selected" in admin.site._actions:
    admin.site.disable_action("delete_selected")


# ── Register SEO dashboard custom view ────────────────────────────────────────

def _register_seo_dashboard():
    from django.urls import path
    original_get_urls = admin.site.__class__.get_urls

    def get_urls(self):
        custom = [path("seo-dashboard/", self.admin_view(seo_dashboard), name="seo_dashboard")]
        return custom + original_get_urls(self)

    admin.site.__class__.get_urls = get_urls


_register_seo_dashboard()


# ═══════════════════════════════════════════════════════════════════════════════
# Site / Header / Footer Settings
# ═══════════════════════════════════════════════════════════════════════════════

@admin.register(SiteSettings)
class SiteSettingsAdmin(RoleProtectedAdminMixin, AuditAdminMixin, ModelAdmin):
    allowed_roles = [ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_CONTENT_ADMIN]

    fieldsets = (
        ("General", {
            "fields": (
                "site_name", "tagline",
                "whatsapp_number", "phone_number", "email", "address",
            ),
        }),
        ("Social Media", {
            "fields": ("instagram_url", "facebook_url", "linkedin_url"),
        }),
        ("Notifications", {
            "fields": (
                "telegram_bot_token", "telegram_chat_id", "telegram_enabled",
            ),
        }),
        ("SEO & Analytics", {
            "fields": (
                "meta_description", "meta_keywords",
                "google_analytics_id",
                "google_ads_conversion_id", "google_ads_conversion_label",
                "microsoft_clarity_id",
            ),
        }),
    )

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(HeaderSettings)
class HeaderSettingsAdmin(RoleProtectedAdminMixin, AuditAdminMixin, TranslationAdmin):
    allowed_roles = [ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_CONTENT_ADMIN, ROLE_CONTENT]

    fieldsets = (
        ("Logo", {
            "fields": ("site_name", "logo", "logo_width", "logo_height"),
        }),
        ("Hero Section (Homepage)", {
            "fields": (
                "hero_title", "hero_subtitle",
                "hero_video", "hero_video_url", "hero_video_poster",
                "hero_video_embed_url",
                "hero_overlay", "hero_overlay_opacity",
                "hero_filter", "hero_brightness",
            ),
        }),
        ("Intro Section", {
            "fields": (
                "intro_video", "intro_video_url", "intro_video_poster",
                "intro_video_embed_url",
                "intro_title", "intro_text",
            ),
        }),
        ("Navigation", {
            "fields": (
                "whatsapp_number", "contact_button_text",
                "show_home", "show_properties", "show_partnerships",
                "show_about", "show_contact",
            ),
        }),
    )

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(FooterSettings)
class FooterSettingsAdmin(RoleProtectedAdminMixin, AuditAdminMixin, TranslationAdmin):
    allowed_roles = [ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_CONTENT_ADMIN, ROLE_CONTENT]

    fieldsets = (
        ("Company", {
            "fields": (
                "company_name", "description", "copyright_text", "address",
            ),
        }),
        ("Contact", {
            "fields": ("phone_number", "phone_number_2", "email", "whatsapp_number", "whatsapp_button_text"),
        }),
        ("Social Media", {
            "fields": (
                "instagram_url", "facebook_url", "linkedin_url",
                "x_url", "youtube_url",
            ),
        }),
    )

    def has_delete_permission(self, request, obj=None):
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# Services & Process Steps
# ═══════════════════════════════════════════════════════════════════════════════

@admin.register(Service)
class ServiceAdmin(RoleProtectedAdminMixin, AuditAdminMixin, TranslationAdmin):
    allowed_roles = [ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_CONTENT_ADMIN, ROLE_CONTENT]
    list_display = ["title", "icon", "order", "is_active"]
    list_editable = ["order", "is_active"]
    search_fields = ["title"]


@admin.register(ProcessStep)
class ProcessStepAdmin(RoleProtectedAdminMixin, AuditAdminMixin, ModelAdmin):
    allowed_roles = [ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_CONTENT_ADMIN, ROLE_CONTENT]
    list_display = ["step_number", "title", "is_active"]
    list_editable = ["is_active"]


# ═══════════════════════════════════════════════════════════════════════════════
# Contact & Lead Forms
# ═══════════════════════════════════════════════════════════════════════════════

@admin.register(ContactSubmission)
class ContactSubmissionAdmin(RoleProtectedAdminMixin, SoftDeleteAdminMixin, AuditAdminMixin, ModelAdmin):
    allowed_roles = [ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_SALES, ROLE_SUPPORT]
    list_display = ["full_name", "phone", "email", "request_type", "source", "is_read", "created_at", "superadmin_delete_btn"]
    list_filter = ["request_type", "source", "is_read", "deleted_at"]
    search_fields = ["full_name", "phone", "email"]
    list_editable = ["is_read"]
    readonly_fields = ["created_at", "source"]

    fieldsets = (
        ("Contact Info", {
            "fields": ("full_name", "phone", "email", "request_type", "message", "property_interest"),
        }),
        ("Status", {
            "fields": ("source", "is_read", "notes", "created_at"),
        }),
    )

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    def delete_model(self, request, obj):
        obj.hard_delete()

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.hard_delete()

    def get_actions(self, request):
        actions = super().get_actions(request)
        if request.user.is_superuser:
            actions['bulk_hard_delete_selected'] = (
                self.__class__.bulk_hard_delete_selected,
                'bulk_hard_delete_selected',
                '🗑 حذف دائمی موارد انتخاب‌شده (Superadmin)',
            )
        return actions

    def bulk_hard_delete_selected(self, request, queryset):
        from django.template.response import TemplateResponse
        if request.POST.get('confirm_bulk_delete') != 'yes':
            # Pass PKs as a plain list so the template can iterate directly
            selected_pks = list(queryset.values_list('pk', flat=True))
            context = {
                **self.admin_site.each_context(request),
                'opts': self.model._meta,
                'queryset': queryset,
                'count': len(selected_pks),
                'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
                'selected_pks': selected_pks,
                'title': 'تأیید حذف دائمی',
            }
            return TemplateResponse(request, 'admin/contact_bulk_delete_confirm.html', context)

        count = queryset.count()
        for obj in queryset:
            obj.hard_delete()
        self.message_user(request, f'{count} لید به‌صورت دائمی حذف شد.', level=messages.SUCCESS)

    bulk_hard_delete_selected.short_description = '🗑 حذف دائمی موارد انتخاب‌شده (Superadmin)'

    @admin.display(description="")
    def superadmin_delete_btn(self, obj):
        from django.urls import reverse
        if not (hasattr(self, '_request') and self._request and self._request.user.is_superuser):
            return ""
        url = reverse("admin:core_contactsubmission_delete", args=[obj.pk])
        return format_html(
            '<button type="button" class="pl-delete-trigger" data-url="{}" '
            'style="display:inline-flex;align-items:center;gap:4px;padding:3px 10px;'
            'border-radius:6px;background:#fee2e2;color:#dc2626;font-size:0.8rem;'
            'font-weight:600;cursor:pointer;border:1px solid #fca5a5;">'
            '<span style="font-size:0.9rem;">🗑</span> حذف'
            '</button>',
            url,
        )

    def changelist_view(self, request, extra_context=None):
        self._request = request
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(PartnerLead)
class PartnerLeadAdmin(RoleProtectedAdminMixin, AuditAdminMixin, ModelAdmin):
    allowed_roles = [ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_SALES, ROLE_SUPPORT]
    list_display = ["first_name", "last_name", "email", "phone", "partner_type", "country", "created_at", "superadmin_delete_btn"]
    list_filter = ["partner_type", "country"]
    search_fields = ["first_name", "last_name", "email", "phone"]
    readonly_fields = ["created_at"]

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    @admin.display(description="")
    def superadmin_delete_btn(self, obj):
        from django.urls import reverse
        if not (hasattr(self, '_request') and self._request and self._request.user.is_superuser):
            return ""
        url = reverse("admin:core_partnerlead_delete", args=[obj.pk])
        return format_html(
            '<button type="button" class="pl-delete-trigger" data-url="{}" '
            'style="display:inline-flex;align-items:center;gap:4px;padding:3px 10px;'
            'border-radius:6px;background:#fee2e2;color:#dc2626;font-size:0.8rem;'
            'font-weight:600;cursor:pointer;border:1px solid #fca5a5;">'
            '<span style="font-size:0.9rem;">🗑</span> حذف'
            '</button>',
            url,
        )

    def changelist_view(self, request, extra_context=None):
        self._request = request
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(Customer)
class CustomerAdmin(RoleProtectedAdminMixin, SoftDeleteAdminMixin, AuditAdminMixin, ModelAdmin):
    allowed_roles = [ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_SALES, ROLE_SUPPORT]
    list_display = ["full_name", "email", "phone", "created_at"]
    search_fields = ["full_name", "email", "phone"]
    readonly_fields = ["created_at", "updated_at"]


# ═══════════════════════════════════════════════════════════════════════════════
# Chat
# ═══════════════════════════════════════════════════════════════════════════════

class ChatMessageInline(TabularInline):
    model = ChatMessage
    extra = 0
    readonly_fields = ["direction", "message", "created_at"]
    fields = ["direction", "message", "created_at"]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ChatLead)
class ChatLeadAdmin(RoleProtectedAdminMixin, SoftDeleteAdminMixin, AuditAdminMixin, ModelAdmin):
    allowed_roles = [ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_SALES, ROLE_SUPPORT]
    list_display = [
        "name", "phone", "status", "lead_score", "is_read",
        "assigned_to", "follow_up_date", "created_at",
    ]
    list_filter = ["status", "lead_score", "is_read", "source", "deleted_at"]
    search_fields = ["name", "phone", "topic", "summary"]
    list_editable = ["status", "lead_score", "is_read"]
    readonly_fields = ["created_at", "telegram_sent", "telegram_sent_at"]
    date_hierarchy = "created_at"

    fieldsets = (
        ("Lead Info", {
            "fields": (
                "name", "phone", "topic", "country",
                "source", "source_page", "page_url", "language",
            ),
        }),
        ("Status & Assignment", {
            "fields": (
                "status", "lead_score", "is_read",
                "assigned_to", "follow_up_date", "last_contact_at",
            ),
        }),
        ("Notes", {
            "fields": ("summary", "internal_notes", "conversation_json"),
        }),
        ("Telegram", {
            "fields": ("telegram_sent", "telegram_sent_at"),
            "classes": ("collapse",),
        }),
        ("Timestamps", {
            "fields": ("created_at",),
            "classes": ("collapse",),
        }),
    )


class ChatSessionMessageInline(TabularInline):
    model = ChatSessionMessage
    extra = 0
    readonly_fields = ["role", "content", "is_read", "created_at"]
    fields = ["role", "content", "is_read", "created_at"]

    def has_add_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ChatSession)
class ChatSessionAdmin(RoleProtectedAdminMixin, ModelAdmin):
    allowed_roles = [ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_SALES, ROLE_SUPPORT]
    list_display = ["session_key", "phase", "lead", "agent", "created_at"]
    list_filter = ["phase"]
    search_fields = ["session_key"]
    readonly_fields = ["session_key", "created_at", "updated_at"]
    inlines = [ChatSessionMessageInline]


# ═══════════════════════════════════════════════════════════════════════════════
# Testimonials, FAQs
# ═══════════════════════════════════════════════════════════════════════════════

@admin.register(Testimonial)
class TestimonialAdmin(RoleProtectedAdminMixin, AuditAdminMixin, TranslationAdmin):
    allowed_roles = [
        ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_CONTENT_ADMIN, ROLE_CONTENT,
        ROLE_CONTENT_MANAGER,
    ]
    list_display = ["client_name", "client_country", "rating", "is_active", "created_at"]
    list_filter = ["is_active", "rating"]
    list_editable = ["is_active"]
    search_fields = ["client_name", "client_country"]

    fieldsets = (
        ("Client", {
            "fields": ("client_name", "client_country", "image", "image_alt", "rating", "is_active"),
        }),
        ("Content", {
            "fields": ("content",),
        }),
        SEO_FIELDSET,
    )

    def get_fieldsets(self, request, obj=None):
        from core.admin_seo import _filter_fieldsets
        return _filter_fieldsets(super().get_fieldsets(request, obj), self.model, self)


@admin.register(FAQ)
class FAQAdmin(RoleProtectedAdminMixin, AuditAdminMixin, TranslationAdmin):
    allowed_roles = [
        ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_CONTENT_ADMIN, ROLE_CONTENT,
        ROLE_CONTENT_MANAGER,
    ]
    list_display = ["question", "order", "is_active"]
    list_editable = ["order", "is_active"]
    search_fields = ["question", "answer"]


# ═══════════════════════════════════════════════════════════════════════════════
# About Page Settings
# ═══════════════════════════════════════════════════════════════════════════════

@admin.register(AboutPageSettings)
class AboutPageSettingsAdmin(RoleProtectedAdminMixin, AuditAdminMixin, TranslationAdmin):
    allowed_roles = [ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_CONTENT_ADMIN, ROLE_CONTENT]

    fieldsets = (
        ("Hero Section", {
            "fields": (
                "hero_title", "hero_subtitle",
                "hero_image", "hero_video_url",
            ),
            "description": (
                "Upload a hero background image or enter a video URL. "
                "If both are set, the image takes priority. "
                "Leave both empty to show the default blue gradient."
            ),
        }),
        ("Office Media", {
            "fields": (
                "office_video", "office_video_poster",
                "office_image_1", "office_image_2", "office_image_3",
                "about_exterior_image",
            ),
        }),
        ("About Text", {
            "fields": ("about_title", "about_text"),
        }),
        ("Team Section", {
            "fields": ("team_title", "team_subtitle"),
        }),
    )

    def has_delete_permission(self, request, obj=None):
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# Office & Team
# ═══════════════════════════════════════════════════════════════════════════════

@admin.register(Office)
class OfficeAdmin(RoleProtectedAdminMixin, AuditAdminMixin, TranslationAdmin):
    allowed_roles = [ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_CONTENT_ADMIN, ROLE_CONTENT]
    list_display = ["city", "country", "phone_number", "order", "is_active"]
    list_editable = ["order", "is_active"]


@admin.register(TeamMember)
class TeamMemberAdmin(RoleProtectedAdminMixin, AuditAdminMixin, TranslationAdmin):
    allowed_roles = [
        ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_CONTENT_ADMIN, ROLE_CONTENT,
        ROLE_CONTENT_MANAGER,
    ]
    list_display = ["name", "position", "order", "is_active"]
    list_editable = ["order", "is_active"]
    search_fields = ["name", "position"]


# ═══════════════════════════════════════════════════════════════════════════════
# Front Page Settings
# ═══════════════════════════════════════════════════════════════════════════════

@admin.register(FrontPageSettings)
class FrontPageSettingsAdmin(RoleProtectedAdminMixin, AuditAdminMixin, TranslationAdmin):
    allowed_roles = [ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_CONTENT_ADMIN, ROLE_CONTENT]

    fieldsets = (
        ("Typography", {
            "fields": ("heading_font", "body_font", "heading_size", "body_size", "body_color"),
            "classes": ("collapse",),
        }),
        ("Services Section", {
            "fields": (
                "services_badge", "services_title", "services_description",
            ),
        }),
        ("Process Section", {
            "fields": (
                "process_badge", "process_title", "process_description",
            ),
        }),
        ("Catalogue Section", {
            "fields": (
                "catalogue_badge_text", "catalogue_heading", "catalogue_subtext",
                "catalogue_btn1_title", "catalogue_btn1_label",
                "catalogue_btn2_title", "catalogue_btn2_label",
            ),
        }),
        ("Contact Section", {
            "fields": (
                "contact_badge", "contact_title", "contact_description",
            ),
        }),
    )

    def has_delete_permission(self, request, obj=None):
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# Blog
# ═══════════════════════════════════════════════════════════════════════════════

class BlogPostAdminForm(forms.ModelForm):
    """Force CKEditor5Widget for the content field for all users."""

    class Meta:
        model = BlogPost
        fields = "__all__"
        widgets = {
            "content": CKEditor5Widget(config_name="blog", attrs={"class": "django_ckeditor_5"}),
        }


BLOG_FIELD_PAIRS = [
    ("title_en", "title_tr"),
    ("slug_en", "slug_tr"),
    ("excerpt_en", "excerpt_tr"),
    ("content_en", "content_tr"),
    ("meta_title_en", "meta_title_tr"),
    ("meta_description_en", "meta_description_tr"),
    ("og_title_en", "og_title_tr"),
    ("og_description_en", "og_description_tr"),
]


@admin.register(BlogPost)
class BlogPostAdmin(
    BaseSEOAdmin,
    RoleProtectedAdminMixin,
    AuditAdminMixin,
    TranslationAdmin,
):
    form = BlogPostAdminForm
    allowed_roles = [
        ROLE_SUPERADMIN, ROLE_ADMIN,
        ROLE_CONTENT_ADMIN, ROLE_CONTENT, ROLE_CONTENT_MANAGER,
        ROLE_PROPERTY_BLOG_EDITOR, ROLE_PROPERTY_BLOG_MGR,
    ]

    list_display = [
        "title", "category", "author", "is_published", "noindex", "seo_status", "is_featured",
        "published_date", "views",
    ]
    list_filter = ["is_published", "noindex", "seo_status", "is_featured", "category", "published_date"]
    list_editable = ["is_published", "noindex", "seo_status", "is_featured"]
    search_fields = ["title", "slug", "excerpt", "author"]
    prepopulated_fields = {"slug": ("title",)}
    date_hierarchy = "published_date"

    readonly_fields = ["created_at", "updated_at", "views"]

    class Media:
        css = {"all": ("admin/css/seo_preview.css",)}
        js = ("admin/js/seo_preview.js",)

    fieldsets = (
        ("Content", {
            "fields": (
                "title", "slug", "category", "author",
                "excerpt", "content",
            ),
        }),
        ("Featured Image", {
            "fields": ("featured_image", "featured_image_alt"),
        }),
        ("Publishing", {
            "fields": ("is_published", "is_featured", "published_date"),
        }),
        SEO_FIELDSET,
        ("OG / Social", {
            "fields": ("og_title", "og_description"),
            "classes": ("collapse",),
        }),
        ("Statistics", {
            "fields": ("views",),
            "classes": ("collapse",),
        }),
    )

    actions = make_translate_actions(BLOG_FIELD_PAIRS)


@admin.register(BlogCategory)
class BlogCategoryAdmin(RoleProtectedAdminMixin, AuditAdminMixin, TranslationAdmin):
    allowed_roles = [
        ROLE_SUPERADMIN, ROLE_ADMIN,
        ROLE_CONTENT_ADMIN, ROLE_CONTENT, ROLE_CONTENT_MANAGER,
        ROLE_PROPERTY_BLOG_EDITOR, ROLE_PROPERTY_BLOG_MGR,
    ]
    list_display = ["name", "slug", "order", "is_active"]
    list_editable = ["order", "is_active"]
    prepopulated_fields = {"slug": ("name",)}


# ═══════════════════════════════════════════════════════════════════════════════
# Partnership Page Settings
# ═══════════════════════════════════════════════════════════════════════════════

@admin.register(PartnershipPageSettings)
class PartnershipPageSettingsAdmin(RoleProtectedAdminMixin, AuditAdminMixin, TranslationAdmin):
    allowed_roles = [ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_CONTENT_ADMIN, ROLE_CONTENT]

    fieldsets = (
        ("Hero", {
            "fields": ("hero_title", "hero_subtitle", "hero_image"),
        }),
        ("Video Section", {
            "fields": (
                "video", "video_cover", "video_url",
                "video_title", "video_subtitle",
            ),
        }),
        ("B2B Section", {
            "fields": ("b2b_title", "b2b_text", "b2b_image"),
        }),
        ("Benefits", {
            "fields": (
                "benefit_1_icon", "benefit_1_title", "benefit_1_text",
                "benefit_2_icon", "benefit_2_title", "benefit_2_text",
                "benefit_3_icon", "benefit_3_title", "benefit_3_text",
                "benefit_4_icon", "benefit_4_title", "benefit_4_text",
                "benefit_5_icon", "benefit_5_title", "benefit_5_text",
                "benefit_6_icon", "benefit_6_title", "benefit_6_text",
            ),
        }),
        ("CTA", {
            "fields": ("cta_title", "cta_text", "cta_button_text"),
        }),
    )

    def has_delete_permission(self, request, obj=None):
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# Properties Page Settings
# ═══════════════════════════════════════════════════════════════════════════════

@admin.register(PropertiesPageSettings)
class PropertiesPageSettingsAdmin(RoleProtectedAdminMixin, AuditAdminMixin, TranslationAdmin):
    allowed_roles = [ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_CONTENT_ADMIN, ROLE_CONTENT]

    fieldsets = (
        ("Hero", {
            "fields": (
                "hero_title", "hero_subtitle", "hero_badge",
                "hero_video", "hero_video_poster", "hero_image",
            ),
        }),
        ("Intro Section", {
            "fields": ("intro_title", "intro_text"),
        }),
    )

    def has_delete_permission(self, request, obj=None):
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# Golden Visa Cards
# ═══════════════════════════════════════════════════════════════════════════════

@admin.register(GoldenVisaCard)
class GoldenVisaCardAdmin(
    BaseSEOAdmin,
    RoleProtectedAdminMixin,
    AuditAdminMixin,
    TranslationAdmin,
):
    allowed_roles = [
        ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_CONTENT_ADMIN, ROLE_CONTENT,
        ROLE_CONTENT_MANAGER,
    ]
    list_display = ["title", "subtitle", "order", "is_active"]
    list_editable = ["order", "is_active"]
    search_fields = ["title", "subtitle"]

    fieldsets = (
        ("Card Content", {
            "fields": ("title", "subtitle", "description", "image", "image_alt", "order", "is_active"),
        }),
        SEO_FIELDSET,
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Events
# ═══════════════════════════════════════════════════════════════════════════════

class EventImageInline(TabularInline):
    model = EventImage
    extra = 1
    fields = ["image", "caption", "order", "is_active"]


class EventAdminForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = "__all__"
        widgets = {
            "full_description": CKEditor5Widget(
                config_name="event", attrs={"class": "django_ckeditor_5"}
            ),
        }


@admin.register(Event)
class EventAdmin(BaseSEOAdmin, RoleProtectedAdminMixin, AuditAdminMixin, TranslationAdmin):
    form = EventAdminForm
    allowed_roles = [
        ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_CONTENT_ADMIN, ROLE_CONTENT,
        ROLE_CONTENT_MANAGER,
    ]
    list_display = ["title", "event_date", "location", "order", "is_active"]
    list_filter = ["is_active", "event_date"]
    list_editable = ["order", "is_active"]
    search_fields = ["title", "slug", "short_description"]
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ["created_at", "updated_at"]
    inlines = [EventImageInline]

    fieldsets = (
        ("Event Info", {
            "fields": (
                "title", "slug", "short_description", "full_description",
                "thumbnail", "thumbnail_alt",
                "video_file", "video_url",
                "event_date", "location",
                "order", "is_active",
            ),
        }),
        SEO_FIELDSET,
        ("Timestamps", {
            "fields": ("created_at", "updated_at"),
            "classes": ("collapse",),
        }),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Golden Visa Landing Pages
# ═══════════════════════════════════════════════════════════════════════════════

GV_FIELD_PAIRS = [
    ("hero_title_en", "hero_title_tr"),
    ("hero_subtitle_en", "hero_subtitle_tr"),
    ("intro_text_en", "intro_text_tr"),
    ("section_1_title_en", "section_1_title_tr"),
    ("section_1_text_en", "section_1_text_tr"),
    ("section_2_title_en", "section_2_title_tr"),
    ("section_2_text_en", "section_2_text_tr"),
    ("section_3_title_en", "section_3_title_tr"),
    ("section_3_text_en", "section_3_text_tr"),
    ("tier_250_title_en", "tier_250_title_tr"),
    ("tier_250_desc_en", "tier_250_desc_tr"),
    ("tier_400_title_en", "tier_400_title_tr"),
    ("tier_400_desc_en", "tier_400_desc_tr"),
    ("tier_800_title_en", "tier_800_title_tr"),
    ("tier_800_desc_en", "tier_800_desc_tr"),
    ("benefits_title_en", "benefits_title_tr"),
    ("benefits_text_en", "benefits_text_tr"),
    ("process_title_en", "process_title_tr"),
]


@admin.register(GoldenVisaLandingPage)
class GoldenVisaLandingPageAdmin(RoleProtectedAdminMixin, AuditAdminMixin, TranslationAdmin):
    allowed_roles = [ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_CONTENT_ADMIN, ROLE_CONTENT]
    list_display = ["__str__", "is_published", "noindex", "seo_status", "robots_index"]
    list_editable = ["is_published", "noindex", "seo_status", "robots_index"]

    fieldsets = (
        ("Hero Section (/greece-golden-visa/)", {
            "fields": (
                "hero_title", "hero_subtitle",
                "hero_image", "hero_image_alt",
                "hero_video", "hero_video_opacity",
            ),
        }),
        ("Intro", {
            "fields": ("intro_text",),
        }),
        ("Sections", {
            "fields": (
                "section_1_title", "section_1_text", "section_1_image", "section_1_image_alt",
                "section_2_title", "section_2_text", "section_2_image", "section_2_image_alt",
                "section_3_title", "section_3_text", "section_3_image", "section_3_image_alt",
            ),
        }),
        ("Investment Tiers", {
            "fields": (
                "tier_250_title", "tier_250_desc", "tier_250_image", "tier_250_image_alt",
                "tier_400_title", "tier_400_desc", "tier_400_image", "tier_400_image_alt",
                "tier_800_title", "tier_800_desc", "tier_800_image", "tier_800_image_alt",
            ),
        }),
        ("Benefits & Process", {
            "fields": (
                "benefits_title", "benefits_text", "benefits_bg_image",
                "process_title", "process_steps",
            ),
        }),
        ("Short Videos", {
            "fields": (
                "short_video_urls",
                "short_video_url_1", "short_video_url_2", "short_video_url_3",
                "short_video_url_4", "short_video_url_5",
            ),
            "classes": ("collapse",),
        }),
        ("Publishing", {
            "fields": (
                "is_published",
                "meta_title",
                "meta_description",
                "canonical_url",
                "og_title",
                "og_description",
                "og_image",
                "focus_keyword",
                "noindex",
                "seo_status",
                "robots_index",
                "robots_follow",
            ),
        }),
    )

    actions = make_translate_actions(GV_FIELD_PAIRS)

    def has_delete_permission(self, request, obj=None):
        return False


FONT_SIZE_CHOICES = [
    ("12px", "12px"), ("14px", "14px"), ("16px", "16px"), ("18px", "18px"),
    ("20px", "20px"), ("22px", "22px"), ("24px", "24px"), ("28px", "28px"),
    ("32px", "32px"), ("36px", "36px"), ("40px", "40px"), ("44px", "44px"),
    ("48px", "48px"), ("52px", "52px"), ("56px", "56px"), ("60px", "60px"),
    ("64px", "64px"), ("72px", "72px"), ("80px", "80px"), ("96px", "96px"),
]


class GoldenVisaFaLandingPageForm(forms.ModelForm):
    hero_title_font_size = forms.ChoiceField(
        choices=FONT_SIZE_CHOICES,
        label="سایز فونت تیتر هیرو",
        widget=forms.Select(attrs={"style": "width:120px;"}),
    )
    hero_subtitle_font_size = forms.ChoiceField(
        choices=FONT_SIZE_CHOICES,
        label="سایز فونت ساب‌تایتل هیرو",
        widget=forms.Select(attrs={"style": "width:120px;"}),
    )
    hero_title_color = forms.CharField(
        label="رنگ فونت تیتر هیرو",
        widget=forms.TextInput(attrs={"type": "color", "style": "width:80px;height:40px;padding:2px;cursor:pointer;border-radius:6px;"}),
    )
    hero_subtitle_color = forms.CharField(
        label="رنگ فونت ساب‌تایتل هیرو",
        widget=forms.TextInput(attrs={"type": "color", "style": "width:80px;height:40px;padding:2px;cursor:pointer;border-radius:6px;"}),
    )

    class Meta:
        model = GoldenVisaFaLandingPage
        fields = "__all__"
        widgets = {
            "intro_text": CKEditor5Widget(config_name="blog", attrs={"class": "django_ckeditor_5"}),
        }


@admin.register(GoldenVisaFaLandingPage)
class GoldenVisaFaLandingPageAdmin(RoleProtectedAdminMixin, AuditAdminMixin, ModelAdmin):
    allowed_roles = [ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_CONTENT_ADMIN]
    form = GoldenVisaFaLandingPageForm
    list_display = ["__str__", "is_published", "noindex", "seo_status"]
    list_editable = ["is_published", "noindex", "seo_status"]

    fieldsets = (
        ("Hero", {
            "fields": (
                "hero_title", "hero_subtitle", "hero_cta_text",
                "hero_image", "hero_image_alt",
                "hero_video",
                "hero_image_opacity",
                "hero_content_vertical_align", "hero_content_horizontal_align",
                "hero_title_color", "hero_title_font_size",
                "hero_subtitle_color", "hero_subtitle_font_size",
            ),
        }),
        ("Intro Section", {
            "fields": (
                "intro_title", "intro_text", "intro_image", "intro_image_alt",
                "intro_bullet_1", "intro_bullet_2", "intro_bullet_3",
                "intro_feature_1_icon", "intro_feature_1_text",
                "intro_feature_2_icon", "intro_feature_2_text",
                "intro_feature_3_icon", "intro_feature_3_text",
            ),
        }),
        ("Investment Tiers", {
            "fields": (
                "tiers_title",
                "tier_1_title", "tier_1_short_desc", "tier_1_long_desc",
                "tier_1_price_label", "tier_1_price_amount",
                "tier_1_image", "tier_1_image_alt", "tier_1_cta_text",
                "tier_2_title", "tier_2_short_desc", "tier_2_long_desc",
                "tier_2_price_label", "tier_2_price_amount",
                "tier_2_image", "tier_2_image_alt", "tier_2_cta_text",
                "tier_3_title", "tier_3_short_desc", "tier_3_long_desc",
                "tier_3_price_label", "tier_3_price_amount",
                "tier_3_image", "tier_3_image_alt", "tier_3_cta_text",
            ),
        }),
        ("Projects", {
            "fields": ("projects_title",),
        }),
        ("Benefits", {
            "fields": (
                "benefits_title", "benefits_bg_image", "benefits_text",
            ),
        }),
        ("مزایای آدونیس گروپ (سکشن بعد از چرا گلدن ویزا)", {
            "fields": (
                "adonis_feat_section_title", "adonis_feat_section_subtitle",
                "adonis_feat_1_icon", "adonis_feat_1_title", "adonis_feat_1_text",
                "adonis_feat_2_icon", "adonis_feat_2_title", "adonis_feat_2_text",
                "adonis_feat_3_icon", "adonis_feat_3_title", "adonis_feat_3_text",
                "adonis_feat_4_icon", "adonis_feat_4_title", "adonis_feat_4_text",
                "adonis_feat_5_icon", "adonis_feat_5_title", "adonis_feat_5_text",
                "adonis_feat_6_icon", "adonis_feat_6_title", "adonis_feat_6_text",
            ),
        }),
        ("مراحل گلدن ویزا", {
            "fields": (
                "process_title",
                "step_1_title", "step_1_subtitle",
                "step_2_title", "step_2_subtitle",
                "step_3_title", "step_3_subtitle",
                "step_4_title", "step_4_subtitle",
                "step_5_title", "step_5_subtitle",
                "step_6_title", "step_6_subtitle",
            ),
        }),
        ("Why Adonis Section", {
            "fields": (
                "why_adonis_title", "why_adonis_subtitle",
                "why_item_1_icon", "why_item_1_title", "why_item_1_text",
                "why_item_2_icon", "why_item_2_title", "why_item_2_text",
                "why_item_3_icon", "why_item_3_title", "why_item_3_text",
                "why_item_4_icon", "why_item_4_title", "why_item_4_text",
                "why_adonis_bg_image", "why_adonis_overlay_opacity",
            ),
        }),
        ("Own Short Videos", {
            "fields": (
                "own_shorts_title",
                "own_short_video_url_1", "own_short_video_url_2",
                "own_short_video_url_3", "own_short_video_url_4",
                "own_shorts_more_url",
            ),
        }),
        ("Testimonial Short Videos", {
            "fields": (
                "testimonial_shorts_title",
                "testimonial_short_video_url_1", "testimonial_short_video_url_2",
                "testimonial_short_video_url_3", "testimonial_short_video_url_4",
                "testimonial_shorts_more_url",
            ),
        }),
        ("Social Links (FA)", {
            "fields": (
                "fa_instagram_url", "fa_linkedin_url", "fa_telegram_url",
                "fa_whatsapp_number", "fa_whatsapp_number_2",
                "fa_x_url", "fa_youtube_url",
            ),
        }),
        ("SEO & Publishing", {
            "fields": (
                "seo_title",
                "meta_description",
                "canonical_url",
                "og_title",
                "og_description",
                "og_image",
                "focus_keyword",
                "noindex",
                "seo_status",
                "robots_index",
                "robots_follow",
                "is_published",
            ),
        }),
    )

    def has_delete_permission(self, request, obj=None):
        return False


# ═══════════════════════════════════════════════════════════════════════════════
# Golden Visa FA Process Steps
# ═══════════════════════════════════════════════════════════════════════════════


@admin.register(GoldenVisaFaProcessStep)
class GoldenVisaFaProcessStepAdmin(RoleProtectedAdminMixin, ModelAdmin):
    allowed_roles = [ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_CONTENT_ADMIN]
    list_display = ['display_order', 'step_number', 'title', 'is_active']
    list_editable = ['display_order', 'is_active']
    list_display_links = ['title']
    ordering = ['display_order', 'step_number']
    fieldsets = (
        (None, {
            'fields': (
                'step_number', 'title', 'description',
                'icon', 'image',
                'display_order', 'is_active',
            ),
        }),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# Page SEO
# ═══════════════════════════════════════════════════════════════════════════════

@admin.register(PageSEO)
class PageSEOAdmin(RoleProtectedAdminMixin, AuditAdminMixin, ModelAdmin):
    allowed_roles = [ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_CONTENT_ADMIN]
    list_display = ["page_key", "seo_status", "noindex", "updated_at"]
    list_filter = ["seo_status", "noindex"]
    search_fields = ["page_key", "focus_keyword"]

    fieldsets = (
        ("Page", {
            "fields": ("page_key",),
        }),
        ("English SEO", {
            "fields": ("meta_title_en", "meta_desc_en", "og_title_en", "og_desc_en"),
        }),
        ("Turkish SEO", {
            "fields": ("meta_title_tr", "meta_desc_tr", "og_title_tr", "og_desc_tr"),
        }),
        ("OG Image", {
            "fields": ("og_image",),
        }),
        ("Common SEO", {
            "fields": ("canonical_url", "focus_keyword", "noindex", "seo_status", "updated_at"),
        }),
    )

    readonly_fields = ("updated_at",)


# ═══════════════════════════════════════════════════════════════════════════════
# Audit & Error Logs
# ═══════════════════════════════════════════════════════════════════════════════

@admin.register(AuditLog)
class AuditLogAdmin(RoleProtectedAdminMixin, ModelAdmin):
    allowed_roles = [ROLE_SUPERADMIN, ROLE_ADMIN]
    list_display = ["action", "actor", "object_ref", "content_type", "ip_address", "created_at"]
    list_filter = ["action", "content_type"]
    search_fields = ["object_ref", "actor__username", "ip_address"]
    readonly_fields = [
        "actor", "content_type", "object_id", "object_ref",
        "action", "changes", "ip_address", "created_at",
    ]
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(ErrorLog)
class ErrorLogAdmin(RoleProtectedAdminMixin, ModelAdmin):
    allowed_roles = [ROLE_SUPERADMIN, ROLE_ADMIN]
    list_display = ["error_type", "url", "method", "is_read", "ip_address", "created_at"]
    list_filter = ["error_type", "method", "is_read"]
    list_editable = ["is_read"]
    search_fields = ["error_type", "error_message", "url", "ip_address"]
    readonly_fields = [
        "error_type", "error_message", "traceback",
        "url", "method", "user_agent", "ip_address",
        "user", "request_data", "created_at",
    ]
    date_hierarchy = "created_at"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# ═══════════════════════════════════════════════════════════════════════════════
# Slug History (read-only)
# ═══════════════════════════════════════════════════════════════════════════════

@admin.register(SlugHistory)
class SlugHistoryAdmin(RoleProtectedAdminMixin, ModelAdmin):
    allowed_roles = [ROLE_SUPERADMIN, ROLE_ADMIN]
    list_display = ["old_slug", "content_type", "object_id", "language", "created_at"]
    list_filter = ["language", "content_type"]
    search_fields = ["old_slug"]
    readonly_fields = ["content_type", "object_id", "old_slug", "language", "created_at"]

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser


# ═══════════════════════════════════════════════════════════════════════════════
# Webinar Landing — Settings & Registrations
# Isolated admin for the Persian webinar landing page (/webinar/).
# ═══════════════════════════════════════════════════════════════════════════════

class WebinarLandingSettingsForm(forms.ModelForm):
    """Wires CKEditor5 to the long-text fields on the webinar landing settings.

    Uses the dedicated ``webinar_full`` config so admins get font-family,
    font-size, font-colour and background-colour controls on every text block.
    """

    class Meta:
        model = WebinarLandingSettings
        # The intro_title / intro_description / intro_video fields were
        # part of the now-deleted "Why this webinar" section. They are
        # excluded from the form so the admin UI stays clean. The columns
        # remain in the DB (no migration necessary) in case the section
        # is ever re-introduced in the future.
        exclude = ("intro_title", "intro_description", "intro_video")
        widgets = {
            "hero_subtitle":    CKEditor5Widget(config_name="webinar_full", attrs={"class": "django_ckeditor_5"}),
            "hero_description": CKEditor5Widget(config_name="webinar_full", attrs={"class": "django_ckeditor_5"}),
            "success_text":     CKEditor5Widget(config_name="webinar_full", attrs={"class": "django_ckeditor_5"}),
            "cta_title":        CKEditor5Widget(config_name="webinar_full", attrs={"class": "django_ckeditor_5"}),
        }


@admin.register(WebinarLandingSettings)
class WebinarLandingSettingsAdmin(RoleProtectedAdminMixin, AuditAdminMixin, ModelAdmin):
    """Admin for the singleton WebinarLandingSettings row."""

    allowed_roles = [ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_CONTENT_ADMIN, ROLE_CONTENT]
    form = WebinarLandingSettingsForm
    list_display = ["__str__", "active_status", "noindex", "seo_status"]
    list_editable = ["active_status", "noindex", "seo_status"]

    # Loaded only on this admin page — does NOT affect any other admin model
    # because the CSS selectors inside webinar-admin.css are scoped to
    # `.form-row.field-<webinar-only-field>` which only exist on this page.
    class Media:
        css = {"all": ("css/webinar-admin.css",)}

    fieldsets = (
        ("وضعیت صفحه / Page status", {
            "fields": ("active_status",),
            "description": (
                "اگر این گزینه غیرفعال شود، صفحه /webinar/ با خطای 404 نمایش داده می‌شود."
            ),
        }),
        ("Hero", {
            "fields": (
                "hero_badge",
                "hero_title",
                "hero_subtitle",
                "hero_description",
                "hero_background_image",
                "hero_speaker_photo",
                "hero_speaker_name",
                "hero_speaker_title",
            ),
        }),
        ("اطلاعات وبینار / Webinar info bar", {
            "fields": (
                "webinar_date_text",
                "webinar_time_text",
                "webinar_format_text",
            ),
        }),
        ("مزایا / Benefit cards", {
            "fields": (
                "benefit_1_title", "benefit_1_text",
                "benefit_2_title", "benefit_2_text",
                "benefit_3_title", "benefit_3_text",
            ),
        }),
        ("فرم ثبت‌نام / Registration form", {
            "fields": ("form_title", "form_button_text"),
        }),
        ("پیام موفقیت / Success modal", {
            "fields": ("success_title", "success_text", "success_button_text"),
        }),
        ("CTA پایانی / Final CTA", {
            "fields": ("cta_title", "cta_button_text"),
        }),
        ("SEO", {
            "fields": (
                "meta_title",
                "meta_description",
                "canonical_url",
                "og_title",
                "og_description",
                "og_image",
                "focus_keyword",
                "noindex",
                "seo_status",
            ),
            "classes": ("collapse",),
        }),
    )

    def has_add_permission(self, request):
        return not WebinarLandingSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        from django.shortcuts import redirect
        from django.urls import reverse
        obj = WebinarLandingSettings.objects.first()
        if obj is None:
            obj = WebinarLandingSettings.get_settings()
        return redirect(reverse("admin:core_webinarlandingsettings_change", args=[obj.pk]))


@admin.register(WebinarRegistration)
class WebinarRegistrationAdmin(RoleProtectedAdminMixin, AuditAdminMixin, ModelAdmin):
    """Admin for individual webinar registrations + CSV export."""

    allowed_roles = [ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_SALES, ROLE_SUPPORT, ROLE_CONTENT_ADMIN]

    list_display = ["full_name", "phone", "email", "created_at"]
    search_fields = ["first_name", "last_name", "phone", "email"]
    list_filter = ["created_at"]
    readonly_fields = ["first_name", "last_name", "phone", "email", "created_at"]
    date_hierarchy = "created_at"
    ordering = ["-created_at"]

    actions = ["export_registrations_csv"]

    fieldsets = (
        ("اطلاعات شرکت‌کننده / Participant", {
            "fields": ("first_name", "last_name", "phone", "email"),
        }),
        ("تاریخ / Timestamp", {
            "fields": ("created_at",),
        }),
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return request.user.is_superuser

    @admin.display(description="Full Name", ordering="first_name")
    def full_name(self, obj):
        return f"{obj.first_name} {obj.last_name}"

    @admin.action(description="📥 خروجی CSV از ثبت‌نام‌های انتخاب‌شده / Export selected as CSV")
    def export_registrations_csv(self, request, queryset):
        import csv
        from django.http import HttpResponse
        from django.utils import timezone as _tz

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        ts = _tz.now().strftime("%Y%m%d_%H%M%S")
        response["Content-Disposition"] = (
            f'attachment; filename="webinar_registrations_{ts}.csv"'
        )
        # UTF-8 BOM so Excel opens Persian text correctly.
        response.write("\ufeff")

        writer = csv.writer(response)
        writer.writerow([
            "First Name", "Last Name", "Phone", "Email", "Registered At",
        ])
        for reg in queryset.order_by("-created_at"):
            writer.writerow([
                reg.first_name,
                reg.last_name,
                reg.phone,
                reg.email,
                reg.created_at.strftime("%Y-%m-%d %H:%M:%S") if reg.created_at else "",
            ])
        return response

    def get_actions(self, request):
        actions = super().get_actions(request)
        # Make the CSV action available regardless of selection mode.
        return actions


# ── /fa-new/ Persian Preview Settings ────────────────────────────────────────

class _ColorInput(forms.TextInput):
    """<input type="color"> widget — works natively for hex values (#rrggbb)."""
    input_type = 'color'
    template_name = 'django/forms/widgets/input.html'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.attrs.setdefault('style', 'width:80px;height:36px;padding:2px;cursor:pointer;')


class FaNewSettingsForm(forms.ModelForm):
    """Custom form for FaNewSettings that applies CKEditor5 and color widgets."""

    class Meta:
        model = FaNewSettings
        fields = '__all__'
        widgets = {
            # ── Overlay subtitles → CKEditor 5 minimal ────────────────────
            'o1_subtitle': CKEditor5Widget(
                config_name='minimal',
                attrs={'class': 'django_ckeditor_5'},
            ),
            'o2_subtitle': CKEditor5Widget(
                config_name='minimal',
                attrs={'class': 'django_ckeditor_5'},
            ),
            'o3_subtitle': CKEditor5Widget(
                config_name='minimal',
                attrs={'class': 'django_ckeditor_5'},
            ),
            # ── Color pickers ─────────────────────────────────────────────
            'hero_text_color':            _ColorInput(),
            'hero_subtitle_color':        _ColorInput(),
            'hero_accent_color':          _ColorInput(),
            'hero_scrim_color':           _ColorInput(),
            'hero_cta_primary_bg':        _ColorInput(),
            'hero_cta_primary_text':      _ColorInput(),
            'hero_cta_secondary_border':  _ColorInput(),
            'hero_cta_secondary_text':    _ColorInput(),
        }


@admin.register(FaNewSettings)
class FaNewSettingsAdmin(ModelAdmin):
    change_form_template = 'admin/core/fanewsettings/change_form.html'
    form = FaNewSettingsForm
    list_display = ('__str__', 'has_logo', 'has_video', 'updated_at')
    readonly_fields = ('updated_at',)

    fieldsets = (
        # ── 1. Logo ───────────────────────────────────────────────────────
        ('لوگو هدر', {
            'description': 'PNG با پس‌زمینه شفاف — ارتفاع ۶۰ تا ۱۲۰ پیکسل.',
            'fields': ('header_logo',),
        }),

        # ── 2. Hero Video ─────────────────────────────────────────────────
        ('ویدیو هیرو', {
            'description': 'MP4 (H.264) با faststart — حداکثر ۵۰۰ مگابایت.',
            'fields': ('hero_video', 'hero_video_poster'),
        }),

        # ── 3. Hero Overlay Texts ─────────────────────────────────────────
        ('متن‌های هیرو فارسی', {
            'description': (
                'متن‌هایی که روی اولین اسلاید ویدیوی هیرو نمایش داده می‌شوند. '
                'اگر خالی باشند، متن‌های پیش‌فرض نشان داده می‌شود.'
            ),
            'fields': (
                'hero_label',
                'hero_title',
                'hero_subtitle',
                ('hero_cta_text', 'hero_cta_url'),
            ),
        }),

        # ── 4. Overlay 1 ──────────────────────────────────────────────────
        ('🎬 متن اسلاید ۱ — روی ویدیو', {
            'classes': ('collapse',),
            'description': (
                'اولین متنی که هنگام شروع اسکرول نشان داده می‌شود. '
                'درصد شروع/پایان: ۰ = ابتدای اسکرول، ۱۰۰ = انتهای هیرو.'
            ),
            'fields': (
                ('o1_eyebrow', 'o1_highlight'),
                'o1_title',
                'o1_subtitle',
                ('o1_start', 'o1_end'),
            ),
        }),

        # ── 5. Overlay 2 ──────────────────────────────────────────────────
        ('🎬 متن اسلاید ۲ — روی ویدیو', {
            'classes': ('collapse',),
            'fields': (
                ('o2_eyebrow', 'o2_highlight'),
                'o2_title',
                'o2_subtitle',
                ('o2_start', 'o2_end'),
            ),
        }),

        # ── 6. Overlay 3 ──────────────────────────────────────────────────
        ('🎬 متن اسلاید ۳ — روی ویدیو', {
            'classes': ('collapse',),
            'fields': (
                ('o3_eyebrow', 'o3_highlight'),
                'o3_title',
                'o3_subtitle',
                ('o3_start', 'o3_end'),
            ),
        }),

        # ── 7. Overlay 4 (CTA) ────────────────────────────────────────────
        ('🎬 متن اسلاید ۴ — دکمه‌دار (CTA)', {
            'classes': ('collapse',),
            'description': 'آخرین اسلاید — دکمه‌های دریافت مشاوره اینجا تعریف می‌شوند.',
            'fields': (
                ('o4_eyebrow', 'o4_highlight'),
                'o4_title',
                ('o4_start', 'o4_end'),
            ),
        }),

        # ── 8. CTA Buttons ────────────────────────────────────────────────
        ('دکمه‌های CTA', {
            'description': 'دکمه‌هایی که در اسلاید ۴ نمایش داده می‌شوند.',
            'fields': (
                ('cta_primary_label', 'cta_primary_url'),
                ('cta_secondary_label', 'cta_secondary_url'),
            ),
        }),

        # ── 9. Colors ─────────────────────────────────────────────────────
        ('رنگ‌های هیرو', {
            'classes': ('collapse',),
            'description': (
                'رنگ‌ها باید به فرمت hex (#rrggbb) وارد شوند تا color picker کار کند. '
                'برای رنگ‌های شفاف می‌توانید مستقیم rgba() تایپ کنید.'
            ),
            'fields': (
                ('hero_text_color', 'hero_subtitle_color', 'hero_accent_color', 'hero_scrim_color'),
                ('hero_cta_primary_bg', 'hero_cta_primary_text',
                 'hero_cta_secondary_border', 'hero_cta_secondary_text'),
            ),
        }),

        # ── 10. Advanced / Notes ──────────────────────────────────────────
        ('یادداشت داخلی / پیشرفته', {
            'classes': ('collapse',),
            'fields': ('note', 'updated_at'),
        }),
    )

    def has_logo(self, obj):
        return bool(obj.header_logo)
    has_logo.boolean = True
    has_logo.short_description = 'لوگو'

    def has_video(self, obj):
        return bool(obj.hero_video)
    has_video.boolean = True
    has_video.short_description = 'ویدیو'

    def has_add_permission(self, request):
        return not FaNewSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        from django.urls import reverse
        from django.shortcuts import redirect
        obj = FaNewSettings.get_settings()
        return redirect(reverse('admin:core_fanewsettings_change', args=[obj.pk]))


# ── /fa-new/ Featured Properties (5 slots for homepage carousel) ──────────────

@admin.register(FaNewFeaturedProperties)
class FaNewFeaturedPropertiesAdmin(ModelAdmin):
    """Admin for selecting 5 featured properties for the Persian homepage carousel."""
    
    list_display = ('__str__', 'slot_1_name', 'slot_2_name', 'slot_3_name', 'slot_4_name', 'slot_5_name')
    
    fieldsets = (
        ('📌 املاک منتخب کاروسل صفحه اصلی', {
            'description': (
                'از اینجا ۵ ملک را برای نمایش در کاروسل صفحه اصلی فارسی انتخاب کنید. '
                'این املاک به ترتیب از ۱ تا ۵ در کاروسل نمایش داده می‌شوند. '
                'هر ملکی که انتخاب نکنید، اسلات خالی می‌ماند و نمایش داده نمی‌شود.'
            ),
            'fields': (
                'property_1',
                'property_2',
                'property_3',
                'property_4',
                'property_5',
            ),
        }),
    )
    
    raw_id_fields = ['property_1', 'property_2', 'property_3', 'property_4', 'property_5']
    
    @admin.display(description='ملک ۱')
    def slot_1_name(self, obj):
        return obj.property_1.name if obj.property_1 else '—'
    
    @admin.display(description='ملک ۲')
    def slot_2_name(self, obj):
        return obj.property_2.name if obj.property_2 else '—'
    
    @admin.display(description='ملک ۳')
    def slot_3_name(self, obj):
        return obj.property_3.name if obj.property_3 else '—'
    
    @admin.display(description='ملک ۴')
    def slot_4_name(self, obj):
        return obj.property_4.name if obj.property_4 else '—'
    
    @admin.display(description='ملک ۵')
    def slot_5_name(self, obj):
        return obj.property_5.name if obj.property_5 else '—'
    
    def has_add_permission(self, request):
        return not FaNewFeaturedProperties.objects.exists()
    
    def has_delete_permission(self, request, obj=None):
        return False
    
    def changelist_view(self, request, extra_context=None):
        from django.urls import reverse
        from django.shortcuts import redirect
        obj = FaNewFeaturedProperties.get_settings()
        return redirect(reverse('admin:core_fanewfeaturedproperties_change', args=[obj.pk]))


# ── /fa-new/ Section builder ──────────────────────────────────────────────────

class FaNewSectionItemInline(StackedInline):
    model = FaNewSectionItem
    extra = 0
    fieldsets = (
        (None, {
            'fields': (
                ('order', 'badge', 'is_featured', 'stat_number'),
                ('title', 'subtitle', 'amount', 'location'),
                ('description', 'body'),
                ('author_name', 'author_meta'),
                ('cta_label', 'cta_url'),
                ('image', 'image_alt', 'accent_color'),
            )
        }),
    )
    ordering = ('order',)
    ordering_field = 'order'
    hide_ordering_field = False
    show_change_link = False
    classes = ('collapse', 'fa-section-items-inline')
    tab = True

    def get_extra(self, request, obj=None, **kwargs):
        return super().get_extra(request, obj, **kwargs)


class FaNewResidencyTypeInline(StackedInline):
    """Inline for the 3 residency type cards (residency_types section)."""
    model = FaNewSectionItem
    extra = 0
    min_num = 3
    max_num = 3
    validate_min = True
    classes = ()
    tab = False
    verbose_name = 'کارت اقامت'
    verbose_name_plural = '۳ کارت اقامت یونان — هر کارت را پر کنید'
    ordering = ('order',)
    
    fieldsets = (
        ('📷 تصویر کارت', {
            'fields': ('image', 'image_alt'),
            'description': 'تصویر پس‌زمینه کارت (ابعاد پیشنهادی: 800×600 پیکسل)',
        }),
        ('📝 محتوای کارت', {
            'fields': ('title', 'body'),
            'description': 'عنوان و توضیح کوتاه کارت',
        }),
        ('🔗 لینک صفحه لندینگ', {
            'fields': ('cta_label', 'cta_url'),
            'description': 'متن دکمه (مثلاً «ادامه مطلب») و لینک صفحه لندینگ (مثلاً /fa-new/p/golden-visa/)',
        }),
        ('⚙️ تنظیمات', {
            'fields': ('order',),
            'classes': ('collapse',),
        }),
    )

    def get_extra(self, request, obj=None, **kwargs):
        try:
            existing = obj.items.count() if obj else 0
        except Exception:
            existing = 0
        return max(0, 3 - existing)


class FaNewGatewayCardInline(StackedInline):
    model = FaNewGatewayCard
    extra = 0
    ordering_field = 'order'
    hide_ordering_field = True
    show_change_link = False
    fields = (
        'order',
        'is_active',
        'badge',
        'title',
        'subtitle',
        'description',
        'image_preview',
        'image',
        'image_alt',
        'cta_text',
        'cta_link',
        'overlay_color',
        'overlay_opacity',
        'accent_color',
        'hover_preset',
    )
    ordering = ('order', 'id')
    classes = ()
    tab = True
    readonly_fields = ('image_preview',)
    verbose_name = 'کارت مسیر سرمایه‌گذاری'
    verbose_name_plural = 'کارت‌های مسیر سرمایه‌گذاری'

    def get_queryset(self, request):
        qs = super().get_queryset(request)
        return qs.filter(section__section_type='gateway')

    def has_add_permission(self, request, obj=None):
        if obj and obj.section_type != 'gateway':
            return False
        return super().has_add_permission(request, obj)

    def image_preview(self, obj):
        if not obj or not obj.image:
            return '—'
        return format_html(
            '<img src="{}" alt="{}" style="width:88px;height:56px;object-fit:cover;border-radius:8px;border:1px solid rgba(100,116,139,.35)">',
            obj.image.url,
            obj.image_alt or obj.title or 'gateway-card',
        )
    image_preview.short_description = 'پیش‌نمایش تصویر'


def _inject_persian_quick_nav(context):
    """Persian admin quick-nav injector.

    The original helper was referenced from ``render_change_form`` but its
    definition was missing from the uploaded project, which raised NameError
    (HTTP 500) on every section change page. No template depends on its output,
    so this is a safe no-op that keeps the change form working. Re-implement
    here if the quick-nav links need to be restored.
    """
    return context


_FA_SECTION_HINTS = {
    'why_greece': (
        'info',
        "📌 بخش ۱ — «مزایای کلیدی یونان» — "
        "این سکشن ۴ کارت شیشه‌ای زیر Hero نمایش می‌دهد. "
        "عنوان/زیرعنوان سکشن از فیلدهای «متن» خوانده می‌شود. "
        "تصویر پس‌زمینه را از بخش «تصاویر» آپلود کنید. "
        "هر کارت را از طریق آیتم‌های پایین (عنوان + متن) مدیریت کنید.",
    ),
    'why_adonis': (
        'success',
        "📌 بخش ۲ — «آشنایی با آدونیس» — "
        "این سکشن بعد از مزایای یونان نمایش داده می‌شود. "
        "تصویر اصلی را از فیلد «تصاویر» آپلود کنید. "
        "آمار را از طریق آیتم‌های پایین اضافه کنید. "
        "آیتم‌هایی که عدد آمار دارند به‌صورت استت‌کارت و بقیه به‌صورت بولت نمایش می‌یابند.",
    ),
    'why_adonis_stats': (
        'success',
        "سکشن چرا آدونیس - ۴ کارت آماری. "
        "متن‌ها: eyebrow، title، title_color، subtitle. "
        "تصویر: background_image و background_image_opacity (0-100). "
        "کارت‌ها: stat_number (عدد)، badge (پسوند +)، title (عنوان).",
    ),
    'intro_stats': (
        'warning',
        "⚠️ «آشنایی با آدونیس (قدیمی)» — "
        "این نوع بخش قدیمی است. لطفاً نوع بخش را به «آشنایی با آدونیس» (why_adonis) تغییر دهید. "
        "محتوای این سکشن به همان شکل why_adonis نمایش داده می‌شود.",
    ),
    'gateway': (
        'info',
        "📌 بخش ۳ — «معرفی خدمات آدونیس» — "
        "کارت‌های این سکشن از اینلاین «کارت‌های مسیر سرمایه‌گذاری» مدیریت می‌شوند. "
        "هر کارت تصویر، عنوان، توضیح و CTA مستقل دارد.",
    ),
    'featured_properties': (
        'success',
        "📌 «پروژه‌های منتخب املاک» — این سکشن یک کاروسل از املاک واقعی شماست. "
        "کارت‌ها از «املاک» (properties) خوانده می‌شوند، نه از آیتم‌های این سکشن. "
        "برای انتخاب اینکه کدام پروژه‌ها روی فرانت‌پیج بیایند، در «همه ملک‌ها» تیک "
        "«نمایش در صفحه اصلی» (show_on_homepage) را بزنید و ترتیب را با «display_order» تنظیم کنید. "
        "فقط عنوان/زیرعنوان این سکشن از همین‌جا خوانده می‌شود.",
    ),
    'residency_types': (
        'info',
        "📌 «انواع اقامت یونان» — ۳ کارت لاکچری زیر هم. "
        "هر کارت را از آیتم‌های پایین بسازید: «عنوان» = تیتر روی کارت، «متن» = توضیح کوتاه، "
        "«تصویر» = عکس پس‌زمینه کارت (داخل آیتم‌ها، نه بخش تصاویر)، و «لینک دکمه (cta_url)» = آدرس لندینگ‌پیج آن کارت "
        "(مثلاً /fa-new/p/اسلاگ/ که از بخش «صفحات فارسی» می‌سازید). "
        "«متن دکمه» پیش‌فرض «ادامه مطلب» است.",
    ),
    'routes': (
        'info',
        "📌 سکشن «مسیرهای گلدن ویزا» — "
        "هر آیتم یک مسیر سرمایه‌گذاری است. "
        "ویژگی‌ها را در فیلد «متن/توضیح» هر خط جداگانه بنویسید. "
        "اگر تصویر کارت لازم دارید از فیلد «تصویر» استفاده کنید.",
    ),
    'projects': (
        'info',
        "📌 سکشن «پروژه‌های منتخب» — "
        "برای هر پروژه یک آیتم با تصویر، عنوان، موقعیت و لینک اضافه کنید.",
    ),
    'process': (
        'info',
        "📌 سکشن «فرآیند همکاری» — "
        "هر آیتم یک مرحله از فرآیند است. "
        "شماره مرحله را در فیلد «برچسب/شماره» وارد کنید.",
    ),
    'trust': (
        'info',
        "📌 سکشن «اعتماد و تجربه» — "
        "هر آیتم یک نقل‌قول از مشتری است. "
        "متن نقل‌قول را در «متن/توضیح»، نام و مشخصات را در فیلدهای مربوطه وارد کنید.",
    ),
    'consult': (
        'success',
        "📌 سکشن «مشاوره رایگان» — "
        "این سکشن به‌صورت خودکار فرم مشاوره را نمایش می‌دهد. "
        "عنوان و زیرعنوان را از فیلدهای متن تنظیم کنید.",
    ),
}

# Fields that are only relevant for specific section types.
# Any field not listed here is shown for all section types.
_FA_SECTION_TYPE_IMAGES_FIELDS = {
    'intro_stats': (
        ('background_image', 'background_image_alt'),
        'background_video',
    ),
    'why_adonis': (
        ('background_image', 'background_image_alt'),
        'background_video',
    ),
    'why_adonis_stats': (
        ('background_image', 'background_image_alt'),
        ('background_image_opacity', 'background_image_position'),
    ),
    'why_greece': (
        ('background_image', 'background_image_alt'),
        ('background_image_opacity', 'background_image_position'),
    ),
    'gateway': (
        ('card_image_1', 'card_image_1_alt'),
        ('card_image_2', 'card_image_2_alt'),
        'background_video',
    ),
    'projects': (
        ('background_image', 'background_image_alt'),
    ),
}

_FA_SECTION_BASE_IMAGES_FIELDS = (
    ('background_image', 'background_image_alt'),
    ('card_image_1', 'card_image_1_alt'),
    ('card_image_2', 'card_image_2_alt'),
    'background_video',
)


class FaNewSectionForm(forms.ModelForm):
    """Custom form for FaNewSection with color picker widgets."""
    class Meta:
        model = FaNewSection
        fields = '__all__'
        widgets = {
            'title_color': _ColorInput(),
            'text_color': _ColorInput(),
            'accent_color': _ColorInput(),
            'background_color': _ColorInput(),
            'gradient_color': _ColorInput(),
            'card_background': _ColorInput(),
            'border_color': forms.TextInput(attrs={'style': 'width:200px;'}),
            'card_1_accent_color': _ColorInput(),
            'card_2_accent_color': _ColorInput(),
        }


@admin.register(FaNewSection)
class FaNewSectionAdmin(admin.ModelAdmin):
    form = FaNewSectionForm
    change_form_template = 'admin/core/fanewsection/change_form.html'
    change_list_template = 'admin/core/fanewsection/change_list.html'
    list_display = (
        'order',
        'section_type_badge',
        'section_name',
        'title_preview',
        'is_active',
        'device_visibility',
        'item_count',
        'preview_button',
    )
    list_display_links = ('order', 'section_type_badge', 'section_name')
    list_editable = ('is_active',)
    list_filter = ('section_type', 'is_active', 'show_on_desktop', 'show_on_mobile')
    search_fields = ('section_name', 'title', 'subtitle', 'anchor_id')
    ordering = ('order', 'id')
    readonly_fields = ('admin_small_preview', 'preview_button', 'section_type_badge')

    # ── base fieldset layout (can be pruned per section_type via get_fieldsets) ──
    fieldsets = (
        ('۱ · تنظیمات عمومی', {
            'description': 'نام داخلی برای مدیریت در پنل ادمین استفاده می‌شود و روی سایت نمایش داده نمی‌شود.',
            'fields': (
                ('section_name', 'section_type'),
                ('is_active', 'order'),
                'anchor_id',
                ('show_on_desktop', 'show_on_mobile'),
                'preview_button',
            ),
        }),
        ('۲ · برچسب کوچک (Eyebrow)', {
            'description': 'متن کوچک بالای عنوان اصلی',
            'fields': (
                'eyebrow',
                'accent_color',
            ),
        }),
        ('۳ · عنوان اصلی (Title)', {
            'description': 'عنوان بزرگ سکشن با تنظیمات رنگ و سایز',
            'fields': (
                'title',
                'title_color',
                ('title_font_size_desktop', 'title_font_size_mobile'),
                'text_alignment',
            ),
        }),
        ('۴ · زیرعنوان (Subtitle)', {
            'description': 'توضیحات زیر عنوان اصلی',
            'fields': (
                'subtitle',
                ('text_color', 'subtitle_font_size', 'subtitle_alignment'),
            ),
        }),
        ('۵ · توضیحات و دکمه‌ها', {
            'classes': ('collapse',),
            'description': 'توضیحات اضافی و دکمه‌های CTA',
            'fields': (
                'description',
                'description_font_size',
                ('cta_primary_text', 'cta_primary_url'),
                ('cta_secondary_text', 'cta_secondary_url'),
            ),
        }),
        ('۶ · تصاویر و ویدیو', {
            'description': 'تصویر پس‌زمینه سکشن',
            'fields': _FA_SECTION_BASE_IMAGES_FIELDS,
        }),
        ('۷ · طراحی پس‌زمینه', {
            'classes': ('collapse',),
            'description': 'رنگ پس‌زمینه و استایل سکشن',
            'fields': (
                ('background_color', 'gradient_color'),
                ('card_background', 'border_color'),
                ('border_radius', 'shadow_intensity', 'blur_intensity'),
                ('section_padding_top', 'section_padding_bottom', 'card_gap'),
                ('font_weight', 'line_height'),
            ),
        }),
        ('۸ · کارت‌های دو‌تایی (gateway)', {
            'classes': ('collapse',),
            'description': 'فیلدهای قدیمی gateway.',
            'fields': (
                'card_1_label', 'card_1_title', 'card_1_subtitle', 'card_1_description',
                ('card_1_image', 'card_1_image_alt'),
                ('card_1_cta_text', 'card_1_cta_link'),
                'card_1_accent_color',
                'card_2_label', 'card_2_title', 'card_2_subtitle', 'card_2_description',
                ('card_2_image', 'card_2_image_alt'),
                ('card_2_cta_text', 'card_2_cta_link'),
                'card_2_accent_color',
            ),
        }),
        ('۹ · ریسپانسیو و نمایش', {
            'classes': ('collapse',),
            'fields': (
                ('mobile_layout', 'desktop_layout'),
                ('max_width_container', 'hide_image_on_mobile'),
            ),
        }),
        ('۱۰ · المان تزئینی', {
            'classes': ('collapse',),
            'description': 'گل‌های تزئینی بین هیرو و سکشن gateway.',
            'fields': (
                'decorative_flowers_enabled',
                ('decorative_left_image', 'decorative_right_image'),
                ('decorative_opacity', 'decorative_blur_intensity'),
                ('decorative_animation_enabled', 'decorative_show_on_mobile'),
            ),
        }),
        ('۹ · پیش‌نمایش', {
            'fields': ('admin_small_preview',),
        }),
    )

    # ── list_display helpers ───────────────────────────────────────────────────

    _SECTION_TYPE_COLORS = {
        'why_greece':  ('🇬🇷', '#ecfdf5', '#166534'),
        'gateway':     ('🏢', '#eff6ff', '#1d4ed8'),
        'intro_stats': ('⭐', '#fefce8', '#854d0e'),
        'why_adonis':  ('🏛️', '#f0fdf4', '#15803d'),
        'routes':      ('🛣️',  '#f5f3ff', '#6d28d9'),
        'projects':    ('🏗️',  '#fff7ed', '#c2410c'),
        'process':     ('📋', '#f0f9ff', '#0369a1'),
        'trust':       ('💬', '#fdf4ff', '#7e22ce'),
        'consult':     ('📞', '#f0fdf4', '#166534'),
    }

    def section_type_badge(self, obj):
        emoji, bg, fg = self._SECTION_TYPE_COLORS.get(
            obj.section_type, ('◻️', '#f8fafc', '#334155')
        )
        label = obj.get_section_type_display()
        return format_html(
            '<span style="'
            'display:inline-block;padding:3px 10px;border-radius:999px;'
            'background:{};color:{};font-size:12px;font-weight:600;white-space:nowrap;'
            '">{} {}</span>',
            bg, fg, emoji, label,
        )
    section_type_badge.short_description = 'نوع بخش'
    section_type_badge.admin_order_field = 'section_type'

    def title_preview(self, obj):
        title = obj.title or obj.section_name or '—'
        sub = obj.subtitle or obj.description or ''
        if sub:
            sub_html = format_html(
                '<div style="color:#64748b;font-size:11px;margin-top:2px;'
                'white-space:nowrap;overflow:hidden;text-overflow:ellipsis;max-width:280px">{}</div>',
                sub[:80],
            )
            return format_html(
                '<div><div style="font-weight:600">{}</div>{}</div>',
                title[:60], sub_html,
            )
        return format_html('<span style="font-weight:600">{}</span>', title[:60])
    title_preview.short_description = 'عنوان / خلاصه'

    def section_type_display(self, obj):
        return obj.get_section_type_display()
    section_type_display.short_description = 'نوع بخش'
    section_type_display.admin_order_field = 'section_type'

    def device_visibility(self, obj):
        if obj.show_on_desktop and obj.show_on_mobile:
            return format_html('<span style="color:#16a34a;font-size:12px">🖥️📱 همه</span>')
        if obj.show_on_desktop:
            return format_html('<span style="color:#2563eb;font-size:12px">🖥️ دسکتاپ</span>')
        if obj.show_on_mobile:
            return format_html('<span style="color:#d97706;font-size:12px">📱 موبایل</span>')
        return format_html('<span style="color:#dc2626;font-size:12px">⛔ پنهان</span>')
    device_visibility.short_description = 'نمایش'

    def item_count(self, obj):
        if obj.section_type == 'gateway':
            count = obj.gateway_cards.filter(is_active=True).count()
            return format_html(
                '<span style="font-weight:700;color:#2563eb">{}</span> کارت فعال',
                count,
            )
        count = obj.items.count()
        if count == 0:
            return format_html('<span style="color:#94a3b8">۰ آیتم</span>')
        return format_html(
            '<span style="font-weight:700;color:#0369a1">{}</span> آیتم',
            count,
        )
    item_count.short_description = 'آیتم‌ها'

    def preview_button(self, obj):
        if not obj or not obj.pk:
            return 'بعد از ذخیره، لینک پیش‌نمایش فعال می‌شود.'
        url = obj.admin_preview_url
        anchor = obj.anchor_id or f'fa-section-{obj.section_type}'
        return format_html(
            '<a class="button" href="{}#{}" target="_blank" rel="noopener" '
            'style="display:inline-flex;align-items:center;gap:6px">'
            '👁 پیش‌نمایش زنده</a>',
            url, anchor,
        )
    preview_button.short_description = 'پیش‌نمایش'

    def admin_small_preview(self, obj):
        if not obj.pk:
            return 'بعد از ذخیره، پیش‌نمایش اینجا نمایش داده می‌شود.'
        title = obj.title or obj.section_name or obj.get_section_type_display()
        subtitle = obj.subtitle or obj.description or ''
        style = obj.section_inline_style
        return format_html(
            '<div class="fa-section-admin-preview" style="{}">'
            '<div class="fa-section-admin-preview-eyebrow">{}</div>'
            '<div class="fa-section-admin-preview-title">{}</div>'
            '<div class="fa-section-admin-preview-subtitle">{}</div>'
            '</div>',
            style,
            obj.eyebrow or obj.get_section_type_display(),
            title,
            subtitle[:200],
        )
    admin_small_preview.short_description = 'پیش‌نمایش کوچک'

    # ── queryset + inlines ────────────────────────────────────────────────────

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('items', 'gateway_cards')

    def get_inlines(self, request, obj):
        if obj is None:
            return []
        if obj.section_type == 'gateway':
            return [FaNewGatewayCardInline]
        if obj.section_type == 'residency_types':
            return [FaNewResidencyTypeInline]
        return [FaNewSectionItemInline]

    # ── context-sensitive fieldsets ───────────────────────────────────────────

    def get_fieldsets(self, request, obj=None):
        """
        Hide fieldsets that are irrelevant for the current section_type.
        """
        all_fs = list(super().get_fieldsets(request, obj))
        if obj is None:
            return all_fs
        st = obj.section_type
        # Remove gateway legacy cards fieldset for non-gateway sections
        if st != 'gateway':
            all_fs = [
                fs for fs in all_fs
                if 'card_1_label' not in fs[1].get('fields', ())
                and not any(
                    isinstance(f, (list, tuple)) and 'card_1_label' in f
                    for f in fs[1].get('fields', ())
                )
            ]
        # Remove decorative fieldset for non-gateway sections
        if st != 'gateway':
            all_fs = [
                fs for fs in all_fs
                if 'decorative_flowers_enabled' not in fs[1].get('fields', ())
                and not any(
                    isinstance(f, (list, tuple)) and 'decorative_flowers_enabled' in f
                    for f in fs[1].get('fields', ())
                )
            ]
        # Swap the images fieldset to the per-type field set so each section
        # type shows only the image fields it actually uses — this is what
        # surfaces «شفافیت تصویر» (background_image_opacity) for why_greece.
        type_img_fields = _FA_SECTION_TYPE_IMAGES_FIELDS.get(st)
        if type_img_fields:
            rebuilt = []
            for name, opts in all_fs:
                if name == '۳ · تصاویر و ویدیو':
                    opts = {**opts, 'fields': type_img_fields}
                rebuilt.append((name, opts))
            all_fs = rebuilt
        # Residency cards manage images per-item (not in section images fieldset).
        # Also hide the legacy 2-card fieldset for residency_types.
        # But keep background image for the section itself.
        if st == 'residency_types':
            all_fs = [
                fs for fs in all_fs 
                if fs[0] != '۴ · کارت‌های دو‌تایی (gateway — نسخه قدیمی)'
            ]
            # Customize images fieldset for residency_types - only bg image + opacity
            rebuilt = []
            for name, opts in all_fs:
                if name == '۳ · تصاویر و ویدیو':
                    opts = {
                        **opts,
                        'description': 'تصویر پس‌زمینه سکشن (اختیاری) — با اپاسیتی تیره روی سایت نمایش داده می‌شود.',
                        'fields': (
                            ('background_image', 'background_image_alt'),
                            ('background_image_opacity', 'background_image_position'),
                        ),
                    }
                rebuilt.append((name, opts))
            all_fs = rebuilt
        return all_fs

    # ── helpful change-form messages per section type ─────────────────────────

    def render_change_form(self, request, context, *args, **kwargs):
        _inject_persian_quick_nav(context)
        obj = context.get('original')
        if obj:
            hint = _FA_SECTION_HINTS.get(obj.section_type)
            if hint:
                level_name, text = hint
                level_map = {
                    'success': messages.SUCCESS,
                    'warning': messages.WARNING,
                    'info': messages.INFO,
                    'error': messages.ERROR,
                }
                messages.add_message(request, level_map.get(level_name, messages.INFO), text)
        return super().render_change_form(request, context, *args, **kwargs)

    # ── reorder drag & drop endpoint ──────────────────────────────────────────

    def get_urls(self):
        urls = super().get_urls()
        custom_urls = [
            path(
                'reorder/',
                self.admin_site.admin_view(self.reorder_view),
                name='core_fanewsection_reorder',
            )
        ]
        return custom_urls + urls

    def reorder_view(self, request):
        if request.method != 'POST':
            return JsonResponse({'ok': False, 'error': 'Method not allowed'}, status=405)
        try:
            payload = json.loads(request.body.decode('utf-8'))
            ids = payload.get('ids', [])
            if not isinstance(ids, list):
                raise ValueError('ids must be list')
            ids = [int(pk) for pk in ids]
        except Exception:
            return JsonResponse({'ok': False, 'error': 'Invalid payload'}, status=400)

        existing = list(
            FaNewSection.objects.filter(pk__in=ids).values_list('pk', flat=True)
        )
        if len(existing) != len(ids):
            return JsonResponse({'ok': False, 'error': 'Some sections were not found'}, status=400)

        with transaction.atomic():
            for index, section_id in enumerate(ids, start=1):
                FaNewSection.objects.filter(pk=section_id).update(order=index)

        return JsonResponse({'ok': True})

    class Media:
        css = {'all': ('admin/css/fa-admin-ui.css', 'admin/css/fanew_section_admin.css')}
        js = ('admin/js/fanew_section_sort.js', 'admin/js/fa-admin-enhancer.js')


# ── /fa-new/ Navigation Menu ──────────────────────────────────────────────────

class FaNavMenuChildInline(TabularInline):
    """Inline for submenu items shown inside a parent menu item."""
    model = FaNavMenuItem
    fk_name = 'parent'
    extra = 1
    fields = ('order', 'label', 'url', 'is_active', 'open_in_new_tab')
    ordering = ('order',)
    verbose_name = 'زیرمنو'
    verbose_name_plural = 'زیرمنوها'


@admin.register(FaNavMenuItem)
class FaNavMenuItemAdmin(admin.ModelAdmin):
    change_form_template = 'admin/core/fanavmenuitem/change_form.html'
    change_list_template = 'admin/core/fanavmenuitem/change_list.html'

    class Media:
        # Persian RTL + Estedad styling for the menu admin (the custom
        # templates wrap content in .fa-admin-content; this stylesheet also
        # carries the Unfold #content-main RTL rules). Not loaded globally on
        # the main /admin/, only on the menu screens.
        css = {'all': ('css/persian-admin.css',)}

    list_display = ('order', 'label', 'url', 'parent', 'is_active', 'open_in_new_tab', 'children_count', 'edit_button')
    list_display_links = ('label',)
    list_editable = ('order', 'is_active')
    list_filter = ('is_active', 'parent')
    ordering = ('parent__order', 'order')
    inlines = [FaNavMenuChildInline]
    fieldsets = (
        ('آیتم منو', {
            'description': 'اگر این آیتم زیرمنوی یک آیتم دیگر است، فیلد «زیرمنوی» را پر کنید.',
            'fields': ('parent', 'label', 'url', 'order'),
        }),
        ('تنظیمات نمایش', {
            'fields': ('is_active', 'open_in_new_tab'),
        }),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).select_related('parent')

    def children_count(self, obj):
        count = obj.children.count()
        return f'{count} زیرمنو' if count else '—'
    children_count.short_description = 'زیرمنوها'

    def edit_button(self, obj):
        return format_html(
            '<div style="display:flex;gap:8px;align-items:center;">'
            '<a href="/fa-admin/core/fanavmenuitem/{}/change/" '
            'style="background:linear-gradient(135deg,#10b981,#34d399);color:#fff;'
            'padding:6px 14px;border-radius:6px;text-decoration:none;font-weight:600;'
            'font-size:12px;display:inline-flex;align-items:center;gap:4px;'
            'box-shadow:0 2px 6px rgba(16,185,129,0.3);transition:all 0.2s">'
            '✏️ ویرایش</a>'
            '<button type="button" onclick="confirmDelete({}, \'{}\')" '
            'style="background:linear-gradient(135deg,#ef4444,#f87171);color:#fff;'
            'padding:6px 14px;border-radius:6px;border:none;font-weight:600;'
            'font-size:12px;display:inline-flex;align-items:center;gap:4px;'
            'box-shadow:0 2px 6px rgba(239,68,68,0.3);cursor:pointer;transition:all 0.2s">'
            '🗑️ حذف</button>'
            '</div>',
            obj.pk, obj.pk, obj.label,
        )
    edit_button.short_description = 'عملیات'
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete menu items."""
        return request.user.is_superuser

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['title'] = 'منوی ناوبری صفحه فارسی'
        return super().changelist_view(request, extra_context=extra_context)


# Also register FaNavMenuItem on the Persian admin site
persian_admin_site.register(FaNavMenuItem, FaNavMenuItemAdmin)


# ── /fa-new/ Footer Settings ──────────────────────────────────────────────────

@admin.register(FaFooterSettings)
class FaFooterSettingsAdmin(ModelAdmin):
    list_display = ('__str__', 'brand_name', 'phone', 'email', 'updated_at')
    readonly_fields = ('updated_at',)

    fieldsets = (
        ('ستون برند', {
            'description': 'اطلاعات برند که در سمت راست فوتر نمایش داده می‌شوند.',
            'fields': ('brand_name', 'brand_tagline', 'footer_logo', 'logo_max_width'),
        }),
        ('📍 دفتر تهران', {
            'description': 'نشانی و تلفن دفتر تهران (در فوتر نمایش داده می‌شود).',
            'fields': ('tehran_address', 'tehran_phone'),
        }),
        ('📍 دفتر آتن', {
            'description': 'نشانی و تلفن دفتر آتن.',
            'fields': ('athens_address', 'athens_phone'),
        }),
        ('ستون تماس (عمومی)', {
            'description': 'ایمیل و عنوان ستون تماس.',
            'fields': ('contact_title', 'email'),
        }),
        ('ستون لینک‌های سریع', {
            'description': 'عنوان ستون لینک‌ها. لینک‌ها به‌صورت خودکار از منوی ناوبری/بخش‌های فعال صفحه گرفته می‌شوند.',
            'fields': ('links_title',),
        }),
        ('🎨 شبکه‌های اجتماعی (آیکون‌های رنگی)', {
            'description': 'فقط لینک‌هایی که پر کنید در فوتر با آیکون رنگی نمایش داده می‌شوند.',
            'fields': ('whatsapp_url', 'telegram_url', 'youtube_url', 'x_url', 'facebook_url', 'instagram_url', 'linkedin_url'),
        }),
        ('نوار پایین', {
            'fields': ('copyright_text', 'footer_tag'),
        }),
        ('سیستم', {
            'classes': ('collapse',),
            'fields': ('updated_at',),
        }),
    )

    def has_add_permission(self, request):
        return not FaFooterSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        from django.urls import reverse
        from django.shortcuts import redirect
        obj = FaFooterSettings.get_settings()
        return redirect(reverse('admin:core_fafootersettings_change', args=[obj.pk]))


# ══════════════════════════════════════════════════════════════════════════════
# Register core models on the Persian Admin Site (/fa-admin/)
# ══════════════════════════════════════════════════════════════════════════════
try:
    persian_admin_site.register(FaNewSettings, FaNewSettingsAdmin)
except admin.sites.AlreadyRegistered:
    pass

try:
    persian_admin_site.register(FaNewSection, FaNewSectionAdmin)
except admin.sites.AlreadyRegistered:
    pass

try:
    persian_admin_site.register(FaFooterSettings, FaFooterSettingsAdmin)
except admin.sites.AlreadyRegistered:
    pass

try:
    persian_admin_site.register(FaNewFeaturedProperties, FaNewFeaturedPropertiesAdmin)
except admin.sites.AlreadyRegistered:
    pass


# Professional User admin (single-form create with password + access level).
from core import admin_users  # noqa: E402,F401
