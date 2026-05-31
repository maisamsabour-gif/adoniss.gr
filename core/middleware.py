import sys
import traceback
import logging
import re

from django.conf import settings
from django.http import HttpResponsePermanentRedirect

logger = logging.getLogger(__name__)


# ═══════════════════════════════════════════════════════════════════════════════
# Slug Redirect Middleware — preserve Google-indexed URLs after slug changes
# ═══════════════════════════════════════════════════════════════════════════════

# Maps ContentType model name → (URL name, slug kwarg, uses_language_prefix)
_SLUG_ROUTE_MAP = {
    'property':        ('property_detail',          'slug', True),
    'blogpost':        ('blog_detail',              'slug', True),
    'event':           ('event_detail',             'slug', True),
    'brochure':        ('brochure_viewer',          'slug', True),
    'goldenvisacard':  ('golden_visa_card_detail',  'slug', True),
}

# Regex to strip the optional language prefix (/en/ or /tr/) from the path
_LANG_PREFIX_RE = re.compile(r'^/(?:en|tr)/')


class SlugRedirectMiddleware:
    """
    Intercepts 404 responses and checks whether the requested path matches
    a previously-used slug recorded in SlugHistory.  If found, issues a
    permanent 301 redirect to the object's current canonical URL.

    This prevents Google de-indexing pages when slugs are edited in the admin.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if response.status_code != 404:
            return response

        # Skip admin, static, media, API paths
        path = request.path
        if path.startswith(('/admin/', '/static/', '/media/', '/ckeditor5/', '/i18n/')):
            return response

        # Extract the last non-empty path segment as the candidate slug
        stripped = _LANG_PREFIX_RE.sub('/', path)
        segments = [s for s in stripped.rstrip('/').split('/') if s]
        if not segments:
            return response
        candidate_slug = segments[-1]

        try:
            from core.models import SlugHistory
            hits = (
                SlugHistory.objects
                .filter(old_slug=candidate_slug)
                .select_related('content_type')
            )
            for hit in hits:
                model_name = hit.content_type.model
                route_info = _SLUG_ROUTE_MAP.get(model_name)
                if not route_info:
                    continue

                url_name, slug_kwarg, uses_lang = route_info
                Model = hit.content_type.model_class()
                if Model is None:
                    continue

                try:
                    obj = Model._default_manager.get(pk=hit.object_id)
                except Model.DoesNotExist:
                    continue

                if not hasattr(obj, 'get_absolute_url'):
                    continue

                new_url = obj.get_absolute_url()
                if new_url and new_url != path and new_url != stripped:
                    return HttpResponsePermanentRedirect(new_url)

        except Exception:
            logger.debug('SlugRedirectMiddleware lookup failed', exc_info=True)

        return response


class AdminNoCacheMiddleware:
    """Force no-cache headers on all /admin/ responses so browsers never
    serve a stale version after permission or navigation changes."""

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        if request.path.startswith('/admin/'):
            response['Cache-Control'] = 'no-store, no-cache, must-revalidate, max-age=0'
            response['Pragma'] = 'no-cache'
            response['Expires'] = '0'
        return response


class ErrorCaptureMiddleware:
    """
    Middleware to capture unhandled exceptions and store them in ErrorLog.
    Superadmins will see a notification badge in the admin panel.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)
        return response

    def process_exception(self, request, exception):
        from core.models import ErrorLog

        exc_type, exc_value, exc_tb = sys.exc_info()
        tb_str = ''.join(traceback.format_exception(exc_type, exc_value, exc_tb))

        request_data = {}
        try:
            if request.method == 'POST':
                request_data['POST'] = {k: v for k, v in request.POST.items() if 'password' not in k.lower()}
            request_data['GET'] = dict(request.GET)
        except Exception:
            pass

        def get_client_ip(request):
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                return x_forwarded_for.split(',')[0].strip()
            return request.META.get('REMOTE_ADDR')

        try:
            ErrorLog.objects.create(
                error_type=exc_type.__name__ if exc_type else 'Unknown',
                error_message=str(exc_value),
                traceback=tb_str,
                url=request.build_absolute_uri(),
                method=request.method,
                user_agent=request.META.get('HTTP_USER_AGENT', '')[:500],
                ip_address=get_client_ip(request),
                user=request.user if request.user.is_authenticated else None,
                request_data=request_data,
            )
        except Exception as e:
            logger.error(f'Failed to save ErrorLog: {e}')

        return None
