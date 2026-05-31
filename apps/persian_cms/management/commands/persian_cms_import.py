import json
from pathlib import Path

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

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
)


IMPORT_MODEL_MAP = {
    "persian_cms.persianpage": PersianPage,
    "persian_cms.persiansection": PersianSection,
    "persian_cms.persianblogpost": PersianBlogPost,
    "persian_cms.persianseosettings": PersianSEOSettings,
    "persian_cms.persianmenuitem": PersianMenuItem,
    "persian_cms.persianfootersettings": PersianFooterSettings,
    "persian_cms.persianmediaasset": PersianMediaAsset,
    "persian_cms.persiancta": PersianCTA,
    "persian_cms.persianfaq": PersianFAQ,
    "persian_cms.persianredirectmap": PersianRedirectMap,
}


class Command(BaseCommand):
    help = "Import Persian CMS JSON export into current database."

    def add_arguments(self, parser):
        parser.add_argument("--input", required=True, type=str, help="Path to export json")
        parser.add_argument("--truncate", action="store_true", help="Delete existing rows before import")

    @transaction.atomic
    def handle(self, *args, **options):
        input_path = Path(options["input"])
        if not input_path.is_absolute():
            input_path = Path.cwd() / input_path
        if not input_path.exists():
            raise CommandError(f"Input file not found: {input_path}")

        payload = json.loads(input_path.read_text(encoding="utf-8"))
        models_payload = payload.get("models", {})
        truncate = options.get("truncate", False)

        for model_label, model in IMPORT_MODEL_MAP.items():
            records = models_payload.get(model_label, [])
            if truncate:
                model.objects.all().delete()
            for record in records:
                pk = record.get("id")
                if pk is None:
                    continue
                defaults = {k: v for k, v in record.items() if k != "id"}
                model.objects.update_or_create(id=pk, defaults=defaults)
            self.stdout.write(self.style.SUCCESS(f"Imported {len(records)} rows into {model_label}"))
