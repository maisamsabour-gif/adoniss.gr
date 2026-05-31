"""
BaseSEOAdmin — mixin for all content ModelAdmins.

Provides:
  - SEO Score panel in the change form (score + issues list)
  - Non-blocking SEO warnings on save (informational only — never prevents publish)
  - Bulk "SEO Report" action
"""
from __future__ import annotations

from django.contrib import admin, messages

from core.seo_audit import audit_object


# ── Standard SEO fieldset tuple (reuse in any ModelAdmin) ────────────────────

SEO_FIELDSET = (
    '🔍 SEO Settings', {
        'fields': (
            'seo_title', 'meta_description', 'focus_keyword',
            'canonical_url', 'og_image',
            'noindex', 'seo_status',
            'robots_index', 'robots_follow',
            'seo_allow_publish_override',
        ),
        'description': (
            'Google Preview updates live below as you type.<br>'
            '<em>SEO Title</em>: max 60 chars — leave blank to use page title.<br>'
            '<em>Meta Description</em>: max 160 chars.<br>'
            '<em>Focus Keyword</em>: primary keyword — used for scoring only.<br>'
            '<em>Allow indexing</em>: uncheck to add noindex meta tag.'
        ),
    }
)


def _filter_fieldsets(fieldsets, model, model_admin=None):
    """Remove fields from fieldsets that don't exist on the model or admin."""
    model_field_names = {f.name for f in model._meta.get_fields()}
    admin_attrs = set()
    if model_admin:
        admin_attrs = set(getattr(model_admin, 'readonly_fields', []))
        for attr in dir(model_admin):
            if not attr.startswith('_'):
                admin_attrs.add(attr)

    def _exists(name):
        return name in model_field_names or name in admin_attrs

    result = []
    for title, opts in fieldsets:
        fields = opts.get('fields', ())
        filtered = []
        for f in fields:
            if isinstance(f, (list, tuple)):
                kept = [x for x in f if _exists(x)]
                if kept:
                    filtered.append(tuple(kept) if len(kept) > 1 else kept[0])
            elif _exists(f):
                filtered.append(f)
        if filtered:
            new_opts = dict(opts)
            new_opts['fields'] = tuple(filtered)
            result.append((title, new_opts))
    return tuple(result)


class BaseSEOAdmin:
    """
    Mixin that injects the SEO score panel into the change form and surfaces
    SEO issues as non-blocking warnings in the admin message area.

    Publishing is NEVER blocked or reverted — all SEO feedback is advisory only.

    Usage:
        class MyAdmin(BaseSEOAdmin, ModelAdmin):
            ...
    """
    change_form_template = 'admin/change_form_seo.html'

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        return _filter_fieldsets(fieldsets, self.model, self)

    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        extra_context = extra_context or {}
        if object_id:
            try:
                obj = self.model.objects.get(pk=object_id)
                extra_context['seo_report'] = audit_object(obj)
            except self.model.DoesNotExist:
                pass
        return super().changeform_view(request, object_id, form_url, extra_context)

    def save_model(self, request, obj, form, change):
        """
        Save the model normally, then surface any SEO issues as advisory warnings.

        SEO issues do NOT block saving or publishing — they are informational only.
        The page is NEVER automatically reverted to unpublished.
        """
        super().save_model(request, obj, form, change)

        # After saving, run the audit and show warnings for any outstanding issues.
        # This is purely advisory — the save has already completed successfully.
        try:
            result = audit_object(obj)
        except Exception:
            return  # Never let the audit crash the admin save flow

        issues = result.critical + result.warnings
        if not issues:
            return

        lines = []
        for issue in result.critical:
            lines.append(f'• ❌ {issue}')
        for issue in result.warnings:
            lines.append(f'• ⚠️ {issue}')

        msg = (
            f'SEO score: {result.score}/100 — '
            f'{len(result.critical)} critical, {len(result.warnings)} warning(s). '
            'Page was saved normally. Please review the issues below:\n'
            + '\n'.join(lines)
        )
        messages.warning(request, msg)

    @admin.action(description='📊 Generate SEO Report')
    def seo_report_action(self, request, queryset):
        """Bulk action: show SEO summary for selected objects."""
        total = queryset.count()
        scores = []
        critical_count = 0
        for obj in queryset:
            result = audit_object(obj)
            scores.append(result.score)
            if result.has_critical:
                critical_count += 1
        avg = sum(scores) / len(scores) if scores else 0
        messages.info(
            request,
            f'SEO Report for {total} items: avg score {avg:.0f}/100, '
            f'{critical_count} with critical issues.'
        )
