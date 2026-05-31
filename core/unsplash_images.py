import os
import re
import requests
from pathlib import Path

UNSPLASH_SEARCH_URL = 'https://api.unsplash.com/search/photos'


def _get_key():
    """Read the key at call-time so .env changes take effect after a restart."""
    # Prefer Django settings if available (reads from .env via python-dotenv)
    try:
        from django.conf import settings as _s
        k = getattr(_s, 'UNSPLASH_ACCESS_KEY', '').strip()
        if k:
            return k
    except Exception:
        pass
    return os.environ.get('UNSPLASH_ACCESS_KEY', '').strip()
REQUEST_TIMEOUT_SECONDS = 20

PROJECT_ROOT = Path(__file__).resolve().parent.parent
COVERS_DIR = PROJECT_ROOT / 'media' / 'fa-blog' / 'covers'
COVERS_PUBLIC_BASE = '/media/fa-blog/covers'


def _safe_slug(value):
    raw = (value or '').strip()
    if not raw:
        return 'fa-content'
    cleaned = re.sub(r'[^\w\-\u0600-\u06FF]+', '-', raw, flags=re.UNICODE)
    cleaned = re.sub(r'-{2,}', '-', cleaned).strip('-').lower()
    return cleaned or 'fa-content'


def _translate_to_english(text):
    source = (text or '').strip()
    if not source:
        return source
    try:
        from deep_translator import GoogleTranslator
        translated = GoogleTranslator(source='auto', target='en').translate(source)
        return (translated or source).strip()
    except Exception:
        return source


def _search_unsplash(query_en, count):
    key = _get_key()
    if not key:
        print('UNSPLASH_ACCESS_KEY is missing.')
        return []

    headers = {'Authorization': f'Client-ID {key}'}
    resp = requests.get(
        UNSPLASH_SEARCH_URL,
        headers=headers,
        params={'query': query_en, 'per_page': max(1, min(count, 30)), 'orientation': 'landscape'},
        timeout=REQUEST_TIMEOUT_SECONDS,
    )
    if resp.status_code != 200:
        print(f'Unsplash error: {resp.status_code}')
        return []
    return resp.json().get('results', [])


def _download_image(source_url, destination):
    try:
        response = requests.get(source_url, timeout=REQUEST_TIMEOUT_SECONDS)
        response.raise_for_status()
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(response.content)
        return True
    except Exception as exc:
        print(f'Failed to download image: {exc}')
        return False


def fetch_pipeline_images(topic_fa, slug, seo_keyword_fa):
    """
    Generate image assets for FaContentPipeline:
    - Translate topic to English and query Unsplash
    - Save first image as cover: media/fa-blog/covers/{slug}.jpg
    - Save two additional inline images
    - Set Persian SEO alt text for the cover
    """
    safe_slug = _safe_slug(slug or topic_fa)
    query_en = _translate_to_english(topic_fa)
    photos = _search_unsplash(query_en, count=3)

    payload = {
        'query_en': query_en,
        'cover_image_name': '',
        'cover_image_url': '',
        'cover_image_alt': (seo_keyword_fa or topic_fa or '').strip(),
        'inline_images': [],
    }

    if not photos:
        return payload

    max_inline = 2
    for idx, photo in enumerate(photos[:3]):
        urls = photo.get('urls') or {}
        image_url = urls.get('regular') or urls.get('full')
        if not image_url:
            continue

        if idx == 0:
            filename = f'{safe_slug}.jpg'
        else:
            filename = f'{safe_slug}-inline-{idx}.jpg'

        destination = COVERS_DIR / filename
        if not _download_image(image_url, destination):
            continue

        public_url = f'{COVERS_PUBLIC_BASE}/{filename}'
        alt_text = photo.get('alt_description') or topic_fa or query_en
        credit = (photo.get('user') or {}).get('name', 'Unsplash')

        if idx == 0:
            payload['cover_image_name'] = f'fa-blog/covers/{filename}'
            payload['cover_image_url'] = public_url
        else:
            if len(payload['inline_images']) >= max_inline:
                continue
            payload['inline_images'].append(public_url)

    return payload


def attach_unsplash_to_generated_article(article, topic_fa):
    """
    Attach cover and inline images to generated article payload.
    Compatible with FaContentPipeline fields and admin form autofill.
    """
    article = article or {}
    slug = (article.get('slug') or '').strip()
    focus = (article.get('focus_keywords') or '').strip()
    seo_keyword_fa = (focus.split(',')[0] if focus else topic_fa).strip()

    assets = fetch_pipeline_images(
        topic_fa=topic_fa,
        slug=slug or topic_fa,
        seo_keyword_fa=seo_keyword_fa,
    )

    article['cover_image'] = assets['cover_image_name']
    article['cover_image_url'] = assets['cover_image_url']
    article['cover_image_alt'] = assets['cover_image_alt']
    article['inline_images'] = assets['inline_images']
    article['unsplash_query_en'] = assets['query_en']
    return article


def search_and_download(query, slug, count=3):
    """Backward-compatible helper for older callers."""
    assets = fetch_pipeline_images(query, slug, query)
    images = []
    if assets['cover_image_url']:
        images.append({
            'path': assets['cover_image_url'],
            'alt': assets['cover_image_alt'],
            'credit': 'Unsplash',
        })
    for item in assets['inline_images'][: max(0, count - 1)]:
        images.append({
            'path': item,
            'alt': query,
            'credit': 'Unsplash',
        })
    return images


def inject_images_into_body(body, images):
    """درج عکس‌ها در داخل متن بلاگ"""
    if not images:
        return body

    # عکس‌های ۲ و ۳ رو بعد از پاراگراف ۳ و ۶ درج کن
    paragraphs = body.split('</p>')
    result = []
    img_index = 1  # از عکس دوم شروع (اول کاور هست)

    for i, para in enumerate(paragraphs):
        result.append(para)
        if para.strip():
            result.append('</p>')
            if i == 2 and img_index < len(images):
                img = images[img_index]
                result.append(f'''
<figure style="margin:2rem 0;text-align:center;">
  <img src="{img['path']}" alt="{img['alt']}" 
       style="width:100%;max-width:800px;border-radius:8px;box-shadow:0 4px 20px rgba(0,0,0,0.15);">
  <figcaption style="font-size:0.8rem;color:#888;margin-top:0.5rem;">عکس از {img['credit']} / Unsplash</figcaption>
</figure>''')
                img_index += 1
            elif i == 5 and img_index < len(images):
                img = images[img_index]
                result.append(f'''
<figure style="margin:2rem 0;text-align:center;">
  <img src="{img['path']}" alt="{img['alt']}" 
       style="width:100%;max-width:800px;border-radius:8px;box-shadow:0 4px 20px rgba(0,0,0,0.15);">
  <figcaption style="font-size:0.8rem;color:#888;margin-top:0.5rem;">عکس از {img['credit']} / Unsplash</figcaption>
</figure>''')
                img_index += 1
        else:
            result.append('</p>')

    return ''.join(result)
