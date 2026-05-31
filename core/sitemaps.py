"""
XML Sitemap definitions for adonisgroup.gr.

Structure
─────────
StaticViewSitemap   — home, about, contact, blog list, partnerships, events
BlogPostSitemap     — published BlogPost objects
PropertySitemap     — active (non-deleted) Property objects

Multilingual support
────────────────────
I18nSitemapMixin wraps get_urls() in django.utils.translation.override() for
every LANGUAGES entry so that i18n_patterns produces the correct language-
prefixed URL for each entry.

  English (prefix_default_language=False): /blog/my-post/
  Turkish:                                 /tr/blog/benim-yaziim/

Django's sitemap framework resolves the domain from the incoming request, so
no SITE_ID / django.contrib.sites is required.
"""

from __future__ import annotations

import logging
from typing import Iterator

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.urls import reverse
from django.utils.translation import override as lang_override

logger = logging.getLogger(__name__)


# ── Multilingual mixin ────────────────────────────────────────────────────────

class I18nSitemapMixin:
    """
    Repeats get_urls() once per configured language, wrapping each call in
    translation.override(lang_code) so reverse() returns the correct prefix.
    """

    def get_urls(self, page: int = 1, site=None, protocol: str | None = None):
        all_urls: list = []
        for lang_code, _ in settings.LANGUAGES:
            with lang_override(lang_code):
                try:
                    all_urls.extend(
                        super().get_urls(page=page, site=site, protocol=protocol)
                    )
                except Exception:
                    logger.exception(
                        "Sitemap error for %s / lang=%s", self.__class__.__name__, lang_code
                    )
        return all_urls


# ── Static pages ──────────────────────────────────────────────────────────────

class StaticViewSitemap(I18nSitemapMixin, Sitemap):
    """
    One entry per static named URL × language.

    Each item is (url_name, priority).  We try to reverse every name and skip
    any that raise NoReverseMatch so the sitemap never hard-crashes on a
    missing URL.
    """

    changefreq = "weekly"
    protocol = "https"

    # (named URL, priority)
    _pages: list[tuple[str, float]] = [
        ("home",         1.0),
        ("about",        0.7),
        ("contact",      0.7),
        ("blog_list",    0.8),
        ("partnerships", 0.6),
        ("event_list",   0.5),
        # Golden Visa is handled by GoldenVisaLandingPageSitemap (respects robots_index)
    ]

    def items(self) -> list[tuple[str, float]]:
        valid = []
        for name, prio in self._pages:
            try:
                reverse(name)          # validate the URL exists
                valid.append((name, prio))
            except Exception:
                logger.warning("Sitemap: skipping unknown URL name %r", name)
        return valid

    def location(self, item: tuple[str, float]) -> str:
        return reverse(item[0])

    def priority(self, item: tuple[str, float]) -> float:
        return item[1]


# ── Blog posts ────────────────────────────────────────────────────────────────

class BlogPostSitemap(I18nSitemapMixin, Sitemap):
    """Published blog posts, ordered newest-first."""

    changefreq = "weekly"
    priority = 0.7
    protocol = "https"

    def items(self):
        from core.models import BlogPost
        return (
            BlogPost.objects
            .filter(is_published=True, robots_index=True, noindex=False)
            .order_by("-updated_at")
            .only("slug_en", "slug_tr", "updated_at")
        )

    def lastmod(self, obj) -> object:
        return obj.updated_at

    def location(self, obj) -> str:
        return obj.get_absolute_url()


# ── Properties ────────────────────────────────────────────────────────────────

class PropertySitemap(I18nSitemapMixin, Sitemap):
    """Active (non-soft-deleted) property listings."""

    changefreq = "weekly"
    priority = 0.9
    protocol = "https"

    def items(self):
        from properties.models import Property
        return (
            Property.objects
            .filter(is_active=True, deleted_at__isnull=True, robots_index=True)
            .order_by("-updated_at")
            .only("slug_en", "slug_tr", "updated_at")
        )

    def lastmod(self, obj) -> object:
        return obj.updated_at

    def location(self, obj) -> str:
        return obj.get_absolute_url()


# ── Events ────────────────────────────────────────────────────────────────────

class EventSitemap(I18nSitemapMixin, Sitemap):
    changefreq = "weekly"
    priority = 0.5
    protocol = "https"

    def items(self):
        from core.models import Event
        return (
            Event.objects
            .filter(is_active=True, robots_index=True)
            .order_by("-updated_at")
        )

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


# ── Brochures ─────────────────────────────────────────────────────────────────

class BrochureSitemap(I18nSitemapMixin, Sitemap):
    changefreq = "monthly"
    priority = 0.4
    protocol = "https"

    def items(self):
        from brochures.models import Brochure
        return (
            Brochure.objects
            .filter(is_published=True, robots_index=True)
            .order_by("-updated_at")
        )

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return obj.get_absolute_url()


# ── Golden Visa Landing Page ──────────────────────────────────────────────────

class GoldenVisaLandingPageSitemap(I18nSitemapMixin, Sitemap):
    """
    Singleton sitemap entry for /greece-golden-visa/.

    Only included when the page is both published AND set to robots_index=True.
    Removing the page from the sitemap is as simple as unchecking "Allow indexing"
    in the Django admin.
    """

    changefreq = "monthly"
    priority = 0.9
    protocol = "https"

    def items(self):
        from core.models import GoldenVisaLandingPage
        try:
            obj = GoldenVisaLandingPage.objects.get(pk=1)
            if obj.is_published and obj.robots_index and not getattr(obj, "noindex", False):
                return [obj]
        except GoldenVisaLandingPage.DoesNotExist:
            pass
        return []

    def location(self, obj):
        return reverse("greece_golden_visa")

    def lastmod(self, obj):
        return None


class WebinarLandingSitemap(I18nSitemapMixin, Sitemap):
    changefreq = "monthly"
    priority = 0.8
    protocol = "https"

    def items(self):
        from core.models import WebinarLandingSettings
        obj = WebinarLandingSettings.get_settings()
        if obj.active_status and not getattr(obj, "noindex", False):
            return [obj]
        return []

    def location(self, obj):
        return reverse("webinar_landing")

    def lastmod(self, obj):
        return None


class PersianGoldenVisaAdsSitemap(I18nSitemapMixin, Sitemap):
    changefreq = "weekly"
    priority = 0.8
    protocol = "https"

    def items(self):
        from core.models import GoldenVisaFaLandingPage
        obj = GoldenVisaFaLandingPage.get_settings()
        if obj.is_published and not getattr(obj, "noindex", False):
            return [obj]
        return []

    def location(self, obj):
        return reverse("greece_golden_visa_fa_ads")

    def lastmod(self, obj):
        return None


# ── Registry (imported by urls.py) ────────────────────────────────────────────

sitemaps: dict[str, type[Sitemap]] = {
    "static":      StaticViewSitemap,
    "blog":        BlogPostSitemap,
    "properties":  PropertySitemap,
    "events":      EventSitemap,
    "brochures":   BrochureSitemap,
    "golden_visa": GoldenVisaLandingPageSitemap,
    "webinar":     WebinarLandingSitemap,
    "fa_ads":      PersianGoldenVisaAdsSitemap,
}
