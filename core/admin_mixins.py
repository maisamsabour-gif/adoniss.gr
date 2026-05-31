from django.contrib import admin, messages
from django.template.response import TemplateResponse
from django.utils.translation import gettext_lazy as _

from core.audit import log_audit_event, model_snapshot
from core.rbac import has_any_role


class RoleProtectedAdminMixin:
    """
    Gates admin model access using Django model permissions as the single source
    of truth.  `allowed_roles` is kept for backward compatibility but is now an
    OPTIONAL additional allowlist: if it is set and the user is not in any of
    those roles, access is still granted provided the user holds the underlying
    Django permission.  This lets new groups (e.g. PropertyBlogEditor) work
    automatically once their Django permissions are assigned via seed_rbac_roles,
    without requiring changes to every ModelAdmin class.

    Access logic (first True wins):
      1. Superuser   → always allow
      2. User is in allowed_roles  → allow (legacy fast-path)
      3. User has the Django model permission  → allow
      4. Otherwise   → deny
    """

    allowed_roles = None  # optional role-name allowlist (legacy)

    def _has_access(self, request) -> bool:
        if request.user.is_superuser:
            return True
        # Legacy fast-path: role-name match bypasses the per-perm check.
        if self.allowed_roles and has_any_role(request.user, self.allowed_roles):
            return True
        # Permission-first: staff user with the right Django perm is always allowed,
        # regardless of which group assigned it.
        return request.user.is_staff and request.user.is_active

    def has_module_permission(self, request):
        return self._has_access(request) and super().has_module_permission(request)

    def has_view_permission(self, request, obj=None):
        return self._has_access(request) and super().has_view_permission(request, obj=obj)

    def has_change_permission(self, request, obj=None):
        return self._has_access(request) and super().has_change_permission(request, obj=obj)

    def has_add_permission(self, request):
        return self._has_access(request) and super().has_add_permission(request)

    def has_delete_permission(self, request, obj=None):
        return self._has_access(request) and super().has_delete_permission(request, obj=obj)


class SoftDeleteAdminMixin:
    actions = ["archive_selected", "restore_selected"]

    def get_queryset(self, request):
        qs = self.model.all_objects.all()
        ordering = self.get_ordering(request)
        if ordering:
            qs = qs.order_by(*ordering)
        return qs

    def has_delete_permission(self, request, obj=None):
        # Hard delete is blocked from admin UI for protected models.
        return False

    def delete_model(self, request, obj):
        before = model_snapshot(obj)
        obj.delete()
        after = model_snapshot(obj)
        log_audit_event(
            action="archive",
            obj=obj,
            user=request.user,
            request=request,
            before=before,
            after=after,
            metadata={"source": "admin_delete_button"},
        )

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            self.delete_model(request, obj)

    def _render_archive_restore_confirmation(self, request, queryset, action_name):
        model_name = self.model._meta.verbose_name_plural
        if action_name == "archive":
            title = _("Confirm archive")
            button_label = _("Archive selected")
            question = _("Are you sure you want to archive the selected %(model_name)s?") % {"model_name": model_name}
        else:
            title = _("Confirm restore")
            button_label = _("Restore selected")
            question = _("Are you sure you want to restore the selected %(model_name)s?") % {"model_name": model_name}

        context = {
            **self.admin_site.each_context(request),
            "opts": self.model._meta,
            "queryset": queryset,
            "action_name": action_name,
            "title": title,
            "button_label": button_label,
            "question": question,
            "action_checkbox_name": admin.helpers.ACTION_CHECKBOX_NAME,
        }
        return TemplateResponse(request, "admin/soft_delete_confirmation.html", context)

    @admin.action(description="Archive selected items (soft delete)")
    def archive_selected(self, request, queryset):
        if request.POST.get("confirm_action") != "yes":
            return self._render_archive_restore_confirmation(request, queryset, "archive")

        archived = 0
        for obj in queryset:
            if obj.deleted_at is None:
                before = model_snapshot(obj)
                obj.delete()
                after = model_snapshot(obj)
                log_audit_event(
                    action="archive",
                    obj=obj,
                    user=request.user,
                    request=request,
                    before=before,
                    after=after,
                    metadata={"source": "admin_bulk_action"},
                )
                archived += 1

        self.message_user(request, _(f"{archived} item(s) archived."), level=messages.SUCCESS)

    @admin.action(description="Restore selected archived items")
    def restore_selected(self, request, queryset):
        if request.POST.get("confirm_action") != "yes":
            return self._render_archive_restore_confirmation(request, queryset, "restore")

        restored = 0
        for obj in queryset:
            if obj.deleted_at is not None:
                before = model_snapshot(obj)
                obj.restore()
                after = model_snapshot(obj)
                log_audit_event(
                    action="restore",
                    obj=obj,
                    user=request.user,
                    request=request,
                    before=before,
                    after=after,
                    metadata={"source": "admin_bulk_action"},
                )
                restored += 1

        self.message_user(request, _(f"{restored} item(s) restored."), level=messages.SUCCESS)


class AuditAdminMixin:
    def save_model(self, request, obj, form, change):
        before = None
        if change:
            existing = self.model.all_objects.filter(pk=obj.pk).first() if hasattr(self.model, "all_objects") else self.model.objects.filter(pk=obj.pk).first()
            if existing:
                before = model_snapshot(existing)

        super().save_model(request, obj, form, change)

        action = "update" if change else "create"
        after = model_snapshot(obj)
        log_audit_event(
            action=action,
            obj=obj,
            user=request.user,
            request=request,
            before=before,
            after=after,
            metadata={"source": "admin_save"},
        )
