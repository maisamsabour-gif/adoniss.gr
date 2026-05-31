"""Professional User admin: create a user with password AND access level in a
single, well-organised form. Styled with the Unfold theme to match the rest of
the admin. Replaces Django's default two-step user creation flow.
"""
from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from unfold.admin import ModelAdmin
from unfold.forms import AdminPasswordChangeForm, UserChangeForm, UserCreationForm

User = get_user_model()


class ProUserCreationForm(UserCreationForm):
    """User creation form that also captures profile info and access level."""

    class Meta(UserCreationForm.Meta):
        model = User
        fields = (
            "username",
            "email",
            "first_name",
            "last_name",
            "is_active",
            "is_staff",
            "is_superuser",
            "groups",
        )


try:
    admin.site.unregister(User)
except admin.sites.NotRegistered:
    pass


@admin.register(User)
class ProUserAdmin(BaseUserAdmin, ModelAdmin):
    add_form = ProUserCreationForm
    form = UserChangeForm
    change_password_form = AdminPasswordChangeForm

    filter_horizontal = ("groups", "user_permissions")
    list_display = (
        "username",
        "email",
        "full_name",
        "access_level",
        "is_active",
        "edit_button",
    )
    list_filter = ("is_active", "is_staff", "is_superuser", "groups")
    search_fields = ("username", "first_name", "last_name", "email")
    ordering = ("username",)

    # Single professional create form: identity + password + access level.
    add_fieldsets = (
        (_("اطلاعات کاربر"), {
            "classes": ("wide",),
            "fields": ("username", ("first_name", "last_name"), "email"),
        }),
        (_("رمز عبور"), {
            "classes": ("wide",),
            "description": _("یک رمز عبور قوی انتخاب کنید. کاربر می‌تواند بعداً آن را تغییر دهد."),
            "fields": ("password1", "password2"),
        }),
        (_("سطح دسترسی"), {
            "classes": ("wide",),
            "description": _(
                "«فعال» اجازه ورود می‌دهد · «دسترسی به پنل مدیریت» برای ورود به ادمین لازم است · "
                "«ابرکاربر» تمام دسترسی‌ها را می‌دهد · یا با انتخاب گروه‌ها سطح دسترسی را تعیین کنید."
            ),
            "fields": ("is_active", "is_staff", "is_superuser", "groups"),
        }),
    )

    # Organised edit form.
    fieldsets = (
        (_("ورود"), {"fields": ("username", "password")}),
        (_("اطلاعات شخصی"), {"fields": (("first_name", "last_name"), "email")}),
        (_("سطح دسترسی"), {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
        }),
        (_("تاریخ‌ها"), {"classes": ("collapse",), "fields": ("last_login", "date_joined")}),
    )

    @admin.display(description=_("نام"))
    def full_name(self, obj):
        return obj.get_full_name() or "—"

    @admin.display(description=_("سطح دسترسی"))
    def access_level(self, obj):
        if obj.is_superuser:
            label, color = _("ابرکاربر"), "#dc2626"
        elif obj.is_staff:
            label, color = _("مدیر پنل"), "#2563eb"
        else:
            label, color = _("کاربر عادی"), "#6b7280"
        groups = ", ".join(obj.groups.values_list("name", flat=True))
        badge = format_html(
            '<span style="background:{}1a;color:{};padding:2px 10px;border-radius:9999px;'
            'font-size:12px;font-weight:600;white-space:nowrap;">{}</span>',
            color, color, label,
        )
        if groups:
            return format_html('{} <span style="color:#9ca3af;font-size:12px;">{}</span>', badge, groups)
        return badge

    @admin.display(description=_("عملیات"))
    def edit_button(self, obj):
        return format_html(
            '<a href="/admin/auth/user/{}/change/" '
            'style="background:linear-gradient(135deg,#3b82f6,#60a5fa);color:#fff;'
            'padding:6px 14px;border-radius:6px;text-decoration:none;font-weight:600;'
            'font-size:12px;display:inline-flex;align-items:center;gap:4px;'
            'box-shadow:0 2px 6px rgba(59,130,246,0.3);transition:all 0.2s">'
            '✏️ ویرایش</a>',
            obj.pk,
        )
