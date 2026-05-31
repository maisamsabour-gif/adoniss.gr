import json

from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render

from .models import Brochure


def brochure_list(request):
    """Public list of all published, ready brochures."""
    brochures = (
        Brochure.objects
        .filter(is_published=True, conversion_status=Brochure.STATUS_READY)
        .order_by('-created_at')
    )
    return render(request, 'brochures/list.html', {'brochures': brochures})


def brochure_viewer(request, slug):
    """Flipbook viewer page."""
    brochure    = get_object_or_404(Brochure, slug=slug, is_published=True)
    pages_json  = json.dumps(brochure.get_all_page_urls()) if brochure.is_ready else '[]'

    return render(request, 'brochures/viewer.html', {
        'brochure':   brochure,
        'pages_json': pages_json,
    })


def brochure_pages_api(request, slug):
    """
    JSON endpoint used by the viewer to poll conversion status and get page URLs.
    GET /brochure/<slug>/pages.json
    """
    b = get_object_or_404(Brochure, slug=slug, is_published=True)
    return JsonResponse({
        'title':             b.title,
        'status':            b.conversion_status,
        'page_count':        b.page_count,
        'page_width':        b.page_width,
        'page_height':       b.page_height,
        'aspect_ratio':      b.aspect_ratio,
        'pages':             b.get_all_page_urls() if b.is_ready else [],
        'pdf_url':           b.pdf_file.url if b.pdf_file else '',
    })
