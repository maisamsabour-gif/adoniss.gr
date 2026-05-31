import json
from pathlib import Path

from django.db.models import FileField, ImageField
from django.core.files.base import ContentFile
from django.core.management.base import BaseCommand
from django.core.serializers.json import DjangoJSONEncoder
from django.utils import timezone

from apps.persian_cms.models import (
    PersianBlogPost,
    PersianCTA,
    PersianFAQ,
    PersianFooterSettings,
    PersianMediaAsset,
    PersianMenuItem,
    PersianPage,
    PersianRedirectMap,
    PersianSEOSettings,
    PersianSection,
    PersianExportLog,
)


EXPORT_MODELS = [
    PersianPage,
    PersianSection,
    PersianBlogPost,
    PersianSEOSettings,
    PersianMenuItem,
    PersianFooterSettings,
    PersianMediaAsset,
    PersianCTA,
    PersianFAQ,
    PersianRedirectMap,
]


class Command(BaseCommand):
    help = "Export Persian CMS data to JSON for future domain migration."

    def add_arguments(self, parser):
        parser.add_argument("--output", type=str, default="", help="Optional output file path")

    def handle(self, *args, **options):
        timestamp = timezone.now().strftime("%Y%m%d-%H%M%S")
        output = options.get("output") or f"backups/persian-cms-export-{timestamp}.json"
        output_path = Path(output)
        if not output_path.is_absolute():
            output_path = Path.cwd() / output_path
        output_path.parent.mkdir(parents=True, exist_ok=True)

        payload = {"generated_at": timezone.now().isoformat(), "models": {}, "media_files": []}
        for model in EXPORT_MODELS:
            model_key = model._meta.label_lower
            rows = list(model.objects.all().values())
            payload["models"][model_key] = rows
            payload["media_files"].extend(self._collect_media_paths(model, rows))

        json_bytes = json.dumps(payload, ensure_ascii=False, indent=2, cls=DjangoJSONEncoder).encode("utf-8")
        output_path.write_bytes(json_bytes)
        self.stdout.write(self.style.SUCCESS(f"Exported Persian CMS data: {output_path}"))

        log = PersianExportLog(note="Manual JSON export")
        log.file.save(output_path.name, ContentFile(json_bytes), save=True)

    def _collect_media_paths(self, model, rows):
        file_field_names = [
            field.attname
            for field in model._meta.get_fields()
            if isinstance(field, (FileField, ImageField))
        ]
        media_paths = []
        for row in rows:
            for key in file_field_names:
                value = row.get(key)
                if value:
                    media_paths.append(value)
        return media_paths
