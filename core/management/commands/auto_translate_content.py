"""
Management command: auto_translate_content

Full-site Turkish translation pass.
- Uses OpenAI GPT-4o if OPENAI_API_KEY is set (highest quality)
- Falls back to Google Translate (free, no key needed) otherwise

Usage:
    python manage.py auto_translate_content               # skip already-translated
    python manage.py auto_translate_content --overwrite   # re-translate everything
    python manage.py auto_translate_content --dry-run     # preview, no changes
    python manage.py auto_translate_content --model faq   # single model only
"""

import time
import logging
import re

from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify

logger = logging.getLogger(__name__)

# ── System prompt (OpenAI backend) ───────────────────────────────────────────
_SYSTEM_PROMPT = (
    "You are a professional Turkish translator specialising in Istanbul Turkish "
    "for a luxury real estate and immigration law firm in Greece.\n\n"
    "Rules:\n"
    "1. Translate to natural, fluent Istanbul Turkish.\n"
    "2. Keep SEO-friendly tone and preserve keyword intent for Turkish Google.\n"
    "3. Preserve ALL HTML tags and formatting exactly as they appear.\n"
    "4. DO NOT translate proper nouns: Greece, Athens, Thessaloniki, Schengen, "
    "   Golden Visa, Adonis Group, EU, EUR, USD, or any brand name.\n"
    "5. DO NOT translate URLs, email addresses, phone numbers, or numeric values.\n"
    "6. Country names: use standard Turkish equivalents "
    "   (Yunanistan=Greece, İran=Iran, Türkiye=Turkey, İngiltere=UK, etc.).\n"
    "7. Return ONLY the translated text — no explanations, no quotation marks.\n"
    "8. If input is already in Turkish, return it unchanged."
)

_GOOGLE_MAX_CHARS = 4500  # safe limit below Google's 5000-char cap


def _get_openai_client():
    import os
    api_key = os.getenv('OPENAI_API_KEY', '').strip()
    if not api_key:
        return None
    from openai import OpenAI
    return OpenAI(api_key=api_key)


def _get_google_translator():
    try:
        from deep_translator import GoogleTranslator
        return GoogleTranslator(source='en', target='tr')
    except ImportError:
        return None


# ── Google Translate helpers ──────────────────────────────────────────────────

def _split_html_chunks(text: str, max_chars: int) -> list:
    """
    Split HTML/long text into chunks ≤ max_chars.
    Splits on closing block tags, then on sentences.
    """
    if len(text) <= max_chars:
        return [text]

    # Split on closing block tags (variable-width lookbehind not supported —
    # use a capture group + rejoin approach instead)
    parts = re.split(r'(</(?:p|li|h[1-6]|div|blockquote)>)', text)
    # Rejoin each tag with the preceding part
    rejoined = []
    i = 0
    while i < len(parts):
        if i + 1 < len(parts) and re.match(r'</(?:p|li|h[1-6]|div|blockquote)>', parts[i + 1]):
            rejoined.append(parts[i] + parts[i + 1])
            i += 2
        else:
            rejoined.append(parts[i])
            i += 1

    chunks = []
    current = ''
    for part in rejoined:
        if len(current) + len(part) <= max_chars:
            current += part
        else:
            if current:
                chunks.append(current)
            # If single part is still too large, split on sentences
            if len(part) > max_chars:
                sentences = re.split(r'(?<=[.!?])\s+', part)
                cur_sent = ''
                for s in sentences:
                    if len(cur_sent) + len(s) + 1 <= max_chars:
                        cur_sent += (' ' if cur_sent else '') + s
                    else:
                        if cur_sent:
                            chunks.append(cur_sent)
                        cur_sent = s
                if cur_sent:
                    chunks.append(cur_sent)
                current = ''
            else:
                current = part
    if current:
        chunks.append(current)
    return chunks


def _translate_google(text: str) -> str:
    """Translate text from EN to TR using Google Translate (free)."""
    from deep_translator import GoogleTranslator
    text = (text or '').strip()
    if not text:
        return ''

    chunks = _split_html_chunks(text, _GOOGLE_MAX_CHARS)
    translated_parts = []
    for chunk in chunks:
        if not chunk.strip():
            translated_parts.append(chunk)
            continue
        try:
            result = GoogleTranslator(source='en', target='tr').translate(chunk)
            translated_parts.append(result or chunk)
            if len(chunks) > 1:
                time.sleep(0.5)
        except Exception as exc:
            logger.warning('Google Translate chunk failed: %s', exc)
            translated_parts.append(chunk)
    return ''.join(translated_parts)


def _translate_openai(client, text: str) -> str:
    text = (text or '').strip()
    if not text:
        return ''
    response = client.chat.completions.create(
        model='gpt-4o',
        messages=[
            {'role': 'system', 'content': _SYSTEM_PROMPT},
            {'role': 'user',   'content': text},
        ],
        temperature=0.25,
    )
    return response.choices[0].message.content.strip()


def _translate_text(client, text: str) -> str:
    """Translate using OpenAI if available, else Google Translate."""
    if client is not None:
        return _translate_openai(client, text)
    return _translate_google(text)


# ── Model configs: (label, Model, [(en_field, tr_field, is_slug)]) ────────────
_MODEL_CONFIGS = None


def _get_model_configs():
    global _MODEL_CONFIGS
    if _MODEL_CONFIGS is not None:
        return _MODEL_CONFIGS

    from core.models import (
        BlogPost, BlogCategory,
        Event, GoldenVisaCard, Service, FAQ, Testimonial,
        HeaderSettings, FooterSettings, FrontPageSettings,
        GoldenVisaLandingPage, AboutPageSettings, Office, TeamMember,
    )
    try:
        from core.models import PropertiesPageSettings
    except ImportError:
        PropertiesPageSettings = None
    try:
        from core.models import PartnershipPageSettings
    except ImportError:
        PartnershipPageSettings = None
    from properties.models import Property, PropertyMedia

    configs = [

        # ── Blog ────────────────────────────────────────────────────────────────
        ('BlogCategory', BlogCategory, [
            ('name_en',        'name_tr',        False),
            ('description_en', 'description_tr', False),
        ]),
        ('BlogPost', BlogPost, [
            ('title_en',            'title_tr',            False),
            ('excerpt_en',          'excerpt_tr',          False),
            ('content_en',          'content_tr',          False),
            ('meta_title_en',       'meta_title_tr',       False),
            ('meta_description_en', 'meta_description_tr', False),
            ('og_title_en',         'og_title_tr',         False),
            ('og_description_en',   'og_description_tr',   False),
            ('featured_image_alt_en', 'featured_image_alt_tr', False),
            # slug_tr auto-generated (is_slug=True means: slugify en_field → tr_field)
            ('title_tr',            'slug_tr',             True),
        ]),

        # ── Services / FAQ / Testimonials ────────────────────────────────────
        ('Service', Service, [
            ('title_en',       'title_tr',       False),
            ('description_en', 'description_tr', False),
        ]),
        ('FAQ', FAQ, [
            ('question_en', 'question_tr', False),
            ('answer_en',   'answer_tr',   False),
        ]),
        ('Testimonial', Testimonial, [
            ('content_en',   'content_tr',   False),
            ('image_alt_en', 'image_alt_tr', False),
        ]),

        # ── Golden Visa ──────────────────────────────────────────────────────
        ('GoldenVisaCard', GoldenVisaCard, [
            ('title_en',       'title_tr',       False),
            ('subtitle_en',    'subtitle_tr',    False),
            ('description_en', 'description_tr', False),
            ('image_alt_en',   'image_alt_tr',   False),
        ]),

        # ── Events ───────────────────────────────────────────────────────────
        ('Event', Event, [
            ('title_en',             'title_tr',             False),
            ('short_description_en', 'short_description_tr', False),
            ('full_description_en',  'full_description_tr',  False),
            ('thumbnail_alt_en',     'thumbnail_alt_tr',     False),
            ('title_tr',             'slug_tr',              True),
        ]),

        # ── Site settings (singletons) ───────────────────────────────────────
        ('HeaderSettings', HeaderSettings, [
            ('hero_title_en',          'hero_title_tr',          False),
            ('hero_subtitle_en',       'hero_subtitle_tr',       False),
            ('intro_title_en',         'intro_title_tr',         False),
            ('intro_text_en',          'intro_text_tr',          False),
            ('contact_button_text_en', 'contact_button_text_tr', False),
        ]),
        ('FooterSettings', FooterSettings, [
            ('description_en',         'description_tr',         False),
            ('whatsapp_button_text_en', 'whatsapp_button_text_tr', False),
        ]),
        ('FrontPageSettings', FrontPageSettings, [
            ('services_badge_en',       'services_badge_tr',       False),
            ('services_title_en',       'services_title_tr',       False),
            ('services_description_en', 'services_description_tr', False),
            ('process_badge_en',        'process_badge_tr',        False),
            ('process_title_en',        'process_title_tr',        False),
            ('process_description_en',  'process_description_tr',  False),
            ('catalogue_badge_text_en', 'catalogue_badge_text_tr', False),
            ('catalogue_heading_en',    'catalogue_heading_tr',    False),
            ('catalogue_subtext_en',    'catalogue_subtext_tr',    False),
            ('catalogue_btn1_label_en', 'catalogue_btn1_label_tr', False),
            ('catalogue_btn1_title_en', 'catalogue_btn1_title_tr', False),
            ('catalogue_btn2_label_en', 'catalogue_btn2_label_tr', False),
            ('catalogue_btn2_title_en', 'catalogue_btn2_title_tr', False),
            ('contact_badge_en',        'contact_badge_tr',        False),
            ('contact_title_en',        'contact_title_tr',        False),
            ('contact_description_en',  'contact_description_tr',  False),
        ]),

        # ── About Page ───────────────────────────────────────────────────────
        ('AboutPageSettings', AboutPageSettings, [
            ('hero_title_en',    'hero_title_tr',    False),
            ('hero_subtitle_en', 'hero_subtitle_tr', False),
            ('about_title_en',   'about_title_tr',   False),
            ('about_text_en',    'about_text_tr',    False),
            ('team_title_en',    'team_title_tr',    False),
            ('team_subtitle_en', 'team_subtitle_tr', False),
        ]),

        # ── Team & Offices ───────────────────────────────────────────────────
        ('TeamMember', TeamMember, [
            ('position_en', 'position_tr', False),
            ('bio_en',      'bio_tr',      False),
        ]),
        ('Office', Office, [
            ('city_en',    'city_tr',    False),
            ('country_en', 'country_tr', False),
            ('address_en', 'address_tr', False),
        ]),

        # ── Golden Visa Landing Page (singleton, many fields) ────────────────
        ('GoldenVisaLandingPage', GoldenVisaLandingPage, [
            ('hero_title_en',          'hero_title_tr',          False),
            ('hero_subtitle_en',       'hero_subtitle_tr',       False),
            ('intro_title_en',         'intro_title_tr',         False),
            ('intro_text_en',          'intro_text_tr',          False),
            ('section_1_title_en',     'section_1_title_tr',     False),
            ('section_1_text_en',      'section_1_text_tr',      False),
            ('section_1_image_alt_en', 'section_1_image_alt_tr', False),
            ('section_2_title_en',     'section_2_title_tr',     False),
            ('section_2_text_en',      'section_2_text_tr',      False),
            ('section_2_image_alt_en', 'section_2_image_alt_tr', False),
            ('section_3_title_en',     'section_3_title_tr',     False),
            ('section_3_text_en',      'section_3_text_tr',      False),
            ('section_3_image_alt_en', 'section_3_image_alt_tr', False),
            ('benefits_title_en',      'benefits_title_tr',      False),
            ('benefits_text_en',       'benefits_text_tr',       False),
            ('process_title_en',       'process_title_tr',       False),
            ('process_steps_en',       'process_steps_tr',       False),
            ('cta_title_en',           'cta_title_tr',           False),
            ('cta_text_en',            'cta_text_tr',            False),
            ('cta_button_text_en',     'cta_button_text_tr',     False),
            ('tier_250_title_en',      'tier_250_title_tr',      False),
            ('tier_250_desc_en',       'tier_250_desc_tr',       False),
            ('tier_250_image_alt_en',  'tier_250_image_alt_tr',  False),
            ('tier_400_title_en',      'tier_400_title_tr',      False),
            ('tier_400_desc_en',       'tier_400_desc_tr',       False),
            ('tier_400_image_alt_en',  'tier_400_image_alt_tr',  False),
            ('tier_800_title_en',      'tier_800_title_tr',      False),
            ('tier_800_desc_en',       'tier_800_desc_tr',       False),
            ('tier_800_image_alt_en',  'tier_800_image_alt_tr',  False),
            ('hero_image_alt_en',      'hero_image_alt_tr',      False),
            ('video_title_en',         'video_title_tr',         False),
            ('video_subtitle_en',      'video_subtitle_tr',      False),
            ('benefit_1_title_en',     'benefit_1_title_tr',     False),
            ('benefit_1_text_en',      'benefit_1_text_tr',      False),
            ('benefit_2_title_en',     'benefit_2_title_tr',     False),
            ('benefit_2_text_en',      'benefit_2_text_tr',      False),
            ('benefit_3_title_en',     'benefit_3_title_tr',     False),
            ('benefit_3_text_en',      'benefit_3_text_tr',      False),
            ('benefit_4_title_en',     'benefit_4_title_tr',     False),
            ('benefit_4_text_en',      'benefit_4_text_tr',      False),
            ('benefit_5_title_en',     'benefit_5_title_tr',     False),
            ('benefit_5_text_en',      'benefit_5_text_tr',      False),
            ('benefit_6_title_en',     'benefit_6_title_tr',     False),
            ('benefit_6_text_en',      'benefit_6_text_tr',      False),
        ]),

        # ── Properties Page ──────────────────────────────────────────────────
        *([('PropertiesPageSettings', PropertiesPageSettings, [
            ('hero_title_en',    'hero_title_tr',    False),
            ('hero_subtitle_en', 'hero_subtitle_tr', False),
            ('hero_badge_en',    'hero_badge_tr',    False),
            ('intro_title_en',   'intro_title_tr',   False),
            ('intro_text_en',    'intro_text_tr',    False),
        ])] if PropertiesPageSettings else []),

        # ── Partnership Page ─────────────────────────────────────────────────
        *([('PartnershipPageSettings', PartnershipPageSettings, [
            ('hero_title_en',    'hero_title_tr',    False),
            ('hero_subtitle_en', 'hero_subtitle_tr', False),
            ('b2b_title_en',     'b2b_title_tr',     False),
            ('b2b_text_en',      'b2b_text_tr',      False),
            ('cta_title_en',     'cta_title_tr',     False),
            ('cta_text_en',      'cta_text_tr',      False),
            ('cta_button_text_en', 'cta_button_text_tr', False),
            ('video_title_en',   'video_title_tr',   False),
            ('video_subtitle_en','video_subtitle_tr',False),
            ('benefit_1_title_en','benefit_1_title_tr',False),
            ('benefit_1_text_en', 'benefit_1_text_tr', False),
            ('benefit_2_title_en','benefit_2_title_tr',False),
            ('benefit_2_text_en', 'benefit_2_text_tr', False),
            ('benefit_3_title_en','benefit_3_title_tr',False),
            ('benefit_3_text_en', 'benefit_3_text_tr', False),
            ('benefit_4_title_en','benefit_4_title_tr',False),
            ('benefit_4_text_en', 'benefit_4_text_tr', False),
            ('benefit_5_title_en','benefit_5_title_tr',False),
            ('benefit_5_text_en', 'benefit_5_text_tr', False),
            ('benefit_6_title_en','benefit_6_title_tr',False),
            ('benefit_6_text_en', 'benefit_6_text_tr', False),
        ])] if PartnershipPageSettings else []),

        # ── Properties ───────────────────────────────────────────────────────
        ('Property', Property, [
            ('name_en',                     'name_tr',                     False),
            ('tagline_en',                  'tagline_tr',                  False),
            ('description_en',              'description_tr',              False),
            ('location_en',                 'location_tr',                 False),
            ('area_en',                     'area_tr',                     False),
            ('neighborhood_public_en',      'neighborhood_public_tr',      False),
            ('neighborhood_description_en', 'neighborhood_description_tr', False),
            ('feature_1_en',                'feature_1_tr',                False),
            ('feature_2_en',                'feature_2_tr',                False),
            ('feature_3_en',                'feature_3_tr',                False),
            ('feature_4_en',                'feature_4_tr',                False),
            ('area_highlight_1_en',         'area_highlight_1_tr',         False),
            ('area_highlight_2_en',         'area_highlight_2_tr',         False),
            ('area_highlight_3_en',         'area_highlight_3_tr',         False),
            ('area_highlight_4_en',         'area_highlight_4_tr',         False),
            ('area_highlight_5_en',         'area_highlight_5_tr',         False),
            ('area_highlight_6_en',         'area_highlight_6_tr',         False),
            ('name_tr',                     'slug_tr',                     True),
        ]),
        ('PropertyMedia', PropertyMedia, [
            ('caption_en', 'caption_tr', False),
        ]),
    ]

    _MODEL_CONFIGS = configs
    return _MODEL_CONFIGS


# ── Per-object translation ────────────────────────────────────────────────────

_EMPTY_HTML_PATTERNS = re.compile(
    r'^(<p>(\s|&nbsp;)*<\/p>|<br\s*/?>|\s)*$', re.IGNORECASE
)


def _is_effectively_empty(val: str) -> bool:
    """Return True if val is None, empty, or only whitespace / empty HTML tags."""
    val = (val or '').strip()
    if not val:
        return True
    return bool(_EMPTY_HTML_PATTERNS.match(val))


def _translate_object(client, obj, field_specs, overwrite, dry_run, stdout, style):
    changed = False
    api_calls = 0

    for en_field, tr_field, is_slug in field_specs:
        # Guard: field must exist on model
        if not hasattr(obj, en_field) or not hasattr(obj, tr_field):
            continue

        en_val = (getattr(obj, en_field) or '').strip()
        tr_val = (getattr(obj, tr_field) or '').strip()

        if not en_val:
            continue

        if not _is_effectively_empty(tr_val) and not overwrite:
            continue

        if is_slug:
            new_slug = slugify(en_val)
            if new_slug and (not tr_val or overwrite):
                if not dry_run:
                    setattr(obj, tr_field, new_slug)
                stdout.write(f'    {style.SUCCESS("slug")} {tr_field} ← {repr(new_slug)}')
                changed = True
            continue

        stdout.write(f'    → {tr_field} … ', ending='')
        if dry_run:
            stdout.write(style.WARNING('[dry-run]'))
            continue

        try:
            translated = _translate_text(client, en_val)
            setattr(obj, tr_field, translated)
            api_calls += 1
            changed = True
            preview = translated[:70].replace('\n', ' ')
            stdout.write(style.SUCCESS(f'✓  "{preview}"'))
        except Exception as exc:
            stdout.write(style.ERROR(f'ERROR: {exc}'))
            logger.exception('Translation error for %s.%s (pk=%s)', obj.__class__.__name__, tr_field, getattr(obj, 'pk', '?'))

        # Rate-limit: OpenAI 0.8s, Google Translate 1.2s
        time.sleep(0.8 if client is not None else 1.2)

    if changed and not dry_run:
        try:
            obj.save()
        except Exception as exc:
            stdout.write(style.ERROR(f'    SAVE ERROR for {obj}: {exc}'))

    return changed, api_calls


# ── Command ───────────────────────────────────────────────────────────────────

class Command(BaseCommand):
    help = 'Auto-translate ALL empty Turkish (_tr) fields site-wide using OpenAI GPT-4o'

    def add_arguments(self, parser):
        parser.add_argument(
            '--model', type=str, default='all',
            help='Model to target: all | blogpost | property | faq | goldenvisalandingpage | … (lowercase)',
        )
        parser.add_argument(
            '--overwrite', action='store_true', default=False,
            help='Re-translate fields that already have Turkish content.',
        )
        parser.add_argument(
            '--dry-run', action='store_true', default=False,
            help='Show what would be translated without calling the API.',
        )

    def handle(self, *args, **options):
        model_filter = options['model'].lower()
        overwrite    = options['overwrite']
        dry_run      = options['dry_run']

        client = None
        if not dry_run:
            client = _get_openai_client()
            if client is not None:
                self.stdout.write(self.style.SUCCESS('Backend: OpenAI GPT-4o\n'))
            else:
                google_tr = _get_google_translator()
                if google_tr is None:
                    raise CommandError(
                        'No translation backend available.\n'
                        'Either set OPENAI_API_KEY=sk-... in .env, '
                        'or install deep-translator: pip install deep-translator'
                    )
                self.stdout.write(self.style.WARNING(
                    'OPENAI_API_KEY not set — using Google Translate (free).\n'
                    'For higher quality, add OPENAI_API_KEY to .env.\n'
                ))

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY-RUN — no API calls, no DB writes.\n'))
        if overwrite:
            self.stdout.write(self.style.WARNING('OVERWRITE — existing Turkish content will be replaced.\n'))

        configs = _get_model_configs()
        total_objs = 0
        total_calls = 0

        for label, Model, field_specs in configs:
            if model_filter != 'all' and label.lower() != model_filter:
                continue

            try:
                queryset = Model.objects.all()
                count = queryset.count()
            except Exception as exc:
                self.stdout.write(self.style.ERROR(f'\n{label}: QUERY ERROR — {exc}'))
                continue

            if count == 0:
                self.stdout.write(f'\n{label}: (no records, skipping)')
                continue

            self.stdout.write(f'\n{"─"*64}')
            self.stdout.write(self.style.MIGRATE_HEADING(f'  {label}  ({count} record(s))'))

            for obj in queryset:
                obj_label = (
                    getattr(obj, 'title_en', None)
                    or getattr(obj, 'name_en', None)
                    or getattr(obj, 'question_en', None)
                    or f'pk={obj.pk}'
                )
                self.stdout.write(f'\n  [{label}] {str(obj_label)[:80]}')

                changed, calls = _translate_object(
                    client, obj, field_specs,
                    overwrite=overwrite,
                    dry_run=dry_run,
                    stdout=self.stdout,
                    style=self.style,
                )
                if changed:
                    total_objs += 1
                total_calls += calls

        self.stdout.write(f'\n{"═"*64}')
        self.stdout.write(self.style.SUCCESS(
            f'Finished.  Records updated: {total_objs}  |  API calls: {total_calls}'
        ))
