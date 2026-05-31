"""
Auto-fill missing alt text (caption_en / caption_tr) for PropertyMedia images.

Usage:
    python manage.py fill_image_alt                 # dry-run (preview only)
    python manage.py fill_image_alt --apply         # write to DB
    python manage.py fill_image_alt --apply --overwrite   # replace ALL, even existing

Templates used
--------------
EN:  "{name} – {location} real estate | Golden Visa property"
     variant picks rotate based on the image index inside the property gallery.

TR:  "{name} – {location} gayrimenkul | Altın Vize mülkü"
"""

import random
from django.core.management.base import BaseCommand
from properties.models import Property, PropertyMedia


EN_TEMPLATES = [
    "{name} – {location} real estate investment | Greece Golden Visa",
    "{name} | Luxury property in {location}, Greece",
    "Greece Golden Visa property – {name}, {location}",
    "{name} – Athens real estate | Golden Visa investment",
    "Premium Greek property – {name} | {location}",
    "{name} | Invest in Greece, {location}",
]

TR_TEMPLATES = [
    "{name} – {location} gayrimenkul yatırımı | Yunanistan Altın Vize",
    "{name} | {location}, Yunanistan'da lüks mülk",
    "Yunanistan Altın Vize mülkü – {name}, {location}",
    "{name} – {location} | Altın Vize yatırım fırsatı",
    "Premium Yunan mülkü – {name} | {location}",
    "{name} | Yunanistan'da yatırım, {location}",
]


class Command(BaseCommand):
    help = (
        "Auto-fill missing caption_en / caption_tr for PropertyMedia images. "
        "Run with --apply to write to DB (default is dry-run)."
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--apply',
            action='store_true',
            help='Actually save changes to the database (default: dry-run).',
        )
        parser.add_argument(
            '--overwrite',
            action='store_true',
            help='Overwrite even fields that already have a value.',
        )

    def handle(self, *args, **options):
        apply = options['apply']
        overwrite = options['overwrite']

        if not apply:
            self.stdout.write(self.style.WARNING(
                "DRY-RUN mode — no changes written. Pass --apply to save."
            ))

        updated = 0
        skipped = 0

        for prop in Property.objects.filter(is_active=True).prefetch_related('media'):
            name_en = (prop.name_en or prop.name or '').strip()
            name_tr = (prop.name_tr or name_en).strip()
            loc_en = (prop.location_en or prop.location or 'Greece').strip()
            loc_tr = (prop.location_tr or loc_en).strip()

            images = list(prop.media.filter(image__isnull=False).exclude(image='').order_by('order', 'pk'))

            for idx, media in enumerate(images):
                tpl_en = EN_TEMPLATES[idx % len(EN_TEMPLATES)]
                tpl_tr = TR_TEMPLATES[idx % len(TR_TEMPLATES)]

                new_en = tpl_en.format(name=name_en, location=loc_en)
                new_tr = tpl_tr.format(name=name_tr, location=loc_tr)

                changed = False

                if overwrite or not media.caption_en:
                    if apply:
                        media.caption_en = new_en
                    self.stdout.write(f"  EN [{prop.name} #{idx+1}]: {new_en}")
                    changed = True

                if overwrite or not media.caption_tr:
                    if apply:
                        media.caption_tr = new_tr
                    self.stdout.write(f"  TR [{prop.name} #{idx+1}]: {new_tr}")
                    changed = True

                if changed:
                    if apply:
                        media.save(update_fields=['caption_en', 'caption_tr'])
                    updated += 1
                else:
                    skipped += 1

        self.stdout.write("")
        if apply:
            self.stdout.write(self.style.SUCCESS(
                f"Done. Updated {updated} images, skipped {skipped} (already had alt text)."
            ))
        else:
            self.stdout.write(self.style.WARNING(
                f"Dry-run complete. Would update {updated} images (skipped {skipped}). "
                f"Run with --apply to save."
            ))
