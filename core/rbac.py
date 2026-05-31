from typing import Iterable, Set


ROLE_SUPERADMIN           = "SuperAdmin"
ROLE_ADMIN                = "Admin"
ROLE_SALES                = "Sales"
ROLE_SUPPORT              = "Support"
ROLE_CONTENT              = "Content"
ROLE_CONTENT_ADMIN        = "ContentAdmin"
ROLE_CONTENT_MANAGER      = "ContentManager"
ROLE_PROPERTY_BLOG_EDITOR = "PropertyBlogEditor"
ROLE_PROPERTY_BLOG_MGR    = "Property & Blog Manager"
ROLE_VIEWER               = "Viewer"

ALL_ROLES = {
    ROLE_SUPERADMIN,
    ROLE_ADMIN,
    ROLE_SALES,
    ROLE_SUPPORT,
    ROLE_CONTENT,
    ROLE_CONTENT_ADMIN,
    ROLE_CONTENT_MANAGER,
    ROLE_PROPERTY_BLOG_EDITOR,
    ROLE_PROPERTY_BLOG_MGR,
    ROLE_VIEWER,
}

PHONE_FULL_ACCESS_ROLES = {
    ROLE_SUPERADMIN,
    ROLE_ADMIN,
    ROLE_SALES,
    ROLE_SUPPORT,
}


def get_user_roles(user) -> Set[str]:
    if not user or not user.is_authenticated:
        return set()

    if user.is_superuser:
        return {ROLE_SUPERADMIN}

    roles = set(user.groups.values_list("name", flat=True))
    if not roles and user.is_staff:
        # Backward-compatible default so existing staff users don't get locked out.
        roles.add(ROLE_ADMIN)
    return roles


def has_any_role(user, roles: Iterable[str]) -> bool:
    user_roles = get_user_roles(user)
    return bool(user_roles.intersection(set(roles)))


def can_view_full_phone(user) -> bool:
    return has_any_role(user, PHONE_FULL_ACCESS_ROLES)


def mask_phone_number(phone: str) -> str:
    if not phone:
        return ""

    digits = [c for c in phone if c.isdigit()]
    if len(digits) <= 4:
        return "*" * len(phone)

    visible = 3
    masked_count = max(0, len(digits) - visible)
    masked_digits = ["*"] * masked_count + digits[-visible:]

    result = []
    idx = 0
    for ch in phone:
        if ch.isdigit():
            result.append(masked_digits[idx])
            idx += 1
        else:
            result.append(ch)
    return "".join(result)
