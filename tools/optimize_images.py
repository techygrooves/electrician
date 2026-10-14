#!/usr/bin/env python3
"""Create responsive AVIF, WebP and JPEG versions of a photo for a photo slot.

Development tool only. Requires Pillow (pip install pillow; AVIF needs Pillow 11.2+
or the pillow-avif-plugin package). Run from the project root:

    python3 tools/optimize_images.py my-photo.jpg hero --preset wide
    python3 tools/optimize_images.py kitchen.jpg residential --preset portrait
    python3 tools/optimize_images.py panel.jpg services/electrical-panel-upgrades --preset wide

Presets match the commented <picture> markup in the HTML:
    wide      16:9  -> 768, 1280, 1920, 2560 px wide  (heroes)
    portrait  4:5   -> 480, 800, 1200 px wide         (residential / commercial cards)

The photo is center-cropped to the preset's aspect ratio (use --focus to shift the
crop, e.g. --focus 0.7 keeps more of the right/bottom). Files are written to
assets/images/photos/<slot>-<width>.<avif|webp|jpg>. Then remove the comment markers
around that slot's <picture> element in the HTML.
"""
import argparse
import os
import sys

try:
    from PIL import Image, ImageOps
except ImportError:
    sys.exit("Pillow is required: pip install pillow")

PRESETS = {"wide": ((16, 9), (768, 1280, 1920, 2560)), "portrait": ((4, 5), (480, 800, 1200))}
ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))


def crop_to_ratio(im, rw, rh, focus):
    w, h = im.size
    target = rw / rh
    if w / h > target:  # too wide: crop sides
        new_w = round(h * target)
        left = round((w - new_w) * focus)
        return im.crop((left, 0, left + new_w, h))
    new_h = round(w / target)
    top = round((h - new_h) * focus)
    return im.crop((0, top, w, top + new_h))


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("source")
    ap.add_argument("slot", help="photo slot name, e.g. hero, residential, services/ev-charger-installation")
    ap.add_argument("--preset", choices=PRESETS, default="wide")
    ap.add_argument("--focus", type=float, default=0.5, help="crop position 0-1 (default 0.5 = center)")
    args = ap.parse_args()

    (rw, rh), widths = PRESETS[args.preset]
    im = ImageOps.exif_transpose(Image.open(args.source)).convert("RGB")
    im = crop_to_ratio(im, rw, rh, min(max(args.focus, 0), 1))
    if im.width < widths[-1]:
        print(f"note: source is {im.width}px wide; largest size will be upscaled. A wider original is recommended.")

    out_dir = os.path.join(ROOT, "assets", "images", "photos", os.path.dirname(args.slot))
    os.makedirs(out_dir, exist_ok=True)
    base = os.path.join(ROOT, "assets", "images", "photos", args.slot)
    avif_ok = "AVIF" in Image.SAVE or Image.registered_extensions().get(".avif")
    for w in widths:
        h = round(w * rh / rw)
        resized = im.resize((w, h), Image.LANCZOS)
        resized.save(f"{base}-{w}.jpg", "JPEG", quality=80, optimize=True, progressive=True)
        resized.save(f"{base}-{w}.webp", "WEBP", quality=78, method=6)
        if avif_ok:
            resized.save(f"{base}-{w}.avif", "AVIF", quality=60)
        print(f"wrote {os.path.relpath(base, ROOT)}-{w}.(jpg|webp{'|avif' if avif_ok else ''})  {w}x{h}")
    if not avif_ok:
        print("AVIF not supported by this Pillow build; browsers will use WebP. Remove the AVIF <source> line or install pillow-avif-plugin.")


if __name__ == "__main__":
    main()
