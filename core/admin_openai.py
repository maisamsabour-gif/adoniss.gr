"""
OpenAI auto-translate utilities for Django Admin.

Provides two admin actions per model:
  • "Auto-translate to Turkish (skip existing)" — only fills empty TR fields.
  • "Auto-translate to Turkish (overwrite existing)" — overwrites all TR fields;
    shows an intermediate confirmation page if any TR fields already have content.

Usage in an admin class::

    from core.admin_openai import make_translate_actions

    FIELD_PAIRS = [
        ('title_en', 'title_tr'),
        ('excerpt_en', 'excerpt_tr'),
        ...
    ]

    @admin.register(BlogPost)
    class BlogPostAdmin(...):
        actions = make_translate_actions(FIELD_PAIRS)
        ...

Requires ``OPENAI_API_KEY`` in environment (or .env file).
"""

import logging
import os
import threading

from django.contrib import admin, messages
from django.http import HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse
from django.utils.text import slugify

logger = logging.getLogger(__name__)

_SYSTEM_PROMPT = (
    "You are a professional Turkish translator. Translate to Istanbul Turkish. "
    "Keep SEO-friendly tone. Preserve any HTML formatting. "
    "Return only the translated text, nothing else."
)


# ── OpenAI helpers ────────────────────────────────────────────────────────────

def _get_client():
    """Return an OpenAI client, or None if the key is not configured."""
    api_key = os.getenv('OPENAI_API_KEY', '').strip()
    if not api_key:
        return None
    try:
        from openai import OpenAI
        return OpenAI(api_key=api_key)
    except Exception as exc:
        logger.error('Failed to create OpenAI client: %s', exc)
        return None


def _translate(client, text: str) -> str:
    """Translate *text* to Turkish via GPT-4o. Returns '' for blank input."""
    text = (text or '').strip()
    if not text:
        return ''
    response = client.chat.completions.create(
        model='gpt-4o',
        messages=[
            {'role': 'system', 'content': _SYSTEM_PROMPT},
            {'role': 'user', 'content': text},
        ],
        temperature=0.3,
    )
    return response.choices[0].message.content.strip()


# ── Core translation logic ────────────────────────────────────────────────────

def _has_any_tr_content(obj, field_pairs) -> bool:
    """Return True if any TR field on *obj* already contains text."""
    for _en, tr in field_pairs:
        if (getattr(obj, tr, None) or '').strip():
            return True
    return False


def _translate_obj(client, obj, field_pairs, force: bool):
    """
    Fill TR fields on *obj* from their EN counterparts via OpenAI.

    Returns:
        (changed: bool, skipped: list[str])   — list of TR field names that
        were skipped because they already had content and force=False.
    """
    changed = False
    skipped = []

    for en_field, tr_field in field_pairs:
        en_val = (getattr(obj, en_field, None) or '').strip()
        tr_val = (getattr(obj, tr_field, None) or '').strip()

        if not en_val:
            continue  # nothing to translate

        if tr_val and not force:
            skipped.append(tr_field)
            continue

        translated = _translate(client, en_val)
        setattr(obj, tr_field, translated)
        changed = True

    # Auto-generate Turkish slug from translated title (never send slug to API)
    if changed and hasattr(obj, 'title_tr') and hasattr(obj, 'slug_tr'):
        if obj.title_tr and not (obj.slug_tr or '').strip():
            obj.slug_tr = slugify(obj.title_tr)

    return changed, skipped


def _run_translation(modeladmin, request, queryset, field_pairs, force: bool):
    """Execute the translation loop and emit admin messages."""
    client = _get_client()
    if not client:
        modeladmin.message_user(
            request,
            (
                'OPENAI_API_KEY is not configured. '
                'Add OPENAI_API_KEY=sk-... to your .env file and restart the server.'
            ),
            level=messages.ERROR,
        )
        return

    translated = 0
    all_skipped = []
    errors = 0

    for obj in queryset:
        try:
            changed, skipped = _translate_obj(client, obj, field_pairs, force=force)
            if changed:
                obj.save()
                translated += 1
            all_skipped.extend(skipped)
        except Exception as exc:
            errors += 1
            logger.exception('Error auto-translating %s (pk=%s): %s', obj, obj.pk, exc)
            modeladmin.message_user(
                request,
                f'Error translating "{obj}": {str(exc)[:120]}',
                level=messages.ERROR,
            )

    if translated:
        modeladmin.message_user(
            request,
            f'Successfully translated {translated} object(s) to Turkish.',
        )
    if all_skipped:
        modeladmin.message_user(
            request,
            (
                f'{len(all_skipped)} Turkish field(s) already had content and were skipped. '
                'Use "Auto-translate to Turkish (overwrite)" to overwrite them.'
            ),
            level=messages.WARNING,
        )
    if errors:
        modeladmin.message_user(
            request,
            f'{errors} object(s) failed — see error messages above.',
            level=messages.ERROR,
        )


# ── Confirmation page for the overwrite action ────────────────────────────────

_CONFIRM_TEMPLATE = 'admin/auto_translate_confirm.html'


def _overwrite_action_handler(modeladmin, request, queryset, field_pairs):
    """
    Handle the overwrite action:
      • If none of the selected objects have Turkish content → translate immediately.
      • Otherwise → render a confirmation page.
      • On confirmation (POST with confirm=1) → translate with force=True.
    """
    # Check whether any selected object has existing TR content
    needs_confirm = any(_has_any_tr_content(obj, field_pairs) for obj in queryset)

    if needs_confirm and request.POST.get('confirm_overwrite') != '1':
        # Render confirmation page
        objects_with_tr = [
            obj for obj in queryset if _has_any_tr_content(obj, field_pairs)
        ]
        return render(
            request,
            _CONFIRM_TEMPLATE,
            {
                'title': 'Confirm Auto-Translate (Overwrite)',
                'queryset': queryset,
                'objects_with_tr': objects_with_tr,
                'opts': modeladmin.model._meta,
                'action_checkbox_name': admin.helpers.ACTION_CHECKBOX_NAME,
                'media': modeladmin.media,
            },
        )

    # User confirmed (or no TR content existed) — run with force
    _run_translation(modeladmin, request, queryset, field_pairs, force=True)


# ── Auto-translate on save helper ─────────────────────────────────────────────

def auto_translate_fields_async(obj, field_pairs):
    """
    Background helper for save_model overrides.

    Spawns a daemon thread that translates all empty TR fields from their EN
    counterparts using OpenAI.  Runs *after* the object has already been saved,
    so the thread operates on an existing DB row.

    No exception is ever raised to the caller — errors are only logged.

    Usage in ModelAdmin.save_model::

        def save_model(self, request, obj, form, change):
            super().save_model(request, obj, form, change)
            auto_translate_fields_async(obj, FIELD_PAIRS)
    """
    client = _get_client()
    if not client:
        logger.warning(
            'auto_translate_fields_async: OPENAI_API_KEY not set — skipping.'
        )
        return

    def _work():
        try:
            changed, _ = _translate_obj(client, obj, field_pairs, force=False)
            if changed:
                obj.save()
                logger.info(
                    'auto_translate: saved Turkish fields for %s (pk=%s)',
                    obj.__class__.__name__, obj.pk,
                )
        except Exception as exc:
            logger.exception(
                'auto_translate: error translating %s (pk=%s): %s',
                obj.__class__.__name__, obj.pk, exc,
            )

    t = threading.Thread(target=_work, daemon=True)
    t.start()


# ── Public factory ─────────────────────────────────────────────────────────────

def make_translate_actions(field_pairs):
    """
    Return a list of two admin action callables for *field_pairs*.

    Attach directly to ``actions`` in a ModelAdmin::

        actions = make_translate_actions(FIELD_PAIRS) + ['archive_selected', ...]
    """

    def translate_skip(modeladmin, request, queryset):
        _run_translation(modeladmin, request, queryset, field_pairs, force=False)

    translate_skip.short_description = '🌍 Auto-translate to Turkish (skip existing)'
    translate_skip.__name__ = 'auto_translate_tr_skip'

    def translate_overwrite(modeladmin, request, queryset):
        return _overwrite_action_handler(modeladmin, request, queryset, field_pairs)

    translate_overwrite.short_description = '🌍 Auto-translate to Turkish (overwrite existing)'
    translate_overwrite.__name__ = 'auto_translate_tr_overwrite'

    return [translate_skip, translate_overwrite]
