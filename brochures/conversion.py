"""
PDF → WebP conversion using poppler's pdftoppm + Pillow.
Runs synchronously; callers should use start_conversion_thread() for async.
"""
import logging
import os
import shutil
import subprocess
import threading
from pathlib import Path

from django.conf import settings
from PIL import Image

log = logging.getLogger(__name__)

TARGET_WIDTH = 2400   # max pixels wide; supports 3× DPR screens at max zoom
WEBP_QUALITY = 86     # 0-100; slight bump for crispness at larger dimensions
PDF_DPI      = 250    # 250 DPI → ~2067 px for A4; stays sharp at 2.5× pinch-zoom on 3× DPR

# Use absolute path for pdftoppm to avoid PATH issues in Gunicorn workers
PDFTOPPM_BIN = '/usr/bin/pdftoppm'


# ── Low-level conversion ──────────────────────────────────────────────────────

def _pdf_to_webp(pdf_path: str, output_dir: Path, slug: str):
    """
    Convert *pdf_path* to a sequence of WebP images inside *output_dir*.
    Returns (page_count, first_page_width, first_page_height).
    Raises RuntimeError on any failure.
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # pdftoppm writes: <prefix>-<n>.png  (zero-padded where N>9)
    tmp_prefix = str(output_dir / 'tmp')

    cmd = [
        PDFTOPPM_BIN,
        '-r', str(PDF_DPI),
        '-png',
        str(pdf_path),
        tmp_prefix,
    ]
    result = subprocess.run(cmd, capture_output=True, timeout=600)
    if result.returncode != 0:
        raise RuntimeError(
            f'pdftoppm failed (exit {result.returncode}): '
            f'{result.stderr.decode("utf-8", errors="replace")}'
        )

    # Collect generated PNGs (may be named tmp-1.png, tmp-01.png, tmp-001.png …)
    png_files = sorted(output_dir.glob('tmp-*.png'))
    if not png_files:
        png_files = sorted(output_dir.glob('tmp*.png'))
    if not png_files:
        raise RuntimeError('pdftoppm produced no PNG output files')

    page_width = page_height = 0

    for idx, png_path in enumerate(png_files, start=1):
        webp_path = output_dir / f'page-{idx:03d}.webp'
        try:
            with Image.open(png_path) as img:
                # Normalise colour mode (RGBA, P, etc. → RGB)
                if img.mode not in ('RGB', 'L'):
                    img = img.convert('RGB')

                w, h = img.size
                if w > TARGET_WIDTH:
                    ratio    = TARGET_WIDTH / w
                    new_size = (TARGET_WIDTH, int(h * ratio))
                    img      = img.resize(new_size, Image.LANCZOS)
                    w, h     = new_size

                img.save(str(webp_path), 'WEBP', quality=WEBP_QUALITY, method=4)

                if idx == 1:
                    page_width, page_height = w, h
        finally:
            try:
                png_path.unlink()
            except OSError:
                pass

    return len(png_files), page_width, page_height


def _auto_cover(brochure, output_dir: Path):
    """Copy page-001.webp as the brochure's cover_image if none is set."""
    src = output_dir / 'page-001.webp'
    if not src.exists() or brochure.cover_image:
        return

    covers_dir = Path(settings.MEDIA_ROOT) / 'brochures' / 'covers'
    covers_dir.mkdir(parents=True, exist_ok=True)
    dst_rel = f'brochures/covers/{brochure.slug}-cover.webp'
    dst_abs = Path(settings.MEDIA_ROOT) / dst_rel
    shutil.copy2(src, dst_abs)
    brochure.cover_image = dst_rel


# ── High-level job runner ─────────────────────────────────────────────────────

def run_conversion(brochure_id: int):
    """
    Convert the PDF for *brochure_id* (runs in calling thread).
    Updates Brochure fields: conversion_status, page_count, page_width,
    page_height, cover_image, conversion_error.
    """
    from brochures.models import Brochure  # avoid circular import at module level

    try:
        brochure = Brochure.objects.get(pk=brochure_id)
    except Brochure.DoesNotExist:
        log.error('Brochure pk=%s not found – skipping conversion', brochure_id)
        return

    if not brochure.pdf_file:
        log.warning('Brochure pk=%s has no PDF – skipping', brochure_id)
        return

    log.info('Starting conversion for brochure "%s" (pk=%s)', brochure.title, brochure_id)

    brochure.conversion_status = Brochure.STATUS_PROCESSING
    brochure.conversion_error  = ''
    brochure.save(update_fields=['conversion_status', 'conversion_error'])

    output_dir = Path(brochure.pages_dir())

    try:
        # Remove stale pages from a previous (failed) run
        if output_dir.exists():
            for old in output_dir.glob('page-*.webp'):
                old.unlink(missing_ok=True)

        count, pw, ph = _pdf_to_webp(brochure.pdf_file.path, output_dir, brochure.slug)

        brochure.page_count  = count
        brochure.page_width  = pw
        brochure.page_height = ph

        _auto_cover(brochure, output_dir)

        brochure.conversion_status = Brochure.STATUS_READY
        brochure.conversion_error  = ''
        brochure.save(update_fields=[
            'page_count', 'page_width', 'page_height',
            'conversion_status', 'conversion_error', 'cover_image',
        ])
        log.info('Conversion done: "%s" – %d pages', brochure.title, count)

    except Exception as exc:
        log.exception('Conversion failed for brochure pk=%s', brochure_id)
        brochure.conversion_status = Brochure.STATUS_FAILED
        brochure.conversion_error  = str(exc)
        brochure.save(update_fields=['conversion_status', 'conversion_error'])


def start_conversion_thread(brochure_id: int) -> threading.Thread:
    """Kick off *run_conversion* in a daemon background thread."""
    t = threading.Thread(
        target=run_conversion,
        args=(brochure_id,),
        daemon=True,
        name=f'brochure-convert-{brochure_id}',
    )
    t.start()
    return t
