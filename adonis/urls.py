"""
URL configuration for Adonis project.
"""
from django.contrib import admin
from django.http import HttpResponse
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls.i18n import i18n_patterns
from django.contrib.sitemaps.views import sitemap as sitemap_view
from django.views.decorators.cache import cache_page

from core.sitemaps import sitemaps
from apps.persian_cms.sitemaps import persian_sitemaps
from core.views import admin_dashboard_stats
from core.admin_dashboard_seo import seo_dashboard
from core.views_backup import site_backup_page, site_backup_generate, site_backup_download
from apps.persian_cms.admin_site import persian_admin_site


# Root sitemap includes both global + /fa-new/ Persian URLs.
all_sitemaps = {**sitemaps, **persian_sitemaps}


def robots_txt(request):
    """Serve robots.txt — publicly accessible, no login required.

    The sitemap URL is built from the live host (so it is correct on whatever
    domain the site is served — adoniss.gr) and points at the Persian sitemap,
    keeping this (Persian) site's index separate from the English site.
    """
    host = request.get_host()
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /fa-admin/",
        "Disallow: /persian-admin/",
        "Disallow: /crm/",
        "Disallow: /login/",
        "Disallow: /dashboard/",
        "Disallow: /ckeditor5/",
        "Disallow: /media/private/",
        "",
        "Allow: /static/",
        "Allow: /media/",
        "",
        f"Sitemap: https://{host}/fa-new/sitemap.xml",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")


def ai_txt(request):
    """Optional machine-readable hints for AI crawlers."""
    lines = [
        "Project: ADONISS",
        "Canonical: https://adoniss.gr/",
        "Sitemap: https://adoniss.gr/sitemap.xml",
        "Sitemap: https://adoniss.gr/fa-new/sitemap.xml",
        "Policy: Public marketing pages may be indexed.",
        "Policy: Admin and private paths must not be indexed.",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")


# ── Language-INDEPENDENT URLs ─────────────────────────────────────────────────
# Admin, internal tooling, language switcher, sitemap — no /en/ or /tr/ prefix.
urlpatterns = [
    # Language switcher endpoint (must be outside i18n_patterns)
    path('i18n/', include('django.conf.urls.i18n')),

    # Django admin (keeps plain /admin/ URL, no language prefix needed)
    path('admin/dashboard-stats/', admin_dashboard_stats, name='admin_dashboard_stats'),
    path('admin/seo-dashboard/', seo_dashboard, name='seo_dashboard'),
    path('admin/site-backup/', site_backup_page, name='site_backup_page'),
    path('admin/site-backup/generate/', site_backup_generate, name='site_backup_generate'),
    path('admin/site-backup/download/', site_backup_download, name='site_backup_download'),
    path('admin/', admin.site.urls),

    # Rich-text editor
    path('ckeditor5/', include('django_ckeditor_5.urls')),

    # ── SEO ──────────────────────────────────────────────────────────────────
    # sitemap.xml: cached for 6 hours to reduce DB load
    path(
        'sitemap.xml',
        cache_page(60 * 60 * 6)(sitemap_view),
        {'sitemaps': all_sitemaps},
        name='django.contrib.sitemaps.views.sitemap',
    ),
    # robots.txt: no language prefix, always at root
    path('robots.txt', robots_txt, name='robots_txt'),
    path('ai.txt', ai_txt, name='ai_txt'),
    path('', include(('apps.persian_cms.urls', 'persian_cms'), namespace='persian_cms')),
    path(
        'fa-new/sitemap.xml',
        cache_page(60 * 60 * 6)(sitemap_view),
        {'sitemaps': persian_sitemaps},
        name='persian_sitemap',
    ),
    # Top-level alias for the Persian admin so its instance namespace
    # ("persian_admin") is reversible. The Unfold theme reverses URLs using the
    # admin site's name as the namespace; without this top-level mount that
    # bare "persian_admin:" namespace is unresolvable (it is otherwise only
    # reachable nested as "persian_cms:persian_admin"), causing HTTP 500 on
    # Persian admin changelist/change pages. Placed AFTER the persian_cms
    # include so request routing (incl. /fa-admin/dashboard/) is unchanged.
    path('fa-admin/', persian_admin_site.urls),
]

# ── Language-AWARE URLs ───────────────────────────────────────────────────────
# Public site pages receive a language prefix: /en/... and /tr/...
# prefix_default_language=False keeps English at the root path (/, /properties/,
# etc.) so all existing links continue to work without change.
urlpatterns += i18n_patterns(
    path('', include('core.urls')),
    path('properties/', include('properties.urls')),
    path('brochures/', include('brochures.urls')),
    prefix_default_language=False,
)

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
