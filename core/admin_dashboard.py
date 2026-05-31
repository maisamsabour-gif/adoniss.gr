"""
ADONIS Admin Dashboard — quick-access cards with live counters.

UNFOLD calls `dashboard_callback(request, context)` at admin index time.
We inject `dashboard_cards` into the context; the template reads it.

Cards are shown/hidden purely by Django model permissions (has_perm).
No hardcoded role names here — add a group + permissions via
seed_rbac_roles and the card appears automatically.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Callable

from django.utils import timezone


# ── Card definition ────────────────────────────────────────────────────────────

@dataclass
class DashboardCard:
    title: str
    icon: str                           # Material Symbols name
    link: str                           # admin URL
    color: str = "teal"                 # teal | blue | violet | amber | rose | emerald | sky
    counter_fn: Callable | None = None  # callable(request) → int | None
    description: str = ""
    required_perm: str = ""             # Django permission, e.g. "core.view_blogpost"
                                        # Empty = visible to all staff (superuser check still applies)


# ── Counter helpers ────────────────────────────────────────────────────────────

def _today_start():
    return timezone.now().replace(hour=0, minute=0, second=0, microsecond=0)


def _count_new_leads(request):
    from core.models import ChatLead
    return ChatLead.objects.filter(status="new", deleted_at__isnull=True).count()


def _count_unread_chats(request):
    from core.models import ChatLead
    return ChatLead.objects.filter(is_read=False, deleted_at__isnull=True).count()


def _count_new_contacts_today(request):
    from core.models import ContactSubmission
    return ContactSubmission.objects.filter(
        is_read=False, deleted_at__isnull=True
    ).count()


def _count_partner_leads(request):
    from core.models import PartnerLead
    return PartnerLead.objects.filter(created_at__gte=_today_start()).count()


def _count_active_properties(request):
    from properties.models import Property
    return Property.objects.filter(is_active=True, deleted_at__isnull=True).count()


def _count_published_posts(request):
    from core.models import BlogPost
    try:
        return BlogPost.objects.filter(is_published=True).count()
    except Exception:
        return None


def _count_fa_pipeline_review(request):
    try:
        from properties.models_pipeline import FaContentPipeline
        return FaContentPipeline.objects.filter(status=FaContentPipeline.STATUS_REVIEW).count()
    except Exception:
        return None


def _count_en_pipeline_review(request):
    try:
        from properties.models_pipeline import EnContentPipeline
        return EnContentPipeline.objects.filter(status=EnContentPipeline.STATUS_REVIEW).count()
    except Exception:
        return None


# ── Card definitions ───────────────────────────────────────────────────────────
# Each card is shown when the user has `required_perm`.
# Superusers always see all cards.

CARD_DEFINITIONS: list[DashboardCard] = [
    DashboardCard(
        title="Add Property",
        icon="add_home",
        link="/admin/properties/property/add/",
        color="teal",
        description="Create a new property listing",
        required_perm="properties.add_property",
    ),
    DashboardCard(
        title="All Properties",
        icon="apartment",
        link="/admin/properties/property/",
        color="teal",
        counter_fn=_count_active_properties,
        description="active listings",
        required_perm="properties.view_property",
    ),
    DashboardCard(
        title="New Leads",
        icon="person_raised_hand",
        link="/admin/core/chatlead/?status__exact=new",
        color="rose",
        counter_fn=_count_new_leads,
        description="unactioned leads",
        required_perm="core.view_chatlead",
    ),
    DashboardCard(
        title="Unread Chats",
        icon="chat",
        link="/admin/core/chatlead/?is_read__exact=0",
        color="amber",
        counter_fn=_count_unread_chats,
        description="waiting for response",
        required_perm="core.view_chatlead",
    ),
    DashboardCard(
        title="Contact Submissions",
        icon="mail",
        link="/admin/core/contactsubmission/?is_read__exact=0",
        color="sky",
        counter_fn=_count_new_contacts_today,
        description="unread submissions",
        required_perm="core.view_contactsubmission",
    ),
    DashboardCard(
        title="Partner Leads",
        icon="handshake",
        link="/admin/core/partnerlead/",
        color="violet",
        counter_fn=_count_partner_leads,
        description="received today",
        required_perm="core.view_partnerlead",
    ),
    DashboardCard(
        title="Add Blog Post",
        icon="edit_note",
        link="/admin/core/blogpost/add/",
        color="emerald",
        description="Write a new article",
        required_perm="core.add_blogpost",
    ),
    DashboardCard(
        title="Published Posts",
        icon="article",
        link="/admin/core/blogpost/",
        color="emerald",
        counter_fn=_count_published_posts,
        description="live on site",
        required_perm="core.view_blogpost",
    ),
    DashboardCard(
        title="Upload Brochure",
        icon="picture_as_pdf",
        link="/admin/brochures/brochure/add/",
        color="blue",
        description="Add a downloadable PDF",
        required_perm="brochures.add_brochure",
    ),
    DashboardCard(
        title="Property Units",
        icon="meeting_room",
        link="/admin/properties/propertyunit/",
        color="teal",
        description="Manage individual units",
        required_perm="properties.view_propertyunit",
    ),
    DashboardCard(
        title="Front Page Settings",
        icon="home",
        link="/admin/core/frontpagesettings/",
        color="blue",
        description="Edit homepage content",
        required_perm="core.change_frontpagesettings",
    ),
    DashboardCard(
        title="Users & Access",
        icon="manage_accounts",
        link="/admin/auth/user/",
        color="violet",
        description="Manage staff accounts",
        required_perm="auth.view_user",
    ),
    DashboardCard(
        title="🤖 پایپ‌لاین SEO فارسی",
        icon="auto_awesome",
        link="/admin/properties/facontentpipeline/",
        color="rose",
        counter_fn=_count_fa_pipeline_review,
        description="awaiting review",
        required_perm="",
    ),
    DashboardCard(
        title="🤖 English SEO Pipeline",
        icon="auto_awesome",
        link="/admin/properties/encontentpipeline/",
        color="rose",
        counter_fn=_count_en_pipeline_review,
        description="AI blog pipeline — adonisgroup.gr",
        required_perm="",
    ),
]

# Tailwind color classes per color token
_COLOR_STYLES: dict[str, dict[str, str]] = {
    "teal":    {"bg": "bg-primary-50 dark:bg-primary-950/30",  "icon": "text-primary-600 dark:text-primary-400",  "badge": "bg-primary-100 text-primary-700 dark:bg-primary-900/40 dark:text-primary-300"},
    "blue":    {"bg": "bg-blue-50 dark:bg-blue-950/30",        "icon": "text-blue-600 dark:text-blue-400",        "badge": "bg-blue-100 text-blue-700 dark:bg-blue-900/40 dark:text-blue-300"},
    "violet":  {"bg": "bg-violet-50 dark:bg-violet-950/30",    "icon": "text-violet-600 dark:text-violet-400",    "badge": "bg-violet-100 text-violet-700 dark:bg-violet-900/40 dark:text-violet-300"},
    "amber":   {"bg": "bg-amber-50 dark:bg-amber-950/30",      "icon": "text-amber-600 dark:text-amber-400",      "badge": "bg-amber-100 text-amber-700 dark:bg-amber-900/40 dark:text-amber-300"},
    "rose":    {"bg": "bg-rose-50 dark:bg-rose-950/30",        "icon": "text-rose-600 dark:text-rose-400",        "badge": "bg-rose-100 text-rose-700 dark:bg-rose-900/40 dark:text-rose-300"},
    "emerald": {"bg": "bg-emerald-50 dark:bg-emerald-950/30",  "icon": "text-emerald-600 dark:text-emerald-400",  "badge": "bg-emerald-100 text-emerald-700 dark:bg-emerald-900/40 dark:text-emerald-300"},
    "sky":     {"bg": "bg-sky-50 dark:bg-sky-950/30",          "icon": "text-sky-600 dark:text-sky-400",          "badge": "bg-sky-100 text-sky-700 dark:bg-sky-900/40 dark:text-sky-300"},
}


def _resolve_cards(request) -> list[dict[str, Any]]:
    """Return only the cards this user is allowed to see, with live counters.

    Visibility rule: user must have the card's required_perm (or be superuser).
    """
    user = request.user
    cards = []
    for card in CARD_DEFINITIONS:
        if not user.is_superuser:
            if card.required_perm and not user.has_perm(card.required_perm):
                continue

        counter = None
        if card.counter_fn:
            try:
                counter = card.counter_fn(request)
            except Exception:
                counter = None

        styles = _COLOR_STYLES.get(card.color, _COLOR_STYLES["teal"])
        cards.append({
            "title": card.title,
            "icon": card.icon,
            "link": card.link,
            "description": card.description,
            "counter": counter,
            "bg": styles["bg"],
            "icon_color": styles["icon"],
            "badge_color": styles["badge"],
        })
    return cards


# ── Sidebar badge callbacks (referenced as dotted strings in UNFOLD settings) ─

def badge_new_leads(request) -> int | None:
    """Unread chat leads for sidebar badge."""
    try:
        from core.models import ChatLead
        n = ChatLead.objects.filter(is_read=False, deleted_at__isnull=True).count()
        return n or None
    except Exception:
        return None


def badge_contacts_today(request) -> int | None:
    """Unread contact submissions (sidebar badge)."""
    try:
        from core.models import ContactSubmission
        n = ContactSubmission.objects.filter(
            is_read=False, deleted_at__isnull=True
        ).count()
        return n or None
    except Exception:
        return None


def badge_partner_leads_new(request) -> int | None:
    """Partner leads received today."""
    try:
        from core.models import PartnerLead
        n = PartnerLead.objects.filter(created_at__gte=_today_start()).count()
        return n or None
    except Exception:
        return None


def dashboard_callback(request, context: dict[str, Any]) -> dict[str, Any]:
    """
    Injected by UNFOLD["DASHBOARD_CALLBACK"].
    Adds `dashboard_cards` to the admin index context.
    """
    context["dashboard_cards"] = _resolve_cards(request)
    context["dashboard_user_name"] = (
        request.user.get_full_name() or request.user.username
    )
    return context
