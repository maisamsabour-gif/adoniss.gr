import re
import bleach
from django.conf import settings as django_settings
from django.contrib import admin
from django import forms
from django.db import models
from django.utils.html import format_html, strip_tags
from django_ckeditor_5.widgets import CKEditor5Widget
from .models import Amenity, AmenityCategory, Property, PropertyCategory, PropertyMedia, PropertyInterest, PropertyUnit, UnitBooking
from core.admin_base import ModelAdmin, TabularInline, StackedInline, TranslationAdmin
from core.admin_mixins import AuditAdminMixin, RoleProtectedAdminMixin, SoftDeleteAdminMixin
from core.admin_openai import make_translate_actions
from core.admin_seo import BaseSEOAdmin
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
    can_view_full_phone,
    mask_phone_number,
)


if 'delete_selected' in admin.site._actions:
    admin.site.disable_action('delete_selected')


class TimelineWidget(forms.RadioSelect):
    """Custom widget for timeline stages with visual buttons"""
    template_name = 'admin/widgets/timeline_widget.html'
    
    def __init__(self, attrs=None):
        super().__init__(attrs)
        self.choices = Property.TIMELINE_CHOICES

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        return context


ALLOWED_HTML_TAGS = ['p', 'b', 'strong', 'i', 'em', 'ul', 'ol', 'li', 'br', 'a']
ALLOWED_HTML_ATTRS = {'a': ['href', 'title', 'target']}


# ── Amenity grouped-checkbox widget ────────────────────────────────────────────

class GroupedAmenityCheckboxWidget(forms.Widget):
    """
    Renders amenity checkboxes grouped under their category heading.
    Displayed as 3 columns of checkboxes in the admin.
    """

    def __init__(self, attrs=None):
        super().__init__(attrs)

    def render(self, name, value, attrs=None, renderer=None):
        from django.utils.html import escape, format_html
        from django.utils.safestring import mark_safe

        if value is None:
            value = []
        selected_ids = set(int(v) for v in value if v)

        categories = (
            AmenityCategory.objects
            .filter(is_active=True)
            .prefetch_related(
                models.Prefetch(
                    'amenities',
                    queryset=Amenity.objects.filter(is_active=True).order_by('display_order', 'name'),
                )
            )
            .order_by('display_order', 'name')
        )

        html_parts = ['<div class="amenity-group-wrapper">']
        for cat in categories:
            amenities = list(cat.amenities.all())
            if not amenities:
                continue
            html_parts.append(
                f'<div class="amenity-group">'
                f'<h4 class="amenity-cat-title">{escape(cat.name)}</h4>'
                f'<ul class="amenity-list">'
            )
            for amenity in amenities:
                checked = 'checked' if amenity.pk in selected_ids else ''
                html_parts.append(
                    f'<li>'
                    f'<label class="amenity-label">'
                    f'<input type="checkbox" name="{escape(name)}" value="{amenity.pk}" {checked}> '
                    f'{escape(amenity.name)}'
                    f'</label>'
                    f'</li>'
                )
            html_parts.append('</ul></div>')

        html_parts.append('</div>')
        return mark_safe(''.join(html_parts))

    def value_from_datadict(self, data, files, name):
        return data.getlist(name)


class GroupedAmenityField(forms.ModelMultipleChoiceField):
    widget = GroupedAmenityCheckboxWidget

    def __init__(self, *args, **kwargs):
        kwargs.setdefault('queryset', Amenity.objects.filter(is_active=True))
        kwargs.setdefault('required', False)
        super().__init__(*args, **kwargs)


# ── Amenity Category & Amenity admin ──────────────────────────────────────────

@admin.register(AmenityCategory)
class AmenityCategoryAdmin(RoleProtectedAdminMixin, ModelAdmin):
    allowed_roles = {ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_CONTENT_ADMIN, ROLE_CONTENT_MANAGER, ROLE_PROPERTY_BLOG_EDITOR}
    list_display = ['name', 'slug', 'display_order', 'is_active']
    list_editable = ['display_order', 'is_active']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['display_order', 'name']


@admin.register(Amenity)
class AmenityAdmin(RoleProtectedAdminMixin, ModelAdmin):
    allowed_roles = {ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_CONTENT_ADMIN, ROLE_CONTENT_MANAGER, ROLE_PROPERTY_BLOG_EDITOR}
    list_display = ['name', 'category', 'slug', 'display_order', 'is_active']
    list_editable = ['display_order', 'is_active']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['category__display_order', 'display_order', 'name']


class PropertyAdminForm(forms.ModelForm):
    """
    Property admin form.

    Widgets for the description/tagline fields are applied per language in
    PropertyAdmin.get_form() because modeltranslation generates per-language
    field names (description_en, description_tr, etc.) at runtime.
    """

    amenities = GroupedAmenityField()

    class Meta:
        model = Property
        fields = '__all__'
        widgets = {
            'timeline_stage': TimelineWidget(),
            'address_private': forms.TextInput(attrs={
                'id': 'id_address_private',
                'autocomplete': 'off',
                'placeholder': 'Start typing street or postal code — then pick from the dropdown…',
                'style': 'width:100%; max-width:620px;',
                'class': 'vTextField property-places-input',
            }),
        }

    # ── Helpers ──────────────────────────────────────────────────────────────

    @staticmethod
    def _clean_tagline_value(value: str) -> str:
        if value:
            value = strip_tags(value)
            value = re.sub(r'\s+', ' ', value).strip()
        return value

    @staticmethod
    def _clean_description_value(value: str) -> str:
        if value:
            value = bleach.clean(
                value,
                tags=ALLOWED_HTML_TAGS,
                attributes=ALLOWED_HTML_ATTRS,
                strip=True,
            )
        return value

    # ── Per-language clean methods ────────────────────────────────────────────

    def clean_tagline_en(self):
        return self._clean_tagline_value(self.cleaned_data.get('tagline_en', ''))

    def clean_tagline_tr(self):
        return self._clean_tagline_value(self.cleaned_data.get('tagline_tr', ''))

    def clean_description_en(self):
        return self._clean_description_value(self.cleaned_data.get('description_en', ''))

    def clean_description_tr(self):
        return self._clean_description_value(self.cleaned_data.get('description_tr', ''))

    def clean(self):
        cleaned = super().clean()
        return cleaned

class PropertyUnitInline(StackedInline):
    model = PropertyUnit
    extra = 1
    can_delete = False
    fields = [
        ('unit_label', 'availability'),
        ('size_sqm', 'bedrooms', 'bathrooms'),
        ('parking', 'price', 'order'),
    ]
    ordering = ['order', 'unit_label']

    class Media:
        css = {'all': ['css/admin-utils.css']}


class PropertyMediaFormset(forms.BaseInlineFormSet):
    """Enforce a maximum of 20 media items per property."""

    def clean(self):
        super().clean()
        count = sum(
            1 for form in self.forms
            if form.cleaned_data
            and not form.cleaned_data.get('DELETE', False)
            and (form.cleaned_data.get('image') or form.cleaned_data.get('video'))
        )
        if count > 20:
            raise forms.ValidationError(
                f'A property can have at most 20 media items. You submitted {count}.'
            )


class PropertyMediaInline(TabularInline):
    model = PropertyMedia
    formset = PropertyMediaFormset
    extra = 5
    max_num = 20
    readonly_fields = ['thumb']
    fields = [
        'thumb', 'order', 'is_cover',
        'image', 'video', 'poster',
        'caption_en', 'caption_tr',
        'is_decorative',
    ]
    verbose_name = 'Photo / Video'
    verbose_name_plural = (
        'Photos & Videos — upload, reorder, and set ALT text for each image'
    )
    ordering = ['order']

    # Per-field help text shown inline under each column header
    # (Django TabularInline inherits help_text from the model field automatically,
    #  but we can tighten the column labels here for clarity)
    def get_fields(self, request, obj=None):
        return super().get_fields(request, obj)

    @admin.display(description='Preview')
    def thumb(self, obj):
        if obj.pk and obj.image:
            return format_html(
                '<a href="{0}" target="_blank" class="admin-thumb-link">'
                '<img src="{0}" class="admin-thumb" /></a>',
                obj.image.url,
            )
        if obj.pk and obj.video:
            return format_html('<span class="admin-thumb-video">▶</span>')
        return '—'


@admin.register(PropertyCategory)
class PropertyCategoryAdmin(RoleProtectedAdminMixin, ModelAdmin):
    allowed_roles = {ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_CONTENT, ROLE_CONTENT_ADMIN, ROLE_CONTENT_MANAGER, ROLE_PROPERTY_BLOG_EDITOR}
    list_display = ['name', 'price_label', 'order', 'is_active']
    list_editable = ['order', 'is_active']


# Field pairs for the OpenAI auto-translate action
_PROPERTY_FIELD_PAIRS = [
    ('name_en', 'name_tr'),
    ('tagline_en', 'tagline_tr'),
    ('description_en', 'description_tr'),
    ('location_en', 'location_tr'),
    ('neighborhood_description_en', 'neighborhood_description_tr'),
    ('feature_1_en', 'feature_1_tr'),
    ('feature_2_en', 'feature_2_tr'),
    ('feature_3_en', 'feature_3_tr'),
    ('feature_4_en', 'feature_4_tr'),
    ('area_highlight_1_en', 'area_highlight_1_tr'),
    ('area_highlight_2_en', 'area_highlight_2_tr'),
    ('area_highlight_3_en', 'area_highlight_3_tr'),
    ('area_highlight_4_en', 'area_highlight_4_tr'),
    ('area_highlight_5_en', 'area_highlight_5_tr'),
    ('area_highlight_6_en', 'area_highlight_6_tr'),
]


@admin.register(Property)
class PropertyAdmin(BaseSEOAdmin, RoleProtectedAdminMixin, AuditAdminMixin, SoftDeleteAdminMixin, TranslationAdmin):
    change_form_template = 'admin/properties/property/change_form.html'
    allowed_roles = {ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_SALES, ROLE_CONTENT, ROLE_CONTENT_ADMIN, ROLE_CONTENT_MANAGER, ROLE_PROPERTY_BLOG_EDITOR, ROLE_PROPERTY_BLOG_MGR}
    form = PropertyAdminForm
    actions = make_translate_actions(_PROPERTY_FIELD_PAIRS) + [
        'regenerate_public_location',
        'hide_from_site',
        'show_on_site',
    ]
    list_display = [
        'thumbnail',
        'name',
        'display_order',
        'category',
        'price_label',
        'status',
        'show_on_homepage',
        'is_featured',
        'is_special_offer',
        'visibility_badge',
        'deleted_at',
        'edit_link',
    ]
    list_display_links = ['name']
    list_filter = ['deleted_at', 'status', 'timeline_stage', 'show_on_homepage', 'is_featured',
                   'is_special_offer', 'is_active', 'category', 'golden_visa_eligible']
    search_fields = ['name', 'description', 'location', 'area', 'neighborhood_public', 'city']
    list_editable = ['display_order', 'show_on_homepage', 'is_featured', 'is_special_offer', 'status']
    prepopulated_fields = {'slug': ('name',)}
    ordering = ['display_order', '-is_featured', '-created_at']
    inlines = [PropertyUnitInline]

    class Media:
        css = {'all': [
            'admin/css/timeline_widget.css',
            'css/admin-richtext.css',
            'css/admin-unfold.css',
            'admin/css/admin-polish.css',
            'admin/css/amenity_widget.css',
            'admin/css/seo_preview.css',
        ]}
        js = ['js/admin-richtext.js', 'admin/js/seo_preview.js']

    # ── Visibility toggle (one-click hide/show) ──────────────────────────────

    def get_urls(self):
        from django.urls import path as dj_path
        return [
            dj_path(
                '<int:pk>/toggle-active/',
                self.admin_site.admin_view(self.toggle_active_view),
                name='properties_property_toggle_active',
            ),
        ] + super().get_urls()

    def toggle_active_view(self, request, pk):
        from django.contrib import messages as msg_mod
        from django.http import HttpResponseRedirect
        from django.shortcuts import get_object_or_404
        obj = get_object_or_404(Property, pk=pk)
        obj.is_active = not obj.is_active
        obj.save(update_fields=['is_active'])
        state = 'shown on site ✅' if obj.is_active else 'hidden from site 🚫'
        self.message_user(request, f'"{obj.name}" is now {state}.', msg_mod.SUCCESS)
        referer = request.META.get('HTTP_REFERER', '')
        from django.urls import reverse
        return HttpResponseRedirect(referer or reverse('admin:properties_property_changelist'))

    @admin.display(description='Visibility', ordering='is_active')
    def visibility_badge(self, obj):
        from django.urls import reverse
        url = reverse('admin:properties_property_toggle_active', args=[obj.pk])
        if obj.is_active:
            return format_html(
                '<a href="{}" title="Click to hide from site" '
                'onclick="return confirm(\'Hide "{}" from the website?\')" '
                'style="display:inline-flex;align-items:center;gap:5px;padding:3px 10px;'
                'border-radius:20px;font-size:.75rem;font-weight:600;text-decoration:none;'
                'background:#dcfce7;color:#166534;border:1px solid #bbf7d0;">'
                '● Visible</a>',
                url, obj.name,
            )
        return format_html(
            '<a href="{}" title="Click to show on site" '
            'onclick="return confirm(\'Show "{}" on the website?\')" '
            'style="display:inline-flex;align-items:center;gap:5px;padding:3px 10px;'
            'border-radius:20px;font-size:.75rem;font-weight:600;text-decoration:none;'
            'background:#fee2e2;color:#991b1b;border:1px solid #fecaca;">'
            '○ Hidden</a>',
            url, obj.name,
        )

    @admin.action(description='🚫 Hide from website')
    def hide_from_site(self, request, queryset):
        from django.contrib import messages as msg_mod
        count = queryset.update(is_active=False)
        self.message_user(
            request,
            f'{count} propert{"y" if count == 1 else "ies"} hidden from the website.',
            msg_mod.SUCCESS,
        )

    @admin.action(description='✅ Show on website')
    def show_on_site(self, request, queryset):
        from django.contrib import messages as msg_mod
        count = queryset.update(is_active=True)
        self.message_user(
            request,
            f'{count} propert{"y" if count == 1 else "ies"} are now visible on the website.',
            msg_mod.SUCCESS,
        )

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        """Inject Google Maps API key (and saved coordinates) into the change-form context."""
        extra_context = extra_context or {}
        key = (django_settings.GOOGLE_MAPS_API_KEY or '').strip()
        extra_context['google_maps_api_key'] = key

        # Pass saved private/public coords so the admin template can pre-load the map
        if object_id:
            try:
                obj = self.get_object(request, object_id)
                if obj:
                    extra_context['saved_lat_private'] = obj.lat_private or ''
                    extra_context['saved_lng_private'] = obj.lng_private or ''
                    extra_context['saved_lat_public']  = obj.lat_public  or ''
                    extra_context['saved_lng_public']  = obj.lng_public  or ''
                    extra_context['saved_address']     = obj.address_private or ''
            except Exception:
                pass
        return super().changeform_view(request, object_id, form_url, extra_context)

    def get_form(self, request, obj=None, **kwargs):
        """Apply CKEditor widget to all translated description fields."""
        FormClass = super().get_form(request, obj, **kwargs)
        tagline_widget = forms.TextInput(attrs={
            'style': 'width: 100%; max-width: 600px;',
            'placeholder': 'Plain text only - no HTML allowed',
        })
        nbhd_widget = forms.Textarea(attrs={
            'rows': 6,
            'style': 'width: 100%; min-height: 150px;',
        })
        for lang_code, _lang_name in django_settings.LANGUAGES:
            for field_name, widget in [
                (f'description_{lang_code}', CKEditor5Widget(config_name='blog', attrs={'class': 'django_ckeditor_5'})),
                (f'tagline_{lang_code}', tagline_widget),
                (f'neighborhood_description_{lang_code}', nbhd_widget),
            ]:
                if field_name in FormClass.base_fields:
                    FormClass.base_fields[field_name].widget = widget
        return FormClass

    # ── List-display helpers ─────────────────────────────────────────────────

    @admin.display(description='Photo')
    def thumbnail(self, obj):
        img = obj.main_image
        if img:
            return format_html(
                '<a href="{0}" target="_blank" class="admin-thumb-link">'
                '<img src="{0}" class="admin-thumb" /></a>',
                img.url,
            )
        return '—'

    @admin.display(description='Action')
    def edit_link(self, obj):
        from django.urls import reverse
        url = reverse('admin:properties_property_change', args=[obj.pk])
        return format_html(
            '<a href="{}" style="background:#0d9488;color:#fff;padding:5px 14px;border-radius:6px;'
            'text-decoration:none;font-size:12px;font-weight:600;">Edit</a>',
            url,
        )

    def interest_count(self, obj):
        count = obj.interests.count()
        unread = obj.interests.filter(is_read=False).count()
        if unread:
            return f'{count} ({unread} new)'
        return str(count)
    interest_count.short_description = 'Interests'

    # ── Fieldsets ─────────────────────────────────────────────────────────────

    fieldsets = (
        # ── General ─────────────────────────────────────────────────────────
        ('📋 General', {
            'classes': ('tab',),
            'fields': (
                'name', 'slug', 'category', 'tagline', 'description',
                ('floors', 'units'), ('bedrooms', 'size_sqm'),
                'feature_1', 'feature_2', 'feature_3', 'feature_4',
            ),
            'description': 'Core property information, physical details, and feature badges.',
        }),

        # ── Location ────────────────────────────────────────────────────────
        ('📍 Location', {
            'classes': ('tab',),
            'fields': (
                ('location_en', 'location_tr'),
                ('area_en', 'area_tr'),
                ('neighborhood_public_en', 'neighborhood_public_tr'),
                'city',
                'neighborhood_image', 'neighborhood_description',
                ('distance_to_sea', 'distance_to_metro', 'nearest_metro_station'),
                ('distance_to_center', 'distance_to_acropolis', 'distance_to_airport'),
                ('area_highlight_1', 'area_highlight_2', 'area_highlight_3'),
                ('area_highlight_4', 'area_highlight_5', 'area_highlight_6'),
            ),
            'description': (
                '<b>These fields are shown publicly</b> — never put a street address.<br>'
                '<b>Location</b>: general area (e.g. "South Athens"). '
                '<b>District/Area</b>: e.g. "Alimos", "Glyfada". '
                '<b>City</b>: e.g. "Athens".'
            ),
        }),

        # ── Pricing & Status ────────────────────────────────────────────────
        ('💰 Pricing & Status', {
            'classes': ('tab',),
            'fields': (
                'price', 'price_label',
                'price_tier', 'golden_visa_eligible',
                'status', 'delivery_date',
                'timeline_stage',
            ),
            'description': 'Pricing, Golden Visa eligibility, availability, and construction timeline.',
        }),

        # ── Amenities ───────────────────────────────────────────────────────
        ('🏠 Amenities', {
            'classes': ('tab',),
            'fields': ('amenities',),
            'description': 'Tick the amenities that apply to this property.',
        }),

        # ── Direct Photo Slots ───────────────────────────────────────────────
        ('🖼️ Photos', {
            'classes': ('tab',),
            'fields': (
                'cover_image_slot',
                ('image_1',  'image_2',  'image_3'),
                ('image_4',  'image_5',  'image_6'),
                ('image_7',  'image_8',  'image_9'),
                ('image_10', 'image_11', 'image_12'),
                ('image_13', 'image_14', 'image_15'),
            ),
            'description': (
                'Upload up to 15 photos directly on the property. '
                'iPhone HEIC photos are automatically converted to JPEG — no extra steps needed. '
                'These photos appear in the property gallery alongside any items added in the Media section below. '
                'Leave unused slots blank.<br>'
                '<b>Cover photo:</b> pick which slot becomes the card image shown on the homepage and properties list. '
                'Leave it as <em>"Auto"</em> to use the first available photo.'
            ),
        }),

        # ── Videos ──────────────────────────────────────────────────────────
        ('🎬 Videos', {
            'classes': ('tab',),
            'fields': (
                'video_1', 'video_1_poster',
                'video_2', 'video_2_poster',
            ),
            'description': (
                'Upload up to 2 videos (MP4 recommended, max 500 MB each). '
                'They will be displayed in a player below the photo gallery on the property page. '
                'The poster image (optional) is shown as a thumbnail before the video plays.'
            ),
        }),

        # ── Settings ────────────────────────────────────────────────────────
        ('⚙️ Settings', {
            'classes': ('tab',),
            'fields': (
                ('display_order', 'show_on_homepage'),
                ('is_featured', 'is_special_offer', 'is_active'),
                'whatsapp_message',
                ('public_radius_m', 'location_privacy_mode'),
                'address_private',
                ('postal_code', 'google_place_id'),
                ('lat_private', 'lng_private'),
                ('lat_public', 'lng_public'),
            ),
            'description': (
                'Visibility, WhatsApp message, map circle, and private address.<br>'
                '<b>⚠ Private address is NEVER displayed on the website.</b>'
            ),
        }),

        # ── SEO ─────────────────────────────────────────────────────────────
        ('🔍 SEO', {
            'classes': ('tab',),
            'fields': (
                'seo_title', 'meta_description', 'focus_keyword', 'canonical_url', 'og_image',
                'robots_index', 'robots_follow', 'seo_allow_publish_override',
            ),
            'description': (
                'Google Preview updates live below as you type.<br>'
                '<em>SEO Title</em>: max 70 chars.<br>'
                '<em>Meta Description</em>: max 160 chars.<br>'
                '<em>Focus Keyword</em>: the main keyword this property page targets.'
            ),
        }),
    )

    # Private address fields — only visible to superadmins / staff with full access
    _SUPERADMIN_MAP_FIELDS = {
        'address_private', 'postal_code', 'google_place_id',
        'lat_private', 'lng_private',
    }

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if request.user.is_superuser:
            return fieldsets
        # Remove private address / raw coords for non-superusers
        cleaned = []
        for title, options in fieldsets:
            fields = options.get('fields', ())
            new_fields = []
            for field in fields:
                if isinstance(field, (list, tuple)):
                    filtered = tuple(f for f in field if f not in self._SUPERADMIN_MAP_FIELDS)
                    if filtered:
                        new_fields.append(filtered if len(filtered) > 1 else filtered[0])
                elif field not in self._SUPERADMIN_MAP_FIELDS:
                    new_fields.append(field)
            cleaned.append((title, {**options, 'fields': tuple(new_fields)}))
        return cleaned

    def get_readonly_fields(self, request, obj=None):
        ro = list(super().get_readonly_fields(request, obj))
        # Geocoded private coords, place_id, and public coords are always read-only
        # (they are written by Google Places JS → hidden inputs → save_model, not by hand)
        for f in ('lat_private', 'lng_private', 'google_place_id', 'lat_public', 'lng_public'):
            if f not in ro:
                ro.append(f)
        return ro

    def save_model(self, request, obj, form, change):
        """
        1. Reads Google Places data from the hidden form inputs written by the
           admin JS (_places_lat, _places_lng, _places_place_id, _places_postal).
        2. Surfaces admin-visible warnings when coordinates are missing.
        """
        from django.contrib import messages as admin_messages

        def _post(name):
            return request.POST.get(name, '').strip()

        places_lat  = _post('_places_lat')
        places_lng  = _post('_places_lng')
        place_id    = _post('_places_place_id')
        places_post = _post('_places_postal')

        # ── Apply Places data when a Google suggestion was selected ──
        if places_lat and places_lng:
            try:
                obj.lat_private = round(float(places_lat), 6)
                obj.lng_private = round(float(places_lng), 6)
                obj._coords_injected_by_places = True
            except (ValueError, TypeError):
                pass

        if place_id:
            obj.google_place_id = place_id

        if places_post and not obj.postal_code:
            obj.postal_code = places_post

        super().save_model(request, obj, form, change)

        # ── Post-save warnings ────────────────────────────────────────
        has_coords = obj.lat_private and obj.lng_private
        has_pub    = obj.lat_public  and obj.lng_public

        if obj.is_active and obj.address_private and not has_coords:
            admin_messages.warning(
                request,
                "⚠ This property is published but has NO private coordinates. "
                "The map circle will NOT appear on the property page. "
                "To fix: open the '🔒 Private Address' section, re-type the address "
                "in the field, and SELECT a result from the Google suggestions dropdown.",
            )
        elif has_coords and not has_pub:
            admin_messages.warning(
                request,
                "⚠ Private coordinates exist but the public (obfuscated) coordinates "
                "were not generated. Open this property again and save to trigger regeneration.",
            )
        elif has_coords and has_pub:
            admin_messages.info(
                request,
                f"📍 Location saved — private coords ({obj.lat_private}, {obj.lng_private}), "
                f"public circle at ({obj.lat_public}, {obj.lng_public}). "
                f"The map circle is ready on the property page.",
            )

    @admin.action(description='🔄 Regenerate public location (new random offset)')
    def regenerate_public_location(self, request, queryset):
        updated = 0
        for prop in queryset:
            if prop.lat_private and prop.lng_private:
                prop.regenerate_public_location()
                updated += 1
        self.message_user(
            request,
            f'Public location regenerated for {updated} propert{"y" if updated == 1 else "ies"}.',
        )


@admin.register(PropertyUnit)
class PropertyUnitAdmin(RoleProtectedAdminMixin, AuditAdminMixin, SoftDeleteAdminMixin, ModelAdmin):
    allowed_roles = {ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_SALES, ROLE_CONTENT, ROLE_CONTENT_ADMIN, ROLE_CONTENT_MANAGER, ROLE_PROPERTY_BLOG_EDITOR, ROLE_PROPERTY_BLOG_MGR}
    list_display = ['property', 'unit_label', 'availability', 'size_sqm', 'price', 'deleted_at']
    list_filter = ['deleted_at', 'availability', 'property']
    search_fields = ['property__name', 'unit_label']
    ordering = ['property', 'order', 'unit_label']


@admin.register(PropertyInterest)
class PropertyInterestAdmin(RoleProtectedAdminMixin, AuditAdminMixin, SoftDeleteAdminMixin, ModelAdmin):
    allowed_roles = {ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_SALES, ROLE_SUPPORT, ROLE_CONTENT, ROLE_PROPERTY_BLOG_MGR}
    list_display = ['property', 'full_name', 'email', 'created_at', 'is_read', 'deleted_at']
    list_filter = ['deleted_at', 'is_read', 'created_at', 'property']
    search_fields = ['full_name', 'email', 'phone', 'property__name']
    list_editable = ['is_read']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'

    def get_list_display(self, request):
        base = list(super().get_list_display(request))
        phone_field = 'phone' if can_view_full_phone(request.user) else 'masked_phone'
        base.insert(3, phone_field)
        return base

    @admin.display(description='Phone')
    def masked_phone(self, obj):
        return mask_phone_number(obj.phone)


@admin.register(UnitBooking)
class UnitBookingAdmin(RoleProtectedAdminMixin, AuditAdminMixin, SoftDeleteAdminMixin, ModelAdmin):
    allowed_roles = {ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_SALES, ROLE_SUPPORT, ROLE_CONTENT}
    list_display = ['unit', 'get_property', 'full_name', 'email', 'created_at', 'is_read', 'deleted_at']
    list_filter = ['deleted_at', 'is_read', 'created_at', 'unit__property']
    search_fields = ['full_name', 'email', 'phone', 'unit__unit_label', 'unit__property__name']
    list_editable = ['is_read']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'
    
    def get_property(self, obj):
        return obj.unit.property.name
    get_property.short_description = 'Property'

    def get_list_display(self, request):
        base = list(super().get_list_display(request))
        phone_field = 'phone' if can_view_full_phone(request.user) else 'masked_phone'
        base.insert(4, phone_field)
        return base

    @admin.display(description='Phone')
    def masked_phone(self, obj):
        return mask_phone_number(obj.phone)


# ── FA SEO Content Pipeline ───────────────────────────────────────────────────
from .admin_pipeline import FaContentPipelineAdmin, ContentScheduleAdmin, EnContentPipelineAdmin  # noqa: E402, F401
