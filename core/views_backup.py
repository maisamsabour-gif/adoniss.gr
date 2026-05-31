import gzip
import json
import logging
import os
import shutil
import subprocess
import zipfile
from datetime import datetime, timezone
from pathlib import Path

from django.conf import settings
from django.contrib.admin.views.decorators import staff_member_required
from django.http import FileResponse, JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_GET, require_POST

logger = logging.getLogger(__name__)

BACKUP_DIR = Path(settings.BACKUP_LOCAL_DIR)
SITE_BACKUP_ZIP = BACKUP_DIR / "site_full_backup.zip"
SITE_BACKUP_META = BACKUP_DIR / "site_backup_meta.json"
STALE_FLAG = BACKUP_DIR / ".backup_stale"


def _superuser_required(view_func):
    """Decorator: staff_member_required + is_superuser check."""
    from functools import wraps
    from django.http import HttpResponseForbidden

    @staff_member_required
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if not request.user.is_superuser:
            return HttpResponseForbidden("Access denied.")
        return view_func(request, *args, **kwargs)

    return wrapper


def _get_backup_meta():
    """Read backup metadata if it exists."""
    if not SITE_BACKUP_META.exists():
        return None
    try:
        with open(SITE_BACKUP_META, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


def _is_backup_stale():
    return STALE_FLAG.exists() or not SITE_BACKUP_ZIP.exists()


def mark_backup_stale():
    """Called by signals to flag that a new backup is needed."""
    try:
        BACKUP_DIR.mkdir(parents=True, exist_ok=True)
        STALE_FLAG.touch()
    except OSError:
        logger.warning("Could not mark backup as stale.")


def _dump_database(target_dir: Path) -> Path:
    """Dump the database into target_dir; return the path of the dump file."""
    db_conf = settings.DATABASES["default"]
    engine = db_conf.get("ENGINE", "")

    if "sqlite3" in engine:
        src = Path(db_conf["NAME"])
        dst = target_dir / src.name
        shutil.copy2(src, dst)
        return dst

    if "postgresql" in engine:
        dump_file = target_dir / "database.sql"
        env = os.environ.copy()
        if db_conf.get("PASSWORD"):
            env["PGPASSWORD"] = db_conf["PASSWORD"]
        cmd = [
            "pg_dump",
            "-h", db_conf.get("HOST", "127.0.0.1"),
            "-p", str(db_conf.get("PORT", "5432")),
            "-U", db_conf.get("USER", ""),
            db_conf.get("NAME", ""),
            "-f", str(dump_file),
        ]
        proc = subprocess.run(cmd, env=env, capture_output=True, text=True)
        if proc.returncode != 0:
            raise RuntimeError(f"pg_dump failed: {proc.stderr.strip()}")
        return dump_file

    raise RuntimeError(f"Unsupported DB engine: {engine}")


def _generate_backup():
    """Create a zip file containing the full database + media directory."""
    import tempfile

    BACKUP_DIR.mkdir(parents=True, exist_ok=True)
    tmp_zip = BACKUP_DIR / "site_full_backup.zip.tmp"

    try:
        with zipfile.ZipFile(tmp_zip, "w", zipfile.ZIP_DEFLATED, compresslevel=6) as zf:
            with tempfile.TemporaryDirectory() as tmpdir:
                db_file = _dump_database(Path(tmpdir))
                zf.write(db_file, f"database/{db_file.name}")

            media_root = Path(settings.MEDIA_ROOT)
            if media_root.exists():
                for file_path in media_root.rglob("*"):
                    if file_path.is_file():
                        arcname = f"media/{file_path.relative_to(media_root)}"
                        zf.write(file_path, arcname)

        shutil.move(str(tmp_zip), str(SITE_BACKUP_ZIP))

        meta = {
            "created_at": datetime.now(timezone.utc).isoformat(),
            "size_bytes": SITE_BACKUP_ZIP.stat().st_size,
            "db_engine": settings.DATABASES["default"].get("ENGINE", ""),
        }
        with open(SITE_BACKUP_META, "w", encoding="utf-8") as f:
            json.dump(meta, f, indent=2)

        STALE_FLAG.unlink(missing_ok=True)
        return meta

    except Exception:
        tmp_zip.unlink(missing_ok=True)
        raise


def _format_size(size_bytes):
    for unit in ("B", "KB", "MB", "GB"):
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


@_superuser_required
def site_backup_page(request):
    """Admin page showing backup status with generate/download actions."""
    meta = _get_backup_meta()
    stale = _is_backup_stale()

    context = {
        "title": "Site Full Backup",
        "has_backup": SITE_BACKUP_ZIP.exists(),
        "is_stale": stale,
        "meta": meta,
        "formatted_size": _format_size(meta["size_bytes"]) if meta and "size_bytes" in meta else "—",
        "formatted_date": meta["created_at"][:19].replace("T", " ") + " UTC" if meta else "—",
    }
    return render(request, "admin/site_backup.html", context)


@_superuser_required
@require_POST
def site_backup_generate(request):
    """AJAX endpoint: generate a fresh backup zip."""
    try:
        meta = _generate_backup()
        return JsonResponse({
            "ok": True,
            "size": _format_size(meta["size_bytes"]),
            "date": meta["created_at"][:19].replace("T", " ") + " UTC",
        })
    except Exception as exc:
        logger.exception("Backup generation failed")
        return JsonResponse({"ok": False, "error": str(exc)}, status=500)


@_superuser_required
@require_GET
def site_backup_download(request):
    """Stream the backup zip to the superadmin."""
    if not SITE_BACKUP_ZIP.exists():
        return JsonResponse({"error": "No backup available. Generate one first."}, status=404)

    stamp = datetime.now(timezone.utc).strftime("%Y%m%d-%H%M%S")
    return FileResponse(
        open(SITE_BACKUP_ZIP, "rb"),
        as_attachment=True,
        filename=f"adonis_site_backup_{stamp}.zip",
        content_type="application/zip",
    )
