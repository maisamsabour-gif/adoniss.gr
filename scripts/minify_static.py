#!/usr/bin/env python3
"""
Re-run after editing any CSS/JS source listed in CSS_TARGETS / JS_TARGETS.

Usage (from project root):
    python scripts/minify_static.py

Generates `*.min.css` / `*.min.js` siblings (the templates point at the .min
versions). The original sources are kept on disk for debugging — they are
just unreferenced in production templates.
"""
from pathlib import Path

import csscompressor
import rjsmin

PROJECT_ROOT = Path(__file__).resolve().parent.parent
STATIC = PROJECT_ROOT / "adonis" / "static"

CSS_TARGETS = [
    STATIC / "css/style.css",
    STATIC / "css/golden_visa_landing.css",
    STATIC / "css/bento-grid.css",
]
JS_TARGETS = [
    STATIC / "js/main.js",
    STATIC / "js/bs4-to-bs5-fix.js",
]


def _process(path: Path, fn) -> None:
    if not path.exists():
        print(f"  SKIP (missing): {path}")
        return
    src = path.read_text(encoding="utf-8")
    out = fn(src)
    out_path = path.with_suffix(".min" + path.suffix)
    out_path.write_text(out, encoding="utf-8")
    saved_kb = (len(src) - len(out)) / 1024
    pct = 100 * (1 - len(out) / max(len(src), 1))
    print(
        f"  {path.name:32s} {len(src)/1024:7.1f} KB -> "
        f"{len(out)/1024:7.1f} KB  (-{saved_kb:.1f} KB, -{pct:.0f}%)  =>  {out_path.name}"
    )


def main() -> None:
    print("CSS minification (csscompressor):")
    for p in CSS_TARGETS:
        _process(p, csscompressor.compress)
    print("\nJS minification (rjsmin):")
    for p in JS_TARGETS:
        _process(p, rjsmin.jsmin)


if __name__ == "__main__":
    main()
