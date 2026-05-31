"""
SEO Site Audit Dashboard — custom admin view.

URL: /admin/seo-dashboard/
Shows aggregate SEO health across all public content models.
"""
from __future__ import annotations

from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import render

from apps.persian_cms.models import PersianBlogPost, PersianPage
from core.seo_audit import audit_object
from core.sitemaps import sitemaps
from apps.persian_cms.sitemaps import persian_sitemaps


def _get_all_content_objects():
    """Yield (model_label, obj) for every published content object."""
    from core.models import BlogPost, Event, GoldenVisaCard, GoldenVisaLandingPage, Testimonial
    from properties.models import Property
    from brochures.models import Brochure

    for obj in BlogPost.objects.filter(is_published=True):
        yield 'BlogPost', obj
    for obj in Property.objects.filter(is_active=True, deleted_at__isnull=True):
        yield 'Property', obj
    for obj in Event.objects.filter(is_active=True):
        yield 'Event', obj
    for obj in GoldenVisaCard.objects.filter(is_active=True):
        yield 'GoldenVisaCard', obj
    for obj in Testimonial.objects.filter(is_active=True):
        yield 'Testimonial', obj
    for obj in Brochure.objects.filter(is_published=True):
        yield 'Brochure', obj
    try:
        gv = GoldenVisaLandingPage.objects.get(pk=1)
        if gv.is_published:
            yield 'LandingPage', gv
    except GoldenVisaLandingPage.DoesNotExist:
        pass

    for obj in PersianPage.objects.filter(is_published=True):
        yield 'PersianPage', obj
    for obj in PersianBlogPost.objects.filter(is_published=True):
        yield 'PersianBlogPost', obj


def _build_sitemap_paths():
    paths = set()
    all_maps = [sitemaps, persian_sitemaps]
    for mapping in all_maps:
        for sitemap_class in mapping.values():
            sm = sitemap_class()
            for item in sm.items():
                try:
                    loc = sm.location(item) if hasattr(sm, "location") else item.get_absolute_url()
                    if not loc:
                        continue
                    if not loc.startswith("/"):
                        loc = "/" + loc
                    paths.add(loc)
                except Exception:
                    continue
    return paths


@staff_member_required
def seo_dashboard(request):
    rows = []
    scores = []
    critical_count = 0
    seo_ready = 0
    missing_desc = []
    missing_title = []
    missing_alt = []
    missing_h1 = []
    thin_pages = []
    noindex_pages = []
    missing_from_sitemap = []
    titles_seen: dict[str, list] = {}
    descs_seen: dict[str, list] = {}
    sitemap_paths = _build_sitemap_paths()

    for model_label, obj in _get_all_content_objects():
        result = audit_object(obj)
        name = str(obj)[:60]
        url = obj.get_absolute_url() if hasattr(obj, 'get_absolute_url') else ''

        scores.append(result.score)
        if result.has_critical:
            critical_count += 1
        if result.score >= 80 and not result.has_critical:
            seo_ready += 1

        seo_title = obj.get_seo_title() if hasattr(obj, 'get_seo_title') else ''
        meta_desc = obj.get_meta_description() if hasattr(obj, 'get_meta_description') else ''
        h1 = obj.get_h1() if hasattr(obj, 'get_h1') else ''
        robots_index = getattr(obj, "robots_index", True)
        explicit_noindex = getattr(obj, "noindex", False)

        if not seo_title:
            missing_title.append({'type': model_label, 'name': name, 'url': url})
        if not meta_desc:
            missing_desc.append({'type': model_label, 'name': name, 'url': url})
        if not h1:
            missing_h1.append({'type': model_label, 'name': name, 'url': url})
        if explicit_noindex or not robots_index:
            noindex_pages.append({'type': model_label, 'name': name, 'url': url})

        body_words = 0
        if hasattr(obj, 'get_body_text'):
            body_words = len((obj.get_body_text() or '').split())
        if body_words and body_words < 600:
            thin_pages.append({'type': model_label, 'name': name, 'url': url, 'words': body_words})

        if url and url not in sitemap_paths:
            missing_from_sitemap.append({'type': model_label, 'name': name, 'url': url})

        # ALT check
        if hasattr(obj, 'get_all_image_fields'):
            for field_name, img, alt in obj.get_all_image_fields():
                if img and not alt:
                    missing_alt.append({'type': model_label, 'name': name, 'field': field_name, 'url': url})

        # Duplicate detection
        if seo_title:
            titles_seen.setdefault(seo_title.lower().strip(), []).append({'type': model_label, 'name': name, 'url': url})
        if meta_desc:
            descs_seen.setdefault(meta_desc.lower().strip()[:100], []).append({'type': model_label, 'name': name, 'url': url})

        rows.append({
            'type': model_label,
            'name': name,
            'url': url,
            'score': result.score,
            'critical_count': len(result.critical),
            'warning_count': len(result.warnings),
            'critical': result.critical,
            'warnings': result.warnings,
        })

    # Sort worst-first
    rows.sort(key=lambda r: r['score'])

    avg_score = sum(scores) / len(scores) if scores else 0
    dup_titles = {k: v for k, v in titles_seen.items() if len(v) > 1}
    dup_descs = {k: v for k, v in descs_seen.items() if len(v) > 1}

    context = {
        'title': 'SEO Site Audit',
        'total_pages': len(rows),
        'seo_ready': seo_ready,
        'avg_score': round(avg_score),
        'critical_count': critical_count,
        'rows': rows,
        'missing_title': missing_title,
        'missing_desc': missing_desc,
        'missing_h1': missing_h1,
        'missing_alt': missing_alt,
        'thin_pages': thin_pages,
        'noindex_pages': noindex_pages,
        'missing_from_sitemap': missing_from_sitemap,
        'dup_titles': dup_titles,
        'dup_descs': dup_descs,
    }
    return render(request, 'admin/seo_dashboard.html', context)
