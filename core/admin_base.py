"""
Admin theme base — single source of truth for admin class imports.

To reuse in a new project (e.g. MEDIVEST):
  1. Copy this file to core/admin_base.py in the new project.
  2. Copy the UNFOLD block from settings.py and update SITE_TITLE, SITE_HEADER,
     COLORS, and SIDEBAR navigation links.
  3. Add unfold packages to INSTALLED_APPS (see settings.py comment).
  4. All admin.py files already import from here — no further changes needed.

To switch back to plain Django admin (no theme):
  1. Replace the three unfold imports below with:
       from django.contrib.admin import ModelAdmin, TabularInline, StackedInline
  2. Remove 'unfold*' entries from INSTALLED_APPS.
  3. Remove the UNFOLD block from settings.py.
"""

from modeltranslation.admin import TranslationAdmin as _MTTranslationAdmin
from unfold.admin import ModelAdmin, TabularInline, StackedInline  # noqa: F401


class TranslationAdmin(_MTTranslationAdmin, ModelAdmin):
    """
    Combined admin base for models that have django-modeltranslation fields.

    Mixin order is intentional:
      _MTTranslationAdmin  — provides language-tab fieldset grouping and
                             language-aware form generation.
      ModelAdmin (unfold)  — provides the Unfold theme and UI enhancements.

    Usage::

        @admin.register(BlogPost)
        class BlogPostAdmin(RoleProtectedAdminMixin, TranslationAdmin):
            ...
    """


__all__ = [
    "ModelAdmin",
    "TabularInline",
    "StackedInline",
    "TranslationAdmin",
]
