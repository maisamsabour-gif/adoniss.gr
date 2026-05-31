import json
from datetime import datetime, timedelta, timezone
from pathlib import Path

from django.conf import settings
from django.contrib import admin
from django.core.management.base import BaseCommand, CommandError
from django.db import connection
from django.db.migrations.executor import MigrationExecutor


class Command(BaseCommand):
    help = "Run pre-deploy safety checks."

    def handle(self, *args, **options):
        self._check_backup_freshness()
        self._check_db_connectivity()
        self._check_pending_migrations()
        self._check_admin_destructive_actions()

        self.stdout.write(self.style.SUCCESS("Pre-deploy checks passed."))

    def _check_backup_freshness(self):
        marker_file = Path(settings.BACKUP_LOCAL_DIR) / "last_backup.json"
        if not marker_file.exists():
            raise CommandError(f"Backup marker not found: {marker_file}")

        marker = json.loads(marker_file.read_text(encoding="utf-8"))
        created_at = datetime.fromisoformat(marker["created_at"])
        age = datetime.now(timezone.utc) - created_at
        if age > timedelta(hours=24):
            raise CommandError(f"Latest backup is too old: {age}.")

        if settings.ENV == "production" and settings.BACKUP_REQUIRE_OFFSITE and not marker.get("s3_key"):
            raise CommandError("Off-site backup key missing in marker for production deploy.")

    def _check_db_connectivity(self):
        with connection.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()

    def _check_pending_migrations(self):
        executor = MigrationExecutor(connection)
        targets = executor.loader.graph.leaf_nodes()
        plan = executor.migration_plan(targets)
        if plan:
            raise CommandError("Pending migrations detected. Review/apply migrations before deploy.")

    def _check_admin_destructive_actions(self):
        actions = dict(admin.site.actions)
        if "delete_selected" in actions:
            raise CommandError("Admin destructive action 'delete_selected' is still enabled.")
