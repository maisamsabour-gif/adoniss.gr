"""
Management command to configure Google Maps API key for Property admin.

Usage:
    python manage.py setup_google_maps YOUR_API_KEY_HERE

What it does:
    1. Validates the key format (starts with AIzaSy, correct length)
    2. Tests it against the Google Geocoding API
    3. Writes it to .env
    4. Reloads Django settings
    5. Sends HUP to gunicorn so the change takes effect immediately
"""
import os
import re
import signal
import subprocess
import urllib.request
import urllib.parse
import json

from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = "Configure Google Maps API key for Property admin autocomplete"

    def add_arguments(self, parser):
        parser.add_argument(
            "api_key",
            nargs="?",
            help="Your Google Maps API key (starts with AIzaSy...)",
        )
        parser.add_argument(
            "--test-only",
            action="store_true",
            help="Only test the current key in .env without changing it",
        )

    def handle(self, *args, **options):
        env_path = os.path.join(os.path.dirname(os.path.dirname(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        )), ".env")

        if options["test_only"]:
            return self._test_current_key(env_path)

        api_key = options["api_key"]
        if not api_key:
            self.stderr.write(self.style.ERROR(
                "\n  Missing API key. Usage:\n"
                "  python manage.py setup_google_maps AIzaSyXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX\n"
                "\n  To get a key:\n"
                "  1. Go to https://console.cloud.google.com/google/maps-apis/credentials\n"
                "  2. Click '+ CREATE CREDENTIALS' → 'API key'\n"
                "  3. Enable these APIs: Maps JavaScript API, Places API, Geocoding API\n"
                "  4. Restrict key to HTTP referrers: https://adonisgroup.gr/*\n"
                "  5. Copy the key and run this command\n"
            ))
            raise CommandError("No API key provided.")

        api_key = api_key.strip()

        # --- Step 1: Format validation ---
        self.stdout.write("\n  Step 1/4: Validating key format...")
        if not api_key.startswith("AIzaSy"):
            raise CommandError(
                f"Invalid key format. Google Maps API keys start with 'AIzaSy'. "
                f"Got: '{api_key[:10]}...'"
            )
        if len(api_key) < 30 or len(api_key) > 50:
            raise CommandError(
                f"Suspicious key length ({len(api_key)} chars). "
                f"Typical Google keys are 39 characters."
            )
        self.stdout.write(self.style.SUCCESS("  ✓ Key format looks valid"))

        # --- Step 2: Test against Geocoding API ---
        self.stdout.write("  Step 2/4: Testing key against Google Geocoding API...")
        self._test_key_live(api_key)

        # --- Step 3: Write to .env ---
        self.stdout.write(f"  Step 3/4: Writing key to {env_path}...")
        self._write_to_env(env_path, api_key)
        self.stdout.write(self.style.SUCCESS("  ✓ Key written to .env"))

        # --- Step 4: Reload gunicorn ---
        self.stdout.write("  Step 4/4: Reloading gunicorn...")
        self._reload_gunicorn()

        self.stdout.write(self.style.SUCCESS(
            "\n  ══════════════════════════════════════════\n"
            "  ✅ Google Maps API key configured!\n"
            "  ══════════════════════════════════════════\n"
            "\n"
            "  Property admin now uses REAL Google Places Autocomplete.\n"
            "  Open any Property in admin → scroll to '🔒 Private Address'\n"
            "  → type an address → you'll see Google suggestions.\n"
        ))

    def _test_key_live(self, api_key):
        url = (
            "https://maps.googleapis.com/maps/api/geocode/json?"
            + urllib.parse.urlencode({
                "address": "Syntagma Square, Athens, Greece",
                "key": api_key,
            })
        )
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "AdonisAdmin/1.0"})
            with urllib.request.urlopen(req, timeout=10) as resp:
                data = json.loads(resp.read().decode())

            status = data.get("status", "UNKNOWN")
            if status == "OK":
                loc = data["results"][0]["geometry"]["location"]
                self.stdout.write(self.style.SUCCESS(
                    f"  ✓ Geocoding API works! "
                    f"(Syntagma Square → {loc['lat']:.4f}, {loc['lng']:.4f})"
                ))
            elif status == "REQUEST_DENIED":
                error_msg = data.get("error_message", "No details")
                raise CommandError(
                    f"Google rejected the key: {error_msg}\n"
                    f"  → Make sure 'Geocoding API' is enabled in your Google Cloud project.\n"
                    f"  → Check HTTP referrer restrictions (admin URL must be allowed)."
                )
            elif status == "OVER_QUERY_LIMIT":
                self.stdout.write(self.style.WARNING(
                    "  ⚠ Geocoding API returned OVER_QUERY_LIMIT. "
                    "Key may work but billing may not be enabled."
                ))
            else:
                raise CommandError(f"Unexpected API response: {status}")

        except urllib.error.URLError as e:
            raise CommandError(f"Could not reach Google API: {e}")

    def _test_current_key(self, env_path):
        if not os.path.exists(env_path):
            raise CommandError(f".env not found at {env_path}")

        with open(env_path, "r") as f:
            content = f.read()

        match = re.search(r"^GOOGLE_MAPS_API_KEY=(.+)$", content, re.MULTILINE)
        if not match or not match.group(1).strip():
            self.stderr.write(self.style.ERROR(
                "\n  GOOGLE_MAPS_API_KEY is empty in .env\n"
                "  Run: python manage.py setup_google_maps YOUR_KEY\n"
            ))
            return

        key = match.group(1).strip()
        self.stdout.write(f"\n  Found key: {key[:8]}...{key[-4:]}")
        self._test_key_live(key)
        self.stdout.write(self.style.SUCCESS("  ✓ Key is valid and working\n"))

    def _write_to_env(self, env_path, api_key):
        if not os.path.exists(env_path):
            raise CommandError(f".env not found at {env_path}")

        with open(env_path, "r") as f:
            content = f.read()

        new_line = f"GOOGLE_MAPS_API_KEY={api_key}"
        if re.search(r"^GOOGLE_MAPS_API_KEY=", content, re.MULTILINE):
            content = re.sub(
                r"^GOOGLE_MAPS_API_KEY=.*$",
                new_line,
                content,
                flags=re.MULTILINE,
            )
        else:
            content = content.rstrip() + f"\n{new_line}\n"

        with open(env_path, "w") as f:
            f.write(content)

    def _reload_gunicorn(self):
        try:
            result = subprocess.run(
                ["pgrep", "-f", "gunicorn.*adonis"],
                capture_output=True, text=True,
            )
            pids = result.stdout.strip().split("\n")
            if pids and pids[0]:
                master_pid = int(pids[0])
                os.kill(master_pid, signal.SIGHUP)
                self.stdout.write(self.style.SUCCESS(
                    f"  ✓ Sent HUP to gunicorn (PID {master_pid})"
                ))
            else:
                self.stdout.write(self.style.WARNING(
                    "  ⚠ Gunicorn not found — restart manually: "
                    "kill -HUP $(pgrep -f 'gunicorn.*adonis' | head -1)"
                ))
        except Exception as e:
            self.stdout.write(self.style.WARNING(f"  ⚠ Could not reload gunicorn: {e}"))
