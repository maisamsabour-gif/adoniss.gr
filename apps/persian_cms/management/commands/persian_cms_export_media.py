import json
import shutil
from pathlib import Path

from django.conf import settings
from django.core.files.storage import default_storage
from django.core.management.base import BaseCommand
from django.db.models import FileField, ImageField
from django.db.utils import OperationalError, ProgrammingError
from django.utils import timezone

from apps.persian_cms.management.commands.persian_cms_export import EXPORT_MODELS


class Command(BaseCommand):
    help = "Export Persian CMS media files into a portable folder structure."

    def add_arguments(self, parser):
        parser.add_argument(
            "--output-dir",
            type=str,
            default="",
            help="Optional export directory (default: backups/persian-cms-media-<timestamp>)",
        )

    def handle(self, *args, **options):
        timestamp = timezone.now().strftime("%Y%m%d-%H%M%S")
        output_dir = options.get("output_dir") or f"backups/persian-cms-media-{timestamp}"
        root = Path(output_dir)
        if not root.is_absolute():
            root = Path.cwd() / root
        media_root = root / "media"
        media_root.mkdir(parents=True, exist_ok=True)

        files = self._collect_files()
        exported = []
        for rel_name in files:
            target = media_root / rel_name
            target.parent.mkdir(parents=True, exist_ok=True)
            copied = self._copy_file(rel_name, target)
            if copied:
                exported.append(rel_name)

        manifest = {
            "generated_at": timezone.now().isoformat(),
            "count": len(exported),
            "files": sorted(exported),
        }
        (root / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
        self.stdout.write(self.style.SUCCESS(f"Exported {len(exported)} media files into {root}"))

    def _collect_files(self):
        file_names = set()
        for model in EXPORT_MODELS:
            try:
                rows = list(model.objects.all().values())
            except (OperationalError, ProgrammingError):
                continue
            file_fields = [
                field.attname
                for field in model._meta.get_fields()
                if isinstance(field, (FileField, ImageField))
            ]
            for row in rows:
                for key in file_fields:
                    value = row.get(key)
                    if value:
                        file_names.add(str(value).strip("/"))
        return sorted(file_names)

    def _copy_file(self, rel_name: str, target: Path) -> bool:
        local_source = Path(settings.MEDIA_ROOT) / rel_name
        if local_source.exists():
            shutil.copy2(local_source, target)
            return True
        if default_storage.exists(rel_name):
            with default_storage.open(rel_name, "rb") as src, target.open("wb") as dst:
                shutil.copyfileobj(src, dst)
            return True
        self.stderr.write(f"Skipped missing media file: {rel_name}")
        return False
