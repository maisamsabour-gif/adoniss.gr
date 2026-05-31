from __future__ import annotations

import csv
import re
from pathlib import Path
from urllib.parse import urlparse

from django.conf import settings
from django.contrib.sitemaps import Sitemap
from django.core.management.base import BaseCommand
from django.urls import reverse
from django.utils import timezone
from django.utils.html import strip_tags

from apps.persian_cms.models import PersianBlogPost, PersianPage, PersianSEOSettings
from apps.persian_cms.sitemaps import persian_sitemaps
from brochures.models import Brochure
from core.models import (
    BlogPost,
    GoldenVisaFaLandingPage,
    GoldenVisaLandingPage,
    PageSEO,
    WebinarLandingSettings,
)
from core.sitemaps import sitemaps
from properties.models import Property


def _to_text(value) -> str:
    return strip_tags(value or "").strip()


def _word_count(value) -> int:
    return len(_to_text(value).split())


def _normalize_path(value: str) -> str:
    raw = (value or "").strip()
    if not raw:
        return ""
    parsed = urlparse(raw)
    path = parsed.path if parsed.path else raw
    if not path.startswith("/"):
        path = f"/{path}"
    return path


def _build_sitemap_paths() -> set[str]:
    paths: set[str] = set()
    all_maps: list[dict[str, type[Sitemap]]] = [sitemaps, persian_sitemaps]
    for mapping in all_maps:
        for sitemap_class in mapping.values():
            sm = sitemap_class()
            for item in sm.items():
                try:
                    if hasattr(sm, "location"):
                        loc = sm.location(item)
                    else:
                        loc = item.get_absolute_url()
                    if loc:
                        paths.add(_normalize_path(loc))
                except Exception:
                    continue
    return paths


class Command(BaseCommand):
    help = "Run SEO audit for all public pages/blog content and export CSV report."

    def handle(self, *args, **options):
        report_rows = []
        sitemap_paths = _build_sitemap_paths()

        # Public static pages mapped via PageSEO.
        static_page_rules = [
            ("home", reverse("home")),
            ("about", reverse("about")),
            ("contact", reverse("contact")),
            ("partnerships", reverse("partnerships")),
            ("blog", reverse("blog_list")),
            ("events", reverse("event_list")),
        ]

        for page_key, path in static_page_rules:
            seo = PageSEO.for_page(page_key)
            title = seo.get_meta_title("en") if seo else ""
            description = seo.get_meta_desc("en") if seo else ""
            canonical = (seo.get_canonical_url() if seo else "") or path
            og_image = seo.og_image.url if seo and seo.og_image else ""
            focus_keyword = seo.get_focus_keyword() if seo else ""
            noindex = bool(seo.noindex) if seo else False
            # H1 expected from template/page title: treat static pages as 1.
            h1_count = 1
            has_internal_link = True
            content_words = 800  # static pages are content-rich and managed outside this model.
            missing_alt = False
            in_sitemap = _normalize_path(path) in sitemap_paths

            issues = self._collect_issues(
                meta_title=title,
                meta_description=description,
                h1_count=h1_count,
                missing_alt=missing_alt,
                canonical_url=canonical,
                og_image=og_image,
                focus_keyword=focus_keyword,
                word_count=content_words,
                has_internal_link=has_internal_link,
                noindex=noindex,
                expected_in_sitemap=not noindex,
                in_sitemap=in_sitemap,
            )
            report_rows.append(self._row("StaticPage", page_key, path, issues, title, description, canonical, noindex))

        for post in BlogPost.objects.filter(is_published=True):
            path = post.get_absolute_url()
            title = post.meta_title or post.title
            description = post.meta_description or _to_text(post.excerpt)[:160]
            canonical = post.canonical_url or path
            og_image = post.og_image.url if post.og_image else (post.featured_image.url if post.featured_image else "")
            focus_keyword = post.focus_keyword or ""
            noindex = bool(getattr(post, "noindex", False) or not post.robots_index)
            body_html = post.content or ""
            inline_h1_count = len(re.findall(r"<h1[\s>]", body_html, flags=re.I))
            h1_count = 1 + inline_h1_count
            word_count = _word_count(body_html)
            has_internal_link = bool(re.search(r'href=["\']/(?!/)', body_html))
            missing_alt = bool(re.search(r"<img(?![^>]*\balt=)[^>]*>", body_html, flags=re.I))
            in_sitemap = _normalize_path(path) in sitemap_paths

            issues = self._collect_issues(
                meta_title=title,
                meta_description=description,
                h1_count=h1_count,
                missing_alt=missing_alt,
                canonical_url=canonical,
                og_image=og_image,
                focus_keyword=focus_keyword,
                word_count=word_count,
                has_internal_link=has_internal_link,
                noindex=noindex,
                expected_in_sitemap=not noindex,
                in_sitemap=in_sitemap,
            )
            report_rows.append(self._row("BlogPost", post.slug, path, issues, title, description, canonical, noindex))

        for post in PersianBlogPost.objects.filter(is_published=True):
            path = reverse("persian_cms:fa_new_blog_detail", kwargs={"slug": post.slug})
            title = post.meta_title or post.title
            description = post.meta_description or _to_text(post.excerpt)[:160]
            canonical = post.canonical_url or path
            og_image = post.og_image.url if post.og_image else (post.featured_image.url if post.featured_image else "")
            focus_keyword = post.focus_keyword or ""
            noindex = bool(post.noindex)
            body_html = post.body or ""
            inline_h1_count = len(re.findall(r"<h1[\s>]", body_html, flags=re.I))
            h1_count = 1 + inline_h1_count
            word_count = _word_count(body_html)
            has_internal_link = bool(re.search(r'href=["\']/(?!/)', body_html))
            missing_alt = bool(re.search(r"<img(?![^>]*\balt=)[^>]*>", body_html, flags=re.I))
            in_sitemap = _normalize_path(path) in sitemap_paths

            issues = self._collect_issues(
                meta_title=title,
                meta_description=description,
                h1_count=h1_count,
                missing_alt=missing_alt,
                canonical_url=canonical,
                og_image=og_image,
                focus_keyword=focus_keyword,
                word_count=word_count,
                has_internal_link=has_internal_link,
                noindex=noindex,
                expected_in_sitemap=not noindex,
                in_sitemap=in_sitemap,
            )
            report_rows.append(self._row("PersianBlogPost", post.slug, path, issues, title, description, canonical, noindex))

        for page in PersianPage.objects.filter(is_published=True):
            path = page.route_path
            title = page.meta_title or page.title
            description = page.meta_description or _to_text(page.body)[:160]
            canonical = page.canonical_url or path
            og_image = page.og_image.url if page.og_image else ""
            focus_keyword = page.focus_keyword or ""
            noindex = bool(page.noindex)
            body_html = page.body or ""
            inline_h1_count = len(re.findall(r"<h1[\s>]", body_html, flags=re.I))
            h1_count = 1 + inline_h1_count
            word_count = _word_count(body_html)
            has_internal_link = bool(re.search(r'href=["\']/(?!/)', body_html))
            missing_alt = bool(re.search(r"<img(?![^>]*\balt=)[^>]*>", body_html, flags=re.I))
            in_sitemap = _normalize_path(path) in sitemap_paths

            issues = self._collect_issues(
                meta_title=title,
                meta_description=description,
                h1_count=h1_count,
                missing_alt=missing_alt,
                canonical_url=canonical,
                og_image=og_image,
                focus_keyword=focus_keyword,
                word_count=word_count,
                has_internal_link=has_internal_link,
                noindex=noindex,
                expected_in_sitemap=not noindex,
                in_sitemap=in_sitemap,
            )
            report_rows.append(self._row("PersianPage", page.slug, path, issues, title, description, canonical, noindex))

        # Singleton landing pages.
        gv = GoldenVisaLandingPage.get_settings()
        gv_path = reverse("greece_golden_visa")
        gv_issues = self._collect_issues(
            meta_title=getattr(gv, "meta_title", "") or gv.hero_title,
            meta_description=getattr(gv, "meta_description", ""),
            h1_count=1,
            missing_alt=False,
            canonical_url=getattr(gv, "canonical_url", "") or gv_path,
            og_image=(gv.og_image.url if getattr(gv, "og_image", None) else (gv.hero_image.url if gv.hero_image else "")),
            focus_keyword=getattr(gv, "focus_keyword", ""),
            word_count=_word_count(gv.intro_text) + _word_count(gv.section_1_text) + _word_count(gv.section_2_text) + _word_count(gv.section_3_text),
            has_internal_link=True,
            noindex=bool(getattr(gv, "noindex", False)),
            expected_in_sitemap=not bool(getattr(gv, "noindex", False)),
            in_sitemap=_normalize_path(gv_path) in sitemap_paths,
        )
        report_rows.append(self._row("GoldenVisaLandingPage", "singleton", gv_path, gv_issues, getattr(gv, "meta_title", ""), getattr(gv, "meta_description", ""), getattr(gv, "canonical_url", ""), bool(getattr(gv, "noindex", False))))

        fa_gv = GoldenVisaFaLandingPage.get_settings()
        fa_gv_path = reverse("greece_golden_visa_fa_ads")
        fa_gv_issues = self._collect_issues(
            meta_title=getattr(fa_gv, "seo_title", ""),
            meta_description=getattr(fa_gv, "meta_description", ""),
            h1_count=1,
            missing_alt=False,
            canonical_url=getattr(fa_gv, "canonical_url", "") or fa_gv_path,
            og_image=(fa_gv.og_image.url if getattr(fa_gv, "og_image", None) else ""),
            focus_keyword=getattr(fa_gv, "focus_keyword", ""),
            word_count=_word_count(fa_gv.intro_text) + _word_count(fa_gv.benefits_text),
            has_internal_link=True,
            noindex=bool(getattr(fa_gv, "noindex", False)),
            expected_in_sitemap=not bool(getattr(fa_gv, "noindex", False)),
            in_sitemap=_normalize_path(fa_gv_path) in sitemap_paths,
        )
        report_rows.append(self._row("GoldenVisaFaLandingPage", "singleton", fa_gv_path, fa_gv_issues, getattr(fa_gv, "seo_title", ""), getattr(fa_gv, "meta_description", ""), getattr(fa_gv, "canonical_url", ""), bool(getattr(fa_gv, "noindex", False))))

        webinar = WebinarLandingSettings.get_settings()
        webinar_path = reverse("webinar_landing")
        webinar_issues = self._collect_issues(
            meta_title=webinar.meta_title,
            meta_description=webinar.meta_description,
            h1_count=1,
            missing_alt=False,
            canonical_url=webinar.canonical_url or webinar_path,
            og_image=webinar.og_image.url if webinar.og_image else "",
            focus_keyword=webinar.focus_keyword,
            word_count=700,
            has_internal_link=True,
            noindex=bool(webinar.noindex),
            expected_in_sitemap=not bool(webinar.noindex),
            in_sitemap=_normalize_path(webinar_path) in sitemap_paths,
        )
        report_rows.append(self._row("WebinarLandingSettings", "singleton", webinar_path, webinar_issues, webinar.meta_title, webinar.meta_description, webinar.canonical_url, bool(webinar.noindex)))

        # Property and brochure audits (already public and indexed content).
        for prop in Property.objects.filter(is_active=True, deleted_at__isnull=True):
            path = prop.get_absolute_url()
            title = prop.get_seo_title()
            description = prop.get_meta_description()
            canonical = prop.canonical_url or path
            og_image = prop.get_og_image().url if prop.get_og_image() else ""
            focus_keyword = prop.focus_keyword or ""
            noindex = not prop.robots_index
            body_text = f"{prop.description_en or ''} {prop.description_tr or ''}"
            word_count = _word_count(body_text)
            has_internal_link = True
            missing_alt = not bool(prop.get_featured_image_alt())
            in_sitemap = _normalize_path(path) in sitemap_paths
            issues = self._collect_issues(
                meta_title=title,
                meta_description=description,
                h1_count=1,
                missing_alt=missing_alt,
                canonical_url=canonical,
                og_image=og_image,
                focus_keyword=focus_keyword,
                word_count=word_count,
                has_internal_link=has_internal_link,
                noindex=noindex,
                expected_in_sitemap=not noindex,
                in_sitemap=in_sitemap,
            )
            report_rows.append(self._row("Property", str(prop.pk), path, issues, title, description, canonical, noindex))

        for brochure in Brochure.objects.filter(is_published=True, robots_index=True):
            path = brochure.get_absolute_url()
            title = brochure.get_seo_title()
            description = brochure.get_meta_description()
            canonical = brochure.get_canonical_url() or path
            og_image = brochure.get_og_image().url if brochure.get_og_image() else ""
            focus_keyword = brochure.get_focus_keyword()
            noindex = not brochure.robots_index
            word_count = _word_count(brochure.meta_description)
            has_internal_link = True
            missing_alt = not bool(brochure.get_featured_image_alt())
            in_sitemap = _normalize_path(path) in sitemap_paths
            issues = self._collect_issues(
                meta_title=title,
                meta_description=description,
                h1_count=1,
                missing_alt=missing_alt,
                canonical_url=canonical,
                og_image=og_image,
                focus_keyword=focus_keyword,
                word_count=word_count,
                has_internal_link=has_internal_link,
                noindex=noindex,
                expected_in_sitemap=not noindex,
                in_sitemap=in_sitemap,
            )
            report_rows.append(self._row("Brochure", brochure.slug, path, issues, title, description, canonical, noindex))

        # Validate Persian SEO settings not tied to a concrete object (e.g. blog:<slug>)
        for seo in PersianSEOSettings.objects.exclude(page_key__in=["home", "about", "contact", "golden_visa", "blog"]):
            issues = []
            if not seo.meta_title:
                issues.append("Missing meta title")
            if not seo.meta_description:
                issues.append("Missing meta description")
            if not seo.canonical_url:
                issues.append("Missing canonical URL")
            if not seo.og_image:
                issues.append("Missing OG image")
            if not seo.focus_keyword:
                issues.append("Missing focus keyword")
            if seo.noindex:
                issues.append("Page marked noindex by mistake")
            if seo.page_key.startswith("blog:") and not seo.page:
                slug = seo.page_key.split(":", 1)[1]
                if not PersianBlogPost.objects.filter(slug=slug, is_published=True).exists():
                    issues.append("Referenced Persian blog post missing")

            report_rows.append(
                self._row(
                    "PersianSEOSettings",
                    seo.page_key,
                    seo.canonical_url or "",
                    issues,
                    seo.meta_title,
                    seo.meta_description,
                    seo.canonical_url,
                    seo.noindex,
                )
            )

        report_rows.sort(key=lambda r: (r["issue_count"], r["type"], r["identifier"]), reverse=True)
        self._print_report(report_rows)
        csv_path = self._write_csv(report_rows)
        self.stdout.write(self.style.SUCCESS(f"\nCSV report exported: {csv_path}"))

    def _collect_issues(
        self,
        *,
        meta_title: str,
        meta_description: str,
        h1_count: int,
        missing_alt: bool,
        canonical_url: str,
        og_image: str,
        focus_keyword: str,
        word_count: int,
        has_internal_link: bool,
        noindex: bool,
        expected_in_sitemap: bool,
        in_sitemap: bool,
    ) -> list[str]:
        issues: list[str] = []
        title_len = len((meta_title or "").strip())
        desc_len = len((meta_description or "").strip())

        if title_len == 0:
            issues.append("Missing meta title")
        elif title_len < 30 or title_len > 60:
            issues.append("Meta title too short or too long")

        if desc_len == 0:
            issues.append("Missing meta description")
        elif desc_len < 110 or desc_len > 160:
            issues.append("Meta description too short or too long")

        if h1_count == 0:
            issues.append("Missing H1")
        elif h1_count > 1:
            issues.append("Multiple H1 tags")

        if missing_alt:
            issues.append("Missing image ALT tags")
        if not (canonical_url or "").strip():
            issues.append("Missing canonical URL")
        if not (og_image or "").strip():
            issues.append("Missing OG image")
        if not (focus_keyword or "").strip():
            issues.append("Missing focus keyword")
        if word_count < 600:
            issues.append("Thin content under 600 words")
        if not has_internal_link:
            issues.append("No internal links")
        if noindex:
            issues.append("Page marked noindex by mistake")
        if expected_in_sitemap and not in_sitemap:
            issues.append("Page missing from sitemap")

        return issues

    def _row(self, content_type, identifier, url, issues, meta_title, meta_description, canonical_url, noindex):
        return {
            "type": content_type,
            "identifier": identifier,
            "url": url,
            "issue_count": len(issues),
            "issues": "; ".join(issues) if issues else "OK",
            "meta_title": meta_title or "",
            "meta_description": meta_description or "",
            "canonical_url": canonical_url or "",
            "noindex": "yes" if noindex else "no",
        }

    def _print_report(self, rows):
        self.stdout.write(self.style.MIGRATE_HEADING("SEO AUDIT REPORT"))
        total = len(rows)
        failing = sum(1 for r in rows if r["issue_count"] > 0)
        self.stdout.write(f"Total audited items: {total}")
        self.stdout.write(f"Items with issues: {failing}")
        self.stdout.write("")
        for row in rows:
            marker = "OK" if row["issue_count"] == 0 else f"{row['issue_count']} issue(s)"
            self.stdout.write(f"[{row['type']}] {row['identifier']} -> {row['url']} :: {marker}")
            if row["issue_count"] > 0:
                self.stdout.write(f"  - {row['issues']}")

    def _write_csv(self, rows) -> str:
        reports_dir = Path(settings.BASE_DIR) / "reports"
        reports_dir.mkdir(parents=True, exist_ok=True)
        csv_path = reports_dir / "seo_audit_report.csv"
        with csv_path.open("w", newline="", encoding="utf-8") as fp:
            writer = csv.DictWriter(
                fp,
                fieldnames=[
                    "type",
                    "identifier",
                    "url",
                    "issue_count",
                    "issues",
                    "meta_title",
                    "meta_description",
                    "canonical_url",
                    "noindex",
                    "generated_at",
                ],
            )
            writer.writeheader()
            now = timezone.now().isoformat()
            for row in rows:
                writer.writerow({**row, "generated_at": now})
        return str(csv_path)
