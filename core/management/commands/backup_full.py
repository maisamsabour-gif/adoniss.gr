"""Full site backup: PostgreSQL + .env (bundled) and incremental media sync.

Local artifact (always): a single timestamped tar.gz under BACKUP_LOCAL_DIR
containing the database dump and a copy of .env, with day-based retention.

Off-site (optional, activates when S3/ArvanCloud Object Storage is configured
via BACKUP_S3_BUCKET + AWS_* + BACKUP_S3_ENDPOINT_URL):
  * the daily archive is uploaded under BACKUP_S3_PREFIX,
  * the media/ tree is *incrementally* synced under BACKUP_MEDIA_PREFIX
    (only new/changed files are uploaded — the 1.2GB media set is not
    re-uploaded every day).

Designed to keep working during an international-internet cutoff: with no
off-site target configured it still produces a local archive; when Arvan
(a domestic, S3-compatible store) is configured, backups stay inside Iran.
"""
import os
import shutil
import subprocess
import tarfile
from datetime import datetime, timedelta, timezone
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Full backup: database + .env (local archive) and incremental media sync to object storage."

    def add_arguments(self, parser):
        parser.add_argument("--label", default="daily", help="Backup label (daily/manual/…).")
        parser.add_argument("--skip-upload", action="store_true", help="Local archive only; skip object-storage.")
        parser.add_argument("--skip-media", action="store_true", help="Do not sync the media/ tree.")

    # ── main ──────────────────────────────────────────────────────────────
    def handle(self, *args, **options):
        label = options["label"]
        now = datetime.now(timezone.utc)
        stamp = now.strftime("%Y%m%d-%H%M%S")

        backup_dir = Path(settings.BACKUP_LOCAL_DIR)
        backup_dir.mkdir(parents=True, exist_ok=True)

        work = backup_dir / f".work-{stamp}"
        work.mkdir(parents=True, exist_ok=True)
        try:
            db_file = self._dump_database(work, stamp)
            archive = backup_dir / f"adoniss-{label}-{stamp}.tar.gz"
            self._build_archive(archive, db_file)
        finally:
            shutil.rmtree(work, ignore_errors=True)

        self.stdout.write(self.style.SUCCESS(f"Local archive: {archive.name} ({self._human(archive.stat().st_size)})"))

        self._prune_local(backup_dir, days=settings.BACKUP_RETENTION_DAYS)

        uploaded = False
        media_synced = 0
        if not options["skip_upload"]:
            client, bucket = self._s3_client()
            if client:
                key = f"{settings.BACKUP_S3_PREFIX.strip('/')}/{now.strftime('%Y/%m/%d')}/{archive.name}"
                client.upload_file(str(archive), bucket, key)
                uploaded = True
                self.stdout.write(self.style.SUCCESS(f"Uploaded archive → {bucket}/{key}"))
                if not options["skip_media"]:
                    media_synced = self._sync_media(client, bucket)
                    self.stdout.write(self.style.SUCCESS(f"Media sync: {media_synced} new/changed file(s) uploaded"))
            else:
                if settings.BACKUP_REQUIRE_OFFSITE and settings.ENV == "production":
                    raise CommandError("Off-site backup required in production but object storage is not configured.")
                self.stdout.write(self.style.WARNING(
                    "Object storage not configured (BACKUP_S3_BUCKET/keys/endpoint) — local archive only."
                ))

        self._write_marker(backup_dir, now, archive, label, uploaded, media_synced)

    # ── database dump ───────────────────────────────────────────────────────
    def _dump_database(self, work: Path, stamp: str) -> Path:
        db = settings.DATABASES["default"]
        engine = db.get("ENGINE", "")
        if "postgresql" in engine:
            out = work / "database.sql"
            env = os.environ.copy()
            if db.get("PASSWORD"):
                env["PGPASSWORD"] = db["PASSWORD"]
            cmd = [
                "pg_dump",
                "-h", db.get("HOST", "127.0.0.1"),
                "-p", str(db.get("PORT", "5432")),
                "-U", db.get("USER", ""),
                "--no-owner", "--no-privileges",
                db.get("NAME", ""),
                "-f", str(out),
            ]
            proc = subprocess.run(cmd, env=env, capture_output=True, text=True)
            if proc.returncode != 0:
                raise CommandError(f"pg_dump failed: {proc.stderr.strip()}")
            return out
        if "sqlite3" in engine:
            src = Path(db["NAME"])
            if not src.exists():
                raise CommandError(f"SQLite file not found: {src}")
            out = work / "database.sqlite3"
            shutil.copy2(src, out)
            return out
        raise CommandError(f"Unsupported database engine for backup: {engine}")

    def _build_archive(self, archive: Path, db_file: Path):
        with tarfile.open(archive, "w:gz", compresslevel=6) as tar:
            tar.add(db_file, arcname=db_file.name)
            env_path = Path(settings.BASE_DIR) / ".env"
            if env_path.exists():
                tar.add(env_path, arcname="env")
        os.chmod(archive, 0o600)

    # ── object storage (S3 / ArvanCloud) ────────────────────────────────────
    def _s3_client(self):
        bucket = settings.BACKUP_S3_BUCKET
        key = os.getenv("AWS_ACCESS_KEY_ID")
        secret = os.getenv("AWS_SECRET_ACCESS_KEY")
        if not (bucket and key and secret):
            return None, None
        import boto3
        client = boto3.client(
            "s3",
            endpoint_url=settings.BACKUP_S3_ENDPOINT_URL or None,
            region_name=os.getenv("AWS_S3_REGION_NAME") or None,
            aws_access_key_id=key,
            aws_secret_access_key=secret,
        )
        return client, bucket

    def _sync_media(self, client, bucket) -> int:
        """Upload only media files missing from / differing in size on the bucket."""
        media_root = Path(settings.MEDIA_ROOT)
        if not media_root.exists():
            return 0
        prefix = settings.BACKUP_MEDIA_PREFIX.strip("/")

        remote = {}
        paginator = client.get_paginator("list_objects_v2")
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix + "/"):
            for obj in page.get("Contents", []):
                remote[obj["Key"]] = obj["Size"]

        uploaded = 0
        for path in media_root.rglob("*"):
            if not path.is_file():
                continue
            rel = path.relative_to(media_root).as_posix()
            key = f"{prefix}/{rel}"
            size = path.stat().st_size
            if remote.get(key) == size:
                continue
            client.upload_file(str(path), bucket, key)
            uploaded += 1
        return uploaded

    # ── retention + marker ───────────────────────────────────────────────────
    def _prune_local(self, backup_dir: Path, *, days: int):
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        for f in backup_dir.glob("adoniss-*.tar.gz"):
            mtime = datetime.fromtimestamp(f.stat().st_mtime, tz=timezone.utc)
            if mtime < cutoff:
                f.unlink(missing_ok=True)

    def _write_marker(self, backup_dir, now, archive, label, uploaded, media_synced):
        import json
        marker = {
            "created_at": now.isoformat(),
            "archive": archive.name,
            "size_bytes": archive.stat().st_size,
            "label": label,
            "uploaded_offsite": uploaded,
            "media_files_synced": media_synced,
        }
        with open(backup_dir / "last_backup_full.json", "w", encoding="utf-8") as fh:
            json.dump(marker, fh, indent=2, ensure_ascii=False)

    @staticmethod
    def _human(n: int) -> str:
        for unit in ("B", "KB", "MB", "GB"):
            if n < 1024 or unit == "GB":
                return f"{n:.1f}{unit}" if unit != "B" else f"{n}B"
            n /= 1024
