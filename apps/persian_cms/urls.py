from django.urls import path, re_path
from django.views.generic import RedirectView

from . import views
from .admin_site import persian_admin_site


app_name = "persian_cms"


urlpatterns = [
    # Persian admin
    path("fa-admin/dashboard/", views.fa_admin_dashboard, name="fa_admin_dashboard"),
    path("fa-admin/", persian_admin_site.urls),
    path("persian-admin/", RedirectView.as_view(url="/admin/", permanent=False), name="persian_admin_redirect_root"),
    path(
        "persian-admin/<path:subpath>/",
        RedirectView.as_view(url="/admin/%(subpath)s", permanent=False),
        name="persian_admin_redirect",
    ),

    # ══════════════════════════════════════════════════════════════════════════════
    # ROOT URLs (adoniss.eu) — Main Persian site served at root
    # ══════════════════════════════════════════════════════════════════════════════
    path("", views.fa_new_home, name="home"),
    path("properties/", views.fa_new_properties, name="properties"),
    re_path(r"^properties/(?P<slug>[-\w\u200c]+)/$", views.fa_new_property_detail, name="property_detail"),
    path("about/", views.fa_new_about, name="about"),
    path("contact/", views.fa_new_contact, name="contact"),
    path("golden-visa/", views.fa_new_golden_visa, name="golden_visa"),
    re_path(r"^p/(?P<slug>[-\w\u200c]+)/$", views.fa_new_custom_page, name="custom_page"),
    path("blog/", views.fa_new_blog_list, name="blog_list"),
    re_path(r"^blog/(?P<slug>[-\w\u200c]+)/$", views.fa_new_blog_detail, name="blog_detail"),
    path("api/consult/", views.fa_new_consult_submit, name="consult_submit"),

    # ══════════════════════════════════════════════════════════════════════════════
    # Legacy /fa-new/ URLs — kept for backward compatibility
    # ══════════════════════════════════════════════════════════════════════════════
    path("fa-new/", views.fa_new_home, name="fa_new_home"),
    path("fa-new/properties/", views.fa_new_properties, name="fa_new_properties"),
    re_path(r"^fa-new/properties/(?P<slug>[-\w\u200c]+)/$", views.fa_new_property_detail, name="fa_new_property_detail"),
    path("fa-new/about/", views.fa_new_about, name="fa_new_about"),
    path("fa-new/contact/", views.fa_new_contact, name="fa_new_contact"),
    path("fa-new/golden-visa/", views.fa_new_golden_visa, name="fa_new_golden_visa"),
    re_path(r"^fa-new/p/(?P<slug>[-\w\u200c]+)/$", views.fa_new_custom_page, name="fa_new_custom_page"),
    path("fa-new/blog/", views.fa_new_blog_list, name="fa_new_blog_list"),
    re_path(r"^fa-new/blog/(?P<slug>[-\w\u200c]+)/$", views.fa_new_blog_detail, name="fa_new_blog_detail"),
    path("fa-new/robots.txt", views.fa_new_robots_txt, name="fa_new_robots_txt"),
    path("fa-new/api/consult/", views.fa_new_consult_submit, name="fa_new_consult_submit"),
]
