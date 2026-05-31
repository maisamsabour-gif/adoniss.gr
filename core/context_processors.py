from django.conf import settings
from django.utils.translation import get_language


def _resolve_wa_url(number_or_url: str) -> str:
    """Convert a phone number or full WA link to a usable href."""
    if not number_or_url:
        return ''
    if number_or_url.startswith('http') or number_or_url.startswith('https'):
        return number_or_url
    clean = number_or_url.strip().replace(' ', '').replace('-', '')
    return f'https://wa.me/{clean.lstrip("+")}'


def site_settings(request):
    """Make site settings and header/footer models available to all templates."""
    lang = get_language() or 'en'
    wa_number = getattr(settings, 'WHATSAPP_NUMBER', '+306985989596')

    # Lazily import to avoid circular imports at module load time
    header_settings = None
    footer_settings = None
    site_obj = None
    google_analytics_id = ''
    google_ads_conversion_id = ''
    google_ads_conversion_label = ''
    microsoft_clarity_id = ''
    gtm_id = getattr(settings, 'GTM_ID', 'GTM-WS58NGGC')

    site_phone = ''
    site_email = ''
    site_address = ''

    try:
        from core.models import HeaderSettings, FooterSettings, SiteSettings
        header_settings = HeaderSettings.get_settings()
        footer_settings = FooterSettings.get_settings()
        site_obj = SiteSettings.get_settings()

        # Override WhatsApp from header settings if set
        if header_settings and header_settings.whatsapp_number:
            wa_number = header_settings.whatsapp_number

        if site_obj:
            google_analytics_id = site_obj.google_analytics_id or ''
            google_ads_conversion_id = site_obj.google_ads_conversion_id or ''
            google_ads_conversion_label = site_obj.google_ads_conversion_label or ''
            microsoft_clarity_id = site_obj.microsoft_clarity_id or ''

            # Pull contact info from SiteSettings (admin) so DB values are not
            # overwritten by Django settings fallbacks.
            site_phone = (site_obj.phone_number or '').strip()
            site_email = (site_obj.email or '').strip()
            site_address = (site_obj.address or '').strip()
    except Exception:
        pass

    if not site_email:
        site_email = getattr(settings, 'SITE_EMAIL', 'info@adonisgroup.gr')
    if not site_address:
        site_address = getattr(settings, 'SITE_ADDRESS', 'Athens, Alimos, Poseidonos Avenue, No. 78, 1st Floor')
    if not site_phone:
        site_phone = getattr(settings, 'SITE_PHONE', wa_number)

    return {
        'SITE_NAME': getattr(settings, 'SITE_NAME', 'Adonis Group'),
        'SITE_TAGLINE': getattr(settings, 'SITE_TAGLINE', 'Greek Residency & Immigration'),
        'WHATSAPP_NUMBER': wa_number,
        'WHATSAPP_URL': _resolve_wa_url(wa_number),
        'SITE_PHONE': site_phone,
        'SITE_EMAIL': site_email,
        'SITE_ADDRESS': site_address,
        'CURRENT_LANG': lang,
        'header_settings': header_settings,
        'footer_settings': footer_settings,
        'site_settings_obj': site_obj,
        'GOOGLE_ANALYTICS_ID': google_analytics_id,
        'GOOGLE_ADS_CONVERSION_ID': google_ads_conversion_id,
        'GOOGLE_ADS_CONVERSION_LABEL': google_ads_conversion_label,
        'MICROSOFT_CLARITY_ID': microsoft_clarity_id,
        'GTM_ID': gtm_id,
    }
