import gzip
import os
import shutil
import subprocess
from pathlib import Path

import boto3
from django.conf import settings
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Restore database backup (intended for staging / drills)."

    def add_arguments(self, parser):
        parser.add_argument("--local-file", help="Path to local .gz backup file.")
        parser.add_argument("--s3-key", help="S3 key to download and restore.")
        parser.add_argument("--dry-run", action="store_true", help="Validate restore steps without mutating DB.")
        parser.add_argument("--force-production", action="store_true", help="Override production safety guard.")

    def handle(self, *args, **options):
        if settings.ENV == "production" and not options["force_production"]:
            raise CommandError("Restore is blocked in production unless --force-production is explicitly provided.")

        local_file = options.get("local_file")
        s3_key = options.get("s3_key")
        dry_run = options.get("dry_run")

        if not local_file and not s3_key:
            raise CommandError("Provide either --local-file or --s3-key.")

        if local_file and s3_key:
            raise CommandError("Use only one of --local-file or --s3-key.")

        backup_path = Path(local_file) if local_file else self._download_s3_backup(s3_key)
        if not backup_path.exists():
            raise CommandError(f"Backup file not found: {backup_path}")

        self.stdout.write(self.style.WARNING(f"Using backup: {backup_path}"))
        if dry_run:
            self.stdout.write(self.style.SUCCESS("Dry run successful. No changes applied."))
            return

        db_conf = settings.DATABASES["default"]
        engine = db_conf.get("ENGINE", "")
        if "sqlite3" in engine:
            self._restore_sqlite(backup_path, Path(db_conf["NAME"]))
        elif "postgresql" in engine:
            self._restore_postgres(backup_path, db_conf)
        else:
            raise CommandError(f"Unsupported engine for restore: {engine}")

        self.stdout.write(self.style.SUCCESS("Restore completed successfully."))

    def _download_s3_backup(self, s3_key):
        bucket = settings.BACKUP_S3_BUCKET
        if not bucket:
            raise CommandError("BACKUP_S3_BUCKET is not configured.")

        tmp_dir = Path(settings.BACKUP_LOCAL_DIR)
        tmp_dir.mkdir(parents=True, exist_ok=True)
        local_path = tmp_dir / Path(s3_key).name

        client = boto3.client(
            "s3",
            region_name=os.getenv("AWS_S3_REGION_NAME") or None,
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID") or None,
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY") or None,
        )
        client.download_file(bucket, s3_key, str(local_path))
        return local_path

    def _restore_sqlite(self, backup_path: Path, db_path: Path):
        pre_restore = db_path.with_suffix(db_path.suffix + ".pre-restore")
        if db_path.exists():
            shutil.copy2(db_path, pre_restore)

        with gzip.open(backup_path, "rb") as src, open(db_path, "wb") as dst:
            shutil.copyfileobj(src, dst)

    def _restore_postgres(self, backup_path: Path, db_conf):
        temp_sql = Path(str(backup_path).replace(".gz", ""))
        with gzip.open(backup_path, "rb") as src, open(temp_sql, "wb") as dst:
            shutil.copyfileobj(src, dst)

        env = os.environ.copy()
        if db_conf.get("PASSWORD"):
            env["PGPASSWORD"] = db_conf["PASSWORD"]
        cmd = [
            "psql",
            "-h",
            db_conf.get("HOST", "127.0.0.1"),
            "-p",
            str(db_conf.get("PORT", "5432")),
            "-U",
            db_conf.get("USER", ""),
            "-d",
            db_conf.get("NAME", ""),
            "-f",
            str(temp_sql),
        ]
        proc = subprocess.run(cmd, env=env, capture_output=True, text=True)
        temp_sql.unlink(missing_ok=True)
        if proc.returncode != 0:
            raise CommandError(f"psql restore failed: {proc.stderr.strip()}")
