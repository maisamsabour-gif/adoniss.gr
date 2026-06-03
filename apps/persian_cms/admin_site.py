from django.http import HttpRequest, HttpResponse
from django.template.response import TemplateResponse
from django.urls import reverse, NoReverseMatch
from unfold.sites import UnfoldAdminSite


def _persian_sidebar_navigation(request):
    """Return sidebar navigation for Persian admin - NO English properties.
    
    All sections are collapsible (accordion-style) for cleaner UI.
    """
    return [
        # ═══════════════════════════════════════════════════════════════════
        # 1. تنظیمات صفحه اصلی
        # ═══════════════════════════════════════════════════════════════════
        {
            'title': '⚙️ تنظیمات صفحه اصلی',
            'separator': True,
            'collapsible': True,
            'items': [
                {'title': 'تنظیمات هیرو', 'icon': 'play_circle', 'link': '/fa-admin/core/fanewsettings/', 'has_permission': True},
                {'title': 'سکشن‌های صفحه', 'icon': 'view_agenda', 'link': '/fa-admin/core/fanewsection/', 'has_permission': True},
                {'title': 'تنظیمات فوتر', 'icon': 'bottom_navigation', 'link': '/fa-admin/core/fafootersettings/', 'has_permission': True},
            ],
        },
        # ═══════════════════════════════════════════════════════════════════
        # 2. منو و زیرمنوها
        # ═══════════════════════════════════════════════════════════════════
        {
            'title': '🧭 منو و صفحات',
            'separator': True,
            'collapsible': True,
            'items': [
                {'title': 'همه منوها', 'icon': 'menu', 'link': '/fa-admin/core/fanavmenuitem/', 'has_permission': True},
                {'title': 'افزودن آیتم منو', 'icon': 'add_circle', 'link': '/fa-admin/core/fanavmenuitem/add/', 'has_permission': True},
                {'title': 'همه صفحات', 'icon': 'description', 'link': '/fa-admin/persian_cms/persianpage/', 'has_permission': True},
                {'title': 'ساخت صفحه جدید', 'icon': 'note_add', 'link': '/fa-admin/persian_cms/persianpage/add/', 'has_permission': True},
            ],
        },
        # ═══════════════════════════════════════════════════════════════════
        # 3. پروژه‌های ساختمانی
        # ═══════════════════════════════════════════════════════════════════
        {
            'title': '🏗️ پروژه‌های ساختمانی',
            'separator': True,
            'collapsible': True,
            'items': [
                {'title': 'همه پروژه‌ها', 'icon': 'apartment', 'link': '/fa-admin/persian_cms/faproperty/', 'has_permission': True},
                {'title': 'افزودن پروژه', 'icon': 'add_home', 'link': '/fa-admin/persian_cms/faproperty/add/', 'has_permission': True},
                {'title': 'رسانه‌های پروژه‌ها', 'icon': 'photo_library', 'link': '/fa-admin/persian_cms/fapropertymedia/', 'has_permission': True},
            ],
        },
        # ═══════════════════════════════════════════════════════════════════
        # 4. محتوا و بلاگ
        # ═══════════════════════════════════════════════════════════════════
        {
            'title': '📝 محتوا و بلاگ',
            'separator': True,
            'collapsible': True,
            'items': [
                {'title': 'همه پست‌ها', 'icon': 'article', 'link': '/fa-admin/persian_cms/persianblogpost/', 'has_permission': True},
                {'title': 'نوشتن پست جدید', 'icon': 'post_add', 'link': '/fa-admin/persian_cms/persianblogpost/add/', 'has_permission': True},
                {'title': 'سوالات متداول', 'icon': 'quiz', 'link': '/fa-admin/persian_cms/persianfaq/', 'has_permission': True},
                {'title': 'رسانه‌ها', 'icon': 'perm_media', 'link': '/fa-admin/persian_cms/persianmediaasset/', 'has_permission': True},
            ],
        },
        # ═══════════════════════════════════════════════════════════════════
        # 5. لندینگ پیج‌ها
        # ═══════════════════════════════════════════════════════════════════
        {
            'title': '🚀 لندینگ پیج‌ها',
            'separator': True,
            'collapsible': True,
            'items': [
                {'title': 'همه لندینگ‌ها', 'icon': 'rocket_launch', 'link': '/fa-admin/persian_cms/goldenvisalandingpage/', 'has_permission': True},
                {'title': 'ساخت لندینگ جدید', 'icon': 'add_circle', 'link': '/fa-admin/persian_cms/goldenvisalandingpage/add/', 'has_permission': True},
            ],
        },
        # ═══════════════════════════════════════════════════════════════════
        # 7. پیام‌های دریافتی
        # ═══════════════════════════════════════════════════════════════════
        {
            'title': '📩 پیام‌های دریافتی',
            'separator': True,
            'collapsible': True,
            'items': [
                {'title': 'فرم‌های تماس', 'icon': 'mail', 'link': '/fa-admin/core/contactsubmission/', 'has_permission': True},
                {'title': 'درخواست مشاوره', 'icon': 'support_agent', 'link': '/fa-admin/core/consultrequest/', 'has_permission': True},
            ],
        },
        # ═══════════════════════════════════════════════════════════════════
        # 8. سئو و بهینه‌سازی
        # ═══════════════════════════════════════════════════════════════════
        {
            'title': '🔍 سئو و بهینه‌سازی',
            'separator': True,
            'collapsible': True,
            'items': [
                {'title': 'تنظیمات سئو', 'icon': 'travel_explore', 'link': '/fa-admin/persian_cms/persianseosettings/', 'has_permission': True},
                {'title': 'ریدایرکت‌ها', 'icon': 'alt_route', 'link': '/fa-admin/persian_cms/persianredirectmap/', 'has_permission': True},
            ],
        },
        # ═══════════════════════════════════════════════════════════════════
        # 9. کاربران و سطح دسترسی
        # ═══════════════════════════════════════════════════════════════════
        {
            'title': '👥 کاربران و دسترسی',
            'separator': True,
            'collapsible': True,
            'items': [
                {'title': 'همه کاربران', 'icon': 'group', 'link': '/admin/auth/user/', 'has_permission': True},
                {'title': 'افزودن کاربر', 'icon': 'person_add', 'link': '/admin/auth/user/add/', 'has_permission': True},
                {'title': 'گروه‌های دسترسی', 'icon': 'admin_panel_settings', 'link': '/admin/auth/group/', 'has_permission': True},
            ],
        },
        # ═══════════════════════════════════════════════════════════════════
        # پیش‌نمایش سایت (همیشه باز)
        # ═══════════════════════════════════════════════════════════════════
        {
            'title': '👁 پیش‌نمایش سایت',
            'separator': True,
            'collapsible': False,
            'items': [
                {'title': 'صفحه اصلی', 'icon': 'home', 'link': '/fa-new/', 'has_permission': True},
                {'title': 'صفحه املاک', 'icon': 'apartment', 'link': '/fa-new/properties/', 'has_permission': True},
                {'title': 'صفحه بلاگ', 'icon': 'article', 'link': '/fa-new/blog/', 'has_permission': True},
            ],
        },
    ]


class PersianAdminSite(UnfoldAdminSite):
    """Persian-only admin site - completely separate from English admin.
    
    This admin site has its own sidebar navigation that only shows
    Persian models (FaProperty, etc.) and never links to English properties.
    """
    site_header = "ADONIS Persian CMS"
    site_title = "پنل مدیریت فارسی آدونیس"
    index_title = "داشبورد مدیریت محتوای فارسی"
    site_url = "/fa-new/"
    enable_nav_sidebar = True
    login_template = "persian_cms/admin/login.html"
    logout_template = "persian_cms/admin/logout.html"
    index_template = "persian_cms/admin/index.html"
    settings_name = "UNFOLD_PERSIAN"

    class Media:
        css = {"all": ("css/persian-admin.css",)}

    def each_context(self, request: HttpRequest):
        ctx = super().each_context(request)
        ctx["is_rtl"] = True
        ctx["is_nav_sidebar_enabled"] = True
        ctx["is_popup"] = False
        # Force custom sidebar navigation without English properties
        sidebar_nav = _persian_sidebar_navigation(request)
        ctx["navigation"] = sidebar_nav
        ctx["sidebar_navigation"] = sidebar_nav
        # Provide logout URL for this admin site (persian_admin:logout)
        try:
            ctx["logout_url"] = reverse(f"{self.name}:logout")
        except NoReverseMatch:
            ctx["logout_url"] = reverse("admin:logout")
        # Provide password_change URL for this admin site
        try:
            ctx["password_change_url"] = reverse(f"{self.name}:password_change")
        except NoReverseMatch:
            ctx["password_change_url"] = reverse("admin:password_change")
        return ctx
    
    def get_sidebar_list(self, request):
        """Override to return only Persian navigation items."""
        return _persian_sidebar_navigation(request)
    
    def has_permission(self, request):
        """Check if user has permission to access this admin site."""
        return request.user.is_active and request.user.is_staff

    def index(self, request: HttpRequest, extra_context=None) -> HttpResponse:
        cards = [
            # ── املاک فارسی (جدا از انگلیسی) ──
            {"title": "🏠 پروژه‌های ملکی فارسی", "url": reverse("persian_cms:persian_admin:persian_cms_faproperty_changelist")},
            {"title": "🖼️ رسانه‌های املاک", "url": reverse("persian_cms:persian_admin:persian_cms_fapropertymedia_changelist")},
            # ── صفحه اصلی و تنظیمات ──
            {"title": "صفحه اصلی (طراحی کامل)", "url": reverse("persian_cms:persian_admin:core_fanewsection_changelist")},
            {"title": "تنظیمات هیرو / هدر", "url": reverse("persian_cms:persian_admin:core_fanewsettings_changelist")},
            {"title": "منوی هدر (fa-new)", "url": reverse("persian_cms:persian_admin:core_fanavmenuitem_changelist")},
            {"title": "فوتر (fa-new)", "url": reverse("persian_cms:persian_admin:core_fafootersettings_changelist")},
            # ── محتوا ──
            {"title": "مدیریت صفحه اصلی", "url": reverse("persian_cms:persian_admin:persian_cms_persianpage_changelist")},
            {"title": "مدیریت بلاگ فارسی", "url": reverse("persian_cms:persian_admin:persian_cms_persianblogpost_changelist")},
            {"title": "تنظیمات سئو", "url": reverse("persian_cms:persian_admin:persian_cms_persianseosettings_changelist")},
            {"title": "منوها", "url": reverse("persian_cms:persian_admin:persian_cms_persianmenuitem_changelist")},
            {"title": "فوتر", "url": reverse("persian_cms:persian_admin:persian_cms_persianfootersettings_changelist")},
            {"title": "رسانه‌ها", "url": reverse("persian_cms:persian_admin:persian_cms_persianmediaasset_changelist")},
            {"title": "سوالات متداول", "url": reverse("persian_cms:persian_admin:persian_cms_persianfaq_changelist")},
            {"title": "دکمه‌ها و CTA", "url": reverse("persian_cms:persian_admin:persian_cms_persiancta_changelist")},
        ]
        context = {
            **self.each_context(request),
            "title": self.index_title,
            "cards": cards,
            "app_list": self.get_app_list(request),
            **(extra_context or {}),
        }
        request.current_app = self.name
        return TemplateResponse(request, self.index_template, context)


persian_admin_site = PersianAdminSite(name="persian_admin")
