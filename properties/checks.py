from django.conf import settings
from django.core.checks import Warning, register


@register()
def check_google_maps_api_key(app_configs, **kwargs):
    errors = []
    key = getattr(settings, "GOOGLE_MAPS_API_KEY", "")
    if not key or not key.strip():
        errors.append(
            Warning(
                "GOOGLE_MAPS_API_KEY is not configured. "
                "Property admin will fall back to Nominatim (less precise).",
                hint=(
                    "Run: python manage.py setup_google_maps YOUR_KEY\n"
                    "  Get a key at: https://console.cloud.google.com/google/maps-apis/credentials"
                ),
                id="properties.W001",
            )
        )
    return errors
