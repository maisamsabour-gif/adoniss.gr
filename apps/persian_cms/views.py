from __future__ import annotations

from typing import Any

from django.contrib.auth.decorators import user_passes_test
from django.db.utils import OperationalError, ProgrammingError
from django.http import HttpRequest, HttpResponse
from django.shortcuts import render
from django.utils import timezone

from core.views import fa_new_home as legacy_fa_new_home

from .models import (
    PersianBlogPost,
    PersianCTA,
    PersianFAQ,
    PersianFooterSettings,
    PersianMenuItem,
    PersianPage,
    PersianSEOSettings,
    PersianSection,
    GoldenVisaLandingPage,
)


def _is_staff(user) -> bool:
    return user.is_active and (user.is_staff or user.is_superuser)


def _absolute_url(request: HttpRequest, path: str) -> str:
    return request.build_absolute_uri(path)


def _seo_context(request: HttpRequest, page_key: str, fallback_title: str, fallback_description: str) -> dict[str, Any]:
    try:
        seo = PersianSEOSettings.for_page(page_key)
    except (OperationalError, ProgrammingError):
        seo = None
    title = fallback_title
    description = fallback_description
    canonical = _absolute_url(request, request.path)
    og_title = fallback_title
    og_description = fallback_description
    og_image = ""
    robots = "index, follow"
    if seo:
        title = seo.meta_title or title
        description = seo.meta_description or description
        canonical = seo.canonical_url or canonical
        og_title = seo.og_title or title
        og_description = seo.og_description or description
        og_image = seo.og_image.url if seo.og_image else ""
        robots = seo.robots_content
    robots_meta = robots.replace(" ", "")
    return {
        "meta_title": title,
        "meta_description": description,
        "canonical_url": canonical,
        "og_title": og_title,
        "og_description": og_description,
        "og_image": og_image,
        "robots_content": robots,
        "robots_meta": robots_meta,
    }


def _safe_first(queryset):
    try:
        return queryset.first()
    except (OperationalError, ProgrammingError):
        return None


def _safe_list(queryset):
    try:
        return list(queryset)
    except (OperationalError, ProgrammingError):
        return []


def _collect_home_context(request: HttpRequest) -> dict[str, Any]:
    page = _safe_first(PersianPage.objects.filter(page_type="home", is_published=True))
    sections = _safe_list(PersianSection.objects.filter(is_active=True).order_by("sort_order", "id"))
    menu_items = _safe_list(PersianMenuItem.objects.filter(is_active=True).order_by("sort_order", "id"))
    try:
        footer = PersianFooterSettings.get_settings()
    except (OperationalError, ProgrammingError):
        footer = None
    faq_items = _safe_list(PersianFAQ.objects.filter(is_active=True).order_by("sort_order", "id"))
    ctas = _safe_list(PersianCTA.objects.filter(is_active=True).order_by("sort_order", "id"))
    blog_posts = _safe_list(
        PersianBlogPost.objects
        .filter(is_published=True)
        .order_by("-published_at", "-id")[:8]
    )
    seo = _seo_context(
        request,
        "home",
        "آدونیس | اقامت یونان از مسیر سرمایه‌گذاری",
        "با پروژه‌های اختصاصی آدونیس در آتن، اقامت یونان و دسترسی به اروپا را برای خود و خانواده‌تان فراهم کنید.",
    )
    if page:
        seo.update({
            "meta_title": page.meta_title or seo["meta_title"],
            "meta_description": page.meta_description or seo["meta_description"],
            "canonical_url": page.canonical_url or seo["canonical_url"],
            "og_title": page.og_title or seo["og_title"],
            "og_description": page.og_description or seo["og_description"],
            "og_image": page.og_image.url if page.og_image else seo["og_image"],
            "robots_content": "noindex, follow" if page.noindex else seo["robots_content"],
        })
    return {
        "page": page,
        "sections": sections,
        "nav_items": menu_items,
        "footer": footer,
        "faq_items": faq_items,
        "cta_items": ctas,
        "blog_posts": blog_posts,
        **seo,
    }


def fa_new_home(request: HttpRequest) -> HttpResponse:
    # Use the full Persian homepage layout, driven by FaNew* models.
    return legacy_fa_new_home(request)


def fa_new_about(request: HttpRequest) -> HttpResponse:
    page = _safe_first(PersianPage.objects.filter(page_type="about", is_published=True))
    context = _seo_context(request, "about", "درباره آدونیس", "درباره آدونیس و خدمات مهاجرتی.")
    if page:
        context.update({
            "meta_title": page.meta_title or context["meta_title"],
            "meta_description": page.meta_description or context["meta_description"],
            "canonical_url": page.canonical_url or context["canonical_url"],
            "og_title": page.og_title or context["og_title"],
            "og_description": page.og_description or context["og_description"],
            "og_image": page.og_image.url if page.og_image else context["og_image"],
            "robots_content": "noindex, follow" if page.noindex else context["robots_content"],
        })
    context.update({"page": page})
    return render(request, "persian_cms/public/page.html", context)


def fa_new_contact(request: HttpRequest) -> HttpResponse:
    page = _safe_first(PersianPage.objects.filter(page_type="contact", is_published=True))
    context = _seo_context(request, "contact", "تماس با آدونیس", "راه‌های ارتباطی با تیم فارسی آدونیس.")
    if page:
        context.update({
            "meta_title": page.meta_title or context["meta_title"],
            "meta_description": page.meta_description or context["meta_description"],
            "canonical_url": page.canonical_url or context["canonical_url"],
            "og_title": page.og_title or context["og_title"],
            "og_description": page.og_description or context["og_description"],
            "og_image": page.og_image.url if page.og_image else context["og_image"],
            "robots_content": "noindex, follow" if page.noindex else context["robots_content"],
        })
    try:
        footer = PersianFooterSettings.get_settings()
    except (OperationalError, ProgrammingError):
        footer = None
    context.update({"page": page, "footer": footer})
    return render(request, "persian_cms/public/page.html", context)


def _fa_chrome(request):
    """Shared /fa-new/ header+footer context (nav, footer, settings)."""
    from core.models import FaNewSettings, FaNewSection, FaNavMenuItem, FaFooterSettings
    fa_settings = _safe_first(FaNewSettings.objects.all())
    nav_items = _safe_list(
        FaNavMenuItem.objects.filter(is_active=True).prefetch_related("children").order_by("order")
    )
    try:
        footer = FaFooterSettings.get_settings()
    except (OperationalError, ProgrammingError):
        footer = None
    sections = _safe_list(FaNewSection.objects.filter(is_active=True).order_by("order"))
    return {
        "settings": fa_settings, "nav_items": nav_items, "footer": footer,
        "sections": sections, "consult_anchor": "fa-section-consult",
        "projects_anchor": "fa-section-projects", "is_home": False,
    }


def fa_new_properties(request: HttpRequest) -> HttpResponse:
    """Persian properties landing (/fa-new/properties/) — served under the Persian
    nginx allowlist, with the Persian header/footer."""
    from .models import FaProperty
    
    qs = FaProperty.objects.filter(is_active=True).order_by("display_order", "-is_featured", "-created_at")
    items = []
    for p in qs:
        img = ""
        mi = p.main_image
        if mi:
            try:
                img = mi.url
            except Exception:
                img = ""
        items.append({
            "name": p.name or "",
            "slug": p.slug or "",
            "location": p.location or "",
            "price_label": p.price_label or (f"€{p.price:,.0f}" if p.price else ""),
            "area": p.area or "",
            "image_url": img,
            "is_featured": p.is_featured,
            "url": p.get_absolute_url(),
        })
    seo = _seo_context(request, "properties", "املاک و پروژه‌های آدونیس",
                       "پروژه‌های ساختمانی و املاک منتخب آدونیس در یونان برای سرمایه‌گذاری و اقامت.")
    ctx = {**_fa_chrome(request), "properties": items, **seo}
    return render(request, "fa_new/properties.html", ctx)


def fa_new_property_detail(request: HttpRequest, slug: str) -> HttpResponse:
    """Persian property detail page (/fa-new/properties/<slug>/)."""
    from django.http import Http404
    from .models import FaProperty
    
    prop = _safe_first(FaProperty.objects.filter(slug=slug, is_active=True))
    if not prop:
        raise Http404("پروژه پیدا نشد.")
    
    # Collect all images
    images = []
    for i in range(1, 16):
        img = getattr(prop, f'image_{i}', None)
        if img and img.name:
            images.append({
                'url': img.url,
                'alt': getattr(prop, f'image_{i}_alt', '') or prop.name,
                'caption': getattr(prop, f'image_{i}_caption', ''),
            })
    
    # Get related properties
    related = FaProperty.objects.filter(is_active=True).exclude(pk=prop.pk).order_by('-is_featured', 'display_order')[:4]
    
    # SEO
    seo = _seo_context(request, f"property:{slug}", prop.meta_title or prop.name, prop.meta_description or prop.short_description or "")
    seo.update({
        "meta_title": prop.meta_title or prop.name,
        "meta_description": prop.meta_description or prop.short_description or "",
        "canonical_url": prop.canonical_url or request.build_absolute_uri(),
        "og_title": prop.og_title or prop.name,
        "og_description": prop.og_description or prop.meta_description or prop.short_description,
        "og_image": prop.main_image.url if prop.main_image else None,
        "robots_content": "noindex, follow" if prop.noindex else "index, follow",
    })
    
    ctx = {
        **_fa_chrome(request),
        "property": prop,
        "images": images,
        "related_properties": related,
        **seo,
    }
    return render(request, "fa_new/property_detail.html", ctx)


def fa_new_custom_page(request: HttpRequest, slug: str) -> HttpResponse:
    """Render any published custom PersianPage at /fa-new/p/<slug>/ using the
    same header/footer chrome as the home page."""
    from django.http import Http404
    from core.models import FaNewSettings, FaNewSection, FaNavMenuItem, FaFooterSettings

    page = _safe_first(PersianPage.objects.filter(slug=slug, is_published=True))
    if not page:
        raise Http404("صفحه فارسی پیدا نشد.")

    fa_settings = _safe_first(FaNewSettings.objects.all())
    nav_items = _safe_list(
        FaNavMenuItem.objects.filter(is_active=True).prefetch_related("children").order_by("order")
    )
    try:
        footer = FaFooterSettings.get_settings()
    except (OperationalError, ProgrammingError):
        footer = None
    sections = _safe_list(FaNewSection.objects.filter(is_active=True).order_by("order"))

    seo = _seo_context(request, f"page:{slug}", page.title, page.meta_description or "")
    seo.update({
        "meta_title": page.meta_title or page.title,
        "meta_description": page.meta_description or seo.get("meta_description", ""),
        "canonical_url": page.canonical_url or seo.get("canonical_url"),
        "og_title": page.og_title or page.title,
        "og_description": page.og_description or page.meta_description,
        "og_image": page.og_image.url if page.og_image else seo.get("og_image"),
        "robots_content": "noindex, follow" if page.noindex else seo.get("robots_content", "index, follow"),
    })

    context = {
        "page": page,
        "settings": fa_settings,
        "nav_items": nav_items,
        "footer": footer,
        "sections": sections,
        "consult_anchor": "fa-section-consult",
        "projects_anchor": "fa-section-projects",
        "is_home": False,
        **seo,
    }
    return render(request, "fa_new/page.html", context)


def fa_new_golden_visa(request: HttpRequest) -> HttpResponse:
    """Golden Visa landing page using the new GoldenVisaLandingPage model."""
    from core.models import FaNewSettings, FaNavMenuItem, FaFooterSettings
    
    landing = _safe_first(GoldenVisaLandingPage.objects.filter(is_active=True))
    
    # Get settings for header/footer
    fa_new = FaNewSettings.get_settings()
    header_logo_url = fa_new.header_logo.url if fa_new.header_logo else None
    
    # Get navigation items
    nav_items = (
        FaNavMenuItem.objects
        .filter(is_active=True)
        .prefetch_related('children')
        .order_by('order')
    )
    
    # Get footer settings
    footer = FaFooterSettings.get_settings()
    
    context = _seo_context(
        request,
        "golden_visa",
        landing.title if landing else "گلدن ویزای یونان",
        landing.meta_description if landing else "همه مسیرهای دریافت گلدن ویزای یونان برای مخاطب فارسی.",
    )
    
    if landing:
        context.update({
            "meta_title": landing.title,
            "meta_description": landing.meta_description or context["meta_description"],
            "meta_keywords": landing.meta_keywords,
            "og_image": landing.og_image.url if landing.og_image else context["og_image"],
        })
    
    context.update({
        "landing": landing,
        "page": landing,
        "settings": fa_new,
        "fa": fa_new,
        "header_logo_url": header_logo_url,
        "nav_items": nav_items,
        "footer": footer,
    })
    return render(request, "persian_cms/public/golden_visa.html", context)


def fa_new_blog_list(request: HttpRequest) -> HttpResponse:
    posts = _safe_list(PersianBlogPost.objects.filter(is_published=True).order_by("-published_at", "-id"))
    context = _seo_context(request, "blog", "بلاگ فارسی آدونیس", "آخرین مقالات فارسی درباره اقامت یونان.")
    blog_page = _safe_first(PersianPage.objects.filter(page_type="blog", is_published=True))
    if blog_page:
        context.update({
            "meta_title": blog_page.meta_title or context["meta_title"],
            "meta_description": blog_page.meta_description or context["meta_description"],
            "canonical_url": blog_page.canonical_url or context["canonical_url"],
            "og_title": blog_page.og_title or context["og_title"],
            "og_description": blog_page.og_description or context["og_description"],
            "og_image": blog_page.og_image.url if blog_page.og_image else context["og_image"],
            "robots_content": "noindex, follow" if blog_page.noindex else context["robots_content"],
        })
    context.update({"posts": posts})
    return render(request, "persian_cms/public/blog_list.html", context)


def fa_new_blog_detail(request: HttpRequest, slug: str) -> HttpResponse:
    post = _safe_first(PersianBlogPost.objects.filter(slug=slug, is_published=True))
    title = post.title if post else "مقاله یافت نشد"
    description = post.excerpt if post and post.excerpt else "جزئیات مقاله فارسی."
    context = _seo_context(request, f"blog:{slug}", title, description)
    if post:
        context.update({
            "meta_title": post.meta_title or context["meta_title"],
            "meta_description": post.meta_description or context["meta_description"],
            "canonical_url": post.canonical_url or context["canonical_url"],
            "og_title": post.og_title or context["og_title"],
            "og_description": post.og_description or context["og_description"],
            "og_image": post.og_image.url if post.og_image else (
                post.featured_image.url if post.featured_image else context["og_image"]
            ),
            "robots_content": "noindex, follow" if post.noindex else context["robots_content"],
        })
    context.update({"post": post})
    return render(request, "persian_cms/public/blog_detail.html", context)


@user_passes_test(_is_staff, login_url="/admin/login/")
def fa_admin_dashboard(request: HttpRequest) -> HttpResponse:
    try:
        pages_count = PersianPage.objects.count()
        sections_count = PersianSection.objects.count()
        blogs_count = PersianBlogPost.objects.count()
        faqs_count = PersianFAQ.objects.count()
    except (OperationalError, ProgrammingError):
        pages_count = sections_count = blogs_count = faqs_count = 0
    context = {
        "stats": {
            "pages": pages_count,
            "sections": sections_count,
            "blogs": blogs_count,
            "faqs": faqs_count,
        },
        "updated_at": timezone.now(),
    }
    return render(request, "persian_cms/admin/dashboard.html", context)


def fa_new_robots_txt(request: HttpRequest) -> HttpResponse:
    sitemap_url = request.build_absolute_uri("/sitemap.xml")
    lines = [
        "User-agent: *",
        "Allow: /",
        "Disallow: /admin/",
        "Disallow: /persian-admin/",
        f"Sitemap: {sitemap_url}",
    ]
    return HttpResponse("\n".join(lines), content_type="text/plain; charset=utf-8")


def fa_new_consult_submit(request: HttpRequest) -> HttpResponse:
    """Handle Persian consultation form submission via AJAX.
    
    Saves to ContactSubmission model and sends Telegram notification.
    Returns JSON response for frontend handling.
    """
    import json
    from django.http import JsonResponse
    from django.views.decorators.csrf import csrf_exempt
    from django.views.decorators.http import require_POST
    from core.models import ContactSubmission
    from core.telegram import notify_new_contact
    
    if request.method != "POST":
        return JsonResponse({"ok": False, "error": "Method not allowed"}, status=405)
    
    try:
        # Parse JSON body or form data
        if request.content_type == "application/json":
            data = json.loads(request.body)
        else:
            data = request.POST
        
        # Extract fields
        first_name = (data.get("first_name") or "").strip()
        last_name = (data.get("last_name") or "").strip()
        full_name = f"{first_name} {last_name}".strip()
        phone = (data.get("phone") or "").strip()
        email = (data.get("email") or "").strip()
        message = (data.get("message") or "").strip()
        
        # Validation
        if not full_name:
            return JsonResponse({"ok": False, "error": "لطفاً نام و نام خانوادگی را وارد کنید"}, status=400)
        if not phone:
            return JsonResponse({"ok": False, "error": "لطفاً شماره تماس را وارد کنید"}, status=400)
        
        # Create submission
        submission = ContactSubmission.objects.create(
            full_name=full_name,
            phone=phone,
            email=email,
            message=message,
            request_type="general",
            source="fa_new_consult_modal",
        )
        
        # Send Telegram notification
        try:
            notify_new_contact(submission)
        except Exception:
            pass  # Don't fail the request if Telegram fails
        
        return JsonResponse({
            "ok": True,
            "message": "درخواست شما با موفقیت ثبت شد. کارشناسان ما به زودی با شما تماس خواهند گرفت.",
        })
        
    except json.JSONDecodeError:
        return JsonResponse({"ok": False, "error": "Invalid JSON"}, status=400)
    except Exception as e:
        return JsonResponse({"ok": False, "error": str(e)}, status=500)
