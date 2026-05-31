"""
Idempotent management command that creates the "Property & Blog Manager"
group, assigns it the correct permissions, and moves user "navid" into
that group (removing any previous groups).

Usage:
    python manage.py setup_navid_permissions
"""

from django.contrib.auth.models import Group, Permission, User
from django.core.management import call_command
from django.core.management.base import BaseCommand

from core.rbac import ROLE_PROPERTY_BLOG_MGR

TARGET_USERNAME = "navid"


class Command(BaseCommand):
    help = (
        'Create the "Property & Blog Manager" group with scoped permissions '
        "and assign it to user navid. Safe to re-run."
    )

    def handle(self, *args, **options):
        # 1. Seed all RBAC roles (ensures the group + permissions exist)
        self.stdout.write("Running seed_rbac_roles first …")
        call_command("seed_rbac_roles", stdout=self.stdout)

        # 2. Verify the group was created
        try:
            group = Group.objects.get(name=ROLE_PROPERTY_BLOG_MGR)
        except Group.DoesNotExist:
            self.stderr.write(
                self.style.ERROR(
                    f'Group "{ROLE_PROPERTY_BLOG_MGR}" was not created by '
                    f"seed_rbac_roles. Check the role definition."
                )
            )
            return

        perm_count = group.permissions.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'Group "{ROLE_PROPERTY_BLOG_MGR}" ready — '
                f"{perm_count} permissions assigned."
            )
        )

        # 3. Find the target user
        try:
            user = User.objects.get(username=TARGET_USERNAME)
        except User.DoesNotExist:
            self.stderr.write(
                self.style.ERROR(
                    f'User "{TARGET_USERNAME}" not found. '
                    f"Create the user first, then re-run."
                )
            )
            return

        # 4. Enforce is_staff=True, is_superuser=False
        changed_flags = []
        if not user.is_staff:
            user.is_staff = True
            changed_flags.append("is_staff → True")
        if user.is_superuser:
            user.is_superuser = False
            changed_flags.append("is_superuser → False")
        if changed_flags:
            user.save(update_fields=["is_staff", "is_superuser"])
            self.stdout.write(f"  User flags updated: {', '.join(changed_flags)}")

        # 5. Replace all existing groups with the new one
        old_groups = list(user.groups.values_list("name", flat=True))
        user.groups.clear()
        user.groups.add(group)
        self.stdout.write(
            f"  Removed from groups: {old_groups or '(none)'}\n"
            f"  Added to group: {ROLE_PROPERTY_BLOG_MGR}"
        )

        # 6. Summary
        self.stdout.write(
            self.style.SUCCESS(
                f'\nDone. User "{user.username}" '
                f'({user.get_full_name() or "no display name"}) '
                f'now has role "{ROLE_PROPERTY_BLOG_MGR}" with '
                f"{perm_count} permissions."
            )
        )

        self._print_permission_summary(group)

    def _print_permission_summary(self, group):
        """Print a grouped list of the assigned permissions."""
        perms = (
            group.permissions
            .select_related("content_type")
            .order_by("content_type__app_label", "codename")
        )
        self.stdout.write("\nPermissions breakdown:")
        current_app = None
        for p in perms:
            app = p.content_type.app_label
            if app != current_app:
                current_app = app
                self.stdout.write(f"  [{app}]")
            self.stdout.write(f"    {p.codename}")
