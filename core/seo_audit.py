"""
SEO Audit Engine

audit_object(obj) → { score, critical, warnings, suggestions }

Rule profiles adapt to content type: BLOG, PROPERTY, LANDING, EVENT, GENERIC.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from django.utils.html import strip_tags


@dataclass
class AuditResult:
    score: int = 100
    critical: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    suggestions: list[str] = field(default_factory=list)

    def add_critical(self, msg: str):
        self.critical.append(msg)
        self.score = max(0, self.score - 20)

    def add_warning(self, msg: str):
        self.warnings.append(msg)
        self.score = max(0, self.score - 5)

    def add_suggestion(self, msg: str):
        self.suggestions.append(msg)

    @property
    def has_critical(self) -> bool:
        return len(self.critical) > 0


# ── Content-type detection ──────────────────────────────────────────────────

def _detect_type(obj) -> str:
    name = type(obj).__name__.lower()
    if 'blog' in name or 'post' in name:
        return 'blog'
    if 'property' in name and 'media' not in name:
        return 'property'
    if 'landing' in name or 'goldenvisa' in name:
        return 'landing'
    if 'event' in name:
        return 'event'
    if 'brochure' in name:
        return 'brochure'
    return 'generic'


# ── Individual rule functions ───────────────────────────────────────────────

def _check_title(obj, result: AuditResult):
    h1 = obj.get_h1() if hasattr(obj, 'get_h1') else ''
    if not h1:
        result.add_critical('Missing page title / H1.')
    elif len(h1) > 100:
        result.add_warning(f'H1 is very long ({len(h1)} chars) — keep under 70 for best results.')


def _check_slug(obj, result: AuditResult):
    slug = (getattr(obj, 'slug', '') or getattr(obj, 'slug_en', '') or
            getattr(obj, 'detail_page_url', ''))
    # Singleton models (GoldenVisaLandingPage etc.) have a fixed URL with no slug field
    has_fixed_url = hasattr(obj, 'get_absolute_url') or type(obj).__name__ in ('GoldenVisaLandingPage',)
    if not slug and not has_fixed_url:
        result.add_critical('No URL slug set.')
    elif slug and len(slug) > 75:
        result.add_warning(f'Slug is long ({len(slug)} chars) — shorter URLs rank better.')


def _check_seo_title(obj, result: AuditResult):
    title = getattr(obj, 'seo_title', '') or getattr(obj, 'meta_title', '')
    if not title:
        result.add_warning('SEO title is empty — will fall back to page title.')
    elif len(title) > 60:
        result.add_warning(f'SEO title is {len(title)} chars — exceeds 60 character limit, Google may truncate it.')
    elif len(title) < 30:
        result.add_suggestion('SEO title is short — aim for 40–60 characters.')


def _check_meta_description(obj, result: AuditResult):
    desc = getattr(obj, 'meta_description', '')
    if not desc:
        result.add_critical('Meta description is empty — Google will auto-generate a snippet.')
    elif len(desc) > 160:
        result.add_warning(f'Meta description is {len(desc)} chars — may be truncated (max 160).')
    elif len(desc) < 50:
        result.add_warning('Meta description is very short — aim for 120–160 characters.')


def _check_canonical(obj, result: AuditResult):
    explicit = getattr(obj, 'canonical_url', '')
    has_url = hasattr(obj, 'get_absolute_url')
    if not explicit and not has_url:
        result.add_warning('No canonical URL — page may have duplicate indexing issues.')


def _check_robots(obj, result: AuditResult):
    published = False
    for attr in ('is_published', 'is_active'):
        val = getattr(obj, attr, None)
        if val is not None:
            published = bool(val)
            break

    idx = getattr(obj, 'robots_index', True)
    if published and not idx:
        result.add_warning('Page is published but set to noindex — it will not appear in Google.')


def _check_featured_image(obj, result: AuditResult):
    img = obj.get_featured_image() if hasattr(obj, 'get_featured_image') else None
    if not img:
        result.add_warning('No featured / OG image — social shares will look plain.')
        return

    alt = obj.get_featured_image_alt() if hasattr(obj, 'get_featured_image_alt') else ''
    if not alt or alt == 'Adonis Group property image':
        result.add_critical('Featured image has no ALT text — required for SEO and accessibility.')


def _check_body_length(obj, content_type: str, result: AuditResult):
    body = obj.get_body_text() if hasattr(obj, 'get_body_text') else ''
    # For landing pages with sectioned content, also count other text fields
    if content_type == 'landing':
        extras = []
        for attr in ('benefits_text', 'process_steps', 'tier_250_desc', 'tier_400_desc', 'tier_800_desc'):
            val = getattr(obj, attr, '') or ''
            extras.append(strip_tags(val))
        body = body + ' ' + ' '.join(extras)

    word_count = len(body.split()) if body.strip() else 0

    min_words = {'blog': 300, 'landing': 150, 'property': 100, 'event': 100}.get(content_type, 100)
    if word_count < min_words:
        result.add_warning(
            f'Body text is only {word_count} words — {min_words}+ recommended for {content_type} pages.'
        )
    elif word_count < min_words * 2:
        result.add_suggestion(f'Body is {word_count} words — consider expanding for better ranking.')


def _check_headings(obj, content_type: str, result: AuditResult):
    """Check for H2 headings in long-form content."""
    if content_type not in ('blog', 'landing'):
        return
    html = obj.get_body_html() if hasattr(obj, 'get_body_html') else ''
    if not html:
        return
    h2_count = len(re.findall(r'<h2[\s>]', html, re.I))
    if h2_count == 0:
        result.add_critical('No H2 headings in content — articles need structured sections.')

    h1_count = len(re.findall(r'<h1[\s>]', html, re.I))
    if h1_count > 0:
        result.add_warning(f'Content contains {h1_count} H1 tag(s) — only one H1 per page (auto-set from title).')


def _check_focus_keyword(obj, result: AuditResult):
    kw = getattr(obj, 'focus_keyword', '')
    if not kw:
        result.add_suggestion('No focus keyword set — helps track SEO targeting.')
        return

    kw_lower = kw.lower()
    title = (getattr(obj, 'seo_title', '') or getattr(obj, 'meta_title', '') or '').lower()
    desc = (getattr(obj, 'meta_description', '') or '').lower()

    if kw_lower not in title:
        result.add_warning(f'Focus keyword "{kw}" not found in SEO title.')
    if kw_lower not in desc:
        result.add_warning(f'Focus keyword "{kw}" not found in meta description.')


def _check_images_alt(obj, result: AuditResult):
    """Check all image fields for missing ALT text."""
    if not hasattr(obj, 'get_all_image_fields'):
        return
    for field_name, img, alt, is_decorative in obj.get_all_image_fields():
        if img and not alt and not is_decorative:
            result.add_warning(f'Image "{field_name}" is missing ALT text.')


def _check_property_gallery(obj, result: AuditResult):
    """Property-specific: check gallery has images."""
    if not hasattr(obj, 'media'):
        return
    img_count = obj.media.filter(image__isnull=False).exclude(image='').count()
    if img_count == 0:
        result.add_critical('Property has no gallery photos.')
    elif img_count < 3:
        result.add_warning(f'Only {img_count} gallery photo(s) — 5+ recommended.')

    location = getattr(obj, 'location', '') or ''
    if not location:
        result.add_critical('Property has no location set.')


# ── Main audit function ─────────────────────────────────────────────────────

def audit_object(obj) -> AuditResult:
    """
    Run the full SEO audit on a model instance.

    Returns AuditResult with score (0–100), critical issues, warnings, and suggestions.
    """
    result = AuditResult()
    content_type = _detect_type(obj)

    # Universal checks
    _check_title(obj, result)
    _check_slug(obj, result)
    _check_seo_title(obj, result)
    _check_meta_description(obj, result)
    _check_canonical(obj, result)
    _check_robots(obj, result)
    _check_featured_image(obj, result)
    _check_focus_keyword(obj, result)
    _check_images_alt(obj, result)

    # Content-type-specific checks
    if content_type in ('blog', 'landing', 'event'):
        _check_body_length(obj, content_type, result)

    if content_type in ('blog', 'landing'):
        _check_headings(obj, content_type, result)

    if content_type == 'property':
        _check_property_gallery(obj, result)
        _check_body_length(obj, 'property', result)

    # Clamp score
    result.score = max(0, min(100, result.score))
    return result


def can_publish(obj, user=None) -> tuple[bool, list[str]]:
    """
    Check if obj is allowed to be published.

    Returns (allowed: bool, reasons: list[str]).
    If seo_allow_publish_override is True and user is superadmin, override is allowed.
    """
    result = audit_object(obj)
    if not result.has_critical:
        return True, []

    override = getattr(obj, 'seo_allow_publish_override', False)
    if override and user and user.is_superuser:
        return True, [f'⚠️ SEO override active — {len(result.critical)} critical issue(s) bypassed.']

    return False, result.critical
