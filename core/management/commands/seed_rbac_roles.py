from django.contrib.auth.models import Group, Permission
from django.core.management.base import BaseCommand

from core.rbac import (
    ROLE_ADMIN,
    ROLE_CONTENT,
    ROLE_CONTENT_ADMIN,
    ROLE_CONTENT_MANAGER,
    ROLE_PROPERTY_BLOG_EDITOR,
    ROLE_PROPERTY_BLOG_MGR,
    ROLE_SALES,
    ROLE_SUPPORT,
    ROLE_VIEWER,
)


def _perm(action, model):
    return f"{action}_{model}"


# Shorthand helpers for common permission groups
def _crud(model):
    return [_perm(a, model) for a in ("view", "add", "change", "delete")]

def _view_change(model):
    return [_perm(a, model) for a in ("view", "change")]


class Command(BaseCommand):
    help = "Create/update baseline RBAC groups and permissions."

    def handle(self, *args, **options):
        role_permissions = {
            ROLE_VIEWER: [
                _perm("view", "property"),
                _perm("view", "propertyunit"),
                _perm("view", "unitbooking"),
                _perm("view", "propertyinterest"),
                _perm("view", "contactsubmission"),
                _perm("view", "chatlead"),
                _perm("view", "chatmessage"),
            ],
            ROLE_CONTENT: [
                _perm("view", "blogpost"),
                _perm("add", "blogpost"),
                _perm("change", "blogpost"),
                _perm("view", "blogcategory"),
                _perm("add", "blogcategory"),
                _perm("change", "blogcategory"),
                _perm("view", "testimonial"),
                _perm("add", "testimonial"),
                _perm("change", "testimonial"),
                _perm("view", "faq"),
                _perm("add", "faq"),
                _perm("change", "faq"),
                _perm("view", "service"),
                _perm("add", "service"),
                _perm("change", "service"),
                _perm("view", "processstep"),
                _perm("add", "processstep"),
                _perm("change", "processstep"),
                # Content editors also need full CRUD on these
                *_crud("event"),
                *_crud("teammember"),
                *_crud("goldenvisacard"),
                *_crud("brochure"),
                # View/change page settings
                *_view_change("frontpagesettings"),
                *_view_change("headersettings"),
                *_view_change("footersettings"),
                *_view_change("aboutpagesettings"),
                *_view_change("partnershippagesettings"),
                *_view_change("propertiespagesettings"),
                # Properties (view/add/change — no delete)
                _perm("view", "property"),
                _perm("add", "property"),
                _perm("change", "property"),
                _perm("view", "propertyunit"),
                _perm("add", "propertyunit"),
                _perm("change", "propertyunit"),
                _perm("view", "propertyinterest"),
                _perm("change", "propertyinterest"),
            ],
            # ── PropertyBlogEditor ────────────────────────────────────────────
            # Exactly: Properties (full CRUD) + Blog (full CRUD).
            # No access to leads, contacts, site settings, or any other model.
            ROLE_PROPERTY_BLOG_EDITOR: [
                *_crud("property"),
                *_crud("propertyunit"),
                *_crud("propertycategory"),
                *_crud("blogpost"),
                *_crud("blogcategory"),
            ],

            # ── Property & Blog Manager ──────────────────────────────────────
            # Properties (view/add/change), Units (CRUD), Interest Requests,
            # Blog (CRUD), Brochures (CRUD), Contact messages (view/change).
            ROLE_PROPERTY_BLOG_MGR: [
                _perm("view", "property"),
                _perm("add", "property"),
                _perm("change", "property"),
                *_crud("propertyunit"),
                _perm("view", "propertymedia"),
                _perm("add", "propertymedia"),
                _perm("change", "propertymedia"),
                _perm("delete", "propertymedia"),
                _perm("view", "propertyinterest"),
                _perm("change", "propertyinterest"),
                *_crud("blogpost"),
                *_crud("blogcategory"),
                *_crud("brochure"),
                _perm("view", "contactsubmission"),
                _perm("change", "contactsubmission"),
                _perm("view", "chatlead"),
                _perm("change", "chatlead"),
                _perm("view", "chatmessage"),
                _perm("view", "partnerlead"),
                _perm("change", "partnerlead"),
            ],

            ROLE_CONTENT_MANAGER: [
                # ── Blog (full CRUD) ──────────────────────────────────────────
                *_crud("blogpost"),
                *_crud("blogcategory"),
                # ── All content models (full CRUD) ───────────────────────────
                *_crud("event"),
                *_crud("testimonial"),
                *_crud("teammember"),
                *_crud("goldenvisacard"),
                *_crud("processstep"),
                *_crud("service"),
                *_crud("faq"),
                *_crud("brochure"),
                # ── Properties (full CRUD) ───────────────────────────────────
                *_crud("property"),
                *_crud("propertyunit"),
                *_crud("propertyinterest"),
                *_crud("unitbooking"),
                # ── Page settings (view + change) ────────────────────────────
                *_view_change("frontpagesettings"),
                *_view_change("headersettings"),
                *_view_change("footersettings"),
                *_view_change("aboutpagesettings"),
                *_view_change("partnershippagesettings"),
                *_view_change("propertiespagesettings"),
            ],

            # ── ContentAdmin — dedicated content management role ──────────────
            ROLE_CONTENT_ADMIN: [
                # Blog
                *_crud("blogpost"),
                _perm("view", "blogcategory"),
                _perm("add", "blogcategory"),
                _perm("change", "blogcategory"),
                # Properties (view/add/change — no delete)
                _perm("view", "property"),
                _perm("add", "property"),
                _perm("change", "property"),
                _perm("view", "propertyunit"),
                _perm("add", "propertyunit"),
                _perm("change", "propertyunit"),
                _perm("view", "propertycategory"),
                _perm("view", "amenitycategory"),
                _perm("view", "amenity"),
                # Golden Visa Landing Page (view/change only)
                *_view_change("goldenvisalandingpage"),
                _perm("view", "goldenvisacard"),
                _perm("change", "goldenvisacard"),
                # Page SEO (view/change)
                *_view_change("pageseo"),
                # Content models (full CRUD)
                *_crud("faq"),
                *_crud("processstep"),
                *_crud("testimonial"),
                *_crud("teammember"),
                *_crud("service"),
                *_crud("brochure"),
                *_crud("event"),
                *_crud("eventimage"),
                # Page settings (view/change)
                *_view_change("frontpagesettings"),
                *_view_change("headersettings"),
                *_view_change("footersettings"),
                *_view_change("aboutpagesettings"),
                *_view_change("partnershippagesettings"),
                *_view_change("propertiespagesettings"),
                # Office
                _perm("view", "office"),
                _perm("change", "office"),
            ],
            ROLE_SALES: [
                _perm("view", "property"),
                _perm("add", "property"),
                _perm("change", "property"),
                _perm("view", "propertyunit"),
                _perm("add", "propertyunit"),
                _perm("change", "propertyunit"),
                _perm("view", "unitbooking"),
                _perm("change", "unitbooking"),
                _perm("view", "propertyinterest"),
                _perm("change", "propertyinterest"),
                _perm("view", "customer"),
                _perm("change", "customer"),
            ],
            ROLE_SUPPORT: [
                _perm("view", "contactsubmission"),
                _perm("change", "contactsubmission"),
                _perm("view", "chatlead"),
                _perm("change", "chatlead"),
                _perm("view", "chatmessage"),
                _perm("add", "chatmessage"),
                _perm("change", "chatmessage"),
                _perm("view", "customer"),
                _perm("change", "customer"),
            ],
            # ── Admin — full control over all content & operations,
            #           NO access to auth.User/Group or system-level models.
            ROLE_ADMIN: [
                # ── Properties ───────────────────────────────────────────────
                *_crud("property"),
                *_crud("propertyunit"),
                *_crud("propertycategory"),
                *_crud("amenitycategory"),
                *_crud("amenity"),
                _perm("view", "unitbooking"),
                _perm("change", "unitbooking"),
                _perm("view", "propertyinterest"),
                _perm("change", "propertyinterest"),
                # ── Blog ─────────────────────────────────────────────────────
                *_crud("blogpost"),
                *_crud("blogcategory"),
                # ── Content models ───────────────────────────────────────────
                *_crud("faq"),
                *_crud("processstep"),
                *_crud("testimonial"),
                *_crud("teammember"),
                *_crud("goldenvisacard"),
                *_crud("service"),
                *_crud("brochure"),
                *_crud("event"),
                *_crud("eventimage"),
                # ── Landing pages ────────────────────────────────────────────
                *_view_change("goldenvisalandingpage"),
                *_view_change("pageseo"),
                # ── Messages / leads ─────────────────────────────────────────
                _perm("view", "contactsubmission"),
                _perm("change", "contactsubmission"),
                _perm("view", "chatlead"),
                _perm("change", "chatlead"),
                _perm("view", "chatmessage"),
                _perm("change", "chatmessage"),
                _perm("view", "partnerlead"),
                _perm("change", "partnerlead"),
                # ── Customers ────────────────────────────────────────────────
                _perm("view", "customer"),
                _perm("change", "customer"),
                # ── Brochures (separate app) ─────────────────────────────────
                *_crud("brochure"),
                # ── Page / site settings (content-related only) ──────────────
                # Header, footer, front page design are superadmin-only.
                *_view_change("aboutpagesettings"),
                *_view_change("partnershippagesettings"),
                *_view_change("propertiespagesettings"),
                _perm("view", "office"),
                _perm("change", "office"),
            ],
        }

        for role, codenames in role_permissions.items():
            group, created = Group.objects.get_or_create(name=role)
            # Deduplicate codenames (some roles share entries via helpers)
            unique_codenames = list(dict.fromkeys(codenames))
            perms = Permission.objects.filter(codename__in=unique_codenames)
            group.permissions.set(perms)
            action = "created" if created else "updated"
            self.stdout.write(
                self.style.SUCCESS(
                    f"Role '{role}' {action} — {perms.count()} permissions assigned."
                )
            )

        self.stdout.write(self.style.SUCCESS("RBAC seeding completed."))
