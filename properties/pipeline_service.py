"""
FA SEO Content Pipeline — service layer.

All external calls (Google Suggest, Claude, Unsplash) are isolated here so the
admin and management commands can share the same logic.
"""
import logging
import re
import traceback

import requests
from django.conf import settings
from django.utils import timezone

logger = logging.getLogger(__name__)

# ── Keyword → English translation map ────────────────────────────────────────

_FA_TO_EN = {
    'یونان':       'greece',
    'اقامت':       'residence greece',
    'مهاجرت':      'immigration greece',
    'ملک':         'property greece',
    'خرید ملک':   'buy property greece',
    'گلدن ویزا':  'golden visa greece',
    'سرمایه‌گذاری': 'investment greece',
    'آتن':         'athens',
    'اقامت دائم': 'permanent residence greece',
    'پاسپورت':     'passport greece',
    'شهروندی':     'citizenship greece',
}


def _fa_keyword_to_en(keyword: str) -> str:
    """Best-effort Persian→English translation for Unsplash/API queries."""
    for fa, en in _FA_TO_EN.items():
        if fa in keyword:
            return en
    return 'greece property real estate'


# ── Google Suggest ────────────────────────────────────────────────────────────

def get_google_suggestions(keyword: str) -> list[str]:
    """
    Fetch autocomplete suggestions from Google for *keyword*.
    Tries both Persian (hl=fa) and English (hl=en) locales and merges results.
    Returns up to 15 unique suggestions.
    """
    suggestions: list[str] = []
    base_url = 'https://suggestqueries.google.com/complete/search'
    params_base = {
        'q':      keyword,
        'client': 'firefox',
        'gl':     'gr',
    }
    headers = {'User-Agent': 'Mozilla/5.0 (compatible; AdonisBot/1.0)'}

    for hl in ('fa', 'en'):
        try:
            resp = requests.get(
                base_url,
                params={**params_base, 'hl': hl},
                headers=headers,
                timeout=8,
            )
            resp.raise_for_status()
            data = resp.json()
            # Google returns [query, [suggestion1, suggestion2, ...], ...]
            if isinstance(data, list) and len(data) > 1 and isinstance(data[1], list):
                for s in data[1]:
                    if s and s not in suggestions:
                        suggestions.append(s)
        except Exception as exc:
            logger.warning('Google suggest failed (hl=%s): %s', hl, exc)

    # Always include the original keyword
    if keyword not in suggestions:
        suggestions.insert(0, keyword)

    return suggestions[:15]


# ── Claude Content Generation ─────────────────────────────────────────────────

def generate_content_with_claude(keyword: str, keywords_list: list[str]) -> dict:
    """
    Generate a full SEO blog post in Persian using Claude.
    Returns a dict with keys: title, slug, meta_title, meta_description,
    focus_keywords, excerpt, content.
    """
    try:
        import anthropic
    except ImportError:
        raise RuntimeError(
            'anthropic package is not installed. Run: pip install anthropic'
        )

    api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')
    if not api_key:
        raise RuntimeError(
            'ANTHROPIC_API_KEY is not set in Django settings / .env file.'
        )

    client = anthropic.Anthropic(api_key=api_key)

    kw_list_str = '، '.join(keywords_list[:10])

    prompt = f"""شما مشاور ارشد آدونیس گروپ (adonisgroup.gr) هستید با ۱۵ سال تجربه در حوزه املاک یونان و حقوق مهاجرت. این مقاله را به عنوان یک متخصص واقعی بنویسید که تجربیات و دانش عمیق خود را به اشتراک می‌گذارد، نه به عنوان یک هوش مصنوعی که محتوا تولید می‌کند.

موضوع مقاله: **{keyword}**
کلیدواژه‌های مرتبط: {kw_list_str}

دستورالعمل‌های نگارش:

۱. **لحن و سبک**: از اول شخص جمع به صورت پراکنده استفاده کنید تا حس تیمی و تجربه واقعی منتقل شود. مثال: "در آدونیس گروپ، ما معمولاً به مشتریانمان توصیه می‌کنیم..." یا "از تجربه ما با صدها خانواده ایرانی می‌توانم بگویم که..."

۲. **اطلاعات واقعی و دقیق**: اعداد و ارقام واقعی بیاورید:
   - بازه‌های قیمتی واقعی (مثلاً آپارتمان‌های آتن بین ۱۵۰,۰۰۰ تا ۴۵۰,۰۰۰ یورو)
   - محله‌های واقعی آتن (گلیفادا، پایرئوس، کولوناکی، مارسی، ووالا) و تسالونیکی (کاراتاس، پانوراما، توریم)
   - جدول زمانی واقعی پردازش (مثلاً ۳ تا ۶ ماه برای گلدن ویزا)
   - الزامات قانونی به‌روز

۳. **بخش "تجربه ما"**: یک بخش مجزا با عنوان "## تجربه ما" اضافه کنید که شامل:
   - توصیه‌های عملی حاصل از کار با مشتریان ایرانی
   - نکات خاصی که فقط از تجربه مستقیم به دست می‌آید
   - مثال‌های واقع‌گرایانه از موقعیت‌هایی که مشتریان با آن روبرو شده‌اند

۴. **یادداشت احتیاطی**: یک نکته هشداردهنده واقعی در مقاله بگنجانید (چیزی که ممکن است اشتباه پیش برود یا مراقبت ویژه‌ای نیاز داشته باشد). مثال: "یک اشتباه رایج که می‌بینیم..."

۵. **تنوع ساختاری**: طول جملات و پاراگراف‌ها را متنوع کنید تا مقاله انسانی به نظر برسد. برخی پاراگراف‌ها کوتاه و ضربتی، برخی توضیحی و تفصیلی.

۶. **مشخصات فنی**:
   - بین ۱۰۰۰ تا ۱۵۰۰ کلمه
   - از تیترهای H2 و H3 استفاده کنید (با ## و ###)
   - دارای call-to-action در انتها
   - برای مخاطب ایرانی علاقه‌مند به مهاجرت به یونان

پاسخ را دقیقاً در این قالب بنویسید:

TITLE: [عنوان مقاله - حداکثر ۷۰ کاراکتر]
SLUG: [slug فارسی بدون فاصله، با خط تیره، حداکثر ۱۰۰ کاراکتر]
META_TITLE: [عنوان متا - حداکثر ۶۰ کاراکتر]
META_DESCRIPTION: [توضیحات متا - حداکثر ۱۵۵ کاراکتر]
FOCUS_KEYWORDS: [کلیدواژه‌های تمرکز جدا شده با کاما]
EXCERPT: [چکیده مقاله - ۲ تا ۳ جمله]
CONTENT:
[محتوای کامل مقاله در HTML یا Markdown]
END_CONTENT"""

    message = client.messages.create(
        model='claude-opus-4-5',
        max_tokens=4000,
        messages=[{'role': 'user', 'content': prompt}],
    )

    response_text = message.content[0].text
    return _parse_claude_response(response_text)


def _parse_claude_response(text: str) -> dict:
    """Parse the structured Claude response into a dict."""

    def _extract(marker: str, stop_markers: list[str] | None = None) -> str:
        pattern = rf'^{re.escape(marker)}:\s*(.+?)$'
        m = re.search(pattern, text, re.MULTILINE)
        return m.group(1).strip() if m else ''

    def _extract_block(start_marker: str, end_marker: str) -> str:
        # 1) Strict: content between START: and END markers (newline optional,
        #    content may start on the same line).
        pattern = rf'{re.escape(start_marker)}:[ \t]*\n?(.*?){re.escape(end_marker)}'
        m = re.search(pattern, text, re.DOTALL)
        if m and m.group(1).strip():
            return m.group(1).strip()
        # 2) Fallback: everything after START: to end of text (Claude sometimes
        #    omits the END marker). Trim a trailing END marker if present.
        m2 = re.search(rf'{re.escape(start_marker)}:[ \t]*\n?(.*)$', text, re.DOTALL)
        if m2:
            block = re.split(re.escape(end_marker), m2.group(1))[0]
            return block.strip()
        return ''

    return {
        'title':            _extract('TITLE'),
        'slug':             _extract('SLUG'),
        'meta_title':       _extract('META_TITLE'),
        'meta_description': _extract('META_DESCRIPTION'),
        'focus_keywords':   _extract('FOCUS_KEYWORDS'),
        'excerpt':          _extract('EXCERPT'),
        'content':          _extract_block('CONTENT', 'END_CONTENT'),
    }


# ── Unsplash Image ─────────────────────────────────────────────────────────────

# ── Curated photo bank (CDN URLs — no API key required) ──────────────────────
# These are real Unsplash landscape photos of Greece / real-estate topics.
# The CDN at images.unsplash.com is publicly accessible without auth.
# Format: (photo_id, w_param, photographer_name, topic_tags)

_PHOTO_BANK = [
    # Athens / Acropolis  [200 verified]
    ('1555993539-1732b0258235', 'athens acropolis greece', 'Cristina Gottardi'),
    ('1603565816030-6b389eeb23cb', 'athens greece city', 'Yannis Papanastasopoulos'),
    ('1603565816030-6b389eeb23cb', 'athens greece skyline', 'Yannis Papanastasopoulos'),  # replacement
    # Greek islands / sea  [200 verified]
    ('1570077188670-e3a8d69ac5ff', 'santorini greece blue dome', 'Logan Armstrong'),
    ('1516483638261-f4dbaf036963', 'mykonos greece white buildings', 'Trent Erwin'),
    ('1548199973-03cce0bbc87b',   'greece sea Mediterranean', 'Levi Elizaga'),           # replacement
    # Real estate / property  [200 verified]
    ('1545324418-cc1a3fa10c00', 'modern apartment luxury interior', 'Douglas Sheppard'),
    ('1512917774080-9991f1c4c750', 'luxury villa pool', 'Vita Vilcina'),
    ('1484154218962-a197022b5858', 'modern living room interior', 'Francesca Tosolini'),
    # Golden Visa / investment  [200 verified]
    ('1502602898657-3e91760cbb34', 'golden greece landscape', 'Rolands Varsbergs'),      # replacement
    ('1502602898657-3e91760cbb34', 'greece harbour boats', 'Rolands Varsbergs'),
    # Immigration / travel  [200 verified]
    ('1436491865332-7a61a109cc05', 'airplane travel sky', 'Ross Parmly'),
    ('1507525428034-b723cf961d3e', 'greece beach paradise', 'Sean Oulashin'),
    # Architecture  [200 verified]
    ('1558618666-fcd25c85cd64', 'greek architecture white blue', 'Random Institute'),
    ('1548199973-03cce0bbc87b', 'greece traditional village', 'Levi Elizaga'),
]

# Map keyword topics → preferred photo indices in _PHOTO_BANK
_TOPIC_MAP = {
    'اقامت':          [0, 1, 2],
    'گلدن ویزا':      [9, 10, 0],
    'ملک':            [3, 4, 7],
    'خرید ملک':      [6, 7, 8],
    'سرمایه':         [9, 10, 6],
    'مهاجرت':         [11, 12, 0],
    'یونان':          [0, 1, 13],
    'آتن':            [0, 1, 2],
    'جزیره':          [3, 4, 12],
}


def _pick_curated_photo(keyword: str) -> dict:
    """Select the best matching curated photo for *keyword*."""
    import hashlib

    # Find first topic match
    indices = None
    for topic, idx_list in _TOPIC_MAP.items():
        if topic in keyword:
            indices = idx_list
            break

    if indices is None:
        # Deterministic but varied selection based on keyword hash
        h = int(hashlib.md5(keyword.encode()).hexdigest(), 16)
        indices = [h % len(_PHOTO_BANK)]

    photo_id, _, photographer = _PHOTO_BANK[indices[0]]
    url   = f'https://images.unsplash.com/photo-{photo_id}?auto=format&fit=crop&w=1600&q=80'
    thumb = f'https://images.unsplash.com/photo-{photo_id}?auto=format&fit=crop&w=640&q=75'
    return {
        'url':      url,
        'thumb':    thumb,
        'credit':   f'Photo by {photographer} on Unsplash',
        'photo_id': photo_id,
    }


def get_unsplash_image(keyword: str) -> dict:
    """
    Fetch a relevant landscape photo for *keyword*.

    Strategy:
    1. Try Unsplash Search API with Authorization header (requires valid key).
    2. Fall back to curated bank of known-good Greece/real-estate Unsplash photos
       — these are accessible directly on images.unsplash.com without any API key.

    Returns dict: url, thumb, credit, photo_id.
    """
    access_key = getattr(settings, 'UNSPLASH_ACCESS_KEY', '').strip()
    en_query   = _fa_keyword_to_en(keyword)

    if access_key:
        headers = {'Authorization': f'Client-ID {access_key}'}
        try:
            resp = requests.get(
                'https://api.unsplash.com/search/photos',
                params={
                    'query':          en_query,
                    'per_page':       10,
                    'orientation':    'landscape',
                    'content_filter': 'high',
                },
                headers=headers,
                timeout=10,
            )
            if resp.status_code == 200:
                data    = resp.json()
                results = data.get('results', [])
                if results:
                    photo        = results[0]
                    photo_id     = photo.get('id', '')
                    full_url     = photo['urls']['full']
                    thumb_url    = photo['urls']['small']
                    photographer = photo.get('user', {}).get('name', 'Unsplash')
                    credit       = f'Photo by {photographer} on Unsplash'

                    # Trigger download endpoint (required by Unsplash ToS)
                    dl_link = photo.get('links', {}).get('download_location', '')
                    if dl_link:
                        try:
                            requests.get(dl_link, headers=headers, timeout=5)
                        except Exception:
                            pass

                    return {'url': full_url, 'thumb': thumb_url,
                            'credit': credit, 'photo_id': photo_id}
            else:
                logger.warning(
                    'Unsplash API returned %s for "%s" — falling back to curated bank.',
                    resp.status_code, en_query,
                )
        except Exception as exc:
            logger.warning('Unsplash API error for "%s": %s', en_query, exc)

    # Fallback: curated CDN photos (no API key needed)
    logger.info('Using curated photo bank for keyword: %s', keyword)
    return _pick_curated_photo(keyword)


# ── Pipeline Orchestrator ──────────────────────────────────────────────────────

def run_pipeline(pipeline_item) -> None:
    """
    Full pipeline for one FaContentPipeline instance:
    1. Fetch Google keyword suggestions
    2. Generate content with Claude
    3. Fetch cover image from Unsplash
    4. Persist everything and set status → review
    On any exception: set status → failed and save error_log.
    """
    from .models_pipeline import FaContentPipeline   # local import to avoid circular

    try:
        pipeline_item.status    = FaContentPipeline.STATUS_GENERATING
        pipeline_item.error_log = ''
        pipeline_item.save(update_fields=['status', 'error_log', 'updated_at'])

        # Step 1 — keyword suggestions
        keywords = get_google_suggestions(pipeline_item.keyword)

        # Step 2 — AI content
        generated = generate_content_with_claude(pipeline_item.keyword, keywords)

        # Step 3 — cover image
        image_data = get_unsplash_image(pipeline_item.keyword)

        # Persist
        pipeline_item.title            = generated.get('title', '')
        pipeline_item.focus_keywords   = generated.get('focus_keywords', '')
        pipeline_item.content          = generated.get('content', '')
        pipeline_item.excerpt          = generated.get('excerpt', '')
        pipeline_item.meta_title       = generated.get('meta_title', '')
        pipeline_item.meta_description = generated.get('meta_description', '')
        pipeline_item.cover_image_url  = image_data.get('url', '')
        pipeline_item.cover_image_thumb = image_data.get('thumb', '')
        pipeline_item.cover_image_credit = image_data.get('credit', '')
        pipeline_item.unsplash_photo_id  = image_data.get('photo_id', '')
        pipeline_item.ai_generated     = True

        # Build a unique slug
        raw_slug = generated.get('slug', '') or pipeline_item.keyword
        pipeline_item.slug = _make_unique_slug(raw_slug, pipeline_item.pk)

        pipeline_item.status = FaContentPipeline.STATUS_REVIEW
        pipeline_item.save()

    except Exception:
        tb = traceback.format_exc()
        logger.error('Pipeline failed for item #%s:\n%s', pipeline_item.pk, tb)
        try:
            pipeline_item.status    = FaContentPipeline.STATUS_FAILED
            pipeline_item.error_log = tb
            pipeline_item.save(update_fields=['status', 'error_log', 'updated_at'])
        except Exception:
            pass


def _make_unique_slug(raw: str, current_pk: int | None) -> str:
    """Return a slug that is unique in the FaContentPipeline table."""
    from .models_pipeline import FaContentPipeline

    # Normalise: replace spaces with hyphens, strip unsafe chars
    slug = re.sub(r'\s+', '-', raw.strip())
    slug = re.sub(r'[^\w\u0600-\u06FF-]', '', slug, flags=re.UNICODE)
    slug = slug[:200].strip('-') or 'fa-content'

    base  = slug
    count = 1
    qs    = FaContentPipeline.objects.all()
    if current_pk:
        qs = qs.exclude(pk=current_pk)

    while qs.filter(slug=slug).exists():
        slug  = f'{base}-{count}'
        count += 1

    return slug


def _markdown_to_safe_html(raw: str) -> str:
    """Convert Markdown (or pass-through HTML) to sanitized HTML for the blog."""
    import bleach
    import markdown as _md

    html = _md.markdown(raw or '', extensions=['extra', 'sane_lists', 'nl2br'])
    allowed_tags = set(bleach.sanitizer.ALLOWED_TAGS) | {
        'p', 'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'img', 'figure', 'figcaption',
        'br', 'hr', 'span', 'div', 'table', 'thead', 'tbody', 'tr', 'td', 'th',
        'ul', 'ol', 'li', 'blockquote', 'pre', 'code', 'strong', 'em',
    }
    allowed_attrs = {
        '*': ['class', 'style', 'id'],
        'a': ['href', 'title', 'target', 'rel'],
        'img': ['src', 'alt', 'title', 'width', 'height', 'loading'],
    }
    return bleach.clean(html, tags=allowed_tags, attributes=allowed_attrs, strip=True)


def publish_to_persian_blog(item):
    """Create or update a live PersianBlogPost from a FaContentPipeline item.

    Idempotent — matches by slug, so re-publishing updates the same post.
    Downloads the cover image into the post's featured_image. Returns the post.
    """
    import urllib.request

    from django.core.files.base import ContentFile
    from django.utils import timezone

    from apps.persian_cms.models import PersianBlogPost

    slug = item.slug or _make_unique_slug(item.keyword, None)
    body_html = _markdown_to_safe_html(item.content)

    post, _created = PersianBlogPost.objects.get_or_create(
        slug=slug,
        defaults={'title': item.title or item.keyword, 'body': body_html},
    )
    post.title = item.title or item.keyword
    post.excerpt = item.excerpt or ''
    post.body = body_html
    post.meta_title = (item.meta_title or item.title or '')[:260]
    post.meta_description = item.meta_description or ''
    first_kw = (item.focus_keywords or '').split(',')[0].strip() or item.keyword
    post.focus_keyword = first_kw[:180]
    post.is_published = True
    if not post.published_at:
        post.published_at = timezone.now()

    # Pull the cover image into featured_image (only if not already set).
    if item.cover_image_url and not post.featured_image:
        try:
            req = urllib.request.Request(
                item.cover_image_url, headers={'User-Agent': 'Mozilla/5.0'}
            )
            with urllib.request.urlopen(req, timeout=20) as resp:
                data = resp.read()
            post.featured_image.save(f'{slug[:40]}.jpg', ContentFile(data), save=False)
        except Exception:
            logger.warning('Cover image download failed for pipeline #%s', item.pk)

    post.save()
    return post


# ── English Pipeline ──────────────────────────────────────────────────────────

def get_english_keywords(keyword: str) -> list[str]:
    """
    Fetch English keyword suggestions from Google.
    Tries the base keyword, then appends 'greece', 'golden visa', 'invest greece'.
    Returns up to 15 unique suggestions.
    """
    suggestions: list[str] = []
    base_url = 'https://suggestqueries.google.com/complete/search'
    headers  = {'User-Agent': 'Mozilla/5.0 (compatible; AdonisBot/1.0)'}

    queries = [
        keyword,
        f'{keyword} greece',
        f'{keyword} golden visa',
        f'{keyword} invest greece',
    ]

    for q in queries:
        try:
            resp = requests.get(
                base_url,
                params={'q': q, 'client': 'firefox', 'gl': 'gr', 'hl': 'en'},
                headers=headers,
                timeout=8,
            )
            resp.raise_for_status()
            data = resp.json()
            if isinstance(data, list) and len(data) > 1 and isinstance(data[1], list):
                for s in data[1]:
                    if s and s not in suggestions:
                        suggestions.append(s)
        except Exception as exc:
            logger.warning('English suggest failed (q=%s): %s', q, exc)

    if keyword not in suggestions:
        suggestions.insert(0, keyword)

    return suggestions[:15]


def generate_english_content(keyword: str, keywords_list: list[str]) -> dict:
    """
    Generate a full SEO blog post in English using Claude.
    Returns a dict with keys: title, slug, meta_title, meta_description,
    focus_keywords, excerpt, content.
    """
    try:
        import anthropic
    except ImportError:
        raise RuntimeError(
            'anthropic package is not installed. Run: pip install anthropic'
        )

    api_key = getattr(settings, 'ANTHROPIC_API_KEY', '')
    if not api_key:
        raise RuntimeError(
            'ANTHROPIC_API_KEY is not set in Django settings / .env file.'
        )

    client = anthropic.Anthropic(api_key=api_key)

    kw_list_str = ', '.join(keywords_list[:10])

    prompt = f"""You are Adonis Group's senior consultant (adonisgroup.gr) with 15 years of hands-on experience in Greek real estate and Golden Visa immigration law. Write this article as a real expert sharing genuine insights for English-speaking investors considering Greece — not as an AI generating content.

Article topic: **{keyword}**
Related keywords: {kw_list_str}

Writing guidelines:

1. **Tone & voice**: Use first-person plural occasionally to convey team expertise and lived experience. Examples: "At Adonis Group, we typically advise our clients…" or "From our experience working with hundreds of international families, we've found that…"

2. **Real specifics**: Include concrete, accurate data:
   - Actual price ranges (e.g. Athens apartments from €150,000 to €450,000; villas in the islands from €300,000+)
   - Real Athens neighborhoods: Glyfada, Kolonaki, Piraeus, Marousi, Voula, Kifissia
   - Genuine processing timelines (e.g. 3–6 months for Golden Visa approval)
   - Up-to-date legal requirements and thresholds

3. **"Our Experience" section**: Include a dedicated H2 section titled "Our Experience" containing:
   - Practical advice drawn from working with international clients
   - Specifics only an experienced practitioner would know
   - Realistic scenarios investors commonly encounter

4. **Cautionary note**: Include one honest warning per article — something that can go wrong or requires special attention. Example: "One mistake we see often is…"

5. **Varied structure**: Mix short punchy paragraphs with longer explanatory ones. Vary sentence length so the article reads naturally and humanly.

6. **Technical specs**:
   - 1200–1500 words
   - H2 and H3 headings (## and ###)
   - Strong call-to-action at the end
   - Aimed at English-speaking international investors (European, Middle Eastern, Asian)

Write your response in exactly this format:

TITLE: [Article title — max 70 characters]
SLUG: [lowercase-hyphenated-slug — max 100 characters]
META_TITLE: [Meta title — max 60 characters]
META_DESCRIPTION: [Meta description — max 155 characters]
FOCUS_KEYWORDS: [comma-separated focus keywords]
EXCERPT: [2–3 sentence article summary]
CONTENT:
[Full article content in Markdown]
END_CONTENT"""

    message = client.messages.create(
        model='claude-opus-4-5',
        max_tokens=4000,
        messages=[{'role': 'user', 'content': prompt}],
    )

    response_text = message.content[0].text
    return _parse_claude_response(response_text)


def _make_unique_en_slug(raw: str, current_pk: int | None) -> str:
    """Return a slug that is unique in the EnContentPipeline table."""
    from .models_pipeline import EnContentPipeline

    slug = re.sub(r'\s+', '-', raw.strip().lower())
    slug = re.sub(r'[^\w-]', '', slug)
    slug = slug[:200].strip('-') or 'en-content'

    base  = slug
    count = 1
    qs    = EnContentPipeline.objects.all()
    if current_pk:
        qs = qs.exclude(pk=current_pk)

    while qs.filter(slug=slug).exists():
        slug  = f'{base}-{count}'
        count += 1

    return slug


def run_english_pipeline(pipeline_item) -> None:
    """
    Full pipeline for one EnContentPipeline instance:
    1. Fetch English keyword suggestions
    2. Generate content with Claude (English prompt)
    3. Fetch cover image from Unsplash
    4. Persist everything and set status → review
    On any exception: set status → failed and save error_log.
    """
    from .models_pipeline import EnContentPipeline

    try:
        pipeline_item.status    = EnContentPipeline.STATUS_GENERATING
        pipeline_item.error_log = ''
        pipeline_item.save(update_fields=['status', 'error_log', 'updated_at'])

        keywords   = get_english_keywords(pipeline_item.keyword)
        generated  = generate_english_content(pipeline_item.keyword, keywords)
        image_data = get_unsplash_image(pipeline_item.keyword)

        pipeline_item.title             = generated.get('title', '')
        pipeline_item.focus_keywords    = generated.get('focus_keywords', '')
        pipeline_item.content           = generated.get('content', '')
        pipeline_item.excerpt           = generated.get('excerpt', '')
        pipeline_item.meta_title        = generated.get('meta_title', '')
        pipeline_item.meta_description  = generated.get('meta_description', '')
        pipeline_item.cover_image_url   = image_data.get('url', '')
        pipeline_item.cover_image_thumb = image_data.get('thumb', '')
        pipeline_item.cover_image_credit = image_data.get('credit', '')
        pipeline_item.unsplash_photo_id  = image_data.get('photo_id', '')
        pipeline_item.ai_generated      = True

        raw_slug = generated.get('slug', '') or pipeline_item.keyword
        pipeline_item.slug = _make_unique_en_slug(raw_slug, pipeline_item.pk)

        pipeline_item.status = EnContentPipeline.STATUS_REVIEW
        pipeline_item.save()

    except Exception:
        tb = traceback.format_exc()
        logger.error('English pipeline failed for item #%s:\n%s', pipeline_item.pk, tb)
        try:
            pipeline_item.status    = EnContentPipeline.STATUS_FAILED
            pipeline_item.error_log = tb
            pipeline_item.save(update_fields=['status', 'error_log', 'updated_at'])
        except Exception:
            pass
