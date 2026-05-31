from django.contrib.contenttypes.models import ContentType


def _json_safe(value):
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool, list, dict)):
        return value
    return str(value)


def model_snapshot(instance, fields=None):
    data = {}
    model_fields = fields or [f.name for f in instance._meta.fields]
    for field_name in model_fields:
        try:
            val = getattr(instance, field_name)
        except Exception:
            val = None
        data[field_name] = _json_safe(val)
    return data


def get_client_ip(request):
    if not request:
        return ""
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def log_audit_event(*, action, obj=None, object_ref="", user=None, request=None, before=None, after=None, metadata=None):
    from core.models import AuditLog

    content_type = None
    object_id = ""
    if obj is not None:
        content_type = ContentType.objects.get_for_model(obj.__class__)
        object_id = str(getattr(obj, "pk", ""))
        if not object_ref:
            object_ref = str(obj)

    changes = {}
    if before is not None:
        changes["before"] = before
    if after is not None:
        changes["after"] = after
    if metadata:
        changes["meta"] = metadata

    AuditLog.objects.create(
        actor=user if getattr(user, "is_authenticated", False) else None,
        ip_address=get_client_ip(request),
        action=action,
        content_type=content_type,
        object_id=object_id,
        object_ref=object_ref[:255],
        changes=changes,
    )
