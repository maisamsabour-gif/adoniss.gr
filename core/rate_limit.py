from functools import wraps

from django.core.cache import cache
from django.http import JsonResponse


def _client_ip(request):
    forwarded = request.META.get("HTTP_X_FORWARDED_FOR", "")
    if forwarded:
        return forwarded.split(",")[0].strip()
    return request.META.get("REMOTE_ADDR", "")


def rate_limit(*, key_prefix, limit, window_seconds):
    def decorator(view_func):
        @wraps(view_func)
        def wrapped(request, *args, **kwargs):
            ip = _client_ip(request) or "unknown"
            cache_key = f"rl:{key_prefix}:{ip}"

            created = cache.add(cache_key, 1, timeout=window_seconds)
            if created:
                return view_func(request, *args, **kwargs)

            try:
                current = cache.incr(cache_key)
            except ValueError:
                cache.set(cache_key, 1, timeout=window_seconds)
                current = 1

            if current > limit:
                return JsonResponse(
                    {
                        "success": False,
                        "error": "Too many requests. Please try again later.",
                    },
                    status=429,
                )
            return view_func(request, *args, **kwargs)

        return wrapped

    return decorator
