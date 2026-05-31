"""
Data migration: create "Property & Blog Manager" group and assign it
to user "navid".  Idempotent — safe to re-run via migrate --run-syncdb.

This is a backup of the same logic in:
    python manage.py setup_navid_permissions
"""

from django.db import migrations

TARGET_USERNAME = "navid"
GROUP_NAME = "Property & Blog Manager"

PERMISSION_CODENAMES = [
    # Properties
    "view_property",
    "add_property",
    "change_property",
    "view_propertyunit",
    "add_propertyunit",
    "change_propertyunit",
    "delete_propertyunit",
    "view_propertymedia",
    "add_propertymedia",
    "change_propertymedia",
    "delete_propertymedia",
    "view_propertyinterest",
    "change_propertyinterest",
    # Blog
    "view_blogpost",
    "add_blogpost",
    "change_blogpost",
    "delete_blogpost",
    "view_blogcategory",
    "add_blogcategory",
    "change_blogcategory",
    "delete_blogcategory",
    # Brochures
    "view_brochure",
    "add_brochure",
    "change_brochure",
    "delete_brochure",
    # Contact / lead messages
    "view_contactsubmission",
    "change_contactsubmission",
    "view_chatlead",
    "change_chatlead",
    "view_chatmessage",
    "view_partnerlead",
    "change_partnerlead",
]


def forwards(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    Permission = apps.get_model("auth", "Permission")
    User = apps.get_model("auth", "User")

    group, _ = Group.objects.get_or_create(name=GROUP_NAME)

    perms = Permission.objects.filter(codename__in=PERMISSION_CODENAMES)
    group.permissions.set(perms)

    try:
        user = User.objects.get(username=TARGET_USERNAME)
    except User.DoesNotExist:
        return

    user.is_staff = True
    user.is_superuser = False
    user.save(update_fields=["is_staff", "is_superuser"])

    user.groups.clear()
    user.groups.add(group)


def backwards(apps, schema_editor):
    Group = apps.get_model("auth", "Group")
    User = apps.get_model("auth", "User")

    try:
        user = User.objects.get(username=TARGET_USERNAME)
        user.groups.filter(name=GROUP_NAME).delete()
    except User.DoesNotExist:
        pass

    Group.objects.filter(name=GROUP_NAME).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("core", "0032_headersettings_intro_video_url"),
    ]

    operations = [
        migrations.RunPython(forwards, backwards),
    ]
