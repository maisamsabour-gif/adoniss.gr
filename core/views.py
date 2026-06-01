import json
import hashlib
import logging
import re
from urllib.parse import quote
from urllib.request import Request, urlopen

from django.db import connection
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.core.cache import cache
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_protect
from django.views.decorators.http import require_GET, require_POST

from core import models
from core.models import (
    AboutPageSettings,
    BlogCategory,
    BlogPost,
    ChatLead,
    ChatSession,
    ChatSessionMessage,
    ContactSubmission,
    Event,
    EventImage,
    FAQ,
    FooterSettings,
    FrontPageSettings,
    GoldenVisaCard,
    GoldenVisaFaLandingPage,
    GoldenVisaFaProcessStep,
    GoldenVisaLandingPage,
    HeaderSettings,
    Office,
    PartnerLead,
    PartnershipPageSettings,
    ProcessStep,
    PropertiesPageSettings,
    Service,
    SiteSettings,
    TeamMember,
    Testimonial,
    WebinarLandingSettings,
    WebinarRegistration,
)
from core.forms import ContactForm
from core.rbac import ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_SALES, ROLE_SUPPORT, ROLE_CONTENT, has_any_role
from core.audit import log_audit_event, model_snapshot
from core import telegram

logger = logging.getLogger(__name__)

# Phase constants for ChatSession
PHASE_BOT = 'greeting'
PHASE_WAIT = 'handover'
PHASE_HUMAN = 'qualification'
PHASE_CLOSED = 'closed'

_VALID_PARTNER_TYPES = {key for key, _ in PartnerLead.PARTNER_TYPE_CHOICES}


def _seo(request_or_key, page_key=None, **kwargs):
    """Return a dict with page-level SEO from PageSEO model.

    Accepts both calling conventions:
      _seo(request, 'page_key')   – new style
      _seo('page_key')            – legacy style (request omitted)
    """
    if page_key is None:
        page_key = request_or_key
    from core.models import PageSEO
    from django.utils.translation import get_language
    lang = (get_language() or 'en').split('-')[0]
    try:
        seo = PageSEO.for_page(page_key)
        canonical_fallback = kwargs.get('canonical_url', '')
        if not canonical_fallback and hasattr(request_or_key, 'build_absolute_uri') and hasattr(request_or_key, 'path'):
            canonical_fallback = request_or_key.build_absolute_uri(request_or_key.path)
        robots_meta = seo.get_robots_meta() if hasattr(seo, "get_robots_meta") else ("noindex, follow" if getattr(seo, "noindex", False) else "index, follow")
        return {
            'meta_title': seo.get_meta_title(lang) or kwargs.get('meta_title', ''),
            'meta_description': seo.get_meta_desc(lang) or kwargs.get('meta_description', ''),
            'og_title': seo.get_og_title(lang) or kwargs.get('og_title', ''),
            'og_description': seo.get_og_desc(lang) or kwargs.get('og_description', ''),
            'og_image': seo.og_image.url if seo.og_image else kwargs.get('og_image', ''),
            'canonical_url': seo.get_canonical_url() or canonical_fallback,
            'robots_meta': robots_meta,
        }
    except Exception:
        return {}


def _contains_persian(text: str) -> bool:
    """Return True if text contains Persian/Arabic characters."""
    if not text:
        return False
    return bool(re.search(r'[\u0600-\u06ff]', text))


def _translate_to_fa_cached(text: str) -> str:
    """Translate English text to Persian using a cached lookup."""
    if not text or _contains_persian(text):
        return text
    cache_key = 'fa_' + hashlib.md5(text.encode()).hexdigest()[:16]
    cached = cache.get(cache_key)
    if cached:
        return cached
    return text


def _to_youtube_embed(url: str) -> str:
    """Convert any YouTube URL format to an embeddable URL.

    Handles:
      - https://www.youtube.com/watch?v=ID
      - https://youtu.be/ID
      - https://www.youtube.com/shorts/ID
      - https://youtube.com/shorts/ID?si=...
      - https://www.youtube.com/embed/ID  (already correct)
    """
    if not url:
        return ''
    url = url.strip()
    video_id = None
    # Already embed
    m = re.search(r'youtube\.com/embed/([A-Za-z0-9_\-]{11})', url)
    if m:
        return f'https://www.youtube.com/embed/{m.group(1)}'
    # shorts
    m = re.search(r'youtube\.com/shorts/([A-Za-z0-9_\-]{11})', url)
    if m:
        video_id = m.group(1)
    # watch?v=
    if not video_id:
        m = re.search(r'[?&]v=([A-Za-z0-9_\-]{11})', url)
        if m:
            video_id = m.group(1)
    # youtu.be/
    if not video_id:
        m = re.search(r'youtu\.be/([A-Za-z0-9_\-]{11})', url)
        if m:
            video_id = m.group(1)
    if video_id:
        return f'https://www.youtube.com/embed/{video_id}'
    return url  # return as-is if we couldn't parse it


def _normalize_fa_intro_html(html: str) -> str:
    """Clean up the FA landing page intro HTML for safe rendering."""
    if not html:
        return ''
    # Remove redundant wrapping paragraphs
    html = re.sub(r'<p>\s*(<p>)', r'\1', html, flags=re.IGNORECASE)
    html = re.sub(r'(</p>)\s*</p>', r'\1', html, flags=re.IGNORECASE)
    return html.strip()


def _normalize_phone(phone: str) -> str:
    """Return a normalised E.164-like phone string."""
    if not phone:
        return ''
    cleaned = re.sub(r'[\s\-\(\)\.]+', '', phone.strip())
    return cleaned


def _is_valid_phone(phone: str) -> bool:
    """Basic phone number validation."""
    cleaned = _normalize_phone(phone)
    return bool(re.match(r'^\+?[0-9]{7,15}$', cleaned))


def _can_access_dashboard(user) -> bool:
    return user.is_active and (user.is_staff or user.is_superuser)


# ── Health ────────────────────────────────────────────────────────────────────

def health_live(request):
    return JsonResponse({'status': 'ok', 'service': 'adonis', 'check': 'live'})


def health_ready(request):
    try:
        with connection.cursor() as cursor:
            cursor.execute('SELECT 1')
            cursor.fetchone()
        return JsonResponse({'status': 'ok', 'service': 'adonis', 'check': 'ready', 'db': 'ok'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'db': str(e)}, status=503)


# ── Home ──────────────────────────────────────────────────────────────────────

# CSRF caveat: base.html bakes a {% csrf_token %} into the consultation modal
# form. With per-view caching the same rendered token is served to every
# visitor, so AJAX submissions of that modal will fail CSRF validation
# (their cookie token will not match the cached form token). If the modal
# submit starts 403'ing in production, drop this decorator or refactor the
# token to be fetched separately.
@cache_page(60 * 15)
def home(request):
    """Homepage view"""
    services = Service.objects.filter(is_active=True).order_by('order')
    process_steps = ProcessStep.objects.filter(is_active=True).order_by('step_number')
    testimonials = Testimonial.objects.filter(is_active=True).order_by('-created_at')
    faqs = FAQ.objects.filter(is_active=True).order_by('order')
    contact_form = ContactForm()
    gv_cards = GoldenVisaCard.objects.filter(is_active=True).order_by('order')

    try:
        from properties.models import Property
        featured_properties = Property.objects.filter(is_active=True, is_featured=True).order_by('display_order', '-is_featured')[:6]
    except Exception:
        featured_properties = []

    try:
        from brochures.models import Brochure
        from brochures.models import STATUS_READY
        brochures = Brochure.objects.filter(status=STATUS_READY).order_by('order')[:4]
    except Exception:
        brochures = []

    about_settings = AboutPageSettings.get_settings()
    fp = FrontPageSettings.get_settings()
    seo = _seo(request, 'home')
    ctx = {
        'services': services,
        'process_steps': process_steps,
        'testimonials': testimonials,
        'faqs': faqs,
        'contact_form': contact_form,
        'gv_cards': gv_cards,
        'featured_properties': featured_properties,
        'properties': featured_properties,
        'brochures': brochures,
        'about': about_settings,
        'fp': fp,
        **seo,
    }
    return render(request, 'index.html', ctx)


# ── About ─────────────────────────────────────────────────────────────────────

def about(request):
    """About page"""
    about = AboutPageSettings.get_settings()
    team_members = TeamMember.objects.filter(is_active=True).order_by('order')
    seo = _seo(request, 'about')
    return render(request, 'about.html', {
        'about': about,
        'team_members': team_members,
        **seo,
    })


# ── Contact ───────────────────────────────────────────────────────────────────

def contact(request):
    """Contact page"""
    offices = Office.objects.filter(is_active=True).order_by('order')
    form = ContactForm()

    if request.method == 'POST':
        form = ContactForm(request.POST)
        honeypot = request.POST.get('website', '')
        if honeypot:
            messages.error(request, 'Invalid submission detected.')
            return redirect('contact')
        phone = request.POST.get('phone', '')
        if not _is_valid_phone(phone):
            messages.error(request, 'Please enter a valid phone number.')
        elif form.is_valid():
            submission = form.save(commit=False)
            submission.source = 'contact_page'
            submission.save()
            try:
                telegram.notify_new_contact(submission)
            except Exception:
                pass
            messages.success(request, 'Your message has been sent!')
            return redirect('contact')

    seo = _seo(request, 'contact')
    return render(request, 'contact.html', {'offices': offices, 'form': form, **seo})


# ── AJAX: Submit contact ───────────────────────────────────────────────────────

def submit_contact(request):
    """AJAX contact form submission"""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    honeypot = request.POST.get('website', '')
    if honeypot:
        return JsonResponse({'success': False, 'errors': {'__all__': ['Spam detected.']}})

    form = ContactForm(request.POST)
    phone = request.POST.get('phone', '').strip()
    if phone and not _is_valid_phone(phone):
        return JsonResponse({'success': False, 'errors': {'phone': ['Enter a valid phone number.']}})

    if form.is_valid():
        submission = form.save(commit=False)
        notes = request.POST.get('notes', '')
        if notes:
            submission.notes = '[ads_tracking] ' + notes
        # Detect source from notes or referer
        if 'fa_landing' in notes:
            submission.source = 'fa_landing_modal'
        elif 'consultation_modal' in notes:
            submission.source = 'consultation_modal'
        elif request.META.get('HTTP_REFERER', '').endswith('/contact/') or request.META.get('HTTP_REFERER', '').endswith('/contact'):
            submission.source = 'contact_page'
        else:
            submission.source = 'modal_form'
        submission.save()
        try:
            log_audit_event(
                actor=None, action='create', instance=submission,
                snapshot=model_snapshot(submission),
            )
        except Exception:
            pass
        try:
            telegram.notify_new_contact(submission)
        except Exception:
            pass
        return JsonResponse({'success': True})
    return JsonResponse({'success': False, 'errors': form.errors})


# ── AJAX: Submit chat lead ─────────────────────────────────────────────────────

@csrf_protect
def submit_chat_lead(request):
    """
    AJAX endpoint — chat widget phone number capture.

    Accepts JSON body:
      phone, name, topic, page_url, language,
      conversation  (JSON array of {role, text} objects)
    """
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        data = request.POST

    phone = str(data.get('phone', '')).strip()
    name = str(data.get('name', '')).strip()
    topic = str(data.get('topic', '')).strip()
    page_url = str(data.get('page_url', '')).strip()
    language = str(data.get('language', 'en')).strip()
    conversation_raw = data.get('conversation', [])

    if not phone:
        return JsonResponse({'success': False, 'error': 'Phone number is required.'})
    if not _is_valid_phone(phone):
        return JsonResponse({'success': False, 'error': 'Enter a valid phone number (e.g. +30 210 xxx xxxx).'})

    try:
        from core.chat_utils import normalize_phone, is_valid_phone, generate_chat_summary, detect_language, sanitize_text
    except ImportError:
        normalize_phone = lambda x: x
        generate_chat_summary = lambda x: ''
        detect_language = lambda x: language
        sanitize_text = lambda x: x

    phone = normalize_phone(phone)

    # Process conversation
    if isinstance(conversation_raw, str):
        try:
            conversation_raw = json.loads(conversation_raw)
        except Exception:
            conversation_raw = []

    summary = ''
    try:
        summary = generate_chat_summary(conversation_raw)
    except Exception:
        pass

    # Deduplication: check for recent same phone
    from django.utils import timezone
    from datetime import timedelta
    four_hours_ago = timezone.now() - timedelta(hours=4)
    existing = ChatLead.objects.filter(
        phone=phone,
        created_at__gte=four_hours_ago,
        status__in=['new', 'follow_up'],
    ).first()

    if existing:
        if topic and not existing.topic:
            existing.topic = topic
        if page_url and not existing.page_url:
            existing.page_url = page_url
        if summary:
            existing.summary = summary
        existing.save()
        lead = existing
    else:
        lead = ChatLead.objects.create(
            name=name or phone,
            phone=phone,
            topic=topic,
            page_url=page_url,
            language=language,
            summary=summary,
            source='chat',
        )

    # Telegram notification
    try:
        telegram.notify_chat_lead(lead)
        from django.utils import timezone as tz
        lead.telegram_sent = True
        lead.telegram_sent_at = tz.now()
        lead.save(update_fields=['telegram_sent', 'telegram_sent_at'])
    except Exception:
        pass

    return JsonResponse({'success': True})


# ── AI Consultation Chat Reply ──────────────────────────────────────────────────

@require_POST
def ai_chat_reply(request):
    """
    AI-powered consultation chat endpoint.
    Uses OpenAI GPT-4o-mini if OPENAI_API_KEY is set in environment.
    Returns {fallback: true} when the key is absent so the frontend
    uses its built-in scripted Persian/EN/TR responses instead.

    Lead capture: if the AI detects name + phone in the conversation it
    returns action='lead_saved' and persists a ContactSubmission + Telegram.
    """
    import os

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'fallback': True})

    message  = str(data.get('message',  '')).strip()[:600]
    history  = data.get('history', [])
    page_url = str(data.get('page_url', '')).strip()[:200]
    language = str(data.get('language', 'en')).strip().lower()[:2]
    mode     = str(data.get('mode',     'general')).strip()

    if not message:
        return JsonResponse({'fallback': True})

    api_key = os.getenv('OPENAI_API_KEY', '').strip()
    if not api_key:
        return JsonResponse({'fallback': True})

    try:
        from openai import OpenAI
    except ImportError:
        return JsonResponse({'fallback': True})

    # ── System prompt per language ────────────────────────────────────────────
    _PROMPTS = {
        'fa': (
            "شما یک مشاور متخصص گلدن ویزای یونان در شرکت آدونیس گروپ هستید. "
            "همیشه به فارسی روان و حرفه‌ای پاسخ دهید. "
            "اطلاعات کلیدی: حداقل سرمایه‌گذاری ۲۵۰,۰۰۰ یورو (۸۰۰,۰۰۰ یورو در مناطق ویژه)، "
            "اقامت دائمی برای کل خانواده بدون نیاز به سکونت، "
            "دسترسی به کل منطقه شنگن، مسیر شهروندی بعد از ۷ سال. "
            "هدف شما: درک نیاز مشتری، پاسخ صادقانه به سوالات، "
            "و وقتی که مشتری واقعاً علاقه‌مند بود از او نام کامل و شماره تماس بخواهید. "
            "پاسخ‌هایتان کوتاه باشند (حداکثر ۴ جمله). "
            "وقتی کاربر نام و شماره تلفن داد، فقط دقیقاً این را بنویسید: "
            "LEAD_CAPTURE:{name}|{phone} "
            "و بعد یک پیام تشکر کوتاه فارسی بنویسید."
        ),
        'tr': (
            "Adonis Group şirketinde Yunanistan Altın Vize uzman danışmanısınız. "
            "Her zaman akıcı Türkçe yanıt verin. "
            "Temel bilgiler: minimum 250.000 Euro yatırım (seçkin bölgelerde 800.000 Euro), "
            "tüm aile için kalıcı oturma izni, ikamet zorunluluğu yok, "
            "Schengen erişimi, 7 yıl sonra vatandaşlık yolu. "
            "Amacınız: müşterinin ihtiyaçlarını anlamak, soruları yanıtlamak ve gerçek ilgi "
            "gösterdiğinde ad ve telefon numarası istemek. "
            "Yanıtlar kısa olsun (en fazla 4 cümle). "
            "Kullanıcı ad ve telefon numarası verirse tam olarak şunu yazın: "
            "LEAD_CAPTURE:{name}|{phone} "
            "ardından kısa bir teşekkür mesajı yazın."
        ),
    }
    system_prompt = _PROMPTS.get(language, (
        "You are a Golden Visa consultant at Adonis Group, specialists in Greek real estate. "
        "Always reply in English. "
        "Key facts: minimum investment €250,000 (€800,000 prime areas), "
        "permanent residency for whole family, no stay requirement, Schengen access, citizenship after 7 years. "
        "Goal: understand the visitor's needs, answer clearly, and when genuine interest is shown "
        "ask for their full name and phone number for a callback. "
        "Keep replies concise (max 4 sentences). "
        "When the user gives name and phone, reply with exactly: "
        "LEAD_CAPTURE:{name}|{phone} "
        "followed by a short thank-you message."
    ))

    messages = [{'role': 'system', 'content': system_prompt}]
    for h in (history or [])[-10:]:
        role = 'assistant' if h.get('role') in ('bot', 'assistant') else 'user'
        text = str(h.get('text', '')).strip()[:400]
        if text:
            messages.append({'role': role, 'content': text})
    messages.append({'role': 'user', 'content': message})

    try:
        client = OpenAI(api_key=api_key)
        resp   = client.chat.completions.create(
            model='gpt-4o-mini',
            messages=messages,
            max_tokens=400,
            temperature=0.65,
        )
        reply = resp.choices[0].message.content.strip()
    except Exception as exc:
        logging.getLogger(__name__).error('ai_chat_reply OpenAI error: %s', exc)
        return JsonResponse({'fallback': True})

    # ── Lead capture detection ────────────────────────────────────────────────
    action     = None
    lead_match = re.search(r'LEAD_CAPTURE:([^|\n]+)\|([^\n]+)', reply)
    if lead_match:
        lead_name  = lead_match.group(1).strip()[:100]
        lead_phone = lead_match.group(2).strip()[:30]
        reply      = reply.replace(lead_match.group(0), '').strip()
        try:
            submission = ContactSubmission.objects.create(
                full_name=lead_name,
                phone=lead_phone,
                email='',
                request_type='customer',
                source='ai_chat',
                notes=f'source:ai_consultation_chat | lang:{language} | page:{page_url}',
            )
            try:
                from core import telegram
                telegram.notify_new_contact(submission)
            except Exception:
                pass
            action = 'lead_saved'
        except Exception as exc2:
            logging.getLogger(__name__).error('ai_chat_reply lead save: %s', exc2)

    if action:
        return JsonResponse({'reply': reply, 'action': action})
    return JsonResponse({'reply': reply})


# ── Partnerships ───────────────────────────────────────────────────────────────

def partnerships(request):
    """Partnerships page"""
    partnership = PartnershipPageSettings.get_settings()
    benefits = []
    for i in range(1, 7):
        icon = getattr(partnership, f'benefit_{i}_icon', '')
        title = getattr(partnership, f'benefit_{i}_title', '')
        text = getattr(partnership, f'benefit_{i}_text', '')
        if icon or title:
            benefits.append({'icon': icon, 'title': title, 'text': text})

    seo = _seo(request, 'partnerships')
    return render(request, 'partnerships.html', {
        'partnership': partnership,
        'ps': partnership,
        'benefits': benefits,
        **seo,
    })


# ── Dashboard ─────────────────────────────────────────────────────────────────

@login_required
@user_passes_test(_can_access_dashboard)
def dashboard(request):
    """Custom admin dashboard — context is permission-filtered in the template."""
    try:
        from properties.models import Property, PropertyInterest
        property_count = Property.objects.count()
        interest_count = PropertyInterest.objects.count()
    except Exception:
        property_count = interest_count = 0

    ctx = {
        'contact_count': ContactSubmission.objects.count(),
        'unread_contact_count': ContactSubmission.objects.filter(is_read=False).count(),
        'property_count': property_count,
        'blog_count': BlogPost.objects.filter(is_published=True).count(),
    }
    return render(request, 'dashboard/index.html', ctx)


# ── Blog ──────────────────────────────────────────────────────────────────────

def blog_list(request):
    """Blog listing page"""
    from django.core.paginator import Paginator
    all_posts = BlogPost.objects.filter(is_published=True).order_by('-published_date')
    category_slug = request.GET.get('category', '')
    if category_slug:
        all_posts = all_posts.filter(category__slug=category_slug)
    categories = BlogCategory.objects.filter(is_active=True).order_by('order', 'name')
    paginator = Paginator(all_posts, 12)
    page = request.GET.get('page', 1)
    posts = paginator.get_page(page)
    seo = _seo(request, 'blog')
    return render(request, 'blog/list.html', {
        'posts': posts,
        'categories': categories,
        'selected_category': category_slug,
        **seo,
    })


def blog_detail(request, slug):
    """Blog detail page"""
    from django.shortcuts import get_object_or_404
    from django.db.models import Q
    post = get_object_or_404(BlogPost, Q(slug=slug) | Q(slug_en=slug) | Q(slug_tr=slug), is_published=True)
    # Increment views
    BlogPost.objects.filter(pk=post.pk).update(views=post.views + 1)

    related_posts = BlogPost.objects.filter(
        is_published=True
    ).exclude(pk=post.pk).order_by('-published_date')[:4]

    og_image = post.og_image.url if post.og_image else (post.featured_image.url if post.featured_image else '')

    from django.utils.translation import get_language
    lang = (get_language() or 'en').split('-')[0]

    return render(request, 'blog/detail.html', {
        'post': post,
        'related_posts': related_posts,
        'meta_title': post.get_seo_title(lang),
        'meta_description': post.get_meta_description(lang),
        'og_title': post.og_title or post.get_seo_title(lang),
        'og_description': post.og_description or post.get_meta_description(lang),
        'og_image': og_image,
        'canonical_url': post.canonical_url or request.build_absolute_uri(request.path),
        'robots_meta': 'noindex, follow' if (not post.robots_index or getattr(post, "noindex", False)) else 'index, follow',
    })


# ── API: admin dashboard stats ─────────────────────────────────────────────────

def admin_dashboard_stats(request):
    """API endpoint for admin dashboard statistics"""
    user = request.user
    if not (user.is_staff or has_any_role(user, ROLE_SUPERADMIN, ROLE_ADMIN, ROLE_SALES, ROLE_SUPPORT, ROLE_CONTENT)):
        return JsonResponse({'error': 'Unauthorized'}, status=403)

    try:
        from properties.models import Property, PropertyInterest
        property_count = Property.objects.count()
        interest_count = PropertyInterest.objects.filter(is_read=False).count()
    except Exception:
        property_count = interest_count = 0

    return JsonResponse({
        'contacts_unread': ContactSubmission.objects.filter(is_read=False).count(),
        'leads_new': ChatLead.objects.filter(status='new').count(),
        'properties': property_count,
        'interests_unread': interest_count,
        'blog_published': BlogPost.objects.filter(is_published=True).count(),
    })


# ── Testimonial detail ─────────────────────────────────────────────────────────

def testimonial_detail(request, pk):
    """Single testimonial detail page"""
    from django.shortcuts import get_object_or_404
    testimonial = get_object_or_404(Testimonial, pk=pk, is_active=True)
    related = Testimonial.objects.filter(is_active=True).exclude(pk=pk).order_by('-created_at')[:4]
    return render(request, 'testimonial_detail.html', {
        'testimonial': testimonial,
        'related': related,
    })


# ── Upload video ───────────────────────────────────────────────────────────────

@login_required
def upload_video(request):
    """Large video upload page - handles big file uploads via AJAX"""
    if request.method == 'POST':
        from django.core.files.storage import default_storage
        from django.utils.text import get_valid_filename
        video_file = request.FILES.get('video')
        if not video_file:
            return JsonResponse({'error': 'No video file provided'})
        target = request.POST.get('target', '')
        filename = get_valid_filename(video_file.name)
        path = default_storage.save(f'uploads/{filename}', video_file)
        url = default_storage.url(path)

        # Update the target model
        if target == 'partnership':
            obj = PartnershipPageSettings.objects.first()
            if obj:
                snapshot = model_snapshot(obj)
                obj.video = path
                obj.save(update_fields=['video'])
                log_audit_event(actor=request.user, action='update', instance=obj, snapshot=snapshot)
        elif target == 'header':
            obj = HeaderSettings.objects.first()
            if obj:
                snapshot = model_snapshot(obj)
                obj.hero_video = path
                obj.save(update_fields=['hero_video'])
                log_audit_event(actor=request.user, action='update', instance=obj, snapshot=snapshot)

        return JsonResponse({'url': url, 'path': path})

    return render(request, 'admin/upload_video.html', {})


# ── Golden Visa card detail ────────────────────────────────────────────────────

def golden_visa_card_detail(request, slug):
    """Detail page for a Golden Visa investment tier card."""
    from django.shortcuts import get_object_or_404
    card = get_object_or_404(GoldenVisaCard, pk=slug)
    related_cards = GoldenVisaCard.objects.filter(is_active=True).exclude(pk=card.pk).order_by('order')
    return render(request, 'golden_visa_card_detail.html', {
        'card': card,
        'related_cards': related_cards,
    })


# ── Events ────────────────────────────────────────────────────────────────────

def event_list(request):
    """List all active events"""
    events = Event.objects.filter(is_active=True).order_by('order', '-event_date', '-created_at')
    seo = _seo(request, 'events') if hasattr(request, 'path') else {}
    return render(request, 'events/list.html', {'events': events, **seo})


def event_detail(request, slug):
    """Detail page for a single event with all photos"""
    from django.shortcuts import get_object_or_404
    from django.db.models import Q
    event = get_object_or_404(
        Event,
        Q(slug=slug) | Q(slug_en=slug) | Q(slug_tr=slug),
        is_active=True,
    )
    images = event.images.filter(is_active=True).order_by('order')
    related_events = Event.objects.filter(is_active=True).exclude(pk=event.pk).order_by('order')[:4]
    return render(request, 'events/detail.html', {
        'event': event,
        'images': images,
        'related_events': related_events,
    })


# ── Partner lead ──────────────────────────────────────────────────────────────

def submit_partner_lead(request):
    """AJAX endpoint: validate & save a partnership enquiry, then email marketing."""
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)

    honeypot = request.POST.get('website', '')
    if honeypot:
        return JsonResponse({'success': False, 'error': 'Spam detected.'})

    first_name = request.POST.get('first_name', '').strip()
    last_name = request.POST.get('last_name', '').strip()
    email = request.POST.get('email', '').strip()
    phone = request.POST.get('phone', '').strip()
    partner_type = request.POST.get('partner_type', '').strip().lower()
    other_title = request.POST.get('other_title', '').strip() or None
    country = request.POST.get('country', '').strip() or None
    company = request.POST.get('company', '').strip() or None
    message_text = request.POST.get('message', '').strip() or None
    consent = request.POST.get('consent', '') == '1'

    if not all([first_name, last_name, email, phone, partner_type]):
        return JsonResponse({'success': False, 'error': 'Required fields missing.'})
    if partner_type not in _VALID_PARTNER_TYPES:
        return JsonResponse({'success': False, 'error': 'Invalid partner type.'})
    if not re.match(r'^[^@]+@[^@]+\.[^@]+$', email):
        return JsonResponse({'success': False, 'error': 'Invalid email.'})

    lead = PartnerLead.objects.create(
        first_name=first_name,
        last_name=last_name,
        email=email,
        phone=phone,
        partner_type=partner_type,
        other_title=other_title,
        country=country,
        company=company,
        message=message_text,
        consent=consent,
        source='partnerships_page',
    )

    try:
        _send_partner_lead_emails(lead)
    except Exception as e:
        logger.exception('Partner lead email failed: %s', e)

    try:
        telegram.notify_partner_lead(lead)
    except Exception:
        pass

    return JsonResponse({'success': True})


def _send_partner_lead_emails(lead):
    """Send notification emails for a new partner lead."""
    from django.conf import settings
    from django.core.mail import send_mail
    from django.template.loader import render_to_string

    subject = f'New Partner Enquiry: {lead.get_partner_type_display()} — {lead.first_name} {lead.last_name}'
    body = (
        f'Name: {lead.first_name} {lead.last_name}\n'
        f'Email: {lead.email}\n'
        f'Phone: {lead.phone}\n'
        f'Type: {lead.partner_type}\n'
        f'Country: {lead.country or "-"}\n'
        f'Company: {lead.company or "-"}\n'
        f'Message: {lead.message or "-"}\n'
    )
    marketing_email = getattr(settings, 'MARKETING_EMAIL', '')
    if marketing_email:
        try:
            send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, [marketing_email], fail_silently=True)
        except Exception:
            pass


# ── Greek Golden Visa landing ──────────────────────────────────────────────────

def greek_golden_visa(request):
    """Landing page for the Greek Golden Visa programme."""
    page = GoldenVisaLandingPage.get_settings()
    recent_posts = BlogPost.objects.filter(
        is_published=True,
        category__slug='golden-visa',
    ).select_related('category').order_by('-published_date')[:3]
    if not recent_posts.exists():
        recent_posts = BlogPost.objects.filter(
            is_published=True
        ).order_by('-published_date')[:3]

    from django.utils.translation import get_language
    lang = (get_language() or 'en').split('-')[0]

    og_image_obj = page.hero_image
    og_image = og_image_obj.url if og_image_obj else ''

    faqs = FAQ.objects.filter(is_active=True).order_by('order')
    gv_cards = GoldenVisaCard.objects.filter(is_active=True).order_by('order')

    ctx = {
        'page': page,
        'recent_posts': recent_posts,
        'faqs': faqs,
        'golden_visa_cards': gv_cards,
        'og_image': og_image,
        'meta_title': getattr(page, 'meta_title', '') or page.hero_title,
        'meta_description': getattr(page, 'meta_description', ''),
        'canonical_url': getattr(page, 'canonical_url', '') or request.build_absolute_uri(request.path),
        'og_title': getattr(page, 'og_title', '') or (getattr(page, 'meta_title', '') or page.hero_title),
        'og_description': getattr(page, 'og_description', '') or getattr(page, 'meta_description', ''),
        'robots_meta': 'noindex, follow' if getattr(page, 'noindex', False) else ('index, follow' if getattr(page, 'robots_index', True) else 'noindex, follow'),
    }
    return render(request, 'landing/golden_visa.html', ctx)


# ── FA Landing page ───────────────────────────────────────────────────────────

def _fa_benefits_with_icons(benefits_text: str) -> list:
    """Parse benefit items from text for FA landing page."""
    if not benefits_text:
        return []
    items = []
    for line in benefits_text.strip().split('\n'):
        line = line.strip()
        if line:
            items.append({'text': line})
    return items


def greece_golden_visa_fa_ads(request):
    """Persian high-conversion landing page for Google Ads campaigns."""
    page = GoldenVisaFaLandingPage.get_settings()

    # Hero overlay opacity
    hero_image_opacity = max(0, min(100, int(getattr(page, 'hero_image_opacity', 70) or 70)))
    hero_content_vertical_align = getattr(page, 'hero_content_vertical_align', 'bottom') or 'bottom'
    hero_content_horizontal_align = getattr(page, 'hero_content_horizontal_align', 'right') or 'right'
    hero_title_color = getattr(page, 'hero_title_color', '#FFFFFF') or '#FFFFFF'
    hero_subtitle_color = getattr(page, 'hero_subtitle_color', '#F3F6FB') or '#F3F6FB'

    # Normalize intro HTML
    intro_text = _normalize_fa_intro_html(getattr(page, 'intro_text', '') or '')

    # Build intro bullets and features
    bullets = []
    for i in range(1, 4):
        bullet = getattr(page, f'intro_bullet_{i}', '')
        if bullet and str(bullet).strip():
            bullets.append(str(bullet).strip())

    features = []
    for i in range(1, 4):
        icon = getattr(page, f'intro_feature_{i}_icon', '')
        text = getattr(page, f'intro_feature_{i}_text', '')
        if icon or text:
            features.append({'icon': icon, 'text': text})

    # Why Adonis items
    why_items = []
    for i in range(1, 5):
        icon = getattr(page, f'why_item_{i}_icon', '')
        title = getattr(page, f'why_item_{i}_title', '')
        text = getattr(page, f'why_item_{i}_text', '')
        if icon or title:
            why_items.append({'icon': icon, 'title': title, 'text': text})

    # Tier cards
    tiers = []
    for i in range(1, 4):
        tiers.append({
            'title': getattr(page, f'tier_{i}_title', ''),
            'short_desc': getattr(page, f'tier_{i}_short_desc', ''),
            'long_desc': getattr(page, f'tier_{i}_long_desc', ''),
            'price_label': getattr(page, f'tier_{i}_price_label', ''),
            'price_amount': getattr(page, f'tier_{i}_price_amount', ''),
            'image': getattr(page, f'tier_{i}_image', None),
            'image_alt': getattr(page, f'tier_{i}_image_alt', ''),
            'cta_text': getattr(page, f'tier_{i}_cta_text', ''),
        })

    # Benefits
    benefits = _fa_benefits_with_icons(page.benefits_text or '')

    # Process steps (dynamic from DB; fallback to old text field if empty)
    fa_process_steps = list(
        GoldenVisaFaProcessStep.objects.filter(is_active=True)
        .order_by('display_order', 'step_number')
    )

    # Own shorts — convert to embed URLs
    own_shorts = [
        _to_youtube_embed(getattr(page, f'own_short_video_url_{i}', ''))
        for i in range(1, 5)
        if getattr(page, f'own_short_video_url_{i}', '')
    ]
    testimonial_shorts = [
        _to_youtube_embed(getattr(page, f'testimonial_short_video_url_{i}', ''))
        for i in range(1, 5)
        if getattr(page, f'testimonial_short_video_url_{i}', '')
    ]

    # Featured properties for the "sample properties" section
    from properties.models import Property as PropertyModel
    featured_properties_fa = list(
        PropertyModel.objects.filter(is_active=True, golden_visa_eligible=True)
        .order_by('-is_featured', 'display_order', '-pk')[:3]
    )

    ctx = {
        'page': page,
        'hero_image_opacity': hero_image_opacity,
        'hero_content_vertical_align': hero_content_vertical_align,
        'hero_content_horizontal_align': hero_content_horizontal_align,
        'hero_title_color': hero_title_color,
        'hero_subtitle_color': hero_subtitle_color,
        'intro_text': intro_text,
        'intro_bullets': bullets,
        'intro_features': features,
        'why_items': why_items,
        'tiers': tiers,
        'benefits': benefits,
        'fa_process_steps': fa_process_steps,
        'own_shorts': own_shorts,
        'testimonial_shorts': testimonial_shorts,
        'featured_properties_fa': featured_properties_fa,
        'meta_title': page.seo_title or '',
        'meta_description': page.meta_description or '',
        'canonical_url': getattr(page, 'canonical_url', '') or request.build_absolute_uri(request.path),
        'og_title': getattr(page, 'og_title', '') or (page.seo_title or ''),
        'og_description': getattr(page, 'og_description', '') or (page.meta_description or ''),
        'og_image': page.og_image.url if getattr(page, 'og_image', None) else '',
        'robots_meta': 'noindex, follow' if getattr(page, 'noindex', False) else ('index, follow' if getattr(page, 'robots_index', True) else 'noindex, follow'),
    }
    return render(request, 'landing/golden_visa_fa.html', ctx)


# ── Chat session ───────────────────────────────────────────────────────────────

def _get_visitor_ip(request):
    forwarded = request.META.get('HTTP_X_FORWARDED_FOR', '')
    if forwarded:
        return forwarded.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


def _get_or_create_session(session_key, page_url='', request=None):
    """Return (session, created). Creates only if key is unknown."""
    try:
        return ChatSession.objects.get(session_key=session_key), False
    except ChatSession.DoesNotExist:
        ip = _get_visitor_ip(request) if request else None
        session = ChatSession.objects.create(
            session_key=session_key,
            phase=PHASE_BOT,
            page_url=page_url,
            visitor_ip=ip,
        )
        return session, True


@csrf_protect
def chat_session_start(request):
    """Create or resume a session. Returns phase + agent name if human."""
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    session_key = str(data.get('session_key', '')).strip()
    if not session_key:
        return JsonResponse({'error': 'session_key required'}, status=400)
    page_url = str(data.get('page_url', '')).strip()

    session, _ = _get_or_create_session(session_key, page_url, request)

    agent_name = ''
    if session.agent:
        agent_name = session.agent.get_full_name() or session.agent.username

    return JsonResponse({'phase': session.phase, 'agent': agent_name})


@csrf_protect
def chat_notify_agent(request):
    """
    Called when the frontend detects serious interest.
    Stores the conversation so far, transitions phase → pending_agent,
    and fires a Telegram notification to agents.
    """
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    session_key = str(data.get('session_key', '')).strip()
    page_url = str(data.get('page_url', '')).strip()
    messages_data = data.get('messages', [])
    trigger = str(data.get('trigger', 'interest')).strip()

    session, _ = _get_or_create_session(session_key, page_url, request)

    if session.phase not in (PHASE_BOT, PHASE_WAIT):
        return JsonResponse({'phase': session.phase, 'ok': True})

    from django.utils import timezone
    session.phase = PHASE_WAIT
    session.agent_notified_at = timezone.now()
    session.save(update_fields=['phase', 'agent_notified_at'])

    # Store messages
    for msg in messages_data:
        role = str(msg.get('role', 'user'))
        content = str(msg.get('content', ''))
        if content.strip():
            ChatSessionMessage.objects.get_or_create(
                session=session,
                role=role,
                content=content,
            )

    return JsonResponse({'phase': session.phase, 'ok': True, 'count': str(len(messages_data))})


@csrf_protect
def chat_user_message(request):
    """
    User sends a message in pending_agent or human phase.
    Returns latest agent messages since last_id (if any).
    """
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    session_key = str(data.get('session_key', '')).strip()
    content = str(data.get('content', '')).strip()
    last_id = int(data.get('last_id', 0) or 0)

    if not session_key or not content:
        return JsonResponse({'error': 'Missing fields'}, status=400)

    try:
        session = ChatSession.objects.get(session_key=session_key)
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Unknown session'}, status=404)

    if session.phase == PHASE_CLOSED:
        return JsonResponse({'phase': PHASE_CLOSED, 'messages': []})

    msg = ChatSessionMessage.objects.create(
        session=session,
        role='user',
        content=content,
        is_read=False,
    )
    from django.utils import timezone
    session.updated_at = timezone.now()
    session.save(update_fields=['updated_at'])

    # Return agent messages since last_id
    new_msgs = list(
        session.messages.filter(id__gt=last_id, role='assistant').values(
            'id', 'role', 'content', 'created_at'
        )
    )
    return JsonResponse({'phase': session.phase, 'messages': new_msgs})


def chat_poll(request):
    """
    GET poll: returns new messages and current phase since last_id.
    Frontend calls this every ~4 s while in pending_agent / human phase.
    """
    session_key = request.GET.get('session_key', '').strip()
    last_id = int(request.GET.get('last_id', 0) or 0)

    if not session_key:
        return JsonResponse({'error': 'Missing session_key'}, status=400)

    try:
        session = ChatSession.objects.select_related('agent').get(session_key=session_key)
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Unknown session'}, status=404)

    new_msgs = list(
        session.messages.filter(id__gt=last_id, role='assistant').exclude(
            role='user'
        ).values('id', 'role', 'content', 'created_at')
    )
    for m in new_msgs:
        if m.get('created_at'):
            m['created_at'] = m['created_at'].isoformat()

    # Mark read
    session.messages.filter(id__gt=last_id, role='assistant', is_read=False).update(is_read=True)

    agent_name = ''
    if session.agent:
        agent_name = session.agent.get_full_name() or session.agent.username

    return JsonResponse({
        'phase': session.phase,
        'agent': agent_name,
        'messages': new_msgs,
    })


# ── Agent views ────────────────────────────────────────────────────────────────

def _is_staff(user):
    return user.is_active and user.is_staff


@login_required
@user_passes_test(_is_staff)
def agent_chat_inbox(request):
    """Live-chat inbox for agents — lists sessions needing attention."""
    sessions = (
        ChatSession.objects.filter(phase__in=[PHASE_WAIT, PHASE_HUMAN])
        .select_related('agent', 'lead')
        .prefetch_related('messages')
        .order_by('-updated_at')
    )
    return render(request, 'admin/chat/inbox.html', {'sessions': sessions})


@login_required
@user_passes_test(_is_staff)
def agent_chat_session(request, session_key):
    """Detail view for a single session — shows full transcript."""
    try:
        session = ChatSession.objects.select_related('agent', 'lead').get(session_key=session_key)
    except ChatSession.DoesNotExist:
        from django.http import Http404
        raise Http404

    messages_qs = session.messages.order_by('created_at').filter(role__in=['user', 'assistant'])
    messages_qs.filter(role='user', is_read=False).update(is_read=True)

    if session.phase == PHASE_WAIT and not session.agent:
        session.phase = PHASE_HUMAN
        session.agent = request.user
        session.save(update_fields=['phase', 'agent'])

    return render(request, 'admin/chat/session.html', {
        'session': session,
        'chat_messages': messages_qs,
    })


@login_required
@user_passes_test(_is_staff)
def agent_takeover(request, session_key):
    """Agent claims the session → phase becomes 'human'."""
    try:
        session = ChatSession.objects.get(session_key=session_key)
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

    session.phase = PHASE_HUMAN
    session.agent = request.user
    session.save(update_fields=['phase', 'agent'])

    return JsonResponse({
        'phase': session.phase,
        'agent': request.user.get_full_name() or request.user.username,
    })


@login_required
@user_passes_test(_is_staff)
def agent_send_message(request, session_key):
    """Agent sends a reply to the visitor."""
    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, ValueError):
        return JsonResponse({'error': 'Invalid JSON'}, status=400)

    content = str(data.get('content', '')).strip()
    if not content:
        return JsonResponse({'error': 'Empty message'}, status=400)

    try:
        session = ChatSession.objects.select_related('agent').get(session_key=session_key)
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

    msg = ChatSessionMessage.objects.create(
        session=session,
        role='assistant',
        content=content,
        is_read=False,
    )
    from django.utils import timezone
    session.updated_at = timezone.now()
    session.save(update_fields=['updated_at'])

    return JsonResponse({
        'id': msg.id,
        'role': msg.role,
        'content': msg.content,
        'created_at': msg.created_at.isoformat(),
    })


@login_required
@user_passes_test(_is_staff)
def agent_close_session(request, session_key):
    """Close a session."""
    try:
        session = ChatSession.objects.get(session_key=session_key)
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

    session.phase = PHASE_CLOSED
    from django.utils import timezone
    session.updated_at = timezone.now()
    session.save(update_fields=['phase', 'updated_at'])

    return JsonResponse({'phase': PHASE_CLOSED, 'ok': True})


@login_required
@user_passes_test(_is_staff)
def agent_poll(request, session_key):
    """Agent-side poll: returns new user messages since last_id."""
    if not request.user.is_authenticated or not request.user.is_staff:
        return JsonResponse({'error': 'Forbidden'}, status=403)

    last_id = int(request.GET.get('last_id', 0) or 0)

    try:
        session = ChatSession.objects.select_related('agent').get(session_key=session_key)
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Not found'}, status=404)

    new_msgs = list(
        session.messages.filter(id__gt=last_id, role='user').values(
            'id', 'role', 'content', 'created_at'
        )
    )
    for m in new_msgs:
        if m.get('created_at'):
            m['created_at'] = m['created_at'].isoformat()

    session.messages.filter(id__gt=last_id, role='user', is_read=False).update(is_read=True)

    return JsonResponse({
        'phase': session.phase,
        'agent': request.user.get_full_name() or request.user.username,
        'messages': new_msgs,
    })


# ── Webinar Landing (FA) ──────────────────────────────────────────────────────
# Public landing page + AJAX registration endpoint for the Persian webinar
# campaign aimed at Iranian investors in UAE / Turkey. Fully isolated.

_WEBINAR_EMAIL_RE = re.compile(r'^[^@\s]+@[^@\s]+\.[^@\s]+$')


def _webinar_clean_phone(raw: str) -> str:
    """Trim phone and keep only allowed characters (digits, +, space, -, parens)."""
    if not raw:
        return ''
    cleaned = ''.join(ch for ch in raw if ch.isdigit() or ch in '+-() ')
    return cleaned.strip()


def webinar_landing(request):
    """Public view for the Persian webinar landing page."""
    from django.http import Http404

    settings_obj = WebinarLandingSettings.get_settings()
    if not settings_obj.active_status:
        raise Http404('Webinar landing is currently disabled.')

    ctx = {
        'settings': settings_obj,
        'meta_title': settings_obj.meta_title or 'وبینار تخصصی اقامت و سرمایه‌گذاری اروپا',
        'meta_description': settings_obj.meta_description or '',
        'canonical_url': settings_obj.canonical_url or request.build_absolute_uri(request.path),
        'og_title': settings_obj.og_title or settings_obj.meta_title or 'وبینار تخصصی اقامت و سرمایه‌گذاری اروپا',
        'og_description': settings_obj.og_description or settings_obj.meta_description or '',
        'og_image': settings_obj.og_image.url if settings_obj.og_image else '',
        'robots_meta': 'noindex, follow' if settings_obj.noindex else 'index, follow',
    }
    return render(request, 'landing/webinar.html', ctx)


@require_POST
@csrf_protect
def webinar_register(request):
    """AJAX endpoint that stores a WebinarRegistration row."""

    honeypot = request.POST.get('webinar_company', '')
    if honeypot:
        return JsonResponse({'success': False, 'errors': {'__all__': ['Spam detected.']}})

    first_name = (request.POST.get('first_name') or '').strip()
    last_name = (request.POST.get('last_name') or '').strip()
    phone = _webinar_clean_phone(request.POST.get('phone') or '')
    email = (request.POST.get('email') or '').strip()

    errors = {}
    if not first_name or len(first_name) < 2:
        errors['first_name'] = ['نام معتبر وارد کنید.']
    if not last_name or len(last_name) < 2:
        errors['last_name'] = ['نام خانوادگی معتبر وارد کنید.']
    if not phone or sum(ch.isdigit() for ch in phone) < 7:
        errors['phone'] = ['شماره تماس معتبر وارد کنید.']
    if not email or not _WEBINAR_EMAIL_RE.match(email):
        errors['email'] = ['ایمیل معتبر وارد کنید.']

    if errors:
        return JsonResponse({'success': False, 'errors': errors}, status=400)

    registration = WebinarRegistration.objects.create(
        first_name=first_name[:100],
        last_name=last_name[:100],
        phone=phone[:40],
        email=email[:200],
    )

    try:
        log_audit_event(
            action='create',
            obj=registration,
            user=request.user if request.user.is_authenticated else None,
            request=request,
            after=model_snapshot(registration),
            metadata={'source': 'webinar_landing'},
        )
    except Exception:
        logger.exception('webinar: audit log failed')

    try:
        _webinar_notify_telegram(registration)
    except Exception:
        logger.exception('webinar: telegram notify failed')

    return JsonResponse({'success': True, 'id': registration.pk})


def _webinar_notify_telegram(reg):
    """Send a short Telegram notification when a new registration arrives."""
    from django.conf import settings as django_settings
    bot_token = getattr(django_settings, 'TELEGRAM_BOT_TOKEN', '') or ''
    chat_id = getattr(django_settings, 'TELEGRAM_CHAT_ID', '') or ''
    if not bot_token or not chat_id:
        return
    msg = (
        '🎯 <b>ثبت‌نام جدید — وبینار اقامت اروپا</b>\n\n'
        f'👤 <b>{reg.first_name} {reg.last_name}</b>\n'
        f'📱 <code>{reg.phone}</code>\n'
        f'✉️ <code>{reg.email}</code>\n'
        f'🕒 {reg.created_at.strftime("%Y-%m-%d %H:%M") if reg.created_at else "-"}'
    )
    try:
        from core.telegram import send_telegram_message
        send_telegram_message(bot_token, chat_id, msg, parse_mode='HTML')
    except Exception:
        logger.exception('webinar: send_telegram_message failed')


# ── Persian (fa) prototype homepage ──────────────────────────────────────────
# Isolated visual prototype rendered at /fa-new/ . Reads its own dedicated
# FaNewSettings singleton (separate from the English HeaderSettings) so the
# team can upload a Persian-only cinematic hero video without affecting the
# English site or any existing /fa/... ad landing pages.
def fa_new_home(request):
    from core.models import FaNewSettings, FaNewFeaturedProperties, FaNewSection, FaNavMenuItem, FaFooterSettings
    fa_new = FaNewSettings.get_settings()

    if fa_new.hero_video:
        hero_video_url = fa_new.hero_video.url
    else:
        hero_video_url = '/media/hero/adonis-hero-scroll.mp4'

    # Lighter variant for phones (client-side selected; cache-safe). Falls back
    # to the desktop file when no "_web" variant naming is present.
    hero_video_url_mobile = hero_video_url.replace('_web.mp4', '_mobile.mp4')

    if fa_new.hero_video_poster:
        hero_video_poster_url = fa_new.hero_video_poster.url
    else:
        hero_video_poster_url = '/media/hero/adonis-hero-scroll-poster.jpg'

    header_logo_url = fa_new.header_logo.url if fa_new.header_logo else None

    user_agent = (request.META.get('HTTP_USER_AGENT') or '').lower()
    is_mobile_request = any(token in user_agent for token in ('mobile', 'android', 'iphone', 'ipad'))

    section_qs = FaNewSection.objects.filter(is_active=True)
    if is_mobile_request:
        section_qs = section_qs.filter(show_on_mobile=True)
    else:
        section_qs = section_qs.filter(show_on_desktop=True)

    sections = list(
        section_qs.prefetch_related('items', 'gateway_cards').order_by('order', 'id')
    )
    benefits_section = next(
        (section for section in sections if section.section_type == 'why_greece'),
        None,
    )

    default_benefits = [
        {
            'title': 'سفر آزاد در شنگن',
            'description': 'امکان سفر به کشورهای حوزه شنگن بدون نیاز به دریافت ویزای جداگانه.',
        },
        {
            'title': 'بدون شرط حضور',
            'description': 'اقامت یونان از طریق Golden Visa نیازی به زندگی دائم در یونان ندارد.',
        },
        {
            'title': 'اقامت برای خانواده',
            'description': 'امکان دریافت اقامت برای همسر، فرزندان و والدین طبق شرایط قانونی برنامه.',
        },
        {
            'title': 'سرمایه گذاری ملکی',
            'description': 'دریافت اقامت از طریق خرید ملک واجد شرایط و امکان حفظ ارزش سرمایه در اروپا.',
        },
    ]

    benefit_items = []
    if benefits_section is not None:
        all_items = list(benefits_section.items.all().order_by('order', 'id'))
        # Active toggle for cards: if any item is marked featured, only featured
        # cards are shown. Otherwise all cards stay visible.
        if any(item.is_featured for item in all_items):
            all_items = [item for item in all_items if item.is_featured]
        benefit_items = all_items[:4]

    benefits_cards = []
    for index, fallback in enumerate(default_benefits, start=1):
        item = benefit_items[index - 1] if index - 1 < len(benefit_items) else None
        title = fallback['title']
        description = fallback['description']
        image_url = ''
        image_alt = fallback['title']

        if item is not None:
            title = (item.title or fallback['title']).strip()
            description = (
                item.effective_description
                or item.subtitle
                or item.body
                or fallback['description']
            ).strip()
            if item.image:
                image_url = item.image.url
                image_alt = item.image_alt or title

        benefits_cards.append({
            'title': title,
            'description': description,
            'image_url': image_url,
            'image_alt': image_alt,
            'icon_key': str(index),
        })

    sections_render = [section for section in sections if section.section_type != 'why_greece']
    benefits_anchor_id = (
        benefits_section.resolved_anchor_id if benefits_section else 'fa-section-why_greece'
    )
    benefits_eyebrow = (
        benefits_section.eyebrow.strip()
        if benefits_section and benefits_section.eyebrow
        else 'مزایای اقامت یونان'
    )
    benefits_title = (
        benefits_section.title.strip()
        if benefits_section and benefits_section.title
        else '۴ مزیت کلیدی اقامت یونان'
    )
    benefits_subtitle = (
        benefits_section.subtitle.strip()
        if benefits_section and benefits_section.subtitle
        else 'اقامت یونان فقط یک کارت نیست؛ یک مسیر مطمئن برای سفر، خانواده و سرمایه در اروپاست.'
    )
    benefits_bg_image = None
    if benefits_section:
        benefits_bg_image = (
            getattr(benefits_section, "background_image", None)
            or getattr(benefits_section, "section_image", None)
        )
    benefits_bg_image_url = benefits_bg_image.url if benefits_bg_image else ''
    benefits_bg_opacity = (
        getattr(benefits_section, "background_image_opacity", 50) / 100
        if benefits_section else 0.50
    )
    benefits_bg_position = 'center center' if benefits_section else 'center center'

    # Featured property projects for the homepage carousel.
    # Uses FaProperty (Persian properties from persian_cms app) - completely separate from English.
    # If 5 specific properties are selected via FaNewFeaturedProperties, use those;
    # otherwise fallback to all active FaProperty records ordered by display_order.
    featured_properties = []
    try:
        from apps.persian_cms.models import FaProperty
        
        # First, try to get the 5 manually selected featured properties
        featured_settings = FaNewFeaturedProperties.get_settings()
        selected_props = featured_settings.get_properties_list()
        
        if selected_props:
            # Use the manually selected properties
            for p in selected_props:
                # Skip inactive properties
                if not getattr(p, 'is_active', True):
                    continue
                img = ''
                mi = getattr(p, 'main_image', None)
                if mi:
                    try:
                        img = mi.url
                    except Exception:
                        img = ''
                featured_properties.append({
                    'name': (p.name or '').strip(),
                    'location': (p.location or '').strip(),
                    'price_label': (p.price_label or '').strip(),
                    'area': (p.area or '').strip(),
                    'image_url': img,
                    'url': p.get_absolute_url(),
                })
        else:
            # Fallback: use all active FaProperty records if no manual selection exists
            fp_qs = FaProperty.objects.filter(is_active=True, is_featured=True).order_by('display_order', '-created_at')[:12]
            if not fp_qs.exists():
                fp_qs = FaProperty.objects.filter(is_active=True).order_by('display_order', '-created_at')[:12]
            for p in fp_qs:
                img = ''
                mi = getattr(p, 'main_image', None)
                if mi:
                    try:
                        img = mi.url
                    except Exception:
                        img = ''
                featured_properties.append({
                    'name': (p.name or '').strip(),
                    'tagline': (p.tagline or '').strip(),
                    'short_description': (p.short_description or '').strip(),
                    'location': (p.location or '').strip(),
                    'price_label': (p.price_label or '').strip(),
                    'area': (p.area or '').strip(),
                    'property_type': p.get_property_type_display() if hasattr(p, 'get_property_type_display') else '',
                    'image_url': img,
                    'url': p.get_absolute_url(),
                })
    except Exception:
        featured_properties = []

    section_anchor_map = {
        section.section_type: section.resolved_anchor_id
        for section in sections
    }
    consult_anchor = section_anchor_map.get('consult', 'fa-section-consult')
    projects_anchor = section_anchor_map.get('projects', 'fa-section-projects')

    nav_items = (
        FaNavMenuItem.objects
        .filter(is_active=True)
        .prefetch_related('children')
        .order_by('order')
    )

    footer = FaFooterSettings.get_settings()

    return render(request, 'fa_new/home.html', {
        'meta_title': 'آدونیس | اقامت یونان از مسیر سرمایه‌گذاری',
        'meta_description': (
            'با پروژه‌های اختصاصی آدونیس در آتن، اقامت یونان و دسترسی به '
            'اروپا را برای خود و خانواده‌تان فراهم کنید.'
        ),
        'canonical_url': request.build_absolute_uri(request.path),
        'og_title': 'آدونیس | اقامت یونان از مسیر سرمایه‌گذاری',
        'og_description': (
            'با پروژه‌های اختصاصی آدونیس در آتن، اقامت یونان و دسترسی به '
            'اروپا را برای خود و خانواده‌تان فراهم کنید.'
        ),
        'robots_content': 'index, follow',
        'hero_video_url': hero_video_url,
        'hero_video_url_mobile': hero_video_url_mobile,
        'hero_video_poster_url': hero_video_poster_url,
        'header_logo_url': header_logo_url,
        'fa': fa_new,        # legacy alias kept for other template references
        'settings': fa_new,  # primary alias — use {{ settings.field_name }}
        'sections': sections,
        'sections_render': sections_render,
        'section_anchor_map': section_anchor_map,
        'consult_anchor': consult_anchor,
        'projects_anchor': projects_anchor,
        'benefits_section': benefits_section,
        'benefits_cards': benefits_cards,
        'benefits_anchor_id': benefits_anchor_id,
        'benefits_eyebrow': benefits_eyebrow,
        'benefits_title': benefits_title,
        'benefits_subtitle': benefits_subtitle,
        'benefits_bg_image_url': benefits_bg_image_url,
        'benefits_bg_opacity': benefits_bg_opacity,
        'benefits_bg_position': benefits_bg_position,
        'is_mobile_request': is_mobile_request,
        'nav_items': nav_items,
        'footer': footer,
        'featured_properties': featured_properties,
    })
