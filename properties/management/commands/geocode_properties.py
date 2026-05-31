"""
Management command: geocode_properties

Geocodes all active properties that lack private coordinates.
Uses the property's existing `location` field (+ ", Greece") as the query
and falls back to `area` if location is empty.

Usage:
    python manage.py geocode_properties          # only properties missing coords
    python manage.py geocode_properties --all    # force re-geocode all
"""
import time

from django.core.management.base import BaseCommand

from properties.geocoding import geocode_address_nominatim, generate_public_point
from properties.models import Property


class Command(BaseCommand):
    help = "Geocode properties that are missing lat/lng using Nominatim."

    def add_arguments(self, parser):
        parser.add_argument(
            "--all",
            action="store_true",
            help="Re-geocode ALL active properties, even those that already have coords.",
        )

    def handle(self, *args, **options):
        qs = Property.objects.filter(is_active=True, deleted_at__isnull=True)
        if not options["all"]:
            qs = qs.filter(lat_private__isnull=True)

        properties = list(qs)
        if not properties:
            self.stdout.write(self.style.SUCCESS("All properties already have coordinates."))
            return

        self.stdout.write(f"Geocoding {len(properties)} propert{'y' if len(properties) == 1 else 'ies'}…\n")

        ok = 0
        fail = 0
        for p in properties:
            # Build the best possible query string
            query = self._build_query(p)
            if not query:
                self.stdout.write(self.style.WARNING(f"  ✗ pk={p.pk} {p.name}: no location data, skipping"))
                fail += 1
                continue

            self.stdout.write(f"  → pk={p.pk} {p.name}: querying \"{query}\" … ", ending="")
            result = geocode_address_nominatim(query)

            if result is None:
                self.stdout.write(self.style.WARNING("FAIL"))
                fail += 1
                continue

            lat, lng = result
            pub_lat, pub_lng = generate_public_point(lat, lng, radius_m=p.public_radius_m or 400)

            # Direct DB update to avoid re-triggering save() geocoding
            Property.objects.filter(pk=p.pk).update(
                lat_private=round(lat, 6),
                lng_private=round(lng, 6),
                lat_public=round(pub_lat, 6),
                lng_public=round(pub_lng, 6),
                address_private=p.address_private or query,
            )

            self.stdout.write(self.style.SUCCESS(
                f"OK  ({lat:.5f}, {lng:.5f}) → public ({pub_lat:.5f}, {pub_lng:.5f})"
            ))
            ok += 1

        self.stdout.write(f"\nDone: {ok} geocoded, {fail} failed.")

    @staticmethod
    def _build_query(prop):
        """Build the best geocoding query from available property data."""
        # Prefer address_private if already set
        if prop.address_private and prop.address_private.strip():
            return prop.address_private.strip()

        parts = []
        # Use the location field (e.g. "Alimos, South Athens")
        if prop.location and prop.location.strip():
            parts.append(prop.location.strip())
        # Use area as extra context
        if prop.area and prop.area.strip() and prop.area.strip() not in (prop.location or ""):
            parts.append(prop.area.strip())

        if not parts:
            return None

        query = ", ".join(parts)
        # Ensure "Greece" is in the query for better geocoding accuracy
        if "greece" not in query.lower() and "ελλάδα" not in query.lower():
            query += ", Greece"
        return query
