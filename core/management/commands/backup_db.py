import gzip
import json
import os
import shutil
import subprocess
from datetime import datetime, timedelta, timezone
from pathlib import Path

import boto3
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Create database backup, upload to S3 (optional/required), and apply retention."

    def add_arguments(self, parser):
        parser.add_argument("--label", default="manual", help="Backup label (daily/6h/manual).")
        parser.add_argument("--skip-upload", action="store_true", help="Skip S3 upload (for local testing).")

    def handle(self, *args, **options):
        label = options["label"]
        skip_upload = options["skip_upload"]
        now = datetime.now(timezone.utc)

        backup_dir = Path(settings.BACKUP_LOCAL_DIR)
        backup_dir.mkdir(parents=True, exist_ok=True)

        db_conf = settings.DATABASES["default"]
        engine = db_conf.get("ENGINE", "")
        stamp = now.strftime("%Y%m%d-%H%M%S")
        raw_file = backup_dir / f"db-{label}-{stamp}.sql"
        if "sqlite3" in engine:
            sqlite_path = Path(db_conf["NAME"])
            if not sqlite_path.exists():
                raise CommandError(f"SQLite database file not found: {sqlite_path}")
            raw_file = backup_dir / f"db-{label}-{stamp}.sqlite3"
            shutil.copy2(sqlite_path, raw_file)
        elif "postgresql" in engine:
            env = os.environ.copy()
            if db_conf.get("PASSWORD"):
                env["PGPASSWORD"] = db_conf["PASSWORD"]
            cmd = [
                "pg_dump",
                "-h",
                db_conf.get("HOST", "127.0.0.1"),
                "-p",
                str(db_conf.get("PORT", "5432")),
                "-U",
                db_conf.get("USER", ""),
                db_conf.get("NAME", ""),
                "-f",
                str(raw_file),
            ]
            proc = subprocess.run(cmd, env=env, capture_output=True, text=True)
            if proc.returncode != 0:
                raise CommandError(f"pg_dump failed: {proc.stderr.strip()}")
        else:
            raise CommandError(f"Unsupported database engine for backup: {engine}")

        compressed = Path(f"{raw_file}.gz")
        with open(raw_file, "rb") as src, gzip.open(compressed, "wb", compresslevel=6) as dst:
            shutil.copyfileobj(src, dst)
        raw_file.unlink(missing_ok=True)

        s3_key = ""
        if not skip_upload:
            s3_key = self._upload_to_s3(compressed, now)
        elif settings.BACKUP_REQUIRE_OFFSITE and settings.ENV == "production":
            raise CommandError("Off-site backups are mandatory in production. Remove --skip-upload.")

        self._prune_local_backups(backup_dir, days=settings.BACKUP_RETENTION_DAYS)
        if s3_key:
            self._prune_s3_backups(days=settings.BACKUP_RETENTION_DAYS)

        marker = {
            "created_at": now.isoformat(),
            "file": str(compressed),
            "s3_key": s3_key,
            "label": label,
        }
        with open(backup_dir / "last_backup.json", "w", encoding="utf-8") as fh:
            json.dump(marker, fh, indent=2)

        self.stdout.write(self.style.SUCCESS(f"Backup created: {compressed.name}"))
        if s3_key:
            self.stdout.write(self.style.SUCCESS(f"Uploaded to S3: {s3_key}"))

    def _upload_to_s3(self, local_file: Path, now: datetime) -> str:
        bucket = settings.BACKUP_S3_BUCKET
        if not bucket:
            if settings.BACKUP_REQUIRE_OFFSITE and settings.ENV == "production":
                raise CommandError("BACKUP_S3_BUCKET must be configured in production.")
            self.stdout.write(self.style.WARNING("Skipping S3 upload: BACKUP_S3_BUCKET is not configured."))
            return ""

        prefix = settings.BACKUP_S3_PREFIX.strip("/")
        s3_key = f"{prefix}/{now.strftime('%Y/%m/%d')}/{local_file.name}"
        client = boto3.client(
            "s3",
            region_name=os.getenv("AWS_S3_REGION_NAME") or None,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID") or None,
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY") or None,
        )
        client.upload_file(str(local_file), bucket, s3_key)
        return s3_key

    def _prune_local_backups(self, backup_dir: Path, *, days: int):
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        for file_path in backup_dir.glob("db-*.gz"):
            mtime = datetime.fromtimestamp(file_path.stat().st_mtime, tz=timezone.utc)
            if mtime < cutoff:
                file_path.unlink(missing_ok=True)

    def _prune_s3_backups(self, *, days: int):
        bucket = settings.BACKUP_S3_BUCKET
        if not bucket:
            return

        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        client = boto3.client(
            "s3",
            region_name=os.getenv("AWS_S3_REGION_NAME") or None,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID") or None,
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY") or None,
        )

        paginator = client.get_paginator("list_objects_v2")
        prefix = settings.BACKUP_S3_PREFIX.strip("/") + "/"
        to_delete = []
        for page in paginator.paginate(Bucket=bucket, Prefix=prefix):
            for obj in page.get("Contents", []):
                if obj["LastModified"] < cutoff:
                    to_delete.append({"Key": obj["Key"]})

        for i in range(0, len(to_delete), 1000):
            chunk = to_delete[i : i + 1000]
            client.delete_objects(Bucket=bucket, Delete={"Objects": chunk})
