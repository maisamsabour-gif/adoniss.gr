from django.shortcuts import render, get_object_or_404
from django.core.exceptions import ValidationError
from django.core.paginator import Paginator
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Property, PropertyCategory, PropertyInterest, PropertyUnit, UnitBooking
from core.models import PropertiesPageSettings, PageSEO
from core.views import _seo
from core.audit import log_audit_event, model_snapshot
from core.rate_limit import rate_limit

import re


PHONE_DIGIT_RE = re.compile(r"\D+")


def _is_valid_phone(raw_phone, min_digits=7, max_digits=15):
    digits = PHONE_DIGIT_RE.sub("", raw_phone or "")
    return min_digits <= len(digits) <= max_digits


def property_list(request):
    """List all properties"""
    from django.db.models import Prefetch
    from .models import Amenity
    properties = (
        Property.objects
        .filter(is_active=True)
        .prefetch_related(
            Prefetch(
                'amenities',
                queryset=Amenity.objects.filter(is_active=True)
                    .order_by('category__display_order', 'display_order', 'name'),
            )
        )
        .order_by('display_order', '-is_featured')
    )
    categories = PropertyCategory.objects.filter(is_active=True)
    page_settings = PropertiesPageSettings.get_settings()
    
    # Filter by price tier (250, 400, 800)
    price = request.GET.get('price')
    if price in ['250', '400', '800']:
        properties = properties.filter(price_tier=price)
    
    # Filter by category
    category_slug = request.GET.get('category')
    if category_slug:
        properties = properties.filter(category__name__iexact=category_slug)
    
    # Filter by status
    status = request.GET.get('status')
    if status:
        properties = properties.filter(status=status)
    
    # Pagination
    paginator = Paginator(properties, 12)
    page = request.GET.get('page')
    properties = paginator.get_page(page)
    
    context = {
        'properties': properties,
        'categories': categories,
        'page_settings': page_settings,
        **_seo('properties'),
    }
    return render(request, 'properties/list.html', context)


def property_detail(request, slug):
    """Property detail page"""
    from django.db.models import Q, Prefetch
    from .models import Amenity, AmenityCategory
    # Look up by slug_en or slug_tr so both language URL variants always work.
    property_obj = get_object_or_404(
        Property.objects.prefetch_related(
            Prefetch(
                'amenities',
                queryset=Amenity.objects.filter(is_active=True)
                    .select_related('category')
                    .order_by('category__display_order', 'display_order', 'name'),
            )
        ),
        Q(slug_en=slug) | Q(slug_tr=slug),
        is_active=True,
    )
    related_properties = Property.objects.filter(
        is_active=True,
        category=property_obj.category,
    ).exclude(id=property_obj.id)[:4]

    # Build grouped amenity list for template (avoids extra queries)
    amenity_groups = []
    seen_cats = {}
    for amenity in property_obj.amenities.all():
        cat = amenity.category
        if cat.pk not in seen_cats:
            seen_cats[cat.pk] = {'category': cat, 'amenities': []}
            amenity_groups.append(seen_cats[cat.pk])
        seen_cats[cat.pk]['amenities'].append(amenity)

    # Build SEO context: model fields take priority over PageSEO defaults
    cover = property_obj.cover_media
    og_img = property_obj.get_og_image()
    context = {
        'property': property_obj,
        'related_properties': related_properties,
        'amenity_groups': amenity_groups,
        # SEO meta — used by base.html + property detail head block
        'meta_title': property_obj.get_seo_title(),
        'meta_description': property_obj.get_meta_description(),
        'og_title': property_obj.get_og_title(),
        'og_description': property_obj.get_og_description(),
        'og_image_obj': og_img,
        'canonical_url': property_obj.canonical_url or None,
        'robots_meta': property_obj.get_robots_meta() if hasattr(property_obj, 'get_robots_meta') else 'index, follow',
    }
    return render(request, 'properties/detail.html', context)


@require_POST
@rate_limit(key_prefix='property_interest', limit=20, window_seconds=600)
def property_interest(request, pk):
    """AJAX endpoint for 'I am interested' button"""
    property_obj = get_object_or_404(Property, pk=pk, is_active=True)
    if request.POST.get('website'):
        return JsonResponse({'success': False, 'error': 'Spam detected.'}, status=400)

    full_name = request.POST.get('full_name', '').strip()
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()
    message = request.POST.get('message', '').strip()

    if not full_name and not email and not phone:
        return JsonResponse({'success': False, 'error': 'Please provide at least your name, email or phone.'})
    if phone and not _is_valid_phone(phone):
        return JsonResponse({'success': False, 'error': 'Please enter a valid phone number.'}, status=400)

    interest = PropertyInterest.objects.create(
        property=property_obj,
        full_name=full_name,
        email=email,
        phone=phone,
        message=message,
    )
    log_audit_event(
        action='create',
        obj=interest,
        request=request,
        after=model_snapshot(interest),
        metadata={'source': 'property_interest_form'},
    )
    # Send Telegram notification
    from core.telegram import notify_property_interest
    try:
        notify_property_interest(interest)
    except Exception:
        pass  # Don't block form submission if Telegram fails
    return JsonResponse({'success': True, 'message': 'Thank you! We will contact you soon.'})


@require_POST
@rate_limit(key_prefix='unit_booking', limit=12, window_seconds=600)
def book_unit(request, pk):
    """AJAX endpoint for unit booking"""
    unit = get_object_or_404(PropertyUnit, pk=pk, availability='available', property__is_active=True)
    if request.POST.get('website'):
        return JsonResponse({'success': False, 'error': 'Spam detected.'}, status=400)

    full_name = request.POST.get('full_name', '').strip()
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()
    message = request.POST.get('message', '').strip()

    if not full_name or not email or not phone:
        return JsonResponse({'success': False, 'error': 'Please provide your name, email and phone.'})
    if not _is_valid_phone(phone):
        return JsonResponse({'success': False, 'error': 'Please enter a valid phone number.'}, status=400)

    try:
        booking = UnitBooking.objects.create(
            unit=unit,
            full_name=full_name,
            email=email,
            phone=phone,
            message=message,
        )
    except ValidationError as exc:
        return JsonResponse({'success': False, 'error': '; '.join(exc.messages)}, status=400)

    unit.availability = 'reserved'
    unit.save(update_fields=['availability'])

    log_audit_event(
        action='create',
        obj=booking,
        request=request,
        after=model_snapshot(booking),
        metadata={'source': 'unit_booking_form'},
    )
    # Send Telegram notification
    try:
        from core.telegram import notify_unit_booking
        notify_unit_booking(booking)
    except Exception:
        pass
    return JsonResponse({'success': True, 'message': 'Booking request submitted! We will contact you soon.'})
