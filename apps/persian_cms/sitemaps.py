from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from .models import PersianBlogPost, PersianPage, PersianSEOSettings


class PersianStaticSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"

    def items(self):
        routes = [
            ("persian_cms:fa_new_home", "home", "home"),
            ("persian_cms:fa_new_about", "about", "about"),
            ("persian_cms:fa_new_contact", "contact", "contact"),
            ("persian_cms:fa_new_golden_visa", "golden_visa", "golden_visa"),
            ("persian_cms:fa_new_blog_list", "blog", "blog"),
        ]
        available = []
        for name, page_type, page_key in routes:
            try:
                reverse(name)
                page = PersianPage.objects.filter(page_type=page_type, is_published=True).first()
                if page and page.noindex:
                    continue
                seo = PersianSEOSettings.for_page(page_key)
                if seo and seo.noindex:
                    continue
                if seo and not seo.robots_index:
                    continue
                available.append(name)
            except Exception:
                continue
        return available

    def location(self, item):
        return reverse(item)


class PersianBlogSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return PersianBlogPost.objects.filter(is_published=True, noindex=False).order_by("-updated_at")

    def lastmod(self, obj):
        return obj.updated_at

    def location(self, obj):
        return reverse("persian_cms:fa_new_blog_detail", kwargs={"slug": obj.slug})


class PersianPageSitemap(Sitemap):
    protocol = "https"
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        # Only custom pages here; the built-in routes are covered by
        # PersianStaticSitemap, so this avoids duplicate <loc> entries.
        return (
            PersianPage.objects
            .filter(is_published=True, noindex=False)
            .exclude(route_path="")
            .exclude(page_type__in=["home", "about", "contact", "golden_visa", "blog"])
        )

    def location(self, obj):
        return obj.route_path


persian_sitemaps = {
    "persian_static": PersianStaticSitemap,
    "persian_blog": PersianBlogSitemap,
    "persian_page": PersianPageSitemap,
}
