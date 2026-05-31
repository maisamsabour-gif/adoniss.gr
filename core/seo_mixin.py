"""
Reusable SEO and image-accessibility helpers.
"""
from __future__ import annotations

from django.db import models
from django.utils.html import strip_tags
from django.utils.translation import get_language


DEFAULT_IMAGE_ALT = 'Adonis Group image'


def _active_lang(lang: str | None = None) -> str:
    current = (lang or get_language() or 'en').split('-')[0].lower()
    return 'tr' if current == 'tr' else 'en'


def get_localized_field_value(
    instance,
    base_name: str,
    lang: str | None = None,
    fallback_to_en: bool = True,
    default: str = '',
) -> str:
    """
    Resolve <base_name> for current language with EN fallback.

    Order:
      1) <base_name>_<active_lang>
      2) <base_name>_en (optional fallback)
      3) <base_name> (plain non-translated field)
      4) default
    """
    active_lang = _active_lang(lang)
    localized_attr = f'{base_name}_{active_lang}'
    if hasattr(instance, localized_attr):
        value = getattr(instance, localized_attr) or ''
        if value:
            return value.strip()

    if fallback_to_en and active_lang != 'en':
        en_attr = f'{base_name}_en'
        if hasattr(instance, en_attr):
            value = getattr(instance, en_attr) or ''
            if value:
                return value.strip()

    plain = getattr(instance, base_name, '') or ''
    return plain.strip() if plain else default


def is_image_decorative(instance, prefix: str = '') -> bool:
    """Return decorative flag for either '<prefix>_is_decorative' or 'is_decorative'."""
    if prefix:
        prefixed_name = f'{prefix}_is_decorative'
        if hasattr(instance, prefixed_name):
            return bool(getattr(instance, prefixed_name))
    return bool(getattr(instance, 'is_decorative', False))


def get_localized_image_alt(
    instance,
    prefix: str = '',
    lang: str | None = None,
    fallback: str = DEFAULT_IMAGE_ALT,
) -> str:
    """
    Return localized ALT text for an image slot.

    Checks (in order):
      - <prefix>_alt_text_<lang> / <prefix>_alt_text_en
      - <prefix>_alt_<lang> / <prefix>_alt_en
      - <prefix>_caption_<lang> / <prefix>_caption_en
      - generic alt_text / alt / caption fields (same language fallback chain)
      - fallback

    If image is decorative, returns empty string.
    """
    if is_image_decorative(instance, prefix=prefix):
        return ''

    candidates = []
    if prefix:
        candidates.extend([
            f'{prefix}_alt_text',
            f'{prefix}_alt',
            f'{prefix}_caption',
        ])
    candidates.extend(['alt_text', 'alt', 'caption'])

    for base in candidates:
        val = get_localized_field_value(instance, base, lang=lang, fallback_to_en=True, default='')
        if val:
            return val

    return fallback


class SEOMetadata(models.Model):
    """Abstract mixin that adds a standard set of SEO fields."""

    seo_title = models.CharField(
        max_length=70,
        blank=True,
        verbose_name='SEO Title',
        help_text='Shown in Google results (max 70 chars). Leave blank to use page title.',
    )
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        verbose_name='Meta Description',
        help_text='Google snippet text (max 160 chars). Leave blank to auto-generate.',
    )
    focus_keyword = models.CharField(
        max_length=120,
        blank=True,
        verbose_name='Focus Keyword',
        help_text='Primary keyword this page targets. Used for SEO scoring only.',
    )
    canonical_url = models.URLField(
        blank=True,
        verbose_name='Canonical URL',
        help_text='Leave blank — canonical is auto-generated from the page URL.',
    )
    robots_index = models.BooleanField(
        default=True,
        verbose_name='Allow indexing',
        help_text='Uncheck to add noindex — hides page from search engines.',
    )
    robots_follow = models.BooleanField(
        default=True,
        verbose_name='Follow links',
        help_text='Uncheck to add nofollow — tells crawlers to ignore links on this page.',
    )
    og_image = models.ImageField(
        upload_to='seo/og/',
        blank=True,
        null=True,
        verbose_name='OG / Social Image',
        help_text='Sharing image for Facebook, LinkedIn, WhatsApp (1200x630 px).',
    )
    structured_data_json = models.JSONField(
        blank=True,
        null=True,
        verbose_name='Custom Structured Data (JSON-LD)',
        help_text='Advanced — leave empty. If set, this JSON-LD is injected into the page &lt;head&gt;.',
    )
    seo_allow_publish_override = models.BooleanField(
        default=False,
        verbose_name='Override SEO check',
        help_text='Superadmin only — allows publishing even with critical SEO issues.',
    )

    class Meta:
        abstract = True


class SEOContentInterface:
    """Shared protocol for SEO meta rendering and audits."""

    def get_h1(self, lang: str | None = None) -> str:
        """Return the text rendered as <h1> on the page."""
        return (
            get_localized_field_value(self, 'title', lang=lang, default='')
            or get_localized_field_value(self, 'name', lang=lang, default='')
            or get_localized_field_value(self, 'hero_title', lang=lang, default='')
            or str(self)
        )

    def get_seo_title(self, lang: str | None = None) -> str:
        """Return the <title> value with language-aware fallback."""
        return (
            get_localized_field_value(self, 'seo_title', lang=lang, default='')
            or get_localized_field_value(self, 'meta_title', lang=lang, default='')
            or self.get_h1(lang=lang)
        )

    def get_meta_description(self, lang: str | None = None) -> str:
        """Return <meta name=description> value with language-aware fallback."""
        desc = get_localized_field_value(self, 'meta_description', lang=lang, default='')
        if desc:
            return desc

        for field in ('excerpt', 'description', 'content', 'body', 'intro_text', 'hero_subtitle'):
            raw = get_localized_field_value(self, field, lang=lang, default='')
            if raw:
                return strip_tags(raw).strip()[:160]
        return ''

    def get_focus_keyword(self, lang: str | None = None) -> str:
        return get_localized_field_value(self, 'focus_keyword', lang=lang, default='')

    def get_featured_image(self):
        """Return the primary image FieldFile (or None)."""
        for attr in ('og_image', 'featured_image', 'image', 'thumbnail', 'cover_image', 'hero_image'):
            img = getattr(self, attr, None)
            if img:
                return img
        return None

    def get_featured_image_alt(self, lang: str | None = None) -> str:
        """Return localized ALT text for the primary image."""
        fallback = self.get_h1(lang=lang) or DEFAULT_IMAGE_ALT
        for prefix in ('featured_image', 'image', 'thumbnail', 'cover_image', 'hero_image'):
            if getattr(self, prefix, None):
                return get_localized_image_alt(self, prefix=prefix, lang=lang, fallback=fallback)
        return get_localized_image_alt(self, prefix='', lang=lang, fallback=fallback)

    def get_og_title(self, lang: str | None = None) -> str:
        return self.get_seo_title(lang=lang)

    def get_og_description(self, lang: str | None = None) -> str:
        return self.get_meta_description(lang=lang)

    def get_og_image(self):
        """Return OG image FieldFile — og_image field, then featured image."""
        og = getattr(self, 'og_image', None)
        if og:
            return og
        return self.get_featured_image()

    def get_robots_meta(self) -> str:
        """Return robots meta tag content."""
        idx = 'index' if getattr(self, 'robots_index', True) else 'noindex'
        fol = 'follow' if getattr(self, 'robots_follow', True) else 'nofollow'
        return f'{idx}, {fol}'

    def get_canonical_url(self) -> str:
        """Return canonical URL — explicit field or fallback to get_absolute_url()."""
        explicit = getattr(self, 'canonical_url', '') or ''
        if explicit:
            return explicit
        if hasattr(self, 'get_absolute_url'):
            return self.get_absolute_url()
        return ''

    def get_body_text(self, lang: str | None = None) -> str:
        """Return plain body text for audits."""
        for field in ('content', 'description', 'body', 'intro_text', 'full_description'):
            raw = get_localized_field_value(self, field, lang=lang, default='')
            if raw:
                return strip_tags(raw).strip()
        return ''

    def get_body_html(self, lang: str | None = None) -> str:
        """Return raw body HTML for heading analysis."""
        for field in ('content', 'description', 'body', 'intro_text', 'full_description'):
            raw = get_localized_field_value(self, field, lang=lang, default='')
            if raw:
                return raw
        return ''

    def get_all_image_fields(self) -> list[tuple[str, object, str, bool]]:
        """
        Return list of (field_name, image_fieldfile, alt_text, is_decorative)
        for every public image-like field on the object.
        """
        results = []
        image_slots = (
            'featured_image',
            'image',
            'thumbnail',
            'cover_image',
            'hero_image',
            'og_image',
            'neighborhood_image',
            'tier_250_image',
            'tier_400_image',
            'tier_800_image',
        )
        for field_name in image_slots:
            image_obj = getattr(self, field_name, None)
            if image_obj:
                results.append((
                    field_name,
                    image_obj,
                    get_localized_image_alt(self, prefix=field_name, fallback=''),
                    is_image_decorative(self, prefix=field_name),
                ))
        return results

    def seo_context(self) -> dict:
        """Return common SEO context for templates."""
        og_img = self.get_og_image()
        return {
            'meta_title': self.get_seo_title(),
            'meta_description': self.get_meta_description(),
            'og_title': self.get_og_title(),
            'og_description': self.get_og_description(),
            'og_image_obj': og_img if og_img else None,
            'canonical_url': self.get_canonical_url(),
            'robots_meta': self.get_robots_meta(),
        }

    def is_published_for_seo(self) -> bool:
        """Return True if this object should be treated as published."""
        for attr in ('is_published', 'is_active'):
            val = getattr(self, attr, None)
            if val is not None:
                return bool(val)
        return True
