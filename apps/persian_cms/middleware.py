from django.http import HttpResponse
from django.db.utils import OperationalError, ProgrammingError

from .models import PersianRedirectMap


class PersianAdminNoIndexMiddleware:
    """Ensure Persian admin pages are not indexed."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith("/fa-admin/") or request.path.startswith("/persian-admin/"):
            response["X-Robots-Tag"] = "noindex, nofollow, noarchive"
        return response


class PersianRedirectMiddleware:
    """Apply future migration redirects from dedicated Persian map table."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        path = request.path
        try:
            mapping = PersianRedirectMap.objects.filter(is_active=True, source_path=path).first()
        except (OperationalError, ProgrammingError):
            # App may be installed before its first migration is applied.
            mapping = None
        if mapping:
            status_code = mapping.status_code if mapping.status_code in {301, 302, 307, 308} else 301
            response = HttpResponse(status=status_code)
            response["Location"] = mapping.destination_path
            return response
        return self.get_response(request)
