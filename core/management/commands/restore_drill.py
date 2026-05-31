from django.core.management.base import BaseCommand
from django.test import Client

from core.models import ChatLead, ContactSubmission
from properties.models import Property, PropertyInterest, PropertyUnit, UnitBooking


class Command(BaseCommand):
    help = "Post-restore verification drill (data consistency and key pages)."

    def handle(self, *args, **options):
        self.stdout.write("== Data counts ==")
        self.stdout.write(f"Properties: {Property.all_objects.count()}")
        self.stdout.write(f"Units: {PropertyUnit.all_objects.count()}")
        self.stdout.write(f"Bookings: {UnitBooking.all_objects.count()}")
        self.stdout.write(f"Interests: {PropertyInterest.all_objects.count()}")
        self.stdout.write(f"Contacts: {ContactSubmission.all_objects.count()}")
        self.stdout.write(f"Chat leads: {ChatLead.all_objects.count()}")

        self.stdout.write("\n== Endpoint checks ==")
        client = Client()
        checks = [
            ("/", {200}),
            ("/properties/", {200}),
            ("/health/live/", {200}),
            ("/health/ready/", {200}),
            ("/admin/login/", {200}),
        ]
        for path, allowed in checks:
            response = client.get(path)
            ok = response.status_code in allowed
            label = "OK" if ok else "FAIL"
            self.stdout.write(f"{label} {path} -> {response.status_code}")
            if not ok:
                raise SystemExit(1)

        self.stdout.write(self.style.SUCCESS("Restore drill passed."))
