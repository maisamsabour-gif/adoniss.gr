from django.core.exceptions import ValidationError
from django.db import models
from django.db.models import Q
from django.urls import reverse
from django.utils import timezone

from core.safety import SoftDeleteModel
from core.seo_mixin import SEOContentInterface


class AmenityCategory(models.Model):
    """Groups of amenities: Internal, External, Construction, etc."""
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = 'Amenity Category'
        verbose_name_plural = 'Amenity Categories'

    def __str__(self):
        return self.name


class Amenity(models.Model):
    """A single reusable amenity (e.g. Elevator, Balcony, Parking spot)."""
    category = models.ForeignKey(
        AmenityCategory,
        on_delete=models.CASCADE,
        related_name='amenities',
    )
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(
        max_length=80, blank=True,
        help_text='Optional icon key (e.g. "elevator") for future icon sets.',
    )
    display_order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['category__display_order', 'display_order', 'name']
        verbose_name = 'Amenity'
        verbose_name_plural = 'Amenities'

    def __str__(self):
        return f'{self.category.name} › {self.name}'


class PropertyCategory(models.Model):
    """Property categories (e.g., 250K Plan, 800K Plan)"""
    name = models.CharField(max_length=100)
    price_label = models.CharField(max_length=50, help_text='e.g., €250K Plan')
    description = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ['order']
        verbose_name = 'Property Category'
        verbose_name_plural = 'Property Categories'

    def __str__(self):
        return self.name

    def delete(self, using=None, keep_parents=False):
        if self.deleted_at is not None:
            return

        archived_at = timezone.now()
        self.deleted_at = archived_at
        self.save(update_fields=['deleted_at'])

        PropertyUnit.objects.filter(property=self, deleted_at__isnull=True).update(deleted_at=archived_at)
        UnitBooking.objects.filter(unit__property=self, deleted_at__isnull=True).update(deleted_at=archived_at)
        PropertyInterest.objects.filter(property=self, deleted_at__isnull=True).update(deleted_at=archived_at)

    def hard_delete(self, using=None, keep_parents=False):
        has_bookings = UnitBooking.all_objects.filter(unit__property=self).exists()
        if has_bookings:
            raise ValidationError('Cannot permanently delete a property that has booking records. Archive it instead.')
        return super().hard_delete(using=using, keep_parents=keep_parents)


class SimpleImageItem:
    """
    Lightweight wrapper that makes a plain ImageField look like a PropertyMedia
    item so the gallery template works with both PropertyMedia objects and
    direct image slots without modification.
    """
    def __init__(self, image_field, index=0):
        self.image = image_field
        self.order = 1000 + index
        self.is_cover = False

    def get_alt(self, lang=None):
        return ''


def _property_direct_image_upload_path(instance, filename):
    """Upload path for the 15 direct image slots on the Property model."""
    import os, uuid, re
    _, ext = os.path.splitext(filename.lower())
    if ext not in ('.jpg', '.jpeg', '.png', '.webp', '.gif'):
        ext = '.jpg'  # HEIC/HEIF files are converted to JPEG before upload
    slug = (
        getattr(instance, 'slug_en', None)
        or getattr(instance, 'slug', None)
        or 'property'
    ).strip().lower()
    slug = re.sub(r'[^a-z0-9-]', '', slug)[:40].rstrip('-')
    uid = uuid.uuid4().hex[:8]
    return f'properties/gallery/{slug}-{uid}{ext}'


class Property(SEOContentInterface, SoftDeleteModel):
    """Real estate properties"""
    STATUS_CHOICES = [
        ('available', 'Still Available'),
        ('sold_out_soon', 'Sold Out Soon'),
        ('sold_out', 'Sold Out'),
    ]
    
    # Construction Timeline Stages
    TIMELINE_CHOICES = [
        ('ready_to_start', 'Ready to Start Renovation'),
        ('under_renovation', 'Under Renovation'),
        ('finishing_soon', 'Renovation Will Be Finished Soon'),
        ('ready', 'Ready to Deliver'),
    ]
    
    # Basic Info
    name = models.CharField(max_length=200)
    name_fa = models.CharField(max_length=200, blank=True, verbose_name='نام فارسی', help_text='Persian name shown on FA landing page cards')
    slug = models.SlugField(unique=True)
    category = models.ForeignKey(PropertyCategory, on_delete=models.SET_NULL, null=True, related_name='properties')
    tagline = models.CharField(max_length=200, help_text='Short description shown in card')
    tagline_fa = models.CharField(max_length=300, blank=True, verbose_name='توضیح کوتاه فارسی', help_text='Persian tagline shown on FA landing page cards')
    description = models.TextField()
    
    # Pricing
    price = models.DecimalField(max_digits=12, decimal_places=2)
    price_label = models.CharField(max_length=50, help_text='e.g., €250K Plan')
    
    # Location — PUBLIC fields, shown on the website
    location = models.CharField(
        max_length=200,
        verbose_name='Location / Area Label',
        help_text=(
            'Public-facing area description shown on the property card — e.g. "South Athens" or '
            '"Piraeus Coast". Do NOT include street numbers or exact addresses here.'
        ),
    )
    area = models.CharField(
        max_length=100, blank=True,
        verbose_name='District / Sub-area Label (Public)',
        help_text=(
            'Optional secondary area shown on the card — e.g. "Alimos" or "Glyfada". '
            'Keep it at district or neighbourhood level only; never a street address.'
        ),
    )
    
    # Property Details
    floors = models.PositiveIntegerField(default=1)
    units = models.PositiveIntegerField(default=1, help_text='Number of units')
    bedrooms = models.PositiveIntegerField(default=1)
    size_sqm = models.PositiveIntegerField(blank=True, null=True, help_text='Size in square meters')
    
    # Features (shown as badges)
    feature_1 = models.CharField(max_length=100, blank=True, help_text='e.g., 🌅 Fully Renovated')
    feature_2 = models.CharField(max_length=100, blank=True, help_text='e.g., 🏢 4 Floors')
    feature_3 = models.CharField(max_length=100, blank=True, help_text='e.g., 🛂 Delivery May 2026')
    feature_4 = models.CharField(max_length=100, blank=True, help_text='e.g., 🏡 Premium Quality')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    delivery_date = models.CharField(max_length=50, blank=True, help_text='e.g., May 2026')
    
    # Construction Timeline
    timeline_stage = models.CharField(
        max_length=20, 
        choices=TIMELINE_CHOICES, 
        default='coming_soon',
        verbose_name='Project Status',
        help_text='Current stage of construction/renovation'
    )
    
    # Golden Visa Price Tier
    PRICE_TIER_CHOICES = [
        ('250', '€250K'),
        ('400', '€400K'),
        ('800', '€800K'),
    ]
    price_tier = models.CharField(
        max_length=10,
        choices=PRICE_TIER_CHOICES,
        default='250',
        verbose_name='Price Tier (Golden Visa)',
        help_text='Select the Golden Visa price category for this property'
    )
    golden_visa_eligible = models.BooleanField(default=True)
    
    
    # Display Order & Visibility
    display_order = models.PositiveIntegerField(default=0, verbose_name='Display Order',
                                                 help_text='Lower numbers appear first (0 = top)')
    show_on_homepage = models.BooleanField(default=True, verbose_name='Show on Homepage',
                                            help_text='Display this property on the front page')
    is_featured = models.BooleanField(default=False, verbose_name='Featured Property',
                                       help_text='Highlight as a featured/special property')
    is_special_offer = models.BooleanField(default=False, verbose_name='Special Offer',
                                            help_text='Mark as a special sale/promotion')
    is_active = models.BooleanField(default=True, verbose_name='Active',
                                     help_text='Uncheck to hide from website')
    
    # WhatsApp Message
    whatsapp_message = models.CharField(max_length=300, blank=True, help_text='Custom WhatsApp message')

    # Amenities
    amenities = models.ManyToManyField(
        'Amenity',
        blank=True,
        related_name='properties',
        verbose_name='Amenities',
        help_text='Tick amenities that apply to this property. Grouped by category.',
    )

    # ===== PUBLIC LOCATION LABELS (safe to display on the website) =====
    neighborhood_public = models.CharField(
        max_length=200, blank=True,
        verbose_name='Public Neighborhood Label',
        help_text=(
            'Shown next to the map circle on the property page — e.g. "Piraeus Port" or "Glyfada Coast". '
            'Never use a street address here. Leave blank to fall back to the general Area/Location.'
        ),
    )

    # ===== LOCATION & NEIGHBORHOOD SECTION =====
    neighborhood_image = models.ImageField(upload_to='properties/neighborhood/', blank=True, 
                                           verbose_name='Neighborhood Image',
                                           help_text='Image of the area/beach/neighborhood (recommended: 800x500px)')
    neighborhood_description = models.TextField(blank=True, verbose_name='Neighborhood Description',
                                                 help_text='Describe the area, lifestyle, and attractions')
    
    # Distances
    distance_to_sea = models.CharField(max_length=50, blank=True, verbose_name='Distance to Sea/Beach',
                                       help_text='e.g., 500m, 2 min walk')
    distance_to_center = models.CharField(max_length=50, blank=True, verbose_name='Distance to Athens Center',
                                          help_text='e.g., 8 km, 15 min by car')
    distance_to_acropolis = models.CharField(max_length=50, blank=True, verbose_name='Distance to Acropolis',
                                             help_text='e.g., 10 km, 20 min by metro')
    distance_to_metro = models.CharField(max_length=50, blank=True, verbose_name='Distance to Metro Station',
                                         help_text='e.g., 300m, 4 min walk')
    nearest_metro_station = models.CharField(max_length=100, blank=True, verbose_name='Nearest Metro Station',
                                             help_text='e.g., Alimos Metro Station')
    distance_to_airport = models.CharField(max_length=50, blank=True, verbose_name='Distance to Airport',
                                           help_text='e.g., 25 km, 30 min by car')
    
    # Area Highlights (icons will be auto-assigned)
    area_highlight_1 = models.CharField(max_length=100, blank=True, verbose_name='Area Highlight 1',
                                        help_text='e.g., Sandy beaches nearby')
    area_highlight_2 = models.CharField(max_length=100, blank=True, verbose_name='Area Highlight 2',
                                        help_text='e.g., Restaurants & cafes')
    area_highlight_3 = models.CharField(max_length=100, blank=True, verbose_name='Area Highlight 3',
                                        help_text='e.g., Shopping centers')
    area_highlight_4 = models.CharField(max_length=100, blank=True, verbose_name='Area Highlight 4',
                                        help_text='e.g., International schools')
    area_highlight_5 = models.CharField(max_length=100, blank=True, verbose_name='Area Highlight 5',
                                        help_text='e.g., Parks & green spaces')
    area_highlight_6 = models.CharField(max_length=100, blank=True, verbose_name='Area Highlight 6',
                                        help_text='e.g., Medical facilities')
    
    # ===== PRIVATE LOCATION (admin-only) =====
    address_private = models.TextField(
        blank=True,
        verbose_name='Exact Address (Private)',
        help_text='Auto-filled by Google Places autocomplete — never shown to the public.',
    )
    city = models.CharField(
        max_length=100, blank=True, verbose_name='City (Public)',
        help_text='Public city name shown beside the map circle — e.g. "Athens". Safe to display.',
    )
    postal_code = models.CharField(
        max_length=20, blank=True,
        verbose_name='Postal Code (Private)',
        help_text='Auto-filled from Google Places. NEVER shown on the public website.',
    )
    google_place_id = models.CharField(
        max_length=500,
        blank=True,
        verbose_name='Google Place ID (Private)',
        help_text='Auto-filled by Google Places autocomplete. Used for server-side geocoding.',
    )

    # Exact geocoded coordinates — PRIVATE, never sent to browser
    lat_private = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        verbose_name='Latitude (private)',
        help_text='Auto-filled by geocoding. Do not edit manually.',
    )
    lng_private = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        verbose_name='Longitude (private)',
        help_text='Auto-filled by geocoding. Do not edit manually.',
    )

    # Obfuscated public coordinates — safe to embed in page HTML
    lat_public = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        verbose_name='Latitude (public, approximate)',
        help_text='Deliberately shifted from the real location. Auto-generated.',
    )
    lng_public = models.DecimalField(
        max_digits=9, decimal_places=6, null=True, blank=True,
        verbose_name='Longitude (public, approximate)',
        help_text='Deliberately shifted from the real location. Auto-generated.',
    )
    public_radius_m = models.PositiveIntegerField(
        default=400,
        verbose_name='Public Circle Radius (m)',
        help_text='Radius of the "approximate area" circle shown on the map. 250–800 m recommended.',
    )

    PRIVACY_MODE_CHOICES = [
        ('circle_only', 'Circle only (no area name)'),
        ('circle_plus_area', 'Circle + area name'),
    ]
    location_privacy_mode = models.CharField(
        max_length=20,
        choices=PRIVACY_MODE_CHOICES,
        default='circle_plus_area',
        verbose_name='Map Privacy Mode',
    )

    # ── SEO ──────────────────────────────────────────────────────────────────────
    seo_title = models.CharField(
        max_length=70, blank=True, verbose_name='SEO Title',
        help_text='Title shown in Google results (max 70 chars). Leave blank to use property name.',
    )
    meta_description = models.TextField(
        max_length=160, blank=True, verbose_name='Meta Description',
        help_text='Summary shown under the Google result title (max 160 chars). Leave blank to use description excerpt.',
    )
    focus_keyword = models.CharField(
        max_length=120, blank=True, verbose_name='Focus Keyword',
        help_text='Primary keyword this property page targets (e.g. "athens golden visa apartment"). Used for SEO analysis.',
    )
    canonical_url = models.URLField(
        blank=True, verbose_name='Canonical URL',
        help_text='Leave blank — canonical is set automatically from the page URL.',
    )
    og_image = models.ImageField(
        upload_to='seo/og/', blank=True, null=True, verbose_name='OG / Social Image',
        help_text='Custom image for social sharing (1200×630 px). Leave blank to use cover photo.',
    )
    robots_index = models.BooleanField(default=True, verbose_name='Allow indexing',
                                       help_text='Uncheck to add noindex.')
    robots_follow = models.BooleanField(default=True, verbose_name='Follow links')
    seo_allow_publish_override = models.BooleanField(default=False, verbose_name='Override SEO check')

    # ── Direct photo upload slots (15 slots — iPhone HEIC auto-converted to JPEG) ──
    image_1  = models.ImageField(upload_to=_property_direct_image_upload_path, blank=True, verbose_name='Photo 1',  help_text='iPhone HEIC photos are automatically converted to JPEG.')
    image_2  = models.ImageField(upload_to=_property_direct_image_upload_path, blank=True, verbose_name='Photo 2')
    image_3  = models.ImageField(upload_to=_property_direct_image_upload_path, blank=True, verbose_name='Photo 3')
    image_4  = models.ImageField(upload_to=_property_direct_image_upload_path, blank=True, verbose_name='Photo 4')
    image_5  = models.ImageField(upload_to=_property_direct_image_upload_path, blank=True, verbose_name='Photo 5')
    image_6  = models.ImageField(upload_to=_property_direct_image_upload_path, blank=True, verbose_name='Photo 6')
    image_7  = models.ImageField(upload_to=_property_direct_image_upload_path, blank=True, verbose_name='Photo 7')
    image_8  = models.ImageField(upload_to=_property_direct_image_upload_path, blank=True, verbose_name='Photo 8')
    image_9  = models.ImageField(upload_to=_property_direct_image_upload_path, blank=True, verbose_name='Photo 9')
    image_10 = models.ImageField(upload_to=_property_direct_image_upload_path, blank=True, verbose_name='Photo 10')
    image_11 = models.ImageField(upload_to=_property_direct_image_upload_path, blank=True, verbose_name='Photo 11')
    image_12 = models.ImageField(upload_to=_property_direct_image_upload_path, blank=True, verbose_name='Photo 12')
    image_13 = models.ImageField(upload_to=_property_direct_image_upload_path, blank=True, verbose_name='Photo 13')
    image_14 = models.ImageField(upload_to=_property_direct_image_upload_path, blank=True, verbose_name='Photo 14')
    image_15 = models.ImageField(upload_to=_property_direct_image_upload_path, blank=True, verbose_name='Photo 15')

    # ── Cover photo selection (which of the 15 slots is the card cover) ──
    cover_image_slot = models.PositiveSmallIntegerField(
        default=0,
        choices=[(0, 'Auto — use first available photo')] + [(i, f'Photo {i}') for i in range(1, 16)],
        verbose_name='Cover photo (card image)',
        help_text=(
            'Pick which of the 15 photos appears as the COVER on property cards '
            '(homepage, properties list, related cards). '
            'Set to "Auto" to use the first available photo.'
        ),
    )

    # ── Direct video upload slots (shown alongside photos on the property page) ──
    video_1 = models.FileField(
        upload_to='properties/videos/', blank=True,
        verbose_name='Video 1',
        help_text='Upload an MP4 video (max 500 MB). Displayed in a player below the photo gallery.',
    )
    video_1_poster = models.ImageField(
        upload_to='properties/posters/', blank=True,
        verbose_name='Video 1 – Poster / Thumbnail',
        help_text='Optional thumbnail shown before Video 1 plays (recommended: 1280×720 px).',
    )
    video_2 = models.FileField(
        upload_to='properties/videos/', blank=True,
        verbose_name='Video 2',
        help_text='Optional second MP4 video (max 500 MB).',
    )
    video_2_poster = models.ImageField(
        upload_to='properties/posters/', blank=True,
        verbose_name='Video 2 – Poster / Thumbnail',
        help_text='Optional thumbnail shown before Video 2 plays.',
    )

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', '-is_featured', '-created_at']
        verbose_name = 'Property'
        verbose_name_plural = 'Properties'
        indexes = [
            models.Index(fields=['deleted_at', 'is_active']),
            models.Index(fields=['is_active', 'status', 'price_tier']),
            models.Index(fields=['display_order', 'is_featured']),
        ]

    def __str__(self):
        return self.name

    @property
    def main_image(self):
        """Cover image FieldFile — used by list/card templates.

        Resolution order:
          1. Admin-picked direct slot (cover_image_slot 1..15) if it has a file.
          2. PropertyMedia entry flagged is_cover=True.
          3. First available PropertyMedia image.
          4. First non-empty direct slot (image_1..image_15).
        """
        slot = self.cover_image_slot or 0
        if 1 <= slot <= 15:
            picked = getattr(self, f'image_{slot}', None)
            if picked and picked.name:
                return picked
        item = (
            self.media.filter(is_cover=True, image__isnull=False).exclude(image='').first()
            or self.media.filter(image__isnull=False).exclude(image='').order_by('order', 'pk').first()
        )
        if item:
            return item.image
        for direct in self.direct_images:
            return direct
        return None

    @property
    def cover_media(self):
        """The cover item used by templates (PropertyMedia or SimpleImageItem)."""
        slot = self.cover_image_slot or 0
        if 1 <= slot <= 15:
            picked = getattr(self, f'image_{slot}', None)
            if picked and picked.name:
                return SimpleImageItem(picked, index=slot - 1)
        return (
            self.media.filter(is_cover=True, image__isnull=False).exclude(image='').first()
            or self.media.filter(image__isnull=False).exclude(image='').order_by('order', 'pk').first()
        )

    @property
    def gallery_media(self):
        """All image PropertyMedia items, ordered."""
        return self.media.filter(image__isnull=False).exclude(image='').order_by('order', 'pk')

    @property
    def direct_images(self):
        """Non-empty direct image FieldFiles (image_1…image_15), in slot order."""
        result = []
        for i in range(1, 16):
            f = getattr(self, f'image_{i}')
            if f and f.name:
                result.append(f)
        return result

    @property
    def all_gallery_items(self):
        """PropertyMedia images first, then the 15 direct image slots (non-empty)."""
        items = list(self.gallery_media)
        for idx, img in enumerate(self.direct_images):
            items.append(SimpleImageItem(img, idx))
        return items

    @property
    def gallery_cover(self):
        """Cover item for the gallery — admin-picked slot, then PropertyMedia, then first direct image."""
        slot = self.cover_image_slot or 0
        if 1 <= slot <= 15:
            picked = getattr(self, f'image_{slot}', None)
            if picked and picked.name:
                return SimpleImageItem(picked, index=slot - 1)
        pm_cover = (
            self.media.filter(is_cover=True, image__isnull=False).exclude(image='').first()
            or self.media.filter(image__isnull=False).exclude(image='').order_by('order', 'pk').first()
        )
        if pm_cover:
            return pm_cover
        direct = self.direct_images
        if direct:
            return SimpleImageItem(direct[0])
        return None

    @property
    def video_media(self):
        """First video PropertyMedia item, or None."""
        return self.media.filter(video__isnull=False).exclude(video='').order_by('order', 'pk').first()

    @property
    def video(self):
        """Video FieldFile — backward compat for templates."""
        vm = self.video_media
        return vm.video if vm else None

    @property
    def video_poster(self):
        """Video poster FieldFile — backward compat for templates."""
        vm = self.video_media
        return vm.poster if vm else None

    def get_absolute_url(self):
        from django.utils.translation import get_language
        lang = get_language() or 'en'
        slug = getattr(self, f'slug_{lang}', None) or self.slug_en or self.slug
        return reverse('property_detail', kwargs={'slug': slug})

    def get_seo_title(self):
        return self.seo_title or self.name

    def get_meta_description(self):
        if self.meta_description:
            return self.meta_description
        plain = self.description or ''
        import re
        plain = re.sub(r'<[^>]+>', '', plain)
        return plain[:160]

    def get_og_title(self):
        return self.seo_title or self.name

    def get_og_description(self):
        return self.meta_description or self.tagline or self.get_meta_description()[:160]

    def get_og_image(self):
        """Return og_image if set, else fall back to cover photo."""
        if self.og_image:
            return self.og_image
        cover = self.cover_media
        return cover.image if cover else None

    def save(self, *args, **kwargs):
        """
        Auto-geocode when address changes; generate public offset point.

        If _coords_injected_by_places=True is set on the instance, the admin
        form has already written lat_private/lng_private directly from the
        Google Places response — skip the server-side geocoding call.
        If the place_id changed but _coords_injected_by_places is False, use
        the Google Geocoding API (or Nominatim fallback) to fetch coords.
        """
        from core.models import _record_slug_change
        _record_slug_change(self)

        is_new = self.pk is None
        address_changed = False
        place_id_changed = False

        if not is_new:
            try:
                old = Property._default_manager.get(pk=self.pk)
                address_changed = old.address_private != self.address_private
                place_id_changed = old.google_place_id != self.google_place_id
            except Property.DoesNotExist:
                address_changed = bool(self.address_private)
                place_id_changed = bool(self.google_place_id)
        else:
            address_changed = bool(self.address_private)
            place_id_changed = bool(self.google_place_id)

        coords_injected = getattr(self, '_coords_injected_by_places', False)

        if coords_injected:
            # Coords came directly from Google Places JS — always regenerate public point.
            if self.lat_private and self.lng_private:
                self._generate_public_point()
        elif (address_changed or place_id_changed) and self.address_private:
            # Fall back to server-side geocoding (Google Geocoding API → Nominatim).
            self._run_geocoding()
        elif self.address_private and not self.lat_private:
            # Address exists but was never geocoded (manual entry without Places)
            self._run_geocoding()

        # Safety net: if private coords exist but public still missing, generate now.
        if self.lat_private and self.lng_private and not (self.lat_public and self.lng_public):
            self._generate_public_point()

        self._convert_heic_direct_images()
        super().save(*args, **kwargs)

    def _convert_heic_direct_images(self):
        """Convert any HEIC/HEIF uploads in the 15 direct image slots to JPEG."""
        from io import BytesIO
        from PIL import Image
        from django.core.files.base import ContentFile
        import os
        for i in range(1, 16):
            field = getattr(self, f'image_{i}')
            if field and getattr(field, 'name', None) and \
                    field.name.lower().endswith(('.heic', '.heif')):
                try:
                    img = Image.open(field)
                    img = img.convert('RGB')
                    buf = BytesIO()
                    img.save(buf, format='JPEG', quality=90)
                    buf.seek(0)
                    new_name = os.path.basename(
                        os.path.splitext(field.name)[0] + '.jpg'
                    )
                    field.save(new_name, ContentFile(buf.read()), save=False)
                except Exception:
                    pass

    def _run_geocoding(self):
        """Geocode via Google Geocoding API (place_id preferred) or Nominatim fallback."""
        from properties.geocoding import geocode_by_place_id, geocode_address
        result = None
        if self.google_place_id:
            result = geocode_by_place_id(self.google_place_id)
        if result is None:
            result = geocode_address(self.address_private)
        if result:
            self.lat_private, self.lng_private = result
            self._generate_public_point()
        # If geocoding fails we leave existing coords untouched.

    def _generate_public_point(self):
        """Compute + store an obfuscated public lat/lng from the private coords."""
        from properties.geocoding import generate_public_point
        if self.lat_private and self.lng_private:
            pub_lat, pub_lng = generate_public_point(
                float(self.lat_private),
                float(self.lng_private),
                radius_m=self.public_radius_m or 400,
            )
            # Round to 6 d.p. to match DecimalField(decimal_places=6)
            self.lat_public = round(pub_lat, 6)
            self.lng_public = round(pub_lng, 6)

    def regenerate_public_location(self):
        """Force a new random public offset and save.  Called from admin action."""
        if self.lat_private and self.lng_private:
            self._generate_public_point()
            Property._default_manager.filter(pk=self.pk).update(
                lat_public=self.lat_public,
                lng_public=self.lng_public,
            )

    def get_whatsapp_url(self):
        from django.conf import settings
        message = self.whatsapp_message or f"I'm interested in {self.name}"
        number = getattr(settings, 'WHATSAPP_NUMBER', '+306985989596').replace('+', '').replace(' ', '')
        return f"https://wa.me/{number}?text={message}"

    @property
    def has_map(self) -> bool:
        """True only when safe public coordinates are available."""
        return bool(self.lat_public and self.lng_public)

    def get_features_list(self):
        """Return list of non-empty features"""
        features = [self.feature_1, self.feature_2, self.feature_3, self.feature_4]
        return [f for f in features if f]

    def get_all_images(self):
        """Return list of FieldFile objects for all gallery images (ordered)."""
        return [item.image for item in self.gallery_media]


class PropertyInterest(SoftDeleteModel):
    """Customer interest requests from property pages"""
    property = models.ForeignKey(Property, on_delete=models.PROTECT, related_name='interests')
    full_name = models.CharField(max_length=100, blank=True, verbose_name='Full Name')
    email = models.EmailField(blank=True, verbose_name='Email')
    phone = models.CharField(max_length=30, blank=True, verbose_name='Phone')
    message = models.TextField(blank=True, verbose_name='Message')
    is_read = models.BooleanField(default=False, verbose_name='Read')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Property Interest Request'
        verbose_name_plural = 'Property Interest Requests'
        indexes = [
            models.Index(fields=['deleted_at', 'created_at']),
            models.Index(fields=['is_read', 'created_at']),
        ]

    def __str__(self):
        name = self.full_name or self.email or 'Anonymous'
        return f"{name} → {self.property.name} ({self.created_at.strftime('%Y-%m-%d')})"


class PropertyUnit(SoftDeleteModel):
    """Individual units within a property/apartment project"""
    AVAILABILITY_CHOICES = [
        ('available', 'Available'),
        ('reserved', 'Reserved'),
        ('sold', 'Sold'),
    ]
    
    property = models.ForeignKey(Property, on_delete=models.PROTECT, related_name='property_units')
    unit_label = models.CharField(max_length=100, verbose_name='Unit Label', help_text='e.g., Unit A1, Floor 2 - Apt 3')
    size_sqm = models.DecimalField(max_digits=8, decimal_places=2, verbose_name='Size (m²)')
    bedrooms = models.PositiveIntegerField(default=1, verbose_name='Bedrooms')
    bathrooms = models.PositiveIntegerField(default=1, verbose_name='Bathrooms')
    parking = models.BooleanField(default=True, verbose_name='Parking')
    price = models.DecimalField(max_digits=12, decimal_places=2, verbose_name='Price (€)')
    availability = models.CharField(max_length=20, choices=AVAILABILITY_CHOICES, default='available', verbose_name='Status')
    order = models.PositiveIntegerField(default=0, verbose_name='Row Order')
    
    class Meta:
        ordering = ['order', 'unit_label']
        verbose_name = 'Property Unit'
        verbose_name_plural = 'Property Units'
        constraints = [
            models.UniqueConstraint(
                fields=['property', 'unit_label'],
                condition=Q(deleted_at__isnull=True),
                name='uniq_active_unit_label_per_property',
            ),
        ]
        indexes = [
            models.Index(fields=['property', 'availability', 'deleted_at']),
            models.Index(fields=['deleted_at', 'order']),
        ]
    
    def __str__(self):
        return f"{self.property.name} - {self.unit_label}"

    def delete(self, using=None, keep_parents=False):
        if self.deleted_at is not None:
            return

        archived_at = timezone.now()
        self.deleted_at = archived_at
        self.save(update_fields=['deleted_at'])
        UnitBooking.objects.filter(unit=self, deleted_at__isnull=True).update(deleted_at=archived_at)

    def hard_delete(self, using=None, keep_parents=False):
        if UnitBooking.all_objects.filter(unit=self).exists():
            raise ValidationError('Cannot permanently delete a unit that has booking records. Archive it instead.')
        return super().hard_delete(using=using, keep_parents=keep_parents)


class UnitBooking(SoftDeleteModel):
    """Booking requests for property units"""
    unit = models.ForeignKey(PropertyUnit, on_delete=models.PROTECT, related_name='bookings')
    full_name = models.CharField(max_length=100, verbose_name='Full Name')
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=30, verbose_name='Phone')
    message = models.TextField(blank=True, verbose_name='Message')
    is_read = models.BooleanField(default=False, verbose_name='Read')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Unit Booking Request'
        verbose_name_plural = 'Unit Booking Requests'
        indexes = [
            models.Index(fields=['unit', 'created_at']),
            models.Index(fields=['is_read', 'created_at']),
            models.Index(fields=['deleted_at', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.full_name} → {self.unit.unit_label} ({self.unit.property.name})"

    def clean(self):
        super().clean()
        if not self.unit_id:
            return

        email = (self.email or '').strip().lower()
        phone = (self.phone or '').strip()
        if not email and not phone:
            raise ValidationError('Email or phone is required for booking deduplication checks.')

        duplicates = UnitBooking.all_objects.filter(
            unit=self.unit,
            is_read=False,
            deleted_at__isnull=True,
        )
        if self.pk:
            duplicates = duplicates.exclude(pk=self.pk)
        if email:
            duplicates = duplicates.filter(email__iexact=email)
        elif phone:
            duplicates = duplicates.filter(phone=phone)

        if duplicates.exists():
            raise ValidationError('A pending booking already exists for this unit with the same contact details.')

    def save(self, *args, **kwargs):
        self.full_clean()
        return super().save(*args, **kwargs)


def _property_image_upload_path(instance, filename):
    """Save new gallery images with SEO-friendly filenames.

    Pattern: properties/gallery/{property-slug}-{8-char-uuid}.{ext}
    Example: properties/gallery/ermis-athens-a1b2c3d4.jpg
    """
    import re
    import uuid
    import os

    ext = (os.path.splitext(filename)[1] or '.jpg').lower()
    prop = instance.property
    # Prefer the EN slug (most stable, ASCII-safe)
    slug = (
        getattr(prop, 'slug_en', None)
        or getattr(prop, 'slug', None)
        or ''
    ).strip().lower()
    if not slug:
        raw = getattr(prop, 'name_en', None) or getattr(prop, 'name', None) or 'property'
        slug = re.sub(r'[^\w\s-]', '', raw.lower())
        slug = re.sub(r'[\s_]+', '-', slug).strip('-')
    # Keep only URL-safe chars, max 50 chars
    slug = re.sub(r'[^a-z0-9-]', '', slug)[:50].rstrip('-')
    uid = uuid.uuid4().hex[:8]
    return f'properties/gallery/{slug}-{uid}{ext}'


class PropertyMedia(models.Model):
    """A single photo or video belonging to a property gallery."""

    property = models.ForeignKey(
        Property, on_delete=models.CASCADE, related_name='media',
        verbose_name='Property',
    )
    image = models.ImageField(
        upload_to=_property_image_upload_path, blank=True,
        verbose_name='Photo',
        help_text='Upload a photo. HEIC/iPhone photos are automatically converted to JPEG.',
    )
    video = models.FileField(
        upload_to='properties/videos/', blank=True,
        verbose_name='Video',
        help_text='MP4 recommended, max 500 MB. Leave blank when uploading a photo.',
    )
    poster = models.ImageField(
        upload_to='properties/posters/', blank=True,
        verbose_name='Video Poster',
        help_text='Thumbnail shown before the video plays (only used with a video).',
    )
    caption = models.CharField(
        max_length=200, blank=True,
        verbose_name='ALT Text',
        help_text=(
            'Describe what is shown in this image for screen readers and search engines. '
            'Example: "Modern living room with sea view, Alimos Athens". '
            'Leave blank to fall back to the property name. '
            'Tick "Decorative" below if the image is purely visual and needs no description.'
        ),
    )
    is_decorative = models.BooleanField(
        default=False,
        verbose_name='Decorative image',
        help_text=(
            'Tick if this image is a background fill, spacer, or purely visual decoration '
            'that adds no meaningful information. The website will render alt="" for it, '
            'which is correct accessibility practice.'
        ),
    )
    is_cover = models.BooleanField(
        default=False, verbose_name='Cover photo',
        help_text='Mark as the main/cover image shown in property cards.',
    )
    order = models.PositiveIntegerField(
        default=0, verbose_name='Order',
        help_text='Lower numbers appear first in the gallery.',
    )

    class Meta:
        ordering = ['order', 'pk']
        verbose_name = 'Media'
        verbose_name_plural = 'Media'

    def __str__(self):
        if self.video:
            return f'Video – {self.property.name}'
        return f'Photo {self.order} – {self.property.name}'

    def get_alt(self, lang=None):
        """Return the best available ALT text for *lang* (defaults to active language).

        Returns '' immediately for decorative images (correct a11y: alt="").
        Fallback chain: requested lang → English → property name.
        """
        if self.is_decorative:
            return ''
        from django.utils.translation import get_language
        lang = (lang or get_language() or 'en').split('-')[0]  # 'en-us' → 'en'
        value = getattr(self, f'caption_{lang}', None)
        if not value:
            value = getattr(self, 'caption_en', None) or getattr(self, 'caption', None)
        if not value:
            value = getattr(self.property, f'name_{lang}', None) or self.property.name
        return value or ''

    def clean(self):
        super().clean()
        has_image = bool(self.image and getattr(self.image, 'name', None))
        has_video = bool(self.video and getattr(self.video, 'name', None))
        if not has_image and not has_video:
            raise ValidationError('Each media item must have either a photo or a video file.')
        if has_image and has_video:
            raise ValidationError(
                'A media item cannot contain both a photo and a video. Add them as separate items.'
            )

    def save(self, *args, **kwargs):
        """Auto-convert HEIC/HEIF to JPEG before saving."""
        if self.image and getattr(self.image, 'name', None) and \
                self.image.name.lower().endswith(('.heic', '.heif')):
            try:
                from PIL import Image
                from io import BytesIO
                from django.core.files.base import ContentFile
                import os
                img = Image.open(self.image)
                img = img.convert('RGB')
                buf = BytesIO()
                img.save(buf, format='JPEG', quality=90)
                buf.seek(0)
                new_name = os.path.basename(os.path.splitext(self.image.name)[0] + '.jpg')
                self.image.save(new_name, ContentFile(buf.read()), save=False)
            except Exception:
                pass
        super().save(*args, **kwargs)
