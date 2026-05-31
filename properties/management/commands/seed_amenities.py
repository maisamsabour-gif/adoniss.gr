"""
Management command: seed_amenities

Creates default AmenityCategory and Amenity records.
Safe to run multiple times — uses get_or_create so it won't duplicate data.

Usage:
    python manage.py seed_amenities
"""
from django.core.management.base import BaseCommand
from django.utils.text import slugify

from properties.models import Amenity, AmenityCategory


SEED_DATA = [
    {
        "name": "Internal",
        "display_order": 1,
        "amenities": [
            ("Elevator",               "elevator",             1),
            ("Air conditioning",       "air-conditioning",     2),
            ("Secure door",            "secure-door",          3),
            ("Luxury home",            "luxury-home",          4),
            ("Furnished",              "furnished",            5),
            ("Solar water heating",    "solar-water-heating",  6),
            ("Frames: Aluminum",       "frames-aluminum",      7),
            ("Bright",                 "bright",               8),
            ("Fireplace",              "fireplace",            9),
            ("Floor: Wood",            "floor-wood",           10),
            ("Double glass",           "double-glass",         11),
            ("Painted",                "painted",              12),
        ],
    },
    {
        "name": "External",
        "display_order": 2,
        "amenities": [
            ("Parking spot",           "parking-spot",         1),
            ("Residential zone",       "residential-zone",     2),
            ("Balcony",                "balcony",              3),
            ("View",                   "view",                 4),
        ],
    },
    {
        "name": "Construction",
        "display_order": 3,
        "amenities": [
            ("Renovated",              "renovated",            1),
        ],
    },
]


class Command(BaseCommand):
    help = "Seed default amenity categories and amenities (idempotent)."

    def handle(self, *args, **options):
        created_cats = 0
        created_ams = 0

        for cat_data in SEED_DATA:
            cat, cat_created = AmenityCategory.objects.get_or_create(
                slug=slugify(cat_data["name"]),
                defaults={
                    "name": cat_data["name"],
                    "display_order": cat_data["display_order"],
                    "is_active": True,
                },
            )
            if cat_created:
                created_cats += 1
                self.stdout.write(f'  + Category: {cat.name}')
            else:
                self.stdout.write(f'  = Category already exists: {cat.name}')

            for am_name, am_slug, am_order in cat_data["amenities"]:
                am, am_created = Amenity.objects.get_or_create(
                    slug=am_slug,
                    defaults={
                        "category": cat,
                        "name": am_name,
                        "display_order": am_order,
                        "is_active": True,
                    },
                )
                if am_created:
                    created_ams += 1
                    self.stdout.write(f'    + Amenity: {am.name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'\nDone — created {created_cats} categories, {created_ams} amenities.'
            )
        )
