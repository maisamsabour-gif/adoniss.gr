import io
import logging
import os
import shutil
import subprocess
import tempfile

from django.core.files.base import ContentFile
from django.db.models import FileField, ImageField
from django.db.models.signals import post_delete, post_save, pre_save
from django.dispatch import receiver

logger = logging.getLogger(__name__)

_BACKUP_TRACKED_APPS = {"core", "properties", "brochures"}


def _should_track(sender):
    app_label = getattr(sender, "_meta", None)
    if app_label is None:
        return False
    return app_label.app_label in _BACKUP_TRACKED_APPS


@receiver(post_save, dispatch_uid="adonis_backup_mark_stale_on_save")
def mark_stale_on_save(sender, **kwargs):
    if _should_track(sender):
        from core.views_backup import mark_backup_stale
        mark_backup_stale()


@receiver(post_delete, dispatch_uid="adonis_backup_mark_stale_on_delete")
def mark_stale_on_delete(sender, **kwargs):
    if _should_track(sender):
        from core.views_backup import mark_backup_stale
        mark_backup_stale()


# ─────────────────────────────────────────────────────────────────────────────
#   Automatic media compression on upload
#   ----------------------------------------------------------------------
#   • ImageField → re-encode to WebP (quality=82, method=6), keep original
#     basename, swap extension, point the FileField at the new file, then
#     delete the original on disk.
#   • FileField with `.mp4` extension → re-encode in place via ffmpeg
#     (libx264 CRF 28, +faststart, AAC 128k). Replace the original ONLY if
#     the re-encoded copy is strictly smaller.
#   • Existing rows in the DB are left alone — we only act on FieldFiles
#     whose value changed during this save (snapshot taken in pre_save).
#   • Every code path is wrapped in try/except so a failure can never
#     destroy or null out the original FileField value.
#
#   WARNING: video re-encoding runs synchronously inside the request that
#   triggered the model save. ffmpeg can take seconds-to-minutes for large
#   files. For large/frequent uploads, move this to a Celery/RQ task —
#   the helpers below are safe to call from a background worker.
# ─────────────────────────────────────────────────────────────────────────────

_COMPRESSION_APPS = _BACKUP_TRACKED_APPS  # same scope as backup tracking
_WEBP_QUALITY = 82
_WEBP_METHOD = 6
_IMAGE_SOURCE_EXTS = {".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".tif"}
_VIDEO_SOURCE_EXTS = {".mp4"}
_FFMPEG_TIMEOUT_SEC = 1800  # 30 min ceiling per video
_FFMPEG_BIN = shutil.which("ffmpeg")  # resolved once at import time


def _is_compressible_app(sender) -> bool:
    meta = getattr(sender, "_meta", None)
    return meta is not None and meta.app_label in _COMPRESSION_APPS


def _iter_file_fields(instance):
    """Yield (field, fieldfile) for every ImageField / FileField on the model."""
    for field in instance._meta.get_fields():
        if not isinstance(field, (ImageField, FileField)):
            continue
        try:
            fieldfile = getattr(instance, field.attname)
        except Exception:
            continue
        yield field, fieldfile


def _local_path(fieldfile):
    """Return the on-disk path if the storage backend supports it, else None."""
    if not fieldfile or not fieldfile.name:
        return None
    try:
        return fieldfile.path
    except (NotImplementedError, ValueError, AttributeError):
        return None


@receiver(pre_save, dispatch_uid="adonis_media_compression_pre_save")
def _snapshot_old_file_names(sender, instance, raw=False, **kwargs):
    """Capture the previous DB values of file fields so post_save can detect changes."""
    if raw or not _is_compressible_app(sender):
        return
    old = {}
    if instance.pk is not None:
        try:
            file_field_names = [
                f.attname
                for f in instance._meta.get_fields()
                if isinstance(f, (ImageField, FileField))
            ]
            if file_field_names:
                prev = sender._default_manager.only(*file_field_names).get(pk=instance.pk)
                for attname in file_field_names:
                    old[attname] = getattr(prev, attname).name or ""
        except sender.DoesNotExist:
            pass
        except Exception:
            logger.exception("media-compress: pre_save snapshot failed for %s pk=%s",
                             sender.__name__, instance.pk)
    instance._adonis_old_files = old


@receiver(post_save, dispatch_uid="adonis_media_compression_post_save")
def _compress_changed_media(sender, instance, created, raw=False, **kwargs):
    if raw or not _is_compressible_app(sender):
        return
    # Re-entry guard — set when this handler triggers its own .save() below.
    if getattr(instance, "_adonis_compression_done", False):
        return

    old_files = getattr(instance, "_adonis_old_files", {}) or {}
    fields_to_update = []

    for field, fieldfile in _iter_file_fields(instance):
        if not fieldfile or not fieldfile.name:
            continue

        # Req #5: never touch a FieldFile whose value did not change in this save.
        if not created and old_files.get(field.attname, "") == fieldfile.name:
            continue

        path = _local_path(fieldfile)
        if not path:
            logger.warning("media-compress: %s.%s — non-local storage, skipping",
                           sender.__name__, field.name)
            continue
        if not os.path.exists(path):
            logger.warning("media-compress: %s.%s — file missing on disk: %s",
                           sender.__name__, field.name, path)
            continue

        ext = os.path.splitext(fieldfile.name)[1].lower()

        try:
            if isinstance(field, ImageField):
                if ext == ".webp" or ext not in _IMAGE_SOURCE_EXTS:
                    continue  # already optimal, animated, or unknown — skip
                new_name = _convert_image_to_webp(instance, field, fieldfile)
                if new_name and new_name != fieldfile.name:
                    fields_to_update.append(field.name)
            elif isinstance(field, FileField):
                if ext in _VIDEO_SOURCE_EXTS:
                    _reencode_mp4_in_place(fieldfile)
                # PDFs and other FileField content are intentionally left alone.
        except Exception:
            logger.exception(
                "media-compress: failed processing %s.%s (file=%s); original preserved",
                sender.__name__, field.name, fieldfile.name,
            )
            continue

    if fields_to_update:
        instance._adonis_compression_done = True
        try:
            instance.save(update_fields=fields_to_update)
        except Exception:
            logger.exception("media-compress: failed persisting webp paths for %s pk=%s",
                             sender.__name__, instance.pk)


def _convert_image_to_webp(instance, field, fieldfile):
    """Encode `fieldfile` to WebP. On success, swap storage name + delete original.
    Returns the new storage name (e.g. 'blog/foo.webp') or None if nothing changed.
    """
    try:
        from PIL import Image
    except ImportError:
        logger.warning("media-compress: Pillow unavailable, skipping image %s", fieldfile.name)
        return None

    src_path = _local_path(fieldfile)
    if not src_path:
        return None
    src_name = fieldfile.name  # e.g. 'blog/photo.png'
    base, _ext = os.path.splitext(src_name)
    target_name = f"{base}.webp"

    # Encode into memory
    with Image.open(src_path) as img:
        if img.mode in ("P", "CMYK"):
            img = img.convert("RGBA" if "transparency" in img.info else "RGB")
        elif img.mode not in ("RGB", "RGBA"):
            img = img.convert("RGB")
        buf = io.BytesIO()
        img.save(buf, "WEBP", quality=_WEBP_QUALITY, method=_WEBP_METHOD)
    encoded = buf.getvalue()

    storage = fieldfile.storage
    old_size = os.path.getsize(src_path)
    new_size = len(encoded)

    # Don't blow away an existing webp at the target path (e.g. uploaded earlier
    # under the same basename) — overwrite cleanly.
    if storage.exists(target_name) and target_name != src_name:
        try:
            storage.delete(target_name)
        except Exception:
            logger.warning("media-compress: could not remove pre-existing %s", target_name)

    # Persist via storage so layout / permissions match Django's expectations.
    saved_name = storage.save(target_name, ContentFile(encoded))

    # Point the model field at the new file (descriptor accepts a string).
    setattr(instance, field.attname, saved_name)

    # Remove the original file ONLY after the new one is safely on disk.
    if src_name != saved_name:
        try:
            if storage.exists(src_name):
                storage.delete(src_name)
        except Exception:
            logger.warning("media-compress: could not delete original %s", src_name)

    logger.info(
        "media-compress: image %s -> %s (%.1f KB -> %.1f KB, %.0f%% smaller)",
        src_name, saved_name,
        old_size / 1024, new_size / 1024,
        100 * (1 - new_size / max(old_size, 1)),
    )
    return saved_name


def _reencode_mp4_in_place(fieldfile):
    """Re-encode an .mp4 with libx264 CRF 28 + faststart. Replace original only if smaller."""
    if not _FFMPEG_BIN:
        logger.warning("media-compress: ffmpeg not installed; skipping video %s", fieldfile.name)
        return

    src_path = _local_path(fieldfile)
    if not src_path:
        return

    src_dir = os.path.dirname(src_path) or "."
    fd, tmp_path = tempfile.mkstemp(prefix=".adonis_compress_", suffix=".mp4", dir=src_dir)
    os.close(fd)

    try:
        cmd = [
            _FFMPEG_BIN, "-y", "-loglevel", "error", "-nostdin",
            "-i", src_path,
            "-vcodec", "libx264",
            "-crf", "28",
            "-preset", "fast",
            "-movflags", "+faststart",
            "-acodec", "aac",
            "-b:a", "128k",
            tmp_path,
        ]
        result = subprocess.run(cmd, capture_output=True, timeout=_FFMPEG_TIMEOUT_SEC)
        if result.returncode != 0:
            logger.warning(
                "media-compress: ffmpeg failed for %s (rc=%s): %s",
                fieldfile.name, result.returncode,
                result.stderr.decode("utf-8", errors="replace")[:500],
            )
            return

        new_size = os.path.getsize(tmp_path)
        old_size = os.path.getsize(src_path)
        if new_size >= old_size:
            logger.info(
                "media-compress: re-encoded %s not smaller (%d >= %d); keeping original",
                fieldfile.name, new_size, old_size,
            )
            return

        os.replace(tmp_path, src_path)
        tmp_path = None  # ownership transferred — don't delete in finally
        logger.info(
            "media-compress: video %s shrunk %.1f MB -> %.1f MB (%.0f%% smaller)",
            fieldfile.name, old_size / 1_048_576, new_size / 1_048_576,
            100 * (1 - new_size / max(old_size, 1)),
        )
    except subprocess.TimeoutExpired:
        logger.warning("media-compress: ffmpeg timed out (>%ss) for %s",
                       _FFMPEG_TIMEOUT_SEC, fieldfile.name)
    except Exception:
        logger.exception("media-compress: unexpected ffmpeg error for %s", fieldfile.name)
    finally:
        if tmp_path and os.path.exists(tmp_path):
            try:
                os.remove(tmp_path)
            except OSError:
                pass
