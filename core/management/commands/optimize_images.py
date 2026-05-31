"""
Convert .jpg/.jpeg/.png images under STATIC_ROOT, MEDIA_ROOT (and the local
./static and ./media directories) to .webp siblings.

Behaviour:
  - Skips a file if a sibling .webp already exists.
  - Leaves the original .jpg/.png on disk (callers may still reference them).
  - Reports per-file outcome to stdout / errors to stderr.

This command is safe to re-run; it only writes files that don't yet exist.

Usage:
    python manage.py optimize_images            # run with defaults
    python manage.py optimize_images --quality 80
"""
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Convert .jpg/.jpeg/.png images to .webp siblings (idempotent)."

    def add_arguments(self, parser):
        parser.add_argument("--quality", type=int, default=82,
                            help="WebP quality 1-100 (default 82).")
        parser.add_argument("--method", type=int, default=6,
                            help="WebP compression method 0-6 (default 6, slowest+best).")

    def handle(self, *args, **options):
        from PIL import Image

        quality = options["quality"]
        method = options["method"]

        roots = []
        for candidate in (
            settings.STATIC_ROOT,
            settings.MEDIA_ROOT,
            Path("static"),
            Path("media"),
        ):
            if not candidate:
                continue
            p = Path(candidate)
            if p.exists():
                p_resolved = p.resolve()
                if p_resolved not in roots:
                    roots.append(p_resolved)

        if not roots:
            self.stderr.write("No image roots found.")
            return

        total_ok = total_skip = total_fail = 0

        for root in roots:
            self.stdout.write(self.style.NOTICE(f"\nScanning {root} ..."))
            for ext in ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"):
                for img_path in root.rglob(ext):
                    webp_path = img_path.with_suffix(".webp")
                    if webp_path.exists():
                        total_skip += 1
                        continue
                    try:
                        with Image.open(img_path) as img:
                            if img.mode in ("P", "CMYK"):
                                img = img.convert(
                                    "RGBA" if "transparency" in img.info else "RGB"
                                )
                            elif img.mode not in ("RGB", "RGBA"):
                                img = img.convert("RGB")
                            img.save(webp_path, "WEBP", quality=quality, method=method)
                        old_kb = img_path.stat().st_size / 1024
                        new_kb = webp_path.stat().st_size / 1024
                        pct = 100 * (1 - new_kb / max(old_kb, 1))
                        self.stdout.write(
                            f"  OK  {img_path.relative_to(root)}  "
                            f"({old_kb:.0f} -> {new_kb:.0f} KB, -{pct:.0f}%)"
                        )
                        total_ok += 1
                    except Exception as exc:
                        self.stderr.write(f"  FAIL  {img_path}: {exc}")
                        total_fail += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. converted={total_ok}  skipped(existing)={total_skip}  failed={total_fail}"
        ))
