"""
Generate responsive WebP variants at common breakpoint widths (480 / 768 /
1200 / 1920 px) plus a full-size .webp sibling, for every .jpg/.jpeg/.png
under a given directory.

Behaviour:
  - Idempotent: skips any variant whose file already exists.
  - Never enlarges: a width >= source width is silently skipped.
  - Preserves aspect ratio (LANCZOS resampling, quality=80, method=6).
  - Leaves originals untouched.
  - Outputs are written next to the source as `<stem>-<W>.webp`
    (e.g. hero-1200.webp).

Usage:
    python manage.py responsive_images                       # default: adonis/static/images
    python manage.py responsive_images --dir media           # process media/
    python manage.py responsive_images --dir adonis/static/images --quality 85
"""
from pathlib import Path

from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Generate responsive WebP variants at 480/768/1200/1920 widths."

    DEFAULT_DIR = "adonis/static/images"
    SIZES = (480, 768, 1200, 1920)

    def add_arguments(self, parser):
        parser.add_argument("--dir", default=self.DEFAULT_DIR,
                            help=f"Source directory to scan (default: {self.DEFAULT_DIR}).")
        parser.add_argument("--quality", type=int, default=80,
                            help="WebP quality 1-100 for downscaled variants (default 80).")
        parser.add_argument("--full-quality", type=int, default=82,
                            help="WebP quality 1-100 for full-size sibling (default 82).")
        parser.add_argument("--method", type=int, default=6,
                            help="WebP encoding method 0-6 (default 6).")

    def handle(self, *args, **options):
        from PIL import Image

        root = Path(options["dir"])
        if not root.exists():
            self.stderr.write(self.style.ERROR(f"Directory not found: {root}"))
            return

        quality = options["quality"]
        full_quality = options["full_quality"]
        method = options["method"]

        total_ok = total_skip = total_fail = 0

        for ext in ("*.jpg", "*.jpeg", "*.png", "*.JPG", "*.JPEG", "*.PNG"):
            for img_path in root.rglob(ext):
                try:
                    with Image.open(img_path) as img:
                        if img.mode in ("P", "CMYK"):
                            img = img.convert(
                                "RGBA" if "transparency" in img.info else "RGB"
                            )
                        elif img.mode not in ("RGB", "RGBA"):
                            img = img.convert("RGB")

                        orig_w = img.width
                        # 1) Per-breakpoint downsized variants
                        for w in self.SIZES:
                            if w >= orig_w:
                                continue
                            out = img_path.with_name(f"{img_path.stem}-{w}.webp")
                            if out.exists():
                                total_skip += 1
                                continue
                            new_h = round(img.height * (w / orig_w))
                            resized = img.resize((w, new_h), Image.LANCZOS)
                            resized.save(out, "WEBP", quality=quality, method=method)
                            self.stdout.write(
                                f"  OK  {out.relative_to(root)}  ({w}x{new_h})"
                            )
                            total_ok += 1

                        # 2) Full-size .webp sibling (only if missing)
                        full_webp = img_path.with_suffix(".webp")
                        if not full_webp.exists():
                            img.save(full_webp, "WEBP", quality=full_quality, method=method)
                            self.stdout.write(
                                f"  OK  {full_webp.relative_to(root)}  ({orig_w}x{img.height})"
                            )
                            total_ok += 1
                        else:
                            total_skip += 1

                except Exception as exc:
                    self.stderr.write(f"  FAIL  {img_path}: {exc}")
                    total_fail += 1

        self.stdout.write(self.style.SUCCESS(
            f"\nDone. created={total_ok}  skipped(existing)={total_skip}  failed={total_fail}"
        ))
