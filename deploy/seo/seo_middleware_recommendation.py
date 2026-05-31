"""
Reference middleware (optional) for enforcing SEO headers on selected paths.
Do not enable blindly; adapt to your URL policy.
"""


class SeoSecurityHeadersMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        path = request.path or ""
        if path.startswith("/admin/") or path.startswith("/fa-admin/") or path.startswith("/persian-admin/"):
            response["X-Robots-Tag"] = "noindex, nofollow, noarchive"

        return response
